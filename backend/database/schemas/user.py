from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Str(required=True)
    googleId = fields.Str(required=True)
    email = fields.Str(required=True)
    name = fields.Str(required=True)
    lastSyncTime = fields.DateTime()
    roles = fields.List(fields.Str())
    preferences = fields.Dict()
    apiKey = fields.Str()
    createdAt = fields.DateTime(required=True)
    lastLoginAt = fields.DateTime()
    lastActive = fields.DateTime()
    credentials = fields.Dict()