"""
Test module for the Pinecone manager service.

This module contains unit tests for the PineconeManager class, which is responsible
for managing operations related to the Pinecone vector database. The tests cover
initialization, index creation, document upserting, and querying operations.
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
from app.services.database.pinecone_manager_service import PineconeManager
from pinecone import ServerlessSpec
from config import TestingConfig


@pytest.fixture
def mock_pinecone():
    """Create a mock for the Pinecone class."""
    with patch('app.services.database.pinecone_manager_service.Pinecone') as mock:
        yield mock


@pytest.fixture
def mock_openai_embeddings():
    """Create a mock for the OpenAIEmbeddings class."""
    with patch('app.services.database.pinecone_manager_service.OpenAIEmbeddings') as mock:
        yield mock


@pytest.fixture
def mock_document_schema():
    """Create a mock for the DocumentSchema class."""
    with patch('app.services.database.pinecone_manager_service.QueryandDocumentSchema') as mock:
        yield mock


def test_init_pinecone_manager(mock_pinecone, mock_openai_embeddings, mock_document_schema):
    """Test the initialization of the PineconeManager."""
    manager = PineconeManager(
        TestingConfig.PINECONE_API_KEY,
        TestingConfig.PINECONE_ENVIRONMENT,
        TestingConfig.PINECONE_INDEX_NAME,
        TestingConfig.OPENAI_API_KEY
    )
    
    assert manager.index_name == TestingConfig.PINECONE_INDEX_NAME
    assert manager.environment == TestingConfig.PINECONE_ENVIRONMENT
    mock_pinecone.assert_called_once_with(api_key=TestingConfig.PINECONE_API_KEY)
    mock_openai_embeddings.assert_called_once_with(model="text-embedding-ada-002")


@patch('app.services.database.pinecone_manager_service.Pinecone')
def test_ensure_index_exists(MockPinecone):
    """Test the ensure_index_exists method of PineconeManager."""
    mock_pinecone_instance = MockPinecone.return_value
    mock_list_indexes = MagicMock()
    mock_list_indexes.names.return_value = []
    mock_pinecone_instance.list_indexes.return_value = mock_list_indexes

    manager = PineconeManager(
        TestingConfig.PINECONE_API_KEY,
        TestingConfig.PINECONE_ENVIRONMENT,
        TestingConfig.PINECONE_INDEX_NAME,
        TestingConfig.OPENAI_API_KEY
    )

    MockPinecone.assert_called_once_with(api_key=TestingConfig.PINECONE_API_KEY)
    mock_pinecone_instance.list_indexes.assert_called_once()
    mock_pinecone_instance.create_index.assert_called_once_with(
        name=TestingConfig.PINECONE_INDEX_NAME,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region=TestingConfig.PINECONE_ENVIRONMENT.split('-')[0]
        )
    )
    mock_pinecone_instance.Index.assert_called_once_with(TestingConfig.PINECONE_INDEX_NAME)


def test_upsert_document(mock_pinecone, mock_openai_embeddings, mock_document_schema):
    """Test the upsert_document method of PineconeManager."""
    manager = PineconeManager(
        TestingConfig.PINECONE_API_KEY,
        TestingConfig.PINECONE_ENVIRONMENT,
        TestingConfig.PINECONE_INDEX_NAME,
        TestingConfig.OPENAI_API_KEY
    )
    mock_document = {
        'id': 'test_id',
        'content': 'Test content'
    }
    
    mock_embeddings = mock_openai_embeddings.return_value
    mock_embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3]]
    
    result = manager.upsert_document(mock_document)
    
    manager.index.upsert.assert_called_once()
    assert result == {"success": True, "vectors_upserted": 1}


def test_query_similar_documents(mock_pinecone, mock_openai_embeddings):
    """Test the query_similar_documents method of PineconeManager."""
    manager = PineconeManager(
        TestingConfig.PINECONE_API_KEY,
        TestingConfig.PINECONE_ENVIRONMENT,
        TestingConfig.PINECONE_INDEX_NAME,
        TestingConfig.OPENAI_API_KEY
    )
    mock_embeddings = mock_openai_embeddings.return_value
    mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
    
    manager.query_similar_documents("test query")
    
    manager.index.query.assert_called_once()


def test_ensure_index_exists_error(mock_pinecone):
    """Test error handling in the ensure_index_exists method of PineconeManager."""
    mock_pinecone.return_value.list_indexes.side_effect = Exception("Test error")
    
    with pytest.raises(Exception, match="Error ensuring index exists: Test error"):
        PineconeManager(
            TestingConfig.PINECONE_API_KEY,
            TestingConfig.PINECONE_ENVIRONMENT,
            TestingConfig.PINECONE_INDEX_NAME,
            TestingConfig.OPENAI_API_KEY
        )


@patch('app.services.database.pinecone_manager_service.logger')
def test_upsert_document_logging(mock_logger, mock_pinecone, mock_openai_embeddings, mock_document_schema):
    """Test logging in the upsert_document method of PineconeManager."""
    manager = PineconeManager(
        TestingConfig.PINECONE_API_KEY,
        TestingConfig.PINECONE_ENVIRONMENT,
        TestingConfig.PINECONE_INDEX_NAME,
        TestingConfig.OPENAI_API_KEY
    )
    mock_document = {
        'id': 'test_id',
        'content': 'Test content'
    }
    
    mock_embeddings = mock_openai_embeddings.return_value
    mock_embeddings.embed_documents.return_value = [[0.1, 0.2, 0.3]]
    
    manager.upsert_document(mock_document)
    
    mock_logger.info.assert_any_call("Starting upsert for document: test_id")
    mock_logger.info.assert_any_call("Created 1 chunks")
    mock_logger.info.assert_any_call("Created 1 embeddings")
    mock_logger.info.assert_any_call("Upserting 1 vectors to Pinecone")