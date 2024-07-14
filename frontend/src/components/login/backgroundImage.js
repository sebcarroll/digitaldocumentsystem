import React from 'react';
import backgroundImageFile from '../../assets/images/third_party_images/login_background.png';

const BackgroundImage = () => {
  return (
    <div style={{
      position: 'absolute',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      backgroundImage: `url(${backgroundImageFile})`,
      backgroundPosition: 'center',
      backgroundSize: 'cover',
      backgroundRepeat: 'no-repeat',
      zIndex: -1,
    }} />
  );
};

export default BackgroundImage;