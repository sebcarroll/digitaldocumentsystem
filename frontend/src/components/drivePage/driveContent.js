import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchDriveFiles } from '../../services/drive_service.js';
import { checkAuth } from '../../services/authorisation_service.js';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import './driveContent.css';
import { useFileSelection } from '../../hooks/useFileSelection.js';
import { useFolderNavigation } from '../../hooks/useFolderNavigation.js';

/**
 * DriveContent component
 * Renders the content of the drive, including files and folders
 * @param {Object} props - Component props
 * @param {boolean} props.listLayoutActive - Whether the list layout is active
 * @param {boolean} props.filesActive - Whether files are active in the view
 * @param {boolean} props.foldersActive - Whether folders are active in the view
 * @param {Function} props.setError - Function to set error state
 * @param {Function} props.setIsLoading - Function to set loading state
 * @param {Function} props.onFolderChange - Callback for when the current folder changes
 * @param {Function} props.onSelectionChange - Callback for when the file selection changes
 * @param {Function} props.onActionMenuChange - Callback for when the action menu state changes
 * @returns {JSX.Element} The rendered DriveContent component
 */
const DriveContent = ({ 
  listLayoutActive,
  filesActive,
  foldersActive,
  setError,
  setIsLoading,
  onFolderChange,
  onSelectionChange,
  onActionMenuChange
}) => {
  const [driveContent, setDriveContent] = useState([]);
  const navigate = useNavigate();

  const {
    currentFolder,
    navigateToFolder,
  } = useFolderNavigation();

  /**
   * Fetches drive files from the server
   * @param {string} folderId - The ID of the folder to fetch files from
   */
  const getDriveFiles = useCallback(async (folderId) => {
    try {
      setIsLoading(true);
      const authStatus = await checkAuth();
      if (!authStatus.authenticated) {
        navigate('/login');
        return;
      }

      const content = await fetchDriveFiles(folderId);
      setDriveContent(content.files || []);
    } catch (error) {
      console.error('Failed to fetch drive files:', error);
      setError('Failed to load Google Drive files.');
    } finally {
      setIsLoading(false);
    }
  }, [navigate, setError, setIsLoading]);

  const {
    showActionMenu,
    selectedFiles,
    handleFileSelect,
    handleMoreClick,
  } = useFileSelection(getDriveFiles, currentFolder, setError);

  useEffect(() => {
    getDriveFiles(currentFolder.id);
  }, [currentFolder.id, getDriveFiles]);

  useEffect(() => {
    onFolderChange(currentFolder);
  }, [currentFolder, onFolderChange]);

  useEffect(() => {
    onSelectionChange(selectedFiles);
  }, [selectedFiles, onSelectionChange]);

  useEffect(() => {
    onActionMenuChange(showActionMenu);
  }, [showActionMenu, onActionMenuChange]);

  /**
   * Handles file click event
   * @param {Object} file - The file that was clicked
   */
  const handleFileClick = useCallback((file) => {
    if (file.mimeType === 'application/vnd.google-apps.folder') {
      navigateToFolder(file);
    } else {
      handleFileSelect(file);
    }
  }, [navigateToFolder, handleFileSelect]);

  // Filter the drive content based on active view (files or folders)
  const filteredDriveContent = driveContent.filter(file => {
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
                  onClick={(e) => handleMoreClick(e, file)}
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