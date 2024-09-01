"""
This module defines routes for Google Drive access and management.

It includes functions for listing drive contents, opening files,
logging out, and cleaning up services after requests.
"""

from flask import Blueprint, session, jsonify, request, g
from app.utils.drive_utils import get_drive_core
from app.services.google_drive.drive_service import DriveService

drive_bp = Blueprint('drive', __name__)

@drive_bp.route('/drive')
def drive():
    """
    List the contents of a Google Drive folder.

    This function retrieves the contents of a specified Google Drive folder.
    It handles pagination and various error cases.

    Query Parameters:
    - folder_id: The ID of the folder to list (default is 'root').
    - page_token: Token for pagination.
    - page_size: Number of items to retrieve per page (default is 1000).

    Returns:
    - A JSON object containing the list of files and the next page token.
    - In case of errors, returns an appropriate error message and HTTP status code.
    """
    try:
        drive_core = get_drive_core(session)
        
        folder_id = request.args.get('folder_id', 'root')
        page_token = request.args.get('page_token')
        page_size = int(request.args.get('page_size', 1000))
        
        drive_service = DriveService(drive_core)
        file_list, next_page_token = drive_service.list_folder_contents(folder_id, page_token, page_size)
        
        if not file_list:
            return jsonify({"message": "No files found in this folder."})
        else:
            return jsonify({
                "files": file_list,
                "nextPageToken": next_page_token
            })
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as error:
        return jsonify({"error": f"An error occurred: {error}"}), 500

@drive_bp.route('/drive/<file_id>/open')
def open_file(file_id):
    """
    Retrieve the web view link and MIME type for a specific file.

    This function gets the web view link and MIME type for a file
    specified by its file ID. It handles various error cases and
    returns appropriate JSON responses.

    Args:
    - file_id: The ID of the file to open.

    Returns:
    - A JSON object containing the web view link and MIME type of the file.
    - In case of errors, returns an appropriate error message and HTTP status code.
    """
    try:
        drive_core = get_drive_core(session)
        drive_service = DriveService(drive_core)
        web_view_link, mime_type = drive_service.get_file_web_view_link(file_id)
        return jsonify({"webViewLink": web_view_link, "mimeType": mime_type})
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@drive_bp.route('/drive/<folder_id>/details')
def get_folder_details(folder_id):
    """
    Retrieve details for a specific folder in Google Drive.

    This route fetches and returns the details of a folder specified by its ID.
    It uses the DriveService to interact with the Google Drive API.

    Args:
        folder_id (str): The unique identifier of the folder in Google Drive.

    Returns:
        flask.Response: A JSON response containing the folder details.
        - If successful, returns a 200 status code with the folder details.
        - If the folder is not found, returns a 404 status code with an error message.
        - If an unexpected error occurs, returns a 500 status code with an error message.

    Raises:
        Exception: Any unexpected errors that occur during the process.
    """
    try:
        drive_core = get_drive_core(session)
        drive_service = DriveService(drive_core)
        folder_details = drive_service.get_file_details(folder_id)
        if folder_details:
            return jsonify(folder_details)
        else:
            return jsonify({"error": "Folder not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@drive_bp.teardown_app_request
def cleanup_services(exception=None):
    """
    Clean up services after each request.

    This function is called automatically after each request to the blueprint.
    It removes the 'drive_core' object from the Flask 'g' object if it exists.

    Args:
    - exception: An optional exception that occurred during the request.
    """
    if 'drive_core' in g:
        del g.drive_core

@drive_bp.route('/logout')
def logout():
    """
    Log out the current user.

    This function clears the session, effectively logging out the user.

    Returns:
    - A JSON object with a success message.
    """
    session.clear()
    return jsonify({"message": "Logged out successfully"})