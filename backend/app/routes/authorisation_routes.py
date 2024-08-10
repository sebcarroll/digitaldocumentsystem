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
from app.services.sync.sync_service import SyncService
from app.services.google_drive.core import DriveCore
from app.services.user.user_service import UserService
from googleapiclient.errors import Error as GoogleApiError
import redis
from config import Config
import json

redis_client = redis.StrictRedis.from_url(Config.REDIS_TOKEN_URL, decode_responses=True)


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
    and initiates a drive sync for the user.

    Returns:
        flask.Response: A redirect response to the auth success page on success,
                        or a JSON response with error details on failure.

    Raises:
        OAuth2Error: If an OAuth2-specific error occurs during the process.
        GoogleApiError: If an error occurs while interacting with Google APIs.
        Exception: For any other unexpected errors.
    """
    try:
        print("Starting oauth2callback function")
        if 'error' in request.args:
            print(f"Error in request args: {request.args.get('error')}")
            return jsonify({"error": "Authentication failed", "details": request.args.get('error')}), 400

        state = session.get('state')
        if not state:
            print("No state in session")
            return jsonify({"error": "No state in session"}), 400

        print("Creating flow")
        flow = auth_service.create_flow(state)
        print("Fetching token")
        flow.fetch_token(authorization_response=request.url)

        print("Getting credentials")
        credentials = flow.credentials
        credentials_dict = auth_service.credentials_to_dict(credentials)
        print(f"Credentials dict: {credentials_dict}")
        
        print("Creating DriveCore")
        drive_core = DriveCore(credentials_dict)
        print("Fetching user info")
        user_info = auth_service.fetch_user_info(drive_core)
        print(f"User info: {user_info}")

        user_id = user_info.get('id')
        user_email = user_info.get('email')
        
        if user_id:
            print(f"Setting Redis key for user {user_id}")
            redis_client.set(f'user:{user_id}:token', json.dumps(credentials_dict))
        else:
            print("Warning: user_id is None, skipping Redis set operation")

        print("Updating session")
        session['user_email'] = user_email
        session['user_id'] = user_id
        session['last_active'] = datetime.now(timezone.utc).isoformat()

        print("Syncing user drive")
        SyncService.sync_user_drive(user_id)

        print("Redirecting to success page")
        return redirect('http://localhost:3000/auth-success')

    except OAuth2Error as oe:
        print(f"OAuth2 error: {str(oe)}")
        return jsonify({"error": "OAuth2 error occurred", "details": str(oe)}), 400

    except GoogleApiError as ge:
        print(f"Google API error: {str(ge)}")
        return jsonify({"error": "Google API error occurred", "details": str(ge)}), 500

    except Exception as e:
        print(f"Unexpected error in oauth2callback: {str(e)}")
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