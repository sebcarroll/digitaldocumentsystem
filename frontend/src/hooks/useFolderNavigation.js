/**
 * useFolderNavigation.js
 * This custom hook manages folder navigation in Google Drive.
 */

import { useState, useCallback } from 'react';

/**
 * Custom hook for folder navigation in Google Drive.
 * @returns {Object} An object containing folder navigation functions and state.
 */
export const useFolderNavigation = () => {
  // State to keep track of the current folder
  const [currentFolder, setCurrentFolder] = useState({ id: 'root', name: 'Home' });
  // State to maintain the navigation history
  const [folderStack, setFolderStack] = useState([]);

  /**
   * Handle navigation to a folder.
   * @param {Object} folder - The folder to navigate to.
   */
  const navigateToFolder = useCallback((folder) => {
    setFolderStack(prev => [...prev, currentFolder]);
    setCurrentFolder(folder);
  }, [currentFolder]);

  /**
   * Handle navigation to the previous folder.
   */
  const handleBackClick = useCallback(() => {
    if (folderStack.length > 0) {
      const previousFolder = folderStack[folderStack.length - 1];
      setFolderStack(prev => prev.slice(0, -1));
      setCurrentFolder(previousFolder);
    }
  }, [folderStack]);

  /**
   * Handle clicks on breadcrumb items for navigation.
   * @param {number} index - The index of the clicked breadcrumb item.
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
    setCurrentFolder,
    navigateToFolder,
    handleBackClick,
    handleBreadcrumbClick
  };
};