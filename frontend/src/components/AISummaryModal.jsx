import React from 'react';
import { X, Sparkles, Calendar, Clock, MapPin, CheckSquare, Link, User } from 'lucide-react';

const AISummaryModal = ({ isOpen, onClose, summary, emailSubject }) => {
  if (!isOpen || !summary) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
      <div className="glass-panel w-full max-w-2xl rounded-2xl border border-cyan-500/30 overflow-hidden glow-cyan shadow-2xl">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-900/80 flex items-center justify-between">
          <div className="flex items-center gap-2 text-cyan-400 font-semibold text-sm">
            <Sparkles className="w-4 h-4 text-cyan-400 animate-pulse" />
            AI Intelligence Summary
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
          {/* Headline */}
          <div>
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Subject Overview</span>
            <h3 className="text-lg font-bold text-white mt-1">{summary.summary_headline || emailSubject}</h3>
          </div>

          {/* Bullet Points */}
          <div>
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Concise Key Points</span>
            <ul className="mt-2 space-y-2">
              {summary.bullet_points.map((bp, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-slate-200 bg-slate-900/40 p-2.5 rounded-lg border border-slate-800/80">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mt-2 shrink-0"></span>
                  <span>{bp}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Extracted Metadata Grids */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Dates & Times */}
            {(summary.extracted_dates?.length > 0 || summary.extracted_times?.length > 0) && (
              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="flex items-center gap-2 text-xs font-bold text-slate-300 mb-2">
                  <Calendar className="w-4 h-4 text-cyan-400" />
                  Extracted Dates & Times
                </div>
                <div className="space-y-1 text-xs text-slate-300">
                  {summary.extracted_dates?.map((d, i) => <div key={i} className="text-cyan-300 font-mono">• Date: {d}</div>)}
                  {summary.extracted_times?.map((t, i) => <div key={i} className="text-cyan-300 font-mono">• Time: {t}</div>)}
                </div>
              </div>
            )}

            {/* Locations */}
            {summary.extracted_locations?.length > 0 && (
              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
                <div className="flex items-center gap-2 text-xs font-bold text-slate-300 mb-2">
                  <MapPin className="w-4 h-4 text-emerald-400" />
                  Extracted Locations
                </div>
                <div className="space-y-1 text-xs text-emerald-300">
                  {summary.extracted_locations.map((loc, i) => <div key={i}>• {loc}</div>)}
                </div>
              </div>
            )}

            {/* Action Items */}
            {summary.action_items?.length > 0 && (
              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 md:col-span-2">
                <div className="flex items-center gap-2 text-xs font-bold text-slate-300 mb-2">
                  <CheckSquare className="w-4 h-4 text-amber-400" />
                  Required Action Items
                </div>
                <ul className="space-y-1 text-xs text-amber-200">
                  {summary.action_items.map((act, i) => <li key={i}>• {act}</li>)}
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-900/80 text-right">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default AISummaryModal;
