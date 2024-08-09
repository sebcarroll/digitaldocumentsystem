import pytest
from unittest.mock import Mock, patch, call
from flask import g
from app.services.google_drive.drive_service import DriveService
from app.services.google_drive.core import DriveCore
from google.auth.transport.requests import Request

@pytest.fixture
def mock_session():
    return {'credentials': {
        'token': 'test_token',
        'refresh_token': 'test_refresh_token',
        'token_uri': 'test_token_uri',
        'client_id': 'test_client_id',
        'client_secret': 'test_client_secret',
        'scopes': ['test_scope'],
        'expiry': None 
    }}

@pytest.fixture
def drive_service(mock_session):
    drive_core = DriveCore(mock_session['credentials'])
    return DriveService(drive_core)

@patch('app.services.google_drive.drive_service.Request')
@patch('app.services.google_drive.drive_service.build')
def test_get_services(mock_build, mock_request, app, drive_service):
    with app.app_context():
        mock_drive = Mock()
        mock_people = Mock()
        mock_build.side_effect = [mock_drive, mock_people]
        
        with patch.object(drive_service.drive_core.credentials, 'refresh') as mock_refresh:
            drive, people = drive_service.get_services()

            # Log the actual calls to help with debugging
            print(mock_build.mock_calls)

            # Check that build was called with the correct arguments
            mock_build.assert_has_calls([
                call('drive', 'v3', credentials=drive_service.drive_core.credentials),
                call('people', 'v1', credentials=drive_service.drive_core.credentials)
            ], any_order=True)

def test_list_folder_contents(app, drive_service):
    with app.app_context():
        mock_drive = Mock()
        mock_files = Mock()
        mock_drive.files.return_value.list.return_value.execute.return_value = {
            'files': [
                {'name': 'file1', 'id': 'id1', 'mimeType': 'type1'},
                {'name': 'file2', 'id': 'id2', 'mimeType': 'type2'}
            ],
            'nextPageToken': 'next_token'
        }

        with patch.object(drive_service, 'get_services', return_value=(mock_drive, None)):
            file_list, next_page_token = drive_service.list_folder_contents('folder_id')

        assert file_list == [
            {'name': 'file1', 'id': 'id1', 'mimeType': 'type1'},
            {'name': 'file2', 'id': 'id2', 'mimeType': 'type2'}
        ]
        assert next_page_token == 'next_token'

def test_get_file_web_view_link(app, drive_service):
    with app.app_context():
        mock_drive = Mock()
        mock_drive.files.return_value.get.return_value.execute.return_value = {
            'webViewLink': 'https://example.com',
            'mimeType': 'application/pdf'
        }

        with patch.object(drive_service, 'get_services', return_value=(mock_drive, None)):
            web_view_link, mime_type = drive_service.get_file_web_view_link('file_id')

        assert web_view_link == 'https://example.com'
        assert mime_type == 'application/pdf'

def test_cleanup_services(app, drive_service):
    with app.app_context():
        mock_drive = Mock()
        mock_people = Mock()
        g.drive_service = mock_drive
        g.people_service = mock_people

        drive_service.cleanup_services()

        assert 'drive_service' not in g
        assert 'people_service' not in g
        mock_drive.close.assert_called_once()
        mock_people.close.assert_called_once()
