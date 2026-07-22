import React from 'react';

const StatCard = ({ title, value, icon: Icon, color = 'blue', subtitle }) => {
  const colorMap = {
    blue: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30',
    rose: 'text-rose-400 bg-rose-500/10 border-rose-500/30',
    amber: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
    emerald: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
    purple: 'text-purple-400 bg-purple-500/10 border-purple-500/30',
  };

  return (
    <div className="glass-panel p-5 rounded-2xl flex items-start justify-between relative overflow-hidden group hover:border-slate-700 transition-all duration-300">
      <div>
        <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">{title}</p>
        <h3 className="text-3xl font-extrabold text-white tracking-tight">{value}</h3>
        {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
      </div>
      <div className={`p-3.5 rounded-xl border ${colorMap[color] || colorMap.blue} transition-transform group-hover:scale-110 duration-200`}>
        <Icon className="w-6 h-6" />
      </div>
    </div>
  );
};

export default StatCard;
