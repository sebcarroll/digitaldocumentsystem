from pinecone import init, Index
from flask import current_app

def initialize_pinecone():
    init(
        api_key=current_app.config['PINECONE_API_KEY'],
        environment=current_app.config['PINECONE_ENVIRONMENT']
    )
    return Index(current_app.config['PINECONE_INDEX_NAME'])

# Define your index structure here (for documentation purposes)
PINECONE_INDEX_STRUCTURE = {
    "id": "unique_id",
    "vector": "[float_values]",
    "metadata": {
        "googleDriveId": "string",
        "title": "string",
        "mimeType": "string",
        "createdAt": "timestamp",
        "modifiedAt": "timestamp",
        "ownerId": "string",
        "parentFolderId": "string",
        "aiSuggestedCategories": ["string"],
        "userCategories": ["string"],
        "suggestedFolder": "string",
        "userSelectedFolder": "string",
        "version": "integer",
        "accessControl": {
            "ownerId": "string",
            "readers": ["string"],
            "writers": ["string"]
        },
        "sharedFolders": ["string"],
        "sourceUrl": "string",
        "languageCode": "string",
        "webViewLink": "string",
        "lastSyncTime": "timestamp",
        "chunk_index": "integer",
        "total_chunks": "integer"
    }
}