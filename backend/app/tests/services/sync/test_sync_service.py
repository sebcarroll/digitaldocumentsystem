import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from app.services.sync.sync_service import SyncService
from google.oauth2.credentials import Credentials

@pytest.fixture
def mock_session():
    return {
        'credentials': {
            'token': 'fake_token',
            'refresh_token': 'fake_refresh_token',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': 'fake_client_id',
            'client_secret': 'fake_client_secret',
            'scopes': ['https://www.googleapis.com/auth/drive']
        },
        'user_id': 'test_user_id',
        'last_sync_time': '2023-01-01T00:00:00' 
    }

@patch('app.services.sync.sync_service.UserService')
@patch('app.services.sync.sync_service.GoogleDriveService')
@patch('app.services.sync.sync_service.DrivePineconeSync')
def test_sync_user_drive_full_sync(mock_drive_pinecone_sync, mock_google_drive_service, mock_user_service, mock_session):
    # Set last_sync_time to None to trigger full sync
    mock_session['last_sync_time'] = None
    mock_user_service.return_value.get_user.return_value = mock_session
    mock_sync_instance = Mock()
    mock_drive_pinecone_sync.return_value = mock_sync_instance

    result = SyncService.sync_user_drive('test_user_id')

    mock_google_drive_service.assert_called_once()
    mock_drive_pinecone_sync.assert_called_once()
    mock_sync_instance.full_sync.assert_called_once()  # Ensure full_sync was called
    assert result == {"message": "Sync completed successfully"}

@patch('app.services.sync.sync_service.UserService')
@patch('app.services.sync.sync_service.GoogleDriveService')
@patch('app.services.sync.sync_service.DrivePineconeSync')
def test_sync_user_drive_incremental_sync(mock_drive_pinecone_sync, mock_google_drive_service, mock_user_service, mock_session):
    mock_user_service.return_value.get_user.return_value = mock_session
    mock_sync_instance = Mock()
    mock_drive_pinecone_sync.return_value = mock_sync_instance

    result = SyncService.sync_user_drive(mock_session['user_id'])

    mock_google_drive_service.assert_called_once()
    mock_drive_pinecone_sync.assert_called_once()
    mock_sync_instance.incremental_sync.assert_called_once_with('2023-01-01T00:00:00')
    assert 'last_sync_time' in mock_session
    assert result == {"message": "Sync completed successfully"}

@patch('app.services.sync.sync_service.UserService')
def test_sync_user_drive_no_credentials(mock_user_service):
    mock_user_service.return_value.get_user.return_value = None
    result = SyncService.sync_user_drive('test_user_id')
    assert result == {"error": "User not authenticated or user_id missing"}

@patch('app.services.sync.sync_service.UserService')
def test_sync_user_drive_invalid_credentials(mock_user_service):
    mock_user_service.return_value.get_user.return_value = {
        'credentials': 'invalid_format',
        'user_id': 'test_user_id'
    }
    result = SyncService.sync_user_drive('test_user_id')
    assert result == {"error": "Invalid credentials format"}

@patch('app.services.sync.sync_service.UserService')
def test_sync_user_drive_missing_credentials(mock_user_service):
    mock_user_service.return_value.get_user.return_value = {
        'user_id': 'test_user_id'
    }
    result = SyncService.sync_user_drive('test_user_id')
    assert result == {"error": "Credentials missing"}