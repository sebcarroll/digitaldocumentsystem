from googleapiclient.http import MediaIoBaseUpload
import io
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import logging

logger = logging.getLogger(__name__)

class DriveFolderOperations:
    def __init__(self, drive_core):
        self.drive_core = drive_core
        self.drive_service = drive_core.drive_service

    def create_folder(self, parent_folder_id, folder_name):
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        folder = self.drive_service.files().create(body=file_metadata, fields='id').execute()
        return {"id": folder.get('id')}
    
    def upload_folder(self, parent_folder_id, files):
        uploaded_files = []
        folder_structure = {parent_folder_id: parent_folder_id} 

        def create_folder(name, parent_id):
            if (parent_id, name) in folder_structure:
                return folder_structure[(parent_id, name)]
            folder_metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            folder = self.drive_service.files().create(body=folder_metadata, fields='id').execute()
            folder_id = folder.get('id')
            folder_structure[(parent_id, name)] = folder_id
            return folder_id

        def upload_file(file, parent_id):
            file_metadata = {'name': os.path.basename(file.filename), 'parents': [parent_id]}
            media = MediaIoBaseUpload(io.BytesIO(file.read()),
                                      mimetype=file.content_type,
                                      resumable=True)
            file = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            return file.get('id')

        # First, create all necessary folders
        for file in files:
            path_parts = file.filename.split(os.path.sep)
            current_parent = parent_folder_id
            for part in path_parts[:-1]:
                current_parent = create_folder(part, current_parent)

        # Then, upload all files
        for file in files:
            path_parts = file.filename.split(os.path.sep)
            current_parent = parent_folder_id
            for part in path_parts[:-1]:
                current_parent = folder_structure[(current_parent, part)]
            file_id = upload_file(file, current_parent)
            uploaded_files.append({"name": file.filename, "id": file_id})

        return {"uploaded_files": uploaded_files}
    
    def fetch_folders(self, parent_id, page_token=None):
        try:
            results = self.drive_service.files().list(
                q=f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder'",
                spaces='drive',
                fields='nextPageToken, files(id, name, parents)',
                pageToken=page_token,
                pageSize=1000,
                supportsAllDrives=True
            ).execute()
            
            folders = results.get('files', [])
            next_page_token = results.get('nextPageToken')
            return {"folders": folders, "nextPageToken": next_page_token}
        except Exception as e:
            return {"error": str(e)}, 400

    def fetch_all_folders(self):
        """Fetch all folders from Google Drive."""
        try:
            results = []
            page_token = None
            while True:
                response = self.drive_service.files().list(
                    q="mimeType='application/vnd.google-apps.folder' and trashed=false",
                    spaces='drive',
                    fields='nextPageToken, files(id, name, parents)',
                    pageToken=page_token,
                    pageSize=1000,
                    supportsAllDrives=True
                ).execute()
                results.extend(response.get('files', []))
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
            return results
        except Exception as e:
            logger.error(f"Failed to fetch folders: {str(e)}")
            raise Exception(f"Failed to fetch folders: {str(e)}")

    def build_folder_tree(self):
        """Build a tree structure of all folders."""
        logger.info("Building folder tree")
        try:
            folders = self.fetch_all_folders()
            folder_dict = {folder['id']: folder for folder in folders}
            root_folders = []
            
            for folder in folders:
                folder['children'] = []
                parent_id = folder.get('parents', [None])[0]  # Get the first (and only) parent, or None if no parent
                if parent_id is None or parent_id not in folder_dict:
                    root_folders.append(folder)
                else:
                    parent = folder_dict[parent_id]
                    if 'children' not in parent:
                        parent['children'] = []
                    parent['children'].append(folder)
            
            logger.info(f"Built folder tree with {len(root_folders)} root folders")
            return root_folders
        except Exception as e:
            logger.error(f"Failed to build folder tree: {str(e)}")
            raise