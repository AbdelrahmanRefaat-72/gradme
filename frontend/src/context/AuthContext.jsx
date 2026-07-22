import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchCurrentUser = async () => {
    const token = localStorage.getItem('guardian_token');
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const res = await api.get('/auth/me');
      setUser(res.data);
    } catch (err) {
      console.error('Failed to load user profile:', err);
      localStorage.removeItem('guardian_token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCurrentUser();
  }, []);

  const loginWithGoogle = async () => {
    try {
      const res = await api.get('/auth/google/login');
      if (res.data.auth_url) {
        window.location.href = res.data.auth_url;
      }
    } catch (err) {
      console.error('Failed to initiate Google OAuth:', err);
      alert('Could not start Google OAuth. Ensure GOOGLE_CLIENT_ID is configured in backend.');
    }
  };

  const devLogin = async (email = 'dev.user@emailguardian.local') => {
    try {
      const res = await api.post(`/auth/dev-login?email=${encodeURIComponent(email)}`);
      if (res.data.access_token) {
        localStorage.setItem('guardian_token', res.data.access_token);
        await fetchCurrentUser();
        return true;
      }
    } catch (err) {
      console.error('Dev login failed:', err);
      alert('Dev login failed. Check backend status.');
    }
    return false;
  };

  const logout = () => {
    localStorage.removeItem('guardian_token');
    setUser(null);
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider value={{ user, loading, loginWithGoogle, devLogin, logout, refreshUser: fetchCurrentUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
