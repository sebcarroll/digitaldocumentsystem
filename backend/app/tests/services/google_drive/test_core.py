import pytest
from unittest.mock import Mock, patch
from google.oauth2.credentials import Credentials
from app.services.google_drive.core import DriveCore

@pytest.fixture
def mock_credentials_dict():
    return {
        'token': 'fake_token',
        'refresh_token': 'fake_refresh_token',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_id': 'fake_client_id',
        'client_secret': 'fake_client_secret',
        'scopes': ['https://www.googleapis.com/auth/drive']
    }

@pytest.fixture
def mock_drive_service():
    return Mock()

@pytest.fixture
def mock_people_service():
    return Mock()

def test_drive_core_initialization(mock_credentials_dict):
    with patch('app.services.google_drive.core.build') as mock_build:
        mock_build.side_effect = [Mock(), Mock()]  # For drive_service and people_service
        drive_core = DriveCore(mock_credentials_dict)
        
        assert isinstance(drive_core.credentials, Credentials)
        assert mock_build.call_count == 2
        mock_build.assert_any_call('drive', 'v3', credentials=drive_core.credentials)
        mock_build.assert_any_call('people', 'v1', credentials=drive_core.credentials)

def test_list_folder_contents(mock_credentials_dict, mock_drive_service):
    with patch('app.services.google_drive.core.build', return_value=mock_drive_service):
        drive_core = DriveCore(mock_credentials_dict)
        
        # Mock the files().list().execute() chain
        mock_execute = Mock()
        mock_execute.execute.return_value = {
            'files': [
                {'id': 'file1', 'name': 'File 1', 'mimeType': 'text/plain'},
                {'id': 'file2', 'name': 'File 2', 'mimeType': 'application/pdf'}
            ],
            'nextPageToken': None
        }
        mock_drive_service.files.return_value.list.return_value = mock_execute

        result = drive_core.list_folder_contents('folder_id')

        assert len(result) == 2
        assert result[0]['id'] == 'file1'
        assert result[1]['name'] == 'File 2'

        mock_drive_service.files.return_value.list.assert_called_once_with(
            q="'folder_id' in parents",
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType)',
            pageToken=None,
            supportsAllDrives=True
        )

def test_list_folder_contents_pagination(mock_credentials_dict, mock_drive_service):
    with patch('app.services.google_drive.core.build', return_value=mock_drive_service):
        drive_core = DriveCore(mock_credentials_dict)
        
        # Mock the files().list().execute() chain with pagination
        mock_execute = Mock()
        mock_execute.execute.side_effect = [
            {
                'files': [{'id': 'file1', 'name': 'File 1', 'mimeType': 'text/plain'}],
                'nextPageToken': 'token1'
            },
            {
                'files': [{'id': 'file2', 'name': 'File 2', 'mimeType': 'application/pdf'}],
                'nextPageToken': None
            }
        ]
        mock_drive_service.files.return_value.list.return_value = mock_execute

        result = drive_core.list_folder_contents('folder_id')

        assert len(result) == 2
        assert result[0]['id'] == 'file1'
        assert result[1]['name'] == 'File 2'

        assert mock_drive_service.files.return_value.list.call_count == 2
        mock_drive_service.files.return_value.list.assert_any_call(
            q="'folder_id' in parents",
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType)',
            pageToken=None,
            supportsAllDrives=True
        )
        mock_drive_service.files.return_value.list.assert_any_call(
            q="'folder_id' in parents",
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType)',
            pageToken='token1',
            supportsAllDrives=True
        )