import logging
import os
# Setting up logging to save to file
logs_dir = "logs"
log_filename = os.path.join(logs_dir, 'app.log')
def setup_logging():
    """
    Sets up the logging configuration for the application.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        filename=log_filename,  # Log to a file named 'app.log'. Adjust the path as needed.
        filemode='a'  # Append mode
    )
