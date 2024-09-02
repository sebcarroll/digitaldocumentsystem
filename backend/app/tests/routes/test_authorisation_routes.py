"""
Unit tests for the `authorisation_routes.py` module.

This module contains tests for various routes in the `authorisation_routes.py` module,
which handles user authentication through OAuth2 with Google. The tests cover
login, OAuth2 callback handling, authentication status checking, and logout.
These tests use `pytest` and mock external dependencies to isolate the logic being tested.
"""

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, session, json
from app.routes.authorisation_routes import auth_bp
from app.routes.authorisation_routes import redis_client

@pytest.fixture
def client():
    """Set up a Flask test client.

    This fixture creates and returns a Flask test client instance for use in the tests.
    It also registers the `auth_bp` blueprint with the Flask app.

    Returns:
        flask.testing.FlaskClient: A test client for the Flask app.
    """
    app = Flask(__name__)
    app.register_blueprint(auth_bp)
    app.config['SECRET_KEY'] = 'secret'
    return app.test_client()

@pytest.fixture
def init_session(client):
    """Initialize a session for the Flask test client.

    This fixture sets up a session with predefined user data to simulate
    an authenticated user.

    Yields:
        flask.testing.FlaskClient: The test client with an active session.
    """
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_user_id'
        sess['user_email'] = 'test_user_email@example.com'
    yield client

@patch('app.routes.authorisation_routes.auth_service.create_flow')
@patch('app.routes.authorisation_routes.auth_service.credentials_to_dict')
@patch('app.routes.authorisation_routes.auth_service.fetch_user_info')
@patch('app.routes.authorisation_routes.DriveCore')
@patch('app.routes.authorisation_routes.redis_client')
def test_oauth2callback_route_success(mock_redis, mock_drive_core, mock_fetch_user_info,
                                      mock_credentials_to_dict, mock_create_flow,
                                      client, init_session, capfd):
    """Test the successful flow of the OAuth2 callback route.

    This test simulates a successful OAuth2 callback, checking if the route
    correctly processes the callback, stores credentials, and redirects the user.

    Args:
        mock_redis (MagicMock): Mocked Redis client.
        mock_drive_core (MagicMock): Mocked DriveCore class.
        mock_fetch_user_info (MagicMock): Mocked fetch_user_info function.
        mock_credentials_to_dict (MagicMock): Mocked credentials_to_dict function.
        mock_create_flow (MagicMock): Mocked create_flow function.
        client (FlaskClient): Flask test client.
        init_session (FlaskClient): Flask test client with initialized session.
        capfd (pytest.fixture): Fixture to capture stdout/stderr output.
    """
    # Set up session state
    with client.session_transaction() as sess:
        sess['state'] = 'test_state'

    # Mock the OAuth2 flow and credentials
    mock_flow = MagicMock()
    mock_create_flow.return_value = mock_flow
    mock_credentials = MagicMock()
    mock_flow.fetch_token = MagicMock()
    mock_flow.credentials = mock_credentials
    mock_credentials_to_dict.return_value = {
        'token': 'mock_token',
        'refresh_token': 'mock_refresh_token',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_id': 'mock_client_id',
        'client_secret': 'mock_client_secret',
        'scopes': ['https://www.googleapis.com/auth/drive.readonly'],
        'expiry': '2023-08-10T12:00:00Z'
    }
    mock_fetch_user_info.return_value = {'id': 'test_user_id', 'email': 'test_user_email@example.com'}

    # Simulate the call to the callback URL
    response = client.get('/oauth2callback?state=test_state&code=test_code')

    # Capture the output
    captured = capfd.readouterr()
    print("Captured output:", captured.out)

    # Check if Redis `set` method was called
    expected_credentials = json.dumps(mock_credentials_to_dict.return_value)
    mock_redis.set.assert_called_with('user:test_user_id:token', expected_credentials)

    # Ensure the response is correct
    assert response.status_code == 302
    assert 'http://localhost:3000/auth-success' in response.headers['Location']

    # Verify session values are updated correctly
    with client.session_transaction() as sess:
        assert sess['user_email'] == 'test_user_email@example.com'
        assert sess['user_id'] == 'test_user_id'
        assert 'last_active' in sess

