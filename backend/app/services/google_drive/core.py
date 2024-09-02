"""
This module provides the DriveCore class for Google Drive operations.

It includes functionality to initialize Google Drive and People API services
and perform operations such as listing folder contents.
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class DriveCore:
    """
    A core class for Google Drive operations.

    This class initializes Google Drive and People API services and provides
    methods for interacting with Google Drive.
    """

    def __init__(self, credentials):
        """
        Initialize DriveCore with Google credentials.

        Args:
            credentials (dict or Credentials): The Google credentials to use.

        Raises:
            TypeError: If credentials are neither a dict nor a Credentials object.
            Exception: If there's an error building the services.
        """
        try:
            if isinstance(credentials, dict):
                self.credentials = Credentials(**credentials)
            elif isinstance(credentials, Credentials):
                self.credentials = credentials
            else:
                raise TypeError("credentials must be either a dict or a Credentials object")
            
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
            self.people_service = build('people', 'v1', credentials=self.credentials)
        except Exception as e:
            raise Exception(f"Error during DriveCore initialization: {str(e)}")

    def list_folder_contents(self, folder_id, page_token=None):
        """
        List the contents of a Google Drive folder.

        Args:
            folder_id (str): The ID of the folder to list.
            page_token (str, optional): Token for pagination. Defaults to None.

        Returns:
            list: A list of file metadata dictionaries.

        Raises:
            Exception: If there's an error calling the Drive API.
        """
        results = []
        try:
            while True:
                response = self.drive_service.files().list(
                    q=f"'{folder_id}' in parents",
                    spaces='drive',
                    fields='nextPageToken, files(id, name, mimeType)',
                    pageToken=page_token,
                    supportsAllDrives=True
                ).execute()
                
                files = response.get('files', [])
                results.extend(files)
                
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
            
            return results
        except Exception as e:
            raise Exception(f"Error listing folder contents: {str(e)}")