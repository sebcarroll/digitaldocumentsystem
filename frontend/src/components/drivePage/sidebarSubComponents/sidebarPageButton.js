import React from 'react';

const styles = {
  Button: {
    cursor: 'pointer',
    top: '228px',
    left: '16px',
    width: '328px',
    height: '40px',
    padding: '0px 8px',
    border: '0',
    boxSizing: 'border-box',
    backgroundColor: '#dff2fe',
    color: '#000000',
    fontSize: '16px',
    fontFamily: 'Roboto',
    fontWeight: '500',
    lineHeight: '24px',
    textAlign: 'left',
    outline: 'none',
  },
};

const defaultProps = {
  label: 'Home',
};

const SidebarButton = (props) => {
  return (
    <button style={styles.Button}>
      {props.label ?? defaultProps.label}
    </button>
  )
};
export default SidebarButton