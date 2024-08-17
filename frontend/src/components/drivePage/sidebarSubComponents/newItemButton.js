import React, { useState, useRef, useEffect } from 'react';
import { useDrive } from '../../../contexts/driveContext';
import '../sidebar.css';

import FileUploadIcon from '@mui/icons-material/FileUpload';
import DriveFolderUploadIcon from '@mui/icons-material/DriveFolderUpload';
import CreateNewFolderIcon from '@mui/icons-material/CreateNewFolder';
import DescriptionIcon from '@mui/icons-material/Description';
import TableChartIcon from '@mui/icons-material/TableChart';
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';

const NewItemButton = () => {
  const {
    handleCreateFolder,
    handleUploadFile,
    handleUploadFolder,
    handleCreateDoc,
    handleCreateSheet
  } = useDrive();

  const [isOpen, setIsOpen] = useState(false);
  const fileInputRef = useRef(null);
  const folderInputRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    const handleTouchStart = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('touchstart', handleTouchStart);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('touchstart', handleTouchStart);
    };
  }, []);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      handleUploadFile(file);
    }
    event.target.value = '';
    setIsOpen(false);
  };

  const handleFolderChange = (event) => {
    const files = event.target.files;
    if (files.length > 0) {
      handleUploadFolder(files);
    }
    event.target.value = '';
    setIsOpen(false);
  };

  const handleButtonClick = () => {
    setIsOpen(!isOpen);
  };

  const handleMenuItemClick = (action) => {
    if (typeof action === 'function') {
      action();
    }
    setIsOpen(false);
  };

  const menuItems = [
    { icon: <CreateNewFolderIcon />, text: 'New Folder', action: handleCreateFolder },
    { icon: <FileUploadIcon />, text: 'Upload File', action: () => fileInputRef.current.click() },
    { icon: <DriveFolderUploadIcon />, text: 'Upload Folder', action: () => folderInputRef.current.click() },
    { icon: <DescriptionIcon />, text: 'New Google Doc', action: handleCreateDoc },
    { icon: <TableChartIcon />, text: 'New Google Sheet', action: handleCreateSheet },
  ];
  
  return (
    <div className="new-item-button-container" ref={containerRef}>
      <button className="new-item-button" onClick={handleButtonClick}>+ New</button>
      {isOpen && (
        <div className="dropdown-menu">
          {menuItems.map((item, index) => (
            <button key={index} onClick={() => handleMenuItemClick(item.action)}>
              <span className="dropdown-menu-icon">{item.icon}</span>
              <span className="dropdown-menu-text">{item.text}</span>
              <span className="dropdown-menu-arrow"><ArrowForwardIosIcon fontSize="small" /></span>
            </button>
          ))}
        </div>
      )}
      <input
        type="file"
        ref={fileInputRef}
        style={{ display: 'none' }}
        onChange={handleFileChange}
      />
      <input
        type="file"
        ref={folderInputRef}
        style={{ display: 'none' }}
        webkitdirectory="true"
        directory="true"
        multiple
        onChange={handleFolderChange}
      />
    </div>
  );
};

export default NewItemButton;