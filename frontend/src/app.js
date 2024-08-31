import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import AuthSuccess from './pages/AuthSuccess';
import FAQPage from './pages/FaqPage';
import MyDrivePage from './pages/MyDrivePage';
import SharedWithMePage from './pages/SharedWithMePage';
import RecentPage from './pages/RecentPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/auth-success" element={<AuthSuccess />} />
        <Route path="/drive" element={<HomePage />} />
        <Route path="/my-drive" element={<MyDrivePage />} />
        <Route path="/shared-with-me" element={<SharedWithMePage />} />
        <Route path="/recent" element={<RecentPage />} />
        <Route path="/faq" element={<FAQPage />} />
      </Routes>
    </Router>
  );
}
export default App;