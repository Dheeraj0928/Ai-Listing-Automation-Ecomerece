'use client';

import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import type { MarketplaceListing, ListingListResponse } from '@/types/api';

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

const marketplaceColors: Record<string, string> = {
  amazon: 'bg-orange-100 text-orange-700',
  flipkart: 'bg-blue-100 text-blue-700',
  meesho: 'bg-pink-100 text-pink-700',
};

export default function ListingsPage() {
  const [listings, setListings] = useState<MarketplaceListing[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [marketplaceFilter, setMarketplaceFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const { addToast } = useToast();
  const pageSize = 20;

  const fetchListings = useCallback(async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams({ page: page.toString(), page_size: pageSize.toString() });
      if (marketplaceFilter) params.set('marketplace', marketplaceFilter);
      if (statusFilter) params.set('status', statusFilter);

      const data = await api.get<ListingListResponse>(`/listings?${params}`);
      setListings(data.items);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch {
      addToast({ type: 'error', title: 'Failed to load listings' });
    } finally {
      setIsLoading(false);
    }
  }, [page, marketplaceFilter, statusFilter, addToast]);

  useEffect(() => { fetchListings(); }, [fetchListings]);

  const handleValidate = async (id: string) => {
    try {
      await api.post(`/listings/${id}/validate`, {});
      addToast({ type: 'success', title: 'Listing validated' });
      fetchListings();
    } catch {
      addToast({ type: 'error', title: 'Validation failed' });
    }
  };

  const handlePublish = async (id: string) => {
    try {
      await api.post(`/listings/${id}/publish`, {});
      addToast({ type: 'success', title: 'Listing published!' });
      fetchListings();
    } catch {
      addToast({ type: 'error', title: 'Publish failed' });
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Marketplace Listings</h1>
          <p className="text-sm text-slate-500 mt-1">{total} total listings</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3 mb-6">
        <select
          value={marketplaceFilter}
          onChange={(e) => { setMarketplaceFilter(e.target.value); setPage(1); }}
          className="px-3 py-2 rounded-xl border border-slate-200 text-sm bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
        >
          <option value="">All Marketplaces</option>
          <option value="amazon">Amazon</option>
          <option value="flipkart">Flipkart</option>
          <option value="meesho">Meesho</option>
        </select>

        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
          className="px-3 py-2 rounded-xl border border-slate-200 text-sm bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
        >
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="ai_generated">AI Generated</option>
          <option value="validated">Validated</option>
          <option value="needs_review">Needs Review</option>
          <option value="approved">Approved</option>
          <option value="published">Published</option>
          <option value="error">Error</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-100">
              <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Title</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Marketplace</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Completion</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Version</th>
              <th className="text-right px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {isLoading ? (
              <tr><td colSpan={6} className="px-5 py-12 text-center text-slate-400 text-sm">Loading...</td></tr>
            ) : listings.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-5 py-12 text-center">
                  <div className="text-slate-400">
                    <svg className="w-12 h-12 mx-auto mb-3 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    <p className="font-medium">No listings yet</p>
                    <p className="text-sm mt-1">Generate listings from a product page</p>
                  </div>
                </td>
              </tr>
            ) : (
              listings.map((listing) => {
                const title = (listing.listing_data as Record<string, unknown>)?.title as string || 'Untitled';
                return (
                  <tr key={listing.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-5 py-3">
                      <Link href={`/listings/${listing.id}`} className="text-sm font-medium text-slate-700 hover:text-indigo-600 transition-colors">
                        {title.length > 60 ? title.slice(0, 60) + '...' : title}
                      </Link>
                    </td>
                    <td className="px-5 py-3">
                      <span className={`px-2.5 py-1 rounded-lg text-xs font-medium ${marketplaceColors[listing.marketplace] || 'bg-slate-100'}`}>
                        {listing.marketplace.charAt(0).toUpperCase() + listing.marketplace.slice(1)}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      <span className={`px-2.5 py-1 rounded-lg text-xs font-medium ${statusColors[listing.status] || 'bg-slate-100'}`}>
                        {listing.status.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      {listing.completion_percentage != null ? (
                        <div className="flex items-center gap-2">
                          <div className="w-20 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-indigo-500 rounded-full transition-all"
                              style={{ width: `${listing.completion_percentage}%` }}
                            />
                          </div>
                          <span className="text-xs text-slate-500">{listing.completion_percentage}%</span>
                        </div>
                      ) : (
                        <span className="text-xs text-slate-400">—</span>
                      )}
                    </td>
                    <td className="px-5 py-3 text-sm text-slate-500">v{listing.version}</td>
                    <td className="px-5 py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        {(listing.status === 'ai_generated' || listing.status === 'needs_review') && (
                          <button
                            onClick={() => handleValidate(listing.id)}
                            className="px-3 py-1.5 text-xs font-medium text-amber-700 bg-amber-50 rounded-lg hover:bg-amber-100 transition-colors"
                          >
                            Validate
                          </button>
                        )}
                        {(listing.status === 'validated' || listing.status === 'approved') && (
                          <button
                            onClick={() => handlePublish(listing.id)}
                            className="px-3 py-1.5 text-xs font-medium text-green-700 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
                          >
                            Publish
                          </button>
                        )}
                        <Link
                          href={`/listings/${listing.id}`}
                          className="px-3 py-1.5 text-xs font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                        >
                          View
                        </Link>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-sm text-slate-500">Page {page} of {totalPages}</p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 text-sm rounded-xl border border-slate-200 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="px-4 py-2 text-sm rounded-xl border border-slate-200 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
