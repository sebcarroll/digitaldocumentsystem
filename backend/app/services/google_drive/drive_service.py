from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from flask import g

class DriveService:
    def __init__(self, session):
        self.session = session

    def get_services(self):
        if 'drive_service' not in g or 'people_service' not in g:
            credentials = Credentials(**self.session['credentials'])
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                self.session['credentials'] = self._credentials_to_dict(credentials)
            g.drive_service = build('drive', 'v3', credentials=credentials, cache_discovery=False)
            g.people_service = build('people', 'v1', credentials=credentials, cache_discovery=False)
        return g.drive_service, g.people_service

    @staticmethod
    def _credentials_to_dict(credentials):
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

    def list_folder_contents(self, folder_id, page_token=None, page_size=100):
        drive_service, _ = self.get_services()
        query = f"'{folder_id}' in parents and trashed = false"
        if folder_id == 'root':
            query = "trashed = false"

        files = drive_service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token,
            pageSize=page_size
        ).execute()

        items = files.get('files', [])
        next_page_token = files.get('nextPageToken')
        
        file_list = [{"name": item['name'], "id": item['id'], "mimeType": item['mimeType']} for item in items]
        return file_list, next_page_token

    def get_file_web_view_link(self, file_id):
        drive_service, _ = self.get_services()
        file = drive_service.files().get(fileId=file_id, fields="webViewLink,mimeType").execute()
        return file.get('webViewLink'), file.get('mimeType')

    def cleanup_services(self):
        drive_service = g.pop('drive_service', None)
        people_service = g.pop('people_service', None)
        if drive_service is not None:
            drive_service.close()
        if people_service is not None:
            people_service.close()