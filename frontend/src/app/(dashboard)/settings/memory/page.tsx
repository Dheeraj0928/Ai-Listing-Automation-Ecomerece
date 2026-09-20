'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import type { SellerMemory, SellerMemoryListResponse } from '@/types/api';

const scopeLabels: Record<string, string> = {
  global: 'Global',
  marketplace: 'Marketplace',
  product: 'Product',
};

const sourceLabels: Record<string, string> = {
  manual: 'Manual',
  ai_suggested: 'AI Suggested',
  imported: 'Imported',
};

export default function SellerMemoryPage() {
  const [memories, setMemories] = useState<SellerMemory[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const { addToast } = useToast();

  // Form state
  const [fieldName, setFieldName] = useState('');
  const [fieldValue, setFieldValue] = useState('');
  const [scope, setScope] = useState('global');
  const [marketplace, setMarketplace] = useState('');

  const fetchMemories = async () => {
    setIsLoading(true);
    try {
      const data = await api.get<SellerMemoryListResponse>('/memory');
      setMemories(data.items || []);
      setTotal(data.total || 0);
    } catch {
      // No memories yet
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { fetchMemories(); }, []);

  const resetForm = () => {
    setFieldName('');
    setFieldValue('');
    setScope('global');
    setMarketplace('');
    setShowAdd(false);
    setEditId(null);
  };

  const handleSave = async () => {
    if (!fieldName.trim() || !fieldValue.trim()) {
      addToast({ type: 'warning', title: 'Fill in both field name and value' });
      return;
    }

    try {
      if (editId) {
        await api.put(`/memory/${editId}`, {
          field_value: fieldValue,
          scope,
          marketplace: scope === 'marketplace' ? marketplace : undefined,
        });
        addToast({ type: 'success', title: 'Memory updated' });
      } else {
        await api.post('/memory', {
          field_name: fieldName,
          field_value: fieldValue,
          scope,
          marketplace: scope === 'marketplace' ? marketplace : undefined,
        });
        addToast({ type: 'success', title: 'Memory saved' });
      }
      resetForm();
      fetchMemories();
    } catch {
      addToast({ type: 'error', title: 'Save failed' });
    }
  };

  const handleEdit = (mem: SellerMemory) => {
    setEditId(mem.id);
    setFieldName(mem.field_name);
    setFieldValue(mem.field_value);
    setScope(mem.scope);
    setMarketplace(mem.marketplace || '');
    setShowAdd(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/memory/${id}`);
      addToast({ type: 'success', title: 'Memory deactivated' });
      fetchMemories();
    } catch {
      addToast({ type: 'error', title: 'Delete failed' });
    }
  };

  // Common memory field suggestions
  const fieldSuggestions = [
    'brand', 'manufacturer_name', 'manufacturer_address', 'country_of_origin',
    'importer_name', 'importer_address', 'packer_name', 'packer_address',
    'warranty', 'return_policy', 'care_instructions',
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Seller Memory</h1>
          <p className="text-sm text-slate-500 mt-1">
            Memorized values auto-fill into listings. {total} entries saved.
          </p>
        </div>
        <button
          onClick={() => { resetForm(); setShowAdd(true); }}
          className="px-4 py-2.5 text-sm font-medium text-white bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl hover:from-indigo-400 hover:to-purple-500 transition-all shadow-sm"
        >
          + Add Memory
        </button>
      </div>

      {/* Add/Edit form */}
      {showAdd && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 mb-6 animate-in slide-in-from-top-2">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">{editId ? 'Edit Memory' : 'Add New Memory'}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-slate-600 mb-1">Field Name</label>
              <input
                type="text"
                value={fieldName}
                onChange={(e) => setFieldName(e.target.value)}
                disabled={!!editId}
                list="field-suggestions"
                placeholder="e.g. brand, manufacturer_name"
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none disabled:bg-slate-50"
              />
              <datalist id="field-suggestions">
                {fieldSuggestions.map(f => <option key={f} value={f} />)}
              </datalist>
            </div>
            <div>
              <label className="block text-sm text-slate-600 mb-1">Value</label>
              <input
                type="text"
                value={fieldValue}
                onChange={(e) => setFieldValue(e.target.value)}
                placeholder="The value to memorize"
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-sm text-slate-600 mb-1">Scope</label>
              <select
                value={scope}
                onChange={(e) => setScope(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
              >
                <option value="global">Global (all listings)</option>
                <option value="marketplace">Marketplace-specific</option>
              </select>
            </div>
            {scope === 'marketplace' && (
              <div>
                <label className="block text-sm text-slate-600 mb-1">Marketplace</label>
                <select
                  value={marketplace}
                  onChange={(e) => setMarketplace(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                >
                  <option value="">Select marketplace</option>
                  <option value="amazon">Amazon</option>
                  <option value="flipkart">Flipkart</option>
                  <option value="meesho">Meesho</option>
                </select>
              </div>
            )}
          </div>
          <div className="flex gap-2 mt-4">
            <button
              onClick={handleSave}
              className="px-5 py-2 text-sm font-medium text-white bg-indigo-600 rounded-xl hover:bg-indigo-500 transition-colors"
            >
              {editId ? 'Update' : 'Save'}
            </button>
            <button
              onClick={resetForm}
              className="px-5 py-2 text-sm font-medium text-slate-600 bg-slate-100 rounded-xl hover:bg-slate-200 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Memory table */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-100">
              <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Field</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Value</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Scope</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Source</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Used</th>
              <th className="text-right px-5 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {isLoading ? (
              <tr><td colSpan={6} className="px-5 py-12 text-center text-slate-400 text-sm">Loading...</td></tr>
            ) : memories.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-5 py-12 text-center">
                  <p className="text-slate-400 font-medium">No memories saved yet</p>
                  <p className="text-sm text-slate-400 mt-1">Add common values like brand, manufacturer, etc.</p>
                </td>
              </tr>
            ) : (
              memories.map(mem => (
                <tr key={mem.id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-5 py-3 text-sm font-medium text-slate-700">{mem.field_name}</td>
                  <td className="px-5 py-3 text-sm text-slate-600 max-w-xs truncate">{mem.field_value}</td>
                  <td className="px-5 py-3">
                    <span className="text-xs font-medium text-slate-500">
                      {scopeLabels[mem.scope] || mem.scope}
                      {mem.marketplace && ` (${mem.marketplace})`}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-xs text-slate-500">{sourceLabels[mem.source]}</td>
                  <td className="px-5 py-3 text-xs text-slate-500">{mem.usage_count}x</td>
                  <td className="px-5 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => handleEdit(mem)}
                        className="px-3 py-1.5 text-xs font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(mem.id)}
                        className="px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
                      >
                        Remove
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
