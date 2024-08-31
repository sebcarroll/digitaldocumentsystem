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
  isFolder,
  getFolderName,
  folderTree,
  isRecentPage
}) => {
  const getLastInteractionTime = (file) => {
    const dates = [
      new Date(file.modifiedTime),
      new Date(file.viewedByMeTime),
      new Date(file.sharedWithMeTime),
      new Date(file.createdTime)
    ];
    return new Date(Math.max(...dates));
  };

  const getTimeCategory = (date) => {
    const now = new Date();
    const diff = now - date;
    const dayInMs = 24 * 60 * 60 * 1000;

    if (diff < dayInMs) return "Today";
    if (diff < 7 * dayInMs) return "Earlier this week";
    if (diff < 30 * dayInMs) return "Earlier this month";
    if (diff < 365 * dayInMs) return "Earlier this year";
    return "Older";
  };

  const getOwner = (file) => {
    return file.owners && file.owners.length > 0 ? file.owners[0].displayName : "Unknown";
  };

  const getLocation = (file) => {
    if (!file.parents || file.parents.length === 0) {
      return file.shared ? "Shared with me" : "My Drive";
    }
    const parentId = file.parents[0];
    const findFolder = (folders) => {
      for (let folder of folders) {
        if (folder.id === parentId) {
          return folder.name;
        }
        if (folder.children) {
          const result = findFolder(folder.children);
          if (result) return result;
        }
      }
      return null;
    };
    const folderName = findFolder(folderTree);
    return folderName || "My Drive";
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

  const sortedDriveContent = [...filteredDriveContent].sort((a, b) => 
    getLastInteractionTime(b) - getLastInteractionTime(a)
  );

  const groupedContent = sortedDriveContent.reduce((acc, file) => {
    const category = getTimeCategory(getLastInteractionTime(file));
    if (!acc[category]) acc[category] = [];
    acc[category].push(file);
    return acc;
  }, {});

  return (
    <div className={`drive-content ${isRecentPage ? 'recent-page' : ''}`}>
      {Object.keys(groupedContent).length === 0 ? (
        <p className="no-files">No items to display.</p>
      ) : (
        <div className={`file-container ${listLayoutActive ? 'list-view' : 'grid-view'}`}>
          {Object.entries(groupedContent).map(([category, files]) => (
            <React.Fragment key={category}>
              <div className="time-category">{category}</div>
              <div className={`file-${listLayoutActive ? 'list' : 'grid'}`}>
                {listLayoutActive && (
                  <div className="file-list-header">
                    <span>Name</span>
                    <span>Last interaction</span>
                    <span>File size</span>
                    <span></span>
                  </div>
                )}
                {files.map((file) => (
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
                        <div className="file-last-interaction">
                          {getLastInteractionTime(file).toLocaleString()}
                        </div>
                        <div className="file-size">
                          {isFolder(file) ? 'Folder' : formatFileSize(file.size)}
                        </div>
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
            </React.Fragment>
          ))}
        </div>
      )}
    </div>
  );
};

export default DriveContent;