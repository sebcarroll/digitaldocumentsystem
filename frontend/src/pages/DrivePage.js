/**
 * DrivePage.js
 * This component renders the main Drive page, including the file list and various popups.
 */

import React, { useState, useCallback } from 'react';
import './DrivePage.css';
import Sidebar from '../components/drivePage/sidebar.js';
import Header from '../components/drivePage/header.js';
import SearchBar from '../components/drivePage/searchbar.js';
import ViewOptions from '../components/drivePage/viewOptions.js';
import DriveContent from '../components/drivePage/driveContent.js';
import FolderAndRenamePopup from '../components/drivePage/folderAndRenamePopup.js';
import SharePopup from '../components/drivePage/sharePopup.js';
import MovePopup from '../components/drivePage/movePopup.js';
import ChatInterface from './chatInterface.js';
import { useFileOperations } from '../hooks/useFileOperations.js';
import { useFileSelection } from '../hooks/useFileSelection.js';
import { useFolderNavigation } from '../hooks/useFolderNavigation.js';

/**
 * DrivePage component
 * @returns {React.ReactElement} DrivePage component
 */
const DrivePage = () => {
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSharePopupOpen, setIsSharePopupOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatInitialQuery, setChatInitialQuery] = useState('');

  const { 
    currentFolder, 
    folderStack, 
    navigateToFolder, 
    handleBackClick, 
    handleBreadcrumbClick 
  } = useFolderNavigation();

  const { 
    isNewFolderPopupOpen, 
    openCreateFolderPopup, 
    handleCreateFolder, 
    handleUploadFile, 
    handleUploadFolder, 
    handleCreateDoc, 
    handleCreateSheet, 
    setIsNewFolderPopupOpen 
  } = useFileOperations(currentFolder, getDriveFiles, setError);

  const {
    showActionMenu,
    selectedFiles,
    isRenamePopupOpen,
    fileToRename,
    handleFileSelect,
    handleMove,
    handleDelete,
    handleCopyLink,
    openRenamePopup,
    handleRename,
    handleMakeCopy,
    handleCloseActionMenu,
    handleMoreClick,
    setShowActionMenu,
    setIsRenamePopupOpen,
    setSelectedFiles,
    isFolder
  } = useFileSelection(getDriveFiles, currentFolder, setError);

  const handleOpenChat = useCallback((query) => {
    setIsChatOpen(true);
    setChatInitialQuery(query);
  }, []);

  const handleCloseChat = useCallback(() => {
    setIsChatOpen(false);
    setChatInitialQuery('');
  }, []);

  const handleShare = useCallback(() => {
    if (selectedFiles.length > 0) {
      setIsSharePopupOpen(true);
    } else {
      console.log('No files selected to share');
    }
  }, [selectedFiles]);

  const handleCloseSharePopup = useCallback(() => {
    setIsSharePopupOpen(false);
    setShowActionMenu(false);
    setSelectedFiles([]);
  }, [setShowActionMenu, setSelectedFiles]);

  if (error) return <div className="error">{error}</div>;

  return (
    <div className="drive-page">
      {isLoading && <div className="loading-overlay">Loading...</div>}
      <div className="drive-header">
        <Header 
          currentFolder={currentFolder}
          folderStack={folderStack}
          onBreadcrumbClick={handleBreadcrumbClick}
        />
      </div>
      <div className="sidebar">
        <Sidebar
          onCreateFolder={openCreateFolderPopup}
          onUploadFile={handleUploadFile}
          onUploadFolder={handleUploadFolder}
          onCreateDoc={handleCreateDoc}
          onCreateSheet={handleCreateSheet}
        />
      </div>
      <div className="main-area">
        <div className="search-bar-container">
          <SearchBar onOpenChat={handleOpenChat} />
        </div>
        <div className="view-options-container">
          <ViewOptions
            showActionMenu={showActionMenu}
            selectedFiles={selectedFiles}
            onShare={handleShare}
            onMove={() => handleMove(selectedFiles)}
            onDelete={handleDelete}
            onMakeCopy={handleMakeCopy}
            onRename={openRenamePopup}
          />
        </div>
        <main className="main-content">
          <DriveContent 
            currentFolder={currentFolder}
            onFolderChange={navigateToFolder}
            onSelectionChange={setSelectedFiles}
            onActionMenuChange={setShowActionMenu}
            onFileSelect={handleFileSelect}
            onMoreClick={handleMoreClick}
          />
        </main>
      </div>
      <FolderAndRenamePopup
        isOpen={isNewFolderPopupOpen}
        onClose={() => setIsNewFolderPopupOpen(false)}
        onSubmit={handleCreateFolder}
        title="New Folder"
        initialValue="Untitled Folder"
      />
      <FolderAndRenamePopup
        isOpen={isRenamePopupOpen}
        onClose={() => setIsRenamePopupOpen(false)}
        onSubmit={handleRename}
        title={`Rename ${isFolder ? 'Folder' : 'File'}`}
        initialValue={fileToRename?.name || ''}
      />
      {isSharePopupOpen && (
        <SharePopup
          items={selectedFiles}
          onClose={handleCloseSharePopup}
        />
      )}
      <MovePopup
        initialSelectedFiles={selectedFiles}
        onMoveConfirm={handleMove}
        setError={setError}
      />
      {isChatOpen && (
        <div className="chat-interface-container">
          <ChatInterface
            initialQuery={chatInitialQuery}
            onClose={handleCloseChat}
          />
        </div>
      )}
    </div>
  );
};

export default DrivePage;