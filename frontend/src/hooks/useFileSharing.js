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

  useEffect(() => {
    const fetchCurrentUserRole = async () => {
      try {
        const userInfo = await getCurrentUserRole();
        setCurrentUserId(userInfo.id);
      } catch (error) {
        console.error('Failed to fetch current user info:', error);
      }
    };

    fetchCurrentUserRole();
  }, []);

  const fetchPeopleWithAccess = useCallback(async () => {
    if (items.length === 0) return;
    setIsLoading(true);
    setError(null);
    try {
      // Fetch current user's role first
      const userRole = await getCurrentUserRole(items[0].id);
      setCurrentUserRole(userRole.role);
  
      const responses = await Promise.all(items.map(item => getPeopleWithAccess(item.id)));
      const allPeople = responses.flatMap(response => response.peopleWithAccess);
      const uniquePeople = allPeople.reduce((acc, person) => {
        if (!acc.some(p => p.emailAddress === person.emailAddress)) {
          acc.push(person);
        }
        return acc;
      }, []);
      setPeopleWithAccess(uniquePeople);
    } catch (err) {
      setError('Failed to fetch people with access');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [items]);

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
    setIsLoading(true);
    setError(null);
    try {
      await Promise.all(items.map(item => 
        Promise.all(pendingEmails.map(email => 
          shareFile(item.id, [email], 'viewer')
        ))
      ));
      await fetchPeopleWithAccess();
      setPendingEmails([]);
    } catch (err) {
      setError('Failed to share with some or all of the added emails');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [items, pendingEmails, fetchPeopleWithAccess]);

  const handleAccessLevelChange = useCallback(async (personId, newRole) => {
    setIsLoading(true);
    setError(null);
    try {
      await Promise.all(items.map(item => updatePermission(item.id, personId, newRole)));
      await fetchPeopleWithAccess();
    } catch (err) {
      setError('Failed to update permission');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [items, fetchPeopleWithAccess]);

  const handleRemoveAccess = useCallback(async (personId) => {
    if (currentUserRole !== 'editor' && currentUserRole !== 'owner') return;
    setIsLoading(true);
    setError(null);
    try {
      await Promise.all(items.map(item => removePermission(item.id, personId)));
      await fetchPeopleWithAccess();
    } catch (err) {
      setError('Failed to remove access');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [items, fetchPeopleWithAccess, currentUserRole]);

  const handleGeneralAccessChange = useCallback(async (newAccess) => {
    if (currentUserRole !== 'editor' && currentUserRole !== 'owner') return;
    setIsLoading(true);
    setError(null);
    try {
      await Promise.all(items.map(item => updateGeneralAccess(item.id, newAccess, linkAccessRole)));
      setGeneralAccess(newAccess);
    } catch (err) {
      setError('Failed to update general access');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [items, currentUserRole, linkAccessRole]);

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
  };
};