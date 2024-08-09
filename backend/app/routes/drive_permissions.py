from flask import Blueprint, request, jsonify, session
from app.services.google_drive.drive_permissions_service import DrivePermissionsService

drive_permissions_bp = Blueprint('drive_permissions', __name__)

def get_drive_permissions_service():
    if 'credentials' not in session:
        return None
    return DrivePermissionsService(
        session['credentials'],
        session.get('user_email'),
        session.get('user_id')
    )
@drive_permissions_bp.route('/drive/<item_id>/people-with-access', methods=['GET'])
def people_with_access(item_id):
    service = get_drive_permissions_service()
    if not service:
        return jsonify({"error": "Not authenticated"}), 401

    result = service.get_people_with_access(item_id)
    
    if isinstance(result, tuple):
        return jsonify({"error": result[0]}), result[1]
    return jsonify(result)

@drive_permissions_bp.route('/drive/<item_id>/update-permission', methods=['POST'])
def update_permission(item_id):
    service = get_drive_permissions_service()
    if not service:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    permission_id = data.get('permissionId')
    new_role = data.get('role')
    
    result = service.update_permission(item_id, permission_id, new_role)
    
    if isinstance(result, tuple):
        return jsonify({"error": result[0]}), result[1]
    return jsonify(result)

@drive_permissions_bp.route('/drive/<item_id>/remove-permission', methods=['POST'])
def remove_permission(item_id):
    service = get_drive_permissions_service()
    if not service:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    permission_id = data.get('permissionId')
    
    result = service.remove_permission(item_id, permission_id)
    
    if isinstance(result, tuple):
        return jsonify({"error": result[0]}), result[1]
    return jsonify(result)

@drive_permissions_bp.route('/drive/<item_id>/user-role', methods=['GET'])
def get_user_role(item_id):
    service = get_drive_permissions_service()
    if not service:
        return jsonify({"error": "Not authenticated"}), 401

    result = service.get_user_role(item_id)
    
    if isinstance(result, tuple):
        return jsonify({"error": result[0]}), result[1]
    return jsonify(result)