"""
Authentication Blueprint for the application.

This module defines the routes and functions for handling user authentication,
including OAuth2 flow with Google, login, logout, and authentication status checking.
It uses Flask sessions for maintaining user state and interacts with various
services to manage user data and Google Drive operations.
"""

from flask import Blueprint, redirect, request, session, url_for, jsonify, current_app
from datetime import datetime, timezone
from oauthlib.oauth2.rfc6749.errors import OAuth2Error
from app.services.google_drive.auth_service import AuthService
from app.services.google_drive.core import DriveCore
from app.services.natural_language.file_extractor import FileExtractor
from app.services.natural_language.chat_service import ChatService
from app.utils.drive_utils import get_drive_core
from googleapiclient.errors import Error as GoogleApiError
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from config import Config
import requests
import redis
import json

redis_client = redis.StrictRedis.from_url(Config.REDIS_TOKEN_URL, decode_responses=True)

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService(Config)

@auth_bp.before_request
def before_request():
    """
    Perform actions before each request to the auth blueprint.

    This function ensures the session is marked as permanent and modified,
    and updates the last active timestamp for authenticated users.
    """
    session.permanent = True
    session.modified = True
    user_id = session.get('user_id')
    if user_id:
        session['last_active'] = datetime.now(timezone.utc).isoformat()

@auth_bp.route('/login')
def login():
    """
    Initiate the OAuth2 login flow.

    This function creates an OAuth2 flow, generates an authorisation URL,
    and redirects the user to the Google login page. It also stores
    the state token and last active timestamp in the session.

    Returns:
        werkzeug.wrappers.Response: A redirect response to the authorisation URL.
    """ 
    flow = auth_service.create_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    session['last_active'] = datetime.now(timezone.utc).isoformat()
    return redirect(authorization_url)

@auth_bp.route('/oauth2callback')
def oauth2callback():
    """
    Handle the OAuth2 callback from Google.

    This function processes the authorisation response from Google's OAuth2 service,
    retrieves user information, stores the credentials in Redis, and updates the session.
    It also initialises or updates the ChatService with Drive functionality.

    Returns:
        flask.Response: A redirect response to the auth success page on success,
                        or a JSON response with error details on failure.

    Raises:
        OAuth2Error: If an OAuth2-specific error occurs during the process.
        GoogleApiError: If an error occurs while interacting with Google APIs.
        Exception: For any other unexpected errors.
    """
    try:
        if 'error' in request.args:
            return jsonify({"error": "Authentication failed", "details": request.args.get('error')}), 400

        state = session.get('state')
        if not state:
            return jsonify({"error": "No state in session"}), 400

        flow = auth_service.create_flow(state)
        authorization_response = request.url.replace('http://', 'https://', 1)
        flow.fetch_token(authorization_response=authorization_response)

        credentials = flow.credentials
        credentials_dict = auth_service.credentials_to_dict(credentials)
        
        drive_core = DriveCore(credentials_dict)
        user_info = auth_service.fetch_user_info(drive_core)

        user_id = user_info.get('id')
        user_email = user_info.get('email')
        
        if not user_id:
            return jsonify({"error": "Failed to retrieve user ID"}), 500

        redis_client.set(f'user:{user_id}:token', json.dumps(credentials_dict))

        session['user_email'] = user_email
        session['user_id'] = user_id
        session['last_active'] = datetime.now(timezone.utc).isoformat()

        chat_service = current_app.extensions.get('chat_service')
        if chat_service:
            chat_service.drive_core = drive_core
            chat_service.file_extractor = FileExtractor(drive_core=drive_core)
        else:
            current_app.extensions['chat_service'] = ChatService(drive_core)

        return redirect('https://diganise.vercel.app/auth-success')

    except OAuth2Error as oe:
        return jsonify({"error": "OAuth2 error occurred", "details": str(oe)}), 400
    except RefreshError as re:
        return jsonify({"error": "Failed to refresh token", "details": str(re)}), 401
    except GoogleApiError as ge:
        return jsonify({"error": "Google API error occurred", "details": str(ge)}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@auth_bp.route('/check-auth')
def check_auth():
    """
    Check the authentication status of the current user.

    This function verifies if the user is authenticated by checking the session
    and attempting to retrieve the user's DriveCore instance. It updates the
    last active timestamp if the user is authenticated.

    Returns:
        flask.Response: A JSON response indicating the authentication status.
    """
    user_id = session.get('user_id')
    if user_id:
        try:
            credentials_dict = json.loads(redis_client.get(f'user:{user_id}:token'))
            drive_core = DriveCore(credentials_dict)
            if drive_core:
                session['last_active'] = datetime.now(timezone.utc).isoformat()
                return jsonify({"authenticated": True})
        except Exception as e:
            pass
    return jsonify({"authenticated": e})

@auth_bp.route('/refresh-token')
def refresh_token():
    """
    Refresh the user's OAuth2 token.

    This function attempts to refresh the user's OAuth2 token if it has expired.
    If successful, it updates the Redis store with the new credentials.

    Returns:
        flask.Response: A JSON response indicating the result of the refresh attempt.
    """
    user_id = session.get('user_id')
    if user_id:
        try:
            credentials_dict = json.loads(redis_client.get(f'user:{user_id}:token'))
            credentials = Credentials(**credentials_dict)
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                updated_credentials_dict = auth_service.credentials_to_dict(credentials)
                redis_client.set(f'user:{user_id}:token', json.dumps(updated_credentials_dict))
                return jsonify({"message": "Token refreshed successfully"})
        except Exception:
            pass
    return jsonify({"error": "Failed to refresh token"}), 401

@auth_bp.route('/logout')
def logout():
    """
    Log out the current user.

    This function revokes the user's OAuth2 token if it's valid,
    then clears the session and removes the token from Redis, effectively logging out the user.

    Returns:
        flask.Response: A JSON response confirming successful logout.
    """
    user_id = session.get('user_id')
    if user_id:
        try:
            credentials_dict = json.loads(redis_client.get(f'user:{user_id}:token'))
            credentials = Credentials(**credentials_dict)
            if credentials.valid:
                requests.post('https://oauth2.googleapis.com/revoke',
                              params={'token': credentials.token},
                              headers={'content-type': 'application/x-www-form-urlencoded'})
            redis_client.delete(f'user:{user_id}:token')
        except Exception:
            pass
    session.clear()
    return jsonify({"message": "Logged out successfully"})

@auth_bp.route('/user-info')
def get_user_info():
    """
    Retrieve user information for the authenticated user.

    This function fetches the user's email and name from their Google account.

    Returns:
        flask.Response: A JSON response containing the user's email and name,
                        or an error message if retrieval fails.
    """
    try:
        drive_core = get_drive_core(session)
        user_info = AuthService.fetch_user_info(drive_core)
        return jsonify({
            "email": user_info.get('email'),
            "name": user_info.get('name')
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception:
        return jsonify({"error": "Failed to fetch user information"}), 500