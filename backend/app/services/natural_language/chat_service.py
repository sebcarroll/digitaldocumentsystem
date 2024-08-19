"""
Service module for handling chat and document operations.

This module provides a ChatService class that manages interactions with
a language model, vector store, and document handling operations.
"""

import logging
import time
import random
from functools import lru_cache
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import Pinecone
from pinecone import Pinecone as PineconeClient
from openai import RateLimitError
import os

logger = logging.getLogger(__name__)

def retry_with_exponential_backoff(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 3,
    errors: tuple = (RateLimitError,),
):
    """Retry a function with exponential backoff."""
    def wrapper(*args, **kwargs):
        num_retries = 0
        delay = initial_delay

        while True:
            try:
                return func(*args, **kwargs)
            except errors as e:
                num_retries += 1
                if num_retries > max_retries:
                    raise Exception(f"Maximum number of retries ({max_retries}) exceeded.")

                delay *= exponential_base * (1 + jitter * random.random())

                logger.warning(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)

    return wrapper

class ChatService:
    """
    Service class for managing chat operations and document handling.

    This class initializes and manages the components needed for
    processing queries and handling documents using a language model
    and vector store.
    """

    def __init__(self):
        """
        Initialize the ChatService with necessary components.

        Sets up the language model, vector store, and conversation chain
        using environment variables for API keys and configuration.
        """
        logger.info("Initializing ChatService")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")
        self.pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")

        self.llm = ChatOpenAI(temperature=0, 
                              model_name="gpt-40-mini",
                              max_tokens=None,
                              timeout=None,
                              max_retries=2,)
        
        # Initialize Pinecone client
        pc = PineconeClient(api_key=self.pinecone_api_key, environment=self.pinecone_environment)
        self.index = pc.Index(self.pinecone_index_name)
        
        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        self.vectorstore = Pinecone(self.index, self.embeddings, "text")
        
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        self.qa = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(),
            memory=self.memory
        )
        logger.info("ChatService initialized successfully")

    @retry_with_exponential_backoff
    def query(self, question):
        """
        Process a query and return a response.

        Args:
            question (str): The query string.

        Returns:
            str: The response from the language model.

        Raises:
            Exception: If an error occurs during query processing.
        """
        logger.info(f"Processing query: {question}")
        try:
            result = self.qa.invoke({"question": question})  # Using invoke instead of __call__
            logger.info(f"Query processed successfully, result: {result['answer']}")
            return result['answer']
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            raise

    @lru_cache(maxsize=1000)
    def get_embedding(self, text):
        """Get and cache embeddings for a given text."""
        return self.embeddings.embed_query(text)

    def add_document(self, document):
        """
        Add a document to the vector store.

        Args:
            document (dict): The document to add, containing 'id' and 'content'.

        Returns:
            bool: True if successful, False otherwise.
        """
        logger.info(f"Adding document: {document['id']}")
        try:
            texts = [document['content']]
            metadatas = [{"source": document['id']}]
            self.vectorstore.add_texts(texts=texts, metadatas=metadatas)
            logger.info(f"Document {document['id']} added successfully")
            return True
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}", exc_info=True)
            return False

    def delete_document(self, document_id):
        """
        Delete a document from the vector store.

        Args:
            document_id (str): The ID of the document to delete.

        Returns:
            bool: True if successful, False otherwise.
        """
        logger.info(f"Deleting document: {document_id}")
        try:
            self.vectorstore.delete(ids=[document_id])
            logger.info(f"Document {document_id} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}", exc_info=True)
            return False