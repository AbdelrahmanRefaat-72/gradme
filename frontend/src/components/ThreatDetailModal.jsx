import React from 'react';
import { X, ShieldAlert, AlertTriangle, ShieldCheck, CheckCircle2 } from 'lucide-react';
import ThreatBadge from './ThreatBadge';

const ThreatDetailModal = ({ isOpen, onClose, email }) => {
  if (!isOpen || !email) return null;

  const analysis = email.suspicious_analysis;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fadeIn">
      <div className="glass-panel w-full max-w-2xl rounded-2xl border border-rose-500/30 overflow-hidden glow-rose shadow-2xl">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-900/80 flex items-center justify-between">
          <div className="flex items-center gap-2 text-rose-400 font-semibold text-sm">
            <ShieldAlert className="w-5 h-5 text-rose-400" />
            Threat Inspection Report
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 max-h-[80vh] overflow-y-auto">
          {/* Email Header Metadata */}
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400">Sender Header</span>
              {analysis && <ThreatBadge level={analysis.risk_level} score={analysis.risk_score} />}
            </div>
            <p className="text-sm font-bold text-white break-all">{email.sender}</p>
            {email.reply_to && (
              <p className="text-xs text-rose-300 font-mono">Reply-To Header: {email.reply_to}</p>
            )}
            <p className="text-xs font-medium text-slate-300">Subject: {email.subject || '(No Subject)'}</p>
          </div>

          {/* Analysis Results */}
          {analysis ? (
            <div className="space-y-4">
              {/* Score Gauge */}
              <div className="p-4 rounded-xl bg-rose-500/5 border border-rose-500/20 flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Calculated Risk Score</p>
                  <p className="text-3xl font-extrabold text-rose-400 mt-0.5">{analysis.risk_score} <span className="text-xs font-normal text-slate-400">/ 100+</span></p>
                </div>
                <div className="text-right">
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Risk Category</p>
                  <p className="text-sm font-bold text-rose-300 mt-1">{analysis.risk_level}</p>
                </div>
              </div>

              {/* Reasons List */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Triggered Rule Violations</h4>
                <div className="space-y-2">
                  {analysis.reasons?.map((reason, idx) => (
                    <div key={idx} className="p-3 rounded-xl bg-slate-900/60 border border-rose-500/20 text-xs text-rose-200 flex items-start gap-2.5">
                      <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                      <span>{reason}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recommendation */}
              <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs space-y-1">
                <p className="font-bold uppercase tracking-wider text-[10px] text-amber-400">Cyber Security Recommendation</p>
                <p>{analysis.recommendation}</p>
              </div>
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              <span>No threat indicators were triggered for this email.</span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-900/80 text-right">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
          >
            Close Report
          </button>
        </div>
      </div>
    </div>
  );
};

export default ThreatDetailModal;
