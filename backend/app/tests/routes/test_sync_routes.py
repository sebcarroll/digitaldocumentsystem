"""
This module contains unit tests for the sync_routes blueprint.

It includes tests for starting and ending sync sessions, handling file events,
and various error scenarios.
"""

import pytest
from flask import Flask, session
from unittest.mock import patch, MagicMock
from app.routes.sync_routes import sync_bp
from google.oauth2.credentials import Credentials

@pytest.fixture
def app():
    """
    Create and configure a new Flask app instance for each test.

    Returns:
        Flask: A Flask application instance with testing config and sync_bp registered.
    """
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.register_blueprint(sync_bp)
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
def mock_sync_drive_to_pinecone():
    """
    Mock the sync_drive_to_pinecone function.

    Yields:
        MagicMock: A mock object for the sync_drive_to_pinecone function.
    """
    with patch('app.routes.sync_routes.sync_drive_to_pinecone') as mock:
        yield mock

@pytest.fixture
def mock_user_service():
    """
    Mock the UserService class.

    Yields:
        MagicMock: A mock object for the UserService class.
    """
    with patch('app.routes.sync_routes.UserService') as mock:
        yield mock

@pytest.fixture
def mock_drive_pinecone_sync():
    """
    Mock the DrivePineconeSync class.

    Yields:
        MagicMock: A mock object for the DrivePineconeSync class.
    """
    with patch('app.routes.sync_routes.DrivePineconeSync') as mock:
        yield mock

def test_start_sync_session_success(client, mock_sync_drive_to_pinecone):
    """
    Test successful start of a sync session.

    This test ensures that the start_sync_session endpoint correctly initiates
    a sync task when a user is authenticated.
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_user_id'

    response = client.post('/sync/start_session')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Sync session started"
    mock_sync_drive_to_pinecone.delay.assert_called_once_with('test_user_id')

def test_end_sync_session_success(client, mock_sync_drive_to_pinecone):
    """
    Test successful end of a sync session.

    This test ensures that the end_sync_session endpoint correctly initiates
    a sync task when a user is authenticated.
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_user_id'

    response = client.post('/sync/end_session')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Sync session ended"
    mock_sync_drive_to_pinecone.delay.assert_called_once_with('test_user_id')

def test_sync_sessions_not_authenticated(client):
    """
    Test authentication requirement for sync session endpoints.

    This test ensures that both start_sync_session and end_sync_session
    endpoints return a 401 error when a user is not authenticated.
    """
    endpoints = ['/sync/start_session', '/sync/end_session']
    
    for endpoint in endpoints:
        response = client.post(endpoint)
        
        assert response.status_code == 401
        json_data = response.get_json()
        assert json_data['error'] == "User not authenticated"

def test_handle_file_event_success(client, mock_user_service, mock_drive_pinecone_sync):
    """
    Test successful handling of file events.

    This test ensures that the handle_file_event endpoint correctly processes
    'open', 'close', and 'change' events for an authenticated user.
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_user_id'

    mock_user_service_instance = mock_user_service.return_value
    mock_user_service_instance.get_user.return_value = {'credentials': {}}

    mock_sync_service = mock_drive_pinecone_sync.return_value

    event_types = ['open', 'close', 'change']
    
    for event_type in event_types:
        response = client.post('/sync/file_event', json={
            'event_type': event_type,
            'file_id': 'test_file_id'
        })
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['message'] == "File event processed"

        if event_type == 'open':
            mock_sync_service.handle_file_open.assert_called_once_with('test_file_id')
        elif event_type == 'close':
            mock_sync_service.handle_file_close.assert_called_once_with('test_file_id')
        elif event_type == 'change':
            mock_sync_service.handle_file_change.assert_called_once_with('test_file_id')

def test_handle_file_event_not_authenticated(client):
    """
    Test authentication requirement for handle_file_event endpoint.

    This test ensures that the handle_file_event endpoint returns a 401 error
    when a user is not authenticated.
    """
    response = client.post('/sync/file_event', json={
        'event_type': 'open',
        'file_id': 'test_file_id'
    })
    
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['error'] == "User not authenticated"

def test_handle_file_event_missing_data(client):
    """
    Test error handling for missing data in handle_file_event.

    This test ensures that the handle_file_event endpoint returns a 400 error
    when required data (event_type or file_id) is missing.
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_user_id'

    response = client.post('/sync/file_event', json={})
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['error'] == "Missing event_type or file_id"

def test_handle_file_event_invalid_event_type(client, mock_user_service):
    """
    Test error handling for invalid event type in handle_file_event.

    This test ensures that the handle_file_event endpoint returns a 400 error
    when an invalid event_type is provided.
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_user_id'

    mock_user_service_instance = mock_user_service.return_value
    mock_user_service_instance.get_user.return_value = {'credentials': {}}

    response = client.post('/sync/file_event', json={
        'event_type': 'invalid',
        'file_id': 'test_file_id'
    })
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['error'] == "Invalid event_type"

@patch('app.routes.sync_routes.Credentials')
def test_handle_file_event_credentials(mock_credentials, client, mock_user_service, mock_drive_pinecone_sync):
    """
    Test credential handling in handle_file_event.

    This test ensures that the handle_file_event endpoint correctly processes
    user credentials when handling a file event.
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_user_id'

    mock_user_service_instance = mock_user_service.return_value
    mock_user_service_instance.get_user.return_value = {'credentials': {'token': 'test_token'}}

    response = client.post('/sync/file_event', json={
        'event_type': 'open',
        'file_id': 'test_file_id'
    })
    
    assert response.status_code == 200
    mock_credentials.from_authorized_user_info.assert_called_once_with({'token': 'test_token'})
    mock_drive_pinecone_sync.assert_called_once()