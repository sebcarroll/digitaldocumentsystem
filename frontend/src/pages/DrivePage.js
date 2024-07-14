import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchDriveFiles, checkAuth } from '../services/api';

const DrivePage = () => {
  const [driveContent, setDriveContent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const getDriveFiles = async () => {
      try {
        const authStatus = await checkAuth();
        if (!authStatus.authenticated) {
          navigate('/login');
          return;
        }

        const content = await fetchDriveFiles();
        setDriveContent(content.files);
      } catch (error) {
        console.error('Failed to fetch drive files:', error);
        setError('Failed to load Google Drive files.');
      } finally {
        setLoading(false);
      }
    };

    getDriveFiles();
  }, [navigate]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div>
      <h1>Google Drive Files</h1>
      {driveContent.length === 0 ? (
        <p>No files found in Google Drive.</p>
      ) : (
        <ul>
          {driveContent.map((file) => (
            <li key={file.id}>{file.name} ({file.id})</li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default DrivePage;