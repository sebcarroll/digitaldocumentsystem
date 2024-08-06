from marshmallow import Schema, fields

class FolderSchema(Schema):
    id = fields.Str(required=True)
    googleDriveId = fields.Str(required=True)
    name = fields.Str(required=True)
    parentFolderId = fields.Str()
    createdAt = fields.DateTime(required=True)
    modifiedAt = fields.DateTime(required=True)
    ownerId = fields.Str(required=True)
    categories = fields.List(fields.Str())
    accessControl = fields.Dict()
    metadata = fields.Dict()
    lastSyncTime = fields.DateTime()