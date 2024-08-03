// useMovePopup.js
import { useState, useCallback, useEffect } from 'react';
import { fetchFolders } from '../services/api';

export const useMovePopup = (initialSelectedFiles, onMove, setError) => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('suggested');
  const [currentFolder, setCurrentFolder] = useState({ id: 'root', name: 'My Drive' });
  const [folderStack, setFolderStack] = useState([]);
  const [folders, setFolders] = useState([]);
  const [suggestedFolders, setSuggestedFolders] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState(initialSelectedFiles);

  const fetchFoldersData = useCallback(async (folderId = 'root') => {
    try {
      const fetchedFolders = await fetchFolders(folderId);
      setFolders(fetchedFolders);
    } catch (error) {
      console.error('Failed to fetch folders:', error);
      setError('Failed to fetch folders.');
    }
  }, [setError]);

  useEffect(() => {
    if (isOpen) {
      fetchFoldersData();
      // TODO: Implement logic to fetch suggested folders
      setSuggestedFolders([]);
    }
  }, [isOpen, fetchFoldersData]);

  const handleOpen = useCallback((files) => {
    setSelectedFiles(files);
    setIsOpen(true);
  }, []);

  const handleClose = useCallback(() => {
    setIsOpen(false);
    setActiveTab('suggested');
    setCurrentFolder({ id: 'root', name: 'My Drive' });
    setFolderStack([]);
  }, []);

  const handleTabClick = useCallback((tab) => {
    setActiveTab(tab);
    if (tab === 'all') {
      setCurrentFolder({ id: 'root', name: 'My Drive' });
      setFolderStack([]);
      fetchFoldersData();
    }
  }, [fetchFoldersData]);

  const handleFolderClick = useCallback(async (folder) => {
    setFolderStack(prev => [...prev, currentFolder]);
    setCurrentFolder(folder);
    fetchFoldersData(folder.id);
  }, [currentFolder, fetchFoldersData]);

  const handleBreadcrumbClick = useCallback((index) => {
    if (index < folderStack.length) {
      const newStack = folderStack.slice(0, index);
      const clickedFolder = index === -1 ? { id: 'root', name: 'My Drive' } : folderStack[index];
      setFolderStack(newStack);
      setCurrentFolder(clickedFolder);
      fetchFoldersData(clickedFolder.id);
    }
  }, [folderStack, fetchFoldersData]);

  const handleMove = useCallback(() => {
    onMove(selectedFiles.map(f => f.id), currentFolder.id);
    handleClose();
  }, [selectedFiles, currentFolder, onMove, handleClose]);

  return {
    isOpen,
    activeTab,
    currentFolder,
    folderStack,
    folders,
    suggestedFolders,
    selectedFiles,
    handleOpen,
    handleClose,
    handleTabClick,
    handleFolderClick,
    handleBreadcrumbClick,
    handleMove,
  };
};