"""Module for managing Pinecone database operations."""

from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from database.schemas.document import DocumentSchema
import logging

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
        self.document_schema = DocumentSchema()         
        # Initialize Pinecone
        self.pc = Pinecone(api_key=api_key)
        
        # Ensure index exists
        self.ensure_index_exists()
        
        # Get the index
        self.index = self.pc.Index(index_name)
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

    def ensure_index_exists(self):
        """Ensure that the specified Pinecone index exists, creating it if necessary."""
        try:
            existing_indexes = self.pc.list_indexes().names()
            if self.index_name not in existing_indexes:
                logger.info(f"Creating new index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=1536, 
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=self.environment.split('-')[0]
                    )
                )
            else:
                logger.info(f"Index {self.index_name} already exists")
        except Exception as e:
            error_message = f"Error ensuring index exists: {str(e)}"
            logger.error(error_message)
            raise Exception(error_message)

    def upsert_document(self, document):
        """
        Upsert a document into the Pinecone index.

        Args:
            document (dict): The document to upsert.

        Returns:
            dict: A dictionary indicating success and the number of vectors upserted.
        """
        try:
            logger.info(f"Starting upsert for document: {document['id']}")
            chunks = self.text_splitter.split_text(document['content'])
            logger.info(f"Created {len(chunks)} chunks")
            
            embeddings = self.embeddings.embed_documents(chunks)
            logger.info(f"Created {len(embeddings)} embeddings")
            
            vectors = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_id = f"{str(document['id'])}_{i}"
                chunk_metadata = {
                    **document,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "chunk_content": chunk
                }
                vectors.append({
                    "id": chunk_id,
                    "values": embedding,
                    "metadata": chunk_metadata
                })
            
            logger.info(f"Upserting {len(vectors)} vectors to Pinecone")
            upsert_response = self.index.upsert(vectors=vectors)
            logger.info(f"Upsert response: {upsert_response}")
            
            return {"success": True, "vectors_upserted": len(vectors)}
        except Exception as e:
            logger.error(f"Error upserting document {document['id']}: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}
        
    def query_similar_documents(self, query, top_k=5, filter=None):
        """
        Query the Pinecone index for similar documents.

        Args:
            query (str): The query string.
            top_k (int): The number of top results to return.
            filter (dict): An optional filter for the query.

        Returns:
            dict: The query results from Pinecone.
        """
        query_embedding = self.embeddings.embed_query(query)
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_values=True,
            include_metadata=True,
            filter=filter
        )
        return results
    
    def delete_document(self, document_id):
        """
        Delete a document from the Pinecone index once a query has been completed and the interface has been closed.
        
        Args:
        document_id (str): The ID of the document that is to be deleted.

        Returns:

        """
