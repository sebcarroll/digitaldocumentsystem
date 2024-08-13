/**
 * users.js
 * This file contains user-related API calls.
 */

/**
 * Searches for users based on a query string.
 * @param {string} query - The search query.
 * @returns {Promise<Object>} An object containing an array of matching users.
 * @throws {Error} If the search fails.
 */
export const searchUsers = async (query) => {
    try {
      const response = await fetch(`/api/search-users?q=${encodeURIComponent(query)}`);
      if (!response.ok) {
        throw new Error('Failed to search users');
      }
      return await response.json();
    } catch (error) {
      console.error('Error searching users:', error);
      return { users: [] };
    }
  };