import React from 'react';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import FolderSharedIcon from '@mui/icons-material/FolderShared';
import PeopleIcon from '@mui/icons-material/People';
import '../generalComponents/driveContent.css';

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
  showActionMenu,
  isFolder
}) => {
  const getOwner = (file) => {
    return file.owners && file.owners.length > 0 ? file.owners[0].displayName : "Unknown";
  };

  const renderFileIcon = (file) => {
    return (
      <span className="file-type-icon">
        {isFolder(file) ? 
          (file.shared ? <FolderSharedIcon /> : getFileIcon(file.mimeType)) 
          : getFileIcon(file.mimeType)}
      </span>
    );
  };

  const formatSharedDate = (file) => {
    const sharedDate = new Date(file.sharedWithMeTime);
    const createdDate = new Date(file.createdTime);
  
    if (!isNaN(sharedDate.getTime()) && sharedDate.getFullYear() !== 1970) {
      return `Shared • ${sharedDate.toLocaleDateString()}`;
    } else if (!isNaN(createdDate.getTime())) {
      return `Created • ${createdDate.toLocaleDateString()}`;
    } else {
      return 'Date unknown';
    }
  };
  const sharedContent = filteredDriveContent.filter(file => 
    file.shared && file.owners && file.owners[0].me !== true
  );

  const sortedSharedContent = [...sharedContent].sort((a, b) => {
    const dateA = new Date(a.sharedWithMeTime).getFullYear() !== 1970 ? 
      new Date(a.sharedWithMeTime) : new Date(a.createdTime);
    const dateB = new Date(b.sharedWithMeTime).getFullYear() !== 1970 ? 
      new Date(b.sharedWithMeTime) : new Date(b.createdTime);
    return dateB - dateA;
  });

  return (
    <div className="drive-content">
      {sortedSharedContent.length === 0 ? (
        <p className="no-files">No shared items to display.</p>
      ) : (
        <div className={`file-${listLayoutActive ? 'list' : 'grid'}`}>
          {listLayoutActive && (
            <div className="file-list-header">
              <span>Name</span>
              <span>Shared by</span>
              <span>Date</span>
            </div>
          )}
          {sortedSharedContent.map((file) => (
            <div 
              key={file.id} 
              className={`file-item ${selectedFiles.some(f => f.id === file.id) ? 'selected' : ''}`}
              onClick={() => showActionMenu ? handleFileSelect(file) : handleFileClick(file)}
            >
              {listLayoutActive ? (
                <>
                  <div className="file-name">
                    {renderFileIcon(file)}
                    <span className="file-name-text">{file.name}</span>
                    <PeopleIcon className="file-sharing-icon" />
                  </div>
                  <div className="file-owner">{getOwner(file)}</div>
                  <div className="file-modified">{formatSharedDate(file)}</div>
                  <div className="more-options">
                    <MoreVertIcon onClick={(e) => {
                      e.stopPropagation();
                      handleMoreClick(e, file);
                    }} />
                  </div>
                </>
              ) : (
                <>
                  <div className="file-header">
                    <div className="file-name">
                      {renderFileIcon(file)}
                      <span className="file-name-text">{file.name}</span>
                    </div>
                    <div className="file-icons">
                      <PeopleIcon className="file-sharing-icon" />
                      {!isFolder(file) && (
                        <span className="file-size">{formatFileSize(file.size)}</span>
                      )}
                      <div className="more-options">
                        <MoreVertIcon onClick={(e) => {
                          e.stopPropagation();
                          handleMoreClick(e, file);
                        }} />
                      </div>
                    </div>
                  </div>
                  <div className="file-thumbnail">
                    {file.hasThumbnail ? (
                      <img 
                        src={file.thumbnailLink} 
                        alt={file.name} 
                        onError={(e) => {
                          e.target.onerror = null; 
                          e.target.style.display = 'none'; 
                          e.target.nextElementSibling.style.display = 'flex'; 
                        }}
                      />
                    ) : null}
                    <span 
                      className="large-file-icon" 
                      style={{display: file.hasThumbnail ? 'none' : 'flex'}}
                    >
                      {renderFileIcon(file)}
                    </span>
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DriveContent;