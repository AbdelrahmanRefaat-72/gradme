import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { RefreshCw } from 'lucide-react';

const AuthCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { refreshUser } = useAuth();

  useEffect(() => {
    const token = searchParams.get('token');
    if (token) {
      localStorage.setItem('guardian_token', token);
      refreshUser().then(() => {
        navigate('/dashboard');
      });
    } else {
      navigate('/login');
    }
  }, [searchParams, navigate, refreshUser]);

  return (
    <div className="min-h-screen bg-dark-900 flex flex-col items-center justify-center text-center p-6">
      <RefreshCw className="w-10 h-10 text-cyan-400 animate-spin mb-4" />
      <h2 className="text-xl font-bold text-white">Authenticating with Google OAuth...</h2>
      <p className="text-xs text-slate-400 mt-2">Setting up your secure session tokens...</p>
    </div>
  );
};

export default AuthCallback;
