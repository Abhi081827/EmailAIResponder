from langchain.text_splitter import RecursiveCharacterTextSplitter

class TextProcessor:
    """
    A class to handle the processing of text documents.
    """

    def __init__(self, chunk_size=1000, chunk_overlap=50):
        """
        Initializes the text processor with chunk size and overlap.

        :param chunk_size: Size of each text chunk.
        :param chunk_overlap: Overlap between consecutive text chunks.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)

    def split_text(self, documents):
        """
        Splits the documents into chunks.

        :param documents: List of documents to be split.
        :return: List of text chunks.
        """
        if not documents:
            raise ValueError("No documents provided for text splitting.")

        try:
            return self.splitter.split_documents(documents)
        except Exception as e:
            raise RuntimeError(f"Error in text processing: {e}")
