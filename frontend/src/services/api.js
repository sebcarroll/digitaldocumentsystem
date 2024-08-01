const API_URL = process.env.REACT_APP_API_URL;

export const initiateGoogleLogin = () => {
  window.location.href = `${API_URL}/login`;
};

export const checkAuth = async () => {
  const response = await fetch(`${API_URL}/check-auth`, {
    credentials: 'include',
  });
  if (!response.ok) {
    throw new Error('Failed to check authentication status');
  }
  return response.json();
};

export const fetchDriveFiles = async (folderId = 'root') => {
  const response = await fetch(`${API_URL}/drive?folder_id=${folderId}`, {
    credentials: 'include',
  });
  if (!response.ok) {
    throw new Error('Failed to fetch drive files');
  }
  return response.json();
};

export const openDriveFile = async (fileId) => {
  const response = await fetch(`${API_URL}/drive/${fileId}/open`, {
    credentials: 'include',
  });
  if (!response.ok) {
    throw new Error('Failed to open drive file');
  }
  return response.json();
};

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

export const moveFile = async (fileId, newFolderId) => {
  const response = await fetch(`${API_URL}/drive/move-file`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ fileId, newFolderId }),
  });
  if (!response.ok) {
    throw new Error('Failed to move file');
  }
  return response.json();
};

export const deleteFile = async (fileId) => {
  const response = await fetch(`${API_URL}/drive/${fileId}`, {
    method: 'DELETE',
    credentials: 'include',
  });
  if (!response.ok) {
    throw new Error('Failed to delete file');
  }
  return response.json();
};

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

export const copyFile = async (fileId) => {
  const response = await fetch(`${API_URL}/drive/copy-file`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ fileId }),
  });
  if (!response.ok) {
    throw new Error('Failed to copy file');
  }
  return response.json();
};

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
    throw new Error('Failed to move files');
  }
  return response.json();
};

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
    throw new Error('Failed to delete files');
  }
  return response.json();
};

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
    throw new Error('Failed to copy files');
  }
  return response.json();
};