const API_URL = process.env.REACT_APP_API_URL;

export const initiateGoogleLogin = () => {
  window.location.href = `${API_URL}/login`;
};

export const fetchDriveFiles = async () => {
  const response = await fetch(`${API_URL}/drive`, {
    credentials: 'include', // This is important for sending cookies
  });
  if (!response.ok) {
    throw new Error('Failed to fetch drive files');
  }
  return response.json(); // Changed from response.text() to response.json()
};

export const checkAuth = async () => {
  const response = await fetch(`${API_URL}/check-auth`, {
    credentials: 'include',
  });
  if (!response.ok) {
    throw new Error('Failed to check authentication status');
  }
  return response.json();
};