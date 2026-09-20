'use client';

import { useState, useEffect, useRef } from 'react';
import { api } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';

interface JobStatus {
  job_id: string;
  status: string;
  total: number;
  completed: number;
  created: number;
  errors: number;
  error_details?: { row?: number; sku?: string; product_id?: string; marketplace?: string; error: string }[];
}

export default function BulkPage() {
  const { addToast } = useToast();
  const fileRef = useRef<HTMLInputElement>(null);
  const [isImporting, setIsImporting] = useState(false);
  const [activeJob, setActiveJob] = useState<JobStatus | null>(null);
  const [pollingId, setPollingId] = useState<NodeJS.Timeout | null>(null);

  // Poll job status
  useEffect(() => {
    if (!activeJob || activeJob.status === 'completed' || activeJob.status === 'not_found') {
      if (pollingId) clearInterval(pollingId);
      return;
    }

    const id = setInterval(async () => {
      try {
        const status = await api.get<JobStatus>(`/bulk/jobs/${activeJob.job_id}`);
        setActiveJob(status);
        if (status.status === 'completed') {
          clearInterval(id);
          addToast({
            type: status.errors > 0 ? 'warning' : 'success',
            title: `Import complete: ${status.created} created, ${status.errors} errors`,
          });
        }
      } catch {
        clearInterval(id);
      }
    }, 1500);

    setPollingId(id);
    return () => clearInterval(id);
  }, [activeJob?.job_id, activeJob?.status]);

  const handleImport = async () => {
    const file = fileRef.current?.files?.[0];
    if (!file) {
      addToast({ type: 'warning', title: 'Select a CSV or Excel file first' });
      return;
    }
    setIsImporting(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const result = await api.upload<{ job_id: string; total_rows: number }>('/bulk/import', formData);
      setActiveJob({
        job_id: result.job_id,
        status: 'processing',
        total: result.total_rows,
        completed: 0,
        created: 0,
        errors: 0,
      });
      addToast({ type: 'info', title: `Importing ${result.total_rows} products...` });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Import failed';
      addToast({ type: 'error', title: msg });
    } finally {
      setIsImporting(false);
    }
  };

  const handleExport = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/bulk/export`,
        {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
        }
      );
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'products_export.csv';
      a.click();
      URL.revokeObjectURL(url);
      addToast({ type: 'success', title: 'Products exported successfully' });
    } catch {
      addToast({ type: 'error', title: 'Export failed' });
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/bulk/template`,
        {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
        }
      );
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'import_template.csv';
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      addToast({ type: 'error', title: 'Failed to download template' });
    }
  };

  const progressPct = activeJob && activeJob.total > 0
    ? Math.round((activeJob.completed / activeJob.total) * 100)
    : 0;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Bulk Operations</h1>
        <p className="text-slate-500 mt-1">Import, export, and bulk generate listings for your products</p>
      </div>

      {/* Cards Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Import Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4">
          <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
            <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-900">Import Products</h3>
            <p className="text-sm text-slate-500 mt-1">Upload CSV or Excel file to bulk create products</p>
          </div>
          <div className="space-y-3">
            <input
              ref={fileRef}
              type="file"
              accept=".csv,.xlsx,.xls"
              className="block w-full text-sm text-slate-500 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 transition-colors"
            />
            <div className="flex gap-2">
              <button
                onClick={handleImport}
                disabled={isImporting}
                className="flex-1 px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {isImporting ? 'Importing...' : 'Start Import'}
              </button>
              <button
                onClick={handleDownloadTemplate}
                className="px-4 py-2 text-sm font-medium bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors"
              >
                Template
              </button>
            </div>
          </div>
        </div>

        {/* Export Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center">
            <svg className="w-6 h-6 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-900">Export Products</h3>
            <p className="text-sm text-slate-500 mt-1">Download all your products as a CSV file</p>
          </div>
          <button
            onClick={handleExport}
            className="w-full px-4 py-2 text-sm font-medium bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
          >
            Export as CSV
          </button>
        </div>

        {/* Bulk Generate Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4">
          <div className="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center">
            <svg className="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-900">Bulk AI Generate</h3>
            <p className="text-sm text-slate-500 mt-1">Generate AI listings for all products at once</p>
          </div>
          <p className="text-xs text-slate-400">
            Select products from the Products page, then use &quot;Generate Listing&quot; for each, or use the API directly for bulk operations.
          </p>
        </div>
      </div>

      {/* Progress Section */}
      {activeJob && activeJob.status !== 'not_found' && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-900">
              {activeJob.status === 'completed' ? 'Import Complete' : 'Import in Progress'}
            </h3>
            <span className={`px-3 py-1 text-xs font-medium rounded-full ${
              activeJob.status === 'completed'
                ? 'bg-green-100 text-green-700'
                : 'bg-blue-100 text-blue-700'
            }`}>
              {activeJob.status === 'completed' ? 'Done' : `${progressPct}%`}
            </span>
          </div>

          {/* Progress bar */}
          <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
            <div
              className="h-3 rounded-full transition-all duration-500 bg-gradient-to-r from-blue-500 to-indigo-600"
              style={{ width: `${progressPct}%` }}
            />
          </div>

          {/* Stats */}
          <div className="grid grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-slate-900">{activeJob.total}</p>
              <p className="text-xs text-slate-500">Total</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-blue-600">{activeJob.completed}</p>
              <p className="text-xs text-slate-500">Processed</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-emerald-600">{activeJob.created}</p>
              <p className="text-xs text-slate-500">Created</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-red-600">{activeJob.errors}</p>
              <p className="text-xs text-slate-500">Errors</p>
            </div>
          </div>

          {/* Error details */}
          {activeJob.error_details && activeJob.error_details.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-slate-700 mb-2">Error Details</h4>
              <div className="max-h-40 overflow-y-auto space-y-1">
                {activeJob.error_details.map((err, i) => (
                  <div key={i} className="flex gap-2 text-xs bg-red-50 text-red-700 p-2 rounded-lg">
                    <span className="font-medium shrink-0">
                      {err.row ? `Row ${err.row}` : err.sku || err.product_id}:
                    </span>
                    <span>{err.error}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
