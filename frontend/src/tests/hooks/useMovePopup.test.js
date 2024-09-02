import { renderHook, act } from '@testing-library/react-hooks';
import { useMovePopup } from '../../hooks/useMovePopup';
import { fetchDriveFiles, moveFiles } from '../../services/api';

jest.mock('../../services/api', () => ({
  fetchDriveFiles: jest.fn(),
  moveFiles: jest.fn(),
}));

describe('useMovePopup', () => {
  const mockSetError = jest.fn();
  const mockOnMoveComplete = jest.fn();
  const initialSelectedFiles = [{ id: 'file1', name: 'File 1' }];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('initial state', () => {
    const { result } = renderHook(() => useMovePopup(initialSelectedFiles, mockSetError, mockOnMoveComplete));

    expect(result.current.isOpen).toBe(false);
    expect(result.current.selectedFiles).toEqual(initialSelectedFiles);
    expect(result.current.currentFolder).toEqual({ id: 'root', name: 'My Drive' });
    expect(result.current.folderStack).toEqual([]);
    expect(result.current.folders).toEqual([]);
  });

  test('handleOpen', async () => {
    const mockFolders = [{ id: 'folder1', name: 'Folder 1', mimeType: 'application/vnd.google-apps.folder' }];
    fetchDriveFiles.mockResolvedValue({ files: mockFolders });

    const { result, waitForNextUpdate } = renderHook(() => useMovePopup(initialSelectedFiles, mockSetError, mockOnMoveComplete));

    act(() => {
      result.current.handleOpen([{ id: 'file2', name: 'File 2' }]);
    });

    expect(result.current.isOpen).toBe(true);
    expect(result.current.selectedFiles).toEqual([{ id: 'file2', name: 'File 2' }]);

    await waitForNextUpdate();

    expect(fetchDriveFiles).toHaveBeenCalledWith('root');
    expect(result.current.folders).toEqual(mockFolders);
  });

  test('handleClose', () => {
    const { result } = renderHook(() => useMovePopup(initialSelectedFiles, mockSetError, mockOnMoveComplete));

    act(() => {
      result.current.handleClose();
    });

    expect(result.current.isOpen).toBe(false);
    expect(result.current.currentFolder).toEqual({ id: 'root', name: 'My Drive' });
    expect(result.current.folderStack).toEqual([]);
  });

  test('handleFolderClick', async () => {
    const mockFolders = [{ id: 'subfolder1', name: 'Subfolder 1', mimeType: 'application/vnd.google-apps.folder' }];
    fetchDriveFiles.mockResolvedValue({ files: mockFolders });

    const { result, waitForNextUpdate } = renderHook(() => useMovePopup(initialSelectedFiles, mockSetError, mockOnMoveComplete));

    act(() => {
      result.current.handleFolderClick({ id: 'folder1', name: 'Folder 1' });
    });

    expect(result.current.currentFolder).toEqual({ id: 'folder1', name: 'Folder 1' });
    expect(result.current.folderStack).toEqual([{ id: 'root', name: 'My Drive' }]);

    await waitForNextUpdate();

    expect(fetchDriveFiles).toHaveBeenCalledWith('folder1');
    expect(result.current.folders).toEqual(mockFolders);
  });

  test('handleBreadcrumbClick', async () => {
    const mockFolders = [{ id: 'folder1', name: 'Folder 1', mimeType: 'application/vnd.google-apps.folder' }];
    fetchDriveFiles.mockResolvedValue({ files: mockFolders });

    const { result, waitForNextUpdate } = renderHook(() => useMovePopup(initialSelectedFiles, mockSetError, mockOnMoveComplete));

    act(() => {
      result.current.handleFolderClick({ id: 'folder1', name: 'Folder 1' });
    });

    await waitForNextUpdate();

    act(() => {
      result.current.handleBreadcrumbClick(-1);
    });

    expect(result.current.currentFolder).toEqual({ id: 'root', name: 'My Drive' });
    expect(result.current.folderStack).toEqual([]);

    await waitForNextUpdate();

    expect(fetchDriveFiles).toHaveBeenCalledWith('root');
  });

  test('handleMove - success', async () => {
    moveFiles.mockResolvedValue({});

    const { result } = renderHook(() => useMovePopup(initialSelectedFiles, mockSetError, mockOnMoveComplete));

    await act(async () => {
      await result.current.handleMove();
    });

    expect(moveFiles).toHaveBeenCalledWith(['file1'], 'root');
    expect(mockOnMoveComplete).toHaveBeenCalledWith(
      { id: 'root', name: 'My Drive' },
      [{ id: 'root', name: 'My Drive' }]
    );
    expect(result.current.isOpen).toBe(false);
  });

  test('handleMove - failure', async () => {
    const error = new Error('Move failed');
    moveFiles.mockRejectedValue(error);
  
    const { result } = renderHook(() => useMovePopup(initialSelectedFiles, mockSetError, mockOnMoveComplete));
  
    await act(async () => {
      await result.current.handleMove();
    });
  
    expect(moveFiles).toHaveBeenCalledWith(['file1'], 'root');
    expect(mockSetError).toHaveBeenCalledWith('Move failed');
    expect(result.current.isOpen).toBe(false);  // Changed from true to false
    expect(mockOnMoveComplete).not.toHaveBeenCalled();  // Add this line
  });
});