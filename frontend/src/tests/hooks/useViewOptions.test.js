import { renderHook, act } from '@testing-library/react-hooks';
import { useViewOptions } from '../../hooks/useViewOptions';

describe('useViewOptions', () => {
  test('initial state', () => {
    const { result } = renderHook(() => useViewOptions());

    expect(result.current.filesActive).toBe(true);
    expect(result.current.foldersActive).toBe(true);
    expect(result.current.listLayoutActive).toBe(false);
  });

  test('handleFilesClick toggles filesActive', () => {
    const { result } = renderHook(() => useViewOptions());

    act(() => {
      result.current.handleFilesClick();
    });

    expect(result.current.filesActive).toBe(false);

    act(() => {
      result.current.handleFilesClick();
    });

    expect(result.current.filesActive).toBe(true);
  });

  test('handleFoldersClick toggles foldersActive', () => {
    const { result } = renderHook(() => useViewOptions());

    act(() => {
      result.current.handleFoldersClick();
    });

    expect(result.current.foldersActive).toBe(false);

    act(() => {
      result.current.handleFoldersClick();
    });

    expect(result.current.foldersActive).toBe(true);
  });

  test('handleListLayoutClick sets listLayoutActive to true', () => {
    const { result } = renderHook(() => useViewOptions());

    act(() => {
      result.current.handleListLayoutClick();
    });

    expect(result.current.listLayoutActive).toBe(true);
  });

  test('handleGridLayoutClick sets listLayoutActive to false', () => {
    const { result } = renderHook(() => useViewOptions());

    // First, set listLayoutActive to true
    act(() => {
      result.current.handleListLayoutClick();
    });

    expect(result.current.listLayoutActive).toBe(true);

    // Then, set it back to false
    act(() => {
      result.current.handleGridLayoutClick();
    });

    expect(result.current.listLayoutActive).toBe(false);
  });

  test('multiple state changes work correctly', () => {
    const { result } = renderHook(() => useViewOptions());

    act(() => {
      result.current.handleFilesClick();
      result.current.handleFoldersClick();
      result.current.handleListLayoutClick();
    });

    expect(result.current.filesActive).toBe(false);
    expect(result.current.foldersActive).toBe(false);
    expect(result.current.listLayoutActive).toBe(true);

    act(() => {
      result.current.handleFilesClick();
      result.current.handleGridLayoutClick();
    });

    expect(result.current.filesActive).toBe(true);
    expect(result.current.foldersActive).toBe(false);
    expect(result.current.listLayoutActive).toBe(false);
  });
});