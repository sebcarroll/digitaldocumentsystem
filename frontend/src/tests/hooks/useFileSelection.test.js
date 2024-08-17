import { renderHook, act } from '@testing-library/react-hooks';
import { useFileSelection } from '../../hooks/useFileSelection.js';
import * as driveApi from '../../services/drive_service.js';

// Mock the drive service API functions
jest.mock('../../services/drive_service');

describe('useFileSelection', () => {
  let getDriveFiles, currentFolder, setError;

  beforeEach(() => {
    getDriveFiles = jest.fn();
    currentFolder = { id: 'folderId123' };
    setError = jest.fn();
  });

  /**
   * Test for handling file selection.
   * It should select or deselect a file based on its current selection state.
   */
  it('should handle file selection', async () => {
    const file = { id: 'fileId123' };
    const { result } = renderHook(() =>
      useFileSelection(getDriveFiles, currentFolder, setError)
    );
  
    act(() => {
      result.current.setShowActionMenu(true);
    });
  
    // Add a slight delay to ensure state is updated before selection
    await new Promise(r => setTimeout(r, 100));
  
    act(() => {
      result.current.handleFileSelect(file);
    });
  
    expect(result.current.selectedFiles).toContain(file);
  });

  /**
   * Test for handling the 'More' button click.
   * It should set the selected file and show the action menu.
   */
  it('should handle the More button click', () => {
    const file = { id: 'fileId123' };
    const event = { stopPropagation: jest.fn() };

    const { result } = renderHook(() =>
      useFileSelection(getDriveFiles, currentFolder, setError)
    );

    act(() => {
      result.current.handleMoreClick(event, file);
    });

    expect(result.current.selectedFiles).toContain(file);
    expect(result.current.showActionMenu).toBe(true);
  });

  /**
   * Test for handling file movement.
   * It should move the selected files to a new folder and refresh the file list.
   */
  it('should handle file movement', async () => {
    const fileIds = ['fileId123'];
    const newFolderId = 'newFolderId';
    driveApi.moveFiles.mockResolvedValue();

    const { result } = renderHook(() =>
      useFileSelection(getDriveFiles, currentFolder, setError)
    );

    await act(async () => {
      await result.current.handleMove(fileIds, newFolderId);
    });

    expect(driveApi.moveFiles).toHaveBeenCalledWith(fileIds, newFolderId);
    expect(getDriveFiles).toHaveBeenCalledWith(currentFolder.id);
  });

  /**
   * Test for handling file deletion.
   * It should delete the selected files and refresh the file list.
   */
  it('should handle file deletion', async () => {
    const file = { id: 'fileId123' };
    driveApi.deleteFiles.mockResolvedValue();

    const { result } = renderHook(() =>
      useFileSelection(getDriveFiles, currentFolder, setError)
    );

    act(() => {
      result.current.setSelectedFiles([file]);
    });

    await act(async () => {
      await result.current.handleDelete();
    });

    expect(driveApi.deleteFiles).toHaveBeenCalledWith([file.id]);
    expect(getDriveFiles).toHaveBeenCalledWith(currentFolder.id);
    expect(result.current.selectedFiles).toHaveLength(0);
  });

  /**
   * Test for handling copying file link.
   * It should copy the file link to the clipboard and clear the selection.
   */
  it('should handle copying file link', async () => {
    const file = { id: 'fileId123' };
    const response = { webViewLink: 'http://example.com/link' };
    driveApi.openDriveFile.mockResolvedValue(response);
    global.navigator.clipboard = { writeText: jest.fn() };
    global.alert = jest.fn();

    const { result } = renderHook(() =>
      useFileSelection(getDriveFiles, currentFolder, setError)
    );

    act(() => {
      result.current.setSelectedFiles([file]);
    });

    await act(async () => {
      await result.current.handleCopyLink();
    });

    expect(driveApi.openDriveFile).toHaveBeenCalledWith(file.id);
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(response.webViewLink);
    expect(alert).toHaveBeenCalledWith('Link copied to clipboard!');
    expect(result.current.selectedFiles).toHaveLength(0);
  });

  /**
   * Test for opening the rename popup.
   * It should set the file to rename and open the rename popup.
   */
  it('should open the rename popup', () => {
    const file = { id: 'fileId123' };
  
    const { result } = renderHook(() =>
      useFileSelection(getDriveFiles, currentFolder, setError)
    );
  
    // Simulate selecting the file
    act(() => {
      result.current.setSelectedFiles([file]);
    });
  
    // Ensure the file is selected
    expect(result.current.selectedFiles).toContain(file);
  
    // Simulate opening the rename popup
    act(() => {
      result.current.openRenamePopup();
    });
  
    // Check if fileToRename is correctly set
    expect(result.current.fileToRename).toBe(file);
    expect(result.current.isRenamePopupOpen).toBe(true);
  });
  
  /**
   * Test for handling the act of renaming.
   * It should rename the file, refresh the file list, and close the rename popup.
   */
  it('should handle file renaming', async () => {
    const file = { id: 'fileId123' };
    const newName = 'New File Name';
    driveApi.renameFile.mockResolvedValue();  // Mock the API call
  
    const { result } = renderHook(() =>
      useFileSelection(getDriveFiles, currentFolder, setError)
    );
  
    // Simulate selecting the file
    act(() => {
      result.current.setSelectedFiles([file]);
    });
  
    // Add a small delay to ensure state update
    await new Promise((resolve) => setTimeout(resolve, 0));
  
    // Simulate opening the rename popup
    act(() => {
      result.current.openRenamePopup();
    });
  
    // Check if fileToRename is correctly set
    expect(result.current.fileToRename).toBe(file);
  
    // Simulate renaming the file
    await act(async () => {
      await result.current.handleRename(newName);
    });
  
    // Verify the API was called with the correct arguments
    expect(driveApi.renameFile).toHaveBeenCalledWith(file.id, newName);
    
    // Verify that the file list is refreshed
    expect(getDriveFiles).toHaveBeenCalledWith(currentFolder.id);
  
    // Ensure the rename popup is closed and the state is reset
    expect(result.current.fileToRename).toBe(null);
    expect(result.current.isRenamePopupOpen).toBe(false);
    expect(result.current.selectedFiles).toHaveLength(0);
  });  
  
  /**
   * Test for handling making a copy of files.
   * It should copy the selected files and refresh the file list.
   */
  it('should handle making a copy of files', async () => {
    const file = { id: 'fileId123', mimeType: 'application/pdf' };
    driveApi.copyFiles.mockResolvedValue();

    const { result } = renderHook(() =>
      useFileSelection(getDriveFiles, currentFolder, setError)
    );

    act(() => {
      result.current.setSelectedFiles([file]);
    });

    await act(async () => {
      await result.current.handleMakeCopy();
    });

    expect(driveApi.copyFiles).toHaveBeenCalledWith([file.id]);
    expect(getDriveFiles).toHaveBeenCalledWith(currentFolder.id);
    expect(result.current.selectedFiles).toHaveLength(0);
  });

  /**
   * Test for closing the action menu.
   * It should close the action menu and clear selected files.
   */
  it('should close the action menu and clear selected files', () => {
    const file = { id: 'fileId123' };

    const { result } = renderHook(() =>
      useFileSelection(getDriveFiles, currentFolder, setError)
    );

    act(() => {
      result.current.setSelectedFiles([file]);
      result.current.setShowActionMenu(true);
    });

    act(() => {
      result.current.handleCloseActionMenu();
    });

    expect(result.current.showActionMenu).toBe(false);
    expect(result.current.selectedFiles).toHaveLength(0);
  });

  /**
   * Test to check if the selected file is a folder.
   * It should return true if the selected file is a folder.
   */
  it('should check if the selected file is a folder', () => {
    const folder = { id: 'folderId123', mimeType: 'application/vnd.google-apps.folder' };
    const file = { id: 'fileId123', mimeType: 'application/pdf' };

    const { result } = renderHook(() =>
      useFileSelection(getDriveFiles, currentFolder, setError)
    );

    act(() => {
      result.current.setSelectedFiles([folder]);
    });

    expect(result.current.isFolder).toBe(true);

    act(() => {
      result.current.setSelectedFiles([file]);
    });

    expect(result.current.isFolder).toBe(false);
  });
});
