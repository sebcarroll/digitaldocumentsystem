import { useState, useEffect, useCallback } from 'react';
import { searchUsers, getPeopleWithAccess, shareFile, updatePermission, removePermission, updateGeneralAccess, getCurrentUserRole } from '../services/api';

export const useFileSharing = (items) => {
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

  const fetchCurrentUserRole = useCallback(async () => {
    if (items.length === 0) return;
    setIsSharingLoading(true);
    setSharingError(null);
    try {
      const userInfo = await getCurrentUserRole(items[0].id);
      console.log('User Info from API:', userInfo);
      setCurrentUserRole(userInfo.role);
      setCurrentUserId(userInfo.id);
    } catch (error) {
      console.error('Failed to fetch current user info:', error);
      setSharingError('Failed to fetch user role');
    } finally {
      setIsSharingLoading(false);
    }
  }, [items]);

  useEffect(() => {
    fetchCurrentUserRole();
  }, [fetchCurrentUserRole]);

  const fetchPeopleWithAccess = useCallback(async () => {
    if (items.length === 0) return;
    setIsSharingLoading(true);
    setSharingError(null);
    try {
      const response = await getPeopleWithAccess(items[0].id);
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
    fetchPeopleWithAccess();
  }, [fetchPeopleWithAccess]);

  const handleEmailChange = useCallback((value) => {
    setEmail(value);
    if (value.length > 2) {
      searchUsers(value).then(response => {
        setSearchResults(response.users || []);
      }).catch(err => {
        console.error('Failed to search users:', err);
        setSearchResults([]);
      });
    } else {
      setSearchResults([]);
    }
  }, []);

  const handleAddPendingEmail = useCallback((emailToAdd) => {
    setPendingEmails(prev => [...prev, emailToAdd]);
    setEmail('');
  }, []);

  const handleRemovePendingEmail = useCallback((emailToRemove) => {
    setPendingEmails(prev => prev.filter(email => email !== emailToRemove));
  }, []);

  const handleShareWithPendingEmails = useCallback(async () => {
    setIsSharingLoading(true);
    setSharingError(null);
    try {
      await Promise.all(items.map(item => 
        Promise.all(pendingEmails.map(email => 
          shareFile(item.id, [email], 'viewer')
        ))
      ));
      await fetchPeopleWithAccess();
      setPendingEmails([]);
    } catch (err) {
      setSharingError('Failed to share with some or all of the added emails');
      console.error(err);
    } finally {
      setIsSharingLoading(false);
    }
  }, [items, pendingEmails, fetchPeopleWithAccess]);

  const handleAccessLevelChange = useCallback(async (personId, newRole) => {
    setIsSharingLoading(true);
    setSharingError(null);
    try {
      await Promise.all(items.map(item => updatePermission(item.id, personId, newRole)));
      await fetchPeopleWithAccess();
    } catch (err) {
      setSharingError('Failed to update permission');
      console.error(err);
    } finally {
      setIsSharingLoading(false);
    }
  }, [items, fetchPeopleWithAccess]);

  const handleRemoveAccess = useCallback(async (personId) => {
    if (currentUserRole !== 'writer' && currentUserRole !== 'owner') return;
    setIsSharingLoading(true);
    setSharingError(null);
    try {
      await Promise.all(items.map(item => removePermission(item.id, personId)));
      await fetchPeopleWithAccess();
    } catch (err) {
      setSharingError('Failed to remove access');
      console.error(err);
    } finally {
      setIsSharingLoading(false);
    }
  }, [items, fetchPeopleWithAccess, currentUserRole]);

  const handleGeneralAccessChange = async (newAccess, newLinkRole = linkAccessRole) => {
    if (currentUserRole !== 'writer' && currentUserRole !== 'owner') return;
    setIsLoading(true);
    setSharingError(null);
    try {
      await Promise.all(items.map(item => updateGeneralAccess(item.id, newAccess, newLinkRole)));
      setGeneralAccess(newAccess);
      setLinkAccessRole(newLinkRole);
    } catch (err) {
      setSharingError('Failed to update general access');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };
  
const handleLinkAccessChange = (newRole) => {
    setLinkAccessRole(newRole);
    // If you need to update this on the backend immediately:
    handleGeneralAccessChange(generalAccess, newRole);
  };


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
    handleLinkAccessChange,
    fetchCurrentUserRole,
    fetchPeopleWithAccess,
    isSharingLoading,
    sharingError,
  };
};