// src/components/drivePage/headerSubComponents/currentPageText.js

import React, { useEffect, useMemo, useCallback } from 'react';
import { useDrive } from '../../../contexts/driveContext';
import '../header.css';

const CurrentPageText = () => {
  const { folderStack, currentFolder, handleBreadcrumbClick, updateTrigger } = useDrive();

  useEffect(() => {
    console.log('CurrentPageText re-rendered:', { folderStack, currentFolder, updateTrigger });
  }, [folderStack, currentFolder, updateTrigger]);

  const breadcrumbs = useMemo(() => {
    let breadcrumbArray = [...folderStack, currentFolder];
    if (breadcrumbArray.length > 3) {
      breadcrumbArray = [{ id: '...', name: '...' }, ...breadcrumbArray.slice(-2)];
    }
    return breadcrumbArray;
  }, [folderStack, currentFolder]);

  const renderBreadcrumbs = useCallback(() => {
    return breadcrumbs.map((folder, index) => {
      let folderName = folder.name;
      if (folderName.length > 20) {
        folderName = folderName.slice(0, 17) + '...';
      }
      return (
        <React.Fragment key={folder.id}>
          {index > 0 && <span className="breadcrumb-separator">&gt;</span>}
          <span 
            onClick={() => handleBreadcrumbClick(index)} 
            className={`breadcrumb-item ${index === breadcrumbs.length - 1 ? 'current-item' : ''}`}
          >
            {folderName}
          </span>
        </React.Fragment>
      );
    });
  }, [breadcrumbs, handleBreadcrumbClick]);

  return (
    <div className="breadcrumbs">
      {renderBreadcrumbs()}
    </div>
  );
};

export default React.memo(CurrentPageText);