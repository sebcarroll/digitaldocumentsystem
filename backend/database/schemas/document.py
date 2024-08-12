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
    aiSuggestedCategories = fields.List(fields.Str(), missing=[])
    userCategories = fields.List(fields.Str(), missing=[])
    suggestedFolder = fields.Str(allow_none=True)
    userSelectedFolder = fields.Str(allow_none=True)
    metadata = fields.Dict(missing={})
    summary = fields.Str(allow_none=True)
    keywords = fields.List(fields.Str(), missing=[])
    lastEmbeddingUpdate = fields.Str(allow_none=True) 
    version = fields.Int(missing=1)
    accessControl = fields.Dict(missing={})
    sharedFolders = fields.List(fields.Str(), missing=[])
    sourceUrl = fields.Str(allow_none=True)
    citations = fields.List(fields.Str(), missing=[])
    webViewLink = fields.Str(allow_none=True)
    lastSyncTime = fields.Str(allow_none=True) 
    chunk_index = fields.Int(missing=1)
    total_chunks = fields.Int(missing=1)
    content = fields.Str(required=True)

    @post_load
    def convert_dates(self, data, **kwargs):
        for field in ['createdAt', 'modifiedAt', 'lastEmbeddingUpdate', 'lastSyncTime']:
            if data.get(field):
                data[field] = datetime.fromisoformat(data[field].rstrip('Z')).replace(tzinfo=timezone.utc)
        return data