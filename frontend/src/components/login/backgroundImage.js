import React from 'react';
import backgroundImageFile from '../../assets/images/third_party_images/login_background.png';
import '../../pages/LoginPage.css';

const BackgroundImage = () => {
  return (
    <div className="background-image" style={{ backgroundImage: `url(${backgroundImageFile})` }} />
  );
};

export default BackgroundImage;