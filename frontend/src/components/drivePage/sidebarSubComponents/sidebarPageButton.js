import React from 'react';
import '../sidebar.css';

const defaultProps = {
  label: 'Home',
};

const SidebarButton = ({ label = defaultProps.label, isActive, ...props }) => {
  return (
    <button 
      className={`sidebar-button ${isActive ? 'active' : ''}`}
      {...props}
    >
      {label}
    </button>
  );
};

export default SidebarButton;