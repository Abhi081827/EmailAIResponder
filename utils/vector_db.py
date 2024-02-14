import logging
from langchain.vectorstores import Chroma


class VectorDatabase:
    """
    A class for creating and managing a vector database.
    """

    def __init__(self, db_path, embedding_model):
        """
        Initializes the vector database with a database path and embedding model.

        :param db_path: Path to store the vector database.
        :param embedding_model: Embedding model to use for vector creation.
        """
        self.db_path = db_path
        self.embedding_model = embedding_model
        self.vectorstore = None
        self.logger = logging.getLogger(__name__)

    def create_vector_db(self, documents):
        """
        Creates a vector database from the provided documents.
        Handles errors related to vector creation and persistence.

        :param documents: List of documents to be converted into vectors.
        """
        if not documents:
            self.logger.error("No documents provided for vector database creation.")
            raise ValueError("No documents provided for vector database creation.")

        try:
            self.vectorstore = Chroma.from_documents(documents=documents, embedding=self.embedding_model, persist_directory=self.db_path)
            self.vectorstore.persist()
            self.logger.info(f"Vector database created with {len(documents)} documents.")
        except Exception as e:
            self.logger.exception(f"Error in creating vector database: {e}")
            raise RuntimeError(f"Error in creating vector database: {e}")
