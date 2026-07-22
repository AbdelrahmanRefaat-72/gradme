import React, { useState, useEffect } from 'react';
import ThreatBadge from '../components/ThreatBadge';
import ThreatDetailModal from '../components/ThreatDetailModal';
import { ShieldAlert, AlertTriangle, RefreshCw } from 'lucide-react';
import api from '../services/api';

const SuspiciousEmails = () => {
  const [suspiciousEmails, setSuspiciousEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedEmail, setSelectedEmail] = useState(null);

  const fetchSuspicious = async () => {
    setLoading(true);
    try {
      const res = await api.get('/emails/suspicious');
      setSuspiciousEmails(res.data);
    } catch (err) {
      console.error('Failed to load suspicious emails:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSuspicious();
  }, []);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <ShieldAlert className="w-6 h-6 text-rose-400" />
            Suspicious Email Threats
          </h2>
          <p className="text-xs text-slate-400 mt-1">Rule-Based Phishing Engine Threat Intelligence Log</p>
        </div>
        <button
          onClick={fetchSuspicious}
          className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center gap-2"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="p-12 text-center text-cyan-400">Loading threat logs...</div>
      ) : suspiciousEmails.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-2xl border border-slate-800">
          <ShieldAlert className="w-12 h-12 text-emerald-400 mx-auto mb-3 opacity-60" />
          <h3 className="text-base font-bold text-white">No Suspicious Threats Found</h3>
          <p className="text-xs text-slate-400 mt-1">All processed emails passed authentication and domain alignment rules.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {suspiciousEmails.map((email) => (
            <div
              key={email.id}
              className="glass-panel p-5 rounded-2xl border border-rose-500/20 hover:border-rose-500/40 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div className="space-y-2 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-bold text-white">{email.sender}</span>
                  {email.suspicious_analysis && (
                    <ThreatBadge level={email.suspicious_analysis.risk_level} score={email.suspicious_analysis.risk_score} />
                  )}
                </div>
                <h4 className="text-sm font-semibold text-slate-200">{email.subject || '(No Subject)'}</h4>
                <p className="text-xs text-slate-400 truncate max-w-2xl">{email.snippet}</p>
                
                {/* Triggered Reasons Summary */}
                {email.suspicious_analysis?.reasons && (
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {email.suspicious_analysis.reasons.map((r, i) => (
                      <span key={i} className="text-[10px] px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20">
                        {r.split('(')[0]}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <button
                onClick={() => setSelectedEmail(email)}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 transition-all shrink-0 self-start md:self-auto"
              >
                Inspect Threat Report
              </button>
            </div>
          ))}
        </div>
      )}

      <ThreatDetailModal
        isOpen={!!selectedEmail}
        onClose={() => setSelectedEmail(null)}
        email={selectedEmail}
      />
    </div>
  );
};

export default SuspiciousEmails;
