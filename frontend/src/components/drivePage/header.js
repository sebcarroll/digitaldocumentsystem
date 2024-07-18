import React from 'react';
import HeaderBackground from './headerSubComponents/headerBackground';
import CurrentPageText from './headerSubComponents/currentPageText';
import HeaderQuestionIcon from './headerSubComponents/questionIcon';
import HeaderSettingIcon from './headerSubComponents/settingsIcon';
import HeaderProfileIcon from './headerSubComponents/profileIcon';
import logoImage from '../../assets/images/proprietary_images/diganise_logo_july_2024.png';
import './header.css';

const Header = ({ folderStack, currentFolder, onBreadcrumbClick }) => {
  return (
    <HeaderBackground>
      <div className="header-content">
        <div className="logo-and-text">
          <img src={logoImage} alt="Diganise Logo" className="logo" />
          <div className="text">
            <CurrentPageText 
              folderStack={folderStack} 
              currentFolder={currentFolder} 
              onBreadcrumbClick={onBreadcrumbClick}
            />
          </div>
        </div>
        <div className="icon-container">
          <HeaderQuestionIcon />
          <HeaderSettingIcon />
          <HeaderProfileIcon />
        </div>
      </div>
    </HeaderBackground>
  );
};

export default Header;