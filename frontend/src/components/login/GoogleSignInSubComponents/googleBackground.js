import React from 'react';
import '../../../pages/LoginPage.css';

const GoogleBackground = (props) => {
  return (
    <div className="google-background">
      {props.children}
    </div>
  );
};

export default GoogleBackground;