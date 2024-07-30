import React, { useState, useCallback } from 'react';
import DownloadIcon from '@mui/icons-material/Download';
import DriveFileMoveIcon from '@mui/icons-material/DriveFileMove';
import DeleteIcon from '@mui/icons-material/Delete';
import LinkIcon from '@mui/icons-material/Link';
import DriveFileRenameOutlineIcon from '@mui/icons-material/DriveFileRenameOutline';
import FileCopyIcon from '@mui/icons-material/FileCopy';
import CloseIcon from '@mui/icons-material/Close';

const ActionButton = ({ icon, text, onClick }) => {
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
      className="action-button"
    >
      {icon}
      {showText && <span className="action-text">{text}</span>}
    </button>
  );
};

const FileActionMenu = ({ onDownload, onMove, onDelete, onCopyLink, onRename, onMakeCopy, onClose }) => {
  return (
    <div className="file-action-menu">
      <ActionButton icon={<CloseIcon />} text="Close" onClick={onClose} />
      <ActionButton icon={<DownloadIcon />} text="Download" onClick={onDownload} />
      <ActionButton icon={<DriveFileMoveIcon />} text="Move" onClick={onMove} />
      <ActionButton icon={<DeleteIcon />} text="Move to Bin" onClick={onDelete} />
      <ActionButton icon={<LinkIcon />} text="Copy link" onClick={onCopyLink} />
      <ActionButton icon={<DriveFileRenameOutlineIcon />} text="Rename" onClick={onRename} />
      <ActionButton icon={<FileCopyIcon />} text="Make a copy" onClick={onMakeCopy} />
    </div>
  );
};

export default FileActionMenu;