'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import type { RecentActivity } from '@/types/api';

const actionIcons: Record<string, string> = {
  product_created: '📦',
  product_updated: '✏️',
  product_deleted: '🗑️',
  listing_generated: '🤖',
  listing_updated: '📝',
  listing_approved: '✅',
  listing_published: '🚀',
  listing_publish_failed: '❌',
  marketplace_connected: '🔗',
  marketplace_disconnected: '🔌',
};

const actionColors: Record<string, string> = {
  product_created: 'bg-blue-100 border-blue-200',
  product_updated: 'bg-amber-50 border-amber-200',
  product_deleted: 'bg-red-50 border-red-200',
  listing_generated: 'bg-purple-50 border-purple-200',
  listing_updated: 'bg-slate-50 border-slate-200',
  listing_approved: 'bg-green-50 border-green-200',
  listing_published: 'bg-emerald-50 border-emerald-200',
  listing_publish_failed: 'bg-red-50 border-red-200',
  marketplace_connected: 'bg-indigo-50 border-indigo-200',
  marketplace_disconnected: 'bg-slate-50 border-slate-200',
};

function formatTimeAgo(dateStr: string): string {
  const now = new Date();
  const date = new Date(dateStr);
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
  return date.toLocaleDateString();
}

export default function ActivityPage() {
  const [activities, setActivities] = useState<RecentActivity[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const data = await api.get<{ recent_activity: RecentActivity[] }>('/dashboard/stats');
        setActivities(data.recent_activity || []);
      } catch {
        // No activity yet
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-800 mb-1">Activity Log</h1>
      <p className="text-sm text-slate-500 mb-6">Track all actions across your account</p>

      {isLoading ? (
        <div className="flex items-center justify-center py-24">
          <svg className="animate-spin h-8 w-8 text-indigo-600" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        </div>
      ) : activities.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center">
          <svg className="w-16 h-16 mx-auto text-slate-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="text-lg font-semibold text-slate-600">No activity yet</h3>
          <p className="text-sm text-slate-400 mt-1">Actions like creating products, generating listings, and publishing will appear here.</p>
        </div>
      ) : (
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-slate-200" />

          <div className="space-y-4">
            {activities.map((activity, i) => {
              const icon = actionIcons[activity.action] || '📋';
              const colorClass = actionColors[activity.action] || 'bg-slate-50 border-slate-200';

              return (
                <div key={activity.id || i} className="relative flex items-start gap-4 pl-2">
                  {/* Timeline dot */}
                  <div className={`relative z-10 w-10 h-10 rounded-xl ${colorClass} border flex items-center justify-center text-lg flex-shrink-0`}>
                    {icon}
                  </div>

                  {/* Content */}
                  <div className="flex-1 bg-white rounded-2xl border border-slate-200 p-4 hover:shadow-sm transition-shadow">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm font-medium text-slate-700">
                          {activity.action.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                        </p>
                        {activity.message && (
                          <p className="text-xs text-slate-500 mt-0.5">{activity.message}</p>
                        )}
                        <div className="flex items-center gap-2 mt-1.5">
                          <span className="text-xs text-slate-400">{activity.entity_type}</span>
                          {activity.entity_id && (
                            <span className="text-xs text-slate-400 font-mono">
                              #{activity.entity_id.slice(0, 8)}
                            </span>
                          )}
                        </div>
                      </div>
                      <span className="text-xs text-slate-400 whitespace-nowrap ml-4">
                        {formatTimeAgo(activity.created_at)}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
