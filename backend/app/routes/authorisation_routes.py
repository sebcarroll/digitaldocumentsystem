"""
Authentication Blueprint for the application.

This module defines the routes and functions for handling user authentication,
including OAuth2 flow with Google, login, logout, and authentication status checking.
It uses Flask sessions for maintaining user state and interacts with various
services to manage user data and drive synchronization.
"""

from flask import Blueprint, redirect, request, session, url_for, jsonify
from datetime import datetime, timezone
from oauthlib.oauth2.rfc6749.errors import OAuth2Error
from app.services.google_drive.auth_service import AuthService
from app.services.sync.sync_service import SyncService, SyncError
from app.services.google_drive.core import DriveCore
from app.services.user.user_service import UserService
from googleapiclient.errors import Error as GoogleApiError
from google.auth.exceptions import RefreshError
import redis
from config import Config
import json
import logging

redis_client = redis.StrictRedis.from_url(Config.REDIS_TOKEN_URL, decode_responses=True)
logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService(Config)

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
    retrieves user information, stores the credentials in Redis, updates the session,
    and initiates a drive sync for the user as a background task.

    Returns:
        flask.Response: A redirect response to the auth success page on success,
                        or a JSON response with error details on failure.

    Raises:
        OAuth2Error: If an OAuth2-specific error occurs during the process.
        GoogleApiError: If an error occurs while interacting with Google APIs.
        SyncError: If there's an error initiating the sync process.
        Exception: For any other unexpected errors.
    """
    try:
        logger.info("Starting oauth2callback function")
        
        # Check for error in request args
        if 'error' in request.args:
            error_message = f"Error in request args: {request.args.get('error')}"
            logger.error(error_message)
            return jsonify({"error": "Authentication failed", "details": error_message}), 400

        # Verify state
        state = session.get('state')
        if not state:
            logger.error("No state in session")
            return jsonify({"error": "No state in session"}), 400

        # Create flow and fetch token
        logger.info("Creating flow and fetching token")
        flow = auth_service.create_flow(state)
        flow.fetch_token(authorization_response=request.url)

        # Get credentials
        logger.info("Getting credentials")
        credentials = flow.credentials
        credentials_dict = auth_service.credentials_to_dict(credentials)
        logger.debug(f"Credentials dict: {credentials_dict}")
        
        # Create DriveCore and fetch user info
        logger.info("Creating DriveCore and fetching user info")
        drive_core = DriveCore(credentials_dict)
        user_info = auth_service.fetch_user_info(drive_core)
        logger.debug(f"User info: {user_info}")

        user_id = user_info.get('id')
        user_email = user_info.get('email')
        
        if not user_id:
            logger.error("User ID not found in user info")
            return jsonify({"error": "Failed to retrieve user ID"}), 500

        # Store credentials in Redis
        logger.info(f"Setting Redis key for user {user_id}")
        redis_client.set(f'user:{user_id}:token', json.dumps(credentials_dict))

        # Update session
        logger.info("Updating session")
        session['user_email'] = user_email
        session['user_id'] = user_id
        session['last_active'] = datetime.now(timezone.utc).isoformat()

        # Start sync process in background
        logger.info("Initiating background sync process")
        try:
            SyncService.start_sync_if_not_in_progress(user_id)
            logger.info(f"Background sync initiated for user {user_id}")
        except SyncError as se:
            logger.error(f"Failed to start background sync for user {user_id}: {str(se)}")
            # Note: We're not returning an error here as auth was successful
            # The frontend can check sync status separately

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

    except SyncError as se:
        logger.error(f"Sync error: {str(se)}")
        return jsonify({"error": "Sync error occurred", "details": str(se)}), 500

    except Exception as e:
        logger.exception(f"Unexpected error in oauth2callback: {str(e)}")
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
        user_service = UserService()
        try:
            drive_core = user_service.get_drive_core(user_id)
            if drive_core:
                session['last_active'] = datetime.now(timezone.utc).isoformat()
                return jsonify({"authenticated": True})
        except Exception as e:
            print(f"Error getting drive core: {str(e)}")
    return jsonify({"authenticated": False})

@auth_bp.route('/logout')
def logout():
    """
    Log out the current user.

    This function clears the session, effectively logging out the user.

    Returns:
        flask.Response: A JSON response confirming successful logout.
    """
    session.clear()
    return jsonify({"message": "Logged out successfully"})

@auth_bp.route('/sync-status')
def sync_status():
    """
    Check the synchronization status for the current user.

    This function retrieves the current sync status for the authenticated user.
    It requires the user to be authenticated and returns the sync status if available.

    Returns:
        flask.Response: A JSON response containing the sync status or an error message.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    try:
        status = SyncService.get_sync_status(user_id)
        return jsonify({"status": status})
    except Exception as e:
        print(f"Error getting sync status for user {user_id}: {str(e)}")
        return jsonify({"error": "Failed to retrieve sync status"}), 500