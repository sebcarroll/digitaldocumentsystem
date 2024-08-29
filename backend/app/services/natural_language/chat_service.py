"""
This module provides the ChatService class for managing chat operations and document handling.

It integrates with OpenAI's language models, Pinecone vector store, and Google Drive
for processing queries and handling documents.
"""

import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_pinecone import PineconeVectorStore as Pinecone
from langchain.prompts import PromptTemplate

from app.services.natural_language.file_extractor import FileExtractor
from app.services.database.pinecone_manager_service import PineconeManager

logger = logging.getLogger(__name__)

class ChatService:
    """
    Service class for managing chat operations and document handling.

    This class initializes and manages the components needed for
    processing queries and handling documents using a language model
    and vector store.
    """

    def __init__(self, drive_core=None, user_id: Optional[str] = None):
        """
        Initialize the ChatService with necessary components.

        Args:
            drive_core (DriveCore, optional): The DriveCore instance to use for file operations.
            user_id (str, optional): The ID of the user associated with this ChatService instance.
        """
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")
        self.pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")

        self.drive_core = drive_core
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
        
        self.vectorstore = Pinecone(self.pinecone_manager.index, self.pinecone_manager.embeddings, "text")
        
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
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

    def set_user_id(self, user_id: str) -> None:
        """
        Set the user ID for the ChatService instance.

        Args:
            user_id (str): The ID of the user to set.
        """
        self.user_id = user_id

    def has_drive_core(self) -> bool:
        """
        Check if the ChatService instance has a DriveCore object.

        Returns:
            bool: True if DriveCore is set, False otherwise.
        """
        return self.drive_core is not None

    def query(self, question: str) -> str:
        """
        Process a query and return a response.

        Args:
            question (str): The query string.

        Returns:
            str: The response from the language model.

        Raises:
            ValueError: If user_id is not set.
        """
        if not self.user_id:
            raise ValueError("User ID is not set. Call set_user_id() before querying.")

        try:
            result = self.qa.invoke({"question": question})
            return result.get('answer', '')
        except Exception as e:
            logger.error(f"Error processing query for user {self.user_id}: {str(e)}", exc_info=True)
            raise

    def process_and_add_file(self, file_id: str, file_name: str) -> bool:
        """
        Process a file by extracting its text and then add it to the vector store.

        Args:
            file_id (str): The ID of the file in Google Drive.
            file_name (str): The name of the file to be processed.

        Returns:
            bool: True if successful, False otherwise.

        Raises:
            ValueError: If user_id is not set or if DriveCore is not set.
        """
        if not self.user_id:
            raise ValueError("User ID is not set. Call set_user_id() before processing files.")
        if not self.drive_core:
            raise ValueError("DriveCore is not set. Cannot process file.")

        try:
            file_details = self.drive_core.get_file_details(file_id)
            extracted_text = self.file_extractor.extract_text_from_drive_file(file_id, file_name)
            document = {
                "id": file_id,
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