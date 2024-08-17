import { renderHook, act } from '@testing-library/react-hooks';
import { useFileOperations } from '../../hooks/useFileOperations.js'
import * as driveApi from '../../services/drive_service.js';

// Mock the drive service API functions
jest.mock('../../services/drive_service');

describe('useFileOperations', () => {
  let currentFolder, getDriveFiles, setError;

  beforeEach(() => {
    currentFolder = { id: 'folderId123' };
    getDriveFiles = jest.fn();
    setError = jest.fn();
  });

  /**
   * Test for opening the create folder popup.
   * It should set the isNewFolderPopupOpen state to true.
   */
  it('should open the create folder popup', () => {
    const { result } = renderHook(() =>
      useFileOperations(currentFolder, getDriveFiles, setError)
    );

    act(() => {
      result.current.openCreateFolderPopup();
    });

    expect(result.current.isNewFolderPopupOpen).toBe(true);
  });

  /**
   * Test for handling folder creation.
   * It should call the drive API to create a folder and refresh the files.
   */
  it('should handle folder creation', async () => {
    const folderName = 'New Folder';
    driveApi.createFolder.mockResolvedValue({});

    const { result } = renderHook(() =>
      useFileOperations(currentFolder, getDriveFiles, setError)
    );

    await act(async () => {
      await result.current.handleCreateFolder(folderName);
    });

    expect(driveApi.createFolder).toHaveBeenCalledWith(currentFolder.id, folderName);
    expect(getDriveFiles).toHaveBeenCalledWith(currentFolder.id);
    expect(result.current.isNewFolderPopupOpen).toBe(false);
  });

  /**
   * Test for handling file upload.
   * It should call the drive API to upload a file and refresh the files.
   */
  it('should handle file upload', async () => {
    const file = new File(['file content'], 'test.txt', { type: 'text/plain' });
    driveApi.uploadFile.mockResolvedValue({});

    const { result } = renderHook(() =>
      useFileOperations(currentFolder, getDriveFiles, setError)
    );

    await act(async () => {
      await result.current.handleUploadFile(file);
    });

    expect(driveApi.uploadFile).toHaveBeenCalledWith(currentFolder.id, file);
    expect(getDriveFiles).toHaveBeenCalledWith(currentFolder.id);
  });

  /**
   * Test for handling folder upload.
   * It should call the drive API to upload multiple files (folder) and refresh the files.
   */
  it('should handle folder upload', async () => {
    const files = [
      new File(['file content 1'], 'file1.txt', { type: 'text/plain' }),
      new File(['file content 2'], 'file2.txt', { type: 'text/plain' })
    ];
    driveApi.uploadFolder.mockResolvedValue({});

    const { result } = renderHook(() =>
      useFileOperations(currentFolder, getDriveFiles, setError)
    );

    await act(async () => {
      await result.current.handleUploadFolder(files);
    });

    expect(driveApi.uploadFolder).toHaveBeenCalledWith(currentFolder.id, files);
    expect(getDriveFiles).toHaveBeenCalledWith(currentFolder.id);
  });

  /**
   * Test for handling Google Doc creation.
   * It should call the drive API to create a Google Doc and refresh the files.
   */
  it('should handle Google Doc creation', async () => {
    const response = { webViewLink: 'http://example.com/doc' };
    driveApi.createDoc.mockResolvedValue(response);

    const { result } = renderHook(() =>
      useFileOperations(currentFolder, getDriveFiles, setError)
    );

    window.open = jest.fn();

    await act(async () => {
      await result.current.handleCreateDoc();
    });

    expect(driveApi.createDoc).toHaveBeenCalledWith(currentFolder.id);
    expect(getDriveFiles).toHaveBeenCalledWith(currentFolder.id);
    expect(window.open).toHaveBeenCalledWith(response.webViewLink, '_blank', 'noopener,noreferrer');
  });

  /**
   * Test for handling Google Sheet creation.
   * It should call the drive API to create a Google Sheet and refresh the files.
   */
  it('should handle Google Sheet creation', async () => {
    const response = { webViewLink: 'http://example.com/sheet' };
    driveApi.createSheet.mockResolvedValue(response);

    const { result } = renderHook(() =>
      useFileOperations(currentFolder, getDriveFiles, setError)
    );

    window.open = jest.fn();

    await act(async () => {
      await result.current.handleCreateSheet();
    });

    expect(driveApi.createSheet).toHaveBeenCalledWith(currentFolder.id);
    expect(getDriveFiles).toHaveBeenCalledWith(currentFolder.id);
    expect(window.open).toHaveBeenCalledWith(response.webViewLink, '_blank', 'noopener,noreferrer');
  });

  /**
   * Test for handling file upload with no file selected.
   * It should set an error message.
   */
  it('should set an error when no file is selected for upload', async () => {
    const { result } = renderHook(() =>
      useFileOperations(currentFolder, getDriveFiles, setError)
    );

    await act(async () => {
      await result.current.handleUploadFile(null);
    });

    expect(setError).toHaveBeenCalledWith('No file selected for upload.');
  });

  /**
   * Test for handling folder upload with no folder selected.
   * It should set an error message.
   */
  it('should set an error when no folder is selected for upload', async () => {
    const { result } = renderHook(() =>
      useFileOperations(currentFolder, getDriveFiles, setError)
    );

    await act(async () => {
      await result.current.handleUploadFolder([]);
    });

    expect(setError).toHaveBeenCalledWith('No folder selected for upload.');
  });

  /**
   * Test for handling folder creation with an empty folder name.
   * It should not call the drive API and should not close the popup.
   */
  it('should not create a folder if folder name is empty', async () => {
    const { result } = renderHook(() =>
      useFileOperations(currentFolder, getDriveFiles, setError)
    );

    await act(async () => {
      await result.current.handleCreateFolder('');
    });

    expect(driveApi.createFolder).not.toHaveBeenCalled();
    expect(result.current.isNewFolderPopupOpen).toBe(false);
  });
});
