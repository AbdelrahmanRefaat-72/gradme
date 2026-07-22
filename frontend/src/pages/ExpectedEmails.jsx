import React, { useState, useEffect } from 'react';
import AISummaryModal from '../components/AISummaryModal';
import { Target, Plus, Trash2, Sparkles, CheckCircle2, RefreshCw } from 'lucide-react';
import api from '../services/api';

const ExpectedEmails = () => {
  const [rules, setRules] = useState([]);
  const [expectedEmails, setExpectedEmails] = useState([]);
  const [loading, setLoading] = useState(true);

  // Form state
  const [showAddForm, setShowAddForm] = useState(false);
  const [ruleType, setRuleType] = useState('SUBJECT_KEYWORD');
  const [ruleValue, setRuleValue] = useState('');
  const [description, setDescription] = useState('');

  // Modal
  const [selectedSummary, setSelectedSummary] = useState(null);
  const [selectedSubject, setSelectedSubject] = useState('');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [rulesRes, emailsRes] = await Promise.all([
        api.get('/expected-rules'),
        api.get('/emails/expected')
      ]);
      setRules(rulesRes.data);
      setExpectedEmails(emailsRes.data);
    } catch (err) {
      console.error('Failed to load expected email data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAddRule = async (e) => {
    e.preventDefault();
    if (!ruleValue.trim()) return;

    try {
      await api.post('/expected-rules', {
        rule_type: ruleType,
        rule_value: ruleValue.trim(),
        description: description.trim() || undefined,
      });
      setRuleValue('');
      setDescription('');
      setShowAddForm(false);
      fetchData();
    } catch (err) {
      console.error('Failed to create rule:', err);
      alert('Could not add rule.');
    }
  };

  const handleDeleteRule = async (ruleId) => {
    if (!confirm('Are you sure you want to delete this monitoring rule?')) return;
    try {
      await api.delete(`/expected-rules/${ruleId}`);
      fetchData();
    } catch (err) {
      console.error('Failed to delete rule:', err);
    }
  };

  const openSummary = async (emailId, subject) => {
    try {
      const res = await api.get(`/summary/${emailId}`);
      setSelectedSummary(res.data);
      setSelectedSubject(subject);
    } catch (err) {
      console.error('Failed to fetch summary:', err);
    }
  };

  return (
    <div className="p-6 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <Target className="w-6 h-6 text-emerald-400" />
            Expected Emails Monitor
          </h2>
          <p className="text-xs text-slate-400 mt-1">Never miss important interview calls, offer letters, or key sender emails</p>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="px-4 py-2 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white flex items-center gap-2 shadow-lg shadow-emerald-600/20 transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          {showAddForm ? 'Cancel' : 'Create Monitoring Rule'}
        </button>
      </div>

      {/* Add Rule Form */}
      {showAddForm && (
        <form onSubmit={handleAddRule} className="glass-panel p-6 rounded-2xl border border-emerald-500/30 space-y-4 glow-emerald">
          <h3 className="text-sm font-bold text-white">Define New Expected Email Rule</h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Rule Criteria</label>
              <select
                value={ruleType}
                onChange={(e) => setRuleType(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
              >
                <option value="SENDER_EMAIL">Sender Email (e.g. hr@company.com)</option>
                <option value="SENDER_DOMAIN">Sender Domain (e.g. amazon.com)</option>
                <option value="SUBJECT_KEYWORD">Subject Keyword (e.g. Interview)</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Target Value</label>
              <input
                type="text"
                value={ruleValue}
                onChange={(e) => setRuleValue(e.target.value)}
                placeholder={ruleType === 'SENDER_EMAIL' ? 'hr@company.com' : ruleType === 'SENDER_DOMAIN' ? 'amazon.com' : 'Interview'}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Optional Note</label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Job application response"
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
              />
            </div>
          </div>
          <button
            type="submit"
            className="px-6 py-2.5 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition-colors"
          >
            Save Rule
          </button>
        </form>
      )}

      {/* Active Rules List */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800">
        <h3 className="text-sm font-bold text-white mb-4">Active Monitoring Rules ({rules.length})</h3>
        {rules.length === 0 ? (
          <p className="text-xs text-slate-500">No monitoring rules defined yet. Create your first rule above!</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {rules.map((rule) => (
              <div key={rule.id} className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    {rule.rule_type}
                  </span>
                  <p className="text-xs font-bold text-white mt-1.5">{rule.rule_value}</p>
                  {rule.description && <p className="text-[10px] text-slate-400">{rule.description}</p>}
                </div>
                <button
                  onClick={() => handleDeleteRule(rule.id)}
                  className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Expected Emails Feed */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800">
        <h3 className="text-sm font-bold text-white mb-4">Matched Expected Emails Feed</h3>
        {expectedEmails.length === 0 ? (
          <p className="text-xs text-slate-500 py-6 text-center">No expected emails detected yet.</p>
        ) : (
          <div className="space-y-3">
            {expectedEmails.map((email) => (
              <div key={email.id} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white">{email.sender}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-semibold">Matched Expected Rule</span>
                  </div>
                  <h4 className="text-sm font-semibold text-slate-200 mt-1">{email.subject || '(No Subject)'}</h4>
                  <p className="text-xs text-slate-400 truncate max-w-xl">{email.snippet}</p>
                </div>
                <button
                  onClick={() => openSummary(email.id, email.subject)}
                  className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 transition-all shrink-0 self-start md:self-auto"
                >
                  <Sparkles className="w-4 h-4 text-cyan-400" />
                  View AI Summary
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <AISummaryModal
        isOpen={!!selectedSummary}
        onClose={() => setSelectedSummary(null)}
        summary={selectedSummary}
        emailSubject={selectedSubject}
      />
    </div>
  );
};

export default ExpectedEmails;
