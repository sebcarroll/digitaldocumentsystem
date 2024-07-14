import React from 'react';
import { useNavigate } from 'react-router-dom';
import BackgroundImage from '../components/login/backgroundImage.js';
import LoginCard from '../components/login/loginCard.js';
import DontHaveAccountText from '../components/login/dontHaveAccount.js';
import SignUpButton from '../components/login/signUpButton.js';
import GoogleSignInButton from '../components/login/completeGoogleSignInButton.js';

const LoginPage = () => {
  const navigate = useNavigate();

  const handleGoogleSignUp = () => {
    window.open('https://accounts.google.com/signup', '_blank');
  };

  const handleGoogleSignIn = () => {
    window.location.href = 'http://localhost:8080/login';
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center',
      position: 'relative'
    }}>
      <BackgroundImage />

      <LoginCard style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        width: '100%',
        maxWidth: '300px',
        padding: '20px',
        minHeight: '400px',
      }}>
        <div style={{ flex: 1 }} />
        
        <div style={{ 
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          padding: '20px 0',
          marginLeft: '10%',
          marginRight: '10%'
        }}>
          <GoogleSignInButton onClick={handleGoogleSignIn} />
        </div>
        <div style={{ flex: 1 }} />
        
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between',
          alignItems: 'center',
          width: '100%',
          padding: '0 30px',
          boxSizing: 'border-box',
        }}>
          <div style={{ flex: 1, maxWidth: '60%' }}>
            <DontHaveAccountText style={{ 
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis'
            }} />
          </div>
          <div style={{ flex: 1, maxWidth: '40%', display: 'flex', justifyContent: 'flex-end' }}>
            <SignUpButton 
              style={{ cursor: 'pointer' }}
              onClick={handleGoogleSignUp}
            />
          </div>
        </div>
      </LoginCard>
    </div>
  );
};

export default LoginPage;