import pytest
from flask import Flask, session
from unittest.mock import patch, MagicMock
from app.routes.drive_core import drive_core_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.register_blueprint(drive_core_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_list_folder_contents_success(client):
    mock_files = [
        {'id': '1', 'name': 'file1', 'mimeType': 'text/plain'},
        {'id': '2', 'name': 'file2', 'mimeType': 'application/pdf'},
    ]
    
    with patch('app.routes.drive_core.get_drive_core') as mock_get_drive_core:
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
    mock_files_page1 = [{'id': '1', 'name': 'file1', 'mimeType': 'text/plain'}]
    mock_files_page2 = [{'id': '2', 'name': 'file2', 'mimeType': 'application/pdf'}]
    
    with patch('app.routes.drive_core.get_drive_core') as mock_get_drive_core:
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
    with patch('app.routes.drive_core.get_drive_core') as mock_get_drive_core:
        mock_get_drive_core.side_effect = ValueError("Invalid session")

        response = client.get('/drive/list_folder_contents/test_folder_id')

        assert response.status_code == 401
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == "Invalid session"

def test_list_folder_contents_general_error(client):
    with patch('app.routes.drive_core.get_drive_core') as mock_get_drive_core:
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
    with patch('app.routes.drive_core.get_drive_core') as mock_get_drive_core:
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