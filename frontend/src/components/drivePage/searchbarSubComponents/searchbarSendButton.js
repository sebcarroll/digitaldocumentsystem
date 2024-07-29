import React from 'react';
import '../searchbar.css';

const IconComponent = () => (
  <svg className="icon" viewBox="0 0 24 24">
    <path d="M0 0h24v24H0z" fill="none"></path>
    <path d="M2.01 21 23 12 2.01 3 2 10l15 2-15 2z"></path>
  </svg>
);

const defaultProps = {
  IconComponent,
};

const SendButton = (props) => {
  return (
    <button className="send-button">
      {props.IconComponent ? (
        <props.IconComponent className="icon" />
      ) : (
        <defaultProps.IconComponent />
      )}
    </button>
  );
};

export default SendButton;