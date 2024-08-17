/**
 * drive_service.js
 * This file contains functions for interacting with the Google Drive API via our backend.
 */

const API_URL = process.env.REACT_APP_API_URL;

/**
 * Fetches files from Google Drive for a given folder.
 * @param {string} folderId - The ID of the folder to fetch files from. Defaults to 'root'.
 * @returns {Promise<Object>} The list of files in the folder.
 * @throws {Error} If fetching files fails.
 */
export const fetchDriveFiles = async (folderId = 'root') => {
  const response = await fetch(`${API_URL}/drive?folder_id=${folderId}`, {
    credentials: 'include',
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to fetch drive files: ${response.status} ${response.statusText} - ${errorText}`);
  }
  return response.json();
};

/**
 * Opens a specific file in Google Drive.
 * @param {string} fileId - The ID of the file to open.
 * @returns {Promise<Object>} An object containing the webViewLink and mimeType of the file.
 * @throws {Error} If opening the file fails.
 */
export const openDriveFile = async (fileId) => {
  const response = await fetch(`${API_URL}/drive/${fileId}/open`, {
    credentials: 'include',
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to open drive file: ${response.status} ${response.statusText} - ${errorText}`);
  }
  return response.json();
};

/**
 * Creates a new folder in Google Drive.
 * @param {string} parentFolderId - The ID of the parent folder.
 * @param {string} folderName - The name of the new folder.
 * @returns {Promise<Object>} The details of the created folder.
 * @throws {Error} If creating the folder fails.
 */
export const createFolder = async (parentFolderId, folderName) => {
  const response = await fetch(`${API_URL}/drive/create-folder`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ parentFolderId, folderName }),
  });
  if (!response.ok) {
    throw new Error('Failed to create folder');
  }
  return response.json();
};

/**
 * Uploads a file to Google Drive.
 * @param {string} folderId - The ID of the folder to upload the file to.
 * @param {File} file - The file to upload.
 * @returns {Promise<Object>} The details of the uploaded file.
 * @throws {Error} If uploading the file fails.
 */
export const uploadFile = async (folderId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('folderId', folderId);

  const response = await fetch(`${API_URL}/drive/upload-file`, {
    method: 'POST',
    credentials: 'include',
    body: formData,
  });
  if (!response.ok) {
    throw new Error('Failed to upload file');
  }
  return response.json();
};

/**
 * Uploads a folder to Google Drive.
 * @param {string} parentFolderId - The ID of the parent folder.
 * @param {FileList} files - The files to upload.
 * @returns {Promise<Object>} The details of the uploaded folder.
 * @throws {Error} If uploading the folder fails.
 */
export const uploadFolder = async (parentFolderId, files) => {
  const formData = new FormData();
  formData.append('parentFolderId', parentFolderId);
  
  for (let i = 0; i < files.length; i++) {
    formData.append('files', files[i], files[i].webkitRelativePath);
  }

  const response = await fetch(`${API_URL}/drive/upload-folder`, {
    method: 'POST',
    credentials: 'include',
    body: formData,
  });
  if (!response.ok) {
    throw new Error('Failed to upload folder');
  }
  return response.json();
};

/**
 * Creates a new Google Doc.
 * @param {string} folderId - The ID of the folder to create the doc in.
 * @returns {Promise<Object>} The details of the created Google Doc.
 * @throws {Error} If creating the Google Doc fails.
 */
export const createDoc = async (folderId) => {
  const response = await fetch(`${API_URL}/drive/create-doc`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ folderId }),
  });
  if (!response.ok) {
    throw new Error('Failed to create Google Doc');
  }
  return response.json();
};

/**
 * Creates a new Google Sheet.
 * @param {string} folderId - The ID of the folder to create the sheet in.
 * @returns {Promise<Object>} The details of the created Google Sheet.
 * @throws {Error} If creating the Google Sheet fails.
 */
export const createSheet = async (folderId) => {
  const response = await fetch(`${API_URL}/drive/create-sheet`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ folderId }),
  });
  if (!response.ok) {
    throw new Error('Failed to create Google Sheet');
  }
  return response.json();
};

/**
 * Moves files to a new folder in Google Drive.
 * @param {string[]} fileIds - The IDs of the files to move.
 * @param {string} newFolderId - The ID of the destination folder.
 * @returns {Promise<Object>} The result of the move operation.
 * @throws {Error} If moving the files fails.
 */
export const moveFiles = async (fileIds, newFolderId) => {
  const response = await fetch(`${API_URL}/drive/move-files`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ fileIds, newFolderId }),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to move files');
  }
  return response.json();
};

/**
 * Deletes files from Google Drive.
 * @param {string[]} fileIds - The IDs of the files to delete.
 * @returns {Promise<Object>} The result of the delete operation.
 * @throws {Error} If deleting the files fails.
 */
export const deleteFiles = async (fileIds) => {
  const response = await fetch(`${API_URL}/drive/delete-files`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ fileIds }),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to delete files');
  }
  return response.json();
};

/**
 * Renames a file in Google Drive.
 * @param {string} fileId - The ID of the file to rename.
 * @param {string} newName - The new name for the file.
 * @returns {Promise<Object>} The details of the renamed file.
 * @throws {Error} If renaming the file fails.
 */
export const renameFile = async (fileId, newName) => {
  const response = await fetch(`${API_URL}/drive/rename-file`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ fileId, newName }),
  });
  if (!response.ok) {
    throw new Error('Failed to rename file');
  }
  return response.json();
};

/**
 * Copies files in Google Drive.
 * @param {string[]} fileIds - The IDs of the files to copy.
 * @returns {Promise<Object>} The details of the copied files.
 * @throws {Error} If copying the files fails.
 */
export const copyFiles = async (fileIds) => {
  const response = await fetch(`${API_URL}/drive/copy-files`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ fileIds }),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to copy files');
  }
  return response.json();
};

/**
 * Fetches folders from Google Drive.
 * @param {string} folderId - The ID of the parent folder. Defaults to 'root'.
 * @returns {Promise<Object>} The list of folders.
 * @throws {Error} If fetching folders fails.
 */
export const fetchFolders = async (folderId = 'root') => {
  const response = await fetch(`${API_URL}/drive/folders?parent_id=${folderId}`, {
    credentials: 'include',
  });
  if (!response.ok) {
    throw new Error('Failed to fetch folders');
  }
  return response.json();
};