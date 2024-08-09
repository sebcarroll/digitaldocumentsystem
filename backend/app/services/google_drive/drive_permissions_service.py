from .core import DriveCore

class DrivePermissionsService:
    def __init__(self, credentials, user_email=None, user_id=None):
        self.drive_core = DriveCore(credentials)
        self.user_email = user_email
        self.user_id = user_id

    def get_people_with_access(self, item_id):
        try:
            file = self.drive_core.drive_service.files().get(fileId=item_id, fields='owners', supportsAllDrives=True).execute()
            
            permissions = []
            page_token = None
            while True:
                response = self.drive_core.drive_service.permissions().list(
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
            
            if self.user_email in [owner.get('emailAddress') for owner in file.get('owners', [])]:
                current_user_role = "owner"
                current_user_id = self.user_id
            else:
                for permission in permissions:
                    if permission.get('emailAddress') == self.user_email:
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
            
            return {
                "currentUserRole": current_user_role,
                "currentUserId": current_user_id,
                "peopleWithAccess": people_with_access
            }
        except Exception as e:
            return str(e), 400

    def update_permission(self, item_id, permission_id, new_role):
        try:
            user_role = self.get_user_role(item_id)
            if isinstance(user_role, tuple) or user_role.get('role') not in ['owner', 'writer']:
                return "Only owners and editors can update permissions", 403

            updated_permission = self.drive_core.drive_service.permissions().update(
                fileId=item_id,
                permissionId=permission_id,
                body={'role': new_role},
                fields='id,role',
                supportsAllDrives=True
            ).execute()
            return {"message": "Permission updated successfully", "updatedPermission": updated_permission}
        except Exception as e:
            return str(e), 400

    def remove_permission(self, item_id, permission_id):
        try:
            user_role = self.get_user_role(item_id)
            if isinstance(user_role, tuple) or user_role['role'] not in ['owner', 'writer']:
                return "Only owners and editors can remove permissions", 403

            self.drive_core.drive_service.permissions().delete(
                fileId=item_id, 
                permissionId=permission_id,
                supportsAllDrives=True
            ).execute()
            return {"message": "Permission removed successfully"}
        except Exception as e:
            return str(e), 400

    def get_user_role(self, item_id):
        try:
            file = self.drive_core.drive_service.files().get(fileId=item_id, fields='owners,permissions', supportsAllDrives=True).execute()
            
            if self.user_email in [owner['emailAddress'] for owner in file.get('owners', [])]:
                return {"role": "owner", "id": self.user_id}
            
            for permission in file.get('permissions', []):
                if permission.get('emailAddress') == self.user_email:
                    return {"role": permission['role'], "id": permission.get('id')}
            
            return {"role": "viewer", "id": None}
        except Exception as e:
            return str(e), 400