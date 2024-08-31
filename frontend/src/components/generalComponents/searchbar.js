import React, { useState, useCallback } from 'react';
import './searchbar.css';
import SearchbarBackground from './searchbarSubComponents/searchbarBackground.js';
import InputField from './searchbarSubComponents/searchbarInputField.js';
import MaximiseButton from './searchbarSubComponents/searchbarMaximiseButton.js';
import SendButton from './searchbarSubComponents/searchbarSendButton.js';
import AttachFileSharpIcon from '@mui/icons-material/AttachFileSharp';

/**
 * SearchBar component
 * Renders a search bar with chat functionality and document upload
 * @param {Object} props - Component props
 * @param {Function} props.onOpenChat - Function to open the chat interface
 * @returns {JSX.Element} The rendered SearchBar component
 */


const SearchBar = ({ onOpenChat }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    console.log("Form submitted, query:", query);
    console.log("onOpenChat type:", typeof onOpenChat);
    if (query.trim() && typeof onOpenChat === 'function') {
      onOpenChat(query, false);
      setQuery('');
    } else {
      console.error("onOpenChat is not a function or query is empty. Query:", query, "onOpenChat:", onOpenChat);
    }
  }, [query, onOpenChat]);
  
  const handleMaximize = useCallback(() => {
    console.log("Maximize button clicked");
    onOpenChat(query, false);
  }, [query, onOpenChat]);

  const handleUpload = useCallback((e) => {
    e.preventDefault();
    console.log("Upload button clicked");
    onOpenChat(query, true);
  }, [query, onOpenChat]);

  const handleQueryChange = useCallback((e) => {
    setQuery(e.target.value);
  }, []);
  
  
  return (
    <SearchbarBackground>
      <div className="maximise-button-container">
        <MaximiseButton onClick={() => onOpenChat(query, false)} />
      </div>
      <form onSubmit={handleSubmit} className="search-form">
        <div className="file-upload-label" onClick={() => onOpenChat(query, true)}>
          <AttachFileSharpIcon />
        </div>
        <InputField 
          value={query}
          onChange={handleQueryChange}
          placeholder="Type your message here..."
        />
        <SendButton type="submit" onClick={handleSubmit} />
      </form>
    </SearchbarBackground>
  );
};

export default SearchBar;