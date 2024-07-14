import React from 'react';

const styles = {
  Card: {
    top: '362.6963216252684px',
    left: '528px',
    width: '383px',
    height: '170.3036783747316px',
    backgroundColor: '#ffffff',
    borderRadius: '16px',
    boxShadow: '1px 1px 8px rgba(149,149,149,0.25)',
  },
};

const LoginCard = (props) => {
  return (
    <div style={styles.Card}>
      {props.children}
    </div>
  );
};

export default LoginCard;