"""
This module provides the ChatService class for managing chat operations and document handling.

It integrates with OpenAI's language models, Pinecone vector store, and Google Drive
for processing queries and handling documents. The ChatService acts as a coordinator,
utilizing FileExtractor for text extraction and PineconeManager for vector operations.
"""

import logging
import time
import random
from functools import lru_cache
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore as Pinecone
from openai import RateLimitError
import os
from app.services.natural_language.file_extractor import FileExtractor
from app.services.database.pinecone_manager_service import PineconeManager

logger = logging.getLogger(__name__)

def retry_with_exponential_backoff(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 3,
    errors: tuple = (RateLimitError,),
):
    """
    Retry a function with exponential backoff.

    This decorator retries the function with an exponential backoff strategy
    if it raises specified errors.

    Args:
        func (callable): The function to be decorated.
        initial_delay (float): The initial delay between retries in seconds.
        exponential_base (float): The base for the exponential backoff.
        jitter (bool): Whether to add random jitter to the delay.
        max_retries (int): The maximum number of retries.
        errors (tuple): A tuple of error types to catch and retry on.

    Returns:
        callable: The decorated function.
    """
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
    and vector store. It coordinates operations between FileExtractor
    and PineconeManager.
    """

    def __init__(self, drive_core=None):
        """
        Initialize the ChatService with necessary components.

        Sets up the language model, vector store, and conversation chain
        using environment variables for API keys and configuration.

        Args:
            drive_core (DriveCore, optional): An instance of DriveCore for Google Drive operations.
        """
        logger.info("Initializing ChatService")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")
        self.pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")

        self.drive_core = drive_core

        self.llm = ChatOpenAI(temperature=0.2, 
                            model_name="gpt-4o-mini",
                            max_tokens=None,
                            timeout=None,
                            max_retries=2)
        
        # Initialize PineconeManager
        self.pinecone_manager = PineconeManager(
            api_key=self.pinecone_api_key,
            environment=self.pinecone_environment,
            index_name=self.pinecone_index_name,
            openai_api_key=self.openai_api_key
        )
        
        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        self.vectorstore = Pinecone(self.pinecone_manager.index, self.embeddings, "text")
        
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        self.qa = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(),
            memory=self.memory
        )

        # Initialize FileExtractor
        self.file_extractor = FileExtractor(drive_core=self.drive_core) if self.drive_core else None

        logger.info("ChatService initialized successfully")

    @retry_with_exponential_backoff
    def query(self, question, session_id):
        """
        Process a query and return a response.

        Args:
            question (str): The query string.
            session_id (str): The ID of the current session.

        Returns:
            str: The response from the language model.

        Raises:
            Exception: If an error occurs during query processing.
        """
        logger.info(f"Processing query for session {session_id}: {question}")
        try:
            result = self.qa.invoke({"question": question})
            logger.info(f"Query processed successfully, result: {result['answer']}")
            return result['answer']
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            raise

    @lru_cache(maxsize=1000)
    def get_embedding(self, text):
        """
        Get and cache embeddings for a given text.

        Args:
            text (str): The text to embed.

        Returns:
            list: The embedding vector.
        """
        return self.embeddings.embed_query(text)

    def process_and_add_file(self, file_id, file_name, session_id):
        """
        Process a file by extracting its text and then add it to the vector store.

        Args:
            file_id (str): The ID of the file in Google Drive.
            file_name (str): The name of the file to be processed.
            session_id (str): The ID of the current session.

        Returns:
            bool: True if successful, False otherwise.

        Raises:
            ValueError: If Drive functionality is not available.
        """
        if not self.file_extractor:
            raise ValueError("Drive functionality is not available. Please authenticate with Google Drive.")

        logger.info(f"Processing file: {file_name} with ID: {file_id} for session {session_id}")
        try:
            # Extract text using FileExtractor
            extracted_text = self.file_extractor.extract_text_from_file(file_id, file_name)
            
            # Create document structure
            document = {
                "id": file_id,
                "content": extracted_text
            }
            
            # Use PineconeManager to upsert the document
            result = self.pinecone_manager.upsert_document(document, session_id)
            
            if result['success']:
                logger.info(f"File {file_name} processed and added successfully")
                return True
            else:
                logger.error(f"Failed to process and add file: {result.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            logger.error(f"Error processing and adding file {file_name} with ID {file_id}: {str(e)}", exc_info=True)
            return False

    def delete_document(self, document_id, session_id):
        """
        Delete a document from the vector store.

        Args:
            document_id (str): The ID of the document to delete.
            session_id (str): The ID of the current session.

        Returns:
            bool: True if successful, False otherwise.
        """
        logger.info(f"Deleting document: {document_id} for session {session_id}")
        try:
            result = self.pinecone_manager.clear_session_vectors(session_id)
            if result['success']:
                logger.info(f"Document {document_id} deleted successfully")
                return True
            else:
                logger.error(f"Failed to delete document: {result.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}", exc_info=True)
            return False

    def clear_session(self, session_id):
        """
        Clear all vectors associated with a specific session.

        Args:
            session_id (str): The ID of the session to clear.

        Returns:
            dict: A dictionary indicating success and the number of vectors deleted.
        """
        logger.info(f"Clearing session: {session_id}")
        return self.pinecone_manager.clear_session_vectors(session_id)