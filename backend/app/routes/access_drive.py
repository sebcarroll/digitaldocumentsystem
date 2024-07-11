from flask import Blueprint, redirect, session, url_for
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

drive_bp = Blueprint('drive', __name__)

@drive_bp.route('/drive')
def drive():
    if 'credentials' not in session:
        return redirect(url_for('auth.login'))
    
    credentials = Credentials(**session['credentials'])
    drive_service = build('drive', 'v3', credentials=credentials)
    
    files = drive_service.files().list().execute()
    items = files.get('files', [])
    
    if not items:
        return 'No files found in Google Drive.'
    else:
        output = 'Files in Google Drive:<br>'
        for item in items:
            output += f"{item['name']} ({item['id']})<br>"
        return output