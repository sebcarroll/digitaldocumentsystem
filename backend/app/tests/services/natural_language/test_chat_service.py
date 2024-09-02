"""
Unit tests for the ChatService class.

This module contains a set of pytest-based unit tests for the ChatService class,
which manages chat operations and document handling. These tests cover various
functionalities including initialization, query processing, file handling,
and document management.
"""

import pytest
from unittest.mock import Mock, patch
from app.services.natural_language.chat_service import ChatService, DriveCore


@pytest.fixture
def mock_drive_core():
    """
    Fixture to create a mock DriveCore object.

    Returns:
        Mock: A mock object representing DriveCore.
    """
    return Mock(spec=DriveCore)


@pytest.fixture
def chat_service(mock_drive_core):
    """
    Fixture to create a ChatService instance with a mock DriveCore.

    Args:
        mock_drive_core (Mock): A mock DriveCore object.

    Returns:
        ChatService: An instance of ChatService for testing.
    """
    return ChatService(drive_core=mock_drive_core, user_id="test_user")


def test_chat_service_initialization(chat_service):
    """
    Test the initialization of ChatService.

    This test verifies that ChatService is properly initialized with
    the correct attributes and dependencies.

    Args:
        chat_service (ChatService): The ChatService instance to test.
    """
    assert chat_service.user_id == "test_user"
    assert chat_service.drive_core is not None
    assert chat_service.drive_service is not None
    assert chat_service.file_extractor is not None
    assert chat_service.llm is not None
    assert chat_service.pinecone_manager is not None
    assert chat_service.memory is not None


def test_post_process_output(chat_service):
    """
    Test the post_process_output method of ChatService.

    This test checks if markdown is correctly converted to HTML and
    if custom formatting is applied properly.

    Args:
        chat_service (ChatService): The ChatService instance to test.
    """
    markdown_text = "# Title\n\n|Column 1|Column 2|\n|-|-|\n|Data 1|Data 2|\n\n1. Item 1\n2. Item 2\n\n- Bullet 1\n- Bullet 2"
    processed_output = chat_service.post_process_output(markdown_text)
    
    assert "<h1>Title</h1>" in processed_output
    assert "<table>" in processed_output
    assert "<ol><li>Item 1</li></ol>" in processed_output
    assert "<ul><li>Bullet 1</li></ul>" in processed_output


def test_set_user_id(chat_service):
    """
    Test the set_user_id method of ChatService.

    This test verifies that the user ID can be set and updated correctly.

    Args:
        chat_service (ChatService): The ChatService instance to test.
    """
    chat_service.set_user_id("new_user")
    assert chat_service.user_id == "new_user"


def test_has_drive_service(chat_service):
    """
    Test the has_drive_service method of ChatService.

    This test checks if the method correctly reports the presence of a DriveService.

    Args:
        chat_service (ChatService): The ChatService instance to test.
    """
    assert chat_service.has_drive_service() is True

    chat_service_without_drive = ChatService()
    assert chat_service_without_drive.has_drive_service() is False


@patch('app.services.natural_language.chat_service.PineconeManager')
@patch('app.services.natural_language.chat_service.ChatOpenAI')
def test_query(mock_chat_openai, mock_pinecone_manager, chat_service):
    """
    Test the query method of ChatService.

    This test mocks the dependencies and verifies that the query method
    processes input correctly and returns expected output.

    Args:
        mock_chat_openai (Mock): Mocked ChatOpenAI instance.
        mock_pinecone_manager (Mock): Mocked PineconeManager instance.
        chat_service (ChatService): The ChatService instance to test.
    """
    mock_pinecone_manager.return_value.get_selected_documents.return_value = [
        {"metadata": {"content": "Test content", "isSelected": True}}
    ]
    mock_chat_openai.return_value.invoke.return_value.content = "Mocked response"

    result = chat_service.query("Test question")

    assert "Mocked response" in result
    mock_pinecone_manager.return_value.get_selected_documents.assert_called_once()
    mock_chat_openai.return_value.invoke.assert_called_once()


def test_clear_memory(chat_service):
    """
    Test the clear_memory method of ChatService.

    This test verifies that the conversation memory is cleared and
    document selection is reset correctly.

    Args:
        chat_service (ChatService): The ChatService instance to test.
    """
    with patch.object(chat_service.memory, 'clear') as mock_clear, \
         patch.object(chat_service.pinecone_manager, 'update_all_selected_documents') as mock_update:
        
        chat_service.clear_memory()
        
        mock_clear.assert_called_once()
        mock_update.assert_called_once_with("test_user", False)


@patch('app.services.natural_language.chat_service.FileExtractor')
def test_process_and_add_file(mock_file_extractor, chat_service):
    """
    Test the process_and_add_file method of ChatService.

    This test mocks file extraction and document insertion to verify
    correct behavior of the method.

    Args:
        mock_file_extractor (Mock): Mocked FileExtractor instance.
        chat_service (ChatService): The ChatService instance to test.
    """
    chat_service.drive_service.get_file_details.return_value = {"modifiedTime": "2023-01-01"}
    chat_service.pinecone_manager.get_document_metadata.return_value = None
    mock_file_extractor.return_value.extract_text_from_drive_file.return_value = "Extracted text"
    chat_service.pinecone_manager.upsert_document.return_value = {"success": True}

    result = chat_service.process_and_add_file("file_id", "file_name")

    assert result is True
    chat_service.pinecone_manager.upsert_document.assert_called_once()


def test_update_document_selection(chat_service):
    """
    Test the update_document_selection method of ChatService.

    This test verifies that document selection status can be updated correctly.

    Args:
        chat_service (ChatService): The ChatService instance to test.
    """
    chat_service.pinecone_manager.update_document_selection.return_value = True

    result = chat_service.update_document_selection("file_id", True)

    assert result is True
    chat_service.pinecone_manager.update_document_selection.assert_called_once_with("file_id", True, "test_user")


def test_delete_document(chat_service):
    """
    Test the delete_document method of ChatService.

    This test checks if a document can be deleted correctly from the vector store.

    Args:
        chat_service (ChatService): The ChatService instance to test.
    """
    chat_service.pinecone_manager.delete_document.return_value = True

    result = chat_service.delete_document("file_id")

    assert result is True
    chat_service.pinecone_manager.delete_document.assert_called_once_with("file_id", "test_user")