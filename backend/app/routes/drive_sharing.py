from flask import Blueprint, request, jsonify, session
from app.services.google_drive.drive_sharing_service import DriveSharingService

drive_sharing_bp = Blueprint('drive_sharing', __name__)

@drive_sharing_bp.route('/drive/<item_id>/share', methods=['POST'])
def share_item(item_id):
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    emails = data.get('emails', [])
    role = data.get('role', 'reader')
    
    service = DriveSharingService(session)
    result = service.share_item(item_id, emails, role)
    
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)

@drive_sharing_bp.route('/drive/<item_id>/update-general-access', methods=['POST'])
def update_general_access(item_id):
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    new_access = data.get('access')
    link_role = data.get('linkRole', 'reader')

    service = DriveSharingService(session)
    result = service.update_general_access(item_id, new_access, link_role)
    
    if isinstance(result, tuple):
        return jsonify({"error": result[0]}), result[1]
    return jsonify(result)