// sharePopup.js
import React from 'react';
import './sharePopup.css';

const SharePopup = ({ 
  isOpen, 
  onClose, 
  items, 
  onShare, 
  onCopyLink,
  email,
  searchResults,
  peopleWithAccess,
  generalAccess,
  isLoading,
  error,
  onEmailChange,
  onAddPerson,
  onAccessLevelChange,
  onRemoveAccess,
  onGeneralAccessChange
}) => {
  if (!isOpen) return null;

  const handleShare = () => {
    onShare({
      itemIds: items.map(item => item.id),
      peopleWithAccess,
      generalAccess,
    });
    onClose();
  };

  return (
    <div className="share-popup-overlay">
      <div className="share-popup">
        <h2>Share {items.length > 1 ? `${items.length} items` : `'${items[0].name}'`}</h2>
        <input
          type="text"
          value={email}
          onChange={(e) => onEmailChange(e.target.value)}
          placeholder="Add people and groups"
        />
        {searchResults.length > 0 && (
          <ul className="search-results">
            {searchResults.map(person => (
              <li key={person.id} onClick={() => onAddPerson(person)}>
                <img src={person.photoUrl} alt={person.name} />
                {person.name} ({person.email})
              </li>
            ))}
          </ul>
        )}
        <h3>People with access</h3>
        {isLoading && <p>Loading...</p>}
        {error && <p className="error">{error}</p>}
        <ul className="people-with-access">
          {peopleWithAccess.map(person => (
            <li key={person.id}>
              <img src={person.photoLink} alt={person.displayName} />
              <div>
                <strong>{person.displayName}</strong>
                <span>{person.emailAddress}</span>
              </div>
              <select
                value={person.role}
                onChange={(e) => onAccessLevelChange(person.id, e.target.value)}
              >
                <option value="reader">Viewer</option>
                <option value="commenter">Commenter</option>
                <option value="writer">Editor</option>
              </select>
              <button onClick={() => onRemoveAccess(person.id)}>Remove access</button>
            </li>
          ))}
        </ul>
        <div className="general-access">
          <h3>General access</h3>
          <select
            value={generalAccess}
            onChange={(e) => onGeneralAccessChange(e.target.value)}
          >
            <option value="Restricted">Restricted</option>
            <option value="Anyone with the link">Anyone with the link</option>
          </select>
        </div>
        <div className="popup-actions">
          <button onClick={() => onCopyLink(items[0])}>Copy link</button>
          <button onClick={handleShare}>Done</button>
        </div>
      </div>
    </div>
  );
};

export default SharePopup;