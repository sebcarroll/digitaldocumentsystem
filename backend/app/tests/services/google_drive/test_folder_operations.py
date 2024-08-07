import pytest
from unittest.mock import Mock, patch
from app.services.google_drive.folder_operations import DriveFolderOperations
import io

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
def folder_operations(mock_credentials):
    with patch('app.services.google_drive.core.build') as mock_build:
        mock_drive = Mock()
        mock_people = Mock()
        mock_build.side_effect = [mock_drive, mock_people]
        ops = DriveFolderOperations(mock_credentials)
        ops.drive_service = mock_drive
        ops.people_service = mock_people
        return ops, mock_drive


def test_create_folder(folder_operations):
    ops, mock_drive = folder_operations
    mock_drive.files().create().execute.return_value = {'id': 'new_folder_id'}
    
    result = ops.create_folder('parent_folder_id', 'New Folder')
    
    assert result == {"id": "new_folder_id"}
    mock_drive.files().create.assert_called_with(
        body={
            'name': 'New Folder',
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': ['parent_folder_id']
        },
        fields='id'
    )

def test_upload_folder(folder_operations):
    ops, mock_drive = folder_operations

    # Create mock file-like objects
    mock_file1 = io.BytesIO(b"file1 content")
    mock_file1.filename = 'folder/file1.txt'
    mock_file1.content_type = 'text/plain'

    mock_file2 = io.BytesIO(b"file2 content")
    mock_file2.filename = 'folder/subfolder/file2.txt'
    mock_file2.content_type = 'text/plain'

    mock_files = [mock_file1, mock_file2]

    mock_drive.files().create().execute.side_effect = [
        {'id': 'folder_id'},
        {'id': 'subfolder_id'},
        {'id': 'file1_id'},
        {'id': 'file2_id'}
    ]

    result = ops.upload_folder('parent_folder_id', mock_files)

    assert len(result['uploaded_files']) == 2
    assert result['uploaded_files'][0]['name'] == 'folder/file1.txt'
    assert result['uploaded_files'][1]['name'] == 'folder/subfolder/file2.txt'
    assert result['uploaded_files'][0]['id'] == 'file1_id'
    assert result['uploaded_files'][1]['id'] == 'file2_id'

    # Assert that create was called 4 times (2 folders, 2 files)
    assert mock_drive.files().create.call_count == 4

    # Check the order of calls
    calls = mock_drive.files().create.call_args_list
    assert calls[0][1]['body']['name'] == 'folder'
    assert calls[0][1]['body']['mimeType'] == 'application/vnd.google-apps.folder'
    assert calls[1][1]['body']['name'] == 'subfolder'
    assert calls[1][1]['body']['mimeType'] == 'application/vnd.google-apps.folder'
    assert calls[2][1]['body']['name'] == 'file1.txt'
    assert calls[2][1]['body']['mimeType'] != 'application/vnd.google-apps.folder'
    assert calls[3][1]['body']['name'] == 'file2.txt'
    assert calls[3][1]['body']['mimeType'] != 'application/vnd.google-apps.folder'
def test_fetch_folders(folder_operations):
    ops, mock_drive = folder_operations
    mock_drive.files().list().execute.return_value = {
        'files': [
            {'id': 'folder1', 'name': 'Folder 1'},
            {'id': 'folder2', 'name': 'Folder 2'}
        ]
    }
    
    result = ops.fetch_folders('parent_id')
    
    assert result == {
        "folders": [
            {'id': 'folder1', 'name': 'Folder 1'},
            {'id': 'folder2', 'name': 'Folder 2'}
        ]
    }
    mock_drive.files().list.assert_called_with(
        q="'parent_id' in parents and mimeType='application/vnd.google-apps.folder'",
        spaces='drive',
        fields='files(id, name)',
        supportsAllDrives=True
    )