import React from 'react';
import '../viewOptions.css';

const FoldersOnlyViewButton = ({ label = 'Folders', isActive = false, onClick }) => {
  return (
    <button 
      className={`ViewButton FoldersOnlyViewButton ${isActive ? 'active' : 'inactive'}`}
      onClick={onClick}
    >
      {label}
    </button>
  );
};

export default FoldersOnlyViewButton;