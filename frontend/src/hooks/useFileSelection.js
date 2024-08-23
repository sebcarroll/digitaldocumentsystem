// useFileSelection.js
import { useState, useCallback, useMemo, useRef, useEffect } from 'react';
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

  const handleMove = useCallback(async (fileIds, newFolderId) => {
    try {
      await moveFiles(fileIds, newFolderId);
      getDriveFiles(currentFolder.id);
      setShowActionMenu(false);
      setSelectedFiles([]);
      // Note: We'll handle opening the new folder in the DrivePage component
    } catch (error) {
      console.error('Failed to move files:', error);
      setError('Failed to move files. Please try again.');
    }
  }, [getDriveFiles, currentFolder, setError]);


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

  const isMounted = useRef(true);

  useEffect(() => {
    return () => {
      isMounted.current = false;
    };
  }, []);

  const handleCopyLink = useCallback(async (file) => {
    if (!file) return;
    try {
      const data = await openDriveFile(file.id);
      if (data.webViewLink) {
        await navigator.clipboard.writeText(data.webViewLink);
        if (isMounted.current) {
          alert('Link copied to clipboard!');
        }
      } else {
        throw new Error('Web view link not found in response');
      }
    } catch (error) {
      console.error('Failed to copy link:', error);
      if (isMounted.current) {
        setError(`Failed to copy link: ${error.message}`);
      }
    }
  }, [setError]);

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

  const isFolder = useMemo(() => {
    return selectedFiles.some(file => file.mimeType === 'application/vnd.google-apps.folder');
  }, [selectedFiles]);

  const handleMakeCopy = useCallback(async () => {
    try {
      const filesToCopy = selectedFiles.filter(file => file.mimeType !== 'application/vnd.google-apps.folder');
      
      if (filesToCopy.length === 0) {
        setError("No files selected for copying. Folders cannot be copied.");
        return;
      }
  
      await copyFiles(filesToCopy.map(f => f.id));
      await getDriveFiles(currentFolder.id);
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