"""
Test suite for the Google Drive access routes.

This module contains tests for the various endpoints and functionalities
related to Google Drive access in the application.
"""

import pytest
from flask import Flask, session
from unittest.mock import patch, MagicMock
from backend.app.routes.access_drive_routes import drive_bp
from app.utils.drive_utils import get_drive_core

@pytest.fixture
def app():
    """
    Create and configure a new app instance for each test.

    Returns:
        flask.Flask: A Flask app instance configured for testing.
    """
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.register_blueprint(drive_bp)
    return app

@pytest.fixture
def client(app):
    """
    Create a test client for the app.

    Args:
        app (flask.Flask): The Flask app instance.

    Returns:
        flask.testing.FlaskClient: A test client for the Flask app.
    """
    return app.test_client()

def test_drive_success(client):
    """
    Test successful retrieval of Drive contents.

    This test verifies that the /drive endpoint correctly returns
    a list of files when files are present.

    Args:
        client (flask.testing.FlaskClient): The test client.
    """
    with client.session_transaction() as sess:
        sess['credentials'] = {'token': 'test_token'}
    
    with patch('backend.app.routes.access_drive_routes.get_drive_core') as mock_get_drive_core:
        mock_drive_core = mock_get_drive_core.return_value
        mock_drive_core.list_folder_contents.return_value = [
            {'id': '1', 'name': 'file1'},
            {'id': '2', 'name': 'file2'}
        ]

        response = client.get('/drive?folder_id=test_folder&page_token=test_token&page_size=10')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'files' in json_data
        assert len(json_data['files']) == 2
        assert 'nextPageToken' in json_data
        assert json_data['nextPageToken'] is None  # Assuming we're not implementing pagination in DriveCore

def test_drive_no_files(client):
    """
    Test Drive content retrieval when no files are present.

    This test ensures that the /drive endpoint returns an appropriate
    message when no files are found in the specified folder.

    Args:
        client (flask.testing.FlaskClient): The test client.
    """
    with client.session_transaction() as sess:
        sess['credentials'] = {'token': 'test_token'}
    
    with patch('backend.app.routes.access_drive_routes.get_drive_core') as mock_get_drive_core:
        mock_drive_core = mock_get_drive_core.return_value
        mock_drive_core.list_folder_contents.return_value = []

        response = client.get('/drive')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'message' in json_data
        assert json_data['message'] == "No files found in this folder."

def test_drive_value_error(client):
    """
    Test Drive content retrieval with invalid credentials.

    This test verifies that the /drive endpoint correctly handles
    and reports a ValueError, which typically indicates invalid credentials.

    Args:
        client (flask.testing.FlaskClient): The test client.
    """
    with client.session_transaction() as sess:
        sess['credentials'] = {'token': 'invalid_token'}
    
    with patch('backend.app.routes.access_drive_routes.get_drive_core') as mock_get_drive_core:
        mock_get_drive_core.side_effect = ValueError("Invalid credentials")

        response = client.get('/drive')
        
        assert response.status_code == 401
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == "Invalid credentials"

def test_drive_general_error(client):
    """
    Test Drive content retrieval with a general error.

    This test ensures that the /drive endpoint properly handles
    and reports unexpected errors during the file listing process.

    Args:
        client (flask.testing.FlaskClient): The test client.
    """
    with client.session_transaction() as sess:
        sess['credentials'] = {'token': 'test_token'}
    
    with patch('backend.app.routes.access_drive_routes.get_drive_core') as mock_get_drive_core:
        mock_drive_core = mock_get_drive_core.return_value
        mock_drive_core.list_folder_contents.side_effect = Exception("Unexpected error")

        response = client.get('/drive')
        
        assert response.status_code == 500
        json_data = response.get_json()
        assert 'error' in json_data
        assert "An error occurred: Unexpected error" in json_data['error']

def test_open_file_success(client):
    """
    Test successful file opening.

    This test verifies that the /drive/<file_id>/open endpoint
    correctly returns the web view link and MIME type for a file.

    Args:
        client (flask.testing.FlaskClient): The test client.
    """
    with client.session_transaction() as sess:
        sess['credentials'] = {'token': 'test_token'}
    
    with patch('backend.app.routes.access_drive_routes.get_drive_core') as mock_get_drive_core:
        mock_drive_core = mock_get_drive_core.return_value
        mock_drive_core.get_file_web_view_link.return_value = ('https://example.com', 'text/plain')

        response = client.get('/drive/test_file_id/open')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'webViewLink' in json_data
        assert 'mimeType' in json_data
        assert json_data['webViewLink'] == 'https://example.com'
        assert json_data['mimeType'] == 'text/plain'

def test_open_file_value_error(client):
    """
    Test file opening with an invalid file ID.

    This test ensures that the /drive/<file_id>/open endpoint
    properly handles and reports attempts to open an invalid file.

    Args:
        client (flask.testing.FlaskClient): The test client.
    """
    with client.session_transaction() as sess:
        sess['credentials'] = {'token': 'test_token'}
    
    with patch('backend.app.routes.access_drive_routes.get_drive_core') as mock_get_drive_core:
        mock_drive_core = mock_get_drive_core.return_value
        mock_drive_core.get_file_web_view_link.side_effect = ValueError("Invalid file ID")

        response = client.get('/drive/invalid_file_id/open')
        
        assert response.status_code == 401
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == "Invalid file ID"

def test_open_file_general_error(client):
    """
    Test file opening with a general error.

    This test verifies that the /drive/<file_id>/open endpoint
    correctly handles and reports unexpected errors during file opening.

    Args:
        client (flask.testing.FlaskClient): The test client.
    """
    with client.session_transaction() as sess:
        sess['credentials'] = {'token': 'test_token'}
    
    with patch('backend.app.routes.access_drive_routes.get_drive_core') as mock_get_drive_core:
        mock_drive_core = mock_get_drive_core.return_value
        mock_drive_core.get_file_web_view_link.side_effect = Exception("Unexpected error")

        response = client.get('/drive/test_file_id/open')
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == "Unexpected error"

def test_logout(client):
    """
    Test the logout functionality.

    This test ensures that the /logout endpoint correctly clears
    the user's session and returns a success message.

    Args:
        client (flask.testing.FlaskClient): The test client.
    """
    with client.session_transaction() as sess:
        sess['credentials'] = {'token': 'test_token'}

    response = client.get('/logout')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'message' in json_data
    assert json_data['message'] == "Logged out successfully"
    
    with client.session_transaction() as sess:
        assert 'credentials' not in sess

def test_cleanup_services(app):
    """
    Test the cleanup of services after a request.

    This test verifies that the teardown function correctly
    removes the 'drive_core' attribute from the Flask 'g' object.

    Args:
        app (flask.Flask): The Flask app instance.
    """
    with app.test_request_context():
        from flask import g
        g.drive_core = 'test_drive_core'
        
        # Simulate a request
        app.preprocess_request()
        
        # Simulate the teardown
        app.do_teardown_request()
        
        assert not hasattr(g, 'drive_core')