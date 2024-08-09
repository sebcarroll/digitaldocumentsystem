import pytest
from unittest.mock import Mock, patch
from app.services.google_drive.drive_permissions_service import DrivePermissionsService

@pytest.fixture
def mock_credentials():
    return {
        'client_id': 'fake_client_id',
        'client_secret': 'fake_client_secret',
        'refresh_token': 'fake_refresh_token',
        'scopes': ['https://www.googleapis.com/auth/drive']
    }

@pytest.fixture
def drive_permissions_service(mock_credentials):
    with patch('app.services.google_drive.drive_permissions_service.DriveCore') as MockDriveCore:
        mock_drive_core = MockDriveCore.return_value
        mock_drive_core.drive_service = Mock()
        service = DrivePermissionsService(mock_drive_core, user_email='test@example.com', user_id='user123')
        return service

def test_get_people_with_access(drive_permissions_service):
    drive_permissions_service.drive_core.drive_service.files().get().execute.return_value = {
        'owners': [{'emailAddress': 'owner@example.com'}]
    }
    drive_permissions_service.drive_core.drive_service.permissions().list().execute.return_value = {
        'permissions': [
            {'id': 'perm1', 'emailAddress': 'test@example.com', 'role': 'writer'},
            {'id': 'perm2', 'emailAddress': 'other@example.com', 'role': 'reader'}
        ]
    }

    result = drive_permissions_service.get_people_with_access('file123')

    assert result['currentUserRole'] == 'writer'
    assert result['currentUserId'] == 'perm1'
    assert len(result['peopleWithAccess']) == 2

def test_update_permission_success(drive_permissions_service):
    drive_permissions_service.get_user_role = Mock(return_value={'role': 'owner'})
    drive_permissions_service.drive_core.drive_service.permissions().update().execute.return_value = {
        'id': 'perm1',
        'role': 'writer'
    }

    result = drive_permissions_service.update_permission('file123', 'perm1', 'writer')

    assert result['message'] == 'Permission updated successfully'
    assert result['updatedPermission']['role'] == 'writer'

def test_update_permission_unauthorized(drive_permissions_service):
    drive_permissions_service.get_user_role = Mock(return_value={'role': 'reader'})

    result = drive_permissions_service.update_permission('file123', 'perm1', 'writer')

    assert result == ('Only owners and editors can update permissions', 403)

def test_remove_permission_success(drive_permissions_service):
    drive_permissions_service.get_user_role = Mock(return_value={'role': 'owner'})
    drive_permissions_service.drive_core.drive_service.permissions().delete().execute.return_value = {}

    result = drive_permissions_service.remove_permission('file123', 'perm1')

    assert result['message'] == 'Permission removed successfully'

def test_remove_permission_unauthorized(drive_permissions_service):
    drive_permissions_service.get_user_role = Mock(return_value={'role': 'reader'})

    result = drive_permissions_service.remove_permission('file123', 'perm1')

    assert result == ('Only owners and editors can remove permissions', 403)

def test_get_user_role_owner(drive_permissions_service):
    drive_permissions_service.drive_core.drive_service.files().get().execute.return_value = {
        'owners': [{'emailAddress': 'test@example.com'}]
    }

    result = drive_permissions_service.get_user_role('file123')

    assert result['role'] == 'owner'
    assert result['id'] == 'user123'

def test_get_user_role_permission(drive_permissions_service):
    drive_permissions_service.drive_core.drive_service.files().get().execute.return_value = {
        'owners': [{'emailAddress': 'owner@example.com'}],
        'permissions': [{'emailAddress': 'test@example.com', 'role': 'writer', 'id': 'perm123'}]
    }

    result = drive_permissions_service.get_user_role('file123')

    assert result['role'] == 'writer'
    assert result['id'] == 'perm123'