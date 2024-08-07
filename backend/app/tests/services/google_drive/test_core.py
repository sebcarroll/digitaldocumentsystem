import pytest
from unittest.mock import Mock, patch
from app.services.google_drive.core import DriveCore

@pytest.fixture
def mock_credentials():
    return {
        'token': 'test_token',
        'refresh_token': 'test_refresh_token',
        'token_uri': 'test_token_uri',
        'client_id': 'test_client_id',
        'client_secret': 'test_client_secret',
        'scopes': ['test_scope']
    }

@pytest.fixture
def drive_core(mock_credentials):
    with patch('app.services.google_drive.core.build') as mock_build:
        mock_drive = Mock()
        mock_people = Mock()
        mock_build.side_effect = [mock_drive, mock_people]
        core = DriveCore(mock_credentials)
        return core, mock_drive, mock_people

def test_drive_core_initialization(drive_core):
    core, mock_drive, mock_people = drive_core
    assert core.drive_service == mock_drive
    assert core.people_service == mock_people

def test_list_folder_contents(drive_core):
    core, mock_drive, _ = drive_core
    mock_files = Mock()
    mock_drive.files.return_value.list.return_value.execute.side_effect = [
        {
            'files': [{'id': 'file1'}, {'id': 'file2'}],
            'nextPageToken': 'token1'
        },
        {
            'files': [{'id': 'file3'}],
            'nextPageToken': None
        }
    ]

    results = core.list_folder_contents('folder_id')

    assert results == [{'id': 'file1'}, {'id': 'file2'}, {'id': 'file3'}]
    assert mock_drive.files().list.call_count == 2