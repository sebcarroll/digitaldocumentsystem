// src/components/viewOptions/ViewOptions.js

import React from 'react';
import { useDrive } from '../../contexts/driveContext';
import FilesOnlyViewButton from './viewOptionsSubComponents/filesOnlyViewButton';
import FoldersOnlyViewButton from './viewOptionsSubComponents/foldersOnlyViewButton';
import ListLayoutIcon from './viewOptionsSubComponents/listLayoutIcon';
import GridLayoutIcon from './viewOptionsSubComponents/gridLayoutIcon';
import FileActionMenu from './viewOptionsSubComponents/fileActionMenu';
import './viewOptions.css';

/**
 * ViewOptions component
 * @returns {JSX.Element} Rendered ViewOptions component
 */
const ViewOptions = () => {
  const {
    filesActive,
    foldersActive,
    listLayoutActive,
    handleFilesClick,
    handleFoldersClick,
    handleListLayoutClick,
    handleGridLayoutClick,
    showActionMenu,
    selectedFiles,
    handleMove,
    handleDelete,
    handleCopyLink,
    openRenamePopup,
    handleMakeCopy,
    handleCloseActionMenu,
    handleShare,
    isFolder,
  } = useDrive();

  return (
    <div className="view-options">
      {showActionMenu ? (
        <FileActionMenu />
      ) : (
        <>
          <div className="view-type-buttons">
            <FilesOnlyViewButton isActive={filesActive} onClick={handleFilesClick} />
            <FoldersOnlyViewButton isActive={foldersActive} onClick={handleFoldersClick} />
          </div>
          <div className="layout-buttons">
            <button className={`layout-button ${listLayoutActive ? 'active' : ''}`} onClick={handleListLayoutClick}>
              <ListLayoutIcon />
            </button>
            <button className={`layout-button ${!listLayoutActive ? 'active' : ''}`} onClick={handleGridLayoutClick}>
              <GridLayoutIcon />
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default ViewOptions;