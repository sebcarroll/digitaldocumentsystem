"""
This module contains unit tests for the drive_file_operations_routes blueprint.

It includes tests for various file operations such as opening, uploading,
creating, moving, deleting, copying, and renaming files in Google Drive.
"""

import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from backend.app.routes.drive_file_operations_routes import drive_file_ops_bp
import io

@pytest.fixture
def app():
    """
    Create and configure a new Flask app instance for each test.

    Returns:
        Flask: A Flask application instance with testing config and drive_file_ops_bp registered.
    """
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.register_blueprint(drive_file_ops_bp)
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

def test_open_file_success(client):
    """
    Test successful file opening operation.

    This test mocks the drive service and checks if the endpoint correctly
    returns the web view link for the opened file.
    """
    with patch('backend.app.routes.drive_file_operations_routes.get_drive_core') as mock_get_drive_core, \
         patch('backend.app.routes.drive_file_operations_routes.DriveFileOperations') as mock_drive_ops:
        
        mock_drive_ops_instance = mock_drive_ops.return_value
        mock_drive_ops_instance.open_file.return_value = {"webViewLink": "https://example.com/file"}

        response = client.get('/drive/test_file_id/open')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'webViewLink' in json_data
        assert json_data['webViewLink'] == "https://example.com/file"

