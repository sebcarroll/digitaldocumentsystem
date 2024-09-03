import React, { useEffect, useState } from 'react';
import '../header.css';

const CurrentPageText = ({ folderStack, currentFolder, onBreadcrumbClick, path }) => {
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

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

    // Determine how many folders to display
    const maxFolders = windowWidth <= 480 ? 2 : 3;
    const startIndex = Math.max(0, breadcrumbs.length - maxFolders);
    const displayedBreadcrumbs = breadcrumbs.slice(startIndex);

    return displayedBreadcrumbs.map((folder, index) => {
      let folderName = folder.name || 'Unknown';
      if (windowWidth <= 480) {
        folderName = folderName.length > 5 ? folderName.slice(0, 5) + '...' : folderName;
      } else if (folderName.length > 10) {
        folderName = folderName.slice(0, 9) + '...';
      }
      const isLastItem = index === displayedBreadcrumbs.length - 1;
      const isFirstItem = index === 0 && startIndex > 0;

      return (
        <React.Fragment key={folder.id || index}>
          {index > 0 && <span className="breadcrumb-separator">&gt;</span>}
          {isFirstItem && <span className="breadcrumb-ellipsis">..</span>}
          {isLastItem ? (
            <span className="breadcrumb-item current-item">
              {folderName}
            </span>
          ) : (
            <span 
              onClick={() => onBreadcrumbClick(startIndex + index)}
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