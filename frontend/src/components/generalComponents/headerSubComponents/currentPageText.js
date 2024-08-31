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
    let breadcrumbs = [];

    if (path === '/drive' && (!currentFolder || currentFolder.id === 'root')) {
      return <span className="breadcrumb-item current-item">Welcome To Diganise</span>;
    }

    breadcrumbs.push({ id: 'root', name: rootName });

    if (folderStack && folderStack.length > 0) {
      breadcrumbs = [...breadcrumbs, ...folderStack];
    }

    if (currentFolder && currentFolder.id !== 'root') {
      breadcrumbs.push(currentFolder);
    }

    // Remove 'My Drive' from breadcrumbs if it's not the /my-drive page
    if (path !== '/my-drive' && breadcrumbs.length > 1) {
      breadcrumbs = breadcrumbs.filter(crumb => crumb.name !== 'My Drive');
    }

    return breadcrumbs.map((folder, index) => {
      let folderName = folder.name || 'Unknown';
      if (folderName.length > 20) {
        folderName = folderName.slice(0, 17) + '...';
      }
      const isLastItem = index === breadcrumbs.length - 1;
      return (
        <React.Fragment key={folder.id || index}>
          {index > 0 && <span className="breadcrumb-separator">&gt;</span>}
          {isLastItem ? (
            <span className="breadcrumb-item current-item">
              {folderName}
            </span>
          ) : (
            <span 
              onClick={() => onBreadcrumbClick(index)} 
              className="breadcrumb-item clickable"
            >
              {folderName}
            </span>
          )}
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