from marshmallow import Schema, fields, post_load
from datetime import datetime, timezone

class QueryandDocumentSchema(Schema):
    googleDriveFileId = fields.Str(required=True)
    userId = fields.Str(required=True)
    content = fields.Str(required=True)
    isSelected = fields.Boolean(required=True)
    modifiedAt = fields.DateTime(required=True)

    @post_load
    def convert_dates(self, data, **kwargs):
        if data.get('modifiedAt'):
            data['modifiedAt'] = data['modifiedAt'].replace(tzinfo=timezone.utc)
        return data