"""Module for managing Pinecone database operations."""

import logging
from typing import Dict, Any, List
from datetime import datetime
from pinecone import Pinecone as PineconeClient
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger(__name__)

class PineconeManager:
    """Manages operations related to Pinecone vector database."""

    def __init__(self, api_key: str, environment: str, index_name: str, openai_api_key: str = None):
        """
        Initialize the PineconeManager.

        Args:
            api_key (str): The Pinecone API key.
            environment (str): The Pinecone environment.
            index_name (str): The name of the Pinecone index.
            openai_api_key (str, optional): The OpenAI API key for embeddings.
        """
        self.pc = PineconeClient(api_key=api_key, environment=environment)
        self.index = self.pc.Index(index_name)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=openai_api_key)

    def upsert_document(self, document: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Upsert a document into the Pinecone index.

        Args:
            document (Dict[str, Any]): The document to upsert, including 'id', 'content', 'lastModified', and 'isSelected'.
            user_id (str): The ID of the user who owns the document.

        Returns:
            Dict[str, Any]: A dictionary indicating success and the number of vectors upserted.
        """
        try:
            embedding = self.embeddings.embed_query(document['content'])
            metadata = {
                "googleDriveFileId": document['id'],
                "lastModified": document['lastModified'],
                "isSelected": document['isSelected'],
                "content": document['content']  # Store the full content in metadata
            }
            self.index.upsert(vectors=[(document['id'], embedding, metadata)], namespace=user_id)
            return {"success": True, "vectors_upserted": 1}
        except Exception as e:
            logger.error(f"Error upserting document {document['id']} for user {user_id}: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    def update_document_selection(self, file_id: str, is_selected: bool, user_id: str) -> bool:
        """
        Update the selection status of a document.

        Args:
            file_id (str): The Google Drive file ID of the document.
            is_selected (bool): The new selection status.
            user_id (str): The ID of the user who owns the document.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        try:
            self.index.update(id=file_id, set_metadata={"isSelected": is_selected}, namespace=user_id)
            return True
        except Exception as e:
            logger.error(f"Error updating selection for document {file_id} for user {user_id}: {str(e)}", exc_info=True)
            return False

    def delete_document(self, file_id: str, user_id: str) -> bool:
        """
        Delete a document from the Pinecone index.

        Args:
            file_id (str): The Google Drive file ID of the document to delete.
            user_id (str): The ID of the user who owns the document.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        try:
            self.index.delete(ids=[file_id], namespace=user_id)
            return True
        except Exception as e:
            logger.error(f"Error deleting document {file_id} for user {user_id}: {str(e)}", exc_info=True)
            return False
        
    def get_selected_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all selected documents for a given user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            List[Dict[str, Any]]: A list of selected documents and their metadata.
        """
        try:
            results = self.index.query(
                vector=[0] * 1536,  # Dummy vector, not used for filtering
                top_k=10000,  # Set to a high number to retrieve all documents
                include_metadata=True,
                filter={"isSelected": True},
                namespace=user_id
            )
            
            logger.info(f"Retrieved selected documents for user {user_id}:")
            logger.info(f"Number of selected documents: {len(results['matches'])}")
            for match in results['matches']:
                logger.info(f"Document ID: {match['id']}")
                logger.info(f"Metadata: {match['metadata']}")
            
            return results['matches']
        except Exception as e:
            logger.error(f"Error retrieving selected documents for user {user_id}: {str(e)}", exc_info=True)
            return []

    def update_all_selected_documents(self, user_id: str, is_selected: bool) -> bool:
        """
        Update the selection status of all documents for a given user.

        This method fetches all documents for the specified user and updates their status
        to the provided is_selected value.

        Args:
            user_id (str): The ID of the user whose documents are to be updated.
            is_selected (bool): The new selection status to be applied to all documents.

        Returns:
            bool: True if the update operation was successful, False otherwise.

        Raises:
            Exception: If there's an error during the update process.
        """
        try:
            # Fetch all documents for the user
            results = self.index.query(
                vector=[0] * 1536,  # Dummy vector, not used for filtering
                top_k=10000,  # Set to a high number to retrieve all documents
                include_metadata=True,
                namespace=user_id
            )

            # Update each document
            for match in results['matches']:
                document_id = match['id']
                self.update_document_selection(document_id, is_selected, user_id)

            logger.info(f"Updated selection status to {is_selected} for all documents of user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating all documents for user {user_id}: {str(e)}", exc_info=True)
            return False
        
    def get_document_metadata(self, file_id: str, user_id: str) -> Dict[str, Any]:
        """
        Retrieve metadata for a specific document.

        Args:
            file_id (str): The Google Drive file ID of the document.
            user_id (str): The ID of the user who owns the document.

        Returns:
            Dict[str, Any]: The document's metadata if found, empty dict otherwise.
        """
        try:
            results = self.index.fetch(ids=[file_id], namespace=user_id)
            if results and file_id in results['vectors']:
                return results['vectors'][file_id]['metadata']
            return {}
        except Exception as e:
            logger.error(f"Error retrieving metadata for document {file_id} for user {user_id}: {str(e)}", exc_info=True)
            return {}