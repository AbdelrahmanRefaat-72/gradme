import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Shield, Sparkles, Target, Lock, CheckCircle, ArrowRight, Code } from 'lucide-react';

const Login = () => {
  const { loginWithGoogle, devLogin } = useAuth();

  return (
    <div className="min-h-screen bg-dark-900 flex flex-col justify-between relative overflow-hidden">
      {/* Glow Effects */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-10 right-10 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl pointer-events-none"></div>

      {/* Header */}
      <header className="p-6 flex items-center justify-between max-w-7xl mx-auto w-full">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <span className="text-lg font-bold text-white tracking-tight">Smart Email Guardian</span>
        </div>
        <span className="text-xs px-3 py-1 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
          Cyber Security Graduation Project
        </span>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-12 text-center z-10">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 text-xs font-semibold mb-6 glow-cyan">
          <Shield className="w-3.5 h-3.5" />
          Deterministic Rule Engine • AI Summarization • Telegram Alerts
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold text-white tracking-tight leading-tight">
          Next-Gen AI & Rule-Based <br />
          <span className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 bg-clip-text text-transparent">
            Email Threat Protection
          </span>
        </h1>

        <p className="mt-6 text-base sm:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
          Continuously monitors your Gmail inbox and spam folders. Detects phishing threats deterministically with zero AI hallucinations, tracks expected emails, and dispatches structured AI summaries to Telegram.
        </p>

        {/* CTAs */}
        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <button
            onClick={loginWithGoogle}
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl font-bold text-sm bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-xl shadow-cyan-500/25 flex items-center justify-center gap-3 transition-all hover:scale-105"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path fill="#ffffff" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="#ffffff" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#ffffff" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
              <path fill="#ffffff" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
            </svg>
            Sign In with Google OAuth 2.0
          </button>

          <button
            onClick={() => devLogin()}
            className="w-full sm:w-auto px-6 py-3.5 rounded-xl font-semibold text-sm bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700 flex items-center justify-center gap-2 transition-colors"
          >
            <Code className="w-4 h-4 text-cyan-400" />
            Instant Developer Demo Login
          </button>
        </div>

        {/* Feature Highlights Grid */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          <div className="glass-panel p-6 rounded-2xl border border-slate-800">
            <div className="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400 mb-4">
              <Lock className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Rule-Based Phishing Engine</h3>
            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
              SPF, DKIM, DMARC validation, Reply-To mismatch, lookalike typosquatting, high-risk TLDs, and URL shortener detection.
            </p>
          </div>

          <div className="glass-panel p-6 rounded-2xl border border-slate-800">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 mb-4">
              <Target className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Expected Emails Engine</h3>
            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
              Track important senders, domains, or subjects across Inbox & Spam. Never miss a job interview or offer letter.
            </p>
          </div>

          <div className="glass-panel p-6 rounded-2xl border border-slate-800">
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 mb-4">
              <Sparkles className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">AI Summarizer & Telegram</h3>
            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
              Extracted dates, times, deadlines, locations, and action items delivered instantly to your Telegram bot.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="p-6 text-center text-xs text-slate-600 border-t border-slate-800/60">
        Smart Email Guardian • Built with FastAPI, React, Tailwind CSS, SQLite & Google OAuth 2.0
      </footer>
    </div>
  );
};

export default Login;
