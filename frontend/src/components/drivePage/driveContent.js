// src/components/drivePage/DriveContent.js

import React, { useEffect } from 'react';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import './driveContent.css';
import { useDrive } from '../../contexts/driveContext';

/**
 * DriveContent component
 * Renders the content of the drive, including files and folders
 */
const DriveContent = () => {
  const {
    driveFiles,
    currentFolder,
    selectedFiles,
    handleFileClick,
    handleMoreClick,
    getDriveFiles,
    listLayoutActive,
    filesActive,
    foldersActive,
  } = useDrive();

  useEffect(() => {
    getDriveFiles(currentFolder.id);
  }, [currentFolder.id, getDriveFiles]);

  // Filter the drive content based on active view (files or folders)
  const filteredDriveContent = driveFiles.filter(file => {
    const isFolder = file.mimeType === 'application/vnd.google-apps.folder';
    return (filesActive && !isFolder) || (foldersActive && isFolder);
  });

  /**
   * Gets the appropriate icon for a file based on its MIME type
   * @param {string} mimeType - The MIME type of the file
   * @returns {string} The emoji representing the file type
   */
  const getFileIcon = (mimeType) => {
    if (mimeType === 'application/vnd.google-apps.folder') return '📁';
    if (mimeType.includes('image')) return '🖼️';
    if (mimeType.includes('video')) return '🎥';
    if (mimeType.includes('audio')) return '🎵';
    if (mimeType.includes('pdf')) return '📄';
    if (mimeType.includes('spreadsheet')) return '📊';
    if (mimeType.includes('presentation')) return '📽️';
    if (mimeType.includes('document')) return '📝';
    return '📄';
  };

  /**
   * Formats the file size into a human-readable string
   * @param {string|number} size - The file size in bytes
   * @returns {string} The formatted file size
   */
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
              onClick={() => handleFileClick(file)}
            >
              <div className="file-header">
                <span className="file-type-icon">{getFileIcon(file.mimeType)}</span>
                <span className="file-name">{file.name}</span>
                <span className="file-size">{formatFileSize(file.size)}</span>
                <MoreVertIcon 
                  className="more-options"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleMoreClick(e, file);
                  }}
                />
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