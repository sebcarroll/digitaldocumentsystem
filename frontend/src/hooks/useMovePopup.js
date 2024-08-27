// useMovePopup.js
import { useState, useCallback } from 'react';
import { fetchDriveFiles, moveFiles } from '../services/api';

export const useMovePopup = (initialSelectedFiles, setError, onMoveComplete) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState(initialSelectedFiles);
  const [currentFolder, setCurrentFolder] = useState({ id: 'root', name: 'My Drive' });
  const [folderStack, setFolderStack] = useState([]);
  const [folders, setFolders] = useState([]);

  const fetchFoldersData = useCallback(async (folderId) => {
    try {
      const content = await fetchDriveFiles(folderId);
      const folderContent = content && content.files 
        ? content.files.filter(file => file.mimeType === 'application/vnd.google-apps.folder')
        : [];
      setFolders(folderContent);
    } catch (error) {
      console.error('Failed to fetch folders:', error);
      setFolders([]);
    }
  }, []);

  const handleOpen = useCallback((files) => {
    setSelectedFiles(files);
    setIsOpen(true);
    fetchFoldersData('root');
  }, [fetchFoldersData]);

  const handleClose = useCallback(() => {
    setIsOpen(false);
    setCurrentFolder({ id: 'root', name: 'My Drive' });
    setFolderStack([]);
  }, []);

  const handleFolderClick = useCallback((folder) => {
    setFolderStack(prev => [...prev, currentFolder]);
    setCurrentFolder(folder);
    fetchFoldersData(folder.id);
  }, [currentFolder, fetchFoldersData]);

  const handleBreadcrumbClick = useCallback((index) => {
    if (index < folderStack.length) {
      const newStack = folderStack.slice(0, index);
      const clickedFolder = index === -1 ? { id: 'root', name: 'My Drive' } : folderStack[index];
      setFolderStack(newStack);
      setCurrentFolder(clickedFolder);
      fetchFoldersData(clickedFolder.id);
    }
  }, [folderStack, fetchFoldersData]);

const handleMove = useCallback(async () => {
  try {
    await moveFiles(selectedFiles.map(f => f.id), currentFolder.id);
    handleClose();
    onMoveComplete(currentFolder, [...folderStack, currentFolder]);
  } catch (error) {
    setError(error.message || 'Failed to move files');
  }
}, [selectedFiles, currentFolder, folderStack, moveFiles, handleClose, setError, onMoveComplete]);

  return {
    isOpen,
    selectedFiles,
    currentFolder,
    folderStack,
    folders,
    handleOpen,
    handleClose,
    handleFolderClick,
    handleBreadcrumbClick,
    handleMove,
  };
};