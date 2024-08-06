from flask import Blueprint, request, jsonify, session

from .drive_core import get_services, list_folder_contents

drive_sharing_bp = Blueprint('drive_sharing', __name__)

@drive_sharing_bp.route('/drive/<item_id>/share', methods=['POST'])
def share_item(item_id):
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    emails = data.get('emails', [])
    role = data.get('role', 'reader')
    
    drive_service, _ = get_services()
    
    shared_with = []
    errors = []

    for email in emails:
        try:
            permission = {
                'type': 'user',
                'role': role,
                'emailAddress': email
            }
            result = drive_service.permissions().create(
                fileId=item_id, 
                body=permission, 
                fields='id',
                supportsAllDrives=True
            ).execute()
            shared_with.append({"email": email, "permissionId": result.get('id')})
        except Exception as e:
            errors.append(f"Failed to share with {email}: {str(e)}")

    if errors:
        return jsonify({"error": "; ".join(errors), "shared_with": shared_with}), 400
    
    return jsonify({"message": "Item shared successfully", "shared_with": shared_with})


    
@drive_sharing_bp.route('/drive/<item_id>/update-general-access', methods=['POST'])
def update_general_access(item_id):
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    new_access = data.get('access')
    link_role = data.get('linkRole', 'reader')

    drive_service, _ = get_services()
    
    try:
        item = drive_service.files().get(fileId=item_id, fields='mimeType', supportsAllDrives=True).execute()
        is_folder = item['mimeType'] == 'application/vnd.google-apps.folder'

        if new_access == 'Anyone with the link':
            permission = {
                'type': 'anyone',
                'role': link_role,
                'allowFileDiscovery': False
            }
            drive_service.permissions().create(
                fileId=item_id, 
                body=permission,
                supportsAllDrives=True
            ).execute()
            
            if is_folder:
                apply_permission_recursively(drive_service, item_id, permission)

        elif new_access == 'Restricted':
            permissions = drive_service.permissions().list(fileId=item_id, supportsAllDrives=True).execute()
            for permission in permissions.get('permissions', []):
                if permission.get('type') == 'anyone':
                    drive_service.permissions().delete(
                        fileId=item_id, 
                        permissionId=permission['id'],
                        supportsAllDrives=True
                    ).execute()
            
            if is_folder:
                remove_anyone_permission_recursively(drive_service, item_id)
        
        return jsonify({"message": f"General access updated successfully for {'folder' if is_folder else 'file'}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def apply_permission_recursively(drive_service, folder_id, permission):
    items = list_folder_contents(drive_service, folder_id)
    for item in items:
        drive_service.permissions().create(
            fileId=item['id'], 
            body=permission, 
            supportsAllDrives=True
        ).execute()
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            apply_permission_recursively(drive_service, item['id'], permission)

def remove_anyone_permission_recursively(drive_service, folder_id):
    items = list_folder_contents(drive_service, folder_id)
    for item in items:
        permissions = drive_service.permissions().list(fileId=item['id'], supportsAllDrives=True).execute()
        for permission in permissions.get('permissions', []):
            if permission.get('type') == 'anyone':
                drive_service.permissions().delete(
                    fileId=item['id'], 
                    permissionId=permission['id'],
                    supportsAllDrives=True
                ).execute()
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            remove_anyone_permission_recursively(drive_service, item['id'])
