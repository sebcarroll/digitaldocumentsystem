//useFileSelection.js
import { useState, useCallback } from 'react';
import { moveFiles, deleteFiles, copyFiles, openDriveFile, renameFile } from '../services/api';

export const useFileSelection = (getDriveFiles, currentFolder, setError) => {
  const [showActionMenu, setShowActionMenu] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);

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
  }, [selectedFiles, getDriveFiles, currentFolder.id, setError, setShowActionMenu, setSelectedFiles]);

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
  }, [selectedFiles, getDriveFiles, currentFolder.id, setError, setShowActionMenu, setSelectedFiles]);

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

  const handleRename = useCallback(async () => {
    if (selectedFiles.length !== 1) return;
    try {
      const file = selectedFiles[0];
      const newName = prompt("Enter new name for the file:", file.name);
      if (newName) {
        await renameFile(file.id, newName);
        getDriveFiles(currentFolder.id);
      }
    } catch (error) {
      console.error('Failed to rename file:', error);
      setError(error.message);
    } finally {
      setShowActionMenu(false);
      setSelectedFiles([]);
    }
  }, [selectedFiles, getDriveFiles, currentFolder.id, setError]);

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
  }, [selectedFiles, getDriveFiles, currentFolder.id, setError, setShowActionMenu, setSelectedFiles]);

  const handleCloseActionMenu = useCallback(() => {
    setShowActionMenu(false);
    setSelectedFiles([]);
  }, []);

  return {
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
    setShowActionMenu
  };
};