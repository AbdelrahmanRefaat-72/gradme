import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Settings as SettingsIcon, Send, CheckCircle2, AlertCircle, Bot } from 'lucide-react';
import api from '../services/api';

const Settings = () => {
  const { user, refreshUser } = useAuth();
  const [chatId, setChatId] = useState('');
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [statusMsg, setStatusMsg] = useState(null);

  useEffect(() => {
    if (user?.telegram_chat_id) {
      setChatId(user.telegram_chat_id);
    }
  }, [user]);

  const handleSaveTelegram = async (e) => {
    e.preventDefault();
    setSaving(true);
    setStatusMsg(null);
    try {
      await api.post('/settings/telegram', { telegram_chat_id: chatId.trim() });
      await refreshUser();
      setStatusMsg({ type: 'success', text: 'Telegram Chat ID saved successfully! Welcome test message sent.' });
    } catch (err) {
      console.error('Failed to save Telegram Chat ID:', err);
      setStatusMsg({ type: 'error', text: 'Could not save Telegram Chat ID.' });
    } finally {
      setSaving(false);
    }
  };

  const handleTestAlert = async () => {
    setTesting(true);
    setStatusMsg(null);
    try {
      await api.post('/settings/telegram/test');
      setStatusMsg({ type: 'success', text: 'Test alert sent to your Telegram chat!' });
    } catch (err) {
      console.error('Test notification failed:', err);
      setStatusMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to deliver test message.' });
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl space-y-8">
      <div>
        <h2 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
          <SettingsIcon className="w-6 h-6 text-purple-400" />
          Settings & Integrations
        </h2>
        <p className="text-xs text-slate-400 mt-1">Configure Telegram Bot alerts and system preferences</p>
      </div>

      {/* Telegram Bot Integration Card */}
      <div className="glass-panel p-6 rounded-2xl border border-purple-500/30 space-y-6 glow-purple">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Telegram Bot Notification Setup</h3>
            <p className="text-xs text-slate-400">Receive real-time alerts for phishing threats and expected email arrivals</p>
          </div>
        </div>

        {statusMsg && (
          <div
            className={`p-3.5 rounded-xl border text-xs flex items-center gap-2 ${
              statusMsg.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
            }`}
          >
            {statusMsg.type === 'success' ? <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" /> : <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />}
            <span>{statusMsg.text}</span>
          </div>
        )}

        <form onSubmit={handleSaveTelegram} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Telegram Chat ID
            </label>
            <div className="flex gap-3">
              <input
                type="text"
                value={chatId}
                onChange={(e) => setChatId(e.target.value)}
                placeholder="e.g. 123456789"
                className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-white placeholder:text-slate-600 focus:outline-none focus:border-purple-500"
              />
              <button
                type="submit"
                disabled={saving}
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-purple-600 hover:bg-purple-500 text-white shadow-lg transition-colors disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save Chat ID'}
              </button>
            </div>
            <p className="text-[11px] text-slate-500 mt-2">
              How to get your Chat ID: Start a conversation with your Telegram bot or send a message to <code className="text-purple-300">@userinfobot</code>.
            </p>
          </div>
        </form>

        {user?.telegram_chat_id && (
          <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
            <span className="text-xs text-slate-400">Telegram Status: <strong className="text-emerald-400">Connected ({user.telegram_chat_id})</strong></span>
            <button
              onClick={handleTestAlert}
              disabled={testing}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center gap-2 transition-all disabled:opacity-50"
            >
              <Send className={`w-3.5 h-3.5 ${testing ? 'animate-pulse text-purple-400' : ''}`} />
              {testing ? 'Sending Test Alert...' : 'Dispatch Test Alert'}
            </button>
          </div>
        )}
      </div>

      {/* Security Architecture Info */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-3">
        <h3 className="text-sm font-bold text-white">Security Architecture Summary</h3>
        <ul className="space-y-2 text-xs text-slate-400">
          <li>• <strong className="text-slate-200">OAuth Scope:</strong> <code className="text-cyan-400">gmail.readonly</code> (Least Privilege). No write or delete permissions requested.</li>
          <li>• <strong className="text-slate-200">Threat Engine:</strong> 100% Deterministic Rule Engine. Zero AI hallucinations in risk scoring.</li>
          <li>• <strong className="text-slate-200">AI Privacy:</strong> Gemini API is strictly invoked for summarizing text of expected/important emails.</li>
          <li>• <strong className="text-slate-200">Token Management:</strong> Refresh tokens are stored and auto-renewed transparently.</li>
        </ul>
      </div>
    </div>
  );
};

export default Settings;