@patch('app.routes.authorisation_routes.auth_service.create_flow')
def test_login_route(mock_create_flow, client):
    """Test the `/login` route.

    This test verifies that the `/login` route correctly initiates the OAuth2 flow,
    redirects to the authorization URL, and stores the state and last active timestamp
    in the session.

    Args:
        mock_create_flow (MagicMock): Mocked `create_flow` method.
        client (FlaskClient): The test client instance.
    """
    mock_flow = MagicMock()
    mock_flow.authorization_url.return_value = ('https://auth_url', 'test_state')
    mock_create_flow.return_value = mock_flow

    response = client.get('/login')
    assert response.status_code == 302
    assert 'https://auth_url' in response.headers['Location']

    with client.session_transaction() as sess:
        assert 'state' in sess
        assert 'last_active' in sess

@patch('app.routes.authorisation_routes.auth_service.create_flow')
def test_oauth2callback_route_oauth_error(mock_create_flow, client):
    """Test the `/oauth2callback` route for an OAuth2 error.

    This test checks the route's behavior when the OAuth2 callback contains an error,
    ensuring that an appropriate error response is returned.

    Args:
        mock_create_flow (MagicMock): Mocked `create_flow` method.
        client (FlaskClient): The test client instance.
    """
    response = client.get('/oauth2callback?error=access_denied')
    assert response.status_code == 400
    assert response.json == {"error": "Authentication failed", "details": "access_denied"}
    
@patch('app.routes.authorisation_routes.DriveCore')
@patch('app.routes.authorisation_routes.redis_client')
def test_check_auth_route_authenticated(mock_redis, mock_drive_core, client, init_session):
    """Test the `/check-auth` route for an authenticated user.

    This test verifies that the route correctly identifies an authenticated user
    by attempting to retrieve the `DriveCore` instance, and that it updates the
    session's last active timestamp.

    Args:
        mock_redis (MagicMock): Mocked Redis client.
        mock_drive_core (MagicMock): Mocked `DriveCore` class.
        client (FlaskClient): The test client instance.
        init_session (FlaskClient): The test client with an active session.
    """
    mock_redis.get.return_value = json.dumps({'token': 'mock_token'})
    mock_drive_core.return_value = MagicMock()

    response = client.get('/check-auth')
    assert response.status_code == 200
    assert response.json == {"authenticated": True}

    with client.session_transaction() as sess:
        assert 'last_active' in sess

@patch('app.routes.authorisation_routes.DriveCore')
@patch('app.routes.authorisation_routes.redis_client')
def test_check_auth_route_not_authenticated(mock_redis, mock_drive_core, client, init_session):
    """Test the `/check-auth` route for a non-authenticated user.

    This test ensures that if the `DriveCore` retrieval fails, the user is considered
    not authenticated, and the response reflects this.

    Args:
        mock_redis (MagicMock): Mocked Redis client.
        mock_drive_core (MagicMock): Mocked `DriveCore` class.
        client (FlaskClient): The test client instance.
        init_session (FlaskClient): The test client with an active session.
    """
    mock_redis.get.return_value = None

    response = client.get('/check-auth')
    assert response.status_code == 200
    assert response.json == {"authenticated": False}

def test_logout_route(client, init_session):
    """Test the `/logout` route.

    This test verifies that the `/logout` route correctly clears the user's session
    and returns a successful logout message.

    Args:
        client (FlaskClient): The test client instance.
        init_session (FlaskClient): The test client with an active session.
    """
    response = client.get('/logout')
    assert response.status_code == 200
    assert response.json == {"message": "Logged out successfully"}

    with client.session_transaction() as sess:
        assert not sess