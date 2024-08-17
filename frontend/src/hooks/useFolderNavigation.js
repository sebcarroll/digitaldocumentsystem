// useFolderNavigation.js
import { useState, useCallback } from 'react';
import { openDriveFile } from '../services/drive_service';

/**
 * A custom hook for managing folder navigation in a file system-like structure.
 * 
 * @param {Function} setError - A function to set error messages.
 * @returns {Object} An object containing the current folder, folder stack, and navigation functions.
 */
export const useFolderNavigation = (setError) => {
  // State for the current folder
  const [currentFolder, setCurrentFolder] = useState({ id: 'root', name: 'Home' });
  // State for the folder navigation stack
  const [folderStack, setFolderStack] = useState([]);

  /**
   * Handles clicking on a file or folder.
   * If it's a folder, navigate into it. If it's a file, attempt to open it.
   */
  const handleFileClick = useCallback(async (file) => {
    if (file.mimeType === 'application/vnd.google-apps.folder') {
      // If it's a folder, update the stack and current folder
      setFolderStack(prev => [...prev, currentFolder]);
      setCurrentFolder({ id: file.id, name: file.name });
    } else {
      // If it's a file, try to open it
      try {
        const response = await openDriveFile(file.id);
        window.open(response.webViewLink, '_blank');
      } catch (error) {
        console.error('Failed to open file:', error);
        setError('Failed to open file.');
      }
    }
  }, [currentFolder, setError]);

  /**
   * Handles navigating back to the previous folder.
   */
  const handleBackClick = useCallback(() => {
    if (folderStack.length > 0) {
      const previousFolder = folderStack[folderStack.length - 1];
      setFolderStack(prev => prev.slice(0, -1));
      setCurrentFolder(previousFolder);
    }
  }, [folderStack]);

  /**
   * Handles clicking on a breadcrumb to navigate to a specific folder in the hierarchy.
   * 
   * @param {number} index - The index of the folder in the stack to navigate to.
   */
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