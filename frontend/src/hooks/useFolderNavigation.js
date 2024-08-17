// src/hooks/useFolderNavigation.js

import { useState, useCallback } from 'react';
import { openDriveFile } from '../services/drive_service';

export const useFolderNavigation = (setError, fetchDriveFiles) => {
  const [currentFolder, setCurrentFolder] = useState({ id: 'root', name: 'Home' });
  const [folderStack, setFolderStack] = useState([]);

  const handleFileClick = useCallback(async (file) => {
    if (file.mimeType === 'application/vnd.google-apps.folder') {
      setFolderStack(prev => [...prev, currentFolder]);
      setCurrentFolder({ id: file.id, name: file.name });
      try {
        await fetchDriveFiles(file.id);
      } catch (error) {
        console.error('Failed to fetch folder contents:', error);
        setError('Failed to fetch folder contents.');
      }
    } else {
      try {
        const response = await openDriveFile(file.id);
        window.open(response.webViewLink, '_blank');
      } catch (error) {
        console.error('Failed to open file:', error);
        setError('Failed to open file.');
      }
    }
  }, [currentFolder, setError, fetchDriveFiles]);

  const handleBackClick = useCallback(() => {
    if (folderStack.length > 0) {
      const previousFolder = folderStack[folderStack.length - 1];
      setFolderStack(prev => prev.slice(0, -1));
      setCurrentFolder(previousFolder);
      fetchDriveFiles(previousFolder.id).catch(error => {
        console.error('Failed to fetch previous folder contents:', error);
        setError('Failed to fetch previous folder contents.');
      });
    }
  }, [folderStack, fetchDriveFiles, setError]);

  const handleBreadcrumbClick = useCallback((index) => {
    if (index < folderStack.length) {
      const newStack = folderStack.slice(0, index);
      setFolderStack(newStack);
      const clickedFolder = index === folderStack.length ? currentFolder : folderStack[index];
      setCurrentFolder(clickedFolder);
      fetchDriveFiles(clickedFolder.id).catch(error => {
        console.error('Failed to fetch folder contents:', error);
        setError('Failed to fetch folder contents.');
      });
    }
  }, [folderStack, currentFolder, fetchDriveFiles, setError]);

  return {
    currentFolder,
    folderStack,
    handleFileClick,
    handleBackClick,
    handleBreadcrumbClick
  };
};