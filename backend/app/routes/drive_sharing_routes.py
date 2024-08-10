"""
This module provides Flask routes for Google Drive sharing operations.

It includes functionality for sharing items and updating general access
settings for items in Google Drive.
"""

from flask import Blueprint, request, jsonify, session
from app.services.google_drive.drive_sharing_service import DriveSharingService
from app.utils.drive_utils import get_drive_core

drive_sharing_bp = Blueprint('drive_sharing', __name__)

@drive_sharing_bp.route('/drive/<item_id>/share', methods=['POST'])
def share_item(item_id):
    """
    Share a Google Drive item with specified users.

    Args:
        item_id (str): The ID of the item to be shared.

    Returns:
        flask.Response: A JSON response containing the result of the share operation.

    Raises:
        ValueError: If there's an issue with the user's session or credentials.
        Exception: For any other unexpected errors during the process.
    """
    try:
        drive_core = get_drive_core(session)
        service = DriveSharingService(drive_core)
        
        data = request.json
        if not data or 'emails' not in data or 'role' not in data:
            return jsonify({"error": "Missing required fields"}), 400
        
        emails = data.get('emails', [])
        role = data.get('role', 'reader')
        
        result = service.share_item(item_id, emails, role)
        
        if 'error' in result:
            return jsonify(result), 400
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@drive_sharing_bp.route('/drive/<item_id>/update-general-access', methods=['POST'])
def update_general_access(item_id):
    """
    Update the general access settings for a Google Drive item.

    Args:
        item_id (str): The ID of the item to update access for.

    Returns:
        flask.Response: A JSON response containing the result of the access update.

    Raises:
        ValueError: If there's an issue with the user's session or credentials.
        Exception: For any other unexpected errors during the process.
    """
    try:
        drive_core = get_drive_core(session)
        service = DriveSharingService(drive_core)
        
        data = request.json
        new_access = data.get('access')
        link_role = data.get('linkRole', 'reader')

        result = service.update_general_access(item_id, new_access, link_role)
        
        if isinstance(result, tuple):
            return jsonify({"error": result[0]}), result[1]
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500