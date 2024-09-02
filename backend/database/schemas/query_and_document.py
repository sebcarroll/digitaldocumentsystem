from marshmallow import Schema, fields, post_load
from datetime import datetime, timezone

class DocumentSchema(Schema):
    """
    A Marshmallow schema for validating and deserializing document data.

    This schema expects the following fields:
    - `googleDriveFileId`: The Google Drive file ID (string).
    - `content`: The content of the document (string).
    - `isSelected`: A flag indicating if the document is selected (boolean).
    - `modifiedAt`: The timestamp when the document was last modified (datetime).

    After deserialization, the `modifiedAt` field will be converted to UTC.
    """
    googleDriveFileId = fields.Str(required=True)
    content = fields.Str(required=True)
    isSelected = fields.Boolean(required=True)
    modifiedAt = fields.DateTime(required=True)

    @post_load
    def convert_dates(self, data, **kwargs):
        """
        Converts the `modifiedAt` field to UTC timezone after loading the data.

        Args:
            data (dict): The deserialized data from the schema.

        Returns:
            dict: The updated data with `modifiedAt` in UTC timezone.
        """
        if data.get('modifiedAt'):
            data['modifiedAt'] = data['modifiedAt'].replace(tzinfo=timezone.utc)
        return data
