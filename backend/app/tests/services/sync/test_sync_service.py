import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from app.services.sync.sync_service import SyncService
from app.services.sync.drive_pinecone_sync import DrivePineconeSync

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
        'user_id': 'test_user_id'
    }

@patch('app.services.sync.sync_service.DrivePineconeSync')
def test_sync_user_drive_full_sync(mock_drive_pinecone_sync, mock_session):
    mock_sync_instance = Mock()
    mock_drive_pinecone_sync.return_value = mock_sync_instance

    result = SyncService.sync_user_drive(mock_session)

    mock_drive_pinecone_sync.assert_called_once()
    mock_sync_instance.full_sync.assert_called_once()
    assert 'last_sync_time' in mock_session
    assert result == {"message": "Sync completed successfully"}

@patch('app.services.sync.sync_service.DrivePineconeSync')
def test_sync_user_drive_incremental_sync(mock_drive_pinecone_sync, mock_session):
    mock_session['last_sync_time'] = '2023-01-01T00:00:00'
    mock_sync_instance = Mock()
    mock_drive_pinecone_sync.return_value = mock_sync_instance

    result = SyncService.sync_user_drive(mock_session)

    mock_drive_pinecone_sync.assert_called_once()
    mock_sync_instance.incremental_sync.assert_called_once_with('2023-01-01T00:00:00')
    assert 'last_sync_time' in mock_session
    assert result == {"message": "Sync completed successfully"}

def test_sync_user_drive_no_credentials():
    session = {}
    result = SyncService.sync_user_drive(session)
    assert result == {"error": "User not authenticated"}