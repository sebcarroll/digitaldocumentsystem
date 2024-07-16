import React from 'react';

const styles = {
  Card: {
    top: '387px',
    left: '560px',
    width: '300px',
    height: '68px',
    backgroundColor: '#ffffff',
    borderRadius: '9999px',
    border: '1px solid #4285f4',
    boxSizing: 'border-box',
    boxShadow: '1px 1px 8px rgba(149,149,149,0.25)',
  },
};

const GoogleBackground = (props) => {
  return (
    <div style={styles.Card}>
      {props.children}
    </div>
  );
};

export default GoogleBackground;