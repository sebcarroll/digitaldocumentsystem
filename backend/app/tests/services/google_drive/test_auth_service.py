import pytest
from unittest.mock import Mock, patch
from app.services.google_drive.auth_service import AuthService

@pytest.fixture
def mock_config():
    """Fixture to provide a mock configuration for testing."""
    config = Mock()
    config.GOOGLE_CLIENT_ID = 'test_client_id'
    config.GOOGLE_CLIENT_SECRET = 'test_client_secret'
    config.GOOGLE_REDIRECT_URI = 'http://localhost:5000/oauth2callback'
    config.SCOPES = ['test_scope']
    return config

@pytest.fixture
def auth_service(mock_config):
    """Fixture to provide an instance of AuthService initialized with mock_config."""
    return AuthService(mock_config)

def test_create_flow(app, auth_service):
    """
    Test the create_flow method of AuthService.
    
    This test ensures that the Flow is created with the correct client configuration
    and scopes, and that the redirect URI is correctly set.
    """
    with app.app_context():
        with patch('app.services.google_drive.auth_service.Flow.from_client_config') as mock_flow, \
             patch('app.services.google_drive.auth_service.url_for') as mock_url_for:
            mock_url_for.return_value = 'http://test.com/callback'
            auth_service.create_flow()

            mock_flow.assert_called_once()
            _, kwargs = mock_flow.call_args
            assert kwargs['client_config']['web']['client_id'] == 'test_client_id'
            assert kwargs['client_config']['web']['client_secret'] == 'test_client_secret'
            assert kwargs['scopes'] == ['test_scope']
            assert kwargs['redirect_uri'] == 'http://test.com/callback'

def test_fetch_user_info():
    """
    Test the fetch_user_info method of AuthService.
    
    This test ensures that user information is correctly fetched from the Google
    service using the provided credentials.
    """
    mock_credentials = Mock()
    mock_service = Mock()
    mock_userinfo = Mock()
    mock_service.userinfo.return_value.get.return_value.execute.return_value = {
        'email': 'test@example.com',
        'id': '12345'
    }

    with patch('app.services.google_drive.auth_service.build', return_value=mock_service):
        user_info = AuthService.fetch_user_info(mock_credentials)

    assert user_info == {'email': 'test@example.com', 'id': '12345'}

def test_credentials_to_dict():
    """
    Test the credentials_to_dict method of AuthService.
    
    This test verifies that the credentials are correctly converted to a dictionary.
    """
    mock_credentials = Mock()
    mock_credentials.token = 'test_token'
    mock_credentials.refresh_token = 'test_refresh_token'
    mock_credentials.token_uri = 'test_token_uri'
    mock_credentials.client_id = 'test_client_id'
    mock_credentials.client_secret = 'test_client_secret'
    mock_credentials.scopes = ['test_scope']

    credentials_dict = AuthService.credentials_to_dict(mock_credentials)

    assert credentials_dict == {
        'token': 'test_token',
        'refresh_token': 'test_refresh_token',
        'token_uri': 'test_token_uri',
        'client_id': 'test_client_id',
        'client_secret': 'test_client_secret',
        'scopes': ['test_scope']
    }