import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { checkAuth, fetchUserInfo, fetchFolderDetails, fetchFolderTree } from '../services/api';
import './DrivePage.css';
import Sidebar from '../components/generalComponents/sidebar.js';
import Header from '../components/generalComponents/header.js';
import SearchBar from '../components/generalComponents/searchbar.js';
import ViewOptions from '../components/generalComponents/viewOptions.js';
import { useFileOperations } from '../hooks/useFileOperations.js';
import { useFileSelection } from '../hooks/useFileSelection.js';
import { useViewOptions } from '../hooks/useViewOptions.js';
import { useFolderNavigation } from '../hooks/useFolderNavigation.js';
import { useFileSharing } from '../hooks/useFileSharing.js';
import StyledPopup from '../components/generalComponents/folderAndRenamePopup.js';
import SharePopup from '../components/generalComponents/sharePopup.js';
import MovePopup from '../components/generalComponents/movePopup.js';
import { useMovePopup } from '../hooks/useMovePopup';
import ChatInterface from './chatInterface.js';

/**
 * BaseDrivePage component
 * Renders the main drive page with file management functionality
 * @param {React.Component} DriveContent - The component to render the drive content
 * @param {Function} fetchFiles - The function to fetch files for this specific page
 * @returns {JSX.Element} The rendered BaseDrivePage component
 */
const BaseDrivePage = ({ DriveContent, fetchFiles }) => {
  const [driveContent, setDriveContent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSharePopupOpen, setIsSharePopupOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatInitialQuery, setChatInitialQuery] = useState('');
  const [folderNames, setFolderNames] = useState({});
  const [folderTree, setFolderTree] = useState([]);
  const [userEmail, setUserEmail] = useState('');
  const [userName, setUserName] = useState('');
  const [isUploadPopupOpen, setIsUploadPopupOpen] = useState(false);
  const navigate = useNavigate();

  const { currentFolder, folderStack, handleBackClick, handleBreadcrumbClick, handleFileClick } = useFolderNavigation(setError);

  const getDriveFiles = useCallback(async (folderId) => {
    try {
      setLoading(true);
      const authStatus = await checkAuth();
      if (!authStatus.authenticated) {
        navigate('/login');
        return;
      }

      const content = await fetchFiles(folderId);
      setDriveContent(content.files || []);
    } catch (error) {
      console.error('Failed to fetch drive files:', error);
      setError('Failed to load Google Drive files.');
    } finally {
      setLoading(false);
    }
  }, [navigate, fetchFiles]);

  const getFolderTree = useCallback(async () => {
    try {
      console.log('Initiating folder tree fetch...');
      const data = await fetchFolderTree();
      console.log('Folder tree fetch successful:', data);
      setFolderTree(data.folderTree);
    } catch (error) {
      console.error('Failed to fetch folder tree:', error);
      setError(`Failed to load folder structure: ${error.message}`);
    }
  }, []);

  useEffect(() => {
    const checkAuthAndFetchUserInfo = async () => {
      try {
        const authStatus = await checkAuth();
        if (authStatus.authenticated) {
          const userInfo = await fetchUserInfo();
          setUserEmail(userInfo.email);
          setUserName(userInfo.name);
        } else {
          navigate('/login');
        }
      } catch (error) {
        console.error('Failed to fetch user info:', error);
        setError('Failed to load user information.');
      }
    };

    checkAuthAndFetchUserInfo();
  }, [navigate]);

  useEffect(() => {
    console.log('BaseDrivePage mounted or updated');
    if (currentFolder && currentFolder.id) {
      getDriveFiles(currentFolder.id);
    }
    getFolderTree();
  }, [currentFolder, getDriveFiles, getFolderTree]);

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

  const handleMoveComplete = useCallback((destinationFolder, newFolderStack) => {
    setShowActionMenu(false);
    setSelectedFiles([]);
    handleFileClick(destinationFolder, newFolderStack);
  }, [setShowActionMenu, setSelectedFiles, handleFileClick]);

  const {
    isOpen: isMovePopupOpen,
    selectedFiles: moveSelectedFiles,
    currentFolder: moveCurrentFolder,
    folderStack: moveFolderStack,
    folders: moveFolders,
    handleOpen: handleOpenMovePopup,
    handleClose: handleCloseMovePopup,
    handleFolderClick: handleMoveFolderClick,
    handleBreadcrumbClick: handleMoveBreadcrumbClick,
    handleMove: handleMoveFiles,
  } = useMovePopup(selectedFiles, setError, handleMoveComplete);

  const handleOpenChat = useCallback((query = '', openUploadMenu = false) => {
    console.log("handleOpenChat called in BaseDrivePage", { query, openUploadMenu });
    setIsChatOpen(true);
    setChatInitialQuery(query);
    if (openUploadMenu) {
      setIsUploadPopupOpen(true);
    }
  }, []);

  const handleCloseChat = useCallback(() => {
    setIsChatOpen(false);
    setChatInitialQuery('');
    setIsUploadPopupOpen(false);
  }, []);

  const handleShare = () => {
    if (selectedFiles.length > 0) {
      setIsSharePopupOpen(true);
    } else {
      console.log('No files selected to share');
    }
  };

  const handleCloseSharePopup = useCallback(() => {
    setIsSharePopupOpen(false);
    setShowActionMenu(false);
    setSelectedFiles([]);
  }, []);

  useEffect(() => {
    console.log('isChatOpen changed:', isChatOpen);
  }, [isChatOpen]);

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

  const getFolderName = useCallback(async (folderId) => {
    if (folderNames[folderId]) {
      return folderNames[folderId];
    }
  
    try {
      const response = await fetchFolderDetails(folderId);
      const name = response.name;
      setFolderNames(prev => ({ ...prev, [folderId]: name }));
      return name;
    } catch (error) {
      console.error('Error fetching folder name:', error);
      return 'Unknown Folder';
    }
  }, [folderNames]);

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
          userEmail={userEmail}
          userName={userName}
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
          <SearchBar onOpenChat={handleOpenChat}/>
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
            isFolder={(file) => file.mimeType === 'application/vnd.google-apps.folder'} 
            getFolderName={getFolderName} 
            folderTree={folderTree}
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
        selectedFiles={moveSelectedFiles}
        currentFolder={moveCurrentFolder}
        folderStack={moveFolderStack}
        folders={moveFolders}
        handleFolderClick={handleMoveFolderClick}
        handleBreadcrumbClick={handleMoveBreadcrumbClick}
      />
      {isChatOpen && (
        <ChatInterface
          initialQuery={chatInitialQuery}
          onClose={handleCloseChat}
          getFileIcon={getFileIcon}
          isUploadPopupOpen={isUploadPopupOpen}
          setIsUploadPopupOpen={setIsUploadPopupOpen}
        />
      )}
    </div>
  );
};

export default BaseDrivePage;