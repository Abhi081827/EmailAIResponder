import os
from langchain.document_loaders import PyPDFLoader, DirectoryLoader, UnstructuredHTMLLoader, BSHTMLLoader
from langchain.document_loaders.pdf import PyPDFDirectoryLoader

class DocumentLoader:
    """
    A class to handle loading of documents from various sources.
    """

    def __init__(self, data_path):
        """
        Initializes the document loader with a given data path.
        
        :param data_path: Path to the data directory.
        """
        self.data_path = data_path
        self.loader = None

    def load_documents(self):
        """
        Loads documents from the specified data path.
        Handles errors related to path validity and document loading.

        :return: List of loaded documents.
        """
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"The specified path '{self.data_path}' does not exist.")

        try:
            # Assuming PDF files in a directory
            self.loader = PyPDFDirectoryLoader(self.data_path)
            documents = self.loader.load()

            if not documents:
                raise ValueError("No documents found in the specified path.")

            return documents

        except Exception as e:
            raise RuntimeError(f"Error loading documents: {e}")
