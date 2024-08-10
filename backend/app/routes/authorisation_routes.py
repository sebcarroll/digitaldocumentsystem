from flask import Blueprint, redirect, request, session, url_for, jsonify
from config import Config
from datetime import datetime, timezone
from oauthlib.oauth2.rfc6749.errors import OAuth2Error
from app.services.google_drive.auth_service import AuthService
from app.services.sync.sync_service import SyncService
from app.services.google_drive.core import DriveCore
from app.services.user.user_service import UserService
import json

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService(Config)

@auth_bp.route('/login')
def login():
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
    state = session['state']
    flow = auth_service.create_flow(state)
    try:
        flow.fetch_token(authorization_response=request.url)
    except OAuth2Error as e:
        return jsonify({"error": "Authentication failed", "details": str(e)}), 400

    credentials = flow.credentials
    credentials_dict = auth_service.credentials_to_dict(credentials)
    
    # Fetch user info
    try:
        drive_core = DriveCore(credentials)
        user_info = auth_service.fetch_user_info(drive_core)
        user_id = user_info.get('id')
        user_email = user_info.get('email')
        
        # Save credentials to file
        with open(f'tokens/{user_id}.json', 'w') as token_file:
            json.dump(credentials_dict, token_file)
        
        session['user_email'] = user_email
        session['user_id'] = user_id
        print(f"DEBUG: User authenticated - Email: {user_email}, ID: {user_id}")
    except Exception as e:
        print(f"ERROR: Failed to fetch user info - {str(e)}")
        return jsonify({"error": "Failed to fetch user info", "details": str(e)}), 500

    session['last_active'] = datetime.now(timezone.utc).isoformat()
    
    # Perform sync
    sync_result = SyncService.sync_user_drive(user_id)
    print(f"DEBUG: Initial sync result - {sync_result}")

    return redirect('http://localhost:3000/auth-success')

@auth_bp.route('/check-auth')
def check_auth():
    user_id = session.get('user_id')
    if user_id:
        user_service = UserService()
        drive_core = user_service.get_drive_core(user_id)
        if drive_core:
            session['last_active'] = datetime.now(timezone.utc).isoformat()
            return jsonify({"authenticated": True})
    return jsonify({"authenticated": False})

@auth_bp.route('/logout')
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})