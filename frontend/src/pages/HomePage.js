import React from 'react';
import { fetchDriveFiles } from '../services/api';
import BaseDrivePage from './BaseDrivePage';
import DriveContent from '../components/homePage/homePageContent.js';

/**
 * DrivePage component
 * Renders the main drive page with file management functionality
 * @returns {JSX.Element} The rendered DrivePage component
 */
const HomePage = () => {
  return (
    <BaseDrivePage
      DriveContent={DriveContent}
      fetchFiles={fetchDriveFiles}
    />
  );
};

export default HomePage;