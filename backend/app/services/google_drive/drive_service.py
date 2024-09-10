"""Module for managing Google Drive service operations."""

from google.auth.transport.requests import Request
from flask import g
from .core import DriveCore
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError

class DriveService:
    """Service for handling Google Drive operations."""

    def __init__(self, drive_core):
        """
        Initialize the DriveService.

        Args:
            drive_core (DriveCore): The DriveCore instance.
        """
        self.drive_core = drive_core

    def get_services(self):
        """
        Get or create Google Drive and People services.

        Returns:
            tuple: A tuple containing the Drive service and People service.
        """
        if 'drive_service' in g and 'people_service' in g:
            return g.drive_service, g.people_service

        if self.drive_core.credentials.expired and self.drive_core.credentials.refresh_token:
            try:
                self.drive_core.credentials.refresh(Request())
            except RefreshError as e:
                raise Exception(f"Error refreshing credentials: {str(e)}")

        g.drive_service = build('drive', 'v3', credentials=self.drive_core.credentials)
        g.people_service = build('people', 'v1', credentials=self.drive_core.credentials)

        return g.drive_service, g.people_service

    def list_folder_contents(self, folder_id, page_token=None, page_size=1000):
        """
        List contents of a Google Drive folder.

        Args:
            folder_id (str): ID of the folder to list.
            page_token (str, optional): Token for pagination.
            page_size (int, optional): Number of items per page.

        Returns:
            tuple: A tuple containing the list of files and the next page token.
        """
        drive_service, _ = self.get_services()
        query = f"'{folder_id}' in parents and trashed = false"
        if folder_id == 'root':
            query = "trashed = false"

        files = drive_service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType, size, hasThumbnail, thumbnailLink, modifiedTime, createdTime, viewedByMeTime, sharedWithMeTime, owners, parents, shared)",
            pageToken=page_token,
            pageSize=page_size,
            orderBy="modifiedTime desc"
        ).execute()

        items = files.get('files', [])
        next_page_token = files.get('nextPageToken')

        file_list = [{
            "name": item['name'],
            "id": item['id'],
            "mimeType": item['mimeType'],
            "size": item.get('size'),
            "hasThumbnail": item.get('hasThumbnail', False),
            "thumbnailLink": item.get('thumbnailLink'),
            "modifiedTime": item.get('modifiedTime'),
            "createdTime": item.get('createdTime'),
            "viewedByMeTime": item.get('viewedByMeTime'),
            "sharedWithMeTime": item.get('sharedWithMeTime'),
            "owners": item.get('owners', []),
            "parents": item.get('parents', []),
            "shared": item.get('shared', False)
        } for item in items]
        return file_list, next_page_token

    def get_file_web_view_link(self, file_id):
        """
        Get the web view link for a file.

        Args:
            file_id (str): ID of the file.

        Returns:
            tuple: A tuple containing the web view link and mime type.
        """
        drive_service, _ = self.get_services()
        try:
            file = drive_service.files().get(fileId=file_id, fields="webViewLink,mimeType").execute()
            return file.get('webViewLink'), file.get('mimeType')
        except Exception as e:
            raise Exception(f"Error getting file web view link: {str(e)}")
    
    def get_file_details(self, file_id):
        """
        Get details of a specific file.

        Args:
            file_id (str): ID of the file.

        Returns:
            dict: A dictionary containing file details.
        """
        drive_service, _ = self.get_services()
        try:
            file = drive_service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, size, hasThumbnail, thumbnailLink, modifiedTime, createdTime, viewedByMeTime, sharedWithMeTime, owners, parents, shared"
            ).execute()
            return {
                "id": file.get('id'),
                "name": file.get('name'),
                "mimeType": file.get('mimeType'),
                "size": file.get('size'),
                "hasThumbnail": file.get('hasThumbnail', False),
                "thumbnailLink": file.get('thumbnailLink'),
                "modifiedTime": file.get('modifiedTime'),
                "createdTime": file.get('createdTime'),
                "viewedByMeTime": file.get('viewedByMeTime'),
                "sharedWithMeTime": file.get('sharedWithMeTime'),
                "owners": file.get('owners', []),
                "parents": file.get('parents', []),
                "shared": file.get('shared', False)
            }
        except Exception as e:
            raise Exception(f"Error retrieving file details: {str(e)}")

    def cleanup_services(self):
        """Clean up and close Drive and People services."""
        drive_service = g.pop('drive_service', None)
        people_service = g.pop('people_service', None)
        if drive_service is not None:
            drive_service.close()
        if people_service is not None:
            people_service.close()