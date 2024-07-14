import React from 'react';

const styles = {
  Button: {
    cursor: 'pointer',
    top: '474px',
    left: '800px',
    width: '91px',
    height: '40px',
    padding: '0px 8px',
    border: '0',
    boxSizing: 'border-box',
    borderRadius: '9999px',
    backgroundColor: '#7a52f4',
    color: '#ffffff',
    fontSize: '16px',
    fontFamily: 'Inter',
    fontWeight: 700,
    lineHeight: '24px',
    outline: 'none',
  },
};

const defaultProps = {
  label: 'Sign up',
};

const SignUpButton = ({ onClick, label = defaultProps.label, style }) => {
  return (
    <button 
      style={{ ...styles.Button, ...style }} 
      onClick={onClick}
    >
      {label}
    </button>
  );
};

export default SignUpButton;