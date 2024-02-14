import gradio as gr
import pandas as pd
from .email_reader import EmailReader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import  RunnablePassthrough
import datetime
import os
from langchain_community.chat_models import ChatOllama
from config import *
from transformers import pipeline
import logging



# Initialize zero-shot classification model
Data_path = os.path.join('Email_Data', 'emails.xlsx')

class EmailResponder:
    """Class to handle email responses and sentiment analysis."""

    def __init__(self):
        """Initialize the EmailResponder object."""
        try:
            self.classifier = pipeline("zero-shot-classification", model=ZERO_SHOT_MODEL)
            self.text_labels = ['Positive', 'Negative', 'Neutral']
            self.template = template
            self.embed_model = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)
            self.DB_PATH = DB_PATH
            self.vectorstore = Chroma(persist_directory=self.DB_PATH, embedding_function=self.embed_model)
            self.retriever = self.vectorstore.as_retriever()
            self.prompt = ChatPromptTemplate.from_template(self.template)
            self.ollama_llm = OLLAMA_MODEL
            self.model_local = ChatOllama(model=self.ollama_llm)
            self.chain = (
                {"context": self.retriever, "question": RunnablePassthrough()}
                | self.prompt
                | self.model_local
                | StrOutputParser()
            )
        except Exception as e:
            logging.error(f"Error initializing EmailResponder: {e}")
            raise

    def generate_response(self, body, subject):
        """Generate a response based on sentiment analysis and a pre-defined model chain.

        Args:
            body (str): The body of the email.
            subject (str): The subject of the email.

        Returns:
            Tuple[str, float, str]: A tuple containing sentiment label, sentiment score, and the generated reply.
        """
        try:
            # Assuming you want to analyze the body for sentiment
            result = self.classifier(body, self.text_labels, multi_label=False)
            sentiment_label = result['labels'][0]
            sentiment_score = result['scores'][0]
            today = datetime.date.today()
            query = f"Todays date -{today}\n  sentiment - {sentiment_label}\n Subject -{subject}\n Body-{body} "
            reply_body = self.chain.invoke(query)
            return sentiment_label, sentiment_score, reply_body
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            raise

class EmailProcessor(EmailResponder):
    """Class to process emails and manage email-related tasks."""

    def __init__(self):
        """Initialize the EmailProcessor object."""
        super().__init__()

    def fetch_and_save_emails(self, email_user, email_pass):
        """Fetch unseen emails and save them to an Excel file.

        Args:
            email_user (str): Email username.
            email_pass (str): Email password.

        Returns:
            str: Success message or error message.
        """
        try:
            reader = EmailReader('imap-mail.outlook.com', email_user, email_pass)
            reader.connect()
            reader.login()
            reader.fetch_unseen_emails()
            reader.save_emails_to_excel(Data_path)
            return "Emails fetched and saved to 'emails.xlsx'"
        except Exception as e:
            logging.error(f"Error fetching and saving emails: {e}")
            raise

    def load_emails(self):
        """Load emails from the Excel file.

        Returns:
            Tuple[str, str, str, int]: A tuple containing sender, subject, body, and email index.
        """
        try:
            df = pd.read_excel(Data_path)
            if not df.empty:
                return self.update_email_content(df, 0)
            return "N/A", "N/A", "N/A", 0
        except Exception as e:
            logging.error(f"Error loading emails: {e}")
            raise

    def send_reply_and_move_next(self, email_user, email_pass, index, reply_body):
        """Send a reply to the current email and move to the next one.

        Args:
            email_user (str): Email username.
            email_pass (str): Email password.
            index (int): Current email index.
            reply_body (str): Reply body.

        Returns:
            Tuple[str, str, str, str, int, str, str, str]: A tuple containing response message, sender, subject, body, index,
            and empty reply and sentiment fields.
        """
        try:
            df = pd.read_excel(Data_path)
            if 0 <= index < len(df):
                # Retrieve the message ID of the current email
                msg_id = df.iloc[index]['Message ID']  # Replace 'Message ID' with the actual column name for message IDs in your DataFrame
                reader = EmailReader('imap-mail.outlook.com', email_user, email_pass)
                reader.connect()
                reader.login()
                send_status = reader.reply_to_email(msg_id, reply_body)
                reader.close_connection()

                response_message = send_status if send_status else "Reply sent successfully!"
                From, Subject, Body, index = self.update_email_content(df, index)

                # Clear reply body and sentiment fields
                return response_message, From, Subject, Body, index, "", "", ""

            else:
                return "Invalid email index.", "", "", "", index, "", "", ""
        except Exception as e:
            logging.error(f"Error sending reply and moving next: {e}")
            raise

    def update_email_content(self, df, index):
        """Update email content based on the index.

        Args:
            df (pd.DataFrame): DataFrame containing email data.
            index (int): Email index.

        Returns:
            Tuple[str, str, str, int]: A tuple containing sender, subject, body, and email index.
        """
        try:
            if 0 <= index < len(df):
                email = df.iloc[index]
                return email["From"], email["Subject"], str(email["Body"]), index
            return "N/A", "N/A", "N/A", index
        except Exception as e:
            logging.error(f"Error updating email content: {e}")
            raise

    def navigate_emails(self, direction, index):
        """Navigate through emails based on the given direction.

        Args:
            direction (str): Navigation direction ('next' or 'prev').
            index (int): Current email index.

        Returns:
            Tuple[str, str, str, int]: A tuple containing sender, subject, body, and email index.
        """
        try:
            df = pd.read_excel(Data_path)
            if direction == "next":
                index = index + 1 if index < len(df) - 1 else index
            elif direction == "prev":
                index = index - 1 if index > 0 else index
            return self.update_email_content(df, index)
        except Exception as e:
            logging.error(f"Error navigating emails: {e}")
            raise

    def show_popup(self, response_message):
        """Display a popup with the given response message.

        Args:
            response_message (str): Response message.

        Returns:
            gr.Info: Gradio Info object.
        """
        try:
            if response_message:
                gr.update(value=response_message, visible=True)
            return gr.Info(text=response_message)
        except Exception as e:
            logging.error(f"Error showing popup: {e}")
            raise
