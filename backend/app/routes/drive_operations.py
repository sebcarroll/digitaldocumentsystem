from flask import Blueprint, request, jsonify, session
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import os

drive_ops_bp = Blueprint('drive_ops', __name__)

def get_services():
    credentials = Credentials(**session['credentials'])
    drive_service = build('drive', 'v3', credentials=credentials)
    people_service = build('people', 'v1', credentials=credentials)
    return drive_service, people_service

@drive_ops_bp.route('/drive/<file_id>/open', methods=['GET'])
def open_file(file_id):
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    drive_service, _ = get_services()
    
    try:
        file = drive_service.files().get(fileId=file_id, fields='webViewLink').execute()
        return jsonify({"webViewLink": file.get('webViewLink')})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@drive_ops_bp.route('/drive/create-folder', methods=['POST'])
def create_folder():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    parent_folder_id = data.get('parentFolderId', 'root')
    folder_name = data.get('folderName')

    drive_service, _ = get_services()
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }
    file = drive_service.files().create(body=file_metadata, fields='id').execute()
    return jsonify({"id": file.get('id')})

@drive_ops_bp.route('/drive/upload-file', methods=['POST'])
def upload_file():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    file = request.files['file']
    folder_id = request.form.get('folderId', 'root')

    drive_service, _ = get_services()
    file_metadata = {'name': file.filename, 'parents': [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(file.read()),
                              mimetype=file.content_type,
                              resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return jsonify({"id": file.get('id')})

@drive_ops_bp.route('/drive/upload-folder', methods=['POST'])
def upload_folder():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    parent_folder_id = request.form.get('parentFolderId', 'root')
    files = request.files.getlist('files')

    drive_service, _ = get_services()
    uploaded_files = []

    def create_folder(name, parent_id):
        folder_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')

    def upload_file(file, parent_id):
        file_metadata = {'name': os.path.basename(file.filename), 'parents': [parent_id]}
        media = MediaIoBaseUpload(io.BytesIO(file.read()),
                                  mimetype=file.content_type,
                                  resumable=True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')

    folder_structure = {}

    for file in files:
        path_parts = file.filename.split(os.path.sep)
        current_parent = parent_folder_id

        for i, part in enumerate(path_parts[:-1]):
            if i == 0:
                if part not in folder_structure:
                    folder_id = create_folder(part, current_parent)
                    folder_structure[part] = folder_id
                current_parent = folder_structure[part]
            else:
                parent_path = os.path.sep.join(path_parts[:i])
                current_path = os.path.sep.join(path_parts[:i+1])
                if current_path not in folder_structure:
                    folder_id = create_folder(part, current_parent)
                    folder_structure[current_path] = folder_id
                current_parent = folder_structure[current_path]

        file_id = upload_file(file, current_parent)
        uploaded_files.append({"name": file.filename, "id": file_id})

    return jsonify({"uploaded_files": uploaded_files})

@drive_ops_bp.route('/drive/create-doc', methods=['POST'])
def create_doc():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    folder_id = data.get('folderId', 'root')

    drive_service, _ = get_services()
    file_metadata = {
        'name': 'Untitled document',
        'mimeType': 'application/vnd.google-apps.document',
        'parents': [folder_id]
    }
    file = drive_service.files().create(body=file_metadata, fields='id, webViewLink').execute()
    return jsonify({
        "id": file.get('id'),
        "webViewLink": file.get('webViewLink')
    })

@drive_ops_bp.route('/drive/create-sheet', methods=['POST'])
def create_sheet():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    folder_id = data.get('folderId', 'root')

    drive_service, _ = get_services()
    file_metadata = {
        'name': 'Untitled spreadsheet',
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'parents': [folder_id]
    }
    file = drive_service.files().create(body=file_metadata, fields='id, webViewLink').execute()
    return jsonify({
        "id": file.get('id'),
        "webViewLink": file.get('webViewLink')
    })  

@drive_ops_bp.route('/drive/move-files', methods=['POST'])
def move_files():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    file_ids = data.get('fileIds', [])
    new_folder_id = data.get('newFolderId')

    drive_service, _ = get_services()
    
    moved_files = []
    errors = []

    for file_id in file_ids:
        try:
            file = drive_service.files().get(fileId=file_id, fields='parents').execute()
            previous_parents = ",".join(file.get('parents'))
            file = drive_service.files().update(
                fileId=file_id,
                addParents=new_folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
            moved_files.append({"id": file.get('id'), "parents": file.get('parents')})
        except Exception as e:
            errors.append(f"Failed to move file {file_id}: {str(e)}")

    if errors:
        return jsonify({"error": "; ".join(errors), "moved_files": moved_files}), 400
    
    return jsonify({"message": "Files moved successfully", "moved_files": moved_files})

@drive_ops_bp.route('/drive/delete-files', methods=['POST'])
def delete_files():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    file_ids = data.get('fileIds', [])

    drive_service, _ = get_services()
    
    deleted_files = []
    errors = []

    for file_id in file_ids:
        try:
            drive_service.files().delete(fileId=file_id).execute()
            deleted_files.append(file_id)
        except Exception as e:
            errors.append(f"Failed to delete file {file_id}: {str(e)}")

    if errors:
        return jsonify({"error": "; ".join(errors), "deleted_files": deleted_files}), 400
    
    return jsonify({"message": "Files deleted successfully", "deleted_files": deleted_files})

@drive_ops_bp.route('/drive/copy-files', methods=['POST'])
def copy_files():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    file_ids = data.get('fileIds', [])

    drive_service, _ = get_services()
    
    copied_files = []
    errors = []

    for file_id in file_ids:
        try:
            copied_file = drive_service.files().copy(fileId=file_id, fields='id, name').execute()
            copied_files.append({"id": copied_file.get('id'), "name": copied_file.get('name')})
        except Exception as e:
            errors.append(f"Failed to copy file {file_id}: {str(e)}")

    if errors:
        return jsonify({"error": "; ".join(errors), "copied_files": copied_files}), 400
    
    return jsonify({"message": "Files copied successfully", "copied_files": copied_files})

@drive_ops_bp.route('/drive/rename-file', methods=['POST'])
def rename_file():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    file_id = data.get('fileId')
    new_name = data.get('newName')

    drive_service, _ = get_services()
    
    try:
        file = drive_service.files().update(
            fileId=file_id,
            body={'name': new_name},
            fields='id, name'
        ).execute()
        return jsonify({"id": file.get('id'), "name": file.get('name')})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@drive_ops_bp.route('/drive/<item_id>/people-with-access', methods=['GET'])
def people_with_access(item_id):
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    drive_service, _ = get_services()
    
    try:
        permissions = drive_service.permissions().list(
            fileId=item_id,
            fields="permissions(id,emailAddress,role,displayName,photoLink)",
            supportsAllDrives=True
        ).execute()
        return jsonify({"peopleWithAccess": permissions.get('permissions', [])})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@drive_ops_bp.route('/drive/<item_id>/share', methods=['POST'])
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

@drive_ops_bp.route('/drive/<item_id>/update-permission', methods=['POST'])
def update_permission(item_id):
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    permission_id = data.get('permissionId')
    new_role = data.get('role')
    
    drive_service, _ = get_services()
    
    try:
        # Check if the current user is an owner or editor
        user_role = get_user_role(item_id)
        if user_role.get('role') not in ['owner', 'editor']:
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


@drive_ops_bp.route('/drive/<item_id>/remove-permission', methods=['POST'])
def remove_permission(item_id):
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    permission_id = data.get('permissionId')
    
    drive_service, _ = get_services()
    
    try:
        # Check if the current user is an owner or editor
        user_role = get_user_role(item_id)
        if user_role['role'] not in ['owner', 'editor']:
            return jsonify({"error": "Only owners and editors can remove permissions"}), 403

        drive_service.permissions().delete(
            fileId=item_id, 
            permissionId=permission_id,
            supportsAllDrives=True
        ).execute()
        return jsonify({"message": "Permission removed successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@drive_ops_bp.route('/drive/<item_id>/update-general-access', methods=['POST'])
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

def list_folder_contents(drive_service, folder_id, page_token=None):
    results = []
    while True:
        response = drive_service.files().list(
            q=f"'{folder_id}' in parents",
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType)',
            pageToken=page_token,
            supportsAllDrives=True
        ).execute()
        results.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return results

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

@drive_ops_bp.route('/drive/folders', methods=['GET'])
def fetch_folders():
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    drive_service, _ = get_services()
    parent_id = request.args.get('parent_id', 'root')
    
    try:
        results = drive_service.files().list(
            q=f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder'",
            spaces='drive',
            fields='files(id, name)',
            supportsAllDrives=True
        ).execute()
        
        folders = results.get('files', [])
        return jsonify({"folders": folders})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@drive_ops_bp.route('/drive/<item_id>/user-role', methods=['GET'])
def get_user_role(item_id):
    if 'credentials' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    drive_service, _ = get_services()
    
    try:
        file = drive_service.files().get(fileId=item_id, fields='owners,permissions', supportsAllDrives=True).execute()
        user_email = session.get('user_email')
        
        if user_email in [owner['emailAddress'] for owner in file.get('owners', [])]:
            return jsonify({"role": "owner"})
        
        for permission in file.get('permissions', []):
            if permission.get('emailAddress') == user_email:
                return jsonify({"role": permission['role']})
        
        return jsonify({"role": "viewer"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
