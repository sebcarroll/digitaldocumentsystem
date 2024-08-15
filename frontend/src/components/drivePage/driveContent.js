import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchDriveFiles } from '../../services/drive_service.js';
import { checkAuth } from '../../services/authorisation_service.js';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import './driveContent.css';

/**
 * DriveContent component
 * Renders the content of the drive, including files and folders
 * @param {Object} props - Component props
 * @param {Object} props.currentFolder - The current folder being displayed
 * @param {boolean} props.listLayoutActive - Whether the list layout is active
 * @param {Function} props.handleFileClick - Function to handle file click
 * @param {Function} props.handleFileSelect - Function to handle file selection
 * @param {Function} props.handleMoreClick - Function to handle more options click
 * @param {Array} props.selectedFiles - Array of selected files
 * @param {boolean} props.showActionMenu - Whether to show the action menu
 * @param {boolean} props.filesActive - Whether files are active in the view
 * @param {boolean} props.foldersActive - Whether folders are active in the view
 * @param {Function} props.setError - Function to set error state
 * @param {Function} props.setIsLoading - Function to set loading state
 * @returns {JSX.Element} The rendered DriveContent component
 */
const DriveContent = ({ 
  currentFolder,
  listLayoutActive, 
  handleFileClick, 
  handleFileSelect,
  handleMoreClick, 
  selectedFiles,
  showActionMenu,
  filesActive,
  foldersActive,
  setError,
  setIsLoading
}) => {
  const [driveContent, setDriveContent] = useState([]);
  const navigate = useNavigate();

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

  useEffect(() => {
    getDriveFiles(currentFolder.id);
  }, [currentFolder.id, getDriveFiles]);

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