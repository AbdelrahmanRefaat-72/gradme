import React from 'react';
import { ShieldCheck, AlertTriangle, AlertOctagon } from 'lucide-react';

const ThreatBadge = ({ level, score }) => {
  if (level === 'HIGH_RISK') {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30 glow-rose">
        <AlertOctagon className="w-3.5 h-3.5" />
        High Risk ({score})
      </span>
    );
  }

  if (level === 'MEDIUM_RISK') {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
        <AlertTriangle className="w-3.5 h-3.5" />
        Medium Risk ({score})
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 glow-emerald">
      <ShieldCheck className="w-3.5 h-3.5" />
      Safe ({score})
    </span>
  );
};

export default ThreatBadge;
