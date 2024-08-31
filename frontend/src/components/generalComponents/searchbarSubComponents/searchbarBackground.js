// SearchbarBackground.js
import React from 'react';
import '../searchbar.css';

const SearchbarBackground = (props) => {
  return (
    <div className="searchbar-background">
      {props.children}
    </div>
  );
};

export default SearchbarBackground;