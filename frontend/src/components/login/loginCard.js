import React from 'react';
import '../../pages/LoginPage.css';

const LoginCard = (props) => {
  return (
    <div className="login-card">
      {props.children}
    </div>
  );
};

export default LoginCard;