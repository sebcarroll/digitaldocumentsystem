import React from 'react';

const styles = {
  Text: {
    color: '#5d5d5b',
    fontSize: '16px',
    fontFamily: 'Inter',
    fontWeight: 500,
    lineHeight: '24px',
  },
};

const defaultProps = {
  text: 'Don\'t have a Google account?',
};

const DontHaveAccountText = (props) => {
  return (
    <div style={styles.Text}>
      {props.text ?? defaultProps.text}
    </div>
  );
};

export default DontHaveAccountText;