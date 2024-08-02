from flask import Blueprint, redirect, session, url_for, jsonify, request, g
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

drive_bp = Blueprint('drive', __name__)

def get_drive_service():
    if 'drive_service' not in g or 'people_service' not in g:
        credentials = Credentials(**session['credentials'])
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            session['credentials'] = credentials_to_dict(credentials)
        g.drive_service = build('drive', 'v3', credentials=credentials, cache_discovery=False)
        g.people_service = build('people', 'v1', credentials=credentials, cache_discovery=False)
    return g.drive_service, g.people_service


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
    page_token = request.args.get('page_token')
    page_size = int(request.args.get('page_size', 100))  # Default to 100 items per page

    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    drive_service = get_drive_service()
    
    query = f"'{folder_id}' in parents and trashed = false"
    if folder_id == 'root':
        query = "trashed = false"

    try:
        files = drive_service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token,
            pageSize=page_size
        ).execute()

        items = files.get('files', [])
        next_page_token = files.get('nextPageToken')
        
        if not items:
            return jsonify({"message": "No files found in this folder."})
        else:
            file_list = [{"name": item['name'], "id": item['id'], "mimeType": item['mimeType']} for item in items]
            return jsonify({
                "files": file_list,
                "nextPageToken": next_page_token
            })

    except HttpError as error:
        return jsonify({"error": f"An error occurred: {error}"}), 500

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