// src/contexts/DriveContext.js

import React, { createContext, useContext, useState, useCallback } from 'react';
import { useFileSelection } from '../hooks/useFileSelection';
import { useFileSharing } from '../hooks/useFileSharing';
import { useFolderNavigation } from '../hooks/useFolderNavigation';
import { useGetDriveFiles } from '../hooks/useGetDriveFiles';
import { useMovePopup } from '../hooks/useMovePopup';
import { useViewOptions } from '../hooks/useViewOptions';
import { useFileOperations } from '../hooks/useFileOperations';

const DriveContext = createContext();

/**
 * DriveProvider component
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components
 */
export const DriveProvider = ({ children }) => {
  // State for error handling and loading
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  
  // State for drive files
  const [driveFiles, setDriveFiles] = useState([]);

  // Custom hooks
  const getDriveFiles = useGetDriveFiles(setError, setIsLoading);
  const folderNavigation = useFolderNavigation(setError);
  const fileSelection = useFileSelection(getDriveFiles, folderNavigation.currentFolder, setError);
  const fileSharing = useFileSharing(fileSelection.selectedFiles);
  const movePopup = useMovePopup(fileSelection.selectedFiles, fileSelection.handleMove, setError);
  const viewOptions = useViewOptions();
  const fileOperations = useFileOperations(folderNavigation.currentFolder, getDriveFiles, setError);

  // Destructure viewOptions
  const {
    filesActive,
    foldersActive,
    listLayoutActive,
    handleFilesClick,
    handleFoldersClick,
    handleListLayoutClick,
    handleGridLayoutClick
  } = viewOptions;

  // Sidebar items
  const [sidebarItems] = useState([
    { path: '/', label: 'Home' },
    { path: '/my-archive', label: 'My Archive' },
    { path: '/shared-with-me', label: 'Shared with me' },
    { path: '/recent', label: 'Recent' },
    { path: '/bin', label: 'Bin' }
  ]);

  /**
   * Fetch drive files
   * @param {string} folderId - ID of the folder to fetch files from
   */
  const fetchDriveFiles = useCallback(async (folderId) => {
    try {
      setIsLoading(true);
      const files = await getDriveFiles(folderId);
      setDriveFiles(files);
      return files;
    } catch (err) {
      setError("Failed to fetch drive files");
      return [];
    } finally {
      setIsLoading(false);
    }
  }, [getDriveFiles, setError, setIsLoading]);

  /**
   * Handle file click
   * @param {Object} file - File object that was clicked
   */
  const handleFileClick = useCallback((file) => {
    if (file.mimeType === 'application/vnd.google-apps.folder') {
      folderNavigation.navigateToFolder(file);
    } else {
      fileSelection.handleFileSelect(file);
    }
  }, [folderNavigation, fileSelection]);

  /**
   * Close action menu
   */
  const handleCloseActionMenu = useCallback(() => {
    fileSelection.setShowActionMenu(false);
    fileSelection.setSelectedFiles([]);
  }, [fileSelection]);

  // Context value
  const value = {
    error,
    setError,
    isLoading,
    setIsLoading,
    getDriveFiles: fetchDriveFiles,
    driveFiles,
    sidebarItems,
    handleFileClick,
    handleCloseActionMenu,
    filesActive,
    foldersActive,
    listLayoutActive,
    handleFilesClick,
    handleFoldersClick,
    handleListLayoutClick,
    handleGridLayoutClick,
    ...folderNavigation,
    ...fileSelection,
    ...fileSharing,
    ...movePopup,
    ...fileOperations,
  };

  return <DriveContext.Provider value={value}>{children}</DriveContext.Provider>;
};

/**
 * Custom hook to use Drive context
 * @returns {Object} Drive context value
 */
export const useDrive = () => useContext(DriveContext);