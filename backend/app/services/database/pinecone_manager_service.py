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
                "isSelected": document['isSelected']
            }
            self.index.upsert(vectors=[(document['id'], embedding, metadata)], namespace=user_id)
            return {"success": True, "vectors_upserted": 1}
        except Exception as e:
            logger.error(f"Error upserting document {document['id']} for user {user_id}: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    def query_similar_documents(self, query: str, user_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query the Pinecone index for similar documents.

        Args:
            query (str): The query string.
            user_id (str): The ID of the user performing the query.
            top_k (int): The number of top results to return.

        Returns:
            List[Dict[str, Any]]: A list of the top similar documents.
        """
        query_embedding = self.embeddings.embed_query(query)
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter={"isSelected": True},
            namespace=user_id
        )
        return results['matches']

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