// useFolderNavigation.test.js
import { renderHook, act } from '@testing-library/react-hooks';
import { useFolderNavigation } from '../../hooks/useFolderNavigation';
import { openDriveFile } from '../../services/drive_service';

// Mock the drive_service
jest.mock('../../services/drive_service', () => ({
  openDriveFile: jest.fn(),
}));

/**
 * Test suite for the useFolderNavigation hook.
 * These tests cover the main functionality of the hook, including
 * initialization, navigation, file opening, and error handling.
 */
describe('useFolderNavigation', () => {
  let setError;

  beforeEach(() => {
    setError = jest.fn();
    window.open = jest.fn();
  });

  /**
   * Test case: Initialization
   * Ensures that the hook initializes with the root folder and an empty stack.
   */
  it('should initialize with root folder', () => {
    const { result } = renderHook(() => useFolderNavigation(setError));
    expect(result.current.currentFolder).toEqual({ id: 'root', name: 'Home' });
    expect(result.current.folderStack).toEqual([]);
  });

  /**
   * Test case: Folder navigation
   * Verifies that clicking on a folder updates the current folder and stack correctly.
   */
  it('should handle folder click', () => {
    const { result } = renderHook(() => useFolderNavigation(setError));
    act(() => {
      result.current.handleFileClick({ id: 'folder1', name: 'Folder 1', mimeType: 'application/vnd.google-apps.folder' });
    });
    expect(result.current.currentFolder).toEqual({ id: 'folder1', name: 'Folder 1' });
    expect(result.current.folderStack).toEqual([{ id: 'root', name: 'Home' }]);
  });

  /**
   * Test case: File opening
   * Checks if clicking on a file triggers the openDriveFile function and opens the file in a new tab.
   */
  it('should handle file click', async () => {
    openDriveFile.mockResolvedValue({ webViewLink: 'https://example.com' });
    const { result } = renderHook(() => useFolderNavigation(setError));
    await act(async () => {
      await result.current.handleFileClick({ id: 'file1', name: 'File 1', mimeType: 'application/pdf' });
    });
    expect(openDriveFile).toHaveBeenCalledWith('file1');
    expect(window.open).toHaveBeenCalledWith('https://example.com', '_blank');
  });

  /**
   * Test case: Error handling
   * Ensures that errors during file opening are caught and the error state is updated.
   */
  it('should handle file open error', async () => {
    openDriveFile.mockRejectedValue(new Error('Failed to open'));
    const { result } = renderHook(() => useFolderNavigation(setError));
    await act(async () => {
      await result.current.handleFileClick({ id: 'file1', name: 'File 1', mimeType: 'application/pdf' });
    });
    expect(setError).toHaveBeenCalledWith('Failed to open file.');
  });

  /**
   * Test case: Back navigation
   * Verifies that the back functionality correctly returns to the previous folder.
   */
  it('should handle back click', () => {
    const { result } = renderHook(() => useFolderNavigation(setError));
    act(() => {
      result.current.handleFileClick({ id: 'folder1', name: 'Folder 1', mimeType: 'application/vnd.google-apps.folder' });
    });
    act(() => {
      result.current.handleBackClick();
    });
    expect(result.current.currentFolder).toEqual({ id: 'root', name: 'Home' });
    expect(result.current.folderStack).toEqual([]);
  });

  /**
   * Test case: Breadcrumb navigation
   * Checks if clicking on a breadcrumb correctly navigates to the specified folder in the hierarchy.
   */
  it('should handle breadcrumb click', () => {
    const { result } = renderHook(() => useFolderNavigation(setError));
    act(() => {
      result.current.handleFileClick({ id: 'folder1', name: 'Folder 1', mimeType: 'application/vnd.google-apps.folder' });
    });
    act(() => {
      result.current.handleFileClick({ id: 'folder2', name: 'Folder 2', mimeType: 'application/vnd.google-apps.folder' });
    });
    act(() => {
      result.current.handleBreadcrumbClick(0);
    });
    expect(result.current.currentFolder).toEqual({ id: 'root', name: 'Home' });
    expect(result.current.folderStack).toEqual([]);
  });
});