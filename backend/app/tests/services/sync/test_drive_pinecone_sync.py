"""
This module contains unit tests for the DrivePineconeSync class.

It tests various functionalities of the DrivePineconeSync class, including
file and folder synchronization, error handling, and integration with
Google Drive and Pinecone services.
"""

import pytest
import logging
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from app.services.sync.drive_pinecone_sync import DrivePineconeSync
from config import Config

@pytest.fixture
def mock_drive_service():
    """Create and return a mock Google Drive service."""
    return Mock()

@pytest.fixture
def mock_pinecone_manager():
    """Create and return a mock Pinecone manager."""
    with patch('app.services.sync.drive_pinecone_sync.PineconeManager') as mock:
        yield mock.return_value

@pytest.fixture
def drive_pinecone_sync(mock_drive_service, mock_pinecone_manager):
    """Create and return a DrivePineconeSync instance with mock services."""
    with patch('app.services.sync.drive_pinecone_sync.PineconeManager') as mock_pinecone:
        mock_pinecone.return_value = mock_pinecone_manager
        return DrivePineconeSync('test_user_id', mock_drive_service)

def test_sync_file(drive_pinecone_sync, mock_drive_service, mock_pinecone_manager):
    """Test the sync_file method of DrivePineconeSync."""
    mock_drive_service.get_file_metadata.return_value = {
        'id': 'test_file_id',
        'name': 'test_file.txt',
        'mimeType': 'text/plain',
        'createdTime': '2023-01-01T00:00:00Z',
        'modifiedTime': '2023-01-02T00:00:00Z',
        'owners': [{'emailAddress': 'owner@example.com'}],
        'parents': ['parent_folder_id'],
        'webViewLink': 'https://example.com/view',
        'permissions': [
            {'emailAddress': 'reader@example.com', 'role': 'reader'},
            {'emailAddress': 'writer@example.com', 'role': 'writer'}
        ]
    }
    mock_drive_service.get_file_content.return_value = 'File content'

    drive_pinecone_sync.sync_file('test_file_id')

    mock_drive_service.get_file_metadata.assert_called_once_with('test_file_id')
    mock_drive_service.get_file_content.assert_called_once_with('test_file_id')
    mock_pinecone_manager.upsert_document.assert_called_once()

    upserted_doc = mock_pinecone_manager.upsert_document.call_args[0][0]
    assert upserted_doc['googleDriveId'] == 'test_file_id'
    assert upserted_doc['title'] == 'test_file.txt'
    assert upserted_doc['content'] == 'File content'
    assert upserted_doc['accessControl']['ownerId'] == 'owner@example.com'
    assert 'reader@example.com' in upserted_doc['accessControl']['readers']
    assert 'writer@example.com' in upserted_doc['accessControl']['writers']

def test_sync_folder(drive_pinecone_sync, mock_drive_service, caplog):
    """Test the sync_folder method of DrivePineconeSync."""
    caplog.set_level(logging.DEBUG)
    
    mock_drive_service.get_folder_metadata.return_value = {
        'id': 'test_folder_id',
        'name': 'Test Folder',
        'createdTime': '2023-01-01T00:00:00Z',
        'modifiedTime': '2023-01-02T00:00:00Z',
        'owners': [{'emailAddress': 'owner@example.com'}],
        'parents': ['parent_folder_id'],
        'permissions': [
            {'emailAddress': 'reader@example.com', 'role': 'reader'},
            {'emailAddress': 'writer@example.com', 'role': 'writer'}
        ]
    }
    mock_drive_service.list_folder_contents.return_value = [
        {'id': 'file1', 'mimeType': 'text/plain'},
        {'id': 'file2', 'mimeType': 'text/plain'}
    ]

    with patch.object(drive_pinecone_sync, 'sync_file') as mock_sync_file:
        logging.debug("Starting test_sync_folder")
        
        drive_pinecone_sync.sync_folder('test_folder_id')
        
        logging.debug("sync_folder completed without raising an exception")

        mock_drive_service.get_folder_metadata.assert_called_once_with('test_folder_id')
        mock_drive_service.list_folder_contents.assert_called_once_with('test_folder_id')
        mock_sync_file.assert_any_call('file1')
        mock_sync_file.assert_any_call('file2')

    logging.debug("test_sync_folder completed")

    print("\nCaptured logs:")
    print(caplog.text)

