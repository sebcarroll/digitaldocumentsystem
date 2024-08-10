"""
This module provides Flask routes for Google Drive folder operations.

It includes functionality for creating folders, uploading folders,
and fetching folder information from Google Drive.
"""

from flask import Blueprint, request, jsonify, session
from app.services.google_drive.folder_operations import DriveFolderOperations
from app.utils.drive_utils import get_drive_core

drive_folder_ops_bp = Blueprint('drive_folder_ops', __name__)

@drive_folder_ops_bp.route('/drive/create-folder', methods=['POST'])
def create_folder():
    """
    Create a new folder in Google Drive.

    Expects a JSON payload with 'folderName' and optional 'parentFolderId'.

    Returns:
        flask.Response: A JSON response containing the created folder's details.

    Raises:
        ValueError: If there's an issue with the user's session or credentials.
        Exception: For any other unexpected errors during the process.
    """
    try:
        drive_core = get_drive_core(session)
        folder_ops = DriveFolderOperations(drive_core)
        data = request.json
        parent_folder_id = data.get('parentFolderId', 'root')
        folder_name = data.get('folderName')
        result = folder_ops.create_folder(parent_folder_id, folder_name)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@drive_folder_ops_bp.route('/drive/upload-folder', methods=['POST'])
def upload_folder():
    """
    Upload a folder to Google Drive.

    Expects a multipart/form-data request with 'files' and optional 'parentFolderId'.

    Returns:
        flask.Response: A JSON response containing the result of the folder upload operation.

    Raises:
        ValueError: If there's an issue with the user's session or credentials.
        Exception: For any other unexpected errors during the process.
    """
    try:
        drive_core = get_drive_core(session)
        folder_ops = DriveFolderOperations(drive_core)
        parent_folder_id = request.form.get('parentFolderId', 'root')
        files = request.files.getlist('files')
        result = folder_ops.upload_folder(parent_folder_id, files)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@drive_folder_ops_bp.route('/drive/folders', methods=['GET'])
def fetch_folders():
    """
    Fetch folders from Google Drive.

    Accepts an optional query parameter 'parent_id' to specify the parent folder.

    Returns:
        flask.Response: A JSON response containing the list of folders.

    Raises:
        ValueError: If there's an issue with the user's session or credentials.
        Exception: For any other unexpected errors during the process.
    """
    try:
        drive_core = get_drive_core(session)
        folder_ops = DriveFolderOperations(drive_core)
        parent_id = request.args.get('parent_id', 'root')
        result = folder_ops.fetch_folders(parent_id)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500