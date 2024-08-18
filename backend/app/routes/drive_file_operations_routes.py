"""
This module provides Flask routes for Google Drive file operations.

It includes functionality for opening, uploading, creating, moving, deleting,
copying, and renaming files in Google Drive.
"""

from flask import Blueprint, request, jsonify, session
from app.services.google_drive.file_operations import DriveFileOperations
from app.utils.drive_utils import get_drive_core

drive_file_ops_bp = Blueprint('drive_file_ops', __name__)

@drive_file_ops_bp.route('/drive/<file_id>/open', methods=['GET'])
def open_file(file_id):
    """
    Open a file in Google Drive.

    Args:
        file_id (str): The ID of the file to open.

    Returns:
        flask.Response: A JSON response containing the file's web view link.

    Raises:
        ValueError: If there's an issue with the user's session or credentials.
        Exception: For any other unexpected errors during the process.
    """
    try:
        drive_core = get_drive_core()
        drive_ops = DriveFileOperations(drive_core)
        return jsonify(drive_ops.open_file(file_id))
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@drive_file_ops_bp.route('/drive/upload-file', methods=['POST'])
def upload_file():
    """
    Upload a file to Google Drive.

    Expects a multipart/form-data request with 'file' and optional 'folderId'.

    Returns:
        flask.Response: A JSON response containing the uploaded file's details.

    Raises:
        ValueError: If there's an issue with the user's session or credentials.
        Exception: For any other unexpected errors during the process.
    """
    try:
        drive_core = get_drive_core()
        drive_ops = DriveFileOperations(drive_core)
        file = request.files['file']
        folder_id = request.form.get('folderId', 'root')
        return jsonify(drive_ops.upload_file(file, folder_id))
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@drive_file_ops_bp.route('/drive/create-doc', methods=['POST'])
def create_doc():
    """
    Create a new Google Doc.

    Expects a JSON payload with optional 'folderId'.

    Returns:
        flask.Response: A JSON response containing the created document's details.

    Raises:
        ValueError: If there's an issue with the user's session or credentials.
        Exception: For any other unexpected errors during the process.
    """
    try:
        drive_core = get_drive_core()
        drive_ops = DriveFileOperations(drive_core)
        data = request.json
        folder_id = data.get('folderId', 'root')
        return jsonify(drive_ops.create_doc(folder_id))
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@drive_file_ops_bp.route('/drive/create-sheet', methods=['POST'])
def create_sheet():
    """
    Create a new Google Sheet.

    Expects a JSON payload with optional 'folderId'.

    Returns:
        flask.Response: A JSON response containing the created spreadsheet's details.

    Raises:
        ValueError: If there's an issue with the user's session or credentials.
        Exception: For any other unexpected errors during the process.
    """
    try:
        drive_core = get_drive_core()
        drive_ops = DriveFileOperations(drive_core)
        data = request.json
        folder_id = data.get('folderId', 'root')
        return jsonify(drive_ops.create_sheet(folder_id))
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@drive_file_ops_bp.route('/drive/move-files', methods=['POST'])
def move_files():
    """
    Move files to a new folder in Google Drive.

    Expects a JSON payload with 'fileIds' and 'newFolderId'.

    Returns:
        flask.Response: A JSON response containing the result of the move operation.

    Raises:
        ValueError: If there's an issue with the user's session or credentials.
        Exception: For any other unexpected errors during the process.
    """
    try:
        drive_core = get_drive_core()
        drive_ops = DriveFileOperations(drive_core)
        data = request.json
        return jsonify(drive_ops.move_files(data['fileIds'], data['newFolderId']))
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@drive_file_ops_bp.route('/drive/delete-files', methods=['POST'])
def delete_files():
    """
    Delete files from Google Drive.

    Expects a JSON payload with 'fileIds'.

    Returns:
        flask.Response: A JSON response containing the result of the delete operation.

    Raises:
        ValueError: If there's an issue with the user's session or credentials.
        Exception: For any other unexpected errors during the process.
    """
    try:
        drive_core = get_drive_core()
        drive_ops = DriveFileOperations(drive_core)
        data = request.json
        return jsonify(drive_ops.delete_files(data['fileIds']))
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@drive_file_ops_bp.route('/drive/copy-files', methods=['POST'])
def copy_files():
    """
    Copy files in Google Drive.

    Expects a JSON payload with 'fileIds'.

    Returns:
        flask.Response: A JSON response containing the result of the copy operation.

    Raises:
        ValueError: If there's an issue with the user's session or credentials.
        Exception: For any other unexpected errors during the process.
    """
    try:
        drive_core = get_drive_core()
        drive_ops = DriveFileOperations(drive_core)
        data = request.json
        return jsonify(drive_ops.copy_files(data['fileIds']))
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@drive_file_ops_bp.route('/drive/rename-file', methods=['POST'])
def rename_file():
    """
    Rename a file in Google Drive.

    Expects a JSON payload with 'fileId' and 'newName'.

    Returns:
        flask.Response: A JSON response containing the renamed file's details.

    Raises:
        ValueError: If there's an issue with the user's session or credentials.
        Exception: For any other unexpected errors during the process.
    """
    try:
        drive_core = get_drive_core()
        drive_ops = DriveFileOperations(drive_core)
        data = request.json
        return jsonify(drive_ops.rename_file(data['fileId'], data['newName']))
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500