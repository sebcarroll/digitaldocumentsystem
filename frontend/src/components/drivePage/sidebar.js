// Sidebar.js
import React from 'react';
import { useLocation } from 'react-router-dom';
import NewItemButton from './sidebarSubComponents/newItemButton.js';
import './sidebar.css';
import SidebarButton from './sidebarSubComponents/sidebarPageButton.js';

const Sidebar = ({ onCreateFolder, onUploadFile, onUploadFolder, onCreateDoc, onCreateSheet }) => {
    const location = useLocation();
  
    const sidebarItems = [
      { path: '/drive', label: 'Home' },
      { path: '/my-drive', label: 'My Drive' },
      { path: '/shared-with-me', label: 'Shared with me' },
      { path: '/recent', label: 'Recent' },
      { path: '/bin', label: 'Bin' }
    ];
  
    return (
      <aside className="sidebar">
        <div className="new-button-container">
          <NewItemButton
            onCreateFolder={onCreateFolder}
            onUploadFile={onUploadFile}
            onUploadFolder={onUploadFolder}
            onCreateDoc={onCreateDoc}
            onCreateSheet={onCreateSheet}
          />
        </div>
        <nav className="sidebar-nav">
          {sidebarItems.map((item) => {
            return (
              <SidebarButton
                key={item.path}
                to={item.path}
                label={item.label}
                isActive={location.pathname === item.path}
              />
            );
          })}
        </nav>
      </aside>
    );
  };
  
  export default Sidebar;