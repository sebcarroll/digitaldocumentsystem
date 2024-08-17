// src/components/DrivePage.js

import React, { useState, useCallback } from 'react';
import { useDrive } from '../contexts/driveContext';
import './DrivePage.css';
import Sidebar from '../components/drivePage/sidebar';
import Header from '../components/drivePage/header';
import SearchBar from '../components/drivePage/searchbar';
import ViewOptions from '../components/drivePage/viewOptions';
import DriveContent from '../components/drivePage/driveContent';
import FolderAndRenamePopup from '../components/drivePage/folderAndRenamePopup';
import SharePopup from '../components/drivePage/sharePopup';
import MovePopup from '../components/drivePage//movePopup';
import ChatInterface from './chatInterface';

/**
 * DrivePage component
 * @returns {React.ReactElement} DrivePage component
 */
const DrivePage = () => {
  const {
    error,
    isLoading,
    currentFolder,
    folderStack,
    handleBreadcrumbClick,
    selectedFiles,
    setSelectedFiles,
    showActionMenu,
    setShowActionMenu,
    handleMove,
    handleDelete,
    handleMakeCopy,
    openRenamePopup,
    isNewFolderPopupOpen,
    isRenamePopupOpen,
  } = useDrive();

  // Local state
  const [isSharePopupOpen, setIsSharePopupOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatInitialQuery, setChatInitialQuery] = useState('');

  /**
   * Handle opening the chat interface
   * @param {string} query - Initial query for the chat
   */
  const handleOpenChat = useCallback((query) => {
    setIsChatOpen(true);
    setChatInitialQuery(query);
  }, []);

  /**
   * Handle closing the chat interface
   */
  const handleCloseChat = useCallback(() => {
    setIsChatOpen(false);
    setChatInitialQuery('');
  }, []);

  /**
   * Handle closing the share popup
   */
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
        />
      </div>
      <div className="sidebar">
        <Sidebar />
      </div>
      <div className="main-area">
        <div className="search-bar-container">
          <SearchBar onOpenChat={handleOpenChat} />
        </div>
        <div className="view-options-container">
          <ViewOptions
            showActionMenu={showActionMenu}
            selectedFiles={selectedFiles}
            onShare={() => setIsSharePopupOpen(true)}
            onMove={() => handleMove(selectedFiles.map(f => f.id), currentFolder.id)}
            onDelete={handleDelete}
            onMakeCopy={handleMakeCopy}
            onRename={openRenamePopup}
          />
        </div>
        <main className="main-content">
          <DriveContent />
        </main>
      </div>
      {(isNewFolderPopupOpen || isRenamePopupOpen) && <FolderAndRenamePopup />}
      {isSharePopupOpen && (
        <SharePopup
          items={selectedFiles}
          onClose={handleCloseSharePopup}
        />
      )}
      <MovePopup />
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