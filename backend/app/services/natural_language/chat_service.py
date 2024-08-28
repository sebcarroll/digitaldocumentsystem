"""
This module provides the ChatService class for managing chat operations and document handling.

It integrates with OpenAI's language models, Pinecone vector store, and Google Drive
for processing queries and handling documents.
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
from pinecone import Pinecone as PineconeClient
from openai import RateLimitError
import os
from app.services.natural_language.file_extractor import FileExtractor
import re
import markdown
from langchain.prompts import PromptTemplate

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

    def __init__(self, drive_core=None):
        """
        Initialize the ChatService with necessary components.

        Args:
            drive_core (DriveCore, optional): The DriveCore instance to use for file operations.
        """
        logger.info("Initializing ChatService")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")
        self.pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")

        self.drive_core = drive_core
        if self.drive_core:
            self.file_extractor = FileExtractor(drive_core=self.drive_core)

        self.llm = ChatOpenAI(
            temperature=0.3,
            model_name="gpt-4o-mini",
            max_tokens=None,
            timeout=None,
            max_retries=2
        )
        
        # Initialize Pinecone client
        pc = PineconeClient(api_key=self.pinecone_api_key, environment=self.pinecone_environment)
        self.index = pc.Index(self.pinecone_index_name)
        
        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        self.vectorstore = Pinecone(self.index, self.embeddings, "text")
        
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

        {context}

        {chat_history}

        Question: {question}
        Helpful Answer:"""

        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "chat_history", "question"]
        )

        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            input_key="question",
            output_key="answer",
            return_messages=True
        )

        self.qa = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 5}),
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": PROMPT},
            return_source_documents=True,
            return_generated_question=True,
            verbose=True
        )

    def post_process_output(self, text):
        html = markdown.markdown(text)
            
        html = re.sub(r'<p>\|(.+)\|</p>', r'<table><tr><th>\1</th></tr>', html)
        html = re.sub(r'<p>\|[-:|\s]+\|</p>', '', html)
        html = re.sub(r'<p>\|(.+)\|</p>', r'<tr><td>\1</td></tr>', html)
        html = html.replace('</tr><table>', '</table>')
            
        html = re.sub(r'<p>(\d+\. .*?)</p>', r'<ol><li>\1</li></ol>', html)
        html = re.sub(r'<p>(- .*?)</p>', r'<ul><li>\1</li></ul>', html)
            
        return html

    def set_drive_core(self, drive_core):
        """
        Set or update the DriveCore instance for the ChatService.

        Args:
            drive_core (DriveCore): The DriveCore instance to set.
        """
        self.drive_core = drive_core
        self.file_extractor = FileExtractor(drive_core=self.drive_core)
        logger.info("DriveCore set for ChatService")

    def has_drive_core(self):
        """
        Check if the ChatService has a DriveCore instance.

        Returns:
            bool: True if DriveCore is set, False otherwise.
        """
        return self.drive_core is not None

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
            result = self.qa({"question": question})
            logger.debug(f"Raw result: {result}")
            logger.debug(f"Retrieved documents: {result.get('source_documents', [])}")
            logger.debug(f"Generated question: {result.get('generated_question', '')}")
            logger.debug(f"Chat history: {self.memory.chat_memory.messages}")
            
            # Extract the answer from the result
            answer = result['answer']
            
            processed_result = self.post_process_output(answer)
            return processed_result
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            raise

    def clear_memory(self):
        self.memory.clear()

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

    def process_and_add_file(self, file_id, file_name):
        """
        Process a file by extracting its text and then add it to the vector store.

        Args:
            file_id (str): The ID of the file in Google Drive.
            file_name (str): The name of the file to be processed.

        Returns:
            bool: True if successful, False otherwise.
        """
        logger.info(f"Processing file: {file_name} with ID: {file_id}")
        try:
            if not self.has_drive_core():
                raise ValueError("DriveCore not set. Cannot process file.")
            
            # Extract text using FileExtractor
            extracted_text = self.file_extractor.extract_text_from_drive_file(file_id, file_name)
            document = {
                "id": file_id,
                "content": extracted_text
            }
            # Add the extracted text to the vector store
            return self.add_document(document)
        except Exception as e:
            logger.error(f"Error processing and adding file {file_name} with ID {file_id}: {str(e)}", exc_info=True)
            return False