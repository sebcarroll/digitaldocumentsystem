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

export const searchUsers = async (query) => {
  try {
    const response = await fetch(`/api/search-users?q=${encodeURIComponent(query)}`);
    if (!response.ok) {
      throw new Error('Failed to search users');
    }
    return await response.json();
  } catch (error) {
    console.error('Error searching users:', error);
    return { users: [] };
  }
};

export const getPeopleWithAccess = async (fileId) => {
  const response = await fetch(`${API_URL}/drive/${fileId}/people-with-access`, {
    credentials: 'include',
  });
  if (!response.ok) {
    throw new Error('Failed to get people with access');
  }
  const data = await response.json();
  console.log('API response data:', data); // Log the response data
  return data;
};

export const shareFile = async (fileId, emails, role) => {
  const response = await fetch(`${API_URL}/drive/${fileId}/share`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ emails, role }),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to share file');
  }
  return response.json();
};

export const getCurrentUserRole = async (fileId) => {
  const response = await fetch(`${API_URL}/drive/${fileId}/user-role`, {
    credentials: 'include',
  });
  if (!response.ok) {
    throw new Error('Failed to get current user role');
  }
  const data = await response.json();
  return { role: data.role, id: data.id };
};

export const updatePermission = async (fileId, permissionId, role) => {
  const response = await fetch(`${API_URL}/drive/${fileId}/update-permission`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ permissionId, role }),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to update permission');
  }
  return response.json();
};

export const removePermission = async (fileId, permissionId) => {
  const response = await fetch(`${API_URL}/drive/${fileId}/remove-permission`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ permissionId }),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to remove permission');
  }
  return response.json();
};

export const updateGeneralAccess = async (fileId, newAccess, linkRole) => {
  const response = await fetch(`${API_URL}/drive/${fileId}/update-general-access`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ access: newAccess, linkRole: linkRole }),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || `Failed to update general access: ${response.statusText}`);
  }
  return response.json();
};

export const fetchFolders = async (folderId = 'root') => {
  const response = await fetch(`${API_URL}/drive/folders?parent_id=${folderId}`, {
    credentials: 'include',
  });
  if (!response.ok) {
    throw new Error('Failed to fetch folders');
  }
  return response.json();
};

export const sendQuery = async (query) => {
  const response = await fetch(`${API_URL}/chat/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ query }),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to process query');
  }
  return response.json();
};

export const addDocument = async (document) => {
  const response = await fetch(`${API_URL}/chat/document`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ document }),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to add document');
  }
  return response.json();
};

export const updateDocument = async (document) => {
  const response = await fetch(`${API_URL}/chat/document`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ document }),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to update document');
  }
  return response.json();
};

export const deleteDocument = async (documentId) => {
  const response = await fetch(`${API_URL}/chat/document`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ document_id: documentId }),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Failed to delete document');
  }
  return response.json();
};

