/**
 * SharePopup.js
 * This component renders a popup for sharing files or folders with other users.
 */

import React from 'react';
import './popup.css';
import { useFileSharing } from '../../hooks/useFileSharing.js';

/**
 * SharePopup component
 * @param {Object} props - Component props
 * @param {Array} props.items - Files or folders to be shared
 * @param {Function} props.onClose - Function to call when closing the popup
 * @returns {React.ReactElement} SharePopup component
 */
const SharePopup = ({ items, onClose }) => {
  const {
    email,
    searchResults,
    peopleWithAccess,
    generalAccess,
    pendingEmails,
    currentUserRole,
    linkAccessRole,
    currentUserId,
    handleEmailChange,
    handleAddPendingEmail,
    handleRemovePendingEmail,
    handleAccessLevelChange,
    handleRemoveAccess,
    handleGeneralAccessChange,
    handleShareWithPendingEmails,
    handleLinkAccessRoleChange,
    isSharingLoading,
    sharingError,
  } = useFileSharing(items);

  const title = items.length > 1 
    ? `Share ${items.length} items` 
    : items.length === 1 
      ? `Share '${items[0].name}'` 
      : 'Share';

  const handleKeyDown = (e) => {
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      if (email.trim()) {
        handleAddPendingEmail(email.trim());
      }
    }
  };

  const handleDone = () => {
    handleShareWithPendingEmails();
    onClose();
  };

  const canEditPermissions = ['writer', 'owner'].includes(currentUserRole?.toLowerCase());

  return (
    <div className="share-popup-overlay">
      <div className="share-popup">
        <h2>{title}</h2>
        {canEditPermissions && (
          <div className="email-input-container">
            {pendingEmails.map((pendingEmail, index) => (
              <span key={index} className="pending-email">
                {pendingEmail}
                <button onClick={() => handleRemovePendingEmail(pendingEmail)}>&times;</button>
              </span>
            ))}
            <input
              type="text"
              value={email}
              onChange={(e) => handleEmailChange(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Add people and groups"
            />
          </div>
        )}
        {searchResults.length > 0 && canEditPermissions && (
          <ul className="search-results">
            {searchResults.map(person => (
              <li key={person.id} onClick={() => handleAddPendingEmail(person.email)}>
                <img src={person.photoUrl} alt={person.name} />
                {person.name} ({person.email})
              </li>
            ))}
          </ul>
        )}
        <h3>People with access</h3>
        {isSharingLoading && <p>Loading...</p>}
        {sharingError && <p className="error">{sharingError}</p>}
        <ul className="people-with-access">
          {peopleWithAccess.map(person => (
            <li key={person.id}>
              <img src={person.photoLink} alt={person.displayName} />
              <div className="person-info">
                <strong>{person.displayName}</strong>
                <span>{person.emailAddress}</span>
              </div>
              <select
                value={person.role}
                onChange={(e) => handleAccessLevelChange(person.id, e.target.value)}
                disabled={!canEditPermissions || person.role.toLowerCase() === 'owner'}
              >
                <option value="viewer">Viewer</option>
                <option value="commenter">Commenter</option>
                <option value="writer">Editor</option>
                {person.role.toLowerCase() === 'owner' && <option value="owner">Owner</option>}
              </select>
              {canEditPermissions && person.role.toLowerCase() !== 'owner' && (
                <button onClick={() => handleRemoveAccess(person.id)}>Remove access</button>
              )}
            </li>
          ))}
        </ul>
        <div className="general-access">
          <h3>General access</h3>
          <select
            value={generalAccess}
            onChange={(e) => handleGeneralAccessChange(e.target.value)}
            disabled={!canEditPermissions}
          >
            <option value="Restricted">Restricted</option>
            <option value="Anyone with the link">Anyone with the link</option>
          </select>
          {generalAccess === "Anyone with the link" && (
            <select
              value={linkAccessRole}
              onChange={(e) => handleLinkAccessRoleChange(e.target.value)}
              disabled={!canEditPermissions}
            >
              <option value="viewer">Viewer</option>
              <option value="commenter">Commenter</option>
              <option value="writer">Editor</option>
            </select>
          )}
        </div>
        <div className="popup-actions">
          <button onClick={handleDone}>Done</button>
        </div>
      </div>
    </div>
  );
};

export default SharePopup;