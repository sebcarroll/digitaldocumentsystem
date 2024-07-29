import React from 'react';
import '../../../pages/LoginPage.css';

const defaultProps = {
  text: 'Sign in with Google',
};

const SignInText = (props) => {
  return (
    <div className="sign-in-text">
      {props.text ?? defaultProps.text}
    </div>
  );
};

export default SignInText;