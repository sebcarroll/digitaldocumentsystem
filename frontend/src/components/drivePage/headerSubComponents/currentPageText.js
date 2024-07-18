import React from 'react';
import { useLocation } from 'react-router-dom';
import '../header.css';

const CurrentPageText = ({ folderStack, currentFolder, onBreadcrumbClick }) => {
  const location = useLocation();

  const getPageTitle = () => {
    const path = location.pathname.split('/').filter(Boolean);
    if (path.length === 0) return 'Welcome to Diganise';
    return path[path.length - 1].charAt(0).toUpperCase() + path[path.length - 1].slice(1);
  };

  const getBreadcrumbs = () => {
    if (folderStack.length === 0 && currentFolder.id === 'root') return getPageTitle();

    let breadcrumbs = [...folderStack, currentFolder];
    if (breadcrumbs.length > 3) {
      breadcrumbs = [{ id: '...', name: '...' }, ...breadcrumbs.slice(-2)];
    }

    return breadcrumbs.map((folder, index) => {
      let folderName = folder.id === 'root' ? getPageTitle() : folder.name;
      if (folderName.length > 20) {
        folderName = folderName.slice(0, 17) + '...';
      }
      return (
        <React.Fragment key={folder.id}>
          {index > 0 && <span className="breadcrumb-separator"> &gt; </span>}
          <span 
            onClick={() => onBreadcrumbClick(index)} 
            className={`breadcrumb-item ${index === breadcrumbs.length - 1 ? 'current-item' : ''}`}
          >
            {folderName}
          </span>
        </React.Fragment>
      );
    });
  };

  return (
    <div className="text">
      <div className="breadcrumbs">
        {getBreadcrumbs()}
      </div>
    </div>
  );
};

export default CurrentPageText;