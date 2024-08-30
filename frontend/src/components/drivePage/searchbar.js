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
    if (query.trim()) {
      onOpenChat(query, false); // false indicates not to open upload menu
      setQuery('');
    }
  }, [query, onOpenChat]);
  
  const handleMaximize = useCallback(() => {
    console.log("Maximize button clicked");
    onOpenChat(query, false);
  }, [query, onOpenChat]);

  const handleUpload = useCallback(() => {
    console.log("Upload button clicked");
    onOpenChat(query, true); // true indicates to open upload menu
  }, [query, onOpenChat]);

  const handleQueryChange = useCallback((e) => {
    setQuery(e.target.value);
  }, []);
  
  return (
    <SearchbarBackground>
      <div className="maximise-button-container">
        <MaximiseButton onClick={handleMaximize} />
      </div>
      <AttachFileSharpIcon onClick={handleUpload} />
      <form onSubmit={handleSubmit} className="search-form">
        <InputField 
          value={query}
          onChange={handleQueryChange}
        />
        <SendButton onClick={handleSubmit} />
      </form>
    </SearchbarBackground>
  );
};

export default SearchBar;