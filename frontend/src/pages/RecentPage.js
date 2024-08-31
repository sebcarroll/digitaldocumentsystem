import React from 'react';
import { fetchDriveFiles } from '../services/api';
import BaseDrivePage from './DrivePage';
import DriveContent from '../components/recentPage/recentDriveContent.js';

/**
 * DrivePage component
 * Renders the main drive page with file management functionality
 * @returns {JSX.Element} The rendered DrivePage component
 */
const RecentPage = () => {
  return (
    <BaseDrivePage
      DriveContent={DriveContent}
      fetchFiles={fetchDriveFiles}
    />
  );
};

export default RecentPage;