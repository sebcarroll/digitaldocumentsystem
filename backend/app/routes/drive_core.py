from flask import Blueprint, session
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

drive_core_bp = Blueprint('drive_core', __name__)

def get_services():
    credentials = Credentials(**session['credentials'])
    drive_service = build('drive', 'v3', credentials=credentials)
    people_service = build('people', 'v1', credentials=credentials)
    return drive_service, people_service

def list_folder_contents(drive_service, folder_id, page_token=None):
    results = []
    while True:
        response = drive_service.files().list(
            q=f"'{folder_id}' in parents",
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType)',
            pageToken=page_token,
            supportsAllDrives=True
        ).execute()
        results.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return results