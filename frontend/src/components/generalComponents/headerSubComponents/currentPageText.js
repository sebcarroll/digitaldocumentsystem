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

    // Add the root name only if it's not already in the folderStack
    if (!folderStack.length || folderStack[0].name !== rootName) {
      breadcrumbs.push({ id: 'root', name: rootName });
    }

    // Add folders from the folderStack
    if (folderStack && folderStack.length > 0) {
      breadcrumbs = [...breadcrumbs, ...folderStack];
    }

    // Add the current folder if it's not the root and not already in the breadcrumbs
    if (currentFolder && currentFolder.id !== 'root' && 
        (breadcrumbs.length === 0 || breadcrumbs[breadcrumbs.length - 1].id !== currentFolder.id)) {
      breadcrumbs.push(currentFolder);
    }

    // Remove duplicate entries
    breadcrumbs = breadcrumbs.filter((crumb, index, self) =>
      index === self.findIndex((t) => t.id === crumb.id)
    );

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