import React from 'react';
import '../../pages/LoginPage.css';

const defaultProps = {
  label: 'Sign up',
};

const SignUpButton = ({ onClick, label = defaultProps.label, style }) => {
  return (
    <button 
      className="sign-up-button" 
      style={style} 
      onClick={onClick}
    >
      {label}
    </button>
  );
};

export default SignUpButton;