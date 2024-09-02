import pytest
from unittest.mock import Mock, patch
from app.services.google_drive.file_operations import DriveFileOperations

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
def file_operations(mock_credentials):
    """Fixture to initialize DriveFileOperations with a mocked DriveCore."""
    with patch('app.services.google_drive.core.DriveCore') as MockDriveCore:
        mock_drive_core = MockDriveCore.return_value
        mock_drive_core.drive_service = Mock()
        ops = DriveFileOperations(mock_drive_core)
        return ops, mock_drive_core.drive_service

def test_open_file(file_operations):
    """Test opening a file and retrieving its webViewLink."""
    ops, mock_drive = file_operations
    mock_drive.files().get().execute.return_value = {'webViewLink': 'https://example.com'}
    
    result = ops.open_file('file_id')
    
    assert result == {"webViewLink": "https://example.com"}
    mock_drive.files().get.assert_called_with(fileId='file_id', fields='webViewLink')

def test_upload_file(file_operations):
    """Test uploading a file to a specified folder."""
    ops, mock_drive = file_operations
    mock_file = Mock()
    mock_file.filename = 'test.txt'
    mock_file.read.return_value = b'file content'  # Mock file content
    mock_drive.files().create().execute.return_value = {'id': 'new_file_id'}
    
    result = ops.upload_file(mock_file, 'folder_id')
    
    assert result == {"id": "new_file_id"}
    mock_drive.files().create.assert_called()

def test_create_doc(file_operations):
    """Test creating a new Google Doc in a specified folder."""
    ops, mock_drive = file_operations
    mock_drive.files().create().execute.return_value = {'id': 'doc_id', 'webViewLink': 'https://doc.com'}
    
    result = ops.create_doc('folder_id')
    
    assert result == {"id": "doc_id", "webViewLink": "https://doc.com"}
    mock_drive.files().create.assert_called()

def test_move_files(file_operations):
    """Test moving files from one folder to another."""
    ops, mock_drive = file_operations
    mock_drive.files().get().execute.return_value = {'parents': ['old_folder']}
    mock_drive.files().update().execute.return_value = {'id': 'file_id', 'parents': ['new_folder']}
    
    result = ops.move_files(['file_id'], 'new_folder')
    
    assert result == {"message": "Files moved successfully", "moved_files": [{"id": "file_id", "parents": ["new_folder"]}]}
    mock_drive.files().update.assert_called()

def test_delete_files(file_operations):
    """Test deleting files by their IDs."""
    ops, mock_drive = file_operations
    
    result = ops.delete_files(['file_id'])
    
    assert result == {"message": "Files deleted successfully", "deleted_files": ["file_id"]}
    mock_drive.files().delete.assert_called_with(fileId='file_id')

def test_copy_files(file_operations):
    """Test copying files and verifying the copied file's ID and name."""
    ops, mock_drive = file_operations
    mock_drive.files().copy().execute.return_value = {'id': 'new_file_id', 'name': 'Copy of file'}
    
    result = ops.copy_files(['file_id'])
    
    assert result == {"message": "Files copied successfully", "copied_files": [{"id": "new_file_id", "name": "Copy of file"}]}
    mock_drive.files().copy.assert_called_with(fileId='file_id', fields='id, name')

def test_rename_file(file_operations):
    """Test renaming a file and verifying the updated name."""
    ops, mock_drive = file_operations
    mock_drive.files().update().execute.return_value = {'id': 'file_id', 'name': 'new_name'}
    
    result = ops.rename_file('file_id', 'new_name')
    
    assert result == {"id": "file_id", "name": "new_name"}
    mock_drive.files().update.assert_called_with(fileId='file_id', body={'name': 'new_name'}, fields='id, name')
