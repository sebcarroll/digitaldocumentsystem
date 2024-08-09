import pytest
from flask import Flask, session
from unittest.mock import patch, MagicMock
from app.routes.access_drive import drive_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(drive_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_drive_success(client):
    with patch('app.routes.drive_core.get_drive_core') as mock_get_drive_core, \
         patch('app.routes.drive_core.DriveService') as mock_drive_service:
        
        mock_drive_service_instance = mock_drive_service.return_value
        mock_drive_service_instance.list_folder_contents.return_value = (
            [{'id': '1', 'name': 'file1'}, {'id': '2', 'name': 'file2'}],
            'next_page_token'
        )

        response = client.get('/drive?folder_id=test_folder&page_token=test_token&page_size=10')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'files' in json_data
        assert 'nextPageToken' in json_data
        assert len(json_data['files']) == 2
        assert json_data['nextPageToken'] == 'next_page_token'

def test_drive_no_files(client):
    with patch('app.routes.drive_core.get_drive_core') as mock_get_drive_core, \
         patch('app.routes.drive_core.DriveService') as mock_drive_service:
        
        mock_drive_service_instance = mock_drive_service.return_value
        mock_drive_service_instance.list_folder_contents.return_value = ([], None)

        response = client.get('/drive')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'message' in json_data
        assert json_data['message'] == "No files found in this folder."

def test_drive_value_error(client):
    with patch('app.routes.drive_core.get_drive_core') as mock_get_drive_core, \
         patch('app.routes.drive_core.DriveService') as mock_drive_service:
        
        mock_drive_service_instance = mock_drive_service.return_value
        mock_drive_service_instance.list_folder_contents.side_effect = ValueError("Invalid credentials")

        response = client.get('/drive')
        
        assert response.status_code == 401
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == "Invalid credentials"

def test_drive_general_error(client):
    with patch('app.routes.drive_core.get_drive_core') as mock_get_drive_core, \
         patch('app.routes.drive_core.DriveService') as mock_drive_service:
        
        mock_drive_service_instance = mock_drive_service.return_value
        mock_drive_service_instance.list_folder_contents.side_effect = Exception("Unexpected error")

        response = client.get('/drive')
        
        assert response.status_code == 500
        json_data = response.get_json()
        assert 'error' in json_data
        assert "An error occurred: Unexpected error" in json_data['error']

def test_open_file_success(client):
    with patch('app.routes.drive_core.get_drive_core') as mock_get_drive_core, \
         patch('app.routes.drive_core.DriveService') as mock_drive_service:
        
        mock_drive_service_instance = mock_drive_service.return_value
        mock_drive_service_instance.get_file_web_view_link.return_value = ('https://example.com', 'text/plain')

        response = client.get('/drive/test_file_id/open')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'webViewLink' in json_data
        assert 'mimeType' in json_data
        assert json_data['webViewLink'] == 'https://example.com'
        assert json_data['mimeType'] == 'text/plain'

def test_open_file_value_error(client):
    with patch('app.routes.drive_core.get_drive_core') as mock_get_drive_core, \
         patch('app.routes.drive_core.DriveService') as mock_drive_service:
        
        mock_drive_service_instance = mock_drive_service.return_value
        mock_drive_service_instance.get_file_web_view_link.side_effect = ValueError("Invalid file ID")

        response = client.get('/drive/invalid_file_id/open')
        
        assert response.status_code == 401
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == "Invalid file ID"

def test_open_file_general_error(client):
    with patch('app.routes.drive_core.get_drive_core') as mock_get_drive_core, \
         patch('app.routes.drive_core.DriveService') as mock_drive_service:
        
        mock_drive_service_instance = mock_drive_service.return_value
        mock_drive_service_instance.get_file_web_view_link.side_effect = Exception("Unexpected error")

        response = client.get('/drive/test_file_id/open')
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == "Unexpected error"

def test_logout(client):
    with client.session_transaction() as sess:
        sess['user'] = 'test_user'

    response = client.get('/logout')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'message' in json_data
    assert json_data['message'] == "Logged out successfully"
    
    with client.session_transaction() as sess:
        assert 'user' not in sess

def test_cleanup_services(app):
    with app.test_request_context():
        from flask import g
        g.drive_core = 'test_drive_core'
        
        drive_bp.teardown_app_request(None)
        
        assert not hasattr(g, 'drive_core')