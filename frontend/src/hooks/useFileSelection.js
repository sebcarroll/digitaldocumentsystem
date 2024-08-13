/**
 * useFileSelection.js
 * This custom hook manages file selection and related actions in Google Drive.
 */

import { useState, useCallback, useMemo } from 'react';
import * as driveApi from '../services/drive_service';

/**
 * Custom hook for file selection and related actions in Google Drive.
 * @param {Function} getDriveFiles - Function to refresh the file list.
 * @param {Object} currentFolder - The current folder object.
 * @param {Function} setError - Function to set error messages.
 * @returns {Object} An object containing file selection functions and state.
 */
export const useFileSelection = (getDriveFiles, currentFolder, setError) => {
  const [showActionMenu, setShowActionMenu] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isRenamePopupOpen, setIsRenamePopupOpen] = useState(false);
  const [fileToRename, setFileToRename] = useState(null);

  /**
   * Handle file selection.
   * @param {Object} file - The file to select or deselect.
   */
  const handleFileSelect = useCallback((file) => {
    if (showActionMenu) {
      setSelectedFiles(prev => {
        const isSelected = prev.some(f => f.id === file.id);
        return isSelected ? prev.filter(f => f.id !== file.id) : [...prev, file];
      });
    }
  }, [showActionMenu]);

  /**
   * Handle 'More' button click.
   * @param {Event} event - The click event.
   * @param {Object} file - The file associated with the 'More' button.
   */
  const handleMoreClick = useCallback((event, file) => {
    event.stopPropagation();
    setSelectedFiles([file]);
    setShowActionMenu(true);
  }, []);

  /**
   * Handle moving files.
   * @param {string[]} fileIds - The IDs of the files to move.
   * @param {string} newFolderId - The ID of the destination folder.
   */
  const handleMove = useCallback(async (fileIds, newFolderId) => {
    try {
      await driveApi.moveFiles(fileIds, newFolderId);
      getDriveFiles(currentFolder.id);
    } catch (error) {
      setError('Failed to move files. Please try again.');
    }
  }, [getDriveFiles, currentFolder, setError]);

  /**
   * Handle deleting files.
   */
  const handleDelete = useCallback(async () => {
    try {
      await driveApi.deleteFiles(selectedFiles.map(f => f.id));
      getDriveFiles(currentFolder.id);
      setShowActionMenu(false);
      setSelectedFiles([]);
    } catch (error) {
      setError(error.message);
    }
  }, [selectedFiles, getDriveFiles, currentFolder.id, setError]);

  /**
   * Handle copying file link.
   */
  const handleCopyLink = useCallback(async () => {
    if (selectedFiles.length !== 1) return;
    try {
      const file = selectedFiles[0];
      const response = await driveApi.openDriveFile(file.id);
      navigator.clipboard.writeText(response.webViewLink);
      alert('Link copied to clipboard!');
    } catch (error) {
      setError(error.message);
    } finally {
      setShowActionMenu(false);
      setSelectedFiles([]);
    }
  }, [selectedFiles, setError]);

  /**
   * Open rename popup.
   */
  const openRenamePopup = useCallback(() => {
    if (selectedFiles.length !== 1) return;
    setFileToRename(selectedFiles[0]);
    setIsRenamePopupOpen(true);
  }, [selectedFiles]);

  /**
   * Handle renaming file.
   * @param {string} newName - The new name for the file.
   */
  const handleRename = useCallback(async (newName) => {
    if (!fileToRename) return;
    try {
      await driveApi.renameFile(fileToRename.id, newName);
      getDriveFiles(currentFolder.id);
    } catch (error) {
      setError(error.message);
    } finally {
      setIsRenamePopupOpen(false);
      setFileToRename(null);
      setShowActionMenu(false);
      setSelectedFiles([]);
    }
  }, [fileToRename, getDriveFiles, currentFolder.id, setError]);

  /**
   * Check if selected file is a folder.
   */
  const isFolder = useMemo(() => {
    return selectedFiles.some(file => file.mimeType === 'application/vnd.google-apps.folder');
  }, [selectedFiles]);

  /**
   * Handle making a copy of files.
   */
  const handleMakeCopy = useCallback(async () => {
    try {
      const filesToCopy = selectedFiles.filter(file => file.mimeType !== 'application/vnd.google-apps.folder');
      
      if (filesToCopy.length === 0) {
        setError("No files selected for copying. Folders cannot be copied.");
        return;
      }
  
      await driveApi.copyFiles(filesToCopy.map(f => f.id));
      await getDriveFiles(currentFolder.id);
      setShowActionMenu(false);
      setSelectedFiles([]);
    } catch (error) {
      setError(error.message);
    }
  }, [selectedFiles, getDriveFiles, currentFolder.id, setError]);
  
  /**
   * Close action menu.
   */
  const handleCloseActionMenu = useCallback(() => {
    setShowActionMenu(false);
    setSelectedFiles([]);
  }, []);

  return {
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
  };
};