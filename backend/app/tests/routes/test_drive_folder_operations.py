import pytest
from flask import Flask, session
from unittest.mock import patch, MagicMock
from app.routes.drive_folder_operations import drive_folder_ops_bp
import io

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.register_blueprint(drive_folder_ops_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_folder_success(client):
    with patch('app.routes.drive_folder_operations.get_drive_core') as mock_get_drive_core, \
         patch('app.routes.drive_folder_operations.DriveFolderOperations') as mock_folder_ops:
        
        mock_folder_ops_instance = mock_folder_ops.return_value
        mock_folder_ops_instance.create_folder.return_value = {"id": "new_folder_id", "name": "New Folder"}

        response = client.post('/drive/create-folder', json={'parentFolderId': 'parent_id', 'folderName': 'New Folder'})
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'id' in json_data
        assert json_data['name'] == "New Folder"

def test_upload_folder_success(client):
    with patch('app.routes.drive_folder_operations.get_drive_core') as mock_get_drive_core, \
         patch('app.routes.drive_folder_operations.DriveFolderOperations') as mock_folder_ops:
        
        mock_folder_ops_instance = mock_folder_ops.return_value
        mock_folder_ops_instance.upload_folder.return_value = {"success": True, "uploadedFiles": 2}

        data = {
            'parentFolderId': 'parent_id',
            'files': [
                (io.BytesIO(b"file1 content"), 'file1.txt'),
                (io.BytesIO(b"file2 content"), 'file2.txt')
            ]
        }
        response = client.post('/drive/upload-folder', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        assert json_data['uploadedFiles'] == 2

def test_fetch_folders_success(client):
    with patch('app.routes.drive_folder_operations.get_drive_core') as mock_get_drive_core, \
         patch('app.routes.drive_folder_operations.DriveFolderOperations') as mock_folder_ops:
        
        mock_folder_ops_instance = mock_folder_ops.return_value
        mock_folder_ops_instance.fetch_folders.return_value = [
            {"id": "folder1", "name": "Folder 1"},
            {"id": "folder2", "name": "Folder 2"}
        ]

        response = client.get('/drive/folders?parent_id=parent_id')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert len(json_data) == 2
        assert json_data[0]['name'] == "Folder 1"
        assert json_data[1]['id'] == "folder2"

def test_create_folder_value_error(client):
    with patch('app.routes.drive_folder_operations.get_drive_core') as mock_get_drive_core:
        mock_get_drive_core.side_effect = ValueError("Invalid session")

        response = client.post('/drive/create-folder', json={'parentFolderId': 'parent_id', 'folderName': 'New Folder'})
        
        assert response.status_code == 401
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == "Invalid session"

def test_upload_folder_value_error(client):
    with patch('app.routes.drive_folder_operations.get_drive_core') as mock_get_drive_core:
        mock_get_drive_core.side_effect = ValueError("Invalid session")

        data = {
            'parentFolderId': 'parent_id',
            'files': [
                (io.BytesIO(b"file1 content"), 'file1.txt')
            ]
        }
        response = client.post('/drive/upload-folder', data=data, content_type='multipart/form-data')
        
        assert response.status_code == 401
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == "Invalid session"

def test_fetch_folders_value_error(client):
    with patch('app.routes.drive_folder_operations.get_drive_core') as mock_get_drive_core:
        mock_get_drive_core.side_effect = ValueError("Invalid session")

        response = client.get('/drive/folders?parent_id=parent_id')
        
        assert response.status_code == 401
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == "Invalid session"

def test_general_error_handling(client):
    with patch('app.routes.drive_folder_operations.get_drive_core') as mock_get_drive_core:
        mock_get_drive_core.side_effect = Exception("Unexpected error")

        endpoints = [
            ('/drive/create-folder', 'POST'),
            ('/drive/upload-folder', 'POST'),
            ('/drive/folders', 'GET')
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