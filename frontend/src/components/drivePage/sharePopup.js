import React from 'react';
import './popup.css';

const SharePopup = ({ 
  isOpen, 
  onClose, 
  items = [], 
  onCopyLink,
  email,
  searchResults,
  peopleWithAccess,
  generalAccess,
  isLoading,
  error,
  pendingEmails,
  onEmailChange,
  onAddPendingEmail,
  onRemovePendingEmail,
  onAccessLevelChange,
  onRemoveAccess,
  onGeneralAccessChange,
  onShareWithPendingEmails,
  currentUserRole,
  linkAccessRole,
  currentUserId,
  onLinkAccessChange,
  isSharingLoading,
}) => {
  if (!isOpen) return null;

  if (isSharingLoading) {
    return (
      <div className="share-popup-overlay">
        <div className="share-popup">
          <h2>Loading...</h2>
        </div>
      </div>
    );
  }

  const currentUserAccess = peopleWithAccess.find(person => person.id === currentUserId);

  const title = items.length > 1 
    ? `Share ${items.length} items` 
    : items.length === 1 
      ? `Share '${items[0].name}'` 
      : 'Share';

  const handleKeyDown = (e) => {
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      if (email.trim()) {
        onAddPendingEmail(email.trim());
      }
    }
  };

  const handleDone = () => {
    onShareWithPendingEmails();
    onClose();
  };

  const canEditPermissions = ['writer', 'owner'].includes(currentUserRole.toLowerCase());

  const anyoneWithLinkPerson = peopleWithAccess.find(person => person.id === 'anyoneWithLink');
  const filteredPeopleWithAccess = peopleWithAccess.filter(person => person.id !== 'anyoneWithLink');

  return (
    <div className="share-popup-overlay">
      <div className="share-popup">
      <h2>{title}</h2> 
        <h3>People with access</h3>
        {isLoading && <p>Loading...</p>}
        {error && <p className="error">{error}</p>}
        <ul className="people-with-access">
          {filteredPeopleWithAccess.map(person => (
            <li key={person.id}>
              <img src={person.photoLink} alt={person.displayName} />
              <div className="person-info">
                <strong>{person.displayName}</strong>
                <span>{person.emailAddress}</span>
              </div>
              <select
                value={person.role}
                onChange={(e) => onAccessLevelChange(person.id, e.target.value)}
                disabled={
                  !canEditPermissions ||
                  person.role.toLowerCase() === 'owner'
                }
              >
                <option value="viewer">Viewer</option>
                <option value="commenter">Commenter</option>
                <option value="writer">Editor</option>
                {person.role.toLowerCase() === 'owner' && <option value="owner">Owner</option>}
              </select>
              {canEditPermissions && person.role.toLowerCase() !== 'owner' && (
                <button onClick={() => onRemoveAccess(person.id)}>Remove access</button>
              )}
            </li>
          ))}
        </ul>
        <div className="general-access">
          <h3>General access</h3>
          <div className="access-controls">
            <select
              value={generalAccess}
              onChange={(e) => onGeneralAccessChange(e.target.value)}
              disabled={!canEditPermissions}
            >
              <option value="Restricted">Restricted</option>
              <option value="Anyone with the link">Anyone with the link</option>
            </select>
            {generalAccess === "Anyone with the link" && (
              <select
                value={linkAccessRole}
                onChange={(e) => onLinkAccessChange(e.target.value)}
                disabled={!canEditPermissions}
              >
                <option value="viewer">Viewer</option>
                <option value="commenter">Commenter</option>
                <option value="writer">Editor</option>
              </select>
            )}
          </div>
          {generalAccess === "Anyone with the link" && (
            <p className="access-description">
              Anyone on the Internet with the link can {
                linkAccessRole === 'viewer' ? 'view' :
                linkAccessRole === 'commenter' ? 'comment' :
                linkAccessRole === 'writer' ? 'edit' : 
                'access'
              }
            </p>
          )}
        </div>
        <div className="popup-actions">
          {canEditPermissions && (
            <button onClick={() => items.length > 0 && onCopyLink(items[0])} disabled={items.length === 0}>
              Copy link
            </button>
          )}
          <button onClick={handleDone}>Done</button>
        </div>
      </div>
    </div>
  );
};

export default SharePopup;