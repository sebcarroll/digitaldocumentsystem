import React from 'react';
import { useLocation } from 'react-router-dom';
import '../generalComponents/sidebar.css';
import SidebarButton from '../generalComponents/sidebarSubComponents/sidebarPageButton.js';

const Sidebar = ({ onCreateFolder, onUploadFile, onUploadFolder, onCreateDoc, onCreateSheet }) => {
    const location = useLocation();
  
    const sidebarItems = [
      { path: '/drive', label: 'Home' },
      { path: '/my-drive', label: 'My Drive' },
      { path: '/shared-with-me', label: 'Shared with me' },
      { path: '/recent', label: 'Recent' },
    ];
  
    console.log('Current location:', location.pathname);

    return (
      <aside className="sidebar">
        <nav className="sidebar-nav">
          {sidebarItems.map((item) => {
            console.log(`Rendering SidebarButton for ${item.label}. Path: ${item.path}, Active: ${location.pathname === item.path}`);
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