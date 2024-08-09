import pytest
from flask import Flask, session
from unittest.mock import patch, MagicMock
from app.routes.drive_permissions import drive_permissions_bp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.register_blueprint(drive_permissions_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_get_drive_permissions_service():
    with patch('app.routes.drive_permissions.get_drive_permissions_service') as mock:
        yield mock

def test_people_with_access_success(client, mock_get_drive_permissions_service):
    mock_service = MagicMock()
    mock_service.get_people_with_access.return_value = [
        {"email": "user1@example.com", "role": "writer"},
        {"email": "user2@example.com", "role": "reader"}
    ]
    mock_get_drive_permissions_service.return_value = mock_service

    response = client.get('/drive/item123/people-with-access')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data) == 2
    assert json_data[0]['email'] == "user1@example.com"
    assert json_data[1]['role'] == "reader"

def test_update_permission_success(client, mock_get_drive_permissions_service):
    mock_service = MagicMock()
    mock_service.update_permission.return_value = {"success": True}
    mock_get_drive_permissions_service.return_value = mock_service

    response = client.post('/drive/item123/update-permission', 
                           json={'permissionId': 'perm123', 'role': 'writer'})
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success'] is True

def test_remove_permission_success(client, mock_get_drive_permissions_service):
    mock_service = MagicMock()
    mock_service.remove_permission.return_value = {"success": True}
    mock_get_drive_permissions_service.return_value = mock_service

    response = client.post('/drive/item123/remove-permission', 
                           json={'permissionId': 'perm123'})
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success'] is True

def test_get_user_role_success(client, mock_get_drive_permissions_service):
    mock_service = MagicMock()
    mock_service.get_user_role.return_value = {"role": "owner"}
    mock_get_drive_permissions_service.return_value = mock_service

    response = client.get('/drive/item123/user-role')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['role'] == "owner"

def test_not_authenticated(client, mock_get_drive_permissions_service):
    mock_get_drive_permissions_service.return_value = None

    endpoints = [
        ('/drive/item123/people-with-access', 'GET'),
        ('/drive/item123/update-permission', 'POST'),
        ('/drive/item123/remove-permission', 'POST'),
        ('/drive/item123/user-role', 'GET')
    ]

    for endpoint, method in endpoints:
        if method == 'GET':
            response = client.get(endpoint)
        else:
            response = client.post(endpoint, json={})
        
        assert response.status_code == 401
        json_data = response.get_json()
        assert json_data['error'] == "Not authenticated"

def test_exception_handling(client, mock_get_drive_permissions_service):
    mock_service = MagicMock()
    mock_service.get_people_with_access.side_effect = Exception("Test error")
    mock_service.update_permission.side_effect = Exception("Test error")
    mock_service.remove_permission.side_effect = Exception("Test error")
    mock_service.get_user_role.side_effect = Exception("Test error")
    mock_get_drive_permissions_service.return_value = mock_service

    endpoints = [
        ('/drive/item123/people-with-access', 'GET'),
        ('/drive/item123/update-permission', 'POST'),
        ('/drive/item123/remove-permission', 'POST'),
        ('/drive/item123/user-role', 'GET')
    ]

    for endpoint, method in endpoints:
        if method == 'GET':
            response = client.get(endpoint)
        else:
            response = client.post(endpoint, json={})
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data['error'] == "Test error"

def test_update_permission_missing_data(client, mock_get_drive_permissions_service):
    mock_service = MagicMock()
    mock_get_drive_permissions_service.return_value = mock_service

    response = client.post('/drive/item123/update-permission', json={})
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data

def test_remove_permission_missing_data(client, mock_get_drive_permissions_service):
    mock_service = MagicMock()
    mock_get_drive_permissions_service.return_value = mock_service

    response = client.post('/drive/item123/remove-permission', json={})
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data