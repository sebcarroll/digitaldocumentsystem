import React from 'react';

const styles = {
  Text: {
    color: '#080a0b',
    fontSize: '20px',
    fontFamily: 'Inter',
    fontWeight: 700,
    lineHeight: '28px',
  },
};

const defaultProps = {
  text: 'Sign in with Google',
};

const SignInText = (props) => {
  return (
    <div style={styles.Text}>
      {props.text ?? defaultProps.text}
    </div>
  );
};

export default SignInText;