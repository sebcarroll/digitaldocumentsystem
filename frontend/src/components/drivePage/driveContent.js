// DriveContent.js
import React from 'react';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import './driveContent.css';

/**
 * Formats the file size into a human-readable string
 * @param {string|number} size - The file size in bytes
 * @returns {string} The formatted file size
 */
const formatFileSize = (size) => {
  if (size == null || isNaN(size)) {
    return 'N/A'; // Return 'N/A' for null, undefined, or NaN values
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

const DriveContent = ({ 
  filteredDriveContent, 
  listLayoutActive, 
  handleFileClick, 
  handleFileSelect,
  handleMoreClick, 
  getFileIcon,
  selectedFiles,
  showActionMenu
}) => {
  return (
    <div className="drive-content">
      {filteredDriveContent.length === 0 ? (
        <p className="no-files">No items to display.</p>
      ) : (
        <div className={`file-${listLayoutActive ? 'list' : 'grid'}`}>
          {filteredDriveContent.map((file) => (
            <div 
              key={file.id} 
              className={`file-item ${selectedFiles.some(f => f.id === file.id) ? 'selected' : ''}`}
              onClick={() => showActionMenu ? handleFileSelect(file) : handleFileClick(file)}
            >
              <div className="file-header">
                <span className="file-type-icon">{getFileIcon(file.mimeType)}</span>
                <span className="file-name">{file.name}</span>
                <span className="file-size">{formatFileSize(file.size)}</span>
                <div className="file-actions">
                  <MoreVertIcon onClick={(e) => {
                    e.stopPropagation();
                    handleMoreClick(e, file);
                  }} />
                </div>
              </div>
              <div className="file-thumbnail">
                {file.hasThumbnail ? (
                  <img src={file.thumbnailLink} alt={file.name} />
                ) : (
                  <span className="default-icon">{getFileIcon(file.mimeType)}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DriveContent;