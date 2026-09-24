'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import type { MarketplaceAccount } from '@/types/api';

const marketplaceConfig = [
  {
    id: 'amazon',
    name: 'Amazon',
    description: 'Sell on Amazon India with SP-API integration',
    gradient: 'from-orange-400 to-orange-600',
    bg: 'bg-orange-50',
    icon: '🛒',
  },
  {
    id: 'flipkart',
    name: 'Flipkart',
    description: 'Connect to Flipkart Seller Hub',
    gradient: 'from-blue-400 to-blue-600',
    bg: 'bg-blue-50',
    icon: '🛍️',
  },
  {
    id: 'meesho',
    name: 'Meesho',
    description: 'Manage your Meesho supplier panel',
    gradient: 'from-pink-400 to-pink-600',
    bg: 'bg-pink-50',
    icon: '📦',
  },
];

export default function MarketplacesPage() {
  const [accounts, setAccounts] = useState<MarketplaceAccount[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [connecting, setConnecting] = useState<string | null>(null);
  const [testing, setTesting] = useState<string | null>(null);
  const [syncing, setSyncing] = useState<string | null>(null);
  const [configModal, setConfigModal] = useState<string | null>(null);
  const [credsForm, setCredsForm] = useState({ app_id: '', app_secret: '', is_live: false });
  const [savingCreds, setSavingCreds] = useState(false);
  const { addToast } = useToast();

  const fetchAccounts = async () => {
    try {
      const data = await api.get<{ items: MarketplaceAccount[] }>('/marketplaces');
      setAccounts(data.items || []);
    } catch {
      // First time — no accounts yet
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { fetchAccounts(); }, []);

  const handleConnect = async (marketplace: string) => {
    setConnecting(marketplace);
    try {
      await api.post('/marketplaces', {
        marketplace,
        account_name: `My ${marketplace.charAt(0).toUpperCase() + marketplace.slice(1)} Account`,
      });
      addToast({ type: 'success', title: `${marketplace.charAt(0).toUpperCase() + marketplace.slice(1)} connected!` });
      fetchAccounts();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Connection failed';
      addToast({ type: 'error', title: msg });
    } finally {
      setConnecting(null);
    }
  };

  const handleDisconnect = async (marketplace: string) => {
    try {
      await api.delete(`/marketplaces/${marketplace}`);
      addToast({ type: 'success', title: `${marketplace.charAt(0).toUpperCase() + marketplace.slice(1)} disconnected` });
      fetchAccounts();
    } catch {
      addToast({ type: 'error', title: 'Disconnect failed' });
    }
  };

  const handleSync = async (marketplace: string) => {
    setSyncing(marketplace);
    try {
      await api.post(`/marketplaces/${marketplace}/sync`, {});
      addToast({ type: 'success', title: `Synced with ${marketplace.charAt(0).toUpperCase() + marketplace.slice(1)}` });
      fetchAccounts();
    } catch {
      addToast({ type: 'error', title: 'Sync failed' });
    } finally {
      setSyncing(null);
    }
  };

  const handleTestConnection = async (marketplace: string) => {
    setTesting(marketplace);
    try {
      const result = await api.post<{ status: string; message: string }>(`/marketplaces/${marketplace}/test-connection`, {});
      addToast({
        type: result.status === 'success' ? 'success' : 'error',
        title: result.message,
      });
    } catch {
      addToast({ type: 'error', title: 'Test connection failed' });
    } finally {
      setTesting(null);
    }
  };

  const handleSaveCredentials = async () => {
    if (!configModal) return;
    setSavingCreds(true);
    try {
      await api.put(`/marketplaces/${configModal}`, {
        credentials: {
          app_id: credsForm.app_id,
          app_secret: credsForm.app_secret,
        },
        config: {
          mode: credsForm.is_live ? 'live' : 'mock',
        },
      });
      addToast({ type: 'success', title: `${configModal.toUpperCase()} API credentials saved!` });
      setConfigModal(null);
      fetchAccounts();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Save failed';
      addToast({ type: 'error', title: msg });
    } finally {
      setSavingCreds(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-24">
        <svg className="animate-spin h-8 w-8 text-indigo-600" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Marketplace Accounts</h1>
        <p className="text-slate-500 mt-1">Connect and manage your seller accounts across multiple marketplaces</p>
      </div>

      {/* Grid */}
      <div className="grid md:grid-cols-3 gap-6">
        {marketplaceConfig.map((mp) => {
          const account = accounts.find((a) => a.marketplace === mp.id);
          const isConnected = account && account.status === 'connected';

          return (
            <div
              key={mp.id}
              className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
            >
              <div>
                <div className={`h-2 bg-gradient-to-r ${mp.gradient}`} />
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-12 h-12 rounded-xl ${mp.bg} flex items-center justify-center text-2xl`}>
                        {mp.icon}
                      </div>
                      <div>
                        <h3 className="font-semibold text-slate-800">{mp.name}</h3>
                        <p className="text-xs text-slate-500">{mp.description}</p>
                      </div>
                    </div>
                  </div>

                  {isConnected ? (
                    <div className="space-y-3">
                      <div className="bg-slate-50 rounded-xl p-3.5 space-y-2 text-xs">
                        <div className="flex justify-between">
                          <span className="text-slate-500">Status</span>
                          <span className="flex items-center gap-1.5 text-emerald-700 font-medium">
                            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
                            Connected &middot; {account?.config?.mode === 'live' ? 'Live API' : 'Sandbox (Mock)'}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">Active Listings</span>
                          <span className="text-slate-700 font-medium">{account?.listing_count || 0}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">Last Synced</span>
                          <span className="text-slate-700 font-medium">
                            {account?.last_sync_at ? new Date(account.last_sync_at).toLocaleDateString('en-IN') : 'Just now'}
                          </span>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-2">
                        <button
                          onClick={() => handleTestConnection(mp.id)}
                          disabled={testing === mp.id}
                          className="py-2 text-xs font-medium text-emerald-700 bg-emerald-50 rounded-xl hover:bg-emerald-100 transition-colors disabled:opacity-50"
                        >
                          {testing === mp.id ? 'Testing...' : 'Test Connection'}
                        </button>
                        <button
                          onClick={() => handleSync(mp.id)}
                          disabled={syncing === mp.id}
                          className="py-2 text-xs font-medium text-indigo-700 bg-indigo-50 rounded-xl hover:bg-indigo-100 transition-colors disabled:opacity-50"
                        >
                          {syncing === mp.id ? 'Syncing...' : 'Sync Stock'}
                        </button>
                      </div>

                      <div className="flex gap-2">
                        <button
                          onClick={() => {
                            setConfigModal(mp.id);
                            setCredsForm({
                              app_id: '',
                              app_secret: '',
                              is_live: account?.config?.mode === 'live',
                            });
                          }}
                          className="flex-1 py-1.5 text-xs font-medium text-slate-600 bg-slate-100 rounded-xl hover:bg-slate-200 transition-colors"
                        >
                          API Credentials
                        </button>
                        <button
                          onClick={() => handleDisconnect(mp.id)}
                          className="py-1.5 px-3 text-xs font-medium text-red-600 bg-red-50 rounded-xl hover:bg-red-100 transition-colors"
                        >
                          Disconnect
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => handleConnect(mp.id)}
                      disabled={connecting === mp.id}
                      className={`w-full py-2.5 text-sm font-medium text-white bg-gradient-to-r ${mp.gradient} rounded-xl hover:opacity-90 transition-all shadow-sm disabled:opacity-50`}
                    >
                      {connecting === mp.id ? 'Connecting...' : 'Connect Account'}
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Credential Modal */}
      {configModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 space-y-5 shadow-2xl">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-slate-900 capitalize">
                {configModal} API Credentials
              </h3>
              <button
                onClick={() => setConfigModal(null)}
                className="text-slate-400 hover:text-slate-600 text-lg font-semibold"
              >
                &times;
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  {configModal === 'amazon' ? 'Seller Central App ID / Client ID' : 'App ID / Client ID'}
                </label>
                <input
                  type="text"
                  placeholder="e.g. amzn1.sp.solution.xxxx"
                  value={credsForm.app_id}
                  onChange={(e) => setCredsForm({ ...credsForm, app_id: e.target.value })}
                  className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  App Secret / Client Secret
                </label>
                <input
                  type="password"
                  placeholder="••••••••••••••••"
                  value={credsForm.app_secret}
                  onChange={(e) => setCredsForm({ ...credsForm, app_secret: e.target.value })}
                  className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none"
                />
              </div>

              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                <div>
                  <p className="text-xs font-semibold text-slate-800">Production Live Mode</p>
                  <p className="text-xs text-slate-500">Toggle off to use verified mock sandbox</p>
                </div>
                <input
                  type="checkbox"
                  checked={credsForm.is_live}
                  onChange={(e) => setCredsForm({ ...credsForm, is_live: e.target.checked })}
                  className="w-4 h-4 text-indigo-600 rounded"
                />
              </div>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => setConfigModal(null)}
                className="flex-1 py-2 text-sm font-medium text-slate-600 bg-slate-100 rounded-xl hover:bg-slate-200 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveCredentials}
                disabled={savingCreds}
                className="flex-1 py-2 text-sm font-medium text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 transition-colors disabled:opacity-50"
              >
                {savingCreds ? 'Saving...' : 'Save & Verify'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
