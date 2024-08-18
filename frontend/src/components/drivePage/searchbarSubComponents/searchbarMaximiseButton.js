import React from 'react';
import '../searchbar.css';

/**
 * IconComponent for the MaximiseButton
 * @returns {JSX.Element} The SVG icon
 */
const IconComponent = () => (
  <svg className="maximise-icon" viewBox="0 0 24 24">
    <path fill="none" d="M0 0h24v24H0z"></path>
    <path d="M21 11V3h-8l3.29 3.29-10 10L3 13v8h8l-3.29-3.29 10-10z"></path>
  </svg>
);

const defaultProps = {
  IconComponent,
};

/**
 * MaximiseButton component
 * @param {Object} props - Component props
 * @param {Function} props.onClick - Function to handle button click
 * @param {Function} [props.IconComponent] - Custom icon component
 * @returns {JSX.Element} The rendered MaximiseButton component
 */
const MaximiseButton = ({ onClick, IconComponent: CustomIcon }) => {
  const Icon = CustomIcon || defaultProps.IconComponent;

  return (
    <button className="maximise-button" onClick={onClick}>
      <Icon className="maximise-icon" />
    </button>
  );
};

export default MaximiseButton;