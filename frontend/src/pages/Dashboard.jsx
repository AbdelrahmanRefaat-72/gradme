import React, { useState, useEffect } from 'react';
import StatCard from '../components/StatCard';
import ThreatBadge from '../components/ThreatBadge';
import AISummaryModal from '../components/AISummaryModal';
import ThreatDetailModal from '../components/ThreatDetailModal';
import { Mail, ShieldAlert, Target, Bell, Sparkles, AlertTriangle, ExternalLink, RefreshCw } from 'lucide-react';
import api from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [recentEmails, setRecentEmails] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modals state
  const [selectedSummary, setSelectedSummary] = useState(null);
  const [selectedSummarySubject, setSelectedSummarySubject] = useState('');
  const [selectedThreatEmail, setSelectedThreatEmail] = useState(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [statsRes, emailsRes] = await Promise.all([
        api.get('/stats/dashboard'),
        api.get('/emails/recent?limit=10')
      ]);
      setStats(statsRes.data);
      setRecentEmails(emailsRes.data);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const openSummaryModal = async (emailId, subject) => {
    try {
      const res = await api.get(`/summary/${emailId}`);
      setSelectedSummary(res.data);
      setSelectedSummarySubject(subject);
    } catch (err) {
      console.error('Failed to load summary:', err);
    }
  };

  const openThreatModal = async (emailId) => {
    try {
      const res = await api.get(`/emails/${emailId}`);
      setSelectedThreatEmail(res.data);
    } catch (err) {
      console.error('Failed to load threat detail:', err);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh]">
        <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight">Security Overview Dashboard</h2>
          <p className="text-xs text-slate-400 mt-1">Real-time threat status & expected email intelligence</p>
        </div>
        <button
          onClick={fetchDashboardData}
          className="self-start sm:self-auto px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center gap-2 transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh Stats
        </button>
      </div>

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Total Emails Analyzed"
          value={stats?.total_emails || 0}
          icon={Mail}
          color="blue"
          subtitle="Processed from Inbox & Spam"
        />
        <StatCard
          title="Suspicious Threats"
          value={stats?.suspicious_count || 0}
          icon={ShieldAlert}
          color="rose"
          subtitle={`${stats?.high_risk_count || 0} High Risk • ${stats?.medium_risk_count || 0} Medium`}
        />
        <StatCard
          title="Expected Emails"
          value={stats?.expected_count || 0}
          icon={Target}
          color="emerald"
          subtitle={`${stats?.active_rules_count || 0} Active User Rules`}
        />
        <StatCard
          title="Unread Alerts"
          value={stats?.unread_notifications || 0}
          icon={Bell}
          color="amber"
          subtitle="Dashboard & Telegram Logs"
        />
      </div>

      {/* High Risk Security Notice Banner */}
      {stats?.high_risk_count > 0 && (
        <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-between glow-rose">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-6 h-6 text-rose-400 shrink-0" />
            <div>
              <h4 className="text-sm font-bold text-rose-300">High Risk Phishing Threats Detected!</h4>
              <p className="text-xs text-slate-400">Our Rule-Based Engine flagged {stats.high_risk_count} emails with critical threat indicators.</p>
            </div>
          </div>
          <a
            href="/suspicious-emails"
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-rose-600 hover:bg-rose-500 text-white shadow-lg transition-all shrink-0"
          >
            Review Threats
          </a>
        </div>
      )}

      {/* Recent Emails Feed */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Mail className="w-4 h-4 text-cyan-400" />
            Recent Incoming Email Feed
          </h3>
          <span className="text-xs text-slate-400">Latest 10 emails</span>
        </div>

        {recentEmails.length === 0 ? (
          <div className="text-center py-12 text-slate-500 text-sm">
            No emails synced yet. Click "Sync Gmail" in the top bar to fetch messages!
          </div>
        ) : (
          <div className="space-y-3">
            {recentEmails.map((email) => (
              <div
                key={email.id}
                className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="space-y-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-bold text-white truncate max-w-[240px]">{email.sender}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 uppercase font-mono">{email.folder}</span>
                    {email.is_expected && (
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-semibold">
                        🎯 Expected Email
                      </span>
                    )}
                  </div>
                  <h4 className="text-sm font-semibold text-slate-200 truncate">{email.subject || '(No Subject)'}</h4>
                  <p className="text-xs text-slate-400 truncate max-w-2xl">{email.snippet}</p>
                </div>

                {/* Badges & Actions */}
                <div className="flex items-center gap-3 shrink-0">
                  {email.is_suspicious ? (
                    <button
                      onClick={() => openThreatModal(email.id)}
                      className="hover:opacity-80 transition-opacity"
                    >
                      <ThreatBadge level={email.suspicious_analysis?.risk_level || 'HIGH_RISK'} score={email.suspicious_analysis?.risk_score || 60} />
                    </button>
                  ) : (
                    <ThreatBadge level="SAFE" score={0} />
                  )}

                  {/* AI Summary Button */}
                  <button
                    onClick={() => openSummaryModal(email.id, email.subject)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 transition-all"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                    AI Summary
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modals */}
      <AISummaryModal
        isOpen={!!selectedSummary}
        onClose={() => setSelectedSummary(null)}
        summary={selectedSummary}
        emailSubject={selectedSummarySubject}
      />
      <ThreatDetailModal
        isOpen={!!selectedThreatEmail}
        onClose={() => setSelectedThreatEmail(null)}
        email={selectedThreatEmail}
      />
    </div>
  );
};

export default Dashboard;
