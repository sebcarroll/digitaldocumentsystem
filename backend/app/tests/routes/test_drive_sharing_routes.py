"""
This module contains unit tests for the drive_sharing_routes blueprint.

It includes tests for sharing items and updating general access settings
in Google Drive.
"""

import pytest
from flask import Flask, session
from unittest.mock import patch, MagicMock
from backend.app.routes.drive_sharing_routes import drive_sharing_bp

@pytest.fixture
def app():
    """
    Create and configure a new Flask app instance for each test.

    Returns:
        Flask: A Flask application instance with testing config and drive_sharing_bp registered.
    """
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.register_blueprint(drive_sharing_bp)
    return app

@pytest.fixture
def client(app):
    """
    Create a test client for the app.

    Args:
        app (Flask): The Flask application instance.

    Returns:
        FlaskClient: A test client for the Flask application.
    """
    return app.test_client()

@pytest.fixture
def mock_get_drive_core():
    """
    Mock the get_drive_core function.

    Yields:
        MagicMock: A mock object for the get_drive_core function.
    """
    with patch('backend.app.routes.drive_sharing_routes.get_drive_core') as mock:
        yield mock

@pytest.fixture
def mock_drive_sharing_service():
    """
    Mock the DriveSharingService class.

    Yields:
        MagicMock: A mock object for the DriveSharingService class.
    """
    with patch('backend.app.routes.drive_sharing_routes.DriveSharingService') as mock:
        yield mock

def test_share_item_success(client, mock_get_drive_core, mock_drive_sharing_service):
    """
    Test successful item sharing in Google Drive.

    This test mocks the drive service and checks if the endpoint correctly
    shares an item and returns the operation result.
    """
    mock_service = MagicMock()
    mock_service.share_item.return_value = {"success": True, "shared": 2}
    mock_drive_sharing_service.return_value = mock_service

    response = client.post('/drive/item123/share', 
                           json={'emails': ['user1@example.com', 'user2@example.com'], 'role': 'writer'})
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success'] is True
    assert json_data['shared'] == 2

def test_share_item_error(client, mock_get_drive_core, mock_drive_sharing_service):
    """
    Test error handling when sharing an item fails.

    This test ensures that the endpoint properly handles and reports
    errors returned by the sharing service.
    """
    mock_service = MagicMock()
    mock_service.share_item.return_value = {"error": "Invalid email"}
    mock_drive_sharing_service.return_value = mock_service

    response = client.post('/drive/item123/share', 
                           json={'emails': ['invalid_email'], 'role': 'writer'})
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['error'] == "Invalid email"

def test_update_general_access_success(client, mock_get_drive_core, mock_drive_sharing_service):
    """
    Test successful update of general access settings.

    This test mocks the drive service and checks if the endpoint correctly
    updates general access settings and returns the operation result.
    """
    mock_service = MagicMock()
    mock_service.update_general_access.return_value = {"success": True, "newAccess": "anyone"}
    mock_drive_sharing_service.return_value = mock_service

    response = client.post('/drive/item123/update-general-access', 
                           json={'access': 'anyone', 'linkRole': 'reader'})
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success'] is True
    assert json_data['newAccess'] == "anyone"

def test_update_general_access_error(client, mock_get_drive_core, mock_drive_sharing_service):
    """
    Test error handling when updating general access settings fails.

    This test ensures that the endpoint properly handles and reports
    errors returned by the sharing service.
    """
    mock_service = MagicMock()
    mock_service.update_general_access.return_value = ("Invalid access type", 400)
    mock_drive_sharing_service.return_value = mock_service

    response = client.post('/drive/item123/update-general-access', 
                           json={'access': 'invalid', 'linkRole': 'reader'})
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['error'] == "Invalid access type"

def test_share_item_value_error(client, mock_get_drive_core):
    """
    Test error handling for invalid session when sharing an item.

    This test ensures that the endpoint properly handles and reports
    a ValueError, which might occur due to an invalid session.
    """
    mock_get_drive_core.side_effect = ValueError("Invalid session")

    response = client.post('/drive/item123/share', 
                           json={'emails': ['user1@example.com'], 'role': 'writer'})
    
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['error'] == "Invalid session"

def test_update_general_access_value_error(client, mock_get_drive_core):
    """
    Test error handling for invalid session when updating general access.

    This test ensures that the endpoint properly handles and reports
    a ValueError, which might occur due to an invalid session.
    """
    mock_get_drive_core.side_effect = ValueError("Invalid session")

    response = client.post('/drive/item123/update-general-access', 
                           json={'access': 'anyone', 'linkRole': 'reader'})
    
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['error'] == "Invalid session"

def test_share_item_general_exception(client, mock_get_drive_core, mock_drive_sharing_service):
    """
    Test general error handling when sharing an item.

    This test ensures that the endpoint properly handles and reports
    unexpected exceptions that might occur during the process.
    """
    mock_service = MagicMock()
    mock_service.share_item.side_effect = Exception("Unexpected error")
    mock_drive_sharing_service.return_value = mock_service

    response = client.post('/drive/item123/share', 
                           json={'emails': ['user1@example.com'], 'role': 'writer'})
    
    assert response.status_code == 500
    json_data = response.get_json()
    assert "An error occurred: Unexpected error" in json_data['error']

def test_update_general_access_general_exception(client, mock_get_drive_core, mock_drive_sharing_service):
    """
    Test general error handling when updating general access.

    This test ensures that the endpoint properly handles and reports
    unexpected exceptions that might occur during the process.
    """
    mock_service = MagicMock()
    mock_service.update_general_access.side_effect = Exception("Unexpected error")
    mock_drive_sharing_service.return_value = mock_service

    response = client.post('/drive/item123/update-general-access', 
                           json={'access': 'anyone', 'linkRole': 'reader'})
    
    assert response.status_code == 500
    json_data = response.get_json()
    assert "An error occurred: Unexpected error" in json_data['error']

def test_share_item_missing_data(client, mock_get_drive_core, mock_drive_sharing_service):
    """
    Test sharing an item with missing data in the request.

    This test checks how the endpoint handles requests with missing data.
    """
    mock_service = MagicMock()
    mock_drive_sharing_service.return_value = mock_service

    response = client.post('/drive/item123/share', json={})
    
    assert response.status_code == 200  # This might be 400 if you add input validation
    mock_service.share_item.assert_called_with('item123', [], 'reader')

def test_update_general_access_missing_data(client, mock_get_drive_core, mock_drive_sharing_service):
    """
    Test updating general access with missing data in the request.

    This test checks how the endpoint handles requests with missing data.
    """
    mock_service = MagicMock()
    mock_drive_sharing_service.return_value = mock_service

    response = client.post('/drive/item123/update-general-access', json={})
    
    assert response.status_code == 500  # This should be 400 with proper input validation
    json_data = response.get_json()
    assert "An error occurred" in json_data['error']