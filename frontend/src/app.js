import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { DriveProvider } from './contexts/driveContext'; // Adjust the import path as necessary
import LoginPage from './pages/LoginPage';
import DrivePage from './pages/DrivePage';
import AuthSuccess from './pages/AuthSuccess';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/auth-success" element={<AuthSuccess />} />
        <Route 
          path="/drive" 
          element={
            <DriveProvider>
              <DrivePage />
            </DriveProvider>
          } 
        />
      </Routes>
    </Router>
  );
}

export default App;