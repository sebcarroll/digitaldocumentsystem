import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
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
        <Route path="/drive" element={<DrivePage />} />
      </Routes>
    </Router>
  );
}

export default App;