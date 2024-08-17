// src/contexts/DriveContext.js

import React, { createContext, useContext, useState, useCallback, useEffect, useMemo } from 'react';
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

  // State for folder and rename popup
  const [isNewFolderPopupOpen, setIsNewFolderPopupOpen] = useState(false);
  const [isRenamePopupOpen, setIsRenamePopupOpen] = useState(false);
  const [fileToRename, setFileToRename] = useState(null);

  // Custom hooks
  const getDriveFiles = useGetDriveFiles(setError, setIsLoading);

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

  const folderNavigation = useFolderNavigation(setError, fetchDriveFiles);
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

  // Effect to fetch new folder contents when the current folder changes
  useEffect(() => {
    fetchDriveFiles(folderNavigation.currentFolder.id);
  }, [folderNavigation.currentFolder, fetchDriveFiles]);

  /**
   * Close action menu
   */
  const handleCloseActionMenu = useCallback(() => {
    fileSelection.setShowActionMenu(false);
    fileSelection.setSelectedFiles([]);
  }, [fileSelection]);

  // Context value
  const value = useMemo(() => ({
    error,
    setError,
    isLoading,
    setIsLoading,
    getDriveFiles: fetchDriveFiles,
    driveFiles,
    sidebarItems,
    handleCloseActionMenu,
    filesActive,
    foldersActive,
    listLayoutActive,
    handleFilesClick,
    handleFoldersClick,
    handleListLayoutClick,
    handleGridLayoutClick,
    isNewFolderPopupOpen,
    setIsNewFolderPopupOpen,
    isRenamePopupOpen,
    setIsRenamePopupOpen,
    fileToRename,
    setFileToRename,
    ...folderNavigation,
    ...fileSelection,
    ...fileSharing,
    ...movePopup,
    ...fileOperations,
  }), [
    error, isLoading, driveFiles, sidebarItems, filesActive, foldersActive, listLayoutActive,
    folderNavigation, fileSelection, fileSharing, movePopup, fileOperations,
    isNewFolderPopupOpen, isRenamePopupOpen, fileToRename,
    fetchDriveFiles, handleCloseActionMenu, handleFilesClick,
    handleFoldersClick, handleListLayoutClick, handleGridLayoutClick,
  ]);

  return <DriveContext.Provider value={value}>{children}</DriveContext.Provider>;
};

/**
 * Custom hook to use Drive context
 * @returns {Object} Drive context value
 */
export const useDrive = () => useContext(DriveContext);