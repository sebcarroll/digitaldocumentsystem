from marshmallow import Schema, fields

class SyncLogSchema(Schema):
    id = fields.Str(required=True)
    userId = fields.Str(required=True)
    startTime = fields.DateTime(required=True)
    endTime = fields.DateTime()
    status = fields.Str()
    changesProcessed = fields.Int()
    errors = fields.List(fields.Str())
    syncType = fields.Str()
    affectedDocuments = fields.List(fields.Str())
    performance = fields.Dict()