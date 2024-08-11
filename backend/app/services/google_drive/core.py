"""
This module provides the DriveCore class for Google Drive operations.

It includes functionality to initialize Google Drive and People API services
and perform operations such as listing folder contents.
"""

import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set up logging
logger = logging.getLogger(__name__)

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
            HttpError: If there's an error building the services.
        """
        logger.debug("Initializing DriveCore")
        try:
            if isinstance(credentials, dict):
                self.credentials = Credentials(**credentials)
                logger.debug("Credentials initialized from dict")
            elif isinstance(credentials, Credentials):
                self.credentials = credentials
                logger.debug("Using provided Credentials object")
            else:
                logger.error(f"Invalid credentials type: {type(credentials)}")
                raise TypeError("credentials must be either a dict or a Credentials object")
            
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
            self.people_service = build('people', 'v1', credentials=self.credentials)
            logger.info("Drive and People services initialized successfully")
        except HttpError as e:
            logger.error(f"HTTP error occurred while building services: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during DriveCore initialization: {e}")
            raise

    def list_folder_contents(self, folder_id, page_token=None):
        """
        List the contents of a Google Drive folder.

        Args:
            folder_id (str): The ID of the folder to list.
            page_token (str, optional): Token for pagination. Defaults to None.

        Returns:
            list: A list of file metadata dictionaries.

        Raises:
            HttpError: If there's an error calling the Drive API.
        """
        logger.debug(f"Listing contents of folder: {folder_id}")
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
                logger.debug(f"Retrieved {len(files)} files")
                
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
            
            logger.info(f"Retrieved a total of {len(results)} files from folder {folder_id}")
            return results
        except HttpError as e:
            logger.error(f"HTTP error occurred while listing folder contents: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error while listing folder contents: {e}")
            raise