import React, { useState, useEffect } from 'react';
import { Bell, CheckCheck, Send, ShieldAlert, Target } from 'lucide-react';
import api from '../services/api';

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const res = await api.get('/notifications');
      setNotifications(res.data);
    } catch (err) {
      console.error('Failed to load notifications:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const markAsRead = async (notifId) => {
    try {
      await api.patch(`/notifications/${notifId}/read`);
      fetchNotifications();
    } catch (err) {
      console.error('Failed to mark read:', err);
    }
  };

  const markAllRead = async () => {
    try {
      await api.post('/notifications/read-all');
      fetchNotifications();
    } catch (err) {
      console.error('Failed to mark all read:', err);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <Bell className="w-6 h-6 text-amber-400" />
            Security & Expected Email Notifications
          </h2>
          <p className="text-xs text-slate-400 mt-1">Audit log of UI alerts and Telegram bot dispatches</p>
        </div>
        <button
          onClick={markAllRead}
          className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center gap-2 transition-all"
        >
          <CheckCheck className="w-4 h-4 text-emerald-400" />
          Mark All Read
        </button>
      </div>

      {loading ? (
        <div className="p-12 text-center text-cyan-400">Loading notifications...</div>
      ) : notifications.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-2xl border border-slate-800">
          <Bell className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-bold text-white">No Notifications Yet</h3>
          <p className="text-xs text-slate-400 mt-1">Alerts for expected emails and threat warnings will appear here.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {notifications.map((notif) => {
            const isPhishing = notif.notification_type === 'PHISHING_ALERT';
            return (
              <div
                key={notif.id}
                className={`glass-panel p-5 rounded-2xl border ${
                  notif.is_read ? 'border-slate-800/80 opacity-75' : isPhishing ? 'border-rose-500/40 bg-rose-500/5' : 'border-emerald-500/40 bg-emerald-500/5'
                } transition-all flex flex-col md:flex-row md:items-center justify-between gap-4`}
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    {isPhishing ? (
                      <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 font-semibold">
                        <ShieldAlert className="w-3 h-3" /> Phishing Alert
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-semibold">
                        <Target className="w-3 h-3" /> Expected Email
                      </span>
                    )}
                    <span className="text-[10px] text-slate-500">
                      {new Date(notif.created_at).toLocaleString()}
                    </span>
                    {notif.sent_to_telegram && (
                      <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 inline-flex items-center gap-1">
                        <Send className="w-3 h-3" /> Telegram Sent
                      </span>
                    )}
                  </div>
                  <h4 className="text-sm font-bold text-white">{notif.title}</h4>
                  <pre className="text-xs text-slate-300 font-sans whitespace-pre-wrap">{notif.message_text}</pre>
                </div>

                {!notif.is_read && (
                  <button
                    onClick={() => markAsRead(notif.id)}
                    className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors shrink-0 self-start md:self-auto"
                  >
                    Mark Read
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Notifications;
