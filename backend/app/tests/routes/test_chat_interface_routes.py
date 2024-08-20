"""
Unit tests for the chat interface routes module of the Google Drive Sync API.

This module contains pytest-based unit tests for the chat functionality,
including query processing and document management routes. It uses mocking
to isolate route handling from the underlying ChatService implementation.

File: test_chat_interface_routes.py
"""

import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from app.routes.chat_interface_routes import chat_bp

@pytest.fixture
def app():
    """
    Create and configure a new Flask app instance for each test.

    Returns:
        Flask: A Flask application instance with the chat blueprint registered.
    """
    app = Flask(__name__)
    app.register_blueprint(chat_bp)
    return app

@pytest.fixture
def client(app):
    """
    Create a test client for the app.

    Args:
        app (Flask): The Flask application instance.

    Returns:
        FlaskClient: A test client for the Flask application.
    """
    return app.test_client()

def test_query_llm_success(client):
    """
    Test successful query processing.

    This test verifies that a valid query returns the expected response
    with a 200 status code.

    Args:
        client (FlaskClient): The test client for the Flask application.
    """
    with patch('app.routes.chat_interface_routes.chat_service.query') as mock_query:
        mock_query.return_value = "Test response"
        response = client.post('/query', json={'query': 'Test query'})
        assert response.status_code == 200
        assert response.json == {"response": "Test response"}

def test_query_llm_no_query(client):
    """
    Test query processing with no input.

    This test checks that sending an empty query results in a 400 error.

    Args:
        client (FlaskClient): The test client for the Flask application.
    """
    response = client.post('/query', json={})
    assert response.status_code == 400
    assert response.json == {"error": "No query provided"}

def test_query_llm_exception(client):
    """
    Test query processing when an exception occurs.

    This test verifies that the route handles exceptions gracefully,
    returning a 500 error.

    Args:
        client (FlaskClient): The test client for the Flask application.
    """
    with patch('app.routes.chat_interface_routes.chat_service.query') as mock_query:
        mock_query.side_effect = Exception("Test error")
        response = client.post('/query', json={'query': 'Test query'})
        assert response.status_code == 500
        assert response.json == {"error": "An error occurred while processing the query"}

def test_manage_document_add_success(client):
    """
    Test successful document addition.

    This test checks that a valid document can be added successfully,
    returning a 200 status code.

    Args:
        client (FlaskClient): The test client for the Flask application.
    """
    with patch('app.routes.chat_interface_routes.chat_service.add_document') as mock_add:
        mock_add.return_value = True
        response = client.post('/document', json={'document': {'id': '1', 'content': 'Test content'}})
        assert response.status_code == 200
        assert response.json == {"message": "Document processed and stored successfully"}

def test_manage_document_add_failure(client):
    """
    Test failed document addition.

    This test verifies that when document addition fails, a 500 error is returned.

    Args:
        client (FlaskClient): The test client for the Flask application.
    """
    with patch('app.routes.chat_interface_routes.chat_service.add_document') as mock_add:
        mock_add.return_value = False
        response = client.post('/document', json={'document': {'id': '1', 'content': 'Test content'}})
        assert response.status_code == 500
        assert response.json == {"error": "Failed to process document"}

def test_manage_document_add_no_document(client):
    """
    Test document addition with no document provided.

    This test checks that attempting to add a document without providing one
    results in a 400 error.

    Args:
        client (FlaskClient): The test client for the Flask application.
    """
    response = client.post('/document', json={})
    assert response.status_code == 400
    assert response.json == {"error": "No document provided"}

def test_manage_document_delete_success(client):
    """
    Test successful document deletion.

    This test verifies that a document can be deleted successfully,
    returning a 200 status code.

    Args:
        client (FlaskClient): The test client for the Flask application.
    """
    with patch('app.routes.chat_interface_routes.chat_service.delete_document') as mock_delete:
        mock_delete.return_value = True
        response = client.delete('/document', json={'document_id': '1'})
        assert response.status_code == 200
        assert response.json == {"message": "Document deleted successfully"}

def test_manage_document_delete_failure(client):
    """
    Test failed document deletion.

    This test checks that when document deletion fails, a 500 error is returned.

    Args:
        client (FlaskClient): The test client for the Flask application.
    """
    with patch('app.routes.chat_interface_routes.chat_service.delete_document') as mock_delete:
        mock_delete.return_value = False
        response = client.delete('/document', json={'document_id': '1'})
        assert response.status_code == 500
        assert response.json == {"error": "Failed to delete document"}

def test_manage_document_delete_no_id(client):
    """
    Test document deletion with no ID provided.

    This test verifies that attempting to delete a document without providing
    an ID results in a 400 error.

    Args:
        client (FlaskClient): The test client for the Flask application.
    """
    response = client.delete('/document', json={})
    assert response.status_code == 400
    assert response.json == {"error": "No document ID provided"}

def test_manage_document_exception(client):
    """
    Test document management when an exception occurs.

    This test checks that the route handles exceptions during document
    management gracefully, returning a 500 error.

    Args:
        client (FlaskClient): The test client for the Flask application.
    """
    with patch('app.routes.chat_interface_routes.chat_service.add_document') as mock_add:
        mock_add.side_effect = Exception("Test error")
        response = client.post('/document', json={'document': {'id': '1', 'content': 'Test content'}})
        assert response.status_code == 500
        assert response.json == {"error": "An error occurred while managing the document"}