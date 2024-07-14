import React from 'react';
import GoogleBackground from './googleBackground';
import GoogleLogo from './googleLogo';
import SignInText from './signInText';

const GoogleSignInButton = ({ onClick }) => {
  return (
    <div 
      onClick={onClick}
      style={{
        cursor: 'pointer',
        width: '100%',
      }}
    >
      <GoogleBackground style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: '100%',
        padding: '10px',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '20px',
          marginTop: '10px'
        }}>
          <GoogleLogo />
          <SignInText />
        </div>
      </GoogleBackground>
    </div>
  );
};

export default GoogleSignInButton;