import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { fetchDriveFiles, checkAuth, openDriveFile, createFolder, uploadFile, uploadFolder, createDoc, createSheet } from '../services/api';
import './DrivePage.css';
import Sidebar from '../components/drivePage/sidebar.js';
import Header from '../components/drivePage/header.js';
import SearchBar from '../components/drivePage/searchbar.js';

const DrivePage = () => {
  const [driveContent, setDriveContent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentFolder, setCurrentFolder] = useState({ id: 'root', name: 'Home' });
  const [folderStack, setFolderStack] = useState([]);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    getDriveFiles(currentFolder.id);
  }, [currentFolder.id, navigate]);

  const getDriveFiles = async (folderId) => {
    try {
      setLoading(true);
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
      setLoading(false);
    }
  };

  const handleFileClick = async (file) => {
    if (file.mimeType === 'application/vnd.google-apps.folder') {
      setFolderStack([...folderStack, currentFolder]);
      setCurrentFolder({ id: file.id, name: file.name });
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

  const handleBreadcrumbClick = (index) => {
    if (index < folderStack.length) {
      const newStack = folderStack.slice(0, index);
      setFolderStack(newStack);
      setCurrentFolder(folderStack[index]);
    }
  };

  const handleCreateFolder = async () => {
    const folderName = prompt("Enter folder name:");
    if (folderName) {
      try {
        await createFolder(currentFolder.id, folderName);
        getDriveFiles(currentFolder.id);
      } catch (error) {
        setError('Failed to create folder.');
      }
    }
  };

  const handleUploadFile = async (file) => {
    if (file) {
      try {
        await uploadFile(currentFolder.id, file);
        getDriveFiles(currentFolder.id);
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
        await uploadFolder(currentFolder.id, files);
        getDriveFiles(currentFolder.id);
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
      const response = await createDoc(currentFolder.id);
      getDriveFiles(currentFolder.id);
      if (response.webViewLink) {
        window.open(response.webViewLink, '_blank', 'noopener,noreferrer');
      }
    } catch (error) {
      setError('Failed to create Google Doc.');
    }
  };
  
  const handleCreateSheet = async () => {
    try {
      const response = await createSheet(currentFolder.id);
      getDriveFiles(currentFolder.id);
      if (response.webViewLink) {
        window.open(response.webViewLink, '_blank', 'noopener,noreferrer');
      }
    } catch (error) {
      setError('Failed to create Google Sheet.');
    }
  };

  const handleSearch = (query) => {
    // Implement your search logic here
    console.log('Searching for:', query);
    // You might want to call an API to search files or filter the current driveContent
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
      <div className="drive-header">
        <Header 
          folderStack={folderStack}
          currentFolder={currentFolder}
          onBreadcrumbClick={handleBreadcrumbClick}
        />
      </div>
      <div className="sidebar">
        <Sidebar
          onCreateFolder={handleCreateFolder}
          onUploadFile={handleUploadFile}
          onUploadFolder={handleUploadFolder}
          onCreateDoc={handleCreateDoc}
          onCreateSheet={handleCreateSheet}
        />
      </div>
      <div className="main-area">
        <div className="search-bar-container">
          <SearchBar onSearch={handleSearch} />
        </div>
        <main className="main-content">
          <div className="drive-content">
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
          </div>
        </main>
      </div>
    </div>
  );
};

export default DrivePage;