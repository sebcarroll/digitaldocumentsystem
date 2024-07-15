from flask import Blueprint, redirect, session, url_for, jsonify, request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

drive_bp = Blueprint('drive', __name__)

@drive_bp.route('/drive')
def drive():
    folder_id = request.args.get('folder_id', 'root')
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    credentials = Credentials(**session['credentials'])
    drive_service = build('drive', 'v3', credentials=credentials)
    
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

    credentials = Credentials(**session['credentials'])
    drive_service = build('drive', 'v3', credentials=credentials)

    try:
        file = drive_service.files().get(fileId=file_id, fields="webViewLink,mimeType").execute()
        return jsonify({"webViewLink": file.get('webViewLink'), "mimeType": file.get('mimeType')})
    except Exception as e:
        return jsonify({"error": str(e)}), 400