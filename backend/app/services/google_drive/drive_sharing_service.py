from .core import DriveCore
from google.oauth2.credentials import Credentials


class DriveSharingService:
    def __init__(self, drive_core):
        self.drive_core = drive_core
        self.drive_service = drive_core.drive_service

    def share_item(self, item_id, emails, role):
        shared_with = []
        errors = []

        for email in emails:
            try:
                permission = {
                    'type': 'user',
                    'role': role,
                    'emailAddress': email
                }
                result = self.drive_core.drive_service.permissions().create(
                    fileId=item_id, 
                    body=permission, 
                    fields='id',
                    supportsAllDrives=True
                ).execute()
                shared_with.append({"email": email, "permissionId": result.get('id')})
            except Exception as e:
                errors.append(f"Failed to share with {email}: {str(e)}")

        if errors:
            return {"error": "; ".join(errors), "shared_with": shared_with}
        
        return {"message": "Item shared successfully", "shared_with": shared_with}

    def update_general_access(self, item_id, new_access, link_role):
        try:
            item = self.drive_core.drive_service.files().get(fileId=item_id, fields='mimeType', supportsAllDrives=True).execute()
            is_folder = item['mimeType'] == 'application/vnd.google-apps.folder'

            if new_access == 'Anyone with the link':
                permission = {
                    'type': 'anyone',
                    'role': link_role,
                    'allowFileDiscovery': False
                }
                self.drive_core.drive_service.permissions().create(
                    fileId=item_id, 
                    body=permission,
                    supportsAllDrives=True
                ).execute()
                
                if is_folder:
                    self._apply_permission_recursively(item_id, permission)

            elif new_access == 'Restricted':
                permissions = self.drive_core.drive_service.permissions().list(fileId=item_id, supportsAllDrives=True).execute()
                for permission in permissions.get('permissions', []):
                    if permission.get('type') == 'anyone':
                        self.drive_core.drive_service.permissions().delete(
                            fileId=item_id, 
                            permissionId=permission['id'],
                            supportsAllDrives=True
                        ).execute()
                
                if is_folder:
                    self._remove_anyone_permission_recursively(item_id)
            
            return {"message": f"General access updated successfully for {'folder' if is_folder else 'file'}"}
        except Exception as e:
            return str(e), 400

    def _apply_permission_recursively(self, folder_id, permission):
        items = self.drive_core.list_folder_contents(folder_id)
        for item in items:
            self.drive_core.drive_service.permissions().create(
                fileId=item['id'], 
                body=permission, 
                supportsAllDrives=True
            ).execute()
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                self._apply_permission_recursively(item['id'], permission)

    def _remove_anyone_permission_recursively(self, folder_id):
        items = self.drive_core.list_folder_contents(folder_id)
        for item in items:
            permissions = self.drive_core.drive_service.permissions().list(fileId=item['id'], supportsAllDrives=True).execute()
            for permission in permissions.get('permissions', []):
                if permission.get('type') == 'anyone':
                    self.drive_core.drive_service.permissions().delete(
                        fileId=item['id'], 
                        permissionId=permission['id'],
                        supportsAllDrives=True
                    ).execute()
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                self._remove_anyone_permission_recursively(item['id'])