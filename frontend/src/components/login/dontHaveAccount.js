import React from 'react';
import '../../pages/LoginPage.css';

const defaultProps = {
  text: 'Don\'t have an account?',
};

const DontHaveAccountText = (props) => {
  return (
    <div className="dont-have-account-text">
      {props.text ?? defaultProps.text}
    </div>
  );
};

export default DontHaveAccountText;