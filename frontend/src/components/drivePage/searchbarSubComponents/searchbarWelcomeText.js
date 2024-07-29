import React from 'react';
import '../searchbar.css';

const defaultProps = {
  text: 'Hello! How can I assist you today?',
};

const WelcomeText = (props) => {
  return (
    <div className="welcome-card">
      <div className="welcome-text">
        {props.text ?? defaultProps.text}
      </div>
    </div>
  );
};

export default WelcomeText;