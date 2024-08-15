/**
 * MovePopup.js
 * This component renders a popup for moving files or folders to a different location.
 */

import React from 'react';
import './popup.css';
import { useMovePopup } from '../../hooks/useMovePopup.js';

/**
 * MovePopup component
 * @param {Object} props - Component props
 * @param {Array} props.initialSelectedFiles - Initially selected files for moving
 * @param {Function} props.onMoveConfirm - Callback function to execute when move is confirmed
 * @param {Function} props.setError - Function to set error messages
 * @returns {React.ReactElement} MovePopup component
 */
const MovePopup = ({ initialSelectedFiles, onMoveConfirm, setError }) => {
  const {
    isOpen,
    activeTab,
    currentFolder,
    folderStack,
    folders,
    suggestedFolders,
    selectedFiles,
    handleOpen,
    handleClose,
    handleTabClick,
    handleFolderClick,
    handleBreadcrumbClick,
    handleBackClick,
    handleMoveConfirm,
  } = useMovePopup(initialSelectedFiles, onMoveConfirm, setError);

  if (!isOpen) return null;

  const title = selectedFiles.length === 1
    ? `Move "${selectedFiles[0].name}"`
    : `Move ${selectedFiles.length} items`;

  return (
    <div className="popup-overlay">
      <div className="popup-content move-popup">
        <h2>{title}</h2>
        <div className="tabs">
          <button
            className={activeTab === 'suggested' ? 'active' : ''}
            onClick={() => handleTabClick('suggested')}
          >
            Suggested
          </button>
          <button
            className={activeTab === 'all' ? 'active' : ''}
            onClick={() => handleTabClick('all')}
          >
            All locations
          </button>
        </div>
        <div className="breadcrumbs">
          <button onClick={() => handleBreadcrumbClick(-1)}>My Drive</button>
          {folderStack.map((folder, index) => (
            <React.Fragment key={folder.id}>
              <span> &gt; </span>
              <button onClick={() => handleBreadcrumbClick(index)}>{folder.name}</button>
            </React.Fragment>
          ))}
          {currentFolder.id !== 'root' && (
            <>
              <span> &gt; </span>
              <span>{currentFolder.name}</span>
            </>
          )}
        </div>
        <div className="folder-list">
          {activeTab === 'suggested'
            ? suggestedFolders.map(folder => (
                <div key={folder.id} className="folder-item" onClick={() => handleFolderClick(folder)}>
                  {folder.name}
                </div>
              ))
            : folders.map(folder => (
                <div key={folder.id} className="folder-item" onClick={() => handleFolderClick(folder)}>
                  {folder.name}
                </div>
              ))
          }
        </div>
        <div className="popup-actions">
          <button className="cancel-button" onClick={handleClose}>Cancel</button>
          <button
            className="ok-button"
            onClick={handleMoveConfirm}
            disabled={currentFolder.id === 'root'}
          >
            Move
          </button>
        </div>
      </div>
    </div>
  );
};

export default MovePopup;