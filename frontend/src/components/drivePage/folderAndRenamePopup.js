/**
 * FolderAndRenamePopup.js
 * This component renders a popup for creating a new folder or renaming an existing item.
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useFileOperations } from '../../hooks/useFileOperations.js';
import { useFileSelection } from '../../hooks/useFileSelection.js';
import './popup.css';

/**
 * FolderAndRenamePopup component
 * @param {Object} props - Component props
 * @param {Object} props.currentFolder - The current folder object
 * @param {Function} props.getDriveFiles - Function to refresh the file list
 * @param {Function} props.setError - Function to set error messages
 * @returns {React.ReactElement} FolderAndRenamePopup component
 */
const FolderAndRenamePopup = ({ currentFolder, getDriveFiles, setError }) => {
  const { 
    isNewFolderPopupOpen, 
    handleCreateFolder, 
    setIsNewFolderPopupOpen 
  } = useFileOperations(currentFolder || { id: 'root' }, getDriveFiles, setError);

  const {
    isRenamePopupOpen,
    fileToRename,
    handleRename,
    setIsRenamePopupOpen,
    isFolder
  } = useFileSelection(getDriveFiles, currentFolder || { id: 'root' }, setError);

  const [inputValue, setInputValue] = useState('');
  const [error, setInputError] = useState('');
  const inputRef = useRef(null);

  const isOpen = isNewFolderPopupOpen || isRenamePopupOpen;
  const actionType = isNewFolderPopupOpen ? 'create' : 'rename';
  const itemType = isNewFolderPopupOpen || isFolder ? 'folder' : 'file';

  /**
   * Effect to set initial input value and focus on input when popup opens
   */
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
        handleRename(inputValue.trim());
      }
    }
  }, [inputValue, isNewFolderPopupOpen, handleCreateFolder, handleRename, validateInput]);

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