import React from 'react';
import '../searchbar.css';

const IconComponent = () => (
  <svg className="send_button_icon" viewBox="0 0 24 24">
    <path d="M0 0h24v24H0z" fill="none"></path>
    <path d="M2.01 21 23 12 2.01 3 2 10l15 2-15 2z"></path>
  </svg>
);

const defaultProps = {
  IconComponent,
};

const SendButton = ({ onClick, type = 'button', IconComponent: PropsIconComponent }) => {
  const ButtonIconComponent = PropsIconComponent || defaultProps.IconComponent;

  return (
    <button 
      className="send-button" 
      onClick={onClick} 
      type={type}
    >
      <ButtonIconComponent className="send_button_icon" />
    </button>
  );
};

export default SendButton;