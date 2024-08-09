import pytest
from flask import Flask, session
from unittest.mock import patch, MagicMock
from app.routes.drive_file_operations import drive_file_ops_bp
import io

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.register_blueprint(drive_file_ops_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_open_file_success(client):
    with patch('app.routes.drive_file_operations.get_drive_core') as mock_get_drive_core, \
         patch('app.routes.drive_file_operations.DriveFileOperations') as mock_drive_ops:
        
        mock_drive_ops_instance = mock_drive_ops.return_value
        mock_drive_ops_instance.open_file.return_value = {"webViewLink": "https://example.com/file"}

        response = client.get('/drive/test_file_id/open')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'webViewLink' in json_data
        assert json_data['webViewLink'] == "https://example.com/file"

def test_upload_file_success(client):
    with patch('app.routes.drive_file_operations.get_drive_core') as mock_get_drive_core, \
         patch('app.routes.drive_file_operations.DriveFileOperations') as mock_drive_ops:
        
        mock_drive_ops_instance = mock_drive_ops.return_value
        mock_drive_ops_instance.upload_file.return_value = {"id": "new_file_id", "name": "test_file.txt"}

        data = {'file': (io.BytesIO(b"test content"), 'test_file.txt'), 'folderId': 'test_folder_id'}
        response = client.post('/drive/upload-file', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'id' in json_data
        assert json_data['name'] == "test_file.txt"

def test_create_doc_success(client):
    with patch('app.routes.drive_file_operations.get_drive_core') as mock_get_drive_core, \
         patch('app.routes.drive_file_operations.DriveFileOperations') as mock_drive_ops:
        
        mock_drive_ops_instance = mock_drive_ops.return_value
        mock_drive_ops_instance.create_doc.return_value = {"id": "new_doc_id", "name": "Untitled document"}

        response = client.post('/drive/create-doc', json={'folderId': 'test_folder_id'})
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'id' in json_data
        assert json_data['name'] == "Untitled document"

def test_create_sheet_success(client):
    with patch('app.routes.drive_file_operations.get_drive_core') as mock_get_drive_core, \
         patch('app.routes.drive_file_operations.DriveFileOperations') as mock_drive_ops:
        
        mock_drive_ops_instance = mock_drive_ops.return_value
        mock_drive_ops_instance.create_sheet.return_value = {"id": "new_sheet_id", "name": "Untitled spreadsheet"}

        response = client.post('/drive/create-sheet', json={'folderId': 'test_folder_id'})
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'id' in json_data
        assert json_data['name'] == "Untitled spreadsheet"

def test_move_files_success(client):
    with patch('app.routes.drive_file_operations.get_drive_core') as mock_get_drive_core, \
         patch('app.routes.drive_file_operations.DriveFileOperations') as mock_drive_ops:
        
        mock_drive_ops_instance = mock_drive_ops.return_value
        mock_drive_ops_instance.move_files.return_value = {"success": True, "movedFiles": 2}

        response = client.post('/drive/move-files', json={'fileIds': ['file1', 'file2'], 'newFolderId': 'new_folder_id'})
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        assert json_data['movedFiles'] == 2

def test_delete_files_success(client):
    with patch('app.routes.drive_file_operations.get_drive_core') as mock_get_drive_core, \
         patch('app.routes.drive_file_operations.DriveFileOperations') as mock_drive_ops:
        
        mock_drive_ops_instance = mock_drive_ops.return_value
        mock_drive_ops_instance.delete_files.return_value = {"success": True, "deletedFiles": 2}

        response = client.post('/drive/delete-files', json={'fileIds': ['file1', 'file2']})
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        assert json_data['deletedFiles'] == 2

def test_copy_files_success(client):
    with patch('app.routes.drive_file_operations.get_drive_core') as mock_get_drive_core, \
         patch('app.routes.drive_file_operations.DriveFileOperations') as mock_drive_ops:
        
        mock_drive_ops_instance = mock_drive_ops.return_value
        mock_drive_ops_instance.copy_files.return_value = {"success": True, "copiedFiles": 2}

        response = client.post('/drive/copy-files', json={'fileIds': ['file1', 'file2']})
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        assert json_data['copiedFiles'] == 2

def test_rename_file_success(client):
    with patch('app.routes.drive_file_operations.get_drive_core') as mock_get_drive_core, \
         patch('app.routes.drive_file_operations.DriveFileOperations') as mock_drive_ops:
        
        mock_drive_ops_instance = mock_drive_ops.return_value
        mock_drive_ops_instance.rename_file.return_value = {"id": "file_id", "name": "new_name.txt"}

        response = client.post('/drive/rename-file', json={'fileId': 'file_id', 'newName': 'new_name.txt'})
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['id'] == "file_id"
        assert json_data['name'] == "new_name.txt"

def test_error_handling(client):
    with patch('app.routes.drive_file_operations.get_drive_core') as mock_get_drive_core:
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
    with patch('app.routes.drive_file_operations.get_drive_core') as mock_get_drive_core:
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