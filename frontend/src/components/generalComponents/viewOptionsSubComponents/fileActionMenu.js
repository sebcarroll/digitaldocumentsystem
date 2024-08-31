import React, { useState, useCallback } from 'react';
import DriveFileMoveIcon from '@mui/icons-material/DriveFileMove';
import DeleteIcon from '@mui/icons-material/Delete';
import LinkIcon from '@mui/icons-material/Link';
import DriveFileRenameOutlineIcon from '@mui/icons-material/DriveFileRenameOutline';
import FileCopyIcon from '@mui/icons-material/FileCopy';
import CloseIcon from '@mui/icons-material/Close';
import PersonAddIcon from '@mui/icons-material/PersonAdd';

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

const FileActionMenu = ({ selectedFiles, onMove, onDelete, onCopyLink, onRename, onMakeCopy, onClose, onShare, isFolder }) => {
  const noFilesSelected = selectedFiles.length === 0;
  const multipleFilesSelected = selectedFiles.length > 1;

  const handleCopyLink = () => {
    if (selectedFiles.length === 1) {
      onCopyLink(selectedFiles[0]);
    }
  };

  return (
    <div className="file-action-menu">
      <div className="action-buttons-container">
        <ActionButton icon={<CloseIcon />} text="Close" onClick={onClose} />
        <div className="selected-count">{selectedFiles.length} selected</div>
        <ActionButton icon={<PersonAddIcon />} text="Share" onClick={onShare} disabled={noFilesSelected} />
        <ActionButton icon={<DriveFileMoveIcon />} text="Move" onClick={() => onMove(selectedFiles)} disabled={noFilesSelected} />
        <ActionButton icon={<DeleteIcon />} text="Move to Bin" onClick={onDelete} disabled={noFilesSelected} />
        <ActionButton icon={<LinkIcon />} text="Copy link" onClick={handleCopyLink} disabled={noFilesSelected || multipleFilesSelected} />
        <ActionButton icon={<DriveFileRenameOutlineIcon />} text="Rename" onClick={onRename} disabled={noFilesSelected || multipleFilesSelected} />
        <ActionButton icon={<FileCopyIcon />} text="Make a copy" onClick={onMakeCopy} disabled={noFilesSelected || isFolder} />
      </div>
    </div>
  );
};

export default FileActionMenu;