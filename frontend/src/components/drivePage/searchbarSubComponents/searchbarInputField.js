import React from 'react';
import '../searchbar.css';

const defaultProps = {
  text: 'Type your message here...',
};

const InputField = (props) => {
  return (
    <input 
      className="input-field" 
      placeholder={props.text ?? defaultProps.text} 
    />
  );
};

export default InputField;