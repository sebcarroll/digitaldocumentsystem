import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const AuthSuccess = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/drive');
    }, 200); // Redirect after 0.2 seconds

    return () => clearTimeout(timer);
  }, [navigate]);

  return <div>Authentication successful. Redirecting...</div>;
};

export default AuthSuccess;