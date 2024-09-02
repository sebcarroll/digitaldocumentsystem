"""
Unit tests for the chat routes module.

This module contains a set of pytest-based unit tests for the chat routes,
which handle chat functionality including query processing and document management
in the vector store. These tests cover various HTTP endpoints and their responses.
"""

import json
import pytest
from flask import Flask, session
from unittest.mock import patch, MagicMock
from app.routes.chat_interface_routes import chat_bp, initialize_chat_service

@pytest.fixture
def app():
    """
    Fixture to create a Flask app with the chat blueprint registered.

    Returns:
        Flask: A Flask application instance for testing.
    """
    app = Flask(__name__)
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.config['TESTING'] = True
    app.secret_key = 'test_secret_key'
    return app

@pytest.fixture
def client(app):
    """
    Fixture to create a test client for the Flask app.

    Args:
        app (Flask): The Flask application instance.

    Returns:
        FlaskClient: A test client for the Flask app.
    """
    return app.test_client()

def test_query_llm(client):
    """
    Test the /query endpoint of the chat routes.

    This test verifies that a query can be successfully processed and a response is returned.

    Args:
        client (FlaskClient): The test client for the Flask app.
    """
    with patch('app.routes.chat_interface_routes.ChatService') as MockChatService:
        mock_chat_service = MockChatService.return_value
        mock_chat_service.query.return_value = "Mocked response"

        response = client.post('/chat/query', json={'query': 'Test query'})
        assert response.status_code == 200
        assert json.loads(response.data) == {"response": "Mocked response"}

def test_query_llm_no_query(client):
    """
    Test the /query endpoint with no query provided.

    This test verifies that an appropriate error response is returned when no query is provided.

    Args:
        client (FlaskClient): The test client for the Flask app.
    """
    response = client.post('/chat/query', json={})
    assert response.status_code == 400
    assert json.loads(response.data) == {"error": "No query provided"}

def test_clear_chat_history(client):
    """
    Test the /clear endpoint of the chat routes.

    This test verifies that the chat history can be successfully cleared.

    Args:
        client (FlaskClient): The test client for the Flask app.
    """
    with patch('app.routes.chat_interface_routes.ChatService') as MockChatService:
        mock_chat_service = MockChatService.return_value
        response = client.post('/chat/clear')
        assert response.status_code == 200
        assert json.loads(response.data) == {"message": "Chat history cleared"}
        mock_chat_service.clear_memory.assert_called_once()

def test_manage_document_post(client):
    """
    Test the POST method of the /document endpoint.

    This test verifies that a document can be successfully processed and added.

    Args:
        client (FlaskClient): The test client for the Flask app.
    """
    with patch('app.routes.chat_interface_routes.ChatService') as MockChatService:
        mock_chat_service = MockChatService.return_value
        mock_chat_service.process_and_add_file.return_value = True

        response = client.post('/chat/document', json={'file_id': 'test_id', 'file_name': 'test.txt'})
        assert response.status_code == 200
        assert json.loads(response.data) == {"message": "File processed and stored successfully"}

def test_manage_document_delete(client):
    """
    Test the DELETE method of the /document endpoint.

    This test verifies that a document can be successfully deleted.

    Args:
        client (FlaskClient): The test client for the Flask app.
    """
    with patch('app.routes.chat_interface_routes.ChatService') as MockChatService:
        mock_chat_service = MockChatService.return_value
        mock_chat_service.delete_document.return_value = True

        response = client.delete('/chat/document', json={'document_id': 'test_id'})
        assert response.status_code == 200
        assert json.loads(response.data) == {"message": "Document deleted successfully"}

def test_update_document_selection(client):
    """
    Test the /update-document-selection endpoint.

    This test verifies that the selection status of a document can be successfully updated.

    Args:
        client (FlaskClient): The test client for the Flask app.
    """
    with patch('app.routes.chat_interface_routes.ChatService') as MockChatService:
        mock_chat_service = MockChatService.return_value
        mock_chat_service.update_document_selection.return_value = True

        response = client.post('/chat/update-document-selection', json={'fileId': 'test_id', 'isSelected': True})
        assert response.status_code == 200
        assert json.loads(response.data) == {"message": "Document selection updated successfully"}

def test_handle_options(client):
    """
    Test the OPTIONS method handling for CORS.

    This test verifies that the appropriate CORS headers are set in the response.

    Args:
        client (FlaskClient): The test client for the Flask app.
    """
    response = client.options('/chat/test-path')
    assert response.status_code == 200
    assert response.headers.get('Access-Control-Allow-Origin') == 'http://localhost:3000'
    assert response.headers.get('Access-Control-Allow-Headers') == 'Content-Type'
    assert response.headers.get('Access-Control-Allow-Methods') == 'GET, POST, PUT, DELETE, OPTIONS'
    assert response.headers.get('Access-Control-Allow-Credentials') == 'true'

def test_upload_documents(client):
    """
    Test the /upload-documents endpoint.

    This test verifies that multiple documents can be successfully uploaded and processed.

    Args:
        client (FlaskClient): The test client for the Flask app.
    """
    with patch('app.routes.chat_interface_routes.ChatService') as MockChatService:
        mock_chat_service = MockChatService.return_value
        mock_chat_service.process_and_add_multiple_files.return_value = {
            'successful_uploads': 2,
            'total_files': 3
        }

        response = client.post('/chat/upload-documents', json={
            'fileIds': ['id1', 'id2', 'id3'],
            'fileNames': ['file1.txt', 'file2.txt', 'file3.txt']
        })
        assert response.status_code == 200
        assert json.loads(response.data) == {
            "message": "Processed 2 out of 3 documents successfully",
            "successful_uploads": 2,
            "total_files": 3
        }

def test_set_documents_unselected(client):
    """
    Test the /set-documents-unselected endpoint.

    This test verifies that multiple documents can be successfully set as unselected.

    Args:
        client (FlaskClient): The test client for the Flask app.
    """
    with patch('app.routes.chat_interface_routes.ChatService') as MockChatService:
        mock_chat_service = MockChatService.return_value
        mock_chat_service.update_document_selection.side_effect = [True, False, True]

        response = client.post('/chat/set-documents-unselected', json={
            'documentIds': ['id1', 'id2', 'id3']
        })
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['message'] == "Documents updated successfully"
        assert result['results'] == [
            {"id": "id1", "success": True},
            {"id": "id2", "success": False},
            {"id": "id3", "success": True}
        ]

def test_initialize_chat_service(app):
    """
    Test the initialize_chat_service function.

    This test verifies that the chat service is properly initialized before each request.

    Args:
        app (Flask): The Flask application instance.
    """
    with app.test_request_context():
        with patch('app.routes.chat_interface_routes.ChatService') as MockChatService, \
             patch('app.routes.chat_interface_routes.get_drive_core') as mock_get_drive_core:
            
            mock_chat_service = MockChatService.return_value
            mock_drive_core = MagicMock()
            mock_get_drive_core.return_value = mock_drive_core
            
            session['user_id'] = 'test_user'
            
            initialize_chat_service()
            
            assert 'chat_service' in app.extensions
            mock_chat_service.set_user_id.assert_called_once_with('test_user')
            mock_chat_service.set_drive_core.assert_called_once_with(mock_drive_core)