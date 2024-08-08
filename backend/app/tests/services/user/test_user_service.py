import pytest
from unittest.mock import patch, mock_open
from app.services.user.user_service import UserService
from google.oauth2.credentials import Credentials

@pytest.fixture
def mock_credentials():
    return {
        'token': 'fake_token',
        'refresh_token': 'fake_refresh_token',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_id': 'fake_client_id',
        'client_secret': 'fake_client_secret',
        'scopes': ['https://www.googleapis.com/auth/drive']
    }

@patch('app.services.user.user_service.Credentials.from_authorized_user_file')
@patch('app.services.user.user_service.build')
def test_get_user(mock_build, mock_credentials):
    mock_credentials.return_value = Credentials(token='fake_token')
    mock_service = mock_build.return_value
    mock_service.userinfo().get().execute.return_value = {
        'email': 'test@example.com',
        'name': 'Test User'
    }

    user = UserService.get_user('test_user_id')

    assert user['id'] == 'test_user_id'
    assert user['email'] == 'test@example.com'
    assert user['name'] == 'Test User'
    assert 'credentials' in user

@patch('app.services.user.user_service.Credentials.from_authorized_user_file')
@patch('builtins.open', new_callable=mock_open)
def test_update_last_sync_time(mock_file, mock_credentials):
    mock_credentials.return_value = Credentials(token='fake_token')
    
    UserService.update_last_sync_time('test_user_id', '2023-01-01T00:00:00')

    mock_file.assert_called_once_with('tokens/test_user_id.json', 'w')
    mock_file().write.assert_called_once()