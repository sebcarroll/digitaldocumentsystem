"""
This module provides Flask routes for Google Drive permissions operations.

It includes functionality for retrieving, updating, and removing permissions,
as well as getting the user's role for a specific Drive item.
"""

from flask import Blueprint, request, jsonify, session
from app.services.google_drive.drive_permissions_service import DrivePermissionsService
from app.utils.drive_utils import get_drive_core

drive_permissions_bp = Blueprint('drive_permissions', __name__)

def get_drive_permissions_service():
    """
    Create and return a DrivePermissionsService instance.

    Returns:
        DrivePermissionsService or None: The service instance if authenticated, None otherwise.
    """
    try:
        drive_core = get_drive_core(session)
        return DrivePermissionsService(
            drive_core,
            session.get('user_email'),
            session.get('user_id')
        )
    except ValueError:
        return None

@drive_permissions_bp.route('/drive/<item_id>/people-with-access', methods=['GET'])
def people_with_access(item_id):
    """
    Get a list of people with access to a specific Drive item.

    Args:
        item_id (str): The ID of the Drive item.

    Returns:
        flask.Response: A JSON response with the list of people who have access.

    Raises:
        401: If the user is not authenticated.
        400: If there's an error retrieving the permissions.
    """
    service = get_drive_permissions_service()
    if not service:
        return jsonify({"error": "Not authenticated"}), 401

    try:
        result = service.get_people_with_access(item_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@drive_permissions_bp.route('/drive/<item_id>/update-permission', methods=['POST'])
def update_permission(item_id):
    """
    Update a permission for a specific Drive item.

    Args:
        item_id (str): The ID of the Drive item.

    Returns:
        flask.Response: A JSON response indicating the success of the operation.

    Raises:
        401: If the user is not authenticated.
        400: If there's an error updating the permission.
    """
    service = get_drive_permissions_service()
    if not service:
        return jsonify({"error": "Not authenticated"}), 401

    try:
        data = request.json
        permission_id = data.get('permissionId')
        new_role = data.get('role')
        result = service.update_permission(item_id, permission_id, new_role)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@drive_permissions_bp.route('/drive/<item_id>/remove-permission', methods=['POST'])
def remove_permission(item_id):
    """
    Remove a permission from a specific Drive item.

    Args:
        item_id (str): The ID of the Drive item.

    Returns:
        flask.Response: A JSON response indicating the success of the operation.

    Raises:
        401: If the user is not authenticated.
        400: If there's an error removing the permission.
    """
    service = get_drive_permissions_service()
    if not service:
        return jsonify({"error": "Not authenticated"}), 401

    try:
        data = request.json
        permission_id = data.get('permissionId')
        result = service.remove_permission(item_id, permission_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@drive_permissions_bp.route('/drive/<item_id>/user-role', methods=['GET'])
def get_user_role(item_id):
    """
    Get the user's role for a specific Drive item.

    Args:
        item_id (str): The ID of the Drive item.

    Returns:
        flask.Response: A JSON response with the user's role.

    Raises:
        401: If the user is not authenticated.
        400: If there's an error retrieving the user's role.
    """
    service = get_drive_permissions_service()
    if not service:
        return jsonify({"error": "Not authenticated"}), 401

    try:
        result = service.get_user_role(item_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400