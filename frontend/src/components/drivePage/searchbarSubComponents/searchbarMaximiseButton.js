import React from 'react';
import '../searchbar.css';

const IconComponent = () => (
  <svg className="maximise-icon" viewBox="0 0 24 24">
    <path fill="none" d="M0 0h24v24H0z"></path>
    <path d="M21 11V3h-8l3.29 3.29-10 10L3 13v8h8l-3.29-3.29 10-10z"></path>
  </svg>
);

const defaultProps = {
  IconComponent,
};

const MaximiseButton = (props) => {
  return props.IconComponent ? (
    <props.IconComponent className="maximise-icon" />
  ) : (
    <defaultProps.IconComponent />
  );
};

export default MaximiseButton;