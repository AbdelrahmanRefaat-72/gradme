import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, ShieldAlert, Target, Bell, Settings } from 'lucide-react';

const Sidebar = () => {
  const navItems = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/suspicious-emails', label: 'Suspicious Emails', icon: ShieldAlert },
    { to: '/expected-emails', label: 'Expected Emails', icon: Target },
    { to: '/notifications', label: 'Notifications', icon: Bell },
    { to: '/settings', label: 'Settings & Bot', icon: Settings },
  ];

  return (
    <aside className="w-64 border-r border-slate-800/80 bg-dark-900 flex flex-col justify-between p-4 shrink-0 hidden md:flex">
      <div className="space-y-1">
        <p className="px-3 text-[10px] font-semibold uppercase tracking-wider text-slate-500 mb-2">Main Menu</p>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/10 text-cyan-400 border border-cyan-500/30 font-semibold glow-cyan'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              {item.label}
            </NavLink>
          );
        })}
      </div>

      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-center">
        <p className="text-xs font-semibold text-slate-300">Deterministic Protection</p>
        <p className="text-[10px] text-slate-500 mt-1">Rule Engine Active • Zero AI Hallucinations for Threat Scores</p>
      </div>
    </aside>
  );
};

export default Sidebar;
