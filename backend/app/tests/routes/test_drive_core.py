"""
This module contains unit tests for the drive_core_routes blueprint.

It includes tests for various scenarios of the list_folder_contents endpoint,
including successful retrieval, multiple pages, empty folders, and error handling.
"""

import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from backend.app.routes.drive_core_routes import drive_core_bp

@pytest.fixture
def app():
    """
    Create and configure a new Flask app instance for each test.

    Returns:
        Flask: A Flask application instance with testing config and drive_core_bp registered.
    """
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.register_blueprint(drive_core_bp)
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

def test_list_folder_contents_success(client):
    """
    Test successful retrieval of folder contents.

    This test mocks the drive service and checks if the endpoint correctly
    returns the list of files in the expected format.
    """
    mock_files = [
        {'id': '1', 'name': 'file1', 'mimeType': 'text/plain'},
        {'id': '2', 'name': 'file2', 'mimeType': 'application/pdf'},
    ]
    
    with patch('backend.app.routes.drive_core_routes.get_drive_core') as mock_get_drive_core:
        mock_drive_core = MagicMock()
        mock_drive_service = MagicMock()
        mock_drive_core.drive_service = mock_drive_service
        mock_get_drive_core.return_value = mock_drive_core

        mock_list = MagicMock()
        mock_drive_service.files().list.return_value = mock_list
        mock_list.execute.return_value = {'files': mock_files}

        response = client.get('/drive/list_folder_contents/test_folder_id')

        assert response.status_code == 200
        json_data = response.get_json()
        assert len(json_data) == 2
        assert json_data[0]['id'] == '1'
        assert json_data[1]['name'] == 'file2'

def test_list_folder_contents_multiple_pages(client):
    """
    Test retrieval of folder contents with multiple pages.

    This test simulates a scenario where the folder contents are spread
    across multiple pages and checks if all files are correctly retrieved.
    """
    mock_files_page1 = [{'id': '1', 'name': 'file1', 'mimeType': 'text/plain'}]
    mock_files_page2 = [{'id': '2', 'name': 'file2', 'mimeType': 'application/pdf'}]
    
    with patch('backend.app.routes.drive_core_routes.get_drive_core') as mock_get_drive_core:
        mock_drive_core = MagicMock()
        mock_drive_service = MagicMock()
        mock_drive_core.drive_service = mock_drive_service
        mock_get_drive_core.return_value = mock_drive_core

        mock_list = MagicMock()
        mock_drive_service.files().list.return_value = mock_list
        mock_list.execute.side_effect = [
            {'files': mock_files_page1, 'nextPageToken': 'token'},
            {'files': mock_files_page2}
        ]

        response = client.get('/drive/list_folder_contents/test_folder_id')

        assert response.status_code == 200
        json_data = response.get_json()
        assert len(json_data) == 2
        assert json_data[0]['id'] == '1'
        assert json_data[1]['name'] == 'file2'

def test_list_folder_contents_value_error(client):
    """
    Test handling of ValueError when listing folder contents.

    This test checks if the endpoint correctly handles and reports
    a ValueError, which might occur due to an invalid session.
    """
    with patch('backend.app.routes.drive_core_routes.get_drive_core') as mock_get_drive_core:
        mock_get_drive_core.side_effect = ValueError("Invalid session")

        response = client.get('/drive/list_folder_contents/test_folder_id')

        assert response.status_code == 401
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == "Invalid session"

def test_list_folder_contents_general_error(client):
    """
    Test handling of general exceptions when listing folder contents.

    This test verifies that the endpoint properly handles and reports
    unexpected errors that might occur during the process.
    """
    with patch('backend.app.routes.drive_core_routes.get_drive_core') as mock_get_drive_core:
        mock_drive_core = MagicMock()
        mock_drive_service = MagicMock()
        mock_drive_core.drive_service = mock_drive_service
        mock_get_drive_core.return_value = mock_drive_core

        mock_list = MagicMock()
        mock_drive_service.files().list.return_value = mock_list
        mock_list.execute.side_effect = Exception("Unexpected error")

        response = client.get('/drive/list_folder_contents/test_folder_id')

        assert response.status_code == 500
        json_data = response.get_json()
        assert 'error' in json_data
        assert "An error occurred: Unexpected error" in json_data['error']

def test_list_folder_contents_empty_folder(client):
    """
    Test listing contents of an empty folder.

    This test ensures that the endpoint correctly handles and returns
    an empty list when the folder has no contents.
    """
    with patch('backend.app.routes.drive_core_routes.get_drive_core') as mock_get_drive_core:
        mock_drive_core = MagicMock()
        mock_drive_service = MagicMock()
        mock_drive_core.drive_service = mock_drive_service
        mock_get_drive_core.return_value = mock_drive_core

        mock_list = MagicMock()
        mock_drive_service.files().list.return_value = mock_list
        mock_list.execute.return_value = {'files': []}

        response = client.get('/drive/list_folder_contents/test_folder_id')

        assert response.status_code == 200
        json_data = response.get_json()
        assert len(json_data) == 0