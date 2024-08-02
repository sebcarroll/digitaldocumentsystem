// useFileSharing.js
import { useState, useEffect, useCallback } from 'react';
import { searchUsers, getPeopleWithAccess, shareFile, updatePermission, removePermission, updateGeneralAccess } from '../services/api';

export const useFileSharing = (items) => {
  const [email, setEmail] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [peopleWithAccess, setPeopleWithAccess] = useState([]);
  const [generalAccess, setGeneralAccess] = useState('Restricted');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchPeopleWithAccess = useCallback(async () => {
    if (items.length === 0) return;
    setIsLoading(true);
    setError(null);
    try {
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

  useEffect(() => {
    fetchPeopleWithAccess();
  }, [fetchPeopleWithAccess]);

  const handleEmailChange = useCallback(async (value) => {
    setEmail(value);
    if (value.length > 2) {
      try {
        const response = await searchUsers(value);
        setSearchResults(response.users);
      } catch (err) {
        console.error('Failed to search users:', err);
        setSearchResults([]);
      }
    } else {
      setSearchResults([]);
    }
  }, []);

  const handleAddPerson = useCallback(async (person) => {
    setIsLoading(true);
    setError(null);
    try {
      await Promise.all(items.map(item => shareFile(item.id, [person.email], 'reader')));
      await fetchPeopleWithAccess();
      setSearchResults([]);
      setEmail('');
    } catch (err) {
      setError('Failed to share with the selected person');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [items, fetchPeopleWithAccess]);

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
  }, [items, fetchPeopleWithAccess]);

  const handleGeneralAccessChange = useCallback(async (newAccess) => {
    setIsLoading(true);
    setError(null);
    try {
      await Promise.all(items.map(item => updateGeneralAccess(item.id, newAccess)));
      setGeneralAccess(newAccess);
    } catch (err) {
      setError('Failed to update general access');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [items]);

  return {
    email,
    searchResults,
    peopleWithAccess,
    generalAccess,
    isLoading,
    error,
    handleEmailChange,
    handleAddPerson,
    handleAccessLevelChange,
    handleRemoveAccess,
    handleGeneralAccessChange,
  };
};