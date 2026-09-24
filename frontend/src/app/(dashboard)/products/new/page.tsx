'use client';

import { useState, type FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import type { Product } from '@/types/api';

export default function NewProductPage() {
  const router = useRouter();
  const { addToast } = useToast();
  const [isLoading, setIsLoading] = useState(false);

  // Smart Reference Import State
  const [importTab, setImportTab] = useState<'none' | 'url' | 'keyword'>('none');
  const [importUrl, setImportUrl] = useState('');
  const [importKeyword, setImportKeyword] = useState('');
  const [isFetchingImport, setIsFetchingImport] = useState(false);
  const [keywordSuggestions, setKeywordSuggestions] = useState<Array<{
    title?: string;
    brand?: string;
    suggested_category?: string;
    description?: string;
    key_features?: string[];
    suggested_price?: number;
    attributes?: Record<string, string>;
    keywords?: string[];
    search_terms?: string[];
  }>>([]);

  const [form, setForm] = useState({
    sku: '',
    product_name: '',
    brand: '',
    subcategory: '',
    product_type: '',
    description: '',
    short_description: '',
    bullet_points: ['', '', '', '', ''],
    price: '',
    mrp: '',
    cost_price: '',
    stock: '0',
    color: '',
    size: '',
    material: '',
    weight: '',
    country_of_origin: 'India',
    manufacturer: '',
    manufacturer_address: '',
    packer: '',
    importer: '',
    keywords: '',
    search_terms: '',
    tags: '',
  });

  const updateField = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const updateBulletPoint = (index: number, value: string) => {
    setForm((prev) => {
      const bullets = [...prev.bullet_points];
      bullets[index] = value;
      return { ...prev, bullet_points: bullets };
    });
  };

  const handleUrlImport = async () => {
    if (!importUrl) {
      addToast({ type: 'warning', title: 'Enter a product URL first' });
      return;
    }
    setIsFetchingImport(true);
    try {
      const res = await api.post<{
        status: string;
        product: Product;
        extracted_attributes?: Record<string, unknown>;
      }>('/reference-import/from-url', {
        url: importUrl,
        marketplace: 'amazon',
        tone: 'professional',
      });
      addToast({
        type: 'success',
        title: 'Product Imported Successfully!',
        message: res.product.product_name,
      });
      router.push(`/products/${res.product.id}`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'URL import failed';
      addToast({ type: 'error', title: msg });
    } finally {
      setIsFetchingImport(false);
    }
  };

  const handleKeywordSearch = async () => {
    if (!importKeyword) {
      addToast({ type: 'warning', title: 'Enter a keyword first' });
      return;
    }
    setIsFetchingImport(true);
    try {
      const res = await api.post<{
        status: string;
        suggestions: Array<{
          title?: string;
          brand?: string;
          suggested_category?: string;
          description?: string;
          key_features?: string[];
          suggested_price?: number;
          attributes?: Record<string, string>;
          keywords?: string[];
          search_terms?: string[];
        }>;
      }>('/reference-import/from-keyword', {
        keyword: importKeyword,
        marketplace: 'amazon',
        tone: 'professional',
      });
      setKeywordSuggestions(res.suggestions || []);
      if (!res.suggestions || res.suggestions.length === 0) {
        addToast({ type: 'info', title: 'No suggestions generated' });
      } else {
        addToast({ type: 'success', title: `${res.suggestions.length} AI suggestions found!` });
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Keyword search failed';
      addToast({ type: 'error', title: msg });
    } finally {
      setIsFetchingImport(false);
    }
  };

  const applySuggestion = (sug: {
    title?: string;
    brand?: string;
    suggested_category?: string;
    description?: string;
    key_features?: string[];
    suggested_price?: number;
    attributes?: Record<string, string>;
    keywords?: string[];
    search_terms?: string[];
  }) => {
    setForm((prev) => ({
      ...prev,
      sku: `PROD-${Math.floor(1000 + Math.random() * 9000)}`,
      product_name: sug.title || prev.product_name,
      brand: sug.brand || prev.brand,
      subcategory: sug.suggested_category || prev.subcategory,
      description: sug.description || prev.description,
      bullet_points: (sug.key_features && sug.key_features.length >= 5)
        ? sug.key_features.slice(0, 5)
        : [...(sug.key_features || []), ...prev.bullet_points].slice(0, 5),
      price: sug.suggested_price ? String(sug.suggested_price) : prev.price,
      mrp: sug.suggested_price ? String(Math.round(sug.suggested_price * 1.4)) : prev.mrp,
      color: sug.attributes?.color || prev.color,
      material: sug.attributes?.material || prev.material,
      keywords: Array.isArray(sug.keywords) ? sug.keywords.join(', ') : prev.keywords,
      search_terms: Array.isArray(sug.search_terms) ? sug.search_terms.join(', ') : prev.search_terms,
    }));
    addToast({ type: 'success', title: 'Form auto-filled from AI suggestion!' });
    setImportTab('none');
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const payload: Record<string, unknown> = {
        sku: form.sku,
        product_name: form.product_name,
        stock: parseInt(form.stock) || 0,
        status: 'draft',
      };

      // Only include non-empty fields
      if (form.brand) payload.brand = form.brand;
      if (form.subcategory) payload.subcategory = form.subcategory;
      if (form.product_type) payload.product_type = form.product_type;
      if (form.description) payload.description = form.description;
      if (form.short_description) payload.short_description = form.short_description;
      if (form.price) payload.price = parseFloat(form.price);
      if (form.mrp) payload.mrp = parseFloat(form.mrp);
      if (form.cost_price) payload.cost_price = parseFloat(form.cost_price);
      if (form.color) payload.color = form.color;
      if (form.size) payload.size = form.size;
      if (form.material) payload.material = form.material;
      if (form.weight) payload.weight = parseFloat(form.weight);
      if (form.country_of_origin) payload.country_of_origin = form.country_of_origin;
      if (form.manufacturer) payload.manufacturer = form.manufacturer;
      if (form.manufacturer_address) payload.manufacturer_address = form.manufacturer_address;
      if (form.packer) payload.packer = form.packer;
      if (form.importer) payload.importer = form.importer;

      const bullets = form.bullet_points.filter((b) => b.trim());
      if (bullets.length > 0) payload.bullet_points = bullets;

      if (form.keywords) payload.keywords = form.keywords.split(',').map((k) => k.trim()).filter(Boolean);
      if (form.search_terms) payload.search_terms = form.search_terms.split(',').map((k) => k.trim()).filter(Boolean);
      if (form.tags) payload.tags = form.tags.split(',').map((k) => k.trim()).filter(Boolean);

      const product = await api.post<Product>('/products', payload);
      addToast({ type: 'success', title: 'Product Created!', message: product.product_name });
      router.push(`/products/${product.id}`);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to create product';
      addToast({ type: 'error', title: 'Error', message });
    } finally {
      setIsLoading(false);
    }
  };

  const inputClass = "w-full px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-sm";
  const labelClass = "block text-sm font-medium text-slate-600 mb-1.5";

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Add New Product</h1>
          <p className="text-slate-500 mt-1">Create a product in your master catalog</p>
        </div>
        <button
          onClick={() => router.back()}
          className="px-4 py-2 text-sm text-slate-600 hover:text-slate-800 border border-slate-200 rounded-xl hover:bg-slate-50 transition-all"
        >
          Cancel
        </button>
      </div>

      {/* Smart Reference Import Card */}
      <div className="bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50 border border-indigo-100 rounded-2xl p-6 space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-indigo-600 text-white flex items-center justify-center shadow-md shadow-indigo-500/20">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">Smart Reference Import</h2>
              <p className="text-xs text-slate-500">Auto-fill this entire form using a competitor link or product keyword</p>
            </div>
          </div>

          <div className="flex gap-1.5 bg-white/80 p-1 rounded-xl border border-indigo-100/60 shadow-sm">
            <button
              type="button"
              onClick={() => setImportTab(importTab === 'keyword' ? 'none' : 'keyword')}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                importTab === 'keyword' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              By Keyword
            </button>
            <button
              type="button"
              onClick={() => setImportTab(importTab === 'url' ? 'none' : 'url')}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                importTab === 'url' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              By URL
            </button>
          </div>
        </div>

        {/* URL Import Tab */}
        {importTab === 'url' && (
          <div className="pt-2 space-y-3">
            <div className="flex gap-2">
              <input
                type="url"
                value={importUrl}
                onChange={(e) => setImportUrl(e.target.value)}
                placeholder="Paste Amazon, Flipkart, or Meesho product link..."
                className="flex-1 px-4 py-2.5 bg-white border border-indigo-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
              />
              <button
                type="button"
                onClick={handleUrlImport}
                disabled={isFetchingImport}
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl transition-colors disabled:opacity-50 flex items-center gap-2 shrink-0 shadow-sm"
              >
                {isFetchingImport ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : null}
                {isFetchingImport ? 'Importing...' : 'Auto-Import Product'}
              </button>
            </div>
            <p className="text-xs text-slate-500">
              AI will extract product attributes, generate listings, and create the product automatically.
            </p>
          </div>
        )}

        {/* Keyword Search Tab */}
        {importTab === 'keyword' && (
          <div className="pt-2 space-y-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={importKeyword}
                onChange={(e) => setImportKeyword(e.target.value)}
                placeholder="e.g. Wireless Noise Cancelling Over-Ear Headphones"
                className="flex-1 px-4 py-2.5 bg-white border border-indigo-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
              />
              <button
                type="button"
                onClick={handleKeywordSearch}
                disabled={isFetchingImport}
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl transition-colors disabled:opacity-50 flex items-center gap-2 shrink-0 shadow-sm"
              >
                {isFetchingImport ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : null}
                {isFetchingImport ? 'Searching AI...' : 'Generate Suggestions'}
              </button>
            </div>

            {keywordSuggestions.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2">
                {keywordSuggestions.map((sug, i) => (
                  <div
                    key={i}
                    className="bg-white rounded-xl border border-indigo-100 p-4 space-y-2.5 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between gap-1 mb-1">
                        <span className="text-xs font-semibold px-2 py-0.5 rounded bg-indigo-50 text-indigo-700">
                          {sug.suggested_category || 'General'}
                        </span>
                        {sug.suggested_price && (
                          <span className="text-xs font-bold text-emerald-600">
                            ₹{sug.suggested_price}
                          </span>
                        )}
                      </div>
                      <p className="text-xs font-semibold text-slate-800 line-clamp-2">{sug.title}</p>
                      {sug.description && (
                        <p className="text-xs text-slate-500 line-clamp-2 mt-1">{sug.description}</p>
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={() => applySuggestion(sug)}
                      className="w-full py-1.5 text-xs font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 rounded-lg transition-colors border border-indigo-200"
                    >
                      Auto-Fill Form with this &rarr;
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Basic Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="sku" className={labelClass}>SKU *</label>
              <input id="sku" type="text" required value={form.sku} onChange={(e) => updateField('sku', e.target.value)} className={inputClass} placeholder="e.g. LED-STAR-001" />
            </div>
            <div>
              <label htmlFor="product_name" className={labelClass}>Product Name *</label>
              <input id="product_name" type="text" required value={form.product_name} onChange={(e) => updateField('product_name', e.target.value)} className={inputClass} placeholder="e.g. Red Star LED Light for Bike and Car" />
            </div>
            <div>
              <label htmlFor="brand" className={labelClass}>Brand</label>
              <input id="brand" type="text" value={form.brand} onChange={(e) => updateField('brand', e.target.value)} className={inputClass} placeholder="e.g. RedStar" />
            </div>
            <div>
              <label htmlFor="product_type" className={labelClass}>Product Type</label>
              <input id="product_type" type="text" value={form.product_type} onChange={(e) => updateField('product_type', e.target.value)} className={inputClass} placeholder="e.g. LED Light" />
            </div>
            <div>
              <label htmlFor="subcategory" className={labelClass}>Subcategory</label>
              <input id="subcategory" type="text" value={form.subcategory} onChange={(e) => updateField('subcategory', e.target.value)} className={inputClass} placeholder="e.g. Automotive Lighting" />
            </div>
          </div>

          <div className="mt-4">
            <label htmlFor="description" className={labelClass}>Description</label>
            <textarea id="description" rows={4} value={form.description} onChange={(e) => updateField('description', e.target.value)} className={inputClass} placeholder="Detailed product description..." />
          </div>

          <div className="mt-4">
            <label htmlFor="short_description" className={labelClass}>Short Description</label>
            <textarea id="short_description" rows={2} value={form.short_description} onChange={(e) => updateField('short_description', e.target.value)} className={inputClass} placeholder="Brief one-line description" />
          </div>

          <div className="mt-4">
            <label className={labelClass}>Bullet Points</label>
            <div className="space-y-2">
              {form.bullet_points.map((bp, i) => (
                <input key={i} type="text" value={bp} onChange={(e) => updateBulletPoint(i, e.target.value)} className={inputClass} placeholder={`Bullet point ${i + 1}`} />
              ))}
            </div>
          </div>
        </div>

        {/* Pricing & Inventory */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Pricing & Inventory</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label htmlFor="price" className={labelClass}>Selling Price (₹)</label>
              <input id="price" type="number" step="0.01" min="0" value={form.price} onChange={(e) => updateField('price', e.target.value)} className={inputClass} placeholder="299.00" />
            </div>
            <div>
              <label htmlFor="mrp" className={labelClass}>MRP (₹)</label>
              <input id="mrp" type="number" step="0.01" min="0" value={form.mrp} onChange={(e) => updateField('mrp', e.target.value)} className={inputClass} placeholder="499.00" />
            </div>
            <div>
              <label htmlFor="cost_price" className={labelClass}>Cost Price (₹)</label>
              <input id="cost_price" type="number" step="0.01" min="0" value={form.cost_price} onChange={(e) => updateField('cost_price', e.target.value)} className={inputClass} placeholder="150.00" />
            </div>
            <div>
              <label htmlFor="stock" className={labelClass}>Stock *</label>
              <input id="stock" type="number" min="0" value={form.stock} onChange={(e) => updateField('stock', e.target.value)} className={inputClass} />
            </div>
          </div>
        </div>

        {/* Attributes */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Attributes</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label htmlFor="color" className={labelClass}>Color</label>
              <input id="color" type="text" value={form.color} onChange={(e) => updateField('color', e.target.value)} className={inputClass} placeholder="e.g. Red" />
            </div>
            <div>
              <label htmlFor="size" className={labelClass}>Size</label>
              <input id="size" type="text" value={form.size} onChange={(e) => updateField('size', e.target.value)} className={inputClass} placeholder="e.g. Medium" />
            </div>
            <div>
              <label htmlFor="material" className={labelClass}>Material</label>
              <input id="material" type="text" value={form.material} onChange={(e) => updateField('material', e.target.value)} className={inputClass} placeholder="e.g. ABS Plastic" />
            </div>
            <div>
              <label htmlFor="weight" className={labelClass}>Weight (kg)</label>
              <input id="weight" type="number" step="0.001" min="0" value={form.weight} onChange={(e) => updateField('weight', e.target.value)} className={inputClass} placeholder="0.250" />
            </div>
          </div>
        </div>

        {/* Manufacturer & Source */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Manufacturer & Source</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="manufacturer" className={labelClass}>Manufacturer</label>
              <input id="manufacturer" type="text" value={form.manufacturer} onChange={(e) => updateField('manufacturer', e.target.value)} className={inputClass} placeholder="e.g. ABC Enterprises" />
            </div>
            <div>
              <label htmlFor="country_of_origin" className={labelClass}>Country of Origin</label>
              <input id="country_of_origin" type="text" value={form.country_of_origin} onChange={(e) => updateField('country_of_origin', e.target.value)} className={inputClass} />
            </div>
            <div className="md:col-span-2">
              <label htmlFor="manufacturer_address" className={labelClass}>Manufacturer Address</label>
              <textarea id="manufacturer_address" rows={2} value={form.manufacturer_address} onChange={(e) => updateField('manufacturer_address', e.target.value)} className={inputClass} placeholder="Full manufacturer address" />
            </div>
            <div>
              <label htmlFor="packer" className={labelClass}>Packer</label>
              <input id="packer" type="text" value={form.packer} onChange={(e) => updateField('packer', e.target.value)} className={inputClass} />
            </div>
            <div>
              <label htmlFor="importer" className={labelClass}>Importer</label>
              <input id="importer" type="text" value={form.importer} onChange={(e) => updateField('importer', e.target.value)} className={inputClass} />
            </div>
          </div>
        </div>

        {/* SEO */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">SEO & Search</h2>
          <div className="space-y-4">
            <div>
              <label htmlFor="keywords" className={labelClass}>Keywords <span className="text-slate-400 font-normal">(comma-separated)</span></label>
              <input id="keywords" type="text" value={form.keywords} onChange={(e) => updateField('keywords', e.target.value)} className={inputClass} placeholder="led light, bike light, car light" />
            </div>
            <div>
              <label htmlFor="search_terms" className={labelClass}>Search Terms <span className="text-slate-400 font-normal">(comma-separated)</span></label>
              <input id="search_terms" type="text" value={form.search_terms} onChange={(e) => updateField('search_terms', e.target.value)} className={inputClass} placeholder="led star light, bike accessory" />
            </div>
            <div>
              <label htmlFor="tags" className={labelClass}>Tags <span className="text-slate-400 font-normal">(comma-separated)</span></label>
              <input id="tags" type="text" value={form.tags} onChange={(e) => updateField('tags', e.target.value)} className={inputClass} placeholder="lighting, automotive, accessory" />
            </div>
          </div>
        </div>

        {/* Submit */}
        <div className="flex items-center justify-end gap-3">
          <button type="button" onClick={() => router.back()} className="px-6 py-2.5 text-sm font-medium text-slate-600 border border-slate-200 rounded-xl hover:bg-slate-50 transition-all">
            Cancel
          </button>
          <button
            type="submit"
            disabled={isLoading}
            className="px-6 py-2.5 text-sm font-medium bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl hover:from-indigo-600 hover:to-purple-700 transition-all shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Creating...' : 'Create Product'}
          </button>
        </div>
      </form>
    </div>
  );
}
