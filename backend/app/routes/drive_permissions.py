from flask import Blueprint, request, jsonify, session
from .drive_core import get_services, list_folder_contents

drive_permissions_bp = Blueprint('drive_permissions', __name__)

@drive_permissions_bp.route('/drive/<item_id>/people-with-access', methods=['GET'])
def people_with_access(item_id):
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    drive_service, _ = get_services()
    user_email = session.get('user_email')
    user_id = session.get('user_id')

    print(f"Debug - User Email: {user_email}, User ID: {user_id}")  # Add this line
    
    try:
        # Get file metadata to check if the current user is an owner
        file = drive_service.files().get(fileId=item_id, fields='owners', supportsAllDrives=True).execute()
        
        # List permissions
        permissions = []
        page_token = None
        while True:
            response = drive_service.permissions().list(
                fileId=item_id,
                fields='permissions(id,emailAddress,role,displayName,photoLink,type),nextPageToken',
                pageSize=100,
                supportsAllDrives=True,
                pageToken=page_token
            ).execute()
            
            permissions.extend(response.get('permissions', []))
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        
        current_user_role = "viewer"
        current_user_id = None
        
        # Check if the user is an owner
        if user_email in [owner.get('emailAddress') for owner in file.get('owners', [])]:
            current_user_role = "owner"
            current_user_id = user_id
        else:
            # Find the user's permission in the list
            for permission in permissions:
                if permission.get('emailAddress') == user_email:
                    current_user_role = permission['role']
                    current_user_id = permission['id']
                    break
        
        people_with_access = [
            {
                "id": perm.get('id'),
                "emailAddress": perm.get('emailAddress'),
                "role": perm.get('role'),
                "displayName": perm.get('displayName'),
                "photoLink": perm.get('photoLink'),
                "type": perm.get('type')
            }
            for perm in permissions
        ]
        print("DEBUG: User Email:", user_email)
        print("DEBUG: User ID:", user_id)
        
        return jsonify({
            "currentUserRole": current_user_role,
            "currentUserId": current_user_id,
            "peopleWithAccess": people_with_access
        })
    except Exception as e:
        print(f"Debug - Error in people_with_access: {str(e)}") 
        return jsonify({"error": str(e)}), 400
    
@drive_permissions_bp.route('/drive/<item_id>/update-permission', methods=['POST'])
def update_permission(item_id):
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    permission_id = data.get('permissionId')
    new_role = data.get('role')
    
    drive_service, _ = get_services()
    
    try:
        # Check if the current user is an owner or writer
        user_role = get_user_role(item_id)
        if user_role.get('role') not in ['owner', 'writer']:
            return jsonify({"error": "Only owners and editors can update permissions"}), 403

        updated_permission = drive_service.permissions().update(
            fileId=item_id,
            permissionId=permission_id,
            body={'role': new_role},
            fields='id,role',
            supportsAllDrives=True
        ).execute()
        return jsonify({"message": "Permission updated successfully", "updatedPermission": updated_permission})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@drive_permissions_bp.route('/drive/<item_id>/remove-permission', methods=['POST'])
def remove_permission(item_id):
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    permission_id = data.get('permissionId')
    
    drive_service, _ = get_services()
    
    try:
        # Check if the current user is an owner or editor
        user_role = get_user_role(item_id)
        if user_role['role'] not in ['owner', 'writer']:
            return jsonify({"error": "Only owners and editors can remove permissions"}), 403

        drive_service.permissions().delete(
            fileId=item_id, 
            permissionId=permission_id,
            supportsAllDrives=True
        ).execute()
        return jsonify({"message": "Permission removed successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    
@drive_permissions_bp.route('/drive/<item_id>/user-role', methods=['GET'])
@drive_permissions_bp.route('/drive/<item_id>/user-role', methods=['GET'])
def get_user_role(item_id):
    print(f"DEBUG: Fetching user role for item {item_id}")  # Add this line
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    drive_service, _ = get_services()
    
    try:
        file = drive_service.files().get(fileId=item_id, fields='owners,permissions', supportsAllDrives=True).execute()
        user_email = session.get('user_email')
        
        print(f"DEBUG: User email from session: {user_email}")  # Add this line
        
        if user_email in [owner['emailAddress'] for owner in file.get('owners', [])]:
            print(f"DEBUG: User is owner")  # Add this line
            return jsonify({"role": "owner", "id": session.get('user_id')})
        
        for permission in file.get('permissions', []):
            if permission.get('emailAddress') == user_email:
                print(f"DEBUG: User role: {permission['role']}")  # Add this line
                return jsonify({"role": permission['role'], "id": permission.get('id')})
        
        print(f"DEBUG: User is viewer (default)")  # Add this line
        return jsonify({"role": "viewer", "id": None})
    except Exception as e:
        print(f"ERROR: Exception in get_user_role: {str(e)}")  # Add this line
        return jsonify({"error": str(e)}), 400