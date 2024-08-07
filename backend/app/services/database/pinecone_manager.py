from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from database.schemas.document import DocumentSchema
import openai
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class PineconeManager:
    def __init__(self, api_key, environment, index_name, openai_api_key):
        logger.info(f"Initializing PineconeManager with index name: {index_name}")
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.environment = environment
        self.ensure_index_exists()
        logger.info(f"Connecting to index: {index_name}")
        self.index = self.pc.Index(index_name)
        logger.info("Successfully connected to Pinecone index")
        self.document_schema = DocumentSchema()
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

    def ensure_index_exists(self):
        try:
            existing_indexes = [index_info['name'] for index_info in self.pc.list_indexes()]
            if self.index_name not in existing_indexes:
                logger.info(f"Creating new index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=1536,  # OpenAI embeddings are 1536 dimensions
                    metric="cosine",
                    spec=pinecone.ServerlessSpec(
                        cloud=pinecone.Cloud.AWS,
                        region=self.environment.split('-')[0]  # Extracts 'eu-west-1' from 'eu-west-1-aws'
                    )
                )
            else:
                logger.info(f"Index {self.index_name} already exists")
        except Exception as e:
            logger.error(f"Error ensuring index exists: {str(e)}")
            raise

    def upsert_document(self, document):
        chunks = self.text_splitter.split_text(document.content)
        embeddings = self.embeddings.embed_documents(chunks)
        
        metadata = self.document_schema.dump(document)
        vectors = []
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = f"{str(document.id)}_{i}"
            chunk_metadata = {
                **metadata,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "chunk_content": chunk
            }
            vectors.append({
                "id": chunk_id,
                "values": embedding,
                "metadata": chunk_metadata
            })
        
        self.index.upsert(vectors=vectors)

    def query_similar_documents(self, query, top_k=5, filter=None):
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
        self.index.delete(filter={"id": {"$eq": document_id}})

    # Add more methods as needed