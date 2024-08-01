// StyledPopup.js
import React, { useState, useEffect, useRef } from 'react';
import './folderAndRenamePopup.css';

const StyledPopup = ({ isOpen, onClose, onSubmit, title, initialValue }) => {
  const [inputValue, setInputValue] = useState(initialValue);
  const inputRef = useRef(null);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isOpen]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(inputValue);
  };

  if (!isOpen) return null;

  return (
    <div className="popup-overlay">
      <div className="popup-content">
        <button className="close-button" onClick={onClose}>&times;</button>
        <h2 className="popup-title">{title}</h2>
        <form onSubmit={handleSubmit}>
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            className="popup-input"
          />
          <div className="button-container">
            <button type="button" onClick={onClose} className="cancel-button">Cancel</button>
            <button type="submit" className="ok-button">OK</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default StyledPopup;