import React from 'react';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import FolderSharedIcon from '@mui/icons-material/FolderShared';
import PeopleIcon from '@mui/icons-material/People';
import '../generalComponents/driveContent.css';

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

  const renderSharingIcon = (file) => {
    if (!isFolder(file) && file.shared) {
      return <PeopleIcon className="file-sharing-icon" />;
    }
    return null;
  };

  const sortByMostRecentlyModified = (a, b) => {
    return new Date(b.modifiedTime) - new Date(a.modifiedTime);
  };

  const sortedDriveContent = [...filteredDriveContent].sort(sortByMostRecentlyModified);

  return (
    <div className="drive-content">
      {sortedDriveContent.length === 0 ? (
        <p className="no-files">No items to display.</p>
      ) : (
        <div className={`file-${listLayoutActive ? 'list' : 'grid'}`}>
          {listLayoutActive && (
            <div className="file-list-header">
              <span>Name</span>
              <span>Owner</span>
              <span>Last Modified</span>
              <span>File Size</span>
              <span></span>
            </div>
          )}
          {sortedDriveContent.map((file) => (
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
                    {renderSharingIcon(file)}
                  </div>
                  <div className="file-owner">{getOwner(file)}</div>
                  <div className="file-modified">{`Modified • ${new Date(file.modifiedTime).toLocaleDateString()}`}</div>
                  <div className="file-size">{isFolder(file) ? '-' : formatFileSize(file.size)}</div>
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
                      {renderSharingIcon(file)}
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