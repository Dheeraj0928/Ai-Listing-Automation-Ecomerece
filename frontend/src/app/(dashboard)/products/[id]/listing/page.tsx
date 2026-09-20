'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import type { Product, MarketplaceListing } from '@/types/api';

export default function ProductListingPage() {
  const params = useParams();
  const router = useRouter();
  const { addToast } = useToast();
  const productId = params.id as string;

  const [product, setProduct] = useState<Product | null>(null);
  const [existingListings, setExistingListings] = useState<MarketplaceListing[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedMarketplaces, setSelectedMarketplaces] = useState<string[]>([]);
  const [tone, setTone] = useState('professional');
  const [provider, setProvider] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const [prod, listings] = await Promise.all([
          api.get<Product>(`/products/${productId}`),
          api.get<{ items: MarketplaceListing[] }>(`/listings?product_id=${productId}`),
        ]);
        setProduct(prod);
        setExistingListings(listings.items || []);
      } catch {
        addToast({ type: 'error', title: 'Product not found' });
        router.push('/products');
      } finally {
        setIsLoading(false);
      }
    })();
  }, [productId, addToast, router]);

  const toggleMarketplace = (mp: string) => {
    setSelectedMarketplaces(prev =>
      prev.includes(mp) ? prev.filter(m => m !== mp) : [...prev, mp]
    );
  };

  const handleGenerate = async () => {
    if (selectedMarketplaces.length === 0) {
      addToast({ type: 'warning', title: 'Select at least one marketplace' });
      return;
    }

    setIsGenerating(true);
    try {
      const result = await api.post<{ data: MarketplaceListing[] }>('/listings/generate', {
        product_id: productId,
        marketplaces: selectedMarketplaces,
        tone,
        provider: provider || undefined,
      });
      const newListings = result.data || [];
      addToast({ type: 'success', title: `Generated ${newListings.length} listing(s)!` });

      // Refresh existing listings
      const updated = await api.get<{ items: MarketplaceListing[] }>(`/listings?product_id=${productId}`);
      setExistingListings(updated.items || []);
      setSelectedMarketplaces([]);
    } catch {
      addToast({ type: 'error', title: 'Generation failed. Check AI provider settings.' });
    } finally {
      setIsGenerating(false);
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

  if (!product) return null;

  const marketplaces = [
    { id: 'amazon', name: 'Amazon', color: 'from-orange-400 to-orange-600', icon: '🛒' },
    { id: 'flipkart', name: 'Flipkart', color: 'from-blue-400 to-blue-600', icon: '🛍️' },
    { id: 'meesho', name: 'Meesho', color: 'from-pink-400 to-pink-600', icon: '📦' },
  ];

  return (
    <div>
      <Link href={`/products/${productId}`} className="text-sm text-indigo-600 hover:text-indigo-700 mb-2 inline-block">&larr; Back to Product</Link>
      <h1 className="text-2xl font-bold text-slate-800 mb-1">Generate Listings</h1>
      <p className="text-sm text-slate-500 mb-6">Product: {product.product_name} ({product.sku})</p>

      {/* Marketplace selection */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 mb-6">
        <h2 className="text-sm font-semibold text-slate-700 mb-4">Select Marketplaces</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {marketplaces.map(mp => {
            const isSelected = selectedMarketplaces.includes(mp.id);
            const hasExisting = existingListings.some(l => l.marketplace === mp.id);
            return (
              <button
                key={mp.id}
                onClick={() => toggleMarketplace(mp.id)}
                className={`relative p-5 rounded-2xl border-2 text-left transition-all duration-200 ${
                  isSelected
                    ? 'border-indigo-500 bg-indigo-50/50 shadow-sm'
                    : 'border-slate-200 hover:border-slate-300 bg-white'
                }`}
              >
                <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${mp.color} flex items-center justify-center text-xl mb-3`}>
                  {mp.icon}
                </div>
                <p className="font-semibold text-slate-800">{mp.name}</p>
                {hasExisting && (
                  <p className="text-xs text-amber-600 mt-1">Existing listing will be updated</p>
                )}
                {isSelected && (
                  <div className="absolute top-3 right-3 w-6 h-6 rounded-full bg-indigo-500 flex items-center justify-center">
                    <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Options */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 mb-6">
        <h2 className="text-sm font-semibold text-slate-700 mb-4">Generation Options</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-slate-600 mb-1">Tone</label>
            <select
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
            >
              <option value="professional">Professional</option>
              <option value="casual">Casual</option>
              <option value="luxury">Luxury</option>
              <option value="technical">Technical</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-slate-600 mb-1">AI Provider (optional)</label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
            >
              <option value="">Default (from settings)</option>
              <option value="openai">OpenAI GPT</option>
              <option value="gemini">Google Gemini</option>
              <option value="mock">Mock (testing)</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={isGenerating || selectedMarketplaces.length === 0}
          className="mt-5 w-full py-3 text-sm font-semibold text-white bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl hover:from-indigo-400 hover:to-purple-500 transition-all shadow-lg shadow-indigo-500/25 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isGenerating ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Generating with AI...
            </span>
          ) : (
            `Generate ${selectedMarketplaces.length} Listing(s)`
          )}
        </button>
      </div>

      {/* Existing listings */}
      {existingListings.length > 0 && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">Existing Listings</h2>
          <div className="space-y-3">
            {existingListings.map(listing => (
              <Link
                key={listing.id}
                href={`/listings/${listing.id}`}
                className="flex items-center justify-between p-4 rounded-xl border border-slate-100 hover:bg-slate-50 transition-colors"
              >
                <div>
                  <p className="text-sm font-medium text-slate-700">
                    {listing.marketplace.charAt(0).toUpperCase() + listing.marketplace.slice(1)}
                  </p>
                  <p className="text-xs text-slate-400 mt-0.5">v{listing.version} &middot; {listing.status.replace(/_/g, ' ')}</p>
                </div>
                <span className="text-xs text-indigo-600 font-medium">Edit &rarr;</span>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
