"""
This module provides Flask routes for interacting with Google Drive.

It includes functionality for listing the contents of a specified folder
in Google Drive, handling pagination and various error scenarios.
"""

from flask import Blueprint, session, jsonify
from app.utils.drive_utils import get_drive_core

drive_core_bp = Blueprint('drive_core', __name__)

@drive_core_bp.route('/drive/list_folder_contents/<folder_id>')
def list_folder_contents(folder_id):
    """
    List the contents of a specified folder in Google Drive.

    This function retrieves all files and folders within the specified
    Google Drive folder, handling pagination if necessary. It returns
    the list of items, each containing id, name, and mimeType.

    Args:
        folder_id (str): The ID of the Google Drive folder to list.

    Returns:
        flask.Response: A JSON response containing an array of file/folder
        objects, each with 'id', 'name', and 'mimeType' fields.

    Raises:
        ValueError: If there's an issue with the user's session or credentials.
        Exception: For any other unexpected errors during the process.

    HTTP Status Codes:
        200: Successfully retrieved folder contents.
        401: Unauthorized access, usually due to invalid session.
        500: Internal server error for any other unexpected issues.
    """
    try:
        drive_core = get_drive_core(session)
        drive_service = drive_core.drive_service
        
        results = []
        page_token = None
        while True:
            response = drive_service.files().list(
                q=f"'{folder_id}' in parents",
                spaces='drive',
                fields='nextPageToken, files(id, name, mimeType)',
                pageToken=page_token,
                supportsAllDrives=True
            ).execute()
            results.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        
        return jsonify(results)
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500