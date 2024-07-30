import React from 'react';
import '../viewOptions.css';

const FilesOnlyViewButton = ({ label = 'Files', isActive = false, onClick }) => {
  return (
    <button 
      className={`ViewButton FilesOnlyViewButton ${isActive ? 'active' : 'inactive'}`}
      onClick={onClick}
    >
      {label}
    </button>
  );
};

export default FilesOnlyViewButton;