'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import type { Product } from '@/types/api';

export default function ProductDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { addToast } = useToast();
  const [product, setProduct] = useState<Product | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchProduct() {
      try {
        const data = await api.get<Product>(`/products/${params.id}`);
        setProduct(data);
      } catch {
        addToast({ type: 'error', title: 'Product not found' });
        router.push('/products');
      } finally {
        setIsLoading(false);
      }
    }
    if (params.id) fetchProduct();
  }, [params.id, router, addToast]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <svg className="animate-spin h-8 w-8 text-indigo-600" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      </div>
    );
  }

  if (!product) return null;

  const statusColors: Record<string, string> = {
    draft: 'bg-amber-100 text-amber-700',
    active: 'bg-emerald-100 text-emerald-700',
    archived: 'bg-slate-100 text-slate-600',
  };

  const InfoField = ({ label, value }: { label: string; value: string | number | null | undefined }) => (
    <div>
      <dt className="text-xs font-medium text-slate-400 uppercase tracking-wider">{label}</dt>
      <dd className="text-sm text-slate-700 mt-0.5">{value || <span className="text-slate-300 italic">Not set</span>}</dd>
    </div>
  );

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-2xl font-bold text-slate-800">{product.product_name}</h1>
            <span className={`inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium capitalize ${statusColors[product.status]}`}>
              {product.status}
            </span>
          </div>
          <p className="text-slate-500 font-mono text-sm">SKU: {product.sku}</p>
        </div>
        <div className="flex gap-2">
          <Link
            href={`/products/${product.id}/listing`}
            className="px-4 py-2 text-sm font-medium bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl hover:from-indigo-600 hover:to-purple-700 transition-all"
          >
            Generate Listings
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6">
            <h2 className="text-lg font-semibold text-slate-800 mb-4">Basic Information</h2>
            <dl className="grid grid-cols-2 gap-4">
              <InfoField label="Brand" value={product.brand} />
              <InfoField label="Product Type" value={product.product_type} />
              <InfoField label="Subcategory" value={product.subcategory} />
              <InfoField label="Country of Origin" value={product.country_of_origin} />
            </dl>
            {product.description && (
              <div className="mt-4 pt-4 border-t border-slate-100">
                <dt className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">Description</dt>
                <dd className="text-sm text-slate-700 whitespace-pre-wrap">{product.description}</dd>
              </div>
            )}
            {product.bullet_points && product.bullet_points.length > 0 && (
              <div className="mt-4 pt-4 border-t border-slate-100">
                <dt className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">Bullet Points</dt>
                <ul className="space-y-1">
                  {product.bullet_points.map((bp, i) => (
                    <li key={i} className="text-sm text-slate-700 flex items-start gap-2">
                      <span className="text-indigo-500 mt-0.5">•</span> {bp}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Pricing */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6">
            <h2 className="text-lg font-semibold text-slate-800 mb-4">Pricing & Inventory</h2>
            <dl className="grid grid-cols-4 gap-4">
              <InfoField label="Selling Price" value={product.price ? `₹${Number(product.price).toLocaleString()}` : null} />
              <InfoField label="MRP" value={product.mrp ? `₹${Number(product.mrp).toLocaleString()}` : null} />
              <InfoField label="Cost Price" value={product.cost_price ? `₹${Number(product.cost_price).toLocaleString()}` : null} />
              <InfoField label="Stock" value={product.stock} />
            </dl>
          </div>

          {/* Attributes */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6">
            <h2 className="text-lg font-semibold text-slate-800 mb-4">Attributes</h2>
            <dl className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <InfoField label="Color" value={product.color} />
              <InfoField label="Size" value={product.size} />
              <InfoField label="Material" value={product.material} />
              <InfoField label="Weight" value={product.weight ? `${product.weight} kg` : null} />
            </dl>
          </div>

          {/* Manufacturer */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6">
            <h2 className="text-lg font-semibold text-slate-800 mb-4">Manufacturer & Source</h2>
            <dl className="grid grid-cols-2 gap-4">
              <InfoField label="Manufacturer" value={product.manufacturer} />
              <InfoField label="Packer" value={product.packer} />
              <InfoField label="Importer" value={product.importer} />
              <InfoField label="Manufacturer Address" value={product.manufacturer_address} />
            </dl>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Images */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6">
            <h2 className="text-lg font-semibold text-slate-800 mb-4">Images</h2>
            {product.images && product.images.length > 0 ? (
              <div className="grid grid-cols-2 gap-2">
                {product.images.map((img) => (
                  <div key={img.id} className="aspect-square rounded-xl bg-slate-100 overflow-hidden">
                    <img src={img.url} alt={img.filename} className="w-full h-full object-cover" />
                  </div>
                ))}
              </div>
            ) : (
              <div className="aspect-square rounded-xl bg-slate-50 flex flex-col items-center justify-center text-slate-400">
                <svg className="w-10 h-10 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <p className="text-sm">No images uploaded</p>
                <p className="text-xs mt-1">Available in Phase 2</p>
              </div>
            )}
          </div>

          {/* SEO */}
          {(product.keywords?.length || product.tags?.length) && (
            <div className="bg-white rounded-2xl border border-slate-200 p-6">
              <h2 className="text-lg font-semibold text-slate-800 mb-4">SEO & Tags</h2>
              {product.keywords && product.keywords.length > 0 && (
                <div className="mb-3">
                  <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">Keywords</p>
                  <div className="flex flex-wrap gap-1.5">
                    {product.keywords.map((kw, i) => (
                      <span key={i} className="px-2 py-0.5 bg-indigo-50 text-indigo-600 rounded-md text-xs font-medium">{kw}</span>
                    ))}
                  </div>
                </div>
              )}
              {product.tags && product.tags.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">Tags</p>
                  <div className="flex flex-wrap gap-1.5">
                    {product.tags.map((tag, i) => (
                      <span key={i} className="px-2 py-0.5 bg-slate-100 text-slate-600 rounded-md text-xs font-medium">{tag}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Listing Status */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6">
            <h2 className="text-lg font-semibold text-slate-800 mb-4">Listings</h2>
            <div className="space-y-3">
              {['amazon', 'flipkart', 'meesho'].map((mp) => (
                <div key={mp} className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                  <span className="text-sm font-medium text-slate-700 capitalize">{mp}</span>
                  <span className="text-xs text-slate-400 px-2 py-1 bg-white rounded-lg border border-slate-200">No listing</span>
                </div>
              ))}
            </div>
          </div>

          {/* Meta */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 text-xs text-slate-400 space-y-1">
            <p>Created: {new Date(product.created_at).toLocaleString()}</p>
            <p>Updated: {new Date(product.updated_at).toLocaleString()}</p>
            <p className="font-mono">ID: {product.id}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
