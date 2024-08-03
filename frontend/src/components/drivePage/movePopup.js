// MovePopup.js
import React from 'react';
import './popup.css';

const MovePopup = ({
  isOpen,
  onClose,
  onMove,
  selectedFiles,
  activeTab,
  currentFolder,
  folderStack,
  folders,
  suggestedFolders,
  handleTabClick,
  handleFolderClick,
  handleBreadcrumbClick,
}) => {
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
          <button className="cancel-button" onClick={onClose}>Cancel</button>
          <button
            className="ok-button"
            onClick={onMove}
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