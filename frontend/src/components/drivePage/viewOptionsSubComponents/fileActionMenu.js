// src/components/viewOptions/viewOptionsSubComponents/fileActionMenu.js

import React, { useState, useCallback } from 'react';
import { useDrive } from '../../../contexts/driveContext';
import DriveFileMoveIcon from '@mui/icons-material/DriveFileMove';
import DeleteIcon from '@mui/icons-material/Delete';
import LinkIcon from '@mui/icons-material/Link';
import DriveFileRenameOutlineIcon from '@mui/icons-material/DriveFileRenameOutline';
import FileCopyIcon from '@mui/icons-material/FileCopy';
import CloseIcon from '@mui/icons-material/Close';
import PersonAddIcon from '@mui/icons-material/PersonAdd';

/**
 * ActionButton component
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.icon - Icon to display
 * @param {string} props.text - Button text
 * @param {Function} props.onClick - Click handler
 * @param {boolean} props.disabled - Whether the button is disabled
 * @returns {JSX.Element} Rendered ActionButton component
 */
const ActionButton = ({ icon, text, onClick, disabled }) => {
  const [showText, setShowText] = useState(false);
  const [hoverTimeout, setHoverTimeout] = useState(null);

  const handleMouseEnter = useCallback(() => {
    const timeout = setTimeout(() => {
      setShowText(true);
    }, 1000);
    setHoverTimeout(timeout);
  }, []);

  const handleMouseLeave = useCallback(() => {
    if (hoverTimeout) {
      clearTimeout(hoverTimeout);
    }
    setShowText(false);
  }, [hoverTimeout]);

  return (
    <button
      onClick={onClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className={`action-button ${disabled ? 'disabled' : ''}`}
      disabled={disabled}
    >
      {icon}
      {showText && <span className="action-text">{text}</span>}
    </button>
  );
};

/**
 * FileActionMenu component
 * @returns {JSX.Element} Rendered FileActionMenu component
 */
const FileActionMenu = () => {
  const {
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

  const noFilesSelected = selectedFiles.length === 0;
  const multipleFilesSelected = selectedFiles.length > 1;

  return (
    <div className="file-action-menu">
      <div className="action-buttons-container">
        <ActionButton icon={<CloseIcon />} text="Close" onClick={handleCloseActionMenu} />
        <div className="selected-count">{selectedFiles.length} selected</div>
        <ActionButton icon={<PersonAddIcon />} text="Share" onClick={handleShare} disabled={noFilesSelected} />
        <ActionButton icon={<DriveFileMoveIcon />} text="Move" onClick={() => handleMove(selectedFiles)} disabled={noFilesSelected} />
        <ActionButton icon={<DeleteIcon />} text="Move to Bin" onClick={handleDelete} disabled={noFilesSelected} />
        <ActionButton icon={<LinkIcon />} text="Copy link" onClick={handleCopyLink} disabled={noFilesSelected || multipleFilesSelected} />
        <ActionButton icon={<DriveFileRenameOutlineIcon />} text="Rename" onClick={openRenamePopup} disabled={noFilesSelected || multipleFilesSelected} />
        <ActionButton icon={<FileCopyIcon />} text="Make a copy" onClick={handleMakeCopy} disabled={noFilesSelected || isFolder} />
      </div>
    </div>
  );
};

export default FileActionMenu;