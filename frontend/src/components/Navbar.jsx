import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Shield, RefreshCw, Bell, LogOut, User as UserIcon } from 'lucide-react';
import api from '../services/api';

const Navbar = ({ onSyncComplete }) => {
  const { user, logout } = useAuth();
  const [syncing, setSyncing] = useState(false);
  const [syncError, setSyncError] = useState('');

  const handleSync = async () => {
    setSyncing(true);
    setSyncError('');
    try {
      await api.post('/emails/sync');
      if (onSyncComplete) onSyncComplete();
    } catch (err) {
      console.error('Sync failed:', err);
      setSyncError(err.response?.data?.detail || 'Gmail sync failed. Please try again.');
    } finally {
      setSyncing(false);
    }
  };

  return (
    <header className="min-h-16 border-b border-slate-800 bg-dark-900/80 backdrop-blur-md sticky top-0 z-40 px-6 py-3 flex flex-wrap items-center justify-between gap-3">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <Shield className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
            Smart Email Guardian
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 uppercase font-mono">
              AI Cyber Shield
            </span>
          </h1>
          <p className="text-xs text-slate-400">Rule-Based Threat Engine & Expected Email Tracking</p>
        </div>
      </div>

      {/* Quick Actions & Profile */}
      <div className="flex items-center gap-4">
        <button
          onClick={handleSync}
          disabled={syncing}
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin text-cyan-400' : ''}`} />
          {syncing ? 'Syncing Gmail...' : 'Sync Gmail'}
        </button>

        {/* Profile Card */}
        {user && (
          <div className="flex items-center gap-3 pl-3 border-l border-slate-800">
            {user.picture_url ? (
              <img src={user.picture_url} alt={user.full_name} className="w-8 h-8 rounded-full border border-slate-700" />
            ) : (
              <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-slate-300">
                <UserIcon className="w-4 h-4" />
              </div>
            )}
            <div className="hidden sm:block text-left">
              <p className="text-xs font-semibold text-slate-200">{user.full_name || 'User'}</p>
              <p className="text-[10px] text-slate-400 truncate max-w-[140px]">{user.email}</p>
            </div>
            <button
              onClick={logout}
              title="Sign Out"
              className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
      {syncError && (
        <div role="alert" className="w-full text-xs text-amber-200 bg-amber-500/10 border border-amber-500/30 rounded-lg px-3 py-2">
          {syncError}
        </div>
      )}
    </header>
  );
};

export default Navbar;
