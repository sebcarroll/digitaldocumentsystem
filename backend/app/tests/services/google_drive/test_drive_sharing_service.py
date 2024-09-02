import pytest
from unittest.mock import Mock, patch
from app.services.google_drive.drive_sharing_service import DriveSharingService

@pytest.fixture
def mock_credentials():
    """Fixture to provide mock credentials for testing."""
    return {
        'token': 'fake_token',
        'refresh_token': 'fake_refresh_token',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_id': 'fake_client_id',
        'client_secret': 'fake_client_secret',
        'scopes': ['https://www.googleapis.com/auth/drive']
    }

@pytest.fixture
def drive_sharing_service(mock_credentials):
    """Fixture to initialize DriveSharingService with a mocked DriveCore."""
    with patch('app.services.google_drive.drive_sharing_service.DriveCore') as MockDriveCore:
        mock_drive_core = MockDriveCore.return_value
        mock_drive_core.drive_service = Mock()
        service = DriveSharingService(mock_drive_core)
        return service
    
def test_share_item_success(drive_sharing_service):
    """
    Test successful sharing of an item with multiple users.
    
    Verifies that the item is shared with all specified users and that the 
    appropriate success message is returned.
    """
    # Mock the successful creation of permissions
    drive_sharing_service.drive_core.drive_service.permissions().create().execute.return_value = {'id': 'perm123'}
    
    result = drive_sharing_service.share_item('file123', ['user1@example.com', 'user2@example.com'], 'reader')
    
    assert result['message'] == "Item shared successfully"
    assert len(result['shared_with']) == 2
    drive_sharing_service.drive_core.drive_service.permissions().create.assert_called()

def test_share_item_partial_failure(drive_sharing_service):
    """
    Test partial failure when sharing an item.
    
    Verifies that if sharing with one user fails, the method still returns 
    success for the other users and includes an error message.
    """
    # Mock the side effect to simulate partial failure
    def side_effect(**kwargs):
        if kwargs['body']['emailAddress'] == 'user1@example.com':
            return Mock(execute=Mock(return_value={'id': 'perm123'}))
        else:
            raise Exception("Sharing failed")

    drive_sharing_service.drive_core.drive_service.permissions().create.side_effect = side_effect
    
    result = drive_sharing_service.share_item('file123', ['user1@example.com', 'user2@example.com'], 'reader')
    
    assert "error" in result
    assert len(result['shared_with']) == 1
    assert "Failed to share with user2@example.com" in result['error']

def test_update_general_access_anyone_with_link(drive_sharing_service):
    """
    Test updating general access to 'Anyone with the link'.
    
    Verifies that the general access is successfully updated for a file.
    """
    # Mock the file type to be non-folder (e.g., a regular file)
    drive_sharing_service.drive_core.drive_service.files().get().execute.return_value = {'mimeType': 'file'}
    
    result = drive_sharing_service.update_general_access('file123', 'Anyone with the link', 'reader')
    
    assert result['message'] == "General access updated successfully for file"
    drive_sharing_service.drive_core.drive_service.permissions().create.assert_called_once()

def test_update_general_access_restricted(drive_sharing_service):
    """
    Test updating general access to 'Restricted'.
    
    Verifies that the general access is successfully restricted and existing 
    'anyone' permissions are removed.
    """
    # Mock the file type to be non-folder and permissions to include 'anyone'
    drive_sharing_service.drive_core.drive_service.files().get().execute.return_value = {'mimeType': 'file'}
    drive_sharing_service.drive_core.drive_service.permissions().list().execute.return_value = {
        'permissions': [{'id': 'perm123', 'type': 'anyone'}]
    }
    
    result = drive_sharing_service.update_general_access('file123', 'Restricted', 'reader')
    
    assert result['message'] == "General access updated successfully for file"
    drive_sharing_service.drive_core.drive_service.permissions().delete.assert_called_once()

def test_update_general_access_folder(drive_sharing_service):
    """
    Test updating general access for a folder.
    
    Verifies that general access is successfully updated for a folder and 
    applies to its contents.
    """
    # Mock the file type to be a folder
    drive_sharing_service.drive_core.drive_service.files().get().execute.return_value = {
        'mimeType': 'application/vnd.google-apps.folder'
    }
    drive_sharing_service.drive_core.list_folder_contents.return_value = []
    
    result = drive_sharing_service.update_general_access('folder123', 'Anyone with the link', 'reader')
    
    assert result['message'] == "General access updated successfully for folder"
    drive_sharing_service.drive_core.drive_service.permissions().create.assert_called_once()