import React, { useState, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { logoutUser } from '../../services/api';
import HeaderBackground from './headerSubComponents/headerBackground';
import CurrentPageText from './headerSubComponents/currentPageText';
import HeaderQuestionIcon from './headerSubComponents/questionIcon';
import HeaderSettingIcon from './headerSubComponents/settingsIcon';
import HeaderProfileIcon from './headerSubComponents/profileIcon';
import logoImage from '../../assets/images/proprietary_images/diganise_logo_july_2024.png';
import './header.css';

const Header = ({ folderStack, currentFolder, onBreadcrumbClick, userEmail, userName }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const isRootFolder = currentFolder && currentFolder.id === 'root' && folderStack && folderStack.length === 0;

  const handleQuestionClick = () => {
    navigate('/faq');
  };

  const handleHomeClick = () => {
    navigate('/drive');
  };

  const handleSettingsClick = () => {
    setIsSettingsOpen(!isSettingsOpen);
    setIsProfileOpen(false);
  };

  const handleProfileClick = () => {
    setIsProfileOpen(!isProfileOpen);
    setIsSettingsOpen(false);
  };

  const handleLogout = useCallback(async () => {
    try {
      await logoutUser();
      navigate('/');
    } catch (error) {
      console.error('Failed to logout:', error);
    }
  }, [navigate]);

  const getPageTitle = () => {
    const path = location.pathname;

    if (path === '/faq') {
      return (
        <div className="breadcrumbs">
          <span className="breadcrumb-item" onClick={handleHomeClick}>Home</span>
          <span className="breadcrumb-separator">&gt;</span>
          <span className="breadcrumb-item current-item">Frequently Asked Questions</span>
        </div>
      );
    } else if (path === '/drive') {
      return isRootFolder ? 'Welcome to Diganise' : 'Home';
    } else if (path === '/my-drive') {
      return isRootFolder ? 'My Drive' : (
        <CurrentPageText
          folderStack={['My Drive', ...folderStack.slice(1)]}
          currentFolder={currentFolder}
          onBreadcrumbClick={onBreadcrumbClick}
        />
      );
    } else if (path === '/shared-with-me') {
      return isRootFolder ? 'Shared With Me' : (
        <CurrentPageText
          folderStack={['Shared With Me', ...folderStack.slice(1)]}
          currentFolder={currentFolder}
          onBreadcrumbClick={onBreadcrumbClick}
        />
      );
    } else if (path === '/recent') {
      return isRootFolder ? 'Recent' : (
        <CurrentPageText
          folderStack={['Recent', ...folderStack.slice(1)]}
          currentFolder={currentFolder}
          onBreadcrumbClick={onBreadcrumbClick}
        />
      );
    }
      else {
      return (
        <CurrentPageText
          folderStack={folderStack}
          currentFolder={currentFolder}
          onBreadcrumbClick={onBreadcrumbClick}
        />
      );
    }
  };

  return (
    <HeaderBackground>
      <div className="header-content">
        <div className="left-section">
          <div className="logo-and-text">
            <img src={logoImage} alt="Diganise Logo" className="logo" onClick={handleHomeClick} style={{cursor: 'pointer'}} />
          </div>
          <span className="text">{getPageTitle()}</span>
        </div>
        <div className="settings-icon-container">
          <HeaderQuestionIcon 
            onClick={handleQuestionClick} 
            title="Frequently Asked Questions"
          />
          <HeaderSettingIcon 
            onClick={handleSettingsClick} 
            isOpen={isSettingsOpen} 
            title="Settings"
          />
          <HeaderProfileIcon 
            onClick={handleProfileClick} 
            title="User Profile"
          />
        </div>
      </div>
      {isSettingsOpen && (
        <div className="settings-dropdown">
          <p className="settings-message">Settings functionality to be implemented in future versions.</p>
        </div>
      )}
      {isProfileOpen && (
        <div className="profile-dropdown">
          <p>Hi, {userName}!</p>
          <p>{userEmail}</p>
          <button onClick={handleLogout}>Sign out</button>
        </div>
      )}
    </HeaderBackground>
  );
};

export default Header;