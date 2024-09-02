"""
Test module for the Google Drive service operations.

This module contains unit tests for the DriveService class, which handles
various Google Drive operations such as listing folder contents, retrieving
file details, and managing service connections.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, g
from app.services.google_drive.drive_service import DriveService
from app.services.google_drive.core import DriveCore

@pytest.fixture
def app():
    """
    Create and configure a Flask app for testing.

    Returns:
        Flask: A Flask application instance.
    """
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def drive_service():
    """
    Create a DriveService instance for testing.

    Returns:
        DriveService: An instance of the DriveService class.
    """
    mock_drive_core = Mock(spec=DriveCore)
    mock_drive_core.credentials = Mock()
    mock_drive_core.credentials.expired = False
    return DriveService(mock_drive_core)

def test_get_services(app, drive_service):
    """
    Test the get_services method of DriveService.

    This test verifies that the method correctly creates and returns
    Drive and People services, and stores them in the Flask g object.
    """
    with app.app_context():
        with patch('app.services.google_drive.drive_service.build') as mock_build:
            mock_drive = Mock()
            mock_people = Mock()
            mock_build.side_effect = [mock_drive, mock_people]

            drive, people = drive_service.get_services()

            assert drive == mock_drive
            assert people == mock_people
            assert g.drive_service == mock_drive
            assert g.people_service == mock_people

def test_get_file_web_view_link(app, drive_service):
    """
    Test the get_file_web_view_link method of DriveService.

    This test verifies that the method correctly retrieves the web view link
    and MIME type for a given file ID.
    """
    with app.app_context():
        mock_drive = Mock()
        mock_drive.files().get().execute.return_value = {
            'webViewLink': 'https://example.com/view',
            'mimeType': 'application/pdf'
        }

        with patch.object(drive_service, 'get_services', return_value=(mock_drive, None)):
            web_view_link, mime_type = drive_service.get_file_web_view_link('file_id')

        assert web_view_link == 'https://example.com/view'
        assert mime_type == 'application/pdf'

def test_get_file_details(app, drive_service):
    """
    Test the get_file_details method of DriveService.

    This test ensures that the method correctly retrieves and formats
    the details of a specific file.
    """
    with app.app_context():
        mock_drive = Mock()
        mock_drive.files().get().execute.return_value = {
            'id': 'file_id',
            'name': 'test_file',
            'mimeType': 'application/pdf',
            'size': '1000',
            'hasThumbnail': True,
            'thumbnailLink': 'http://thumbnail.com',
            'modifiedTime': '2023-01-01T00:00:00.000Z',
            'createdTime': '2023-01-01T00:00:00.000Z',
            'viewedByMeTime': '2023-01-02T00:00:00.000Z',
            'sharedWithMeTime': '2023-01-03T00:00:00.000Z',
            'owners': [{'displayName': 'Owner'}],
            'parents': ['parent_id'],
            'shared': True
        }

        with patch.object(drive_service, 'get_services', return_value=(mock_drive, None)):
            file_details = drive_service.get_file_details('file_id')

        assert file_details['id'] == 'file_id'
        assert file_details['name'] == 'test_file'
        assert file_details['mimeType'] == 'application/pdf'
        assert file_details['size'] == '1000'
        assert file_details['hasThumbnail'] == True
        assert file_details['thumbnailLink'] == 'http://thumbnail.com'
        assert file_details['modifiedTime'] == '2023-01-01T00:00:00.000Z'
        assert file_details['createdTime'] == '2023-01-01T00:00:00.000Z'
        assert file_details['viewedByMeTime'] == '2023-01-02T00:00:00.000Z'
        assert file_details['sharedWithMeTime'] == '2023-01-03T00:00:00.000Z'
        assert file_details['owners'] == [{'displayName': 'Owner'}]
        assert file_details['parents'] == ['parent_id']
        assert file_details['shared'] == True

def test_cleanup_services(app, drive_service):
    """
    Test the cleanup_services method of DriveService.

    This test verifies that the method correctly removes and closes
    the Drive and People services stored in the Flask g object.
    """
    with app.app_context():
        mock_drive_service = Mock()
        mock_people_service = Mock()
        g.drive_service = mock_drive_service
        g.people_service = mock_people_service

        drive_service.cleanup_services()

        assert not hasattr(g, 'drive_service')
        assert not hasattr(g, 'people_service')
        mock_drive_service.close.assert_called_once()
        mock_people_service.close.assert_called_once()