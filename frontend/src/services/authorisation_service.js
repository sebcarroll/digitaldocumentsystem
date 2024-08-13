/**
 * auth.js
 * This file contains authentication-related API calls.
 */

const API_URL = process.env.REACT_APP_API_URL;

/**
 * Initiates the Google login process by redirecting to the login URL.
 */
export const initiateGoogleLogin = () => {
  window.location.href = `${API_URL}/login`;
};

/**
 * Checks the authentication status of the current user.
 * @returns {Promise<Object>} The authentication status and user information.
 * @throws {Error} If the authentication check fails.
 */
export const checkAuth = async () => {
  const response = await fetch(`${API_URL}/check-auth`, {
    credentials: 'include',
  });
  if (!response.ok) {
    throw new Error('Failed to check authentication status');
  }
  return response.json();
};