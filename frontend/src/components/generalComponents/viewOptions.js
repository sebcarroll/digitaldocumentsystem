import React from 'react';
import FilesOnlyViewButton from './viewOptionsSubComponents/filesOnlyViewButton';
import FoldersOnlyViewButton from './viewOptionsSubComponents/foldersOnlyViewButton';
import ListLayoutIcon from './viewOptionsSubComponents/listLayoutIcon';
import GridLayoutIcon from './viewOptionsSubComponents/gridLayoutIcon';
import FileActionMenu from './viewOptionsSubComponents/fileActionMenu';
import './viewOptions.css';

const ViewOptions = ({ 
  filesActive, 
  foldersActive, 
  listLayoutActive, 
  onFilesClick, 
  onFoldersClick, 
  onListLayoutClick, 
  onGridLayoutClick,
  showActionMenu,
  selectedFiles,
  onMove,
  onDelete,
  onCopyLink,
  onRename,
  onMakeCopy,
  onCloseActionMenu,
  onShare,
  isFolder 
}) => {
  return (
    <div className="view-options">
      {showActionMenu ? (
        <FileActionMenu 
          selectedFiles={selectedFiles}
          onMove={onMove}
          onDelete={onDelete}
          onCopyLink={onCopyLink}
          onRename={onRename}
          onMakeCopy={onMakeCopy}
          onClose={onCloseActionMenu}
          onShare={onShare}
          isFolder={isFolder}
        />
      ) : (
        <>
          <div className="view-type-buttons">
            <FilesOnlyViewButton isActive={filesActive} onClick={onFilesClick} />
            <FoldersOnlyViewButton isActive={foldersActive} onClick={onFoldersClick} />
          </div>
          <div className="layout-buttons">
            <button className={`layout-button ${listLayoutActive ? 'active' : ''}`} onClick={onListLayoutClick}>
              <ListLayoutIcon />
            </button>
            <button className={`layout-button ${!listLayoutActive ? 'active' : ''}`} onClick={onGridLayoutClick}>
              <GridLayoutIcon />
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default ViewOptions;