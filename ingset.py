# main.py

import logging
from utils.loaders import DocumentLoader
from utils.text_processing import TextProcessor
from utils.vector_db import VectorDatabase
from config import DATA_PATH, DB_PATH, EMBED_MODEL_NAME
from langchain_community.embeddings import HuggingFaceEmbeddings
from utils.logging_config import setup_logging
import os

setup_logging()


def main():
    """
    Main function to create the vector database from documents.
    """
    try:
        # Initialize the document loader
        doc_loader = DocumentLoader(DATA_PATH)
        documents = doc_loader.load_documents()
        logging.info(f"Processed {len(documents)} pdf files")

        # Check if documents are loaded
        if not documents:
            raise ValueError("No documents loaded. Check your DATA_PATH.")

        # Initialize and apply text processor
        text_processor = TextProcessor()
        texts = text_processor.split_text(documents)

        # Initialize and create vector database
        embed_model = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)
        vector_db = VectorDatabase(DB_PATH, embed_model)
        vector_db.create_vector_db(texts)

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
