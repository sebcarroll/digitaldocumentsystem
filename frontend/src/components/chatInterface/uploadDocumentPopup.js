import React, { useState, useEffect, useCallback } from 'react';
import './uploadDocumentPopup.css';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import FolderIcon from '@mui/icons-material/Folder';
import PeopleIcon from '@mui/icons-material/People';

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
  const getBreadcrumbs = () => {
    let breadcrumbs = [...folderStack, currentFolder].filter(Boolean);
    if (breadcrumbs.length === 0) {
      breadcrumbs = [{ id: 'root', name: 'My Drive' }];
    }
    if (breadcrumbs.length > 3) {
      breadcrumbs = [{ id: '...', name: '...' }, ...breadcrumbs.slice(-2)];
    }

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

  useEffect(() => {
    if (isOpen) {
      console.log("UploadPopup received new props:", { items });
    }
  }, [isOpen, items]);

  const handleFileSelect = useCallback((file) => {
    setSelectedFiles(prevSelected => {
      const isAlreadySelected = prevSelected.some(f => f.id === file.id);
      if (isAlreadySelected) {
        return prevSelected.filter(f => f.id !== file.id);
      } else {
        return [...prevSelected, file];
      }
    });
  }, []);

  if (!isOpen) {
    return null;
  }

  const renderFileIcon = (file) => {
    return (
      <span className="file-type-icon">
        {isFolder(file) ? 
          (file.shared ? <FolderIcon /> : getFileIcon('application/vnd.google-apps.folder')) 
          : getFileIcon(file.mimeType)}
      </span>
    );
  };

  const renderSharingIcon = (file) => {
    if (!isFolder(file) && file.shared) {
      return <PeopleIcon className="file-sharing-icon" />;
    }
    return null;
  };

  const renderItem = (item) => {
    const isItemFolder = isFolder(item);
    const isSelected = selectedFiles.some(f => f.id === item.id);
  
    return (
      <div key={item.id} className="folder-item" onClick={() => {
        if (!isItemFolder) {
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
              {renderFileIcon(item)}
              <span className="file-name-text">{item.name}</span>
              {renderSharingIcon(item)}
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

  const sortByMostRecentlyModified = (a, b) => {
    return new Date(b.modifiedTime) - new Date(a.modifiedTime);
  };

  const filteredAndSortedItems = items
    .filter(item => 
      isFolder(item) || 
      ALLOWED_FORMATS.includes(`.${getFileExtension(item.name)}`) || 
      ALLOWED_FORMATS.includes(item.mimeType)
    )
    .sort(sortByMostRecentlyModified);

  const handleUpload = () => {
    onUpload(selectedFiles);
    setSelectedFiles([]);
    onClose();
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
          {filteredAndSortedItems.length > 0 ? (
            filteredAndSortedItems.map(item => renderItem(item))
          ) : (
            <div className="empty-folder-message">No uploadable files or folders in this location</div>
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