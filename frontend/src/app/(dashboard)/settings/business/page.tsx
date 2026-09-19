'use client';

import { useEffect, useState, type FormEvent } from 'react';
import { api } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import type { BusinessProfile } from '@/types/api';

export default function BusinessProfilePage() {
  const { addToast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  const [form, setForm] = useState({
    business_name: '',
    manufacturer_name: '',
    manufacturer_address: '',
    manufacturer_city: '',
    manufacturer_state: '',
    manufacturer_pincode: '',
    country_of_origin: 'India',
    importer_name: '',
    importer_address: '',
    packer_name: '',
    packer_address: '',
    gstin: '',
    business_email: '',
    business_phone: '',
    warehouse_address: '',
    return_address: '',
  });

  const [autoFill, setAutoFill] = useState<Record<string, boolean>>({});

  useEffect(() => {
    async function fetchProfile() {
      try {
        const data = await api.get<BusinessProfile | null>('/business-profile');
        if (data) {
          setForm({
            business_name: data.business_name || '',
            manufacturer_name: data.manufacturer_name || '',
            manufacturer_address: data.manufacturer_address || '',
            manufacturer_city: data.manufacturer_city || '',
            manufacturer_state: data.manufacturer_state || '',
            manufacturer_pincode: data.manufacturer_pincode || '',
            country_of_origin: data.country_of_origin || 'India',
            importer_name: data.importer_name || '',
            importer_address: data.importer_address || '',
            packer_name: data.packer_name || '',
            packer_address: data.packer_address || '',
            gstin: data.gstin || '',
            business_email: data.business_email || '',
            business_phone: data.business_phone || '',
            warehouse_address: data.warehouse_address || '',
            return_address: data.return_address || '',
          });

          // Parse auto-fill config
          if (data.auto_fill_config) {
            const config: Record<string, boolean> = {};
            Object.entries(data.auto_fill_config).forEach(([key, val]) => {
              if (typeof val === 'object' && val !== null && 'auto_fill' in (val as Record<string, unknown>)) {
                config[key] = (val as Record<string, boolean>).auto_fill;
              }
            });
            setAutoFill(config);
          }
        }
      } catch {
        // Profile doesn't exist yet, that's fine
      } finally {
        setIsLoading(false);
      }
    }
    fetchProfile();
  }, []);

  const updateField = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const toggleAutoFill = (field: string) => {
    setAutoFill((prev) => ({ ...prev, [field]: !prev[field] }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await api.put('/business-profile', form);

      // Save auto-fill config
      const autoFillConfig: Record<string, { auto_fill: boolean; scope: string }> = {};
      Object.entries(autoFill).forEach(([key, val]) => {
        if (val) {
          autoFillConfig[key] = { auto_fill: true, scope: 'global' };
        }
      });
      if (Object.keys(autoFillConfig).length > 0) {
        await api.patch('/business-profile/auto-fill', { auto_fill_config: autoFillConfig });
      }

      addToast({ type: 'success', title: 'Profile Saved', message: 'Your business profile has been updated.' });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to save profile';
      addToast({ type: 'error', title: 'Error', message });
    } finally {
      setIsSaving(false);
    }
  };

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

  const inputClass = "w-full px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-sm";
  const labelClass = "block text-sm font-medium text-slate-600 mb-1.5";

  const FieldWithAutoFill = ({ id, label, value, onChange, type = 'text', rows }: {
    id: string; label: string; value: string; onChange: (v: string) => void; type?: string; rows?: number;
  }) => (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <label htmlFor={id} className={labelClass}>{label}</label>
        <label className="flex items-center gap-1.5 cursor-pointer">
          <input
            type="checkbox"
            checked={autoFill[id] || false}
            onChange={() => toggleAutoFill(id)}
            className="w-3.5 h-3.5 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
          />
          <span className="text-xs text-slate-400">Auto-fill</span>
        </label>
      </div>
      {rows ? (
        <textarea id={id} rows={rows} value={value} onChange={(e) => onChange(e.target.value)} className={inputClass} />
      ) : (
        <input id={id} type={type} value={value} onChange={(e) => onChange(e.target.value)} className={inputClass} />
      )}
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Business Profile</h1>
        <p className="text-slate-500 mt-1">These details will be auto-filled in your product listings</p>
      </div>

      <div className="bg-indigo-50 border border-indigo-200 rounded-2xl p-4 flex items-start gap-3">
        <svg className="w-5 h-5 text-indigo-600 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        <div>
          <p className="text-sm font-medium text-indigo-800">Auto-fill enabled fields</p>
          <p className="text-xs text-indigo-600 mt-0.5">Check the &quot;Auto-fill&quot; box next to any field to automatically populate it in future product listings.</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Business Info */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Business Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FieldWithAutoFill id="business_name" label="Business Name" value={form.business_name} onChange={(v) => updateField('business_name', v)} />
            <FieldWithAutoFill id="gstin" label="GSTIN" value={form.gstin} onChange={(v) => updateField('gstin', v)} />
            <FieldWithAutoFill id="business_email" label="Business Email" value={form.business_email} onChange={(v) => updateField('business_email', v)} type="email" />
            <FieldWithAutoFill id="business_phone" label="Business Phone" value={form.business_phone} onChange={(v) => updateField('business_phone', v)} />
          </div>
        </div>

        {/* Manufacturer */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Manufacturer Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FieldWithAutoFill id="manufacturer_name" label="Manufacturer Name" value={form.manufacturer_name} onChange={(v) => updateField('manufacturer_name', v)} />
            <FieldWithAutoFill id="country_of_origin" label="Country of Origin" value={form.country_of_origin} onChange={(v) => updateField('country_of_origin', v)} />
            <div className="md:col-span-2">
              <FieldWithAutoFill id="manufacturer_address" label="Manufacturer Address" value={form.manufacturer_address} onChange={(v) => updateField('manufacturer_address', v)} rows={2} />
            </div>
            <FieldWithAutoFill id="manufacturer_city" label="City" value={form.manufacturer_city} onChange={(v) => updateField('manufacturer_city', v)} />
            <FieldWithAutoFill id="manufacturer_state" label="State" value={form.manufacturer_state} onChange={(v) => updateField('manufacturer_state', v)} />
            <FieldWithAutoFill id="manufacturer_pincode" label="Pincode" value={form.manufacturer_pincode} onChange={(v) => updateField('manufacturer_pincode', v)} />
          </div>
        </div>

        {/* Importer & Packer */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Importer & Packer</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FieldWithAutoFill id="importer_name" label="Importer Name" value={form.importer_name} onChange={(v) => updateField('importer_name', v)} />
            <FieldWithAutoFill id="packer_name" label="Packer Name" value={form.packer_name} onChange={(v) => updateField('packer_name', v)} />
            <FieldWithAutoFill id="importer_address" label="Importer Address" value={form.importer_address} onChange={(v) => updateField('importer_address', v)} rows={2} />
            <FieldWithAutoFill id="packer_address" label="Packer Address" value={form.packer_address} onChange={(v) => updateField('packer_address', v)} rows={2} />
          </div>
        </div>

        {/* Addresses */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Addresses</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FieldWithAutoFill id="warehouse_address" label="Warehouse Address" value={form.warehouse_address} onChange={(v) => updateField('warehouse_address', v)} rows={3} />
            <FieldWithAutoFill id="return_address" label="Return Address" value={form.return_address} onChange={(v) => updateField('return_address', v)} rows={3} />
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isSaving}
            className="px-8 py-2.5 text-sm font-medium bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl hover:from-indigo-600 hover:to-purple-700 transition-all shadow-sm disabled:opacity-50"
          >
            {isSaving ? 'Saving...' : 'Save Profile'}
          </button>
        </div>
      </form>
    </div>
  );
}
