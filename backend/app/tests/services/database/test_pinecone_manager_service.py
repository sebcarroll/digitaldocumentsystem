"""
Unit tests for the PineconeManager class.

This module contains a set of pytest-based unit tests for the PineconeManager class,
which is responsible for managing operations related to the Pinecone vector database.
These tests cover various functionalities including document upserting, updating,
deleting, and retrieving, as well as content splitting and metadata management.
"""

import pytest
from unittest.mock import Mock, patch
from app.services.database.pinecone_manager_service import PineconeManager


@pytest.fixture
def pinecone_manager():
    """
    Fixture to create a PineconeManager instance with mocked dependencies.

    Returns:
        PineconeManager: An instance of PineconeManager for testing.
    """
    with patch('app.services.database.pinecone_manager_service.PineconeClient'), \
         patch('app.services.database.pinecone_manager_service.OpenAIEmbeddings'):
        return PineconeManager("api_key", "environment", "index_name", "openai_api_key")


def test_split_content(pinecone_manager):
    """
    Test the split_content method of PineconeManager.

    This test verifies that content is correctly split into chunks of specified size.

    Args:
        pinecone_manager (PineconeManager): The PineconeManager instance to test.
    """
    content = "a" * 100000
    chunks = pinecone_manager.split_content(content, chunk_size=38000)
    assert len(chunks) == 3
    assert all(len(chunk.encode('utf-8')) <= 38000 for chunk in chunks)


def test_upsert_document(pinecone_manager):
    """
    Test the upsert_document method of PineconeManager.

    This test verifies that a document is correctly upserted into the Pinecone index.

    Args:
        pinecone_manager (PineconeManager): The PineconeManager instance to test.
    """
    pinecone_manager.embeddings.embed_query.return_value = [0] * 1536
    document = {
        "id": "test_id",
        "content": "test content",
        "lastModified": "2023-01-01",
        "isSelected": True
    }
    result = pinecone_manager.upsert_document(document, "user_id")
    assert result["success"] is True
    assert result["vectors_upserted"] == 1
    pinecone_manager.index.upsert.assert_called_once()


def test_update_document_selection(pinecone_manager):
    """
    Test the update_document_selection method of PineconeManager.

    This test verifies that the selection status of a document is correctly updated.

    Args:
        pinecone_manager (PineconeManager): The PineconeManager instance to test.
    """
    pinecone_manager.index.query.return_value = {
        'matches': [{'id': 'test_id'}]
    }
    result = pinecone_manager.update_document_selection("file_id", True, "user_id")
    assert result is True
    pinecone_manager.index.update.assert_called_once_with(
        id='test_id', set_metadata={"isSelected": True}, namespace="user_id"
    )


def test_delete_document(pinecone_manager):
    """
    Test the delete_document method of PineconeManager.

    This test verifies that a document and all its chunks are correctly deleted from the Pinecone index.

    Args:
        pinecone_manager (PineconeManager): The PineconeManager instance to test.
    """
    pinecone_manager.index.query.return_value = {
        'matches': [{'id': 'test_id'}]
    }
    result = pinecone_manager.delete_document("file_id", "user_id")
    assert result is True
    pinecone_manager.index.delete.assert_called_once_with(ids=['test_id'], namespace="user_id")


def test_get_selected_documents(pinecone_manager):
    """
    Test the get_selected_documents method of PineconeManager.

    This test verifies that selected documents are correctly retrieved and reconstructed.

    Args:
        pinecone_manager (PineconeManager): The PineconeManager instance to test.
    """
    pinecone_manager.index.query.return_value = {
        'matches': [
            {
                'metadata': {
                    'googleDriveFileId': 'file_id',
                    'lastModified': '2023-01-01',
                    'isSelected': True,
                    'content': 'chunk1',
                    'chunkIndex': 0,
                    'totalChunks': 2
                }
            },
            {
                'metadata': {
                    'googleDriveFileId': 'file_id',
                    'lastModified': '2023-01-01',
                    'isSelected': True,
                    'content': 'chunk2',
                    'chunkIndex': 1,
                    'totalChunks': 2
                }
            }
        ]
    }
    result = pinecone_manager.get_selected_documents("user_id")
    assert len(result) == 1
    assert result[0]['metadata']['content'] == 'chunk1chunk2'


def test_update_all_selected_documents(pinecone_manager):
    """
    Test the update_all_selected_documents method of PineconeManager.

    This test verifies that the selection status of all documents for a user is correctly updated.

    Args:
        pinecone_manager (PineconeManager): The PineconeManager instance to test.
    """
    pinecone_manager.index.query.return_value = {
        'matches': [
            {'metadata': {'googleDriveFileId': 'file_id1'}},
            {'metadata': {'googleDriveFileId': 'file_id2'}}
        ]
    }
    with patch.object(pinecone_manager, 'update_document_selection') as mock_update:
        result = pinecone_manager.update_all_selected_documents("user_id", True)
        assert result is True
        assert mock_update.call_count == 2


def test_get_document_metadata(pinecone_manager):
    """
    Test the get_document_metadata method of PineconeManager.

    This test verifies that metadata for a specific document is correctly retrieved.

    Args:
        pinecone_manager (PineconeManager): The PineconeManager instance to test.
    """
    pinecone_manager.index.fetch.return_value = {
        'vectors': {
            'file_id': {
                'metadata': {
                    'lastModified': '2023-01-01',
                    'isSelected': True
                }
            }
        }
    }
    result = pinecone_manager.get_document_metadata("file_id", "user_id")
    assert result == {'lastModified': '2023-01-01', 'isSelected': True}
    pinecone_manager.index.fetch.assert_called_once_with(ids=['file_id'], namespace="user_id")


def test_get_document_metadata_not_found(pinecone_manager):
    """
    Test the get_document_metadata method of PineconeManager when the document is not found.

    This test verifies that an empty dict is returned when the requested document is not found.

    Args:
        pinecone_manager (PineconeManager): The PineconeManager instance to test.
    """
    pinecone_manager.index.fetch.return_value = {'vectors': {}}
    result = pinecone_manager.get_document_metadata("non_existent_file_id", "user_id")
    assert result == {}


def test_upsert_document_large_content(pinecone_manager):
    """
    Test the upsert_document method of PineconeManager with large content.

    This test verifies that large content is correctly split and upserted as multiple chunks.

    Args:
        pinecone_manager (PineconeManager): The PineconeManager instance to test.
    """
    pinecone_manager.embeddings.embed_query.return_value = [0] * 1536
    document = {
        "id": "test_id",
        "content": "a" * 100000,  # Large content
        "lastModified": "2023-01-01",
        "isSelected": True
    }
    result = pinecone_manager.upsert_document(document, "user_id")
    assert result["success"] is True
    assert result["vectors_upserted"] == 3  # Should be split into 3 chunks
    assert pinecone_manager.index.upsert.call_count == 3