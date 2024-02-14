import gradio as gr
from Email_Reader.email_response import EmailProcessor
import logging
from utils.logging_config import setup_logging


setup_logging()

def create_interface(email_processor):
    """
    Create the Gradio interface for email processing.

    Args:
        email_processor (EmailProcessor): An instance of the EmailProcessor class.

    Returns:
        gr.Blocks: Gradio Blocks object representing the interface.
    """
    try:
        
        with gr.Blocks() as app:
            gr.Markdown("<center> <h1 style='font-size: 24px; font-weight:bold;'>Email Processing Interface</h1> </center>")
            with gr.Row():
                user_input = gr.Textbox(label="Email User", placeholder="Enter Email User here")
                pass_input = gr.Textbox(label="Email Password", placeholder="Enter Email Password here", type="password")
                fetch_button = gr.Button("Fetch Emails")
                fetch_output = gr.Label()
            fetch_button.click(email_processor.fetch_and_save_emails, inputs=[user_input, pass_input], outputs=fetch_output)

            with gr.Row():
                with gr.Column():
                    from_field = gr.Textbox(label="From")
                    subject_field = gr.Textbox(label="Subject", placeholder="Subject", lines=3, max_lines=3)
                    body_field = gr.Textbox(label="Body", lines=20, max_lines=20, interactive=True, elem_classes="feedback")  # Set the height as desired
                    load_button = gr.Button("Load Emails")
                    email_index = gr.Number(label="Email Index", value=0, visible=False)
                    response_label = gr.Label(visible=False)
                with gr.Column():
                    Sentiment = gr.Textbox(label="Sentiment", placeholder="Sentiment Analysis Here")
                    Sentiment_score = gr.Textbox(label="Sentiment Score", placeholder="Sentiment Score", lines=3, max_lines=3)
                    reply_body_field = gr.Textbox(label="Reply Body", lines=20, max_lines=20, interactive=True, placeholder="Type your reply here", elem_classes="feedback")  # Set the height as desired
                    reply_button = gr.Button("Reply")

            with gr.Row():
                prev_button = gr.Button("Previous")
                next_button = gr.Button("Next")
                generate_response_button = gr.Button("Generate Response")
                generate_response_button.click(email_processor.generate_response, inputs=[body_field, subject_field], outputs=[Sentiment, Sentiment_score, reply_body_field])

            load_button.click(email_processor.load_emails, outputs=[from_field, subject_field, body_field, email_index])
            prev_button.click(lambda x: email_processor.navigate_emails("prev", x), inputs=[email_index], outputs=[from_field, subject_field, body_field, email_index])
            next_button.click(lambda x: email_processor.navigate_emails("next", x), inputs=[email_index], outputs=[from_field, subject_field, body_field, email_index])
            reply_button.click(email_processor.send_reply_and_move_next, 
                               inputs=[user_input, pass_input, email_index, reply_body_field], 
                               outputs=[response_label, from_field, subject_field, body_field, email_index, Sentiment, Sentiment_score, reply_body_field])

            response_label.change(email_processor.show_popup, inputs=[response_label])

        return app
    except Exception as e:
        logging.error(f"Error creating interface: {e}")
        raise

if __name__ == "__main__":
    try:
        email_processor = EmailProcessor()
        app = create_interface(email_processor)
        app.launch()
    except Exception as e:
        logging.error(f"Error launching application: {e}")
        raise
