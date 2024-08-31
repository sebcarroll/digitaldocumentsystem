import React from 'react';
import { Link } from 'react-router-dom';
import '../sidebar.css';

const defaultProps = {
  label: 'Home',
  to: '/drive',
};

const SidebarButton = ({ label = defaultProps.label, to = defaultProps.to, isActive, onClick, ...props }) => {
  const handleClick = (e) => {
    console.log(`SidebarButton clicked: ${label}, navigating to: ${to}`);
    if (onClick) {
      onClick(e);
    }
  };

  return (
    <Link 
      to={to}
      className={`sidebar-button ${isActive ? 'active' : ''}`}
      onClick={handleClick}
      {...props}
    >
      {label}
    </Link>
  );
};

export default SidebarButton;