import React, { useState, useEffect } from 'react';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import ArrowRightIcon from '@mui/icons-material/ArrowRight';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import './popup.css';

const FolderTree = ({ folder, onSelect, selectedFolder, disabled }) => {
  const [expanded, setExpanded] = useState(false);

  const handleToggle = (e) => {
    e.stopPropagation();
    setExpanded(!expanded);
  };

  const handleSelect = (e) => {
    e.stopPropagation();
    if (!disabled) {
      onSelect(folder.id);
    }
  };

  return (
    <div className={`folder-tree-item ${disabled ? 'disabled' : ''}`}>
      <div className="folder-tree-content">
        <span className="folder-tree-icon" onClick={handleToggle}>
          {folder.children && folder.children.length > 0 ? (
            expanded ? <ArrowDropDownIcon /> : <ArrowRightIcon />
          ) : <span className="folder-tree-icon-placeholder"></span>}
        </span>
        <span className="folder-tree-checkbox" onClick={handleSelect}>
          {selectedFolder === folder.id ? <CheckBoxIcon /> : <CheckBoxOutlineBlankIcon />}
        </span>
        <span className="folder-tree-name">{folder.name}</span>
      </div>
      {expanded && folder.children && folder.children.length > 0 && (
        <div className="folder-tree-children">
          {folder.children.map(childFolder => (
            <FolderTree
              key={childFolder.id}
              folder={childFolder}
              onSelect={onSelect}
              selectedFolder={selectedFolder}
              disabled={disabled}
            />
          ))}
        </div>
      )}
    </div>
  );
};

const MovePopup = ({
  isOpen,
  onClose,
  onMove,
  selectedFiles,
  folders,
}) => {
  const [selectedFolder, setSelectedFolder] = useState(null);
  const [folderStructure, setFolderStructure] = useState([]);

  useEffect(() => {
    // Build the folder structure
    const buildFolderStructure = (folders) => {
      return folders.map(folder => ({
        ...folder,
        children: folder.children ? buildFolderStructure(folder.children) : []
      }));
    };

    setFolderStructure(buildFolderStructure(folders));
  }, [folders]);

  if (!isOpen) return null;

  const title = selectedFiles.length === 1
    ? `Move "${selectedFiles[0].name}"`
    : `Move ${selectedFiles.length} items`;

  const handleSelect = (folderId) => {
    setSelectedFolder(folderId === selectedFolder ? null : folderId);
  };

  const handleMove = () => {
    if (selectedFolder) {
      onMove(selectedFiles.map(f => f.id), selectedFolder);
      onClose();
    }
  };

  return (
    <div className="popup-overlay">
      <div className="popup-content move-popup">
        <h2>{title}</h2>
        <div className="folder-tree">
          {folderStructure.map(folder => (
            <FolderTree
              key={folder.id}
              folder={folder}
              onSelect={handleSelect}
              selectedFolder={selectedFolder}
              disabled={false}
            />
          ))}
        </div>
        <div className="popup-actions">
          <button className="cancel-button" onClick={onClose}>Cancel</button>
          <button
            className="ok-button"
            onClick={handleMove}
            disabled={!selectedFolder}
          >
            Move
          </button>
        </div>
      </div>
    </div>
  );
};

export default MovePopup;