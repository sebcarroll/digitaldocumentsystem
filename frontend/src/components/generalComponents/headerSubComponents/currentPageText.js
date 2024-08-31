import React from 'react';
import '../header.css';

const CurrentPageText = ({ folderStack, currentFolder, onBreadcrumbClick, path }) => {
  const getRootName = () => {
    switch (path) {
      case '/drive':
        return 'Home';
      case '/my-drive':
        return 'My Drive';
      case '/shared-with-me':
        return 'Shared With Me';
      case '/recent':
        return 'Recent';
      default:
        return 'My Drive';
    }
  };

  const getBreadcrumbs = () => {
    const rootName = getRootName();
    let breadcrumbs = [{ id: 'root', name: rootName }];

    if (folderStack && folderStack.length > 0) {
      breadcrumbs = [...breadcrumbs, ...folderStack];
    }

    if (currentFolder && currentFolder.id !== 'root') {
      breadcrumbs.push(currentFolder);
    }

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