import React from 'react';
import './documentList.css';

const SelectedDocuments = ({ documents, onRemove }) => {
  return (
    <div className="selected-documents">
      {documents.map((doc) => (
        <div key={doc.id} className="document-bubble">
          <span className="document-name">{doc.name}</span>
          <button className="remove-document" onClick={() => onRemove(doc.id)}>×</button>
        </div>
      ))}
    </div>
  );
};

export default SelectedDocuments;