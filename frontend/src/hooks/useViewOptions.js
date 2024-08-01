// useViewOptions.js
import { useState, useCallback } from 'react';

export const useViewOptions = () => {
  const [filesActive, setFilesActive] = useState(true);
  const [foldersActive, setFoldersActive] = useState(true);
  const [listLayoutActive, setListLayoutActive] = useState(false);

  const handleFilesClick = useCallback(() => setFilesActive(prev => !prev), []);
  const handleFoldersClick = useCallback(() => setFoldersActive(prev => !prev), []);
  const handleListLayoutClick = useCallback(() => setListLayoutActive(true), []);
  const handleGridLayoutClick = useCallback(() => setListLayoutActive(false), []);

  return {
    filesActive,
    foldersActive,
    listLayoutActive,
    handleFilesClick,
    handleFoldersClick,
    handleListLayoutClick,
    handleGridLayoutClick
  };
};