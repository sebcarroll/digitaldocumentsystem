// src/hooks/__tests__/useFolderNavigation.test.js

import { renderHook, act } from '@testing-library/react-hooks';
import { useFolderNavigation } from '../../hooks/useFolderNavigation';
import { openDriveFile } from '../../services/drive_service';

jest.mock('../../services/drive_service');

describe('useFolderNavigation', () => {
  let setError;
  let fetchDriveFiles;
  let windowOpenSpy;

  beforeEach(() => {
    setError = jest.fn();
    fetchDriveFiles = jest.fn().mockResolvedValue();
    windowOpenSpy = jest.spyOn(window, 'open').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.clearAllMocks();
    windowOpenSpy.mockRestore();
  });

  test('should initialize with root folder', () => {
    const { result } = renderHook(() => useFolderNavigation(setError, fetchDriveFiles));
    expect(result.current.currentFolder).toEqual({ id: 'root', name: 'Home' });
    expect(result.current.folderStack).toEqual([]);
  });

  test('should handle folder click', async () => {
    const { result } = renderHook(() => useFolderNavigation(setError, fetchDriveFiles));
    const folder = { id: 'folder1', name: 'Folder 1', mimeType: 'application/vnd.google-apps.folder' };

    await act(async () => {
      await result.current.handleFileClick(folder);
    });

    expect(result.current.currentFolder).toEqual({ id: 'folder1', name: 'Folder 1' });
    expect(result.current.folderStack).toEqual([{ id: 'root', name: 'Home' }]);
    expect(fetchDriveFiles).toHaveBeenCalledWith('folder1');
  });

  test('should handle file click', async () => {
    openDriveFile.mockResolvedValue({ webViewLink: 'https://example.com' });
    const { result } = renderHook(() => useFolderNavigation(setError, fetchDriveFiles));
    const file = { id: 'file1', name: 'File 1', mimeType: 'application/pdf' };

    await act(async () => {
      await result.current.handleFileClick(file);
    });

    expect(openDriveFile).toHaveBeenCalledWith('file1');
    expect(windowOpenSpy).toHaveBeenCalledWith('https://example.com', '_blank');
  });

  test('should handle back click', async () => {
    const { result } = renderHook(() => useFolderNavigation(setError, fetchDriveFiles));
    const folder1 = { id: 'folder1', name: 'Folder 1', mimeType: 'application/vnd.google-apps.folder' };
    const folder2 = { id: 'folder2', name: 'Folder 2', mimeType: 'application/vnd.google-apps.folder' };

    await act(async () => {
      await result.current.handleFileClick(folder1);
      await result.current.handleFileClick(folder2);
    });

    await act(async () => {
      await result.current.handleBackClick();
    });

    expect(result.current.currentFolder).toEqual({ id: 'folder1', name: 'Folder 1' });
    expect(result.current.folderStack).toEqual([{ id: 'root', name: 'Home' }]);
    expect(fetchDriveFiles).toHaveBeenCalledWith('folder1');
  });

  test('should handle breadcrumb click', async () => {
    const { result } = renderHook(() => useFolderNavigation(setError, fetchDriveFiles));
    const folder1 = { id: 'folder1', name: 'Folder 1', mimeType: 'application/vnd.google-apps.folder' };
    const folder2 = { id: 'folder2', name: 'Folder 2', mimeType: 'application/vnd.google-apps.folder' };

    await act(async () => {
      await result.current.handleFileClick(folder1);
      await result.current.handleFileClick(folder2);
    });

    await act(async () => {
      await result.current.handleBreadcrumbClick(0);
    });

    expect(result.current.currentFolder).toEqual({ id: 'root', name: 'Home' });
    expect(result.current.folderStack).toEqual([]);
    expect(fetchDriveFiles).toHaveBeenCalledWith('root');
  });

  test('should handle fetch folder contents error', async () => {
    fetchDriveFiles.mockRejectedValue(new Error('Fetch error'));
    const { result } = renderHook(() => useFolderNavigation(setError, fetchDriveFiles));
    const folder = { id: 'folder1', name: 'Folder 1', mimeType: 'application/vnd.google-apps.folder' };

    await act(async () => {
      await result.current.handleFileClick(folder);
    });

    expect(setError).toHaveBeenCalledWith('Failed to fetch folder contents.');
  });

  test('should handle open file error', async () => {
    openDriveFile.mockRejectedValue(new Error('Open file error'));
    const { result } = renderHook(() => useFolderNavigation(setError, fetchDriveFiles));
    const file = { id: 'file1', name: 'File 1', mimeType: 'application/pdf' };

    await act(async () => {
      await result.current.handleFileClick(file);
    });

    expect(setError).toHaveBeenCalledWith('Failed to open file.');
  });
});