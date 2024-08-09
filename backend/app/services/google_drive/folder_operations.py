from googleapiclient.http import MediaIoBaseUpload
import io
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class DriveFolderOperations:
    def __init__(self, credentials):
        if isinstance(credentials, dict):
            self.credentials = Credentials(**credentials)
        elif isinstance(credentials, Credentials):
            self.credentials = credentials
        else:
            raise TypeError("credentials must be either a dict or a Credentials object")
        
        self.drive_service = build('drive', 'v3', credentials=self.credentials)

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
    
    def fetch_folders(self, parent_id):
        try:
            results = self.drive_service.files().list(
                q=f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder'",
                spaces='drive',
                fields='files(id, name)',
                supportsAllDrives=True
            ).execute()
            
            folders = results.get('files', [])
            return {"folders": folders}
        except Exception as e:
            return {"error": str(e)}, 400