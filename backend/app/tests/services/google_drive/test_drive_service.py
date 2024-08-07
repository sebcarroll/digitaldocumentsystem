import pytest
from unittest.mock import Mock, patch
from flask import g
from app.services.google_drive.drive_service import DriveService

@pytest.fixture
def mock_session():
    return {'credentials': {
        'token': 'test_token',
        'refresh_token': 'test_refresh_token',
        'token_uri': 'test_token_uri',
        'client_id': 'test_client_id',
        'client_secret': 'test_client_secret',
        'scopes': ['test_scope']
    }}

@pytest.fixture
def drive_service(mock_session):
    return DriveService(mock_session)

def test_get_services(app, drive_service):
    with app.app_context():
        with patch('app.services.google_drive.drive_service.build') as mock_build:
            mock_drive = Mock()
            mock_people = Mock()
            mock_build.side_effect = [mock_drive, mock_people]

            drive, people = drive_service.get_services()

            assert drive == mock_drive
            assert people == mock_people
            assert g.drive_service == mock_drive
            assert g.people_service == mock_people

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