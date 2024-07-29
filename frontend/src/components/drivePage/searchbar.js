// SearchBar.js
import React, { useState } from 'react';
import './searchbar.css';
import SearchbarBackground from './searchbarSubComponents/searchbarBackground';
import InputField from './searchbarSubComponents/searchbarInputField';
import MaximiseButton from './searchbarSubComponents/searchbarMaximiseButton';
import SendButton from './searchbarSubComponents/searchbarSendButton';
import WelcomeText from './searchbarSubComponents/searchbarWelcomeText';

const SearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <SearchbarBackground>
      <div className="maximise-button-container">
        <MaximiseButton />
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