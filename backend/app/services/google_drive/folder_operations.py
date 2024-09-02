"""Module for handling Google Drive folder operations."""

from googleapiclient.http import MediaIoBaseUpload
import io
import os

class DriveFolderOperations:
    """Class for managing Google Drive folder operations."""

    def __init__(self, drive_core):
        """
        Initialize DriveFolderOperations.

        Args:
            drive_core: The DriveCore instance.
        """
        self.drive_core = drive_core
        self.drive_service = drive_core.drive_service

    def create_folder(self, parent_folder_id, folder_name):
        """
        Create a new folder in Google Drive.

        Args:
            parent_folder_id (str): The ID of the parent folder.
            folder_name (str): The name of the new folder.

        Returns:
            dict: A dictionary containing the ID of the created folder.
        """
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        folder = self.drive_service.files().create(body=file_metadata, fields='id').execute()
        return {"id": folder.get('id')}
    
    def upload_folder(self, parent_folder_id, files):
        """
        Upload a folder structure to Google Drive.

        Args:
            parent_folder_id (str): The ID of the parent folder.
            files (list): List of file objects to upload.

        Returns:
            dict: A dictionary containing information about uploaded files.
        """
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
        """
        Fetch folders from a specific parent folder.

        Args:
            parent_id (str): The ID of the parent folder.
            page_token (str, optional): Token for pagination.

        Returns:
            dict: A dictionary containing fetched folders and next page token.
        """
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
        """
        Fetch all folders from Google Drive.

        Returns:
            list: A list of all folders in the Drive.

        Raises:
            Exception: If fetching folders fails.
        """
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
            raise Exception(f"Failed to fetch folders: {str(e)}")

    def build_folder_tree(self):
        """
        Build a tree structure of all folders.

        Returns:
            list: A list of root folders with their hierarchical structure.

        Raises:
            Exception: If building the folder tree fails.
        """
        try:
            folders = self.fetch_all_folders()
            folder_dict = {folder['id']: folder for folder in folders}
            root_folders = []
            
            # First pass: identify the true root folder (My Drive)
            my_drive = next((folder for folder in folders if folder.get('parents') is None), None)
            if my_drive:
                root_folders.append(my_drive)
                folder_dict.pop(my_drive['id'], None)  # Remove My Drive from folder_dict

            # Second pass: build the tree
            for folder_id, folder in folder_dict.items():
                folder['children'] = []
                parent_id = folder.get('parents', [None])[0]
                if parent_id in folder_dict:
                    parent = folder_dict[parent_id]
                    if 'children' not in parent:
                        parent['children'] = []
                    parent['children'].append(folder)
                elif parent_id != my_drive['id']:
                    # If parent is not in folder_dict and not My Drive, it's a top-level folder
                    root_folders.append(folder)

            return root_folders
        except Exception as e:
            raise Exception(f"Failed to build folder tree: {str(e)}")