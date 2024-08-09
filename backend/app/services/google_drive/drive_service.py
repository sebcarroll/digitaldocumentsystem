from google.auth.transport.requests import Request
from flask import g
from .core import DriveCore
from googleapiclient.discovery import build
import logging

logger = logging.getLogger(__name__)

class DriveService:
    def __init__(self, drive_core):
        self.drive_core = drive_core

    def get_services(self):
        # Check if the services are already in the g context
        if 'drive_service' in g and 'people_service' in g:
            logger.info("Returning cached services from g context.")
            return g.drive_service, g.people_service

        if self.drive_core.credentials.expired and self.drive_core.credentials.refresh_token:
            logger.info("Refreshing credentials...")
            self.drive_core.credentials.refresh(Request())

        # Initialize the services
        logger.info("Initializing Google Drive and People services.")
        g.drive_service = build('drive', 'v3', credentials=self.drive_core.credentials)
        g.people_service = build('people', 'v1', credentials=self.drive_core.credentials)

        return g.drive_service, g.people_service

    def list_folder_contents(self, folder_id, page_token=None, page_size=100):
        drive_service, _ = self.get_services()
        query = f"'{folder_id}' in parents and trashed = false"
        if folder_id == 'root':
            query = "trashed = false"

        logger.info(f"Listing contents of folder: {folder_id}")
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
        logger.info(f"Retrieving web view link for file: {file_id}")
        file = drive_service.files().get(fileId=file_id, fields="webViewLink,mimeType").execute()
        return file.get('webViewLink'), file.get('mimeType')

    def cleanup_services(self):
        logger.info("Cleaning up services.")
        drive_service = g.pop('drive_service', None)
        people_service = g.pop('people_service', None)
        if drive_service is not None:
            drive_service.close()
        if people_service is not None:
            people_service.close()
