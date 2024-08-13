import React from 'react';
import HeaderBackground from './headerSubComponents/headerBackground';
import CurrentPageText from './headerSubComponents/currentPageText';
import HeaderQuestionIcon from './headerSubComponents/questionIcon';
import HeaderSettingIcon from './headerSubComponents/settingsIcon';
import HeaderProfileIcon from './headerSubComponents/profileIcon';
import logoImage from '../../assets/images/proprietary_images/diganise_logo_july_2024.png';
import './header.css';

const Header = ({ folderStack, currentFolder, onBreadcrumbClick }) => {
  const isRootFolder = currentFolder.id === 'root' && folderStack.length === 0;

  return (
    <HeaderBackground>
      <div className="header-content">
        <div className="left-section">
          <div className="logo-and-text">
            <img src={logoImage} alt="Diganise Logo" className="logo" />
          </div>
          {isRootFolder ? (
            <span className="text">Welcome to Diganise</span>
          ) : (
            <CurrentPageText
              folderStack={folderStack}
              currentFolder={currentFolder}
              onBreadcrumbClick={onBreadcrumbClick}
            />
          )}
        </div>
        <div className="settings-icon-container">
            <HeaderQuestionIcon />
            <HeaderSettingIcon />
            <HeaderProfileIcon />
          </div>
      </div>
    </HeaderBackground>
  );
};

export default Header;