import React, { useState, useCallback, useEffect } from 'react';
import './DrivePage.css';
import '../services/drive_service.js';
import '../services/authorisation_service.js';
import '../services/permissions_and_sharing_service.js'
import '../services/users_service.js'
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
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSharePopupOpen, setIsSharePopupOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false); 
  const [chatInitialQuery, setChatInitialQuery] = useState('');

  const { currentFolder,
    folderStack,
    handleBackClick,
    handleBreadcrumbClick,
    handleFileClick } = useFolderNavigation();
  
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
  } = useFileSelection(currentFolder, setError, setIsLoading);

  const {
    isNewFolderPopupOpen,
    openCreateFolderPopup,
    handleCreateFolder,
    handleUploadFile,
    handleUploadFolder,
    handleCreateDoc,
    handleCreateSheet,
    setIsNewFolderPopupOpen
  } = useFileOperations(currentFolder, setError, setIsLoading);

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
    handleLinkAccessRoleChange,
    fetchCurrentUserRole,
    fetchPeopleWithAccess,
    isSharingLoading,  
    sharingError,    
  } = useFileSharing(selectedFiles, setError, setIsLoading);

  const {
    isOpen: isMovePopupOpen,
    handleOpen: handleOpenMovePopup,
    handleClose: handleCloseMovePopup,
    handleMove: handleMoveFiles,
  } = useMovePopup(selectedFiles, handleMove, setError, setIsLoading);

  /**
   * Handles opening the chat interface
   * @param {string} query - The initial query for the chat
   */
  const handleOpenChat = useCallback((query) => {
    setIsChatOpen(true);
    setChatInitialQuery(query);
  }, []);

  /**
   * Handles closing the chat interface
   */
  const handleCloseChat = useCallback(() => {
    setIsChatOpen(false);
    setChatInitialQuery('');
  }, []);

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
  }, [setShowActionMenu, setSelectedFiles]);

  useEffect(() => {
    console.log('isChatOpen changed:', isChatOpen);
  }, [isChatOpen]);

  if (error) return <div className="error">{error}</div>;

  return (
    <div className="drive-page">
      {isLoading && <div className="loading-overlay">Loading...</div>}
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
            currentFolder={currentFolder}
            listLayoutActive={listLayoutActive}
            handleFileClick={handleFileClick}
            handleFileSelect={handleFileSelect}
            handleMoreClick={handleMoreClick}
            selectedFiles={selectedFiles}
            showActionMenu={showActionMenu}
            filesActive={filesActive}
            foldersActive={foldersActive}
            setError={setError}
            setIsLoading={setIsLoading}
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
            onLinkAccessChange={handleLinkAccessRoleChange}
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
        handleFolderClick={handleFileClick}
        handleBreadcrumbClick={handleBreadcrumbClick}
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