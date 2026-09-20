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
    try {
      await api.post(`/marketplaces/${marketplace}/sync`, {});
      addToast({ type: 'success', title: `Synced with ${marketplace.charAt(0).toUpperCase() + marketplace.slice(1)}` });
      fetchAccounts();
    } catch {
      addToast({ type: 'error', title: 'Sync failed' });
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
    <div>
      <h1 className="text-2xl font-bold text-slate-800 mb-1">Marketplace Connections</h1>
      <p className="text-sm text-slate-500 mb-6">Connect your seller accounts to publish listings directly</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {marketplaceConfig.map(mp => {
          const account = accounts.find(a => a.marketplace === mp.id);
          const isConnected = account?.status === 'connected';

          return (
            <div key={mp.id} className="bg-white rounded-2xl border border-slate-200 overflow-hidden hover:shadow-md transition-shadow">
              {/* Header gradient */}
              <div className={`h-24 bg-gradient-to-br ${mp.gradient} flex items-center justify-center`}>
                <span className="text-4xl">{mp.icon}</span>
              </div>

              <div className="p-5">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-slate-800">{mp.name}</h3>
                    <p className="text-xs text-slate-500 mt-0.5">{mp.description}</p>
                  </div>
                  {isConnected && (
                    <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-50 text-green-700 text-xs font-medium">
                      <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                      Connected
                    </span>
                  )}
                </div>

                {isConnected ? (
                  <div>
                    <div className="bg-slate-50 rounded-xl p-3 mb-3">
                      <div className="flex justify-between text-xs mb-1.5">
                        <span className="text-slate-500">Account</span>
                        <span className="text-slate-700 font-medium">{account?.account_name || '—'}</span>
                      </div>
                      <div className="flex justify-between text-xs mb-1.5">
                        <span className="text-slate-500">Listings</span>
                        <span className="text-slate-700 font-medium">{account?.listing_count || 0}</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-slate-500">Last Sync</span>
                        <span className="text-slate-700 font-medium">
                          {account?.last_sync_at ? new Date(account.last_sync_at).toLocaleDateString() : 'Never'}
                        </span>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleSync(mp.id)}
                        className="flex-1 py-2 text-xs font-medium text-indigo-700 bg-indigo-50 rounded-xl hover:bg-indigo-100 transition-colors"
                      >
                        Sync Now
                      </button>
                      <button
                        onClick={() => handleDisconnect(mp.id)}
                        className="flex-1 py-2 text-xs font-medium text-red-600 bg-red-50 rounded-xl hover:bg-red-100 transition-colors"
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
          );
        })}
      </div>
    </div>
  );
}
