'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import type { MarketplaceListing } from '@/types/api';

const statusColors: Record<string, string> = {
  draft: 'bg-slate-100 text-slate-600',
  ai_generated: 'bg-blue-100 text-blue-700',
  validated: 'bg-emerald-100 text-emerald-700',
  needs_review: 'bg-amber-100 text-amber-700',
  approved: 'bg-indigo-100 text-indigo-700',
  publishing: 'bg-purple-100 text-purple-700',
  published: 'bg-green-100 text-green-700',
  error: 'bg-red-100 text-red-700',
};

export default function ListingDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { addToast } = useToast();
  const [listing, setListing] = useState<MarketplaceListing | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [editData, setEditData] = useState<Record<string, unknown>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'editor' | 'versions'>('editor');
  const [versions, setVersions] = useState<{ id: string; version_number: number; snapshot: Record<string, unknown>; changes: Record<string, unknown> | null; changed_by: string; change_reason: string; created_at: string }[]>([]);
  const [versionsLoading, setVersionsLoading] = useState(false);

  const listingId = params.id as string;

  useEffect(() => {
    (async () => {
      try {
        const data = await api.get<MarketplaceListing>(`/listings/${listingId}`);
        setListing(data);
        setEditData((data.listing_data || {}) as Record<string, unknown>);
      } catch {
        addToast({ type: 'error', title: 'Listing not found' });
        router.push('/listings');
      } finally {
        setIsLoading(false);
      }
    })();
  }, [listingId, addToast, router]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const updated = await api.put<MarketplaceListing>(`/listings/${listingId}`, {
        listing_data: editData,
      });
      setListing(updated);
      addToast({ type: 'success', title: 'Listing saved' });
    } catch {
      addToast({ type: 'error', title: 'Save failed' });
    } finally {
      setIsSaving(false);
    }
  };

  const handleValidate = async () => {
    try {
      const result = await api.post<{ is_valid: boolean; errors: { field: string; message: string }[] }>(
        `/listings/${listingId}/validate`, {}
      );
      addToast({
        type: result.is_valid ? 'success' : 'warning',
        title: result.is_valid ? 'Listing is valid!' : `${result.errors.length} issue(s) found`,
      });
      // Refresh listing
      const updated = await api.get<MarketplaceListing>(`/listings/${listingId}`);
      setListing(updated);
    } catch {
      addToast({ type: 'error', title: 'Validation failed' });
    }
  };

  const handleApprove = async () => {
    try {
      const updated = await api.post<MarketplaceListing>(`/listings/${listingId}/approve`, {});
      setListing(updated);
      addToast({ type: 'success', title: 'Listing approved!' });
    } catch {
      addToast({ type: 'error', title: 'Approve failed' });
    }
  };

  const handlePublish = async () => {
    try {
      await api.post(`/listings/${listingId}/publish`, {});
      const updated = await api.get<MarketplaceListing>(`/listings/${listingId}`);
      setListing(updated);
      addToast({ type: 'success', title: 'Listing published!' });
    } catch {
      addToast({ type: 'error', title: 'Publish failed' });
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

  if (!listing) return null;

  const data = editData;

  return (
    <div>
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <Link href="/listings" className="text-sm text-indigo-600 hover:text-indigo-700 mb-2 inline-block">&larr; Back to Listings</Link>
          <h1 className="text-2xl font-bold text-slate-800">
            {(data.title as string) || 'Untitled Listing'}
          </h1>
          <div className="flex items-center gap-3 mt-2">
            <span className={`px-2.5 py-1 rounded-lg text-xs font-medium ${statusColors[listing.status]}`}>
              {listing.status.replace(/_/g, ' ')}
            </span>
            <span className="text-sm text-slate-500">
              {listing.marketplace.charAt(0).toUpperCase() + listing.marketplace.slice(1)} &middot; v{listing.version}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleValidate}
            className="px-4 py-2 text-sm font-medium text-amber-700 bg-amber-50 rounded-xl hover:bg-amber-100 transition-colors"
          >
            Validate
          </button>
          {listing.status === 'validated' && (
            <button
              onClick={handleApprove}
              className="px-4 py-2 text-sm font-medium text-indigo-700 bg-indigo-50 rounded-xl hover:bg-indigo-100 transition-colors"
            >
              Approve
            </button>
          )}
          {(listing.status === 'approved' || listing.status === 'validated') && (
            <button
              onClick={handlePublish}
              className="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl hover:from-green-400 hover:to-emerald-500 transition-all shadow-sm"
            >
              Publish
            </button>
          )}
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl hover:from-indigo-400 hover:to-purple-500 transition-all shadow-sm disabled:opacity-50"
          >
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-slate-100 p-1 rounded-xl w-fit">
        <button
          onClick={() => setActiveTab('editor')}
          className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
            activeTab === 'editor'
              ? 'bg-white text-slate-900 shadow-sm'
              : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          Editor
        </button>
        <button
          onClick={() => {
            setActiveTab('versions');
            if (versions.length === 0 && !versionsLoading) {
              setVersionsLoading(true);
              api.get<{ data: typeof versions }>(`/listings/${listingId}/versions`)
                .then((res) => setVersions(res.data || []))
                .catch(() => addToast({ type: 'error', title: 'Failed to load versions' }))
                .finally(() => setVersionsLoading(false));
            }
          }}
          className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
            activeTab === 'versions'
              ? 'bg-white text-slate-900 shadow-sm'
              : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          Version History
        </button>
      </div>

      {activeTab === 'editor' && (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main editor */}
        <div className="lg:col-span-2 space-y-5">
          {/* Title */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <label className="block text-sm font-medium text-slate-600 mb-2">Product Title</label>
            <input
              type="text"
              value={(data.title as string) || ''}
              onChange={(e) => setEditData({ ...editData, title: e.target.value })}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
            />
            <p className="text-xs text-slate-400 mt-1">{((data.title as string) || '').length} / 200 characters</p>
          </div>

          {/* Description */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <label className="block text-sm font-medium text-slate-600 mb-2">Description</label>
            <textarea
              value={(data.description as string) || ''}
              onChange={(e) => setEditData({ ...editData, description: e.target.value })}
              rows={6}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none resize-none"
            />
          </div>

          {/* Bullet Points */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <label className="block text-sm font-medium text-slate-600 mb-2">
              {listing.marketplace === 'flipkart' ? 'Key Features' : 'Bullet Points'}
            </label>
            {((data.bullet_points || data.key_features || []) as string[]).map((bp: string, i: number) => (
              <div key={i} className="flex items-start gap-2 mb-2">
                <span className="mt-2.5 text-xs text-slate-400 font-mono w-5">{i + 1}.</span>
                <textarea
                  value={bp}
                  onChange={(e) => {
                    const key = listing.marketplace === 'flipkart' ? 'key_features' : 'bullet_points';
                    const arr = [...((data[key] || []) as string[])];
                    arr[i] = e.target.value;
                    setEditData({ ...editData, [key]: arr });
                  }}
                  rows={2}
                  className="flex-1 px-3 py-2 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none resize-none"
                />
              </div>
            ))}
          </div>

          {/* Search Terms */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <label className="block text-sm font-medium text-slate-600 mb-2">Search Terms / Keywords</label>
            <input
              type="text"
              value={((data.search_terms as string[]) || []).join(', ')}
              onChange={(e) => setEditData({ ...editData, search_terms: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
              placeholder="keyword1, keyword2, keyword3"
            />
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-5">
          {/* Pricing & Attributes */}
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <h3 className="text-sm font-semibold text-slate-700 mb-3">Product Info</h3>
            {[
              { label: 'Brand', key: 'brand' },
              { label: 'Price', key: 'price' },
              { label: 'Color', key: 'color' },
              { label: 'Size', key: 'size' },
              { label: 'Material', key: 'material' },
              { label: 'SKU', key: 'sku' },
            ].map(({ label, key }) => (
              <div key={key} className="mb-3">
                <label className="block text-xs text-slate-500 mb-1">{label}</label>
                <input
                  type="text"
                  value={String(data[key] ?? '')}
                  onChange={(e) => setEditData({ ...editData, [key]: e.target.value })}
                  className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                />
              </div>
            ))}
          </div>

          {/* Validation Results */}
          {listing.validation_results && (
            <div className="bg-white rounded-2xl border border-slate-200 p-5">
              <h3 className="text-sm font-semibold text-slate-700 mb-3">Validation</h3>
              <div className={`px-3 py-2 rounded-lg text-sm font-medium mb-3 ${listing.validation_results.is_valid ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                {listing.validation_results.is_valid ? 'All checks passed' : 'Issues found'}
              </div>
              {listing.validation_results.errors?.map((err, i) => (
                <div key={i} className="flex items-start gap-2 mb-2">
                  <span className="mt-0.5 w-4 h-4 rounded-full bg-red-100 flex items-center justify-center text-red-600 text-xs flex-shrink-0">!</span>
                  <div>
                    <p className="text-xs font-medium text-slate-700">{err.field}</p>
                    <p className="text-xs text-slate-500">{err.message}</p>
                  </div>
                </div>
              ))}
              {listing.validation_results.warnings?.map((w, i) => (
                <div key={i} className="flex items-start gap-2 mb-2">
                  <span className="mt-0.5 w-4 h-4 rounded-full bg-amber-100 flex items-center justify-center text-amber-600 text-xs flex-shrink-0">!</span>
                  <div>
                    <p className="text-xs font-medium text-slate-700">{w.field}</p>
                    <p className="text-xs text-slate-500">{w.message}</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Error */}
          {listing.error_message && (
            <div className="bg-red-50 rounded-2xl border border-red-200 p-5">
              <h3 className="text-sm font-semibold text-red-700 mb-1">Error</h3>
              <p className="text-sm text-red-600">{listing.error_message}</p>
            </div>
          )}
        </div>
      </div>
      )}

      {/* Version History Tab */}
      {activeTab === 'versions' && (
        <div className="space-y-4">
          {versionsLoading ? (
            <div className="flex items-center justify-center py-16">
              <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : versions.length === 0 ? (
            <div className="text-center py-16 bg-slate-50 rounded-2xl border border-slate-200">
              <svg className="w-16 h-16 mx-auto text-slate-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 className="text-lg font-semibold text-slate-700">No version history</h3>
              <p className="text-sm text-slate-500 mt-1">Version snapshots are created each time the listing is updated</p>
            </div>
          ) : (
            versions.map((ver) => (
              <div key={ver.id} className="bg-white rounded-2xl border border-slate-200 p-5">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center text-sm font-bold">
                      v{ver.version_number}
                    </span>
                    <div>
                      <p className="text-sm font-medium text-slate-800">
                        {ver.change_reason || `Version ${ver.version_number}`}
                      </p>
                      <p className="text-xs text-slate-500">
                        {ver.created_at ? new Date(ver.created_at).toLocaleString('en-IN', {
                          day: '2-digit', month: 'short', year: 'numeric',
                          hour: '2-digit', minute: '2-digit',
                        }) : '—'}
                        {ver.changed_by && ` · by ${ver.changed_by}`}
                      </p>
                    </div>
                  </div>
                </div>
                {ver.changes && Object.keys(ver.changes).length > 0 && (
                  <div className="mt-3 space-y-2">
                    <h4 className="text-xs font-medium text-slate-500 uppercase tracking-wider">Changes</h4>
                    <div className="grid gap-2">
                      {Object.entries(ver.changes).map(([field, change]) => (
                        <div key={field} className="bg-slate-50 rounded-lg p-3">
                          <p className="text-xs font-medium text-slate-700 mb-1 capitalize">{field.replace(/_/g, ' ')}</p>
                          <div className="grid grid-cols-2 gap-2">
                            <div>
                              <p className="text-xs text-red-500 font-medium mb-0.5">Before</p>
                              <pre className="text-xs text-slate-600 bg-white p-2 rounded border border-slate-200 overflow-auto max-h-20">
                                {typeof (change as Record<string, unknown>)?.old === 'string'
                                  ? (change as Record<string, unknown>).old as string
                                  : JSON.stringify((change as Record<string, unknown>)?.old, null, 2)}
                              </pre>
                            </div>
                            <div>
                              <p className="text-xs text-green-500 font-medium mb-0.5">After</p>
                              <pre className="text-xs text-slate-600 bg-white p-2 rounded border border-slate-200 overflow-auto max-h-20">
                                {typeof (change as Record<string, unknown>)?.new === 'string'
                                  ? (change as Record<string, unknown>).new as string
                                  : JSON.stringify((change as Record<string, unknown>)?.new, null, 2)}
                              </pre>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {ver.snapshot && (
                  <details className="mt-3">
                    <summary className="text-xs font-medium text-indigo-600 cursor-pointer hover:text-indigo-700">View full snapshot</summary>
                    <pre className="mt-2 text-xs bg-slate-50 border border-slate-200 rounded-lg p-3 overflow-auto max-h-48">
                      {JSON.stringify(ver.snapshot, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
