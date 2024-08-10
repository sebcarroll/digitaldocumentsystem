"""
Test suite for the Google OAuth authorisation routes.

This module contains tests for the various endpoints and functionalities
related to Google OAuth in the application.
"""

import pytest
from flask import Flask, session, url_for
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timezone
from oauthlib.oauth2.rfc6749.errors import OAuth2Error
from app.routes.authorisation_routes import auth_bp, AuthService, SyncService, UserService
from app.services.google_drive.core import DriveCore

@pytest.fixture
def app():
    """
    Create and configure a new Flask app instance for each test.

    Returns:
        Flask: A Flask application instance configured for testing.
    """
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.register_blueprint(auth_bp)
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

def test_login(client, app):
    """
    Test the login route.

    This test ensures that the login route correctly initializes the OAuth2 flow
    and sets the appropriate session variables.

    Args:
        client (FlaskClient): The test client for the Flask application.
        app (Flask): The Flask application instance.
    """
    with app.test_request_context():
        with patch.object(AuthService, 'create_flow') as mock_create_flow:
            mock_flow = MagicMock()
            mock_flow.authorization_url.return_value = ('https://example.com/auth', 'test_state')
            mock_create_flow.return_value = mock_flow

            response = client.get('/login')

            assert response.status_code == 302
            assert response.headers['Location'] == 'https://example.com/auth'
            assert session['state'] == 'test_state'
            assert 'last_active' in session

def test_oauth2callback_success(client, app):
    """
    Test the OAuth2 callback route for successful authentication.

    This test simulates a successful OAuth2 callback, ensuring that user information
    is correctly processed and stored, and that the appropriate redirect occurs.

    Args:
        client (FlaskClient): The test client for the Flask application.
        app (Flask): The Flask application instance.
    """
    with app.test_request_context():
        with patch.object(AuthService, 'create_flow') as mock_create_flow, \
             patch.object(AuthService, 'credentials_to_dict') as mock_credentials_to_dict, \
             patch.object(AuthService, 'fetch_user_info') as mock_fetch_user_info, \
             patch.object(SyncService, 'sync_user_drive') as mock_sync_user_drive, \
             patch('builtins.open', MagicMock()) as mock_open:

            mock_flow = MagicMock()
            mock_flow.fetch_token.return_value = None
            mock_flow.credentials = MagicMock()
            mock_create_flow.return_value = mock_flow

            mock_credentials_to_dict.return_value = {'token': 'test_token'}
            mock_fetch_user_info.return_value = {'id': 'test_id', 'email': 'test@example.com'}
            mock_sync_user_drive.return_value = 'Sync successful'

            with client.session_transaction() as sess:
                sess['state'] = 'test_state'

            response = client.get('/oauth2callback?code=test_code&state=test_state')

            assert response.status_code == 302
            assert response.headers['Location'] == 'http://localhost:3000/auth-success'
            assert session['user_email'] == 'test@example.com'
            assert session['user_id'] == 'test_id'
            assert 'last_active' in session
            mock_open.assert_called_once_with('tokens/test_id.json', 'w')

def test_oauth2callback_auth_error(client, app):
    """
    Test the OAuth2 callback route for authentication errors.

    This test simulates an authentication error during the OAuth2 callback,
    ensuring that the appropriate error response is returned.

    Args:
        client (FlaskClient): The test client for the Flask application.
        app (Flask): The Flask application instance.
    """
    with app.test_request_context():
        with patch.object(AuthService, 'create_flow') as mock_create_flow:
            mock_flow = MagicMock()
            mock_flow.fetch_token.side_effect = OAuth2Error('Auth failed')
            mock_create_flow.return_value = mock_flow

            with client.session_transaction() as sess:
                sess['state'] = 'test_state'

            response = client.get('/oauth2callback?error=access_denied')

            assert response.status_code == 400
            json_data = response.get_json()
            assert json_data['error'] == 'Authentication failed'

def test_oauth2callback_user_info_error(client, app):
    """
    Test the OAuth2 callback route for user info fetch errors.

    This test simulates an error occurring while fetching user information
    after successful authentication, ensuring that the appropriate error
    response is returned.

    Args:
        client (FlaskClient): The test client for the Flask application.
        app (Flask): The Flask application instance.
    """
    with app.test_request_context():
        with patch.object(AuthService, 'create_flow') as mock_create_flow, \
             patch.object(AuthService, 'fetch_user_info') as mock_fetch_user_info:

            mock_flow = MagicMock()
            mock_flow.fetch_token.return_value = None
            mock_flow.credentials = MagicMock()
            mock_create_flow.return_value = mock_flow

            mock_fetch_user_info.side_effect = Exception('User info fetch failed')

            with client.session_transaction() as sess:
                sess['state'] = 'test_state'

            response = client.get('/oauth2callback?code=test_code&state=test_state')

            assert response.status_code == 500
            json_data = response.get_json()
            assert json_data['error'] == 'Failed to fetch user info'

def test_check_auth_authenticated(client, app):
    """
    Test the check_auth route for an authenticated user.

    This test ensures that the check_auth route correctly identifies
    an authenticated user and returns the appropriate response.

    Args:
        client (FlaskClient): The test client for the Flask application.
        app (Flask): The Flask application instance.
    """
    with app.test_request_context():
        with patch.object(UserService, 'get_drive_core') as mock_get_drive_core:
            mock_get_drive_core.return_value = MagicMock()

            with client.session_transaction() as sess:
                sess['user_id'] = 'test_user_id'

            response = client.get('/check-auth')

            assert response.status_code == 200
            json_data = response.get_json()
            assert json_data['authenticated'] is True
            assert 'last_active' in session

def test_check_auth_not_authenticated(client, app):
    """
    Test the check_auth route for a non-authenticated user.

    This test ensures that the check_auth route correctly identifies
    a non-authenticated user and returns the appropriate response.

    Args:
        client (FlaskClient): The test client for the Flask application.
        app (Flask): The Flask application instance.
    """
    with app.test_request_context():
        response = client.get('/check-auth')

        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['authenticated'] is False

def test_logout(client, app):
    """
    Test the logout route.

    This test ensures that the logout route correctly clears the session
    and returns the appropriate response.

    Args:
        client (FlaskClient): The test client for the Flask application.
        app (Flask): The Flask application instance.
    """
    with app.test_request_context():
        with client.session_transaction() as sess:
            sess['user_id'] = 'test_user_id'
            sess['user_email'] = 'test@example.com'

        response = client.get('/logout')

        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['message'] == 'Logged out successfully'
        
        with client.session_transaction() as sess:
            assert 'user_id' not in sess
            assert 'user_email' not in sess