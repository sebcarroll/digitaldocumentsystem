// src/components/drivePage/header.js

import React, { useEffect, useMemo } from 'react';
import { useDrive } from '../../contexts/driveContext';
import HeaderBackground from './headerSubComponents/headerBackground';
import CurrentPageText from './headerSubComponents/currentPageText';
import HeaderQuestionIcon from './headerSubComponents/questionIcon';
import HeaderSettingIcon from './headerSubComponents/settingsIcon';
import HeaderProfileIcon from './headerSubComponents/profileIcon';
import logoImage from '../../assets/images/proprietary_images/diganise_logo_july_2024.png';
import './header.css';

const Header = () => {
  const { currentFolder, folderStack, handleBreadcrumbClick, updateTrigger } = useDrive();

  console.log('Header render:', { currentFolder, folderStack });

  const isRootFolder = useMemo(() => 
    currentFolder.id === 'root' && folderStack.length === 0, 
    [currentFolder.id, folderStack.length]
  );

  useEffect(() => {
    console.log('Header re-rendered:', { currentFolder, folderStack, updateTrigger });
  }, [currentFolder, folderStack, updateTrigger]);

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
            <CurrentPageText />
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

export default React.memo(Header);