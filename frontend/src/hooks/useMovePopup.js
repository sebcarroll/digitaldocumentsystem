/**
 * useMovePopup.js
 * This custom hook manages the state and UI logic for the move file/folder popup in Google Drive.
 */

import { useState, useCallback, useEffect } from 'react';
import * as driveApi from '../services/drive_service';
import { useFolderNavigation } from './useFolderNavigation';

/**
 * Custom hook for managing the move file/folder popup UI.
 * @param {Array} initialSelectedFiles - Initially selected files for moving.
 * @param {Function} onMoveConfirm - Callback function to execute when move is confirmed.
 * @param {Function} setError - Function to set error messages.
 * @returns {Object} An object containing move popup state and functions.
 */
export const useMovePopup = (initialSelectedFiles, onMoveConfirm, setError) => {
  // State variables
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('suggested');
  const [folders, setFolders] = useState([]);
  const [suggestedFolders, setSuggestedFolders] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState(initialSelectedFiles);

  const { currentFolder, folderStack, navigateToFolder, handleBackClick, handleBreadcrumbClick } = useFolderNavigation();

  /**
   * Fetch folders data from the API.
   * @param {string} folderId - ID of the folder to fetch subfolders for.
   */
  const fetchFoldersData = useCallback(async (folderId = 'root') => {
    try {
      const fetchedFolders = await driveApi.fetchFolders(folderId);
      setFolders(fetchedFolders);
    } catch (error) {
      console.error('Failed to fetch folders:', error);
      setError('Failed to fetch folders.');
    }
  }, [setError]);

  // Fetch folders data when popup is opened
  useEffect(() => {
    if (isOpen) {
      fetchFoldersData(currentFolder.id);
      // TODO: Implement logic to fetch suggested folders
      setSuggestedFolders([]);
    }
  }, [isOpen, currentFolder.id, fetchFoldersData]);

  /**
   * Open the move popup.
   * @param {Array} files - Files selected for moving.
   */
  const handleOpen = useCallback((files) => {
    setSelectedFiles(files);
    setIsOpen(true);
  }, []);

  /**
   * Close the move popup and reset states.
   */
  const handleClose = useCallback(() => {
    setIsOpen(false);
    setActiveTab('suggested');
    navigateToFolder({ id: 'root', name: 'My Drive' });
  }, [navigateToFolder]);

  /**
   * Handle tab change in the move popup.
   * @param {string} tab - The tab to switch to ('suggested' or 'all').
   */
  const handleTabClick = useCallback((tab) => {
    setActiveTab(tab);
    if (tab === 'all') {
      navigateToFolder({ id: 'root', name: 'My Drive' });
      fetchFoldersData('root');
    }
  }, [navigateToFolder, fetchFoldersData]);

  /**
   * Handle folder click in the move popup.
   * @param {Object} folder - The folder that was clicked.
   */
  const handleFolderClick = useCallback((folder) => {
    navigateToFolder(folder);
    fetchFoldersData(folder.id);
  }, [navigateToFolder, fetchFoldersData]);

  /**
   * Confirm the move operation.
   */
  const handleMoveConfirm = useCallback(() => {
    onMoveConfirm(selectedFiles.map(f => f.id), currentFolder.id);
    handleClose();
  }, [selectedFiles, currentFolder.id, onMoveConfirm, handleClose]);

  return {
    isOpen,
    activeTab,
    currentFolder,
    folderStack,
    folders,
    suggestedFolders,
    selectedFiles,
    handleOpen,
    handleClose,
    handleTabClick,
    handleFolderClick,
    handleBreadcrumbClick,
    handleBackClick,
    handleMoveConfirm,
  };
};