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
