import React from 'react';
import '../header.css';

const CurrentPageText = ({ folderStack, currentFolder, onBreadcrumbClick }) => {
  const renderBreadcrumbs = () => {
    let breadcrumbs = [...folderStack, currentFolder];
    if (breadcrumbs.length > 3) {
      breadcrumbs = [{ id: '...', name: '...' }, ...breadcrumbs.slice(-2)];
    }

    return breadcrumbs.map((folder, index) => {
      let folderName = folder.name;
      if (folderName.length > 20) {
        folderName = folderName.slice(0, 17) + '...';
      }
      return (
        <React.Fragment key={folder.id}>
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
      {renderBreadcrumbs()}
    </div>
  );
};

export default CurrentPageText;