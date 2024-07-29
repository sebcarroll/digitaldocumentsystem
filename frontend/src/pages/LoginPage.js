import React from 'react';
import BackgroundImage from '../components/login/backgroundImage.js';
import LoginCard from '../components/login/loginCard.js';
import DontHaveAccountText from '../components/login/dontHaveAccount.js';
import SignUpButton from '../components/login/signUpButton.js';
import GoogleSignInButton from '../components/login/completeGoogleSignInButton.js';
import './LoginPage.css';

const LoginPage = () => {
  const handleGoogleSignUp = () => {
    window.open('https://accounts.google.com/signup', '_blank');
  };

  const handleGoogleSignIn = () => {
    window.location.href = 'http://localhost:8080/login';
  };

  return (
    <div className="login-page">
      <BackgroundImage />

      <LoginCard className="login-card-container">
        <div className="flex-spacer" />
        
        <div className="google-sign-in-container">
          <GoogleSignInButton onClick={handleGoogleSignIn} />
        </div>

        <div className="flex-spacer" />
        
        <div className="account-signup-container">
          <div className="dont-have-account-container">
            <DontHaveAccountText className="dont-have-account-text" />
          </div>
          <div className="signup-button-container">
            <SignUpButton 
              className="signup-button"
              onClick={handleGoogleSignUp}
            />
          </div>
        </div>
      </LoginCard>
    </div>
  );
};

export default LoginPage;