'use client';

import { useEffect, useState, useCallback } from 'react';
import { api } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';

interface AuditLogEntry {
  id: string;
  action: string;
  entity_type: string;
  entity_id: string | null;
  old_value: Record<string, unknown> | null;
  new_value: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

const actionBadges: Record<string, string> = {
  product_created: 'bg-blue-100 text-blue-700',
  product_updated: 'bg-amber-100 text-amber-700',
  product_deleted: 'bg-red-100 text-red-700',
  listing_generated: 'bg-purple-100 text-purple-700',
  listing_updated: 'bg-slate-100 text-slate-700',
  listing_approved: 'bg-green-100 text-green-700',
  listing_published: 'bg-emerald-100 text-emerald-700',
  listing_publish_failed: 'bg-red-100 text-red-700',
  marketplace_connected: 'bg-indigo-100 text-indigo-700',
  marketplace_disconnected: 'bg-slate-100 text-slate-700',
};

export default function AuditPage() {
  const { addToast } = useToast();
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState('');
  const [entityFilter, setEntityFilter] = useState('');
  const [availableActions, setAvailableActions] = useState<string[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const fetchLogs = useCallback(async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams({ page: page.toString(), page_size: '30' });
      if (actionFilter) params.set('action', actionFilter);
      if (entityFilter) params.set('entity_type', entityFilter);

      const data = await api.get<{
        items: AuditLogEntry[];
        total: number;
        total_pages: number;
      }>(`/audit-logs?${params.toString()}`);

      setLogs(data.items || []);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch {
      addToast({ type: 'error', title: 'Failed to load audit logs' });
    } finally {
      setIsLoading(false);
    }
  }, [page, actionFilter, entityFilter, addToast]);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  useEffect(() => {
    (async () => {
      try {
        const data = await api.get<{ actions: string[] }>('/audit-logs/actions');
        setAvailableActions(data.actions || []);
      } catch {
        // Ignore
      }
    })();
  }, []);

  function formatDate(dateStr: string): string {
    const d = new Date(dateStr);
    return d.toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Audit Logs</h1>
        <p className="text-slate-500 mt-1">Track all actions performed in your account</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 items-center">
        <select
          value={actionFilter}
          onChange={(e) => { setActionFilter(e.target.value); setPage(1); }}
          className="px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
        >
          <option value="">All Actions</option>
          {availableActions.map((a) => (
            <option key={a} value={a}>
              {a.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
            </option>
          ))}
        </select>

        <select
          value={entityFilter}
          onChange={(e) => { setEntityFilter(e.target.value); setPage(1); }}
          className="px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white"
        >
          <option value="">All Entities</option>
          <option value="product">Product</option>
          <option value="listing">Listing</option>
          <option value="marketplace">Marketplace</option>
          <option value="business_profile">Business Profile</option>
        </select>

        <span className="text-sm text-slate-500 ml-auto">{total} total entries</span>
      </div>

      {/* Logs Table */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : logs.length === 0 ? (
        <div className="text-center py-20 bg-slate-50 rounded-2xl border border-slate-200">
          <svg className="w-16 h-16 mx-auto text-slate-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <h3 className="text-lg font-semibold text-slate-700">No audit logs yet</h3>
          <p className="text-sm text-slate-500 mt-1">Actions will appear here as you use the platform</p>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 uppercase tracking-wider">Time</th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 uppercase tracking-wider">Action</th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 uppercase tracking-wider">Entity</th>
                  <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 uppercase tracking-wider">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {logs.map((log) => (
                  <tr
                    key={log.id}
                    className="hover:bg-slate-50/50 transition-colors cursor-pointer"
                    onClick={() => setExpandedId(expandedId === log.id ? null : log.id)}
                  >
                    <td className="px-5 py-3.5 text-sm text-slate-600 whitespace-nowrap">
                      {log.created_at ? formatDate(log.created_at) : '—'}
                    </td>
                    <td className="px-5 py-3.5">
                      <span className={`inline-block px-2.5 py-1 text-xs font-medium rounded-full ${actionBadges[log.action] || 'bg-slate-100 text-slate-600'}`}>
                        {log.action.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-sm text-slate-600">
                      <span className="capitalize">{log.entity_type}</span>
                      {log.entity_id && (
                        <span className="ml-1 text-xs text-slate-400 font-mono">
                          {log.entity_id.slice(0, 8)}...
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-3.5 text-sm text-slate-500">
                      {log.new_value && typeof log.new_value === 'object' ? (
                        <span className="text-xs">
                          {Object.entries(log.new_value).slice(0, 2).map(([k, v]) => `${k}: ${v}`).join(', ')}
                        </span>
                      ) : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Expanded detail */}
          {expandedId && (() => {
            const log = logs.find((l) => l.id === expandedId);
            if (!log) return null;
            return (
              <div className="border-t border-slate-200 bg-slate-50 p-5">
                <div className="grid md:grid-cols-2 gap-4">
                  {log.old_value && (
                    <div>
                      <h4 className="text-xs font-medium text-slate-500 uppercase mb-2">Previous Value</h4>
                      <pre className="text-xs bg-white border border-slate-200 rounded-lg p-3 overflow-auto max-h-32">
                        {JSON.stringify(log.old_value, null, 2)}
                      </pre>
                    </div>
                  )}
                  {log.new_value && (
                    <div>
                      <h4 className="text-xs font-medium text-slate-500 uppercase mb-2">New Value</h4>
                      <pre className="text-xs bg-white border border-slate-200 rounded-lg p-3 overflow-auto max-h-32">
                        {JSON.stringify(log.new_value, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            );
          })()}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-5 py-3 border-t border-slate-200 bg-slate-50">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page <= 1}
                className="px-3 py-1.5 text-sm font-medium bg-white border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-40 transition-colors"
              >
                Previous
              </button>
              <span className="text-sm text-slate-500">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(Math.min(totalPages, page + 1))}
                disabled={page >= totalPages}
                className="px-3 py-1.5 text-sm font-medium bg-white border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-40 transition-colors"
              >
                Next
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
