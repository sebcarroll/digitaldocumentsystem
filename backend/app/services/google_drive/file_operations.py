from .core import DriveCore
from googleapiclient.http import MediaIoBaseUpload
import io
import os

class DriveFileOperations(object):
    def __init__(self, drive_service):
        self.drive_service = drive_service
        
    def open_file(self, file_id):
        try:
            file = self.drive_service.files().get(fileId=file_id, fields='webViewLink').execute()
            return {"webViewLink": file.get('webViewLink')}
        except Exception as e:
            return {"error": str(e)}, 400

    def upload_file(self, file, parent_id):  # Fixed indentation
        try:
            file_metadata = {'name': os.path.basename(file.filename), 'parents': [parent_id]}
            media = MediaIoBaseUpload(io.BytesIO(file.read()),
                                      mimetype=file.content_type,
                                      resumable=True)
            file = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            return {"id": file.get('id')}  # Return a dictionary to match the test expectation
        except Exception as e:
            print(f"Error uploading file: {str(e)}")  # For debugging
            return {"error": str(e)}, 400

    
    def create_doc(self, folder_id):
        file_metadata = {
            'name': 'Untitled document',
            'mimeType': 'application/vnd.google-apps.document',
            'parents': [folder_id]
        }
        file = self.drive_service.files().create(body=file_metadata, fields='id, webViewLink').execute()
        return {
            "id": file.get('id'),
            "webViewLink": file.get('webViewLink')
        }

    def create_sheet(self, folder_id):
        file_metadata = {
            'name': 'Untitled spreadsheet',
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [folder_id]
        }
        file = self.drive_service.files().create(body=file_metadata, fields='id, webViewLink').execute()
        return {
            "id": file.get('id'),
            "webViewLink": file.get('webViewLink')
        }

    def move_files(self, file_ids, new_folder_id):
        moved_files = []
        errors = []

        for file_id in file_ids:
            try:
                file = self.drive_service.files().get(fileId=file_id, fields='parents').execute()
                previous_parents = ",".join(file.get('parents'))
                file = self.drive_service.files().update(
                    fileId=file_id,
                    addParents=new_folder_id,
                    removeParents=previous_parents,
                    fields='id, parents'
                ).execute()
                moved_files.append({"id": file.get('id'), "parents": file.get('parents')})
            except Exception as e:
                errors.append(f"Failed to move file {file_id}: {str(e)}")

        if errors:
            return {"error": "; ".join(errors), "moved_files": moved_files}, 400
        return {"message": "Files moved successfully", "moved_files": moved_files}

    def delete_files(self, file_ids):
        deleted_files = []
        errors = []

        for file_id in file_ids:
            try:
                self.drive_service.files().delete(fileId=file_id).execute()
                deleted_files.append(file_id)
            except Exception as e:
                errors.append(f"Failed to delete file {file_id}: {str(e)}")

        if errors:
            return {"error": "; ".join(errors), "deleted_files": deleted_files}, 400
        return {"message": "Files deleted successfully", "deleted_files": deleted_files}

    def copy_files(self, file_ids):
        copied_files = []
        errors = []

        for file_id in file_ids:
            try:
                copied_file = self.drive_service.files().copy(fileId=file_id, fields='id, name').execute()
                copied_files.append({"id": copied_file.get('id'), "name": copied_file.get('name')})
            except Exception as e:
                errors.append(f"Failed to copy file {file_id}: {str(e)}")

        if errors:
            return {"error": "; ".join(errors), "copied_files": copied_files}, 400
        return {"message": "Files copied successfully", "copied_files": copied_files}

    def rename_file(self, file_id, new_name):
        try:
            file = self.drive_service.files().update(
                fileId=file_id,
                body={'name': new_name},
                fields='id, name'
            ).execute()
            return {"id": file.get('id'), "name": file.get('name')}
        except Exception as e:
            return {"error": str(e)}, 400