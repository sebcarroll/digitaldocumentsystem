"""Module for handling Google Drive file operations."""

from googleapiclient.http import MediaIoBaseUpload
import io
import os

class DriveFileOperations:
    """Class for managing Google Drive file operations."""

    def __init__(self, drive_core):
        """
        Initialize DriveFileOperations.

        Args:
            drive_core: The DriveCore instance.
        """
        self.drive_core = drive_core
        self.drive_service = drive_core.drive_service

    def open_file(self, file_id):
        """
        Open a file in Google Drive.

        Args:
            file_id (str): The ID of the file to open.

        Returns:
            dict: A dictionary containing the web view link or an error message.
        """
        try:
            file = self.drive_service.files().get(fileId=file_id, fields='webViewLink').execute()
            return {"webViewLink": file.get('webViewLink')}
        except Exception as e:
            return {"error": str(e)}, 400

    def upload_file(self, file, parent_id):
        """
        Upload a file to Google Drive.

        Args:
            file: The file object to upload.
            parent_id (str): The ID of the parent folder.

        Returns:
            dict: A dictionary containing the uploaded file ID or an error message.
        """
        try:
            file_metadata = {'name': os.path.basename(file.filename), 'parents': [parent_id]}
            media = MediaIoBaseUpload(io.BytesIO(file.read()),
                                      mimetype=file.content_type,
                                      resumable=True)
            file = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            return {"id": file.get('id')} 
        except Exception as e:
            return {"error": str(e)}, 400

    def create_doc(self, folder_id):
        """
        Create a new Google Doc.

        Args:
            folder_id (str): The ID of the folder to create the document in.

        Returns:
            dict: A dictionary containing the new document's ID and web view link, or an error message.
        """
        try:
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
        except Exception as e:
            return {"error": str(e)}, 400

    def create_sheet(self, folder_id):
        """
        Create a new Google Sheet.

        Args:
            folder_id (str): The ID of the folder to create the spreadsheet in.

        Returns:
            dict: A dictionary containing the new spreadsheet's ID and web view link, or an error message.
        """
        try:
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
        except Exception as e:
            return {"error": str(e)}, 400

    def move_files(self, file_ids, new_folder_id):
        """
        Move files to a new folder.

        Args:
            file_ids (list): List of file IDs to move.
            new_folder_id (str): The ID of the destination folder.

        Returns:
            dict: A dictionary containing information about moved files or error messages.
        """
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
        """
        Delete files from Google Drive.

        Args:
            file_ids (list): List of file IDs to delete.

        Returns:
            dict: A dictionary containing information about deleted files or error messages.
        """
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
        """
        Copy files in Google Drive.

        Args:
            file_ids (list): List of file IDs to copy.

        Returns:
            dict: A dictionary containing information about copied files or error messages.
        """
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
        """
        Rename a file in Google Drive.

        Args:
            file_id (str): The ID of the file to rename.
            new_name (str): The new name for the file.

        Returns:
            dict: A dictionary containing the updated file information or an error message.
        """
        try:
            file = self.drive_service.files().update(
                fileId=file_id,
                body={'name': new_name},
                fields='id, name'
            ).execute()
            return {"id": file.get('id'), "name": file.get('name')}
        except Exception as e:
            return {"error": str(e)}, 400