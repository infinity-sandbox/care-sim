import React from 'react';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import logo from '../images/arcturus_logo_white.png'; // Adjust the path to your logo image

const Sidebar: React.FC = () => {
  const navigate = useNavigate(); // Hook to programmatically navigate

  const handleLogout = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault(); // Prevent default link behavior
    // Remove tokens from local storage
    localStorage.removeItem('token');
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');

    // Navigate to login page after logout
    navigate('/login');
  };

  return (
    <div className="sidebar">
      <img src={logo} alt="Logo" className="sidebar-icon" />
      <div className="nav-links">
        {/* <Link to="/home" className="nav-link">Home</Link> */}
        <Link to="/chatbot" className="nav-link">Genie</Link>
        {/* <Link to="/dashboard" className="nav-link">Dashboard</Link> */}
        {/* <Link to="#" className="nav-link">Genie Whisper</Link> */}
        {/* <Link to="#" className="nav-link">Profile</Link> */}
        {/* <Link to="#" className="nav-link">Settings</Link> */}
        <Link to="" onClick={handleLogout} className="nav-link">Sign Out</Link>
      </div>
    </div>
  );
}

export default Sidebar;
