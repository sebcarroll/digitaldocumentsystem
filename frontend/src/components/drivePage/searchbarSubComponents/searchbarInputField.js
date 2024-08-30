import React from 'react';
import '../searchbar.css';

const defaultProps = {
  placeholder: 'Type your message here...',
};

const InputField = ({ value, onChange, placeholder = defaultProps.placeholder }) => {
  return (
    <input 
      className="input-field" 
      placeholder={placeholder}
      value={value}
      onChange={onChange}
    />
  );
};

export default InputField;