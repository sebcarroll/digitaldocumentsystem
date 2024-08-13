import React from 'react';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import './driveContent.css';

const DriveContent = ({ 
  driveContent, 
  listLayoutActive, 
  handleFileClick, 
  handleFileSelect,
  handleMoreClick, 
  selectedFiles,
  showActionMenu,
  filesActive,
  foldersActive
}) => {
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

  const filteredDriveContent = driveContent.filter(file => {
    const isFolder = file.mimeType === 'application/vnd.google-apps.folder';
    return (filesActive && !isFolder) || (foldersActive && isFolder);
  });

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
              <div>
                <div className="file-icon">{getFileIcon(file.mimeType)}</div>
                <div className="file-name">{file.name}</div>
              </div>
              <div className="file-actions">
                <MoreVertIcon onClick={(e) => {
                  e.stopPropagation();
                  handleMoreClick(e, file);
                }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DriveContent;