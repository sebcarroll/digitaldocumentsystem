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
      navigate('/login');
    } catch (error) {
      console.error('Failed to logout:', error);
    }
  }, [navigate]);

  const getPageTitle = () => {
    if (location.pathname === '/faq') {
      return (
        <div className="breadcrumbs">
          <span className="breadcrumb-item" onClick={handleHomeClick}>Home</span>
          <span className="breadcrumb-separator">&gt;</span>
          <span className="breadcrumb-item current-item">Frequently Asked Questions</span>
        </div>
      );
    } else if (isRootFolder) {
      return 'Welcome to Diganise';
    } else {
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
          <HeaderQuestionIcon onClick={handleQuestionClick} />
          <HeaderSettingIcon onClick={handleSettingsClick} isOpen={isSettingsOpen} />
          <HeaderProfileIcon 
            onClick={handleProfileClick} 
            isOpen={isProfileOpen} 
            userEmail={userEmail} 
            userName={userName}
            onLogout={handleLogout}
          />
        </div>
      </div>
      {isSettingsOpen && (
        <div className="settings-dropdown">
          <p className="settings-message">Settings functionality to be implemented in future versions.</p>
        </div>
      )}
    </HeaderBackground>
  );
};

export default Header;