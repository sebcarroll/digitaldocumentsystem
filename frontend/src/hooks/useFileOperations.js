/**
 * useFileOperations.js
 * This custom hook manages file operations in Google Drive.
 */

import { useState, useCallback } from 'react';
import * as driveApi from '../services/drive_service.js'

/**
 * Custom hook for file operations in Google Drive.
 * @param {Object} currentFolder - The current folder object.
 * @param {Function} getDriveFiles - Function to refresh the file list.
 * @param {Function} setError - Function to set error messages.
 * @returns {Object} An object containing file operation functions and state.
 */
export const useFileOperations = (currentFolder, getDriveFiles, setError) => {
  const [isNewFolderPopupOpen, setIsNewFolderPopupOpen] = useState(false);

  // Open the create folder popup
  const openCreateFolderPopup = useCallback(() => {
    setIsNewFolderPopupOpen(true);
  }, []);

  // Handle folder creation
  const handleCreateFolder = useCallback(async (folderName) => {
    if (folderName) {
      try {
        await driveApi.createFolder(currentFolder.id, folderName);
        getDriveFiles(currentFolder.id);
      } catch (error) {
        setError('Failed to create folder.');
      } finally {
        setIsNewFolderPopupOpen(false);
      }
    }
  }, [currentFolder.id, getDriveFiles, setError]);

  // Handle file upload
  const handleUploadFile = useCallback(async (file) => {
    if (file) {
      try {
        await driveApi.uploadFile(currentFolder.id, file);
        getDriveFiles(currentFolder.id);
      } catch (error) {
        setError('Failed to upload file.');
      }
    } else {
      setError('No file selected for upload.');
    }
  }, [currentFolder.id, getDriveFiles, setError]);

  // Handle folder upload
  const handleUploadFolder = useCallback(async (files) => {
    if (files && files.length > 0) {
      try {
        await driveApi.uploadFolder(currentFolder.id, files);
        getDriveFiles(currentFolder.id);
      } catch (error) {
        setError('Failed to upload folder.');
      }
    } else {
      setError('No folder selected for upload.');
    }
  }, [currentFolder.id, getDriveFiles, setError]);

  // Handle Google Doc creation
  const handleCreateDoc = useCallback(async () => {
    try {
      const response = await driveApi.createDoc(currentFolder.id);
      getDriveFiles(currentFolder.id);
      if (response.webViewLink) {
        window.open(response.webViewLink, '_blank', 'noopener,noreferrer');
      }
    } catch (error) {
      setError('Failed to create Google Doc.');
    }
  }, [currentFolder.id, getDriveFiles, setError]);

  // Handle Google Sheet creation
  const handleCreateSheet = useCallback(async () => {
    try {
      const response = await driveApi.createSheet(currentFolder.id);
      getDriveFiles(currentFolder.id);
      if (response.webViewLink) {
        window.open(response.webViewLink, '_blank', 'noopener,noreferrer');
      }
    } catch (error) {
      setError('Failed to create Google Sheet.');
    }
  }, [currentFolder.id, getDriveFiles, setError]);

  return {
    isNewFolderPopupOpen,
    openCreateFolderPopup,
    handleCreateFolder,
    handleUploadFile,
    handleUploadFolder,
    handleCreateDoc,
    handleCreateSheet,
    setIsNewFolderPopupOpen
  };
};