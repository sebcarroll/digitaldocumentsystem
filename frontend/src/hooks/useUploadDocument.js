import { useState, useCallback } from 'react';
import { useFileSelection } from './useFileSelection';
import { fetchDriveFiles } from '../services/api';

export const useUploadDocument = (setError) => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentFolder, setCurrentFolder] = useState({ id: 'root', name: 'My Drive' });
  const [folderStack, setFolderStack] = useState([]);
  const [items, setItems] = useState([]);

  const getDriveFiles = useCallback(async (folderId) => {
    try {
      const content = await fetchDriveFiles(folderId);
      setItems(content && content.files ? content.files : []);
    } catch (error) {
      console.error('Failed to fetch folder contents:', error);
      setError(error.message || 'Failed to fetch folder contents');
      setItems([]);
    }
  }, [setError]);

  const fileSelectionHook = useFileSelection(getDriveFiles, currentFolder, setError);

  const handleOpen = useCallback(() => {
    setIsOpen(true);
    getDriveFiles('root');
  }, [getDriveFiles]);

  const handleClose = useCallback(() => {
    setIsOpen(false);
    setCurrentFolder({ id: 'root', name: 'My Drive' });
    setFolderStack([]);
    fileSelectionHook.setSelectedFiles([]);
    fileSelectionHook.setShowActionMenu(false);
  }, [fileSelectionHook]);

  const handleFolderClick = useCallback((folder) => {
    setFolderStack(prev => [...prev, currentFolder]);
    setCurrentFolder(folder);
    getDriveFiles(folder.id);
  }, [currentFolder, getDriveFiles]);

  const handleBreadcrumbClick = useCallback((index) => {
    if (index < folderStack.length) {
      const newStack = folderStack.slice(0, index);
      const clickedFolder = index === -1 ? { id: 'root', name: 'My Drive' } : folderStack[index];
      setFolderStack(newStack);
      setCurrentFolder(clickedFolder);
      getDriveFiles(clickedFolder.id);
    }
  }, [folderStack, getDriveFiles]);

  const handleUpload = useCallback(async () => {
    // Implement your upload logic here
    console.log('Uploading files:', fileSelectionHook.selectedFiles);
    handleClose();
  }, [fileSelectionHook.selectedFiles, handleClose]);

  return {
    isOpen,
    setIsOpen,
    currentFolder,
    folderStack,
    items,
    handleOpen,
    handleClose,
    handleFolderClick,
    handleBreadcrumbClick,
    handleUpload,
    ...fileSelectionHook
  };
};