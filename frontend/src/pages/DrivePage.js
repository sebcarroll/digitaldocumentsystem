
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchDriveFiles, checkAuth, openDriveFile, createFolder, uploadFile, uploadFolder, createDoc, createSheet } from '../services/api';
import './DrivePage.css';
import NewItemButton from '../components/drivePage/newItemButton.js';

const DrivePage = () => {
  const [driveContent, setDriveContent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentFolder, setCurrentFolder] = useState('root');
  const [folderStack, setFolderStack] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    getDriveFiles(currentFolder);
  }, [currentFolder, navigate]);

  const getDriveFiles = async (folderId) => {
    try {
      setLoading(true);
      const authStatus = await checkAuth();
      if (!authStatus.authenticated) {
        navigate('/login');
        return;
      }

      const content = await fetchDriveFiles(folderId);
      setDriveContent(content.files || []); // Set to empty array if no files
    } catch (error) {
      console.error('Failed to fetch drive files:', error);
      setError('Failed to load Google Drive files.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileClick = async (file) => {
    if (file.mimeType === 'application/vnd.google-apps.folder') {
      setFolderStack([...folderStack, currentFolder]);
      setCurrentFolder(file.id);
    } else {
      try {
        const response = await openDriveFile(file.id);
        window.open(response.webViewLink, '_blank');
      } catch (error) {
        console.error('Failed to open file:', error);
        setError('Failed to open file.');
      }
    }
  };

  const handleBackClick = () => {
    if (folderStack.length > 0) {
      const previousFolder = folderStack.pop();
      setFolderStack([...folderStack]);
      setCurrentFolder(previousFolder);
    }
  };

  const handleCreateFolder = async () => {
    const folderName = prompt("Enter folder name:");
    if (folderName) {
      try {
        await createFolder(currentFolder, folderName);
        getDriveFiles(currentFolder);
      } catch (error) {
        setError('Failed to create folder.');
      }
    }
  };

  const handleUploadFile = async (file) => {
    if (file) {
      try {
        await uploadFile(currentFolder, file);
        getDriveFiles(currentFolder);
      } catch (error) {
        console.error('Failed to upload file:', error);
        setError('Failed to upload file.');
      }
    } else {
      console.error('No file selected');
      setError('No file selected for upload.');
    }
  };

  const handleUploadFolder = async (files) => {
    if (files && files.length > 0) {
      try {
        await uploadFolder(currentFolder, files);
        getDriveFiles(currentFolder);
      } catch (error) {
        console.error('Failed to upload folder:', error);
        setError('Failed to upload folder.');
      }
    } else {
      console.error('No folder selected');
      setError('No folder selected for upload.');
    }
  };

  const handleCreateDoc = async () => {
    try {
      const response = await createDoc(currentFolder);
      getDriveFiles(currentFolder);
      if (response.webViewLink) {
        window.open(response.webViewLink, '_blank', 'noopener,noreferrer');
      }
    } catch (error) {
      setError('Failed to create Google Doc.');
    }
  };
  
  const handleCreateSheet = async () => {
    try {
      const response = await createSheet(currentFolder);
      getDriveFiles(currentFolder);
      if (response.webViewLink) {
        window.open(response.webViewLink, '_blank', 'noopener,noreferrer');
      }
    } catch (error) {
      setError('Failed to create Google Sheet.');
    }
  };

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

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="drive-page">
      <header className="drive-header">
        <h1>My Drive</h1>
        {currentFolder !== 'root' && (
          <button onClick={handleBackClick}>Back</button>
        )}
        <NewItemButton
            onCreateFolder={handleCreateFolder}
            onUploadFile={handleUploadFile}
            onUploadFolder={handleUploadFolder}
            onCreateDoc={handleCreateDoc}
            onCreateSheet={handleCreateSheet}
        />
      </header>
      <main className="drive-content">
        {driveContent.length === 0 ? (
          <p className="no-files">This folder is empty.</p>
        ) : (
          <div className="file-grid">
            {driveContent.map((file) => (
              <div 
                key={file.id} 
                className="file-item"
                onClick={() => handleFileClick(file)}
              >
                <div className="file-icon">{getFileIcon(file.mimeType)}</div>
                <div className="file-name">{file.name}</div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default DrivePage;