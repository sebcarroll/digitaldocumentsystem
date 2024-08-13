import React from 'react';

function DocumentList({ documents }) {
  if (documents.length === 0) return null;

  return (
    <div className="document-list">
      {documents.length === 1 ? (
        <span>{documents[0].name}</span>
      ) : (
        <span>{documents.length} documents uploaded</span>
      )}
    </div>
  );
}

export default DocumentList;