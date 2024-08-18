/**
 * users.js
 * This file contains user-related API calls.
 */

const API_URL = process.env.REACT_APP_API_URL;

/**
 * Makes an API call to the specified endpoint with the given method and data.
 * @param {string} endpoint - The API endpoint to call.
 * @param {string} method - The HTTP method to use (GET, POST, PUT, DELETE).
 * @param {Object} [data] - The data to send with the request (for POST, PUT).
 * @returns {Promise<any>} The response data from the API.
 * @throws {Error} If the API call fails.
 */
async function apiCall(endpoint, method, data = null) {
  const url = `${API_URL}${endpoint}`;
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include', // Include credentials (cookies) with every request
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(url, options);
    if (response.status === 401) {
      // Attempt to refresh the session
      const refreshed = await refreshSession();
      if (refreshed) {
        // Retry the original request
        return apiCall(endpoint, method, data);
      } else {
        throw new Error('Session expired and refresh failed');
      }
    }
    if (!response.ok) {
      const errorBody = await response.text();
      console.error('API call failed:', response.status, errorBody);
      throw new Error(`API call failed: ${response.status} ${response.statusText}`);
    }
    return response.json();
  } catch (error) {
    console.error('API call error:', error);
    throw error;
  }
}

/**
 * Checks the current session status.
 * @returns {Promise<boolean>} True if the user is authenticated, false otherwise.
 */
export const checkSessionStatus = async () => {
  try {
    const response = await apiCall('/check-auth', 'GET');
    return response.authenticated;
  } catch (error) {
    console.error('Error checking session status:', error);
    return false;
  }
};

/**
 * Attempts to refresh the current session.
 * @returns {Promise<boolean>} True if the session was successfully refreshed, false otherwise.
 */
export const refreshSession = async () => {
  try {
    const response = await apiCall('/refresh-token', 'POST');
    return response.success;
  } catch (error) {
    console.error('Error refreshing session:', error);
    return false;
  }
};

/**
 * Searches for users based on a query string.
 * @param {string} query - The search query.
 * @returns {Promise<Object>} An object containing an array of matching users.
 * @throws {Error} If the search fails or the user is not authenticated.
 */
export const searchUsers = async (query) => {
  try {
    const isAuthenticated = await checkSessionStatus();
    if (!isAuthenticated) {
      throw new Error('User is not authenticated');
    }
    const response = await apiCall(`/search-users?q=${encodeURIComponent(query)}`, 'GET');
    return response;
  } catch (error) {
    console.error('Error searching users:', error);
    if (error.message === 'User is not authenticated') {
      throw error; // Re-throw authentication errors
    }
    return { users: [] };
  }
};

/**
 * Handles errors related to user operations.
 * @param {Error} error - The error object.
 * @returns {string} A user-friendly error message.
 */
export const handleUserError = (error) => {
  console.error('User operation failed:', error);
  
  // Log the full error object for debugging
  console.error('Full error object:', JSON.stringify(error, null, 2));
  
  if (error.message.includes('User is not authenticated')) {
    return "Your session has expired. Please log in again.";
  }
  
  // Default error message
  return "An error occurred while performing the user operation. Please try again.";
};