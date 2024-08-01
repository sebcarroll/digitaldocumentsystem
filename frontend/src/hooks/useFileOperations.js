// useFileOperations.js
import { useState, useCallback } from 'react';
import { createFolder, uploadFile, uploadFolder, createDoc, createSheet } from '../services/api';

export const useFileOperations = (currentFolder, getDriveFiles, setError) => {
  const handleCreateFolder = useCallback(async () => {
    const folderName = prompt("Enter folder name:");
    if (folderName) {
      try {
        await createFolder(currentFolder.id, folderName);
        getDriveFiles(currentFolder.id);
      } catch (error) {
        setError('Failed to create folder.');
      }
    }
  }, [currentFolder.id, getDriveFiles, setError]);

  const handleUploadFile = useCallback(async (file) => {
    if (file) {
      try {
        await uploadFile(currentFolder.id, file);
        getDriveFiles(currentFolder.id);
      } catch (error) {
        console.error('Failed to upload file:', error);
        setError('Failed to upload file.');
      }
    } else {
      console.error('No file selected');
      setError('No file selected for upload.');
    }
  }, [currentFolder.id, getDriveFiles, setError]);

  const handleUploadFolder = useCallback(async (files) => {
    if (files && files.length > 0) {
      try {
        await uploadFolder(currentFolder.id, files);
        getDriveFiles(currentFolder.id);
      } catch (error) {
        console.error('Failed to upload folder:', error);
        setError('Failed to upload folder.');
      }
    } else {
      console.error('No folder selected');
      setError('No folder selected for upload.');
    }
  }, [currentFolder.id, getDriveFiles, setError]);

  const handleCreateDoc = useCallback(async () => {
    try {
      const response = await createDoc(currentFolder.id);
      getDriveFiles(currentFolder.id);
      if (response.webViewLink) {
        window.open(response.webViewLink, '_blank', 'noopener,noreferrer');
      }
    } catch (error) {
      setError('Failed to create Google Doc.');
    }
  }, [currentFolder.id, getDriveFiles, setError]);

  const handleCreateSheet = useCallback(async () => {
    try {
      const response = await createSheet(currentFolder.id);
      getDriveFiles(currentFolder.id);
      if (response.webViewLink) {
        window.open(response.webViewLink, '_blank', 'noopener,noreferrer');
      }
    } catch (error) {
      setError('Failed to create Google Sheet.');
    }
  }, [currentFolder.id, getDriveFiles, setError]);

  return {
    handleCreateFolder,
    handleUploadFile,
    handleUploadFolder,
    handleCreateDoc,
    handleCreateSheet
  };
};