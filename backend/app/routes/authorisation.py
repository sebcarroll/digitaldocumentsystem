from flask import Blueprint, redirect, request, session, url_for, jsonify
from config import Config
from datetime import datetime
from oauthlib.oauth2.rfc6749.errors import OAuth2Error
from app.services.google_drive.auth_service import AuthService
from app.services.sync.sync_service import SyncService

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
    session['last_active'] = datetime.now().timestamp()
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
    session['credentials'] = credentials_dict
    
    # Fetch user info
    try:
        user_info = auth_service.fetch_user_info(credentials)
        session['user_email'] = user_info.get('email')
        session['user_id'] = user_info.get('id')
        print(f"DEBUG: User authenticated - Email: {session['user_email']}, ID: {session['user_id']}")
    except Exception as e:
        print(f"ERROR: Failed to fetch user info - {str(e)}")
        session['user_email'] = None
        session['user_id'] = None

    session['last_active'] = datetime.now().timestamp()
    
    # Perform sync
    sync_result = SyncService.sync_user_drive(session)
    print(f"DEBUG: Initial sync result - {sync_result}")

    return redirect('http://localhost:3000/auth-success')

@auth_bp.route('/check-auth')
def check_auth():
    if 'credentials' in session:
        session['last_active'] = datetime.now().timestamp()
        return jsonify({"authenticated": True})
    return jsonify({"authenticated": False})

@auth_bp.route('/logout')
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})