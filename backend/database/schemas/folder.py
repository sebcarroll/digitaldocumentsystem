from marshmallow import Schema, fields, post_load
from datetime import datetime, timezone

class FolderSchema(Schema):
    id = fields.Str(required=True)
    googleDriveId = fields.Str(required=True)
    name = fields.Str(required=True)
    parentFolderId = fields.Str(allow_none=True)
    createdAt = fields.DateTime(required=True)
    modifiedAt = fields.DateTime(required=True)
    ownerId = fields.Str(required=True)
    categories = fields.List(fields.Str(), missing=[])
    accessControl = fields.Dict(missing={})
    metadata = fields.Dict(missing={})
    lastSyncTime = fields.DateTime(allow_none=True)

    @post_load
    def convert_dates(self, data, **kwargs):
        for field in ['createdAt', 'modifiedAt', 'lastSyncTime']:
            if data.get(field):
                if isinstance(data[field], str):
                    data[field] = datetime.fromisoformat(data[field].rstrip('Z')).replace(tzinfo=timezone.utc)
        return data