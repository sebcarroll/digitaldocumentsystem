from flask import Blueprint, redirect, session, url_for, jsonify, request, g
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

drive_bp = Blueprint('drive', __name__)

def get_drive_service():
    if 'drive_service' not in g:
        credentials = Credentials(**session['credentials'])
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            session['credentials'] = credentials_to_dict(credentials)
        g.drive_service = build('drive', 'v3', credentials=credentials, cache_discovery=False)
    return g.drive_service

def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

@drive_bp.route('/drive')
def drive():
    folder_id = request.args.get('folder_id', 'root')
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    drive_service = get_drive_service()
    
    query = f"'{folder_id}' in parents" if folder_id != 'root' else None
    files = drive_service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    items = files.get('files', [])
    
    if not items:
        return jsonify({"message": "No files found in this folder."})
    else:
        file_list = [{"name": item['name'], "id": item['id'], "mimeType": item['mimeType']} for item in items]
        return jsonify({"files": file_list})

@drive_bp.route('/drive/<file_id>/open')
def open_file(file_id):
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    drive_service = get_drive_service()

    try:
        file = drive_service.files().get(fileId=file_id, fields="webViewLink,mimeType").execute()
        return jsonify({"webViewLink": file.get('webViewLink'), "mimeType": file.get('mimeType')})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@drive_bp.teardown_app_request
def cleanup_drive_service(exception=None):
    drive_service = g.pop('drive_service', None)
    if drive_service is not None:
        drive_service.close()

@drive_bp.route('/logout')
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})