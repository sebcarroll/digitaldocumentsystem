"""
This module defines routes for Google Drive access and management.

It includes functions for listing drive contents, opening files,
logging out, and cleaning up services after requests.
"""

from flask import Blueprint, session, jsonify, request, g
from app.utils.drive_utils import get_drive_core
import logging

drive_bp = Blueprint('drive', __name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@drive_bp.route('/drive')
def drive():
    """
    List the contents of a Google Drive folder.

    This function retrieves the contents of a specified Google Drive folder.
    It handles pagination and various error cases.

    Query Parameters:
    - folder_id: The ID of the folder to list (default is 'root').
    - page_token: Token for pagination.
    - page_size: Number of items to retrieve per page (default is 100).

    Returns:
    - A JSON object containing the list of files and the next page token.
    - In case of errors, returns an appropriate error message and HTTP status code.
    """
    logger.info("Entering drive() function")
    try:
        logger.debug("Attempting to get drive_core")
        drive_core = get_drive_core(session)
        logger.debug("drive_core obtained successfully")
        
        folder_id = request.args.get('folder_id', 'root')
        page_token = request.args.get('page_token')
        page_size = int(request.args.get('page_size', 100))
        
        logger.info(f"Listing folder contents. Folder ID: {folder_id}, Page Token: {page_token}, Page Size: {page_size}")
        file_list = drive_core.list_folder_contents(folder_id, page_token)
        next_page_token = None  # Set this based on the result from list_folder_contents if implemented
        logger.debug(f"Received {len(file_list)} files")
        
        if not file_list:
            logger.info("No files found in the folder")
            return jsonify({"message": "No files found in this folder."})
        else:
            logger.info("Successfully retrieved file list")
            return jsonify({
                "files": file_list,
                "nextPageToken": next_page_token
            })
    except ValueError as e:
        logger.error(f"ValueError occurred: {str(e)}")
        return jsonify({"error": str(e)}), 401
    except Exception as error:
        logger.exception(f"Unexpected error occurred: {str(error)}")
        return jsonify({"error": f"An error occurred: {error}"}), 500
    finally:
        logger.info("Exiting drive() function")

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
    logger.info(f"Entering open_file() function for file ID: {file_id}")
    try:
        drive_core = get_drive_core(session)
        web_view_link, mime_type = drive_core.get_file_web_view_link(file_id)
        logger.info(f"Successfully retrieved web view link for file ID: {file_id}")
        return jsonify({"webViewLink": web_view_link, "mimeType": mime_type})
    except ValueError as e:
        logger.error(f"ValueError occurred: {str(e)}")
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 400
    finally:
        logger.info("Exiting open_file() function")

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
        logger.debug("Cleaning up drive_core from request context")
        del g.drive_core

@drive_bp.route('/logout')
def logout():
    """
    Log out the current user.

    This function clears the session, effectively logging out the user.

    Returns:
    - A JSON object with a success message.
    """
    logger.info("Logging out user")
    session.clear()
    logger.info("User logged out successfully")
    return jsonify({"message": "Logged out successfully"})