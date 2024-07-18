import React, { useState, useRef, useEffect } from 'react';
import './newItemButton.css';

const NewItemButton = ({ onCreateFolder, onUploadFile, onUploadFolder, onCreateDoc, onCreateSheet }) => {
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
      onUploadFile(file);
    }
    event.target.value = '';
    setIsOpen(false);
  };

  const handleFolderChange = (event) => {
    const files = event.target.files;
    if (files.length > 0) {
      onUploadFolder(files);
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

  return (
    <div className="new-item-button-container" ref={containerRef}>
      <button className="new-item-button" onClick={handleButtonClick}>+ New</button>
      {isOpen && (
        <div className="dropdown-menu">
          <button onClick={() => handleMenuItemClick(onCreateFolder)}>New Folder</button>
          <button onClick={() => fileInputRef.current.click()}>Upload File</button>
          <button onClick={() => folderInputRef.current.click()}>Upload Folder</button>
          <button onClick={() => handleMenuItemClick(onCreateDoc)}>New Google Doc</button>
          <button onClick={() => handleMenuItemClick(onCreateSheet)}>New Google Sheet</button>
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