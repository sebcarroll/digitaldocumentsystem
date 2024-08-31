// CurrentPageText.js
import React from 'react';
import { useLocation } from 'react-router-dom';
import '../header.css';

const CurrentPageText = ({ folderStack, currentFolder, onBreadcrumbClick }) => {
  const location = useLocation();

  const getRootName = () => {
    switch (location.pathname) {
      case '/drive':
        return 'Home';
      case '/my-drive':
        return 'My Drive';
      case '/shared-with-me':
        return 'Shared With Me';
      case '/recent':
        return 'Recent';
      case '/bin':
        return 'Bin';
      default:
        return 'My Drive';
    }
  };

  const getBreadcrumbs = () => {
    if (!folderStack || !currentFolder) {
      return [{ id: 'root', name: getRootName() }];
    }

    let breadcrumbs = [{ id: 'root', name: getRootName() }, ...folderStack, currentFolder];
    if (breadcrumbs.length > 4) {
      breadcrumbs = [
        breadcrumbs[0],
        { id: '...', name: '...' },
        ...breadcrumbs.slice(-2)
      ];
    }

    return breadcrumbs.map((folder, index) => {
      let folderName = folder.name || 'Unknown';
      if (folderName.length > 20) {
        folderName = folderName.slice(0, 17) + '...';
      }
      return (
        <React.Fragment key={folder.id || index}>
          {index > 0 && <span className="breadcrumb-separator">&gt;</span>}
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
    <div className="breadcrumbs">
      {getBreadcrumbs()}
    </div>
  );
};

export default CurrentPageText;