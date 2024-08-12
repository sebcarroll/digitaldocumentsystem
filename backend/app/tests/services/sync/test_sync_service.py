"""
Unit tests for the SyncService class.

This module contains pytest-based unit tests for the SyncService class,
covering various scenarios including success cases and error handling.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from app.services.sync.sync_service import SyncService, SyncError

@pytest.fixture
def mock_redis():
    """Fixture to mock the redis client."""
    with patch('app.services.sync.sync_service.redis_client') as mock:
        yield mock

@pytest.fixture
def mock_celery_task():
    """Fixture to mock the Celery task."""
    with patch('app.services.sync.sync_service.sync_drive_to_pinecone') as mock:
        yield mock

def test_start_sync_success(mock_redis, mock_celery_task):
    """Test successful start of sync process."""
    user_id = "test_user"
    result = SyncService.start_sync(user_id)
    
    mock_redis.set.assert_called_once_with(f'user:{user_id}:sync_status', 'in_progress')
    mock_celery_task.delay.assert_called_once_with(user_id)
    assert result == {"message": "Sync process initiated"}

def test_start_sync_failure(mock_redis):
    """Test failure in starting sync process."""
    user_id = "test_user"
    mock_redis.set.side_effect = Exception("Redis error")
    
    with pytest.raises(SyncError):
        SyncService.start_sync(user_id)
    
    mock_redis.set.assert_called_once_with(f'user:{user_id}:sync_status', 'in_progress')

def test_get_sync_status_success(mock_redis):
    """Test successful retrieval of sync status."""
    user_id = "test_user"
    mock_redis.get.return_value = 'in_progress'
    
    status = SyncService.get_sync_status(user_id)
    
    mock_redis.get.assert_called_once_with(f'user:{user_id}:sync_status')
    assert status == 'in_progress'

def test_get_sync_status_not_found(mock_redis):
    """Test scenario where sync status is not found."""
    user_id = "test_user"
    mock_redis.get.return_value = None
    
    with pytest.raises(SyncError):
        SyncService.get_sync_status(user_id)

def test_is_sync_in_progress_true(mock_redis):
    """Test when sync is in progress."""
    user_id = "test_user"
    mock_redis.get.return_value = 'in_progress'
    
    assert SyncService.is_sync_in_progress(user_id) is True

def test_is_sync_in_progress_false(mock_redis):
    """Test when sync is not in progress."""
    user_id = "test_user"
    mock_redis.get.return_value = 'completed'
    
    assert SyncService.is_sync_in_progress(user_id) is False

def test_start_sync_if_not_in_progress_started(mock_redis, mock_celery_task):
    """Test starting sync when not already in progress."""
    user_id = "test_user"
    mock_redis.get.return_value = 'completed'
    
    result = SyncService.start_sync_if_not_in_progress(user_id)
    
    assert result is True
    mock_celery_task.delay.assert_called_once_with(user_id)
