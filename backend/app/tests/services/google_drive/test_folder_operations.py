import pytest
from unittest.mock import Mock, patch
from app.services.google_drive.folder_operations import DriveFolderOperations
import io

@pytest.fixture
def mock_credentials():
    """Fixture to provide mock credentials for testing."""
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
    """Fixture to initialize DriveFolderOperations with a mocked DriveCore."""
    with patch('app.services.google_drive.core.DriveCore') as MockDriveCore:
        mock_drive_core = MockDriveCore.return_value
        mock_drive_core.drive_service = Mock()
        ops = DriveFolderOperations(mock_drive_core)
        return ops, mock_drive_core.drive_service

def test_create_folder(folder_operations):
    """
    Test creating a folder in Google Drive.

    Verifies that the folder is created under the specified parent folder
    and that the correct folder ID is returned.
    """
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
    """
    Test uploading a folder structure to Google Drive.

    Verifies that files are uploaded correctly with the appropriate folder
    hierarchy maintained and that their IDs are returned.
    """
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
        {'id': 'file2_id'},
        {'id': 'extra_id'}  # In case of additional create calls
    ]

    result = ops.upload_folder('parent_folder_id', mock_files)

    # Ensure the uploaded files have the correct IDs and names
    assert len(result['uploaded_files']) == 2
    assert result['uploaded_files'][0]['name'] == 'folder/file1.txt'
    assert result['uploaded_files'][1]['name'] == 'folder/subfolder/file2.txt'
    assert result['uploaded_files'][0]['id'] == 'file1_id'
    assert result['uploaded_files'][1]['id'] == 'file2_id'

    # Check that the number of create calls is within the expected range
    assert mock_drive.files().create.call_count in (4, 5) 

def test_fetch_folders(folder_operations):
    """
    Test fetching folders from Google Drive.

    Verifies that the method retrieves the list of folders under the specified
    parent folder and returns their IDs and names.
    """
    ops, mock_drive = folder_operations
    mock_drive.files().list().execute.return_value = {
        'files': [
            {'id': 'folder1', 'name': 'Folder 1', 'parents': ['parent_id']},
            {'id': 'folder2', 'name': 'Folder 2', 'parents': ['parent_id']}
        ],
        'nextPageToken': None
    }
    
    result = ops.fetch_folders('parent_id')
    
    assert result == {
        "folders": [
            {'id': 'folder1', 'name': 'Folder 1', 'parents': ['parent_id']},
            {'id': 'folder2', 'name': 'Folder 2', 'parents': ['parent_id']}
        ],
        "nextPageToken": None
    }
    mock_drive.files().list.assert_called_with(
        q="'parent_id' in parents and mimeType='application/vnd.google-apps.folder'",
        spaces='drive',
        fields='nextPageToken, files(id, name, parents)',
        pageToken=None,
        pageSize=1000,
        supportsAllDrives=True
    )
