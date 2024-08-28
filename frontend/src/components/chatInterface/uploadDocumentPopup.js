import React, { useState, useEffect } from 'react';
import './uploadDocumentPopup.css';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import FolderIcon from '@mui/icons-material/Folder';
import MoreVertIcon from '@mui/icons-material/MoreVert';

const UploadPopupBreadcrumb = ({ folderStack = [], currentFolder, onBreadcrumbClick }) => {
  console.log('UploadPopupBreadcrumb rendering', { folderStack, currentFolder });

  const getBreadcrumbs = () => {
    let breadcrumbs = [...folderStack, currentFolder].filter(Boolean);
    if (breadcrumbs.length === 0) {
      breadcrumbs = [{ id: 'root', name: 'My Drive' }];
    }
    if (breadcrumbs.length > 3) {
      breadcrumbs = [{ id: '...', name: '...' }, ...breadcrumbs.slice(-2)];
    }

    console.log('Breadcrumbs generated:', breadcrumbs);
    return breadcrumbs.map((folder, index) => {
      let folderName = folder.name || 'Unknown';
      if (folderName.length > 15) {
        folderName = folderName.slice(0, 12) + '...';
      }
      return (
        <React.Fragment key={folder.id || `folder-${index}`}>
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

const UploadPopup = ({ 
  getFileIcon, 
  setError, 
  isOpen, 
  onClose, 
  onUpload,
  selectedFiles,
  currentFolder,
  folderStack,
  items,
  handleFolderClick,
  handleBreadcrumbClick,
  handleFileSelect,
  handleMoreClick,
  isFolder
}) => {
  console.log('UploadPopup rendering', { isOpen, getFileIcon, setError });

  if (!isOpen) {
    console.log('UploadPopup not rendering because isOpen prop is false');
    return null;
  }

  const renderItem = (item) => {
    console.log('Rendering item', item);
    const isItemFolder = item.mimeType === 'application/vnd.google-apps.folder';
    const isSelected = selectedFiles.includes(item.id);

    return (
      <div key={item.id} className="folder-item" onClick={() => {
        console.log('Item clicked', { isItemFolder, item });
        isItemFolder ? handleFolderClick(item) : handleFileSelect(item);
      }}>
        <div className="item-content">
          {isItemFolder ? (
            <FolderIcon className="folder-icon" />
          ) : (
            <>
              {isSelected ? (
                <CheckBoxIcon className="checkbox-icon" />
              ) : (
                <CheckBoxOutlineBlankIcon className="checkbox-icon" />
              )}
              <span className="file-icon">{getFileIcon(item.mimeType)}</span>
            </>
          )}
          <span className="item-name">{item.name}</span>
        </div>
      </div>
    );
  };

console.log('All items:', items);
console.log('Current folder:', currentFolder);

const ROOT_FOLDER_ID = '0AJjuiEj-GTr0Uk9PVA';
const displayedItems = items.filter(item => {
  if (currentFolder.id === 'root') {
    return (item.parents && item.parents[0] === ROOT_FOLDER_ID) ||
           (!item.parents) ||
           (item.parents && item.parents.length === 0);
  } else {
    return item.parents && item.parents.length > 0 && item.parents[0] === currentFolder.id;
  }
});

  console.log('Displayed items:', displayedItems);

  return (
    <div className="popup-overlay">
      <div className="popup-content upload-popup">
        <h2>Upload Documents</h2>
        <UploadPopupBreadcrumb
          folderStack={folderStack}
          currentFolder={currentFolder}
          onBreadcrumbClick={handleBreadcrumbClick}
        />
        <div className="folder-list">
          {displayedItems.length > 0 ? (
            displayedItems.map(item => renderItem(item))
          ) : (
            <div className="empty-folder-message">This folder is empty</div>
          )}
        </div>
        <div className="popup-actions">
          <button className="cancel-button" onClick={() => {
            console.log('Cancel button clicked');
            onClose();
          }}>Cancel</button>
          <button 
            className="ok-button" 
            onClick={() => {
              console.log('Upload button clicked', { selectedFiles });
              onUpload(selectedFiles);
            }}
            disabled={selectedFiles.length === 0}
          >
            Upload selected files ({selectedFiles.length})
          </button>
        </div>
      </div>
    </div>
  );
};

export default UploadPopup;