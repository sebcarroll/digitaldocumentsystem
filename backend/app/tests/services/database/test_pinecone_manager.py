import pytest
from unittest.mock import patch, Mock, MagicMock
from app.services.database.pinecone_manager import PineconeManager, Pinecone
from pinecone import ServerlessSpec

@pytest.fixture
def mock_pinecone():
    with patch('app.services.database.pinecone_manager.Pinecone') as mock:
        yield mock

@pytest.fixture
def mock_openai_embeddings():
    with patch('app.services.database.pinecone_manager.OpenAIEmbeddings') as mock:
        yield mock

@pytest.fixture
def mock_document_schema():
    with patch('app.services.database.pinecone_manager.DocumentSchema') as mock:
        yield mock

def test_init_pinecone_manager(mock_pinecone, mock_openai_embeddings, mock_document_schema):
    manager = PineconeManager('fake_api_key', 'fake_environment', 'fake_index', 'fake_openai_key')
    
    assert manager.index_name == 'fake_index'
    assert manager.environment == 'fake_environment'
    mock_pinecone.assert_called_once_with(api_key='fake_api_key')
    mock_openai_embeddings.assert_called_once_with(openai_api_key='fake_openai_key')


@patch('app.services.database.pinecone_manager.Pinecone')
def test_ensure_index_exists(MockPinecone):
    mock_pinecone_instance = MagicMock()
    MockPinecone.return_value = mock_pinecone_instance

    mock_list_indexes = MagicMock()
    mock_list_indexes.names.return_value = []
    mock_pinecone_instance.list_indexes.return_value = mock_list_indexes

    manager = PineconeManager('fake_api_key', 'fake_environment', 'fake_index', 'fake_openai_key')

    MockPinecone.assert_called_once_with(api_key='fake_api_key')

    mock_pinecone_instance.list_indexes.assert_called_once()

    mock_pinecone_instance.create_index.assert_called_once_with(
        name='fake_index',
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="fake_environment"
        )
    )

    mock_pinecone_instance.Index.assert_called_once_with('fake_index')

def test_upsert_document(mock_pinecone, mock_openai_embeddings, mock_document_schema):
    manager = PineconeManager('fake_api_key', 'fake_environment', 'fake_index', 'fake_openai_key')
    mock_document = Mock()
    mock_document.content = "Test content"
    mock_document.id = "test_id"
    
    mock_openai_embeddings.return_value.embed_documents.return_value = [[0.1, 0.2, 0.3]]
    mock_document_schema.return_value.dump.return_value = {'id': 'test_id'}
    
    manager.upsert_document(mock_document)
    
    manager.index.upsert.assert_called_once()

def test_query_similar_documents(mock_pinecone, mock_openai_embeddings):
    manager = PineconeManager('fake_api_key', 'fake_environment', 'fake_index', 'fake_openai_key')
    mock_openai_embeddings.return_value.embed_query.return_value = [0.1, 0.2, 0.3]
    
    manager.query_similar_documents("test query")
    
    manager.index.query.assert_called_once()

def test_delete_document(mock_pinecone):
    manager = PineconeManager('fake_api_key', 'fake_environment', 'fake_index', 'fake_openai_key')
    
    manager.delete_document("test_id")
    
    manager.index.delete.assert_called_once_with(filter={"id": {"$eq": "test_id"}})