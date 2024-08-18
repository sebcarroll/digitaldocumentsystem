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
from googleapiclient.errors import Error as GoogleApiError
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from config import Config
import logging
import requests

logger = logging.getLogger(__name__)

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

    This function creates an OAuth2 flow, generates an authorization URL,
    and redirects the user to the Google login page. It also stores
    the state token and last active timestamp in the session.

    Returns:
        werkzeug.wrappers.Response: A redirect response to the authorization URL.
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

    This function processes the authorization response from Google's OAuth2 service,
    retrieves user information, stores the credentials in the session, and updates the session.
    It also initializes or updates the ChatService with Drive functionality.

    Returns:
        flask.Response: A redirect response to the auth success page on success,
                        or a JSON response with error details on failure.

    Raises:
        OAuth2Error: If an OAuth2-specific error occurs during the process.
        GoogleApiError: If an error occurs while interacting with Google APIs.
        Exception: For any other unexpected errors.
    """
    try:
        logger.info("Starting oauth2callback function")
        
        if 'error' in request.args:
            error_message = f"Error in request args: {request.args.get('error')}"
            logger.error(error_message)
            return jsonify({"error": "Authentication failed", "details": error_message}), 400

        state = session.get('state')
        if not state:
            logger.error("No state in session")
            return jsonify({"error": "No state in session"}), 400

        logger.info("Creating flow and fetching token")
        flow = auth_service.create_flow(state)
        flow.fetch_token(authorization_response=request.url)

        logger.info("Getting credentials")
        credentials = flow.credentials
        credentials_dict = auth_service.credentials_to_dict(credentials)
        logger.debug(f"Credentials dict: {credentials_dict}")
        
        logger.info("Creating DriveCore and fetching user info")
        drive_core = DriveCore(credentials_dict)
        user_info = auth_service.fetch_user_info(drive_core)
        logger.debug(f"User info: {user_info}")

        user_id = user_info.get('id')
        user_email = user_info.get('email')

        if not user_id:
            logger.error("User ID not found in user info")
            return jsonify({"error": "Failed to retrieve user ID"}), 500

        logger.info("Updating session")
        session.permanent = True
        session['user_email'] = user_email
        session['user_id'] = user_id
        session['credentials'] = credentials_dict
        session['last_active'] = datetime.now(timezone.utc).isoformat()
        session.modified = True

        logger.debug(f"Session after update: {session}")

        # Initialize or update ChatService with Drive functionality
        chat_service = current_app.extensions.get('chat_service')
        if chat_service:
            chat_service.drive_core = drive_core
            chat_service.file_extractor = FileExtractor(drive_core=drive_core)
            logger.info("Updated existing ChatService with Drive functionality")
        else:
            current_app.extensions['chat_service'] = ChatService(drive_core)
            logger.info("Created new ChatService with Drive functionality")

        logger.info("Redirecting to success page")
        return redirect('http://localhost:3000/auth-success')

    except OAuth2Error as oe:
        logger.error(f"OAuth2 error: {str(oe)}")
        return jsonify({"error": "OAuth2 error occurred", "details": str(oe)}), 400

    except RefreshError as re:
        logger.error(f"Token refresh error: {str(re)}")
        return jsonify({"error": "Failed to refresh token", "details": str(re)}), 401

    except GoogleApiError as ge:
        logger.error(f"Google API error: {str(ge)}")
        return jsonify({"error": "Google API error occurred", "details": str(ge)}), 500

    except Exception as e:
        logger.exception(f"Unexpected error in oauth2callback: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@auth_bp.route('/check-auth')
def check_auth():
    """
    Check the authentication status of the current user.

    This function verifies if the user is authenticated by checking the session
    for user_id and credentials. It validates the credentials and updates the
    last active timestamp if the user is authenticated.

    Returns:
        flask.Response: A JSON response indicating the authentication status.
    """
    user_id = session.get('user_id')
    credentials_dict = session.get('credentials')
    if user_id and credentials_dict:
        try:
            credentials = Credentials(**credentials_dict)
            if credentials and not credentials.expired:
                session['last_active'] = datetime.now(timezone.utc).isoformat()
                return jsonify({"authenticated": True})
            else:
                session.clear()
        except Exception as e:
            logger.error(f"Error validating credentials: {str(e)}")
    return jsonify({"authenticated": False})

@auth_bp.route('/refresh-token')
def refresh_token():
    """
    Refresh the user's OAuth2 token.

    This function attempts to refresh the user's OAuth2 token if it has expired.
    If successful, it updates the session with the new credentials.

    Returns:
        flask.Response: A JSON response indicating the result of the refresh attempt.
    """
    credentials_dict = session.get('credentials')
    if credentials_dict:
        try:
            credentials = Credentials(**credentials_dict)
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                session['credentials'] = auth_service.credentials_to_dict(credentials)
                session.modified = True
                return jsonify({"message": "Token refreshed successfully"})
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
    return jsonify({"error": "Failed to refresh token"}), 401

@auth_bp.route('/logout')
def logout():
    """
    Log out the current user.

    This function revokes the user's OAuth2 token if it's valid,
    then clears the session, effectively logging out the user.

    Returns:
        flask.Response: A JSON response confirming successful logout.
    """
    credentials_dict = session.get('credentials')
    if credentials_dict:
        try:
            credentials = Credentials(**credentials_dict)
            if credentials.valid:
                requests.post('https://oauth2.googleapis.com/revoke',
                              params={'token': credentials.token},
                              headers={'content-type': 'application/x-www-form-urlencoded'})
        except Exception as e:
            logger.error(f"Error revoking token: {str(e)}")
    session.clear()
    return jsonify({"message": "Logged out successfully"})