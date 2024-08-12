from marshmallow import Schema, fields, post_load
from datetime import datetime, timezone

class DocumentSchema(Schema):
    id = fields.Str(required=True)
    googleDriveId = fields.Str(required=True)
    title = fields.Str(required=True)
    mimeType = fields.Str(required=True)
    createdAt = fields.Str(required=True) 
    modifiedAt = fields.Str(required=True) 
    ownerId = fields.Str(required=True)
    parentFolderId = fields.Str(allow_none=True)
    categories = fields.List(fields.Str(), load_default=[])
    metadata = fields.Dict(load_default={})
    summary = fields.Str(allow_none=True)
    keywords = fields.List(fields.Str(), load_default=[])
    version = fields.Int(load_default=1)
    accessControl = fields.Dict(load_default={})
    sharedFolders = fields.List(fields.Str(), load_default=[])
    sourceUrl = fields.Str(allow_none=True)
    citations = fields.List(fields.Str(), load_default=[])
    webViewLink = fields.Str(allow_none=True)
    chunk_index = fields.Int(load_default=1)
    total_chunks = fields.Int(load_default=1)
    content = fields.Str(required=True)

    @post_load
    def convert_dates(self, data, **kwargs):
        for field in ['createdAt', 'modifiedAt']:
            if data.get(field):
                data[field] = datetime.fromisoformat(data[field].rstrip('Z')).replace(tzinfo=timezone.utc)
        return data