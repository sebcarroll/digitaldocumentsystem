from flask import Blueprint, redirect, session, url_for, jsonify
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

drive_bp = Blueprint('drive', __name__)

@drive_bp.route('/drive')
def drive():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    credentials = Credentials(**session['credentials'])
    drive_service = build('drive', 'v3', credentials=credentials)
    
    files = drive_service.files().list().execute()
    items = files.get('files', [])
    
    if not items:
        return jsonify({"message": "No files found in Google Drive."})
    else:
        file_list = [{"name": item['name'], "id": item['id']} for item in items]
        return jsonify({"files": file_list})