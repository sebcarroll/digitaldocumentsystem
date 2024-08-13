import React, { useState } from 'react';
import './searchbar.css';
import SearchbarBackground from './searchbarSubComponents/searchbarBackground.js';
import InputField from './searchbarSubComponents/searchbarInputField.js';
import MaximiseButton from './searchbarSubComponents/searchbarMaximiseButton.js';
import SendButton from './searchbarSubComponents/searchbarSendButton.js';
import WelcomeText from './searchbarSubComponents/searchbarWelcomeText.js';

const SearchBar = ({ onSearch, onOpenChat }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query);
      onOpenChat(query);
      setQuery('');
    }
  };

  const handleMaximize = () => {
    onOpenChat();
  };

  return (
    <SearchbarBackground>
      <div className="maximise-button-container">
        <MaximiseButton onClick={handleMaximize} />
      </div>
      <WelcomeText />
      <form onSubmit={handleSubmit} className="search-form">
        <InputField 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <SendButton onClick={handleSubmit} />
      </form>
    </SearchbarBackground>
  );
};

export default SearchBar;