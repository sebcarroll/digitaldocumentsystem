import React, { useState, useCallback } from 'react';
import './searchbar.css';
import SearchbarBackground from './searchbarSubComponents/searchbarBackground.js';
import InputField from './searchbarSubComponents/searchbarInputField.js';
import MaximiseButton from './searchbarSubComponents/searchbarMaximiseButton.js';
import SendButton from './searchbarSubComponents/searchbarSendButton.js';
import WelcomeText from './searchbarSubComponents/searchbarWelcomeText.js';

/**
 * SearchBar component
 * Renders a search bar with chat functionality
 * @param {Object} props - Component props
 * @param {Function} props.onOpenChat - Function to open the chat interface
 * @returns {JSX.Element} The rendered SearchBar component
 */
const SearchBar = ({ onOpenChat }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    if (query.trim()) {
      onOpenChat(query);
      setQuery('');
    }
  }, [query, onOpenChat]);
  
  const handleMaximize = useCallback(() => {
    console.log("Maximize button clicked");
    onOpenChat(query);
  }, [query, onOpenChat]);

  const handleQueryChange = useCallback((e) => {
    setQuery(e.target.value);
  }, []);
  
  return (
    <SearchbarBackground>
      <div className="maximise-button-container">
        <MaximiseButton onClick={handleMaximize} />
      </div>
      <WelcomeText />
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