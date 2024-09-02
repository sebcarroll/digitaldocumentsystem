import { renderHook, act } from '@testing-library/react-hooks';
import { useFileSharing } from '../../hooks/useFileSharing.js';
import { searchUsers, getPeopleWithAccess, shareFile, updatePermission, removePermission, updateGeneralAccess, getCurrentUserRole } from '../../services/api.js';

jest.mock('../../services/api.js');

describe('useFileSharing', () => {
  const mockItems = [{ id: 'file1' }, { id: 'file2' }];

  beforeEach(() => {
    jest.clearAllMocks();
    // Set up default mock implementations
    getCurrentUserRole.mockResolvedValue({ role: 'owner', id: 'user1' });
    getPeopleWithAccess.mockResolvedValue({
      peopleWithAccess: [{ id: 'user1', role: 'viewer' }],
      currentUserRole: 'owner',
      currentUserId: 'user1',
      generalAccess: 'Restricted'
    });
    shareFile.mockResolvedValue({});
    updatePermission.mockResolvedValue({});
    removePermission.mockResolvedValue({});
    updateGeneralAccess.mockResolvedValue({});
  });

  test('should initialize with default values', async () => {
    const { result, waitForNextUpdate } = renderHook(() => useFileSharing(mockItems));
    
    await waitForNextUpdate();

    expect(result.current.email).toBe('');
    expect(result.current.searchResults).toEqual([]);
    expect(result.current.peopleWithAccess).toEqual([{ id: 'user1', role: 'viewer' }]);
    expect(result.current.generalAccess).toBe('Restricted');
    expect(result.current.currentUserRole).toBe('owner');
    expect(result.current.currentUserId).toBe('user1');
  });

  test('should update email and trigger user search on handleEmailChange', async () => {
    searchUsers.mockResolvedValue({ users: [{ id: 'user1', email: 'user1@example.com' }] });

    const { result, waitForNextUpdate } = renderHook(() => useFileSharing(mockItems));
    
    await waitForNextUpdate();

    await act(async () => {
      result.current.handleEmailChange('user');
      await waitForNextUpdate();
    });

    expect(result.current.email).toBe('user');
    expect(searchUsers).toHaveBeenCalledWith('user');
    expect(result.current.searchResults).toEqual([{ id: 'user1', email: 'user1@example.com' }]);
  });

  test('should add and remove pending emails', () => {
    const { result } = renderHook(() => useFileSharing(mockItems));

    act(() => {
      result.current.handleAddPendingEmail('user1@example.com');
      result.current.handleAddPendingEmail('user2@example.com');
    });

    expect(result.current.pendingEmails).toEqual(['user1@example.com', 'user2@example.com']);

    act(() => {
      result.current.handleRemovePendingEmail('user1@example.com');
    });

    expect(result.current.pendingEmails).toEqual(['user2@example.com']);
  });

  test('should share files with pending emails on handleShareWithPendingEmails', async () => {
    const { result, waitForNextUpdate } = renderHook(() => useFileSharing(mockItems));
    
    await waitForNextUpdate();

    act(() => {
      result.current.handleAddPendingEmail('user1@example.com');
      result.current.handleAddPendingEmail('user2@example.com');
    });

    await act(async () => {
      await result.current.handleShareWithPendingEmails();
    });

    expect(shareFile).toHaveBeenCalledTimes(4); // 2 files * 2 emails
    expect(result.current.pendingEmails).toEqual([]);
  });

  test('should update access level for a user on handleAccessLevelChange', async () => {
    const { result, waitForNextUpdate } = renderHook(() => useFileSharing(mockItems));
    
    await waitForNextUpdate();

    await act(async () => {
      await result.current.handleAccessLevelChange('user1', 'editor');
    });

    expect(updatePermission).toHaveBeenCalledTimes(2); // 2 files
    expect(updatePermission).toHaveBeenCalledWith('file1', 'user1', 'editor');
    expect(updatePermission).toHaveBeenCalledWith('file2', 'user1', 'editor');
  });

  test('should remove access for a user on handleRemoveAccess', async () => {
    const { result, waitForNextUpdate } = renderHook(() => useFileSharing(mockItems));
    
    await waitForNextUpdate();

    await act(async () => {
      await result.current.handleRemoveAccess('user1');
    });

    expect(removePermission).toHaveBeenCalledTimes(2); // 2 files
    expect(removePermission).toHaveBeenCalledWith('file1', 'user1');
    expect(removePermission).toHaveBeenCalledWith('file2', 'user1');
  });

  test('should update general access on handleGeneralAccessChange', async () => {
    const { result, waitForNextUpdate } = renderHook(() => useFileSharing(mockItems));
    
    await waitForNextUpdate();

    await act(async () => {
      await result.current.handleGeneralAccessChange('Anyone with the link');
    });

    expect(updateGeneralAccess).toHaveBeenCalledTimes(2); // 2 files
    expect(updateGeneralAccess).toHaveBeenCalledWith('file1', 'Anyone with the link', 'viewer');
    expect(updateGeneralAccess).toHaveBeenCalledWith('file2', 'Anyone with the link', 'viewer');
    expect(result.current.generalAccess).toBe('Anyone with the link');
  });
});