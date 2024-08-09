from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


class DriveCore:
    def __init__(self, credentials):
        if isinstance(credentials, dict):
            credential_keys = ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret', 'scopes']
            filtered_credentials = {k: v for k, v in credentials.items() if k in credential_keys}
            self.credentials = Credentials(**filtered_credentials)
        elif isinstance(credentials, Credentials):
            self.credentials = credentials
        else:
            raise TypeError("credentials must be either a dict or a Credentials object")
        
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
        self.people_service = build('people', 'v1', credentials=self.credentials)

    def list_folder_contents(self, folder_id, page_token=None):
        results = []
        while True:
            response = self.drive_service.files().list(
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