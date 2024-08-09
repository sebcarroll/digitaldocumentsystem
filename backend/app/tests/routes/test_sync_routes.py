import pytest
from flask import Flask, session
from unittest.mock import patch, MagicMock
from app.routes.sync_routes import sync_bp
from google.oauth2.credentials import Credentials

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.register_blueprint(sync_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_sync_drive_to_pinecone():
    with patch('app.routes.sync_routes.sync_drive_to_pinecone') as mock:
        yield mock

@pytest.fixture
def mock_user_service():
    with patch('app.routes.sync_routes.UserService') as mock:
        yield mock

@pytest.fixture
def mock_drive_pinecone_sync():
    with patch('app.routes.sync_routes.DrivePineconeSync') as mock:
        yield mock

def test_start_sync_session_success(client, mock_sync_drive_to_pinecone):
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_user_id'

    response = client.post('/sync/start_session')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Sync session started"
    mock_sync_drive_to_pinecone.delay.assert_called_once_with('test_user_id')

def test_end_sync_session_success(client, mock_sync_drive_to_pinecone):
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_user_id'

    response = client.post('/sync/end_session')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Sync session ended"
    mock_sync_drive_to_pinecone.delay.assert_called_once_with('test_user_id')

def test_sync_sessions_not_authenticated(client):
    endpoints = ['/sync/start_session', '/sync/end_session']
    
    for endpoint in endpoints:
        response = client.post(endpoint)
        
        assert response.status_code == 401
        json_data = response.get_json()
        assert json_data['error'] == "User not authenticated"

def test_handle_file_event_success(client, mock_user_service, mock_drive_pinecone_sync):
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
    response = client.post('/sync/file_event', json={
        'event_type': 'open',
        'file_id': 'test_file_id'
    })
    
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['error'] == "User not authenticated"

def test_handle_file_event_missing_data(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_user_id'

    response = client.post('/sync/file_event', json={})
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['error'] == "Missing event_type or file_id"

def test_handle_file_event_invalid_event_type(client, mock_user_service):
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