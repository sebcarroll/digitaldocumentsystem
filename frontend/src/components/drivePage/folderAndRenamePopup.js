// src/components/FolderAndRenamePopup.js

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useDrive } from '../../contexts/driveContext';
import './popup.css';

/**
 * FolderAndRenamePopup component
 * @returns {React.ReactElement} FolderAndRenamePopup component
 */
const FolderAndRenamePopup = () => {
  const {
    isNewFolderPopupOpen,
    setIsNewFolderPopupOpen,
    isRenamePopupOpen,
    setIsRenamePopupOpen,
    fileToRename,
    currentFolder,
    handleCreateFolder,
    handleRename,
    setError
  } = useDrive();

  // Local state
  const [inputValue, setInputValue] = useState('');
  const [error, setInputError] = useState('');
  const inputRef = useRef(null);

  const isOpen = isNewFolderPopupOpen || isRenamePopupOpen;
  const actionType = isNewFolderPopupOpen ? 'create' : 'rename';
  const itemType = isNewFolderPopupOpen || fileToRename?.mimeType === 'application/vnd.google-apps.folder' ? 'folder' : 'file';

  // Effect to set initial input value and focus on input when popup opens
  useEffect(() => {
    if (isOpen) {
      setInputValue(isNewFolderPopupOpen ? 'Untitled Folder' : fileToRename?.name || '');
      setInputError('');
    }
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isOpen, isNewFolderPopupOpen, fileToRename]);

  /**
   * Validates the input value
   * @returns {boolean} Whether the input is valid
   */
  const validateInput = useCallback(() => {
    if (inputValue.trim() === '') {
      setInputError(`${itemType} name cannot be empty.`);
      return false;
    }
    if (inputValue.includes('/') || inputValue.includes('\\')) {
      setInputError(`${itemType} name cannot contain '/' or '\\'.`);
      return false;
    }
    return true;
  }, [inputValue, itemType]);

  /**
   * Handles form submission
   * @param {Event} e - The submit event
   */
  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    if (validateInput()) {
      if (isNewFolderPopupOpen) {
        handleCreateFolder(inputValue.trim());
      } else {
        handleRename(fileToRename.id, inputValue.trim());
      }
      handleClose();
    }
  }, [inputValue, isNewFolderPopupOpen, handleCreateFolder, handleRename, validateInput, fileToRename]);

  /**
   * Handles input change
   * @param {Event} e - The change event
   */
  const handleInputChange = useCallback((e) => {
    setInputValue(e.target.value);
    setInputError('');
  }, []);

  /**
   * Handles closing the popup
   */
  const handleClose = useCallback(() => {
    if (isNewFolderPopupOpen) {
      setIsNewFolderPopupOpen(false);
    } else {
      setIsRenamePopupOpen(false);
    }
  }, [isNewFolderPopupOpen, setIsNewFolderPopupOpen, setIsRenamePopupOpen]);

  if (!isOpen) return null;

  return (
    <div className="popup-overlay">
      <div className="popup-content">
        <button className="close-button" onClick={handleClose}>&times;</button>
        <h2 className="popup-title">
          {actionType === 'create' ? 'Create New Folder' : `Rename ${itemType}`}
        </h2>
        <form onSubmit={handleSubmit}>
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            className={`popup-input ${error ? 'error' : ''}`}
            placeholder={`Enter ${itemType} name`}
          />
          {error && <p className="error-message">{error}</p>}
          <div className="button-container">
            <button type="button" onClick={handleClose} className="cancel-button">Cancel</button>
            <button type="submit" className="ok-button">
              {actionType === 'create' ? 'Create' : 'Rename'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FolderAndRenamePopup;