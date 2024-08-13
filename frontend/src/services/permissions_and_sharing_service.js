/**
 * permissions_and_sharing_service.js
 * This file contains functions for managing permissions and sharing of Google Drive files.
 */

const API_URL = process.env.REACT_APP_API_URL;

/**
 * Retrieves the list of people with access to a specific file.
 * @param {string} fileId - The ID of the file.
 * @returns {Promise<Array>} An array of people with access to the file.
 * @throws {Error} If fetching the access list fails.
 */
export const getPeopleWithAccess = async (fileId) => {
  try {
    const data = await api.getPeopleWithAccess(fileId);
    return data.permissions || [];
  } catch (error) {
    console.error('Error getting people with access:', error);
    throw error;
  }
};

/**
 * Shares a file with specified email addresses and assigns a role.
 * @param {string} fileId - The ID of the file to share.
 * @param {string[]} emails - An array of email addresses to share the file with.
 * @param {string} role - The role to assign to the shared users.
 * @returns {Promise<Object>} The result of the sharing operation.
 * @throws {Error} If sharing the file fails.
 */
export const shareFile = async (fileId, emails, role) => {
  try {
    const result = await api.shareFile(fileId, emails, role);
    return result;
  } catch (error) {
    console.error('Error sharing file:', error);
    throw error;
  }
};

/**
 * Retrieves the current user's role for a specific file.
 * @param {string} fileId - The ID of the file.
 * @returns {Promise<Object>} An object containing the user's role and ID.
 * @throws {Error} If fetching the user role fails.
 */
export const getCurrentUserRole = async (fileId) => {
  try {
    const { role, id } = await api.getCurrentUserRole(fileId);
    return { role, id };
  } catch (error) {
    console.error('Error getting current user role:', error);
    throw error;
  }
};

/**
 * Updates the permission for a user on a specific file.
 * @param {string} fileId - The ID of the file.
 * @param {string} permissionId - The ID of the permission to update.
 * @param {string} role - The new role to assign.
 * @returns {Promise<Object>} The result of the permission update.
 * @throws {Error} If updating the permission fails.
 */
export const updatePermission = async (fileId, permissionId, role) => {
  try {
    const result = await api.updatePermission(fileId, permissionId, role);
    return result;
  } catch (error) {
    console.error('Error updating permission:', error);
    throw error;
  }
};

/**
 * Removes a user's permission for a specific file.
 * @param {string} fileId - The ID of the file.
 * @param {string} permissionId - The ID of the permission to remove.
 * @returns {Promise<Object>} The result of the permission removal.
 * @throws {Error} If removing the permission fails.
 */
export const removePermission = async (fileId, permissionId) => {
  try {
    const result = await api.removePermission(fileId, permissionId);
    return result;
  } catch (error) {
    console.error('Error removing permission:', error);
    throw error;
  }
};

/**
 * Updates the general access settings for a file.
 * @param {string} fileId - The ID of the file.
 * @param {string} newAccess - The new access level ('private', 'domain', or 'anyone').
 * @param {string} linkRole - The role for anyone with the link (if applicable).
 * @returns {Promise<Object>} The result of the general access update.
 * @throws {Error} If updating the general access fails.
 */
export const updateGeneralAccess = async (fileId, newAccess, linkRole) => {
  try {
    const result = await api.updateGeneralAccess(fileId, newAccess, linkRole);
    return result;
  } catch (error) {
    console.error('Error updating general access:', error);
    throw error;
  }
};

/**
 * Checks if the current user has owner or editor permissions for a file.
 * @param {string} fileId - The ID of the file.
 * @returns {Promise<boolean>} True if the user has owner or editor permissions, false otherwise.
 * @throws {Error} If checking the permissions fails.
 */
export const hasOwnerOrEditorPermissions = async (fileId) => {
  try {
    const { role } = await getCurrentUserRole(fileId);
    return role === 'owner' || role === 'writer';
  } catch (error) {
    console.error('Error checking owner/editor permissions:', error);
    throw error;
  }
};

/**
 * Formats the permissions data for display.
 * @param {Array} permissions - The raw permissions data.
 * @returns {Array} Formatted permissions data.
 */
export const formatPermissionsForDisplay = (permissions) => {
  return permissions.map(perm => ({
    id: perm.id,
    email: perm.emailAddress,
    role: perm.role,
    displayName: perm.displayName || perm.emailAddress,
    photoLink: perm.photoLink
  }));
};

/**
 * Handles errors related to permissions and sharing operations.
 * @param {Error} error - The error object.
 * @returns {string} A user-friendly error message.
 */
export const handlePermissionError = (error) => {
  console.error('Permission operation failed:', error);
  
  // Check for specific error types and return appropriate messages
  if (error.message.includes('insufficient permissions')) {
    return "You don't have permission to perform this action.";
  } else if (error.message.includes('not found')) {
    return "The file or user was not found.";
  } else if (error.message.includes('invalid role')) {
    return "The specified role is not valid.";
  }
  
  // Default error message
  return "An error occurred while managing permissions. Please try again.";
};

/**
 * Checks if a given email is valid.
 * @param {string} email - The email to validate.
 * @returns {boolean} True if the email is valid, false otherwise.
 */
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validates a list of emails for sharing.
 * @param {string[]} emails - An array of email addresses.
 * @returns {Object} An object with valid and invalid emails.
 */
export const validateEmails = (emails) => {
  const validEmails = [];
  const invalidEmails = [];

  emails.forEach(email => {
    if (isValidEmail(email.trim())) {
      validEmails.push(email.trim());
    } else {
      invalidEmails.push(email.trim());
    }
  });

  return { validEmails, invalidEmails };
};

/**
 * Checks if the current user is the owner of the file.
 * @param {string} fileId - The ID of the file.
 * @returns {Promise<boolean>} True if the user is the owner, false otherwise.
 * @throws {Error} If checking the ownership fails.
 */
export const isCurrentUserOwner = async (fileId) => {
  try {
    const { role } = await getCurrentUserRole(fileId);
    return role === 'owner';
  } catch (error) {
    console.error('Error checking file ownership:', error);
    throw error;
  }
};