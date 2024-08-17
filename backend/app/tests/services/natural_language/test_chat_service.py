"""
Unit tests for the ChatService module of the Google Drive Sync API.

This module contains pytest-based unit tests for the ChatService class,
including initialization, query processing, document addition, and deletion.
It uses mocking to isolate the ChatService from external dependencies.

File: test_chat_service.py
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.natural_language.chat_service import ChatService, retry_with_exponential_backoff
from openai import APIError, RateLimitError

@pytest.fixture
def chat_service():
    """
    Create and configure a ChatService instance for each test.

    Returns:
        ChatService: A ChatService instance with mocked dependencies.
    """
    with patch('app.services.natural_language.chat_service.ChatOpenAI'), \
         patch('app.services.natural_language.chat_service.PineconeClient'), \
         patch('app.services.natural_language.chat_service.OpenAIEmbeddings'), \
         patch('app.services.natural_language.chat_service.Pinecone'), \
         patch('app.services.natural_language.chat_service.ConversationalRetrievalChain'):
        return ChatService()

def test_chat_service_initialization(chat_service):
    """
    Test successful initialization of ChatService.

    This test verifies that a ChatService instance can be created
    without raising exceptions.

    Args:
        chat_service (ChatService): The ChatService instance.
    """
    assert isinstance(chat_service, ChatService)

def test_query_success(chat_service):
    """
    Test successful query processing.

    This test checks that a query can be processed and returns the expected response.

    Args:
        chat_service (ChatService): The ChatService instance.
    """
    chat_service.qa.invoke = MagicMock(return_value={'answer': 'Test response'})
    result = chat_service.query('Test question')
    assert result == 'Test response'

def test_query_exception(chat_service):
    """
    Test query processing when an exception occurs.

    This test verifies that exceptions during query processing are properly handled.

    Args:
        chat_service (ChatService): The ChatService instance.
    """
    chat_service.qa.invoke = MagicMock(side_effect=Exception('Test error'))
    with pytest.raises(Exception):
        chat_service.query('Test question')

def test_get_embedding(chat_service):
    """
    Test embedding retrieval and caching.

    This test checks that embeddings can be retrieved and are properly cached.

    Args:
        chat_service (ChatService): The ChatService instance.
    """
    chat_service.embeddings.embed_query = MagicMock(return_value=[0.1, 0.2, 0.3])
    embedding1 = chat_service.get_embedding('Test text')
    embedding2 = chat_service.get_embedding('Test text')
    assert embedding1 == embedding2
    chat_service.embeddings.embed_query.assert_called_once_with('Test text')

def test_add_document_success(chat_service):
    """
    Test successful document addition.

    This test verifies that a document can be added successfully to the vector store.

    Args:
        chat_service (ChatService): The ChatService instance.
    """
    chat_service.vectorstore.add_texts = MagicMock()
    result = chat_service.add_document({'id': '1', 'content': 'Test content'})
    assert result is True
    chat_service.vectorstore.add_texts.assert_called_once()

def test_add_document_failure(chat_service):
    """
    Test failed document addition.

    This test checks that document addition failures are handled properly.

    Args:
        chat_service (ChatService): The ChatService instance.
    """
    chat_service.vectorstore.add_texts = MagicMock(side_effect=Exception('Test error'))
    result = chat_service.add_document({'id': '1', 'content': 'Test content'})
    assert result is False

def test_delete_document_success(chat_service):
    """
    Test successful document deletion.

    This test verifies that a document can be deleted successfully from the vector store.

    Args:
        chat_service (ChatService): The ChatService instance.
    """
    chat_service.vectorstore.delete = MagicMock()
    result = chat_service.delete_document('1')
    assert result is True
    chat_service.vectorstore.delete.assert_called_once_with(ids=['1'])

def test_delete_document_failure(chat_service):
    """
    Test failed document deletion.

    This test checks that document deletion failures are handled properly.

    Args:
        chat_service (ChatService): The ChatService instance.
    """
    chat_service.vectorstore.delete = MagicMock(side_effect=Exception('Test error'))
    result = chat_service.delete_document('1')
    assert result is False

@patch('app.services.natural_language.chat_service.time.sleep')
def test_retry_with_exponential_backoff(mock_sleep):
    """
    Test the retry_with_exponential_backoff decorator.

    This test verifies that the decorator properly retries a function
    with exponential backoff when a RateLimitError occurs.

    The test function will raise a RateLimitError on the first three
    calls and an APIError on the fourth call. The test ensures that the
    retry mechanism works as expected, retrying the function the correct
    number of times and ultimately raising an APIError after exceeding
    the maximum number of retries.

    Args:
        mock_sleep (MagicMock): Mocked time.sleep function to avoid
            actual sleep during the test.

    Raises:
        APIError: After the maximum number of retries is exceeded.
    """
    call_count = 0

    # Mocking a response object with a request attribute for RateLimitError
    mock_response = MagicMock()
    mock_response.request = MagicMock()

    # Mocking a request object for APIError
    mock_request = MagicMock()

    @retry_with_exponential_backoff
    def test_function():
        nonlocal call_count
        call_count += 1
        if call_count <= 3:
            raise RateLimitError(message="Test rate limit error", response=mock_response, body="Rate limit exceeded")
        raise APIError("Maximum number of retries (3) exceeded", request=mock_request, body="Retry limit hit")  # Providing 'request' and 'body' arguments

    with pytest.raises(APIError) as exc_info:
        test_function()

    assert str(exc_info.value) == "Maximum number of retries (3) exceeded"
    assert call_count == 4  # Initial call + 3 retries
    assert mock_sleep.call_count == 3