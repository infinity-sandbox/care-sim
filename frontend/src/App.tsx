import React, { useState, useEffect } from 'react';
import { Routes, Route, BrowserRouter } from 'react-router-dom';
import Login from './components/Login';
import ForgotPassword from './components/forgetLink/forgetLinkPage';
import PasswordResetPage from './components/forgetLink/emailRedirectedPage';
import SuccessRegistrationPage from './components/statusPages/successRegistrationPage';
import PrivateRoute from './components/PrivateRoute';
import Register from './components/RegisterForm';
import './App.css';
import DaycareSimulator from './components/DaycareSimulator';
import { SimulatorProvider } from './contexts/SimulatorContext';
import { getUserData } from './services/api';
import './App.css';
import './styles/simulator.css';
import './styles/responsive.css';
import UserAvatar from './components/DaycareSimulator/UserAvatar';


function App() {
  const [userEmail, setUserEmail] = useState('');
  

  useEffect(() => {
    // Fetch user data on app load
    const fetchUserData = async () => {
      try {
        const userData = await getUserData();
        console.log("Fetched user data:", userData); // 👈 Debug
        setUserEmail(userData.email);
        console.log("Set user data:", userData.email); // 👈 Debug
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    };
    
    fetchUserData();
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path='/forgot/password' element={<ForgotPassword />} />
        <Route path='/reset/password' element={<PasswordResetPage />} />
        <Route path='/success/registration' element={<SuccessRegistrationPage />} />
        <Route path='/register' element={<Register />} />
        <Route path="/simulator" element={
          <PrivateRoute>
            <SimulatorProvider email={userEmail}>
              <DaycareSimulator />
            </SimulatorProvider>
          </PrivateRoute>
        } />  
      </Routes>
    </BrowserRouter>
  );
}

export default App;

