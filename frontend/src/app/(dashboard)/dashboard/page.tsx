'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import type { DashboardData } from '@/types/api';

function StatCard({ title, value, icon, color }: { title: string; value: number; icon: React.ReactNode; color: string }) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-md transition-shadow duration-200">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <p className="text-3xl font-bold text-slate-800 mt-1">{value}</p>
        </div>
        <div className={`w-11 h-11 rounded-xl ${color} flex items-center justify-center`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

function MarketplaceCard({ name, listings, published, errors }: { name: string; listings: number; published: number; errors: number }) {
  const colors: Record<string, string> = {
    amazon: 'from-orange-400 to-orange-600',
    flipkart: 'from-blue-400 to-blue-600',
    meesho: 'from-pink-400 to-pink-600',
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-md transition-shadow duration-200">
      <div className="flex items-center gap-3 mb-4">
        <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${colors[name] || 'from-slate-400 to-slate-600'} flex items-center justify-center`}>
          <span className="text-white text-sm font-bold uppercase">{name.charAt(0)}</span>
        </div>
        <div>
          <h3 className="font-semibold text-slate-800 capitalize">{name}</h3>
          <p className="text-xs text-slate-400">Marketplace</p>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div className="text-center p-2 bg-slate-50 rounded-xl">
          <p className="text-lg font-bold text-slate-700">{listings}</p>
          <p className="text-xs text-slate-400">Listings</p>
        </div>
        <div className="text-center p-2 bg-emerald-50 rounded-xl">
          <p className="text-lg font-bold text-emerald-600">{published}</p>
          <p className="text-xs text-slate-400">Published</p>
        </div>
        <div className="text-center p-2 bg-red-50 rounded-xl">
          <p className="text-lg font-bold text-red-600">{errors}</p>
          <p className="text-xs text-slate-400">Errors</p>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchDashboard() {
      try {
        const result = await api.get<DashboardData>('/dashboard/stats');
        setData(result);
      } catch (err) {
        console.error('Failed to load dashboard:', err);
        // Use empty data on error
        setData({
          stats: {
            total_products: 0,
            active_listings: 0,
            draft_listings: 0,
            needs_review_listings: 0,
            publishing_errors: 0,
            low_stock_products: 0,
          },
          marketplace_breakdown: [
            { marketplace: 'amazon', products: 0, listings: 0, errors: 0, published: 0 },
            { marketplace: 'flipkart', products: 0, listings: 0, errors: 0, published: 0 },
            { marketplace: 'meesho', products: 0, listings: 0, errors: 0, published: 0 },
          ],
          recent_activity: [],
        });
      } finally {
        setIsLoading(false);
      }
    }
    fetchDashboard();
  }, []);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 bg-slate-200 rounded-lg animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-white rounded-2xl border border-slate-200 p-5 h-24 animate-pulse">
              <div className="h-3 w-20 bg-slate-200 rounded mb-3" />
              <div className="h-6 w-12 bg-slate-200 rounded" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  const stats = data?.stats;
  const marketplaces = data?.marketplace_breakdown || [];
  const activity = data?.recent_activity || [];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
        <p className="text-slate-500 mt-1">Overview of your multi-marketplace operations</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard
          title="Total Products"
          value={stats?.total_products || 0}
          color="bg-indigo-100"
          icon={<svg className="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" /></svg>}
        />
        <StatCard
          title="Active Listings"
          value={stats?.active_listings || 0}
          color="bg-emerald-100"
          icon={<svg className="w-5 h-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
        />
        <StatCard
          title="Draft Listings"
          value={stats?.draft_listings || 0}
          color="bg-amber-100"
          icon={<svg className="w-5 h-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>}
        />
        <StatCard
          title="Needs Review"
          value={stats?.needs_review_listings || 0}
          color="bg-orange-100"
          icon={<svg className="w-5 h-5 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>}
        />
        <StatCard
          title="Errors"
          value={stats?.publishing_errors || 0}
          color="bg-red-100"
          icon={<svg className="w-5 h-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
        />
        <StatCard
          title="Low Stock"
          value={stats?.low_stock_products || 0}
          color="bg-purple-100"
          icon={<svg className="w-5 h-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" /></svg>}
        />
      </div>

      {/* Marketplace Breakdown + Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Marketplaces */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-lg font-semibold text-slate-800">Marketplace Breakdown</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {marketplaces.map((mp) => (
              <MarketplaceCard
                key={mp.marketplace}
                name={mp.marketplace}
                listings={mp.listings}
                published={mp.published}
                errors={mp.errors}
              />
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div>
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Recent Activity</h2>
          <div className="bg-white rounded-2xl border border-slate-200 divide-y divide-slate-100">
            {activity.length === 0 ? (
              <div className="p-6 text-center">
                <p className="text-sm text-slate-400">No recent activity</p>
                <p className="text-xs text-slate-300 mt-1">Start by creating your first product</p>
              </div>
            ) : (
              activity.slice(0, 8).map((item) => (
                <div key={item.id} className="px-4 py-3 hover:bg-slate-50 transition-colors">
                  <p className="text-sm text-slate-700">{item.message}</p>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {new Date(item.created_at).toLocaleString()}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
