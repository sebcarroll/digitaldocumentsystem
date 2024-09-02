import {
    checkAuth,
    fetchDriveFiles,
    createFolder,
    uploadFile,
    moveFiles,
    deleteFiles,
    getPeopleWithAccess,
    shareFile,
    sendQuery,
    fetchFolderTree,
    logoutUser,
    openDriveFile,
    uploadFolder,
    createDoc,
    createSheet,
    renameFile,
    copyFiles,
    searchUsers,
    getCurrentUserRole,
    updatePermission,
    removePermission,
    updateGeneralAccess,
    fetchFolders,
    addDocument,
    updateDocument,
    deleteDocument,
    uploadDocument,
    fetchFolderDetails,
    clearChatHistory,
    fetchUserInfo,
    updateDocumentSelection,
    uploadSelectedDocuments,
  } from '../../services/api';
  
  // Mock fetch globally
  global.fetch = jest.fn();
  
  const API_URL = process.env.REACT_APP_API_URL;
  
  describe('API functions', () => {
    beforeEach(() => {
      fetch.mockClear();
    });
  
    test('checkAuth makes a GET request to the correct endpoint', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ authenticated: true }),
      });
  
      const result = await checkAuth();
  
      expect(fetch).toHaveBeenCalledWith(`${API_URL}/check-auth`, {
        credentials: 'include',
      });
      expect(result).toEqual({ authenticated: true });
    });
  
    test('fetchDriveFiles makes a GET request with correct parameters', async () => {
        const mockFiles = [{ id: '1', name: 'file1' }];
        fetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ files: mockFiles }),
        });
      
        const result = await fetchDriveFiles('folder123', 'token456');
      
        expect(fetch).toHaveBeenCalledTimes(1);
        const [calledUrl, calledOptions] = fetch.mock.calls[0];
      
        // Parse the called URL
        const url = new URL(calledUrl);
      
        // Check the base URL
        expect(url.origin + url.pathname).toBe(`${API_URL}/drive`);
      
        // Check the query parameters
        expect(url.searchParams.get('folder_id')).toBe('folder123');
        expect(url.searchParams.get('page_token')).toBe('token456');
      
        // Check the options
        expect(calledOptions).toEqual({ credentials: 'include' });
      
        expect(result).toEqual({ files: mockFiles });
      });
  
    test('createFolder makes a POST request with correct body', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ id: 'newFolder123' }),
      });
  
      const result = await createFolder('parent456', 'New Folder');
  
      expect(fetch).toHaveBeenCalledWith(
        `${API_URL}/drive/create-folder`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ parentFolderId: 'parent456', folderName: 'New Folder' }),
        }
      );
      expect(result).toEqual({ id: 'newFolder123' });
    });
  
    test('uploadFile makes a POST request with FormData', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ id: 'file789' }),
      });
  
      const mockFile = new File(['file content'], 'test.txt', { type: 'text/plain' });
      const result = await uploadFile('folder123', mockFile);
  
      expect(fetch).toHaveBeenCalledWith(
        `${API_URL}/drive/upload-file`,
        expect.objectContaining({
          method: 'POST',
          credentials: 'include',
          body: expect.any(FormData),
        })
      );
      expect(result).toEqual({ id: 'file789' });
    });
  
    test('moveFiles makes a POST request with correct body', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true }),
      });
  
      const result = await moveFiles(['file1', 'file2'], 'newFolder123');
  
      expect(fetch).toHaveBeenCalledWith(
        `${API_URL}/drive/move-files`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ fileIds: ['file1', 'file2'], newFolderId: 'newFolder123' }),
        }
      );
      expect(result).toEqual({ success: true });
    });
  
    test('deleteFiles makes a POST request with correct body', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true }),
      });
  
      const result = await deleteFiles(['file1', 'file2']);
  
      expect(fetch).toHaveBeenCalledWith(
        `${API_URL}/drive/delete-files`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ fileIds: ['file1', 'file2'] }),
        }
      );
      expect(result).toEqual({ success: true });
    });
  
    test('getPeopleWithAccess makes a GET request to the correct endpoint', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ people: [{ id: 'user1', role: 'editor' }] }),
      });
  
      const result = await getPeopleWithAccess('file123');
  
      expect(fetch).toHaveBeenCalledWith(
        `${API_URL}/drive/file123/people-with-access`,
        { credentials: 'include' }
      );
      expect(result).toEqual({ people: [{ id: 'user1', role: 'editor' }] });
    });
  
    test('shareFile makes a POST request with correct body', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true }),
      });
  
      const result = await shareFile('file123', ['user1@example.com'], 'editor');
  
      expect(fetch).toHaveBeenCalledWith(
        `${API_URL}/drive/file123/share`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ emails: ['user1@example.com'], role: 'editor' }),
        }
      );
      expect(result).toEqual({ success: true });
    });
  
    test('sendQuery makes a POST request with correct body', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ response: 'Query response' }),
      });
  
      const result = await sendQuery('Test query');
  
      expect(fetch).toHaveBeenCalledWith(
        `${API_URL}/chat/query`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ query: 'Test query' }),
        }
      );
      expect(result).toEqual({ response: 'Query response' });
    });
  
    test('fetchFolderTree makes a GET request to the correct endpoint', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ tree: { id: 'root', children: [] } }),
      });
  
      const result = await fetchFolderTree();
  
      expect(fetch).toHaveBeenCalledWith(
        `${API_URL}/drive/folder-tree`,
        {
          method: 'GET',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
        }
      );
      expect(result).toEqual({ tree: { id: 'root', children: [] } });
    });
  
    test('logoutUser makes a GET request to the correct endpoint', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true }),
      });
  
      const result = await logoutUser();
  
      expect(fetch).toHaveBeenCalledWith(
        `${API_URL}/logout`,
        { method: 'GET', credentials: 'include' }
      );
      expect(result).toEqual({ success: true });
    });
  });

  test('openDriveFile makes a GET request to the correct endpoint', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ webViewLink: 'https://example.com/file' }),
    });

    const result = await openDriveFile('file123');

    expect(fetch).toHaveBeenCalledWith(
      `${API_URL}/drive/file123/open`,
      { credentials: 'include' }
    );
    expect(result).toEqual({ webViewLink: 'https://example.com/file' });
  });

  test('uploadFolder makes a POST request with FormData', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    });

    const mockFiles = [
      new File(['content1'], 'file1.txt', { type: 'text/plain' }),
      new File(['content2'], 'file2.txt', { type: 'text/plain' }),
    ];
    const result = await uploadFolder('folder123', mockFiles);

    expect(fetch).toHaveBeenCalledWith(
      `${API_URL}/drive/upload-folder`,
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
        body: expect.any(FormData),
      })
    );
    expect(result).toEqual({ success: true });
  });

  test('createDoc makes a POST request with correct body', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ id: 'doc123' }),
    });

    const result = await createDoc('folder123');

    expect(fetch).toHaveBeenCalledWith(
      `${API_URL}/drive/create-doc`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ folderId: 'folder123' }),
      }
    );
    expect(result).toEqual({ id: 'doc123' });
  });

  test('createSheet makes a POST request with correct body', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ id: 'sheet123' }),
    });

    const result = await createSheet('folder123');

    expect(fetch).toHaveBeenCalledWith(
      `${API_URL}/drive/create-sheet`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ folderId: 'folder123' }),
      }
    );
    expect(result).toEqual({ id: 'sheet123' });
  });

  test('renameFile makes a POST request with correct body', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    });

    const result = await renameFile('file123', 'New Name');

    expect(fetch).toHaveBeenCalledWith(
      `${API_URL}/drive/rename-file`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ fileId: 'file123', newName: 'New Name' }),
      }
    );
    expect(result).toEqual({ success: true });
  });

  test('copyFiles makes a POST request with correct body', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    });

    const result = await copyFiles(['file1', 'file2']);

    expect(fetch).toHaveBeenCalledWith(
      `${API_URL}/drive/copy-files`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ fileIds: ['file1', 'file2'] }),
      }
    );
    expect(result).toEqual({ success: true });
  });

  test('searchUsers makes a GET request with correct query parameter', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ users: [{ id: 'user1', name: 'User 1' }] }),
    });

    const result = await searchUsers('test query');

    expect(fetch).toHaveBeenCalledWith(
      '/api/search-users?q=test%20query'
    );
    expect(result).toEqual({ users: [{ id: 'user1', name: 'User 1' }] });
  });

  test('getCurrentUserRole makes a GET request to the correct endpoint', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ role: 'editor', id: 'user1' }),
    });

    const result = await getCurrentUserRole('file123');

    expect(fetch).toHaveBeenCalledWith(
      `${API_URL}/drive/file123/user-role`,
      { credentials: 'include' }
    );
    expect(result).toEqual({ role: 'editor', id: 'user1' });
  });

  test('updatePermission makes a POST request with correct body', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    });

    const result = await updatePermission('file123', 'permission1', 'editor');

    expect(fetch).toHaveBeenCalledWith(
      `${API_URL}/drive/file123/update-permission`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ permissionId: 'permission1', role: 'editor' }),
      }
    );
    expect(result).toEqual({ success: true });
  });

  test('removePermission makes a POST request with correct body', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    });

    const result = await removePermission('file123', 'permission1');

    expect(fetch).toHaveBeenCalledWith(
      `${API_URL}/drive/file123/remove-permission`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ permissionId: 'permission1' }),
      }
    );
    expect(result).toEqual({ success: true });
  });

  test('updateGeneralAccess makes a POST request with correct body', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    });

    const result = await updateGeneralAccess('file123', 'anyone', 'reader');

    expect(fetch).toHaveBeenCalledWith(
      `${API_URL}/drive/file123/update-general-access`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ access: 'anyone', linkRole: 'reader' }),
      }
    );
    expect(result).toEqual({ success: true });
  });

  test('fetchFolders makes a GET request with correct query parameter', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ folders: [{ id: 'folder1', name: 'Folder 1' }] }),
    });

    const result = await fetchFolders('parent123');

    expect(fetch).toHaveBeenCalledWith(
      `${API_URL}/drive/folders?parent_id=parent123`,
      { credentials: 'include' }
    );
    expect(result).toEqual({ folders: [{ id: 'folder1', name: 'Folder 1' }] });
  });

  test('addDocument makes a POST request with correct body', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    });

    const document = { id: 'doc1', content: 'Test content' };
    const result = await addDocument(document);

    expect(fetch).toHaveBeenCalledWith(
      `${API_URL}/chat/document`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ document }),
      }
    );
    expect(result).toEqual({ success: true });
  });

  test('updateDocument makes a PUT request with correct body', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    });

    const document = { id: 'doc1', content: 'Updated content' };
    const result = await updateDocument(document);

    expect(fetch).toHaveBeenCalledWith(
      `${API_URL}/chat/document`,
      {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ document }),
      }
    );
    expect(result).toEqual({ success: true });
  });

  test('deleteDocument makes a DELETE request with correct body', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    });

    const result = await deleteDocument('doc1');

    expect(fetch).toHaveBeenCalledWith(
      `${API_URL}/chat/document`,
      {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ document_id: 'doc1' }),
      }
    );
    expect(result).toEqual({ success: true });
  });

  test('uploadDocument makes a POST request with FormData', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    });

    const document = { id: 'doc1', content: 'Test content', type: 'text/plain' };
    const result = await uploadDocument(document);

    expect(fetch).toHaveBeenCalledWith(
      `${API_URL}/drive/upload-file`,
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
        body: expect.any(FormData),
      })
    );
    expect(result).toEqual({ success: true });
  });

  test('fetchFolderDetails makes a GET request to the correct endpoint', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ id: 'folder1', name: 'Folder 1' }),
    });

    const result = await fetchFolderDetails('folder1');

    expect(fetch).toHaveBeenCalledWith(
      `${API_URL}/drive/folder1/details`,
      {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      }
    );
    expect(result).toEqual({ id: 'folder1', name: 'Folder 1' });
  });

  test('clearChatHistory makes a POST request to the correct endpoint', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
    });

    await clearChatHistory();

    expect(fetch).toHaveBeenCalledWith(
      `${API_URL}/chat/clear`,
      {
        method: 'POST',
        credentials: 'include',
      }
    );
  });

  test('fetchUserInfo makes a GET request to the correct endpoint', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ id: 'user1', name: 'User 1' }),
    });

    const result = await fetchUserInfo();

    expect(fetch).toHaveBeenCalledWith(
      `${API_URL}/user-info`,
      { credentials: 'include' }
    );
    expect(result).toEqual({ id: 'user1', name: 'User 1' });
  });

  test('updateDocumentSelection makes a POST request with correct body', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    });

    const result = await updateDocumentSelection('file1', true);

    expect(fetch).toHaveBeenCalledWith(
      `${API_URL}/chat/update-document-selection`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ fileId: 'file1', isSelected: true }),
      }
    );
    expect(result).toEqual({ success: true });
  });

  test('uploadSelectedDocuments makes a POST request with correct body', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    });

    const selectedFiles = [
      { id: 'file1', name: 'File 1' },
      { id: 'file2', name: 'File 2' },
    ];
    const result = await uploadSelectedDocuments(selectedFiles);

    expect(fetch).toHaveBeenCalledWith(
      `${API_URL}/chat/upload-documents`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ fileIds: ['file1', 'file2'], fileNames: ['File 1', 'File 2'] }),
      }
    );
    expect(result).toEqual({ success: true });
  });
