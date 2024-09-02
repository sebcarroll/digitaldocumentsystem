import { renderHook, act } from '@testing-library/react-hooks';
import { useUploadDocument } from '../../hooks/useUploadDocument';
import { fetchDriveFiles } from '../../services/api'; 
import { useFileSelection } from '../../hooks/useFileSelection';

// Mock the dependencies
jest.mock('../../services/api', () => ({
  fetchDriveFiles: jest.fn(),
}));

jest.mock('../../hooks/useFileSelection', () => ({
  useFileSelection: jest.fn(),
}));


describe('useUploadDocument', () => {
  const mockSetError = jest.fn();
  const mockGetDriveFiles = jest.fn();
  const mockSetShowActionMenu = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    useFileSelection.mockReturnValue({
      setShowActionMenu: mockSetShowActionMenu,
    });
  });

  test('initial state', () => {
    const { result } = renderHook(() => useUploadDocument(mockSetError));

    expect(result.current.isOpen).toBe(false);
    expect(result.current.currentFolder).toEqual({ id: 'root', name: 'My Drive' });
    expect(result.current.folderStack).toEqual([]);
    expect(result.current.items).toEqual([]);
    expect(result.current.selectedFiles).toEqual([]);
  });

  test('handleOpen', async () => {
    const mockFiles = [{ id: 'file1', name: 'File 1' }];
    fetchDriveFiles.mockResolvedValue({ files: mockFiles });

    const { result, waitForNextUpdate } = renderHook(() => useUploadDocument(mockSetError));

    act(() => {
      result.current.handleOpen();
    });

    expect(result.current.isOpen).toBe(true);
    expect(fetchDriveFiles).toHaveBeenCalledWith('root');

    await waitForNextUpdate();

    expect(result.current.items).toEqual(mockFiles);
  });

  test('handleClose', () => {
    const { result } = renderHook(() => useUploadDocument(mockSetError));

    act(() => {
      result.current.handleClose();
    });

    expect(result.current.isOpen).toBe(false);
    expect(result.current.currentFolder).toEqual({ id: 'root', name: 'My Drive' });
    expect(result.current.folderStack).toEqual([]);
    expect(result.current.selectedFiles).toEqual([]);
    expect(mockSetShowActionMenu).toHaveBeenCalledWith(false);
  });

  test('handleFolderClick', async () => {
    const mockFiles = [{ id: 'file2', name: 'File 2' }];
    fetchDriveFiles.mockResolvedValue({ files: mockFiles });

    const { result, waitForNextUpdate } = renderHook(() => useUploadDocument(mockSetError));

    act(() => {
      result.current.handleFolderClick({ id: 'folder1', name: 'Folder 1' });
    });

    expect(result.current.currentFolder).toEqual({ id: 'folder1', name: 'Folder 1' });
    expect(result.current.folderStack).toEqual([{ id: 'root', name: 'My Drive' }]);
    expect(fetchDriveFiles).toHaveBeenCalledWith('folder1');

    await waitForNextUpdate();

    expect(result.current.items).toEqual(mockFiles);
  });

  test('handleBreadcrumbClick', async () => {
    const mockFiles = [{ id: 'file3', name: 'File 3' }];
    fetchDriveFiles.mockResolvedValue({ files: mockFiles });

    const { result, waitForNextUpdate } = renderHook(() => useUploadDocument(mockSetError));

    // Setup initial state
    act(() => {
      result.current.handleFolderClick({ id: 'folder1', name: 'Folder 1' });
    });

    await waitForNextUpdate();

    act(() => {
      result.current.handleBreadcrumbClick(-1); // Go back to root
    });

    expect(result.current.currentFolder).toEqual({ id: 'root', name: 'My Drive' });
    expect(result.current.folderStack).toEqual([]);
    expect(fetchDriveFiles).toHaveBeenCalledWith('root');

    await waitForNextUpdate();

    expect(result.current.items).toEqual(mockFiles);
  });

  test('handleFileSelect', () => {
    const { result } = renderHook(() => useUploadDocument(mockSetError));

    act(() => {
      result.current.handleFileSelect({ id: 'file1', name: 'File 1' });
    });

    expect(result.current.selectedFiles).toEqual([{ id: 'file1', name: 'File 1' }]);

    act(() => {
      result.current.handleFileSelect({ id: 'file1', name: 'File 1' });
    });

    expect(result.current.selectedFiles).toEqual([]);
  });

  test('handleUpload', () => {
    const { result } = renderHook(() => useUploadDocument(mockSetError));

    act(() => {
      result.current.handleFileSelect({ id: 'file1', name: 'File 1' });
    });

    const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

    act(() => {
      result.current.handleUpload();
    });

    expect(consoleSpy).toHaveBeenCalledWith('Uploading files:', [{ id: 'file1', name: 'File 1' }]);
    expect(result.current.isOpen).toBe(false);

    consoleSpy.mockRestore();
  });

  test('getDriveFiles error handling', async () => {
    const error = new Error('Fetch failed');
    fetchDriveFiles.mockRejectedValue(error);

    const { result, waitForNextUpdate } = renderHook(() => useUploadDocument(mockSetError));

    act(() => {
      result.current.handleOpen();
    });

    await waitForNextUpdate();

    expect(mockSetError).toHaveBeenCalledWith('Fetch failed');
    expect(result.current.items).toEqual([]);
  });
});