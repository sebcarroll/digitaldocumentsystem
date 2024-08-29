"""
This module provides the ChatService class for managing chat operations and document handling.

It integrates with OpenAI's language models, Pinecone vector store, and Google Drive
for processing queries and handling documents.
"""

import logging
import time
import random
import os
import re
import markdown
from functools import lru_cache
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_core.outputs import LLMResult
from langchain_pinecone import PineconeVectorStore as Pinecone
from pinecone import Pinecone as PineconeClient
from langchain.prompts import PromptTemplate
from openai import RateLimitError

from app.services.natural_language.file_extractor import FileExtractor
from app.services.database.pinecone_manager_service import PineconeManager
from app.services.google_drive.core import DriveCore
from app.services.google_drive.drive_service import DriveService

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

    def __init__(self, drive_core: Optional[DriveCore] = None, user_id: Optional[str] = None):
        """
        Initialize the ChatService with necessary components.

        Args:
            drive_core (DriveCore, optional): The DriveCore instance to use for file operations.
            user_id (str, optional): The ID of the user associated with this ChatService instance.
        """
        logger.info("Initializing ChatService")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")
        self.pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")

        self.drive_core = drive_core
        self.drive_service = DriveService(drive_core) if drive_core else None
        self.user_id = user_id

        if self.drive_core:
            self.file_extractor = FileExtractor(drive_core=self.drive_core)

        self.llm = ChatOpenAI(
            temperature=0.3,
            model_name="gpt-4o-mini",
            max_tokens=None,
            timeout=None,
            max_retries=2
        )
        
        self.pinecone_manager = PineconeManager(
            api_key=self.pinecone_api_key,
            environment=self.pinecone_environment,
            index_name=self.pinecone_index_name
        )
        
        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        self.vectorstore = Pinecone(self.pinecone_manager.index, self.embeddings, "text")
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            input_key="question",
            output_key="answer",
            return_messages=True
        )
        
        prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

        {context}

        {chat_history}

        Question: {question}
        Helpful Answer:"""

        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "chat_history", "question"]
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
        """
        Post-process the output text to convert markdown to HTML and apply custom formatting.

        Args:
            text (str): The input text in markdown format.

        Returns:
            str: The processed HTML output.
        """
        html = markdown.markdown(text)
            
        html = re.sub(r'<p>\|(.+)\|</p>', r'<table><tr><th>\1</th></tr>', html)
        html = re.sub(r'<p>\|[-:|\s]+\|</p>', '', html)
        html = re.sub(r'<p>\|(.+)\|</p>', r'<tr><td>\1</td></tr>', html)
        html = html.replace('</tr><table>', '</table>')
            
        html = re.sub(r'<p>(\d+\. .*?)</p>', r'<ol><li>\1</li></ol>', html)
        html = re.sub(r'<p>(- .*?)</p>', r'<ul><li>\1</li></ul>', html)
            
        return html

    def set_user_id(self, user_id: str) -> None:
        """
        Set the user ID for the ChatService instance.

        Args:
            user_id (str): The ID of the user to set.
        """
        self.user_id = user_id

    def has_drive_service(self) -> bool:
        """
        Check if the ChatService instance has a DriveService object.

        Returns:
            bool: True if DriveService is set, False otherwise.
        """
        return self.drive_service is not None

    def has_drive_core(self) -> bool:
        """
        Returns:
            bool: True if DriveService is set, False otherwise.
        """
        return self.drive_core is not None 

    def set_drive_core(self, drive_core: DriveCore) -> None:
        """
        Set or update the DriveCore instance for the ChatService.

        Args:
            drive_core (DriveCore): The DriveCore instance to set.
        """
        self.drive_core = drive_core
        self.drive_service = DriveService(drive_core)
        self.file_extractor = FileExtractor(drive_core=self.drive_core)
        logger.info("DriveCore and DriveService set for ChatService")

    @retry_with_exponential_backoff
    def query(self, question: str) -> str:
        """
        Process a query and return a response.

        Args:
            question (str): The query string.

        Returns:
            str: The response from the language model.

        Raises:
            ValueError: If user_id is not set.
            Exception: If an error occurs during query processing.
        """
        if not self.user_id:
            raise ValueError("User ID is not set. Call set_user_id() before querying.")

        logger.info(f"Processing query for user {self.user_id}: {question}")
        try:
            result = self.qa.invoke({"question": question})
            
            logger.debug(f"Raw result: {result}")
            logger.debug(f"Retrieved documents: {result.get('source_documents', [])}")
            logger.debug(f"Generated question: {result.get('generated_question', '')}")
            logger.debug(f"Chat history: {self.memory.chat_memory.messages}")
            
            if isinstance(result, dict):
                answer = result.get('answer', '')
            elif isinstance(result, LLMResult):
                answer = result.generations[0][0].text if result.generations else ''
            else:
                answer = str(result)
            
            processed_result = self.post_process_output(answer)
            return processed_result
        except Exception as e:
            logger.error(f"Error processing query for user {self.user_id}: {str(e)}", exc_info=True)
            raise

    def clear_memory(self):
        """Clear the conversation memory."""
        self.memory.clear()

    @lru_cache(maxsize=1000)
    def get_embedding(self, text: str) -> List[float]:
        """
        Get and cache embeddings for a given text.

        Args:
            text (str): The text to embed.

        Returns:
            List[float]: The embedding vector.
        """
        return self.embeddings.embed_query(text)

    def process_and_add_file(self, file_id: str, file_name: str) -> bool:
        """
        Process a file by extracting its text and then add it to the vector store.

        Args:
            file_id (str): The ID of the file in Google Drive.
            file_name (str): The name of the file to be processed.

        Returns:
            bool: True if successful, False otherwise.

        Raises:
            ValueError: If user_id is not set or if DriveService is not set.
        """
        if not self.user_id:
            raise ValueError("User ID is not set. Call set_user_id() before processing files.")
        if not self.drive_service:
            raise ValueError("DriveService is not set. Cannot process file.")

        logger.info(f"Processing file for user {self.user_id}: {file_name} with ID: {file_id}")
        try:
            file_details = self.drive_service.get_file_details(file_id)
            extracted_text = self.file_extractor.extract_text_from_drive_file(file_id, file_name)
            document = {
                "id": file_id,
                "user_id": self.user_id,
                "content": extracted_text,
                "lastModified": file_details.get('modifiedTime'),
                "isSelected": True 
            }
            result = self.pinecone_manager.upsert_document(document, self.user_id)
            return result['success']
        except Exception as e:
            logger.error(f"Error processing file {file_name} with ID {file_id} for user {self.user_id}: {str(e)}", exc_info=True)
            return False

    def update_document_selection(self, file_id: str, is_selected: bool) -> bool:
        """
        Update the selection status of a document.

        Args:
            file_id (str): The Google Drive file ID of the document.
            is_selected (bool): The new selection status.

        Returns:
            bool: True if the update was successful, False otherwise.

        Raises:
            ValueError: If user_id is not set.
        """
        if not self.user_id:
            raise ValueError("User ID is not set. Call set_user_id() before updating document selection.")

        return self.pinecone_manager.update_document_selection(file_id, is_selected, self.user_id)

    def delete_document(self, file_id: str) -> bool:
        """
        Delete a document from the vector store.

        Args:
            file_id (str): The Google Drive file ID of the document to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.

        Raises:
            ValueError: If user_id is not set.
        """
        if not self.user_id:
            raise ValueError("User ID is not set. Call set_user_id() before deleting documents.")

        return self.pinecone_manager.delete_document(file_id, self.user_id)
    
    def process_and_add_multiple_files(self, file_ids: List[str], file_names: List[str]) -> Dict[str, Any]:
        """
        Process multiple files and add them to the vector store.

        Args:
            file_ids (List[str]): The IDs of the files in Google Drive.
            file_names (List[str]): The names of the files to be processed.

        Returns:
            Dict[str, Any]: A dictionary containing the number of successful uploads and total files.

        Raises:
            ValueError: If user_id is not set or if DriveService is not set.
        """
        if not self.user_id:
            raise ValueError("User ID is not set. Call set_user_id() before processing files.")
        if not self.drive_service:
            raise ValueError("DriveService is not set. Cannot process files.")

        successful_uploads = 0
        total_files = len(file_ids)

        for file_id, file_name in zip(file_ids, file_names):
            success = self.process_and_add_file(file_id, file_name)
            if success:
                successful_uploads += 1

        return {
            "successful_uploads": successful_uploads,
            "total_files": total_files
        }