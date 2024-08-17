// src/hooks/useGetDriveFiles.js

import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchDriveFiles } from '../services/drive_service.js';
import { checkAuth } from '../services/authorisation_service.js';

/**
 * Custom hook for fetching drive files
 * @param {Function} setError - Function to set error state
 * @param {Function} setIsLoading - Function to set loading state
 * @returns {Function} getDriveFiles function
 */
export const useGetDriveFiles = (setError, setIsLoading) => {
  const navigate = useNavigate();

  /**
   * Fetches drive files from the server
   * @param {string} folderId - The ID of the folder to fetch files from
   * @returns {Promise<Array>} Array of drive files
   */
  const getDriveFiles = useCallback(async (folderId) => {
    try {
      setIsLoading(true);
      const authStatus = await checkAuth();
      if (!authStatus.authenticated) {
        navigate('/login');
        return [];
      }

      const content = await fetchDriveFiles(folderId);
      return content.files || [];
    } catch (error) {
      console.error('Failed to fetch drive files:', error);
      setError('Failed to load Google Drive files.');
      return [];
    } finally {
      setIsLoading(false);
    }
  }, [navigate, setError, setIsLoading]);

  return getDriveFiles;
};