def test_upload_file_success(client):
    """
    Test successful file upload operation.

    This test mocks the drive service and checks if the endpoint correctly
    handles file upload and returns the uploaded file's details.
    """
    with patch('backend.app.routes.drive_file_operations_routes.get_drive_core') as mock_get_drive_core, \
         patch('backend.app.routes.drive_file_operations_routes.DriveFileOperations') as mock_drive_ops:
        
        mock_drive_ops_instance = mock_drive_ops.return_value
        mock_drive_ops_instance.upload_file.return_value = {"id": "new_file_id", "name": "test_file.txt"}

        data = {'file': (io.BytesIO(b"test content"), 'test_file.txt'), 'folderId': 'test_folder_id'}
        response = client.post('/drive/upload-file', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'id' in json_data
        assert json_data['name'] == "test_file.txt"

def test_create_doc_success(client):
    """
    Test successful document creation operation.

    This test mocks the drive service and checks if the endpoint correctly
    creates a new document and returns its details.
    """
    with patch('backend.app.routes.drive_file_operations_routes.get_drive_core') as mock_get_drive_core, \
         patch('backend.app.routes.drive_file_operations_routes.DriveFileOperations') as mock_drive_ops:
        
        mock_drive_ops_instance = mock_drive_ops.return_value
        mock_drive_ops_instance.create_doc.return_value = {"id": "new_doc_id", "name": "Untitled document"}

        response = client.post('/drive/create-doc', json={'folderId': 'test_folder_id'})
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'id' in json_data
        assert json_data['name'] == "Untitled document"

def test_create_sheet_success(client):
    """
    Test successful spreadsheet creation operation.

    This test mocks the drive service and checks if the endpoint correctly
    creates a new spreadsheet and returns its details.
    """
    with patch('backend.app.routes.drive_file_operations_routes.get_drive_core') as mock_get_drive_core, \
         patch('backend.app.routes.drive_file_operations_routes.DriveFileOperations') as mock_drive_ops:
        
        mock_drive_ops_instance = mock_drive_ops.return_value
        mock_drive_ops_instance.create_sheet.return_value = {"id": "new_sheet_id", "name": "Untitled spreadsheet"}

        response = client.post('/drive/create-sheet', json={'folderId': 'test_folder_id'})
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'id' in json_data
        assert json_data['name'] == "Untitled spreadsheet"

def test_move_files_success(client):
    """
    Test successful file moving operation.

    This test mocks the drive service and checks if the endpoint correctly
    moves files to a new folder and returns the operation result.
    """
    with patch('backend.app.routes.drive_file_operations_routes.get_drive_core') as mock_get_drive_core, \
         patch('backend.app.routes.drive_file_operations_routes.DriveFileOperations') as mock_drive_ops:
        
        mock_drive_ops_instance = mock_drive_ops.return_value
        mock_drive_ops_instance.move_files.return_value = {"success": True, "movedFiles": 2}

        response = client.post('/drive/move-files', json={'fileIds': ['file1', 'file2'], 'newFolderId': 'new_folder_id'})
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        assert json_data['movedFiles'] == 2

def test_delete_files_success(client):
    """
    Test successful file deletion operation.

    This test mocks the drive service and checks if the endpoint correctly
    deletes files and returns the operation result.
    """
    with patch('backend.app.routes.drive_file_operations_routes.get_drive_core') as mock_get_drive_core, \
         patch('backend.app.routes.drive_file_operations_routes.DriveFileOperations') as mock_drive_ops:
        
        mock_drive_ops_instance = mock_drive_ops.return_value
        mock_drive_ops_instance.delete_files.return_value = {"success": True, "deletedFiles": 2}

        response = client.post('/drive/delete-files', json={'fileIds': ['file1', 'file2']})
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        assert json_data['deletedFiles'] == 2

def test_copy_files_success(client):
    """
    Test successful file copying operation.

    This test mocks the drive service and checks if the endpoint correctly
    copies files and returns the operation result.
    """
    with patch('backend.app.routes.drive_file_operations_routes.get_drive_core') as mock_get_drive_core, \
         patch('backend.app.routes.drive_file_operations_routes.DriveFileOperations') as mock_drive_ops:
        
        mock_drive_ops_instance = mock_drive_ops.return_value
        mock_drive_ops_instance.copy_files.return_value = {"success": True, "copiedFiles": 2}

        response = client.post('/drive/copy-files', json={'fileIds': ['file1', 'file2']})
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        assert json_data['copiedFiles'] == 2

def test_rename_file_success(client):
    """
    Test successful file renaming operation.

    This test mocks the drive service and checks if the endpoint correctly
    renames a file and returns the updated file details.
    """
    with patch('backend.app.routes.drive_file_operations_routes.get_drive_core') as mock_get_drive_core, \
         patch('backend.app.routes.drive_file_operations_routes.DriveFileOperations') as mock_drive_ops:
        
        mock_drive_ops_instance = mock_drive_ops.return_value
        mock_drive_ops_instance.rename_file.return_value = {"id": "file_id", "name": "new_name.txt"}

        response = client.post('/drive/rename-file', json={'fileId': 'file_id', 'newName': 'new_name.txt'})
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['id'] == "file_id"
        assert json_data['name'] == "new_name.txt"

def test_error_handling(client):
    """
    Test error handling for invalid session across all endpoints.

    This test ensures that all endpoints properly handle and report
    ValueError exceptions, which might occur due to invalid sessions.
    """
    with patch('backend.app.routes.drive_file_operations_routes.get_drive_core') as mock_get_drive_core:
        mock_get_drive_core.side_effect = ValueError("Invalid session")

        endpoints = [
            ('/drive/test_file_id/open', 'GET'),
            ('/drive/upload-file', 'POST'),
            ('/drive/create-doc', 'POST'),
            ('/drive/create-sheet', 'POST'),
            ('/drive/move-files', 'POST'),
            ('/drive/delete-files', 'POST'),
            ('/drive/copy-files', 'POST'),
            ('/drive/rename-file', 'POST')
        ]

        for endpoint, method in endpoints:
            if method == 'GET':
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})
            
            assert response.status_code == 401
            json_data = response.get_json()
            assert 'error' in json_data
            assert json_data['error'] == "Invalid session"

def test_general_error_handling(client):
    """
    Test general error handling across all endpoints.

    This test ensures that all endpoints properly handle and report
    unexpected exceptions that might occur during the process.
    """
    with patch('backend.app.routes.drive_file_operations_routes.get_drive_core') as mock_get_drive_core:
        mock_get_drive_core.side_effect = Exception("Unexpected error")

        endpoints = [
            ('/drive/test_file_id/open', 'GET'),
            ('/drive/upload-file', 'POST'),
            ('/drive/create-doc', 'POST'),
            ('/drive/create-sheet', 'POST'),
            ('/drive/move-files', 'POST'),
            ('/drive/delete-files', 'POST'),
            ('/drive/copy-files', 'POST'),
            ('/drive/rename-file', 'POST')
        ]

        for endpoint, method in endpoints:
            if method == 'GET':
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})
            
            assert response.status_code == 500
            json_data = response.get_json()
            assert 'error' in json_data
            assert "An error occurred: Unexpected error" in json_data['error']