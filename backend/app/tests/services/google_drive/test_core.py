import pytest
from unittest.mock import Mock, patch
from google.oauth2.credentials import Credentials
from app.services.google_drive.core import DriveCore

@pytest.fixture
def mock_credentials_dict():
    """Fixture to provide a mock dictionary of credentials for testing."""
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
    """Fixture to provide a mock Google Drive service for testing."""
    return Mock()

@pytest.fixture
def mock_people_service():
    """Fixture to provide a mock Google People service for testing."""
    return Mock()

def test_drive_core_initialization(mock_credentials_dict):
    """
    Test the initialization of the DriveCore class.
    
    This test verifies that the DriveCore is initialized with the correct
    credentials and that the Google Drive and People services are correctly built.
    """
    with patch('app.services.google_drive.core.build') as mock_build:
        # Mock the build function to return a mock service for both drive and people
        mock_build.side_effect = [Mock(), Mock()]  
        
        drive_core = DriveCore(mock_credentials_dict)
        
        assert isinstance(drive_core.credentials, Credentials)
        assert mock_build.call_count == 2
        mock_build.assert_any_call('drive', 'v3', credentials=drive_core.credentials)
        mock_build.assert_any_call('people', 'v1', credentials=drive_core.credentials)

def test_list_folder_contents(mock_credentials_dict, mock_drive_service):
    """
    Test the list_folder_contents method of DriveCore.
    
    This test ensures that the contents of a Google Drive folder are listed correctly.
    """
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
    """
    Test the list_folder_contents method of DriveCore with pagination.
    
    This test verifies that the DriveCore correctly handles paginated responses
    from the Google Drive API when listing folder contents.
    """
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