def test_full_sync(drive_pinecone_sync):
    """Test the full_sync method of DrivePineconeSync."""
    with patch.object(drive_pinecone_sync, 'sync_folder') as mock_sync_folder, \
         patch.object(drive_pinecone_sync, 'store_sync_log') as mock_store_sync_log:
        drive_pinecone_sync.full_sync()

    mock_sync_folder.assert_called_once_with()
    mock_store_sync_log.assert_called_once()
    stored_log = mock_store_sync_log.call_args[0][0]
    assert stored_log['userId'] == 'test_user_id'
    assert stored_log['status'] == 'completed'
    assert stored_log['syncType'] == 'full'

def test_incremental_sync(drive_pinecone_sync, mock_drive_service):
    """Test the incremental_sync method of DrivePineconeSync."""
    last_sync_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
    mock_drive_service.list_changed_files.return_value = [
        {'id': 'changed_file1'},
        {'id': 'changed_file2'}
    ]

    with patch.object(drive_pinecone_sync, 'sync_file') as mock_sync_file, \
         patch.object(drive_pinecone_sync, 'store_sync_log') as mock_store_sync_log:
        drive_pinecone_sync.incremental_sync(last_sync_time)

    mock_drive_service.list_changed_files.assert_called_once_with(last_sync_time)
    mock_sync_file.assert_any_call('changed_file1')
    mock_sync_file.assert_any_call('changed_file2')
    mock_store_sync_log.assert_called_once()
    stored_log = mock_store_sync_log.call_args[0][0]
    assert stored_log['userId'] == 'test_user_id'
    assert stored_log['status'] == 'completed'
    assert stored_log['syncType'] == 'incremental'
    assert stored_log['changesProcessed'] == 2

def test_handle_file_open(drive_pinecone_sync):
    """Test the handle_file_open method of DrivePineconeSync."""
    with patch.object(drive_pinecone_sync, 'sync_file') as mock_sync_file:
        drive_pinecone_sync.handle_file_open('test_file_id')
    mock_sync_file.assert_called_once_with('test_file_id')

def test_handle_file_close(drive_pinecone_sync):
    """Test the handle_file_close method of DrivePineconeSync."""
    with patch.object(drive_pinecone_sync, 'sync_file') as mock_sync_file:
        drive_pinecone_sync.handle_file_close('test_file_id')
    mock_sync_file.assert_called_once_with('test_file_id')

def test_handle_file_change(drive_pinecone_sync):
    """Test the handle_file_change method of DrivePineconeSync."""
    with patch.object(drive_pinecone_sync, 'sync_file') as mock_sync_file:
        drive_pinecone_sync.handle_file_change('test_file_id')
    mock_sync_file.assert_called_once_with('test_file_id')

def test_sync_file_error(drive_pinecone_sync, mock_drive_service, caplog):
    """Test error handling in the sync_file method."""
    mock_drive_service.get_file_metadata.side_effect = Exception("Test error")

    drive_pinecone_sync.sync_file('test_file_id')

    assert "Error syncing file test_file_id: Test error" in caplog.text

def test_sync_folder_error(drive_pinecone_sync, mock_drive_service, caplog):
    """Test error handling in the sync_folder method."""
    mock_drive_service.get_folder_metadata.side_effect = Exception("Test error")

    drive_pinecone_sync.sync_folder('test_folder_id')

    assert "Error syncing folder test_folder_id: Test error" in caplog.text

def test_full_sync_error(drive_pinecone_sync):
    """Test error handling in the full_sync method."""
    with patch.object(drive_pinecone_sync, 'sync_folder', side_effect=Exception("Test error")), \
         patch.object(drive_pinecone_sync, 'store_sync_log') as mock_store_sync_log:
        drive_pinecone_sync.full_sync()

    mock_store_sync_log.assert_called_once()
    stored_log = mock_store_sync_log.call_args[0][0]
    assert stored_log['status'] == 'failed'
    assert stored_log['errors'] == ['Test error']

def test_incremental_sync_error(drive_pinecone_sync, mock_drive_service):
    """Test error handling in the incremental_sync method."""
    mock_drive_service.list_changed_files.side_effect = Exception("Test error")

    with patch.object(drive_pinecone_sync, 'store_sync_log') as mock_store_sync_log:
        drive_pinecone_sync.incremental_sync(datetime.now(timezone.utc))

    mock_store_sync_log.assert_called_once()
    stored_log = mock_store_sync_log.call_args[0][0]
    assert stored_log['status'] == 'failed'
    assert stored_log['errors'] == ['Test error']