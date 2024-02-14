import imaplib
import email
import pandas as pd
from email.header import decode_header
import smtplib
import logging

class EmailReader:
    """
    Class to read and process emails using IMAP.
    """

    def __init__(self, imap_url, email_user, email_pass):
        """
        Initialize the EmailReader object.

        Args:
            imap_url (str): IMAP server URL.
            email_user (str): Email username.
            email_pass (str): Email password.
        """
        self.imap_url = imap_url
        self.email_user = email_user
        self.email_pass = email_pass
        self.mail = None
        self.df = pd.DataFrame(columns=['Email ID', 'Message ID', 'From', 'Subject', 'Body'])

    def connect(self):
        """
        Connect to the IMAP server.
        """
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_url)
        except imaplib.IMAP4.error as e:
            logging.error(f"Failed to connect to IMAP server: {e}")
            raise ConnectionError(f"Failed to connect to IMAP server: {e}")

    def login(self):
        """
        Login to the email account.
        """
        try:
            self.mail.login(self.email_user, self.email_pass)
        except imaplib.IMAP4.error as e:
            logging.error(f"Login failed: {e}")
            raise ConnectionError(f"Login failed: {e}")

    def fetch_unseen_emails(self):
        """
        Fetch unseen emails and process them.
        """
        try:
            self.mail.select('inbox')
            status, messages = self.mail.search(None, '(UNSEEN)')
            if status == 'OK':
                for num in messages[0].split():
                    status, data = self.mail.fetch(num, '(RFC822)')
                    if status == 'OK':
                        msg = email.message_from_bytes(data[0][1])
                        self.process_email(msg, num)
        except Exception as e:
            logging.error(f"Error fetching emails: {e}")
            raise Exception(f"Error fetching emails: {e}")

    def process_email(self, msg, email_id):
        """
        Process the email and add it to the DataFrame.

        Args:
            msg (email.message.Message): Email message.
            email_id (bytes): Email ID.
        """
        try:
            message_id = msg.get('Message-ID')
            subject = decode_header(msg['subject'])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            from_ = msg.get('from')
            body = self.get_email_body(msg)
            self.df = self.df._append({'Email ID': email_id.decode(), 'Message ID': message_id, 'From': from_, 'Subject': subject, 'Body': body}, ignore_index=True)
        except Exception as e:
            logging.error(f"Error processing email: {e}")
            raise Exception(f"Error processing email: {e}")

    def get_email_body(self, msg):
        """
        Get the body of the email.

        Args:
            msg (email.message.Message): Email message.

        Returns:
            str: Email body.
        """
        body = ""
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_maintype() == 'text':
                        body = part.get_payload(decode=True)
                        if body is not None:
                            body = body.decode()
                        break
            else:
                body = msg.get_payload(decode=True)
                if body is not None:
                    body = body.decode()
        except Exception as e:
            logging.error(f"Error getting email body: {e}")
        return body

    def save_emails_to_excel(self, filename):
        """
        Save emails to an Excel file.

        Args:
            filename (str): Name of the Excel file.
        """
        try:
            self.df.to_excel(filename, index=False)
        except Exception as e:
            logging.error(f"Error saving emails to Excel: {e}")
            raise Exception(f"Error saving emails to Excel: {e}")

    def close_connection(self):
        """
        Close the IMAP connection.
        """
        try:
            self.mail.close()
            self.mail.logout()
        except Exception as e:
            logging.error(f"Error closing connection: {e}")
            print(f"Error closing connection: {e}")

    def reply_to_email(self, msg_id, reply_body):
        """
        Reply to an email.

        Args:
            msg_id (str): Message ID of the email to reply to.
            reply_body (str): Body of the reply.

        Returns:
            str: Status message.
        """
        try:
            self.mail.select('inbox')
            result, data = self.mail.search(None, f'(HEADER Message-ID "{msg_id}")')
            if result == 'OK':
                email_ids = data[0].split()
                latest_email_id = email_ids[-1]
                result, data = self.mail.fetch(latest_email_id, '(RFC822)')

                if result == 'OK':
                    raw_email = data[0][1]
                    email_message = email.message_from_bytes(raw_email)

                    reply = email.message.EmailMessage()
                    reply['Subject'] = 'Re: ' + email_message['Subject']
                    reply['To'] = email_message['Reply-To'] or email_message['From']
                    reply['From'] = self.email_user
                    reply.set_content(reply_body)

                    with smtplib.SMTP('smtp-mail.outlook.com', 587) as smtp:
                        smtp.ehlo()
                        smtp.starttls()
                        smtp.ehlo()
                        smtp.login(self.email_user, self.email_pass)
                        smtp.send_message(reply)
                    return "Reply sent successfully."
                else:
                    return "Failed to fetch the email."
            else:
                return "Email not found."
        except Exception as e:
            logging.error(f"Error in sending email: {e}")
            raise Exception(f"Error in sending email: {e}")
