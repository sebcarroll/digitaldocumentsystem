import React, { useState, useEffect, useCallback } from 'react';
import './uploadDocumentPopup.css';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import FolderIcon from '@mui/icons-material/Folder';
import PeopleIcon from '@mui/icons-material/People';

// Format file size function
const formatFileSize = (size) => {
  if (size == null || isNaN(size)) {
    return 'N/A';
  }

  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let unitIndex = 0;
  let fileSize = Number(size);

  if (fileSize === 0) {
    return '0 B';
  }

  while (fileSize >= 1024 && unitIndex < units.length - 1) {
    fileSize /= 1024;
    unitIndex++;
  }

  return `${fileSize.toFixed(1)} ${units[unitIndex]}`;
};

const ALLOWED_FORMATS = [
  '.docx', '.xlsx', '.txt', '.csv', '.pdf',
  'application/vnd.google-apps.document',
  'application/vnd.google-apps.spreadsheet'
];

const getFileExtension = (filename) => {
  return filename.slice((filename.lastIndexOf(".") - 1 >>> 0) + 2).toLowerCase();
};

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
  currentFolder,
  folderStack,
  items,
  handleFolderClick,
  handleBreadcrumbClick,
  handleMoreClick,
  isFolder
}) => {
  const [selectedFiles, setSelectedFiles] = useState([]);

  console.log('UploadPopup rendering', { isOpen, getFileIcon, setError });

  useEffect(() => {
    if (isOpen) {
      console.log("UploadPopup received new props:", { items });
    }
  }, [isOpen, items]);

  const handleFileSelect = useCallback((file) => {
    console.log("handleFileSelect called with file:", file);
    setSelectedFiles(prevSelected => {
      const isAlreadySelected = prevSelected.some(f => f.id === file.id);
      if (isAlreadySelected) {
        console.log("Removing file from selection:", file.name);
        return prevSelected.filter(f => f.id !== file.id);
      } else {
        console.log("Adding file to selection:", file.name);
        return [...prevSelected, file];
      }
    });
  }, []);

  useEffect(() => {
    console.log("Selected files updated in UploadPopup:", selectedFiles);
  }, [selectedFiles]);

  if (!isOpen) {
    console.log('UploadPopup not rendering because isOpen prop is false');
    return null;
  }

  const renderItem = (item) => {
    console.log('Rendering item', item);
    const isItemFolder = item.mimeType === 'application/vnd.google-apps.folder';
    const isSelected = selectedFiles.some(f => f.id === item.id);
  
    return (
      <div key={item.id} className="folder-item" onClick={() => {
        console.log('Item clicked', { isItemFolder, item });
        if (!isItemFolder) {
          console.log('Calling handleFileSelect for non-folder item');
          handleFileSelect(item);
        } else {
          handleFolderClick(item);
        }
      }}>
        <div className="item-content">
          {!isItemFolder && (
            <div className="checkbox-container" onClick={(e) => e.stopPropagation()}>
              {isSelected ? (
                <CheckBoxIcon className="checkbox-icon" />
              ) : (
                <CheckBoxOutlineBlankIcon className="checkbox-icon" />
              )}
            </div>
          )}
          <div className="file-header">
            <div className="file-name">
              <span className="file-type-icon">
                {isItemFolder ? <FolderIcon /> : getFileIcon(item.mimeType)}
              </span>
              <span className="file-name-text">{item.name}</span>
              {item.shared && <PeopleIcon className="file-sharing-icon" />}
            </div>
            <div className="file-info">
              {!isItemFolder && (
                <span className="file-size">{formatFileSize(item.size)}</span>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  console.log('All items:', items);
  console.log('Current folder:', currentFolder);

  const ROOT_FOLDER_ID = '0AJjuiEj-GTr0Uk9PVA';
  const displayedItems = items.filter(item => {
    const isInCurrentFolder = (currentFolder.id === 'root' && 
      ((item.parents && item.parents[0] === ROOT_FOLDER_ID) ||
       (!item.parents) ||
       (item.parents && item.parents.length === 0))) ||
      (item.parents && item.parents.length > 0 && item.parents[0] === currentFolder.id);

    const isFolder = item.mimeType === 'application/vnd.google-apps.folder';
    const hasAllowedFormat = ALLOWED_FORMATS.includes(`.${getFileExtension(item.name)}`) || 
                             ALLOWED_FORMATS.includes(item.mimeType);

    return isInCurrentFolder && (isFolder || hasAllowedFormat);
  });

  console.log('Displayed items:', displayedItems);

  const handleUpload = () => {
    console.log('Upload button clicked', { selectedFiles });
    onUpload(selectedFiles);
    setSelectedFiles([]); // Reset selected files
    onClose(); // Close the popup
  };

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
          <button className="cancel-button" onClick={onClose}>Cancel</button>
          <button 
            className="ok-button" 
            onClick={handleUpload}
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