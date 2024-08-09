from .core import DriveCore
from .file_operations import DriveFileOperations
from .folder_operations import DriveFolderOperations
from .drive_permissions_service import DrivePermissionsService
from .drive_sharing_service import DriveSharingService
from google.oauth2.credentials import Credentials
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GoogleDriveService:
    def __init__(self, credentials):
        if isinstance(credentials, dict):
            self.credentials = Credentials(**credentials)
        elif isinstance(credentials, Credentials):
            self.credentials = credentials
        else:
            raise TypeError("credentials must be either a dict or a Credentials object")
        
        self.drive_core = DriveCore(self.credentials)
        self.file_ops = DriveFileOperations(self.drive_core.drive_service)
        self.folder_ops = DriveFolderOperations(self.drive_core.drive_service)
        self.permissions_service = DrivePermissionsService(self.drive_core.drive_service)
        self.sharing_service = DriveSharingService(self.drive_core.drive_service)

    def get_file_metadata(self, file_id):
        return self.drive_core.drive_service.files().get(fileId=file_id, fields='*').execute()

    def get_file_content(self, file_id):
        file = self.get_file_metadata(file_id)
        mime_type = file['mimeType']

        if mime_type == 'application/vnd.google-apps.document':
            content = self.drive_core.drive_service.files().export(fileId=file_id, mimeType='text/plain').execute()
            return content.decode('utf-8')
        elif mime_type == 'application/vnd.google-apps.spreadsheet':
            content = self.drive_core.drive_service.files().export(fileId=file_id, mimeType='text/csv').execute()
            return content.decode('utf-8')
        else:
            # For binary files, you might want to handle differently
            content = self.drive_core.drive_service.files().get_media(fileId=file_id).execute()
            return content

    def list_changed_files(self, last_sync_time):
        query = f"modifiedTime > '{last_sync_time.isoformat()}Z'"
        results = []
        page_token = None
        while True:
            response = self.drive_core.drive_service.files().list(
                q=query,
                spaces='drive',
                fields='nextPageToken, files(id, name, mimeType, modifiedTime)',
                pageToken=page_token
            ).execute()
            results.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        return results

    def get_folder_metadata(self, folder_id):
        return self.drive_core.drive_service.files().get(fileId=folder_id, fields='*').execute()

    # Delegate methods to composed classes
    def open_file(self, file_id):
        return self.file_ops.open_file(file_id)

    def upload_file(self, file, parent_id):
        return self.file_ops.upload_file(file, parent_id)

    def create_doc(self, folder_id):
        return self.file_ops.create_doc(folder_id)

    def create_sheet(self, folder_id):
        return self.file_ops.create_sheet(folder_id)

    def move_files(self, file_ids, new_folder_id):
        return self.file_ops.move_files(file_ids, new_folder_id)

    def delete_files(self, file_ids):
        return self.file_ops.delete_files(file_ids)

    def copy_files(self, file_ids):
        return self.file_ops.copy_files(file_ids)

    def rename_file(self, file_id, new_name):
        return self.file_ops.rename_file(file_id, new_name)

    def create_folder(self, parent_folder_id, folder_name):
        return self.folder_ops.create_folder(parent_folder_id, folder_name)

    def upload_folder(self, parent_folder_id, files):
        return self.folder_ops.upload_folder(parent_folder_id, files)

    def fetch_folders(self, parent_id):
        return self.folder_ops.fetch_folders(parent_id)

    def get_people_with_access(self, item_id):
        return self.permissions_service.get_people_with_access(item_id)

    def update_permission(self, item_id, permission_id, new_role):
        return self.permissions_service.update_permission(item_id, permission_id, new_role)

    def remove_permission(self, item_id, permission_id):
        return self.permissions_service.remove_permission(item_id, permission_id)

    def share_item(self, item_id, emails, role):
        return self.sharing_service.share_item(item_id, emails, role)

    def update_general_access(self, item_id, new_access, link_role):
        return self.sharing_service.update_general_access(item_id, new_access, link_role)