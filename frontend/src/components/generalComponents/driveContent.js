import {React, useEffect, useState} from 'react';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import FolderSharedIcon from '@mui/icons-material/FolderShared';
import PeopleIcon from '@mui/icons-material/People';
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
  showActionMenu,
  isFolder,
  getFolderName,
  folderTree
}) => {
  const getReasonSuggested = (file) => {
    const now = new Date();
    const modifiedDate = new Date(file.modifiedTime);
    const viewedDate = new Date(file.viewedByMeTime);
    const sharedDate = new Date(file.sharedWithMeTime);
    const createdDate = new Date(file.createdTime);

    if (now - modifiedDate < 7 * 24 * 60 * 60 * 1000) {
      return `You modified • ${modifiedDate.toLocaleDateString()}`;
    } else if (now - viewedDate < 7 * 24 * 60 * 60 * 1000) {
      return `You opened • ${viewedDate.toLocaleDateString()}`;
    } else if (now - sharedDate < 7 * 24 * 60 * 60 * 1000) {
      return `Shared with you • ${sharedDate.toLocaleDateString()}`;
    } else if (now - createdDate < 7 * 24 * 60 * 60 * 1000) {
      return `You created • ${createdDate.toLocaleDateString()}`;
    } else {
      // If none of the above conditions are met, return the most recent action
      const mostRecentDate = new Date(Math.max(modifiedDate, viewedDate, sharedDate, createdDate));
      if (mostRecentDate.getTime() === modifiedDate.getTime()) {
        return `Modified • ${modifiedDate.toLocaleDateString()}`;
      } else if (mostRecentDate.getTime() === viewedDate.getTime()) {
        return `Opened • ${viewedDate.toLocaleDateString()}`;
      } else if (mostRecentDate.getTime() === sharedDate.getTime()) {
        return `Shared • ${sharedDate.toLocaleDateString()}`;
      } else {
        return `Created • ${createdDate.toLocaleDateString()}`;
      }
    }
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

  const [fileLocations, setFileLocations] = useState({});

  useEffect(() => {
    const locations = {};
    filteredDriveContent.forEach((file) => {
      locations[file.id] = getLocation(file);
    });
    setFileLocations(locations);
  }, [filteredDriveContent, folderTree]);

  const sortByMostRecentInteraction = (a, b) => {
    const getLatestDate = (file) => {
      return new Date(Math.max(
        new Date(file.modifiedTime),
        new Date(file.viewedByMeTime),
        new Date(file.sharedWithMeTime),
        new Date(file.createdTime)
      ));
    };

    return getLatestDate(b) - getLatestDate(a);
  };

  const sortedDriveContent = [...filteredDriveContent].sort(sortByMostRecentInteraction);

  return (
    <div className="drive-content">
      {sortedDriveContent.length === 0 ? (
        <p className="no-files">No items to display.</p>
      ) : (
        <div className={`file-${listLayoutActive ? 'list' : 'grid'}`}>
          {listLayoutActive && (
            <div className="file-list-header">
              <span>Name</span>
              <span>Reason suggested</span>
              <span>Owner</span>
              <span>Location</span>
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
                  <div className="file-reason">{getReasonSuggested(file)}</div>
                  <div className="file-owner">{getOwner(file)}</div>
                  <div className="file-location">{fileLocations[file.id] || 'Loading...'}</div>
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
                            e.target.onerror = null; // prevents looping
                            e.target.style.display = 'none'; // hide the img element
                            e.target.nextElementSibling.style.display = 'flex'; // show the icon
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