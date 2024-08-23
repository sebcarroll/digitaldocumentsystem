// MovePopup.js
import React from 'react';
import './popup.css';

const MovePopupBreadcrumb = ({ folderStack, currentFolder, onBreadcrumbClick }) => {
  const getBreadcrumbs = () => {
    let breadcrumbs = [...folderStack, currentFolder];
    if (breadcrumbs.length > 3) {
      breadcrumbs = [{ id: '...', name: '...' }, ...breadcrumbs.slice(-2)];
    }

    return breadcrumbs.map((folder, index) => {
      let folderName = folder.name;
      if (folderName.length > 15) {
        folderName = folderName.slice(0, 12) + '...';
      }
      return (
        <React.Fragment key={folder.id}>
          {index > 0 && <span className="move-breadcrumb-separator">&gt;</span>}
          <span 
            onClick={() => onBreadcrumbClick(index)} 
            className={`move-breadcrumb-item ${index === breadcrumbs.length - 1 ? 'move-current-item' : ''}`}
          >
            {folderName}
          </span>
        </React.Fragment>
      );
    });
  };

  return (
    <div className="move-breadcrumbs">
      {getBreadcrumbs()}
    </div>
  );
};

const MovePopup = ({ 
  isOpen, 
  onClose, 
  onMove, 
  selectedFiles, 
  currentFolder, 
  folderStack, 
  folders, 
  handleFolderClick, 
  handleBreadcrumbClick 
}) => {
  if (!isOpen) return null;

  const title = selectedFiles.length === 1
    ? `Move "${selectedFiles[0].name}"`
    : `Move ${selectedFiles.length} items`;

  return (
    <div className="popup-overlay">
      <div className="popup-content move-popup">
        <h2>{title}</h2>
        <MovePopupBreadcrumb
          folderStack={folderStack}
          currentFolder={currentFolder}
          onBreadcrumbClick={handleBreadcrumbClick}
        />
        <div className="folder-list">
          {folders.length > 0 ? (
            folders.map(folder => (
              <div key={folder.id} className="folder-item" onClick={() => handleFolderClick(folder)}>
                {folder.name}
              </div>
            ))
          ) : (
            <div className="empty-folder-message">This folder is empty</div>
          )}
        </div>
        <div className="popup-actions">
        <button className="cancel-button" onClick={onClose}>Cancel</button>
        <button className="ok-button" onClick={onMove}>
            Move here
          </button>
        </div>
      </div>
    </div>
  );
};

export default MovePopup;