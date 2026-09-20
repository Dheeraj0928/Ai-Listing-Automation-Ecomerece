'use client';

import { useState } from 'react';
import { useToast } from '@/hooks/use-toast';

export default function AISettingsPage() {
  const { addToast } = useToast();
  const [provider, setProvider] = useState('mock');
  const [openaiKey, setOpenaiKey] = useState('');
  const [geminiKey, setGeminiKey] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    // In production, these would be saved to the backend as env overrides
    // For now, they work through .env configuration
    setTimeout(() => {
      addToast({
        type: 'info',
        title: 'Settings noted',
        message: 'Update your backend .env file with these values and restart the server.',
      });
      setIsSaving(false);
    }, 500);
  };

  const providers = [
    {
      id: 'mock',
      name: 'Mock Provider',
      description: 'Uses simulated AI responses for testing. No API key needed.',
      icon: '🧪',
      badge: 'Free',
      badgeColor: 'bg-slate-100 text-slate-600',
    },
    {
      id: 'openai',
      name: 'OpenAI GPT',
      description: 'GPT-4o for high-quality, creative product descriptions.',
      icon: '🤖',
      badge: 'Premium',
      badgeColor: 'bg-emerald-100 text-emerald-700',
    },
    {
      id: 'gemini',
      name: 'Google Gemini',
      description: 'Gemini Pro for fast, cost-effective AI generation.',
      icon: '✨',
      badge: 'Premium',
      badgeColor: 'bg-blue-100 text-blue-700',
    },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-800 mb-1">AI Settings</h1>
      <p className="text-sm text-slate-500 mb-6">Configure your AI provider for listing generation</p>

      {/* Provider Selection */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 mb-6">
        <h2 className="text-sm font-semibold text-slate-700 mb-4">Default AI Provider</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {providers.map(p => (
            <button
              key={p.id}
              onClick={() => setProvider(p.id)}
              className={`relative p-5 rounded-2xl border-2 text-left transition-all duration-200 ${
                provider === p.id
                  ? 'border-indigo-500 bg-indigo-50/50 shadow-sm'
                  : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <span className="text-2xl">{p.icon}</span>
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${p.badgeColor}`}>{p.badge}</span>
              </div>
              <h3 className="font-semibold text-slate-800">{p.name}</h3>
              <p className="text-xs text-slate-500 mt-1">{p.description}</p>
              {provider === p.id && (
                <div className="absolute top-3 left-3 w-5 h-5 rounded-full bg-indigo-500 flex items-center justify-center">
                  <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* API Keys */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 mb-6">
        <h2 className="text-sm font-semibold text-slate-700 mb-4">API Keys</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm text-slate-600 mb-1">OpenAI API Key</label>
            <div className="relative">
              <input
                type="password"
                value={openaiKey}
                onChange={(e) => setOpenaiKey(e.target.value)}
                placeholder="sk-..."
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none pr-20"
              />
              <span className="absolute right-3 top-2.5 text-xs text-slate-400">OPENAI_API_KEY</span>
            </div>
            <p className="text-xs text-slate-400 mt-1">Get your key from <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-indigo-500 hover:underline">platform.openai.com</a></p>
          </div>

          <div>
            <label className="block text-sm text-slate-600 mb-1">Google AI API Key</label>
            <div className="relative">
              <input
                type="password"
                value={geminiKey}
                onChange={(e) => setGeminiKey(e.target.value)}
                placeholder="AI..."
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none pr-28"
              />
              <span className="absolute right-3 top-2.5 text-xs text-slate-400">GOOGLE_AI_API_KEY</span>
            </div>
            <p className="text-xs text-slate-400 mt-1">Get your key from <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener noreferrer" className="text-indigo-500 hover:underline">aistudio.google.com</a></p>
          </div>
        </div>
      </div>

      {/* Info card */}
      <div className="bg-indigo-50 rounded-2xl border border-indigo-100 p-6 mb-6">
        <h3 className="text-sm font-semibold text-indigo-800 mb-2">How AI Generation Works</h3>
        <ul className="text-xs text-indigo-700 space-y-1.5">
          <li className="flex items-start gap-2">
            <span className="mt-0.5">1.</span>
            <span>Product data + seller memory are combined into an optimized prompt</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-0.5">2.</span>
            <span>The AI generates marketplace-specific titles, descriptions, bullet points &amp; search terms</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-0.5">3.</span>
            <span>Output is validated against marketplace rules before publishing</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-0.5">4.</span>
            <span>You review, edit if needed, then approve &amp; publish</span>
          </li>
        </ul>
      </div>

      {/* Save */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="px-6 py-2.5 text-sm font-medium text-white bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl hover:from-indigo-400 hover:to-purple-500 transition-all shadow-sm disabled:opacity-50"
        >
          {isSaving ? 'Saving...' : 'Save Settings'}
        </button>
      </div>
    </div>
  );
}
