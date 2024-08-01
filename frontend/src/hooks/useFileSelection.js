// useFileSelection.js
import { useState, useCallback } from 'react';
import { moveFiles, deleteFiles, copyFiles, openDriveFile, renameFile } from '../services/api';

export const useFileSelection = (getDriveFiles, currentFolder, setError) => {
  const [showActionMenu, setShowActionMenu] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isRenamePopupOpen, setIsRenamePopupOpen] = useState(false);
  const [fileToRename, setFileToRename] = useState(null);

  const handleFileSelect = useCallback((file) => {
    if (showActionMenu) {
      setSelectedFiles(prev => {
        const isSelected = prev.some(f => f.id === file.id);
        return isSelected ? prev.filter(f => f.id !== file.id) : [...prev, file];
      });
    }
  }, [showActionMenu]);

  const handleMoreClick = useCallback((event, file) => {
    event.stopPropagation();
    setSelectedFiles([file]);
    setShowActionMenu(true);
  }, []);

  const handleMove = useCallback(async () => {
    try {
      const newFolderId = prompt("Enter the ID of the destination folder:");
      if (newFolderId) {
        await moveFiles(selectedFiles.map(f => f.id), newFolderId);
        getDriveFiles(currentFolder.id);
        setShowActionMenu(false);
        setSelectedFiles([]);
      }
    } catch (error) {
      console.error('Failed to move files:', error);
      setError(error.message);
    }
  }, [selectedFiles, getDriveFiles, currentFolder.id, setError]);

  const handleDelete = useCallback(async () => {
    try {
      await deleteFiles(selectedFiles.map(f => f.id));
      getDriveFiles(currentFolder.id);
      setShowActionMenu(false);
      setSelectedFiles([]);
    } catch (error) {
      console.error('Failed to delete files:', error);
      setError(error.message);
    }
  }, [selectedFiles, getDriveFiles, currentFolder.id, setError]);

  const handleCopyLink = useCallback(async () => {
    if (selectedFiles.length !== 1) return;
    try {
      const file = selectedFiles[0];
      const response = await openDriveFile(file.id);
      navigator.clipboard.writeText(response.webViewLink);
      alert('Link copied to clipboard!');
    } catch (error) {
      console.error('Failed to copy link:', error);
      setError(error.message);
    } finally {
      setShowActionMenu(false);
      setSelectedFiles([]);
    }
  }, [selectedFiles, setError]);

  const openRenamePopup = useCallback(() => {
    if (selectedFiles.length !== 1) return;
    setFileToRename(selectedFiles[0]);
    setIsRenamePopupOpen(true);
  }, [selectedFiles]);

  const handleRename = useCallback(async (newName) => {
    if (!fileToRename) return;
    try {
      await renameFile(fileToRename.id, newName);
      getDriveFiles(currentFolder.id);
    } catch (error) {
      console.error('Failed to rename file:', error);
      setError(error.message);
    } finally {
      setIsRenamePopupOpen(false);
      setFileToRename(null);
      setShowActionMenu(false);
      setSelectedFiles([]);
    }
  }, [fileToRename, getDriveFiles, currentFolder.id, setError]);

  const handleMakeCopy = useCallback(async () => {
    try {
      await copyFiles(selectedFiles.map(f => f.id));
      getDriveFiles(currentFolder.id);
      setShowActionMenu(false);
      setSelectedFiles([]);
    } catch (error) {
      console.error('Failed to make copies:', error);
      setError(error.message);
    }
  }, [selectedFiles, getDriveFiles, currentFolder.id, setError]);

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
    setIsRenamePopupOpen
  };
};