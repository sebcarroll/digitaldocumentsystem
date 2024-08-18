"""
This module provides the PineconeManager class for handling operations with the Pinecone vector database.
"""

import logging
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class PineconeManager:
    """Manages operations related to Pinecone vector database."""

    def __init__(self, api_key, environment, index_name, openai_api_key):
        """
        Initialize the PineconeManager.

        Args:
            api_key (str): The Pinecone API key.
            environment (str): The Pinecone environment.
            index_name (str): The name of the Pinecone index.
            openai_api_key (str): The OpenAI API key.
        """
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self.openai_api_key = openai_api_key
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=api_key)

        # Get the index
        self.index = self.pc.Index(index_name)
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

        # Dictionary to keep track of vector IDs added in each session
        self.session_vectors = {}

    def upsert_document(self, document, session_id):
        """
        Upsert a document into the Pinecone index for the current session.

        Args:
            document (dict): The document to upsert, containing 'id' and 'content'.
            session_id (str): The ID of the current session.

        Returns:
            dict: A dictionary indicating success and the number of vectors upserted.
        """
        try:
            logger.info(f"Starting upsert for document: {document['id']} in session: {session_id}")
            
            chunks = self.text_splitter.split_text(document['content'])
            logger.info(f"Created {len(chunks)} chunks")
            
            embeddings = self.embeddings.embed_documents(chunks)
            logger.info(f"Created {len(embeddings)} embeddings")
            
            vectors = []
            vector_ids = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_id = f"{session_id}_{document['id']}_{i}"
                vector_ids.append(chunk_id)
                
                chunk_metadata = {
                    "document_id": str(document['id']),
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "session_id": session_id
                }
                vectors.append({
                    "id": chunk_id,
                    "values": embedding,
                    "metadata": chunk_metadata
                })
            
            logger.info(f"Upserting {len(vectors)} vectors to Pinecone")
            upsert_response = self.index.upsert(vectors=vectors)
            logger.info(f"Upsert response: {upsert_response}")
            
            # Keep track of vector IDs added in this session
            self.session_vectors[session_id] = self.session_vectors.get(session_id, []) + vector_ids
            
            return {"success": True, "vectors_upserted": len(vectors)}
        except Exception as e:
            logger.error(f"Error upserting document {document['id']}: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    def clear_session_vectors(self, session_id):
        """
        Clear all vectors associated with a specific session.

        Args:
            session_id (str): The ID of the session to clear.

        Returns:
            dict: A dictionary indicating success and the number of vectors deleted.
        """
        try:
            vectors_to_delete = self.session_vectors.get(session_id, [])
            if vectors_to_delete:
                self.index.delete(ids=vectors_to_delete)
                del self.session_vectors[session_id]
                logger.info(f"Cleared {len(vectors_to_delete)} vectors for session {session_id}")
                return {"success": True, "vectors_deleted": len(vectors_to_delete)}
            else:
                logger.info(f"No vectors to clear for session {session_id}")
                return {"success": True, "vectors_deleted": 0}
        except Exception as e:
            logger.error(f"Error clearing vectors for session {session_id}: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}
