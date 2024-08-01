import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchDriveFiles, checkAuth } from '../services/api';
import './DrivePage.css';
import Sidebar from '../components/drivePage/sidebar.js';
import Header from '../components/drivePage/header.js';
import SearchBar from '../components/drivePage/searchbar.js';
import ViewOptions from '../components/drivePage/viewOptions.js';
import DriveContent from '../components/drivePage/driveContent.js';
import { useFileOperations } from '../hooks/useFileOperations.js';
import { useFileSelection } from '../hooks/useFileSelection.js';
import { useViewOptions } from '../hooks/useViewOptions.js';
import { useFolderNavigation } from '../hooks/useFolderNavigation.js';

const DrivePage = () => {
  const [driveContent, setDriveContent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const getDriveFiles = useCallback(async (folderId) => {
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
  }, [navigate]);

  const { currentFolder,
    folderStack,
    handleBackClick,
     handleBreadcrumbClick,
    handleFileClick
     } = useFolderNavigation();
  
  const { 
    showActionMenu, 
    selectedFiles, 
    handleFileSelect, 
    handleMove, 
    handleDelete, 
    handleCopyLink, 
    handleRename, 
    handleMakeCopy, 
    handleCloseActionMenu,
    handleMoreClick,
  } = useFileSelection(getDriveFiles, currentFolder, setError);

  const { 
    filesActive, 
    foldersActive, 
    listLayoutActive, 
    showCover,
    coverTop,
    handleFilesClick, 
    handleFoldersClick, 
    handleListLayoutClick, 
    handleGridLayoutClick,
  } = useViewOptions();

  const { 
    handleCreateFolder,
    handleUploadFile,
    handleUploadFolder,
    handleCreateDoc,
    handleCreateSheet
   } = useFileOperations(currentFolder, getDriveFiles, setError);

  useEffect(() => {
    getDriveFiles(currentFolder.id);
  }, [currentFolder.id, getDriveFiles]);

  const handleSearch = (query) => {
    console.log('Searching for:', query);
    // Implement your search logic here
  };

  const handleShare = () => {
    console.log('Share functionality not implemented yet');
    // Implement your share logic here
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

  const filteredDriveContent = driveContent.filter(file => {
    const isFolder = file.mimeType === 'application/vnd.google-apps.folder';
    return (filesActive && !isFolder) || (foldersActive && isFolder);
  });

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
        <div 
          className={`view-options-cover ${showCover ? 'visible' : ''}`}
          style={{ top: `${coverTop}px` }}
        >
        </div>
        <div className="view-options-container">
        <ViewOptions
          filesActive={filesActive}
          foldersActive={foldersActive}
          listLayoutActive={listLayoutActive}
          onFilesClick={handleFilesClick}
          onFoldersClick={handleFoldersClick}
          onListLayoutClick={handleListLayoutClick}
          onGridLayoutClick={handleGridLayoutClick}
          showActionMenu={showActionMenu}
          selectedFiles={selectedFiles}
          onMove={handleMove}
          onDelete={handleDelete}
          onCopyLink={handleCopyLink}
          onRename={handleRename}
          onMakeCopy={handleMakeCopy}
          onCloseActionMenu={handleCloseActionMenu}
          onShare={handleShare}
        />
      </div>
      <main className="main-content">
      <DriveContent 
        filteredDriveContent={filteredDriveContent}
        listLayoutActive={listLayoutActive}
        handleFileClick={handleFileClick}
        handleFileSelect={handleFileSelect}
        handleMoreClick={handleMoreClick}
        getFileIcon={getFileIcon}
        selectedFiles={selectedFiles}
        showActionMenu={showActionMenu}
      />
      </main>
      </div>
    </div>
  );
};

export default DrivePage;