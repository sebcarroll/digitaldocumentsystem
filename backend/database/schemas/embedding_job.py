from marshmallow import Schema, fields

class EmbeddingJobSchema(Schema):
    id = fields.Str(required=True)
    documentId = fields.Str(required=True)
    status = fields.Str(required=True)
    createdAt = fields.DateTime(required=True)
    startedAt = fields.DateTime()
    completedAt = fields.DateTime()
    error = fields.Str()
    priority = fields.Int()