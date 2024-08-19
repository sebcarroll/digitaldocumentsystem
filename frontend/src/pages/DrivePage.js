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
import { useFileSharing } from '../hooks/useFileSharing.js';
import StyledPopup from '../components/drivePage/folderAndRenamePopup.js';
import SharePopup from '../components/drivePage/sharePopup.js';
import MovePopup from '../components/drivePage/movePopup.js';
import { useMovePopup } from '../hooks/useMovePopup';
import ChatInterface from './chatInterface.js';

/**
 * DrivePage component
 * Renders the main drive page with file management functionality
 * @returns {JSX.Element} The rendered DrivePage component
 */
const DrivePage = () => {
  const [driveContent, setDriveContent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSharePopupOpen, setIsSharePopupOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatInitialQuery, setChatInitialQuery] = useState('');
  const navigate = useNavigate();

  /**
   * Fetches drive files from the server
   * @param {string} folderId - The ID of the folder to fetch files from
   */
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

  const { currentFolder, folderStack, handleBackClick, handleBreadcrumbClick, handleFileClick } = useFolderNavigation(setError);
  
  const {
    showActionMenu,
    selectedFiles,
    isRenamePopupOpen,
    fileToRename,
    isFolder,
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
  } = useFileSelection(getDriveFiles, currentFolder, setError);

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
    filesActive, 
    foldersActive, 
    listLayoutActive, 
    handleFilesClick, 
    handleFoldersClick, 
    handleListLayoutClick, 
    handleGridLayoutClick,
  } = useViewOptions();

  const {
    email,
    searchResults,
    peopleWithAccess,
    generalAccess,
    isLoading,
    pendingEmails,
    currentUserRole,
    linkAccessRole,
    currentUserId,
    handleEmailChange,
    handleAddPendingEmail,
    handleRemovePendingEmail,
    handleAccessLevelChange,
    handleRemoveAccess,
    handleGeneralAccessChange,
    handleShareWithPendingEmails,
    handleLinkAccessChange,
    fetchCurrentUserRole,
    fetchPeopleWithAccess,
    isSharingLoading,  
    sharingError,    
  } = useFileSharing(selectedFiles);

  const {
    isOpen: isMovePopupOpen,
    handleOpen: handleOpenMovePopup,
    handleClose: handleCloseMovePopup,
    handleMove: handleMoveFiles,
  } = useMovePopup(selectedFiles, handleMove, setError);

  useEffect(() => {
    getDriveFiles(currentFolder.id);
  }, [currentFolder.id, getDriveFiles]);

  /**
   * Handles opening the chat interface
   * @param {string} [query=''] - The initial query for the chat
   */
  const handleOpenChat = (query = '') => {
    setIsChatOpen(true);
    setChatInitialQuery(query);
  };

  /**
   * Handles closing the chat interface
   */
  const handleCloseChat = () => {
    setIsChatOpen(false);
    setChatInitialQuery('');
  };

  /**
   * Handles the share functionality
   */
  const handleShare = () => {
    if (selectedFiles.length > 0) {
      setIsSharePopupOpen(true);
    } else {
      console.log('No files selected to share');
    }
  };

  /**
   * Handles closing the share popup
   */
  const handleCloseSharePopup = useCallback(() => {
    setIsSharePopupOpen(false);
    setShowActionMenu(false);
    setSelectedFiles([]);
  }, []);

  useEffect(() => {
    console.log('isChatOpen changed:', isChatOpen);
  }, [isChatOpen]);

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

  // Filter drive content based on active view options
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
          filesActive={filesActive}
          foldersActive={foldersActive}
          listLayoutActive={listLayoutActive}
          onFilesClick={handleFilesClick}
          onFoldersClick={handleFoldersClick}
          onListLayoutClick={handleListLayoutClick}
          onGridLayoutClick={handleGridLayoutClick}
          showActionMenu={showActionMenu}
          selectedFiles={selectedFiles}
          onMove={handleOpenMovePopup}
          onDelete={handleDelete}
          onCopyLink={handleCopyLink}
          onRename={openRenamePopup}
          onMakeCopy={handleMakeCopy}
          onCloseActionMenu={handleCloseActionMenu}
          onShare={handleShare}
          isFolder={isFolder}
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
      <StyledPopup
        isOpen={isNewFolderPopupOpen}
        onClose={() => setIsNewFolderPopupOpen(false)}
        onSubmit={handleCreateFolder}
        title="New Folder"
        initialValue="Untitled Folder"
      />
      <StyledPopup
        isOpen={isRenamePopupOpen}
        onClose={() => setIsRenamePopupOpen(false)}
        onSubmit={handleRename}
        title="Rename"
        initialValue={fileToRename ? fileToRename.name : ''}
      />

      {isSharePopupOpen && (
        currentUserRole === null ? (
          <div>Loading user permissions...</div>
        ) : (
          <SharePopup
            isOpen={true}
            onClose={handleCloseSharePopup}
            items={selectedFiles}
            email={email}
            searchResults={searchResults}
            peopleWithAccess={peopleWithAccess}
            generalAccess={generalAccess}
            isLoading={isSharingLoading} 
            error={sharingError}   
            pendingEmails={pendingEmails}
            currentUserRole={currentUserRole}
            linkAccessRole={linkAccessRole}
            onEmailChange={handleEmailChange}
            onAddPendingEmail={handleAddPendingEmail}
            onRemovePendingEmail={handleRemovePendingEmail}
            onAccessLevelChange={handleAccessLevelChange}
            onRemoveAccess={handleRemoveAccess}
            onGeneralAccessChange={handleGeneralAccessChange}
            onCopyLink={handleCopyLink}
            onShareWithPendingEmails={handleShareWithPendingEmails}
            onLinkAccessChange={handleLinkAccessChange}
            currentUserId={currentUserId}
          />
        )
      )}
      <MovePopup
        isOpen={isMovePopupOpen}
        onClose={handleCloseMovePopup}
        onMove={handleMoveFiles}
        selectedFiles={selectedFiles}
        currentFolder={currentFolder}
        folderStack={folderStack}
        folders={driveContent.filter(item => item.mimeType === 'application/vnd.google-apps.folder')}
        handleFolderClick={handleFileClick}
        handleBreadcrumbClick={handleBreadcrumbClick}
      />
      {isChatOpen && (
        <ChatInterface
          initialQuery={chatInitialQuery}
          onClose={handleCloseChat}
          />
        )}
        </div>
  );
};
export default DrivePage;