import { useState, useCallback } from 'react';
import { openDriveFile } from '../services/api';

export const useFolderNavigation = (setError) => {
  const [currentFolder, setCurrentFolder] = useState({ id: 'root', name: 'My Drive' });
  const [folderStack, setFolderStack] = useState([]);

  const handleFileClick = useCallback(async (file, newFolderStack = null) => {
    if (file.mimeType === 'application/vnd.google-apps.folder') {
      if (newFolderStack) {
        setFolderStack(newFolderStack);
      } else {
        setFolderStack(prev => [...prev, currentFolder]);
      }
      setCurrentFolder({ id: file.id, name: file.name });
    } else {
      try {
        const response = await openDriveFile(file.id);
        window.open(response.webViewLink, '_blank');
      } catch (error) {
        console.error('Failed to open file:', error);
        if (setError) {
          setError('Failed to open file.');
        }
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
    if (index === 0) {
      // Clicking on the root folder
      setFolderStack([]);
      setCurrentFolder({ id: 'root', name: 'My Drive' });
    } else if (index <= folderStack.length) {
      const newStack = folderStack.slice(0, index - 1);
      setFolderStack(newStack);
      setCurrentFolder(folderStack[index - 1]);
    }
  }, [folderStack]);

  const resetNavigation = useCallback(() => {
    setCurrentFolder({ id: 'root', name: 'My Drive' });
    setFolderStack([]);
  }, []);

  return {
    currentFolder,
    folderStack,
    handleFileClick,
    handleBackClick,
    handleBreadcrumbClick,
    resetNavigation
  };
};