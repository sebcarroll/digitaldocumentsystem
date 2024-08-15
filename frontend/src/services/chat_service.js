// src/services/chat_service.js

const API_URL = process.env.REACT_APP_API_URL;

/**
 * Sends a query to the LLM and retrieves the response.
 * @param {string} query - The user's query to send to the LLM.
 * @returns {Promise<Object>} The response from the LLM.
 * @throws {Error} If the query fails.
 */
export const sendQuery = async (query) => {
  try {
    const response = await fetch(`${API_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error('Failed to send query to LLM');
    }

    return await response.json();
  } catch (error) {
    console.error('Error querying LLM:', error);
    throw error;
  }
};

/**
 * Uploads a document to be used by the LLM.
 * @param {Object} document - The document to upload.
 * @returns {Promise<Object>} The response from the document upload.
 * @throws {Error} If the document upload fails.
 */
export const uploadDocument = async (document) => {
  try {
    const response = await fetch(`${API_URL}/document`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ document }),
    });

    if (!response.ok) {
      throw new Error('Failed to upload document');
    }

    return await response.json();
  } catch (error) {
    console.error('Error uploading document:', error);
    throw error;
  }
};