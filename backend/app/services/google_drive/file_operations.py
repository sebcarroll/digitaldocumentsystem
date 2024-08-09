from googleapiclient.http import MediaIoBaseUpload
import io
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DriveFileOperations:
    def __init__(self, drive_core):
        self.drive_core = drive_core
        self.drive_service = drive_core.drive_service
        logger.info("DriveFileOperations initialized with DriveCore and drive_service.")


    def open_file(self, file_id):
        logger.info(f"Attempting to open file with ID: {file_id}")
        try:
            file = self.drive_service.files().get(fileId=file_id, fields='webViewLink').execute()
            logger.info(f"Successfully retrieved file with ID: {file_id}, WebViewLink: {file.get('webViewLink')}")
            return {"webViewLink": file.get('webViewLink')}
        except Exception as e:
            logger.error(f"Error opening file with ID {file_id}: {str(e)}")
            return {"error": str(e)}, 400

    def upload_file(self, file, parent_id):
        logger.info(f"Attempting to upload file {file.filename} to parent ID: {parent_id}")
        try:
            file_metadata = {'name': os.path.basename(file.filename), 'parents': [parent_id]}
            media = MediaIoBaseUpload(io.BytesIO(file.read()),
                                      mimetype=file.content_type,
                                      resumable=True)
            file = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            logger.info(f"File uploaded successfully with ID: {file.get('id')}")
            return {"id": file.get('id')} 
        except Exception as e:
            logger.error(f"Error uploading file {file.filename}: {str(e)}")
            return {"error": str(e)}, 400

    def create_doc(self, folder_id):
        logger.info(f"Attempting to create a new document in folder ID: {folder_id}")
        try:
            file_metadata = {
                'name': 'Untitled document',
                'mimeType': 'application/vnd.google-apps.document',
                'parents': [folder_id]
            }
            file = self.drive_service.files().create(body=file_metadata, fields='id, webViewLink').execute()
            logger.info(f"Document created successfully with ID: {file.get('id')}, WebViewLink: {file.get('webViewLink')}")
            return {
                "id": file.get('id'),
                "webViewLink": file.get('webViewLink')
            }
        except Exception as e:
            logger.error(f"Error creating document in folder ID {folder_id}: {str(e)}")
            return {"error": str(e)}, 400

    def create_sheet(self, folder_id):
        logger.info(f"Attempting to create a new spreadsheet in folder ID: {folder_id}")
        try:
            file_metadata = {
                'name': 'Untitled spreadsheet',
                'mimeType': 'application/vnd.google-apps.spreadsheet',
                'parents': [folder_id]
            }
            file = self.drive_service.files().create(body=file_metadata, fields='id, webViewLink').execute()
            logger.info(f"Spreadsheet created successfully with ID: {file.get('id')}, WebViewLink: {file.get('webViewLink')}")
            return {
                "id": file.get('id'),
                "webViewLink": file.get('webViewLink')
            }
        except Exception as e:
            logger.error(f"Error creating spreadsheet in folder ID {folder_id}: {str(e)}")
            return {"error": str(e)}, 400

    def move_files(self, file_ids, new_folder_id):
        logger.info(f"Attempting to move files to new folder ID: {new_folder_id}")
        moved_files = []
        errors = []

        for file_id in file_ids:
            logger.info(f"Moving file with ID: {file_id} to folder ID: {new_folder_id}")
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
                logger.info(f"File with ID: {file_id} moved successfully to folder ID: {new_folder_id}")
            except Exception as e:
                error_message = f"Failed to move file {file_id}: {str(e)}"
                logger.error(error_message)
                errors.append(error_message)

        if errors:
            return {"error": "; ".join(errors), "moved_files": moved_files}, 400
        return {"message": "Files moved successfully", "moved_files": moved_files}

    def delete_files(self, file_ids):
        logger.info(f"Attempting to delete files with IDs: {file_ids}")
        deleted_files = []
        errors = []

        for file_id in file_ids:
            logger.info(f"Deleting file with ID: {file_id}")
            try:
                self.drive_service.files().delete(fileId=file_id).execute()
                deleted_files.append(file_id)
                logger.info(f"File with ID: {file_id} deleted successfully")
            except Exception as e:
                error_message = f"Failed to delete file {file_id}: {str(e)}"
                logger.error(error_message)
                errors.append(error_message)

        if errors:
            return {"error": "; ".join(errors), "deleted_files": deleted_files}, 400
        return {"message": "Files deleted successfully", "deleted_files": deleted_files}

    def copy_files(self, file_ids):
        logger.info(f"Attempting to copy files with IDs: {file_ids}")
        copied_files = []
        errors = []

        for file_id in file_ids:
            logger.info(f"Copying file with ID: {file_id}")
            try:
                copied_file = self.drive_service.files().copy(fileId=file_id, fields='id, name').execute()
                copied_files.append({"id": copied_file.get('id'), "name": copied_file.get('name')})
                logger.info(f"File with ID: {file_id} copied successfully as {copied_file.get('name')}")
            except Exception as e:
                error_message = f"Failed to copy file {file_id}: {str(e)}"
                logger.error(error_message)
                errors.append(error_message)

        if errors:
            return {"error": "; ".join(errors), "copied_files": copied_files}, 400
        return {"message": "Files copied successfully", "copied_files": copied_files}

    def rename_file(self, file_id, new_name):
        logger.info(f"Attempting to rename file with ID: {file_id} to {new_name}")
        try:
            file = self.drive_service.files().update(
                fileId=file_id,
                body={'name': new_name},
                fields='id, name'
            ).execute()
            logger.info(f"File with ID: {file_id} renamed successfully to {file.get('name')}")
            return {"id": file.get('id'), "name": file.get('name')}
        except Exception as e:
            logger.error(f"Error renaming file with ID {file_id} to {new_name}: {str(e)}")
            return {"error": str(e)}, 400
