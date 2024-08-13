/**
 * useFileSharing.js
 * This custom hook manages file sharing operations in Google Drive.
 */

import { useState, useEffect, useCallback } from 'react';
import * as usersApi from '../services/users_service.js'
import * as permissionsApi from '../services/permissions_and_sharing_service.js';

/**
 * Custom hook for file sharing operations in Google Drive.
 * @param {Array} items - The files or folders to be shared.
 * @returns {Object} An object containing file sharing functions and state.
 */
export const useFileSharing = (items) => {
  // State variables
  const [email, setEmail] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [peopleWithAccess, setPeopleWithAccess] = useState([]);
  const [generalAccess, setGeneralAccess] = useState('Restricted');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pendingEmails, setPendingEmails] = useState([]);
  const [currentUserRole, setCurrentUserRole] = useState(null);
  const [linkAccessRole, setLinkAccessRole] = useState('viewer');
  const [currentUserId, setCurrentUserId] = useState(null);
  const [isSharingLoading, setIsSharingLoading] = useState(false);
  const [sharingError, setSharingError] = useState(null);

  /**
   * Fetch current user's role for the shared item.
   */
  const fetchCurrentUserRole = useCallback(async () => {
    if (items.length === 0) return;
    setIsSharingLoading(true);
    setSharingError(null);
    try {
      const userInfo = await permissionsApi.getCurrentUserRole(items[0].id);
      setCurrentUserRole(userInfo.role);
      setCurrentUserId(userInfo.id);
    } catch (error) {
      console.error('Failed to fetch current user info:', error);
      setSharingError('Failed to fetch user role');
    } finally {
      setIsSharingLoading(false);
    }
  }, [items]);

  /**
   * Fetch people with access to the shared item.
   */
  const fetchPeopleWithAccess = useCallback(async () => {
    if (items.length === 0) return;
    setIsSharingLoading(true);
    setSharingError(null);
    try {
      const response = await permissionsApi.getPeopleWithAccess(items[0].id);
      console.log('API Response:', response); // Log the full API response
      setPeopleWithAccess(response.peopleWithAccess || []);
      setCurrentUserRole(response.currentUserRole || 'viewer');
      setCurrentUserId(response.currentUserId || null);
      setGeneralAccess(response.generalAccess || 'Restricted');
    } catch (err) {
      console.error('Error fetching people with access:', err);
      setSharingError('Failed to fetch people with access');
    } finally {
      setIsSharingLoading(false);
    }
  }, [items]);

  useEffect(() => {
    fetchCurrentUserRole();
    fetchPeopleWithAccess();
  }, [fetchCurrentUserRole, fetchPeopleWithAccess]);

  /**
   * Handle email input change and trigger user search.
   * @param {string} value - The current value of the email input.
   */
  const handleEmailChange = useCallback((value) => {
    setEmail(value);
    if (value.length > 2) {
      usersApi.searchUsers(value).then(response => {
        setSearchResults(response.users || []);
      }).catch(err => {
        console.error('Failed to search users:', err);
        setSearchResults([]);
      });
    } else {
      setSearchResults([]);
    }
  }, []);

  /**
   * Add an email to the list of pending emails to be shared.
   * @param {string} emailToAdd - The email to add to pending list.
   */
  const handleAddPendingEmail = useCallback((emailToAdd) => {
    setPendingEmails(prev => [...prev, emailToAdd]);
    setEmail('');
  }, []);

  /**
   * Remove an email from the list of pending emails.
   * @param {string} emailToRemove - The email to remove from pending list.
   */
  const handleRemovePendingEmail = useCallback((emailToRemove) => {
    setPendingEmails(prev => prev.filter(email => email !== emailToRemove));
  }, []);

  /**
   * Share the item with all pending emails.
   */
  const handleShareWithPendingEmails = useCallback(async () => {
    setIsSharingLoading(true);
    setSharingError(null);
    try {
      await Promise.all(items.map(item => 
        Promise.all(pendingEmails.map(email => 
          permissionsApi.shareFile(item.id, [email], 'viewer')
        ))
      ));
      await fetchPeopleWithAccess();
      setPendingEmails([]);
    } catch (err) {
      console.error('Error sharing with pending emails:', err);
      setSharingError('Failed to share with some or all of the added emails');
    } finally {
      setIsSharingLoading(false);
    }
  }, [items, pendingEmails, fetchPeopleWithAccess]);

  /**
   * Update the access level for a specific user.
   * @param {string} personId - The ID of the person whose access is being changed.
   * @param {string} newRole - The new role to assign to the person.
   */
  const handleAccessLevelChange = useCallback(async (personId, newRole) => {
    setIsSharingLoading(true);
    setSharingError(null);
    try {
      await Promise.all(items.map(item => permissionsApi.updatePermission(item.id, personId, newRole)));
      await fetchPeopleWithAccess();
    } catch (err) {
      console.error('Error updating permission:', err);
      setSharingError('Failed to update permission');
    } finally {
      setIsSharingLoading(false);
    }
  }, [items, fetchPeopleWithAccess]);

  /**
   * Remove access for a specific user.
   * @param {string} personId - The ID of the person whose access is being removed.
   */
  const handleRemoveAccess = useCallback(async (personId) => {
    if (currentUserRole !== 'writer' && currentUserRole !== 'owner') return;
    setIsSharingLoading(true);
    setSharingError(null);
    try {
      await Promise.all(items.map(item => permissionsApi.removePermission(item.id, personId)));
      await fetchPeopleWithAccess();
    } catch (err) {
      console.error('Error removing access:', err);
      setSharingError('Failed to remove access');
    } finally {
      setIsSharingLoading(false);
    }
  }, [items, fetchPeopleWithAccess, currentUserRole]);

  /**
   * Update the general access settings for the item.
   * @param {string} newAccess - The new general access setting.
   */
  const handleGeneralAccessChange = useCallback(async (newAccess) => {
    if (currentUserRole !== 'writer' && currentUserRole !== 'owner') return;
    setIsSharingLoading(true);
    setSharingError(null);
    try {
      await Promise.all(items.map(item => permissionsApi.updateGeneralAccess(item.id, newAccess, linkAccessRole)));
      setGeneralAccess(newAccess);
    } catch (err) {
      console.error('Error updating general access:', err);
      setSharingError('Failed to update general access');
    } finally {
      setIsSharingLoading(false);
    }
  }, [items, currentUserRole, linkAccessRole]);

  /**
   * Update the link access role.
   * @param {string} newRole - The new role for link access.
   */
  const handleLinkAccessRoleChange = useCallback((newRole) => {
    setLinkAccessRole(newRole);
  }, []);

  return {
    email,
    searchResults,
    peopleWithAccess,
    generalAccess,
    isLoading,
    error,
    pendingEmails,
    currentUserRole,
    linkAccessRole,
    currentUserId,
    handleEmailChange,
    handleAddPendingEmail,
    handleRemovePendingEmail,
    handleAccessLevelChange,
    handleRemoveAccess,
    handleGeneralAccessChange,
    handleShareWithPendingEmails,
    handleLinkAccessRoleChange,
    fetchCurrentUserRole,
    fetchPeopleWithAccess,
    isSharingLoading,
    sharingError,
  };
};