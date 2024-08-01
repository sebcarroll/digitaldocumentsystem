// useFolderNavigation.js
import { useState, useCallback } from 'react';
import { openDriveFile } from '../services/api';  // Import the openDriveFile function

export const useFolderNavigation = (setError) => {
  const [currentFolder, setCurrentFolder] = useState({ id: 'root', name: 'Home' });
  const [folderStack, setFolderStack] = useState([]);

  const handleFileClick = useCallback(async (file) => {
    if (file.mimeType === 'application/vnd.google-apps.folder') {
      setFolderStack(prev => [...prev, currentFolder]);
      setCurrentFolder({ id: file.id, name: file.name });
    } else {
      try {
        const response = await openDriveFile(file.id);
        window.open(response.webViewLink, '_blank');
      } catch (error) {
        console.error('Failed to open file:', error);
        setError('Failed to open file.');
      }
    }
  }, [currentFolder, setError]);

  const handleBackClick = useCallback(() => {
    if (folderStack.length > 0) {
      const previousFolder = folderStack[folderStack.length - 1];
      setFolderStack(prev => prev.slice(0, -1));
      setCurrentFolder(previousFolder);
    }
  }, [folderStack]);

  const handleBreadcrumbClick = useCallback((index) => {
    if (index < folderStack.length) {
      const newStack = folderStack.slice(0, index);
      setFolderStack(newStack);
      setCurrentFolder(folderStack[index]);
    }
  }, [folderStack]);

  return {
    currentFolder,
    folderStack,
    handleFileClick,
    handleBackClick,
    handleBreadcrumbClick
  };
};