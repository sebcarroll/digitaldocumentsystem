import React from 'react';
import GoogleBackground from './GoogleSignInSubComponents/googleBackground';
import GoogleLogo from './GoogleSignInSubComponents/googleLogo';
import SignInText from './GoogleSignInSubComponents/signInText';
import '../../pages/LoginPage.css';

const GoogleSignInButton = ({ onClick }) => {
  return (
    <div onClick={onClick} className="google-sign-in-button">
      <GoogleBackground className="google-background">
        <div className="google-content">
          <GoogleLogo />
          <SignInText />
        </div>
      </GoogleBackground>
    </div>
  );
};

export default GoogleSignInButton;