import React from 'react';
import '../header.css';

const HeaderBackground = (props) => {
  return (
    <div className="header">
      {props.children}
    </div>
  );
};

export default HeaderBackground;