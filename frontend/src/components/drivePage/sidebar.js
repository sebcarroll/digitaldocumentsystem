// src/components/Sidebar.js
import React from 'react';
import { useLocation } from 'react-router-dom';
import { useDrive } from '../../contexts/driveContext';
import NewItemButton from '../drivePage/sidebarSubComponents/newItemButton';
import SidebarButton from '../drivePage/sidebarSubComponents/sidebarPageButton';
import './sidebar.css';

const Sidebar = () => {
  const location = useLocation();
  const {
    sidebarItems,
    openCreateFolderPopup,
    handleUploadFile,
    handleUploadFolder,
    handleCreateDoc,
    handleCreateSheet
  } = useDrive();

  return (
    <aside className="sidebar">
      <div className="new-button-container">
        <NewItemButton />
      </div>
      <nav className="sidebar-nav">
        {sidebarItems.map((item) => (
          <SidebarButton
            key={item.path}
            to={item.path}
            label={item.label}
            isActive={location.pathname === item.path}
          />
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;