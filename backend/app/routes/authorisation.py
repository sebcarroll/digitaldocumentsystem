from flask import Blueprint, redirect, request, session, url_for, jsonify
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from config import Config
from datetime import datetime
from oauthlib.oauth2.rfc6749.errors import OAuth2Error

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": Config.GOOGLE_CLIENT_ID,
                "client_secret": Config.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": [Config.GOOGLE_REDIRECT_URI]
            }
        },
        scopes=Config.SCOPES,
        redirect_uri=url_for('auth.oauth2callback', _external=True)
    )
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
    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": Config.GOOGLE_CLIENT_ID,
                "client_secret": Config.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": [Config.GOOGLE_REDIRECT_URI]
            }
        },
        scopes=Config.SCOPES,
        state=state,
        redirect_uri=url_for('auth.oauth2callback', _external=True)
    )
    try:
        flow.fetch_token(authorization_response=request.url)
    except OAuth2Error as e:
        return jsonify({"error": "Authentication failed", "details": str(e)}), 400

    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    # Fetch user info
    try:
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        session['user_email'] = user_info.get('email')
        session['user_id'] = user_info.get('id')
        print(f"DEBUG: User authenticated - Email: {session['user_email']}, ID: {session['user_id']}")
    except Exception as e:
        print(f"ERROR: Failed to fetch user info - {str(e)}")
        # Even if we fail to fetch user info, we don't want to block the authentication process
        # So we'll set these to None and continue
        session['user_email'] = None
        session['user_id'] = None

    session['last_active'] = datetime.now().timestamp()

    # Log the final scopes granted to the user
    print(f"DEBUG: Authentication successful. Granted scopes: {credentials.scopes}")

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
