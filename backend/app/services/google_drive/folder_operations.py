from .core import DriveCore
from googleapiclient.http import MediaIoBaseUpload
import io
import os

class DriveFolderOperations(DriveCore):
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
        folder_structure = {}

        def upload_file(file, parent_id):
            file_metadata = {'name': os.path.basename(file.filename), 'parents': [parent_id]}
            media = MediaIoBaseUpload(io.BytesIO(file.read()),
                                    mimetype=file.content_type,
                                    resumable=True)
            file = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            return file.get('id')

        # Create folders first
        for file in files:
            path_parts = file.filename.split(os.path.sep)
            current_parent = parent_folder_id

            for i, part in enumerate(path_parts[:-1]):
                current_path = os.path.sep.join(path_parts[:i+1])
                if current_path not in folder_structure:
                    folder_id = self.create_folder(current_parent, part)['id']
                    folder_structure[current_path] = folder_id
                current_parent = folder_structure[current_path]

        # Then upload files
        for file in files:
            path_parts = file.filename.split(os.path.sep)
            current_path = os.path.sep.join(path_parts[:-1])
            current_parent = folder_structure.get(current_path, parent_folder_id)

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