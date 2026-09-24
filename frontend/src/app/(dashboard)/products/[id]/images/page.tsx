'use client';

import { useEffect, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';
import type { ProductImage } from '@/types/api';

export default function ProductImagesPage() {
  const params = useParams();
  const router = useRouter();
  const { addToast } = useToast();
  const productId = params.id as string;

  const [images, setImages] = useState<ProductImage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [imageType, setImageType] = useState('main');

  const [isProcessing, setIsProcessing] = useState<string | null>(null);

  const fetchImages = useCallback(async () => {
    try {
      const data = await api.get<ProductImage[]>(`/products/${productId}/images`);
      setImages(data || []);
    } catch {
      addToast({ type: 'error', title: 'Failed to load images' });
    } finally {
      setIsLoading(false);
    }
  }, [productId, addToast]);

  useEffect(() => {
    fetchImages();
  }, [fetchImages]);

  const handleUpload = async (files: FileList | File[]) => {
    if (!files.length) return;
    setIsUploading(true);
    try {
      const formData = new FormData();
      Array.from(files).forEach((file) => formData.append('files', file));

      await api.upload(`/products/${productId}/images?image_type=${imageType}`, formData);
      addToast({ type: 'success', title: `${files.length} image(s) uploaded` });
      await fetchImages();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Upload failed';
      addToast({ type: 'error', title: msg });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (imageId: string) => {
    if (!confirm('Delete this image?')) return;
    try {
      await api.delete(`/products/${productId}/images/${imageId}`);
      addToast({ type: 'success', title: 'Image deleted' });
      await fetchImages();
    } catch {
      addToast({ type: 'error', title: 'Failed to delete image' });
    }
  };

  const handleSetPrimary = async (imageId: string) => {
    try {
      await api.put(`/products/${productId}/images/${imageId}/primary`);
      addToast({ type: 'success', title: 'Primary image updated' });
      await fetchImages();
    } catch {
      addToast({ type: 'error', title: 'Failed to set primary' });
    }
  };

  const handleReorder = async (currentIndex: number, direction: 'left' | 'right') => {
    const targetIndex = direction === 'left' ? currentIndex - 1 : currentIndex + 1;
    if (targetIndex < 0 || targetIndex >= images.length) return;

    const newOrder = [...images];
    const [moved] = newOrder.splice(currentIndex, 1);
    newOrder.splice(targetIndex, 0, moved);

    setImages(newOrder);
    try {
      await api.put(`/products/${productId}/images/reorder`, newOrder.map((img) => img.id));
      addToast({ type: 'success', title: 'Image order updated' });
      await fetchImages();
    } catch {
      addToast({ type: 'error', title: 'Failed to reorder images' });
      await fetchImages();
    }
  };

  const handleStudioWhiteBg = async (imageId: string) => {
    setIsProcessing(imageId);
    try {
      await api.post(`/products/${productId}/images/${imageId}/studio-white-bg`, {});
      addToast({ type: 'success', title: 'Studio pure white background image created!' });
      await fetchImages();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Studio conversion failed';
      addToast({ type: 'error', title: msg });
    } finally {
      setIsProcessing(null);
    }
  };

  const handleGenerateMockup = async () => {
    setIsProcessing('mockup');
    try {
      await api.post(`/products/${productId}/images/generate-mockup`, {});
      addToast({ type: 'success', title: 'AI Studio catalog asset generated!' });
      await fetchImages();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Mockup generation failed';
      addToast({ type: 'error', title: msg });
    } finally {
      setIsProcessing(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files.length) {
      handleUpload(e.dataTransfer.files);
    }
  };

  const imageTypes = [
    { value: 'main', label: 'Main' },
    { value: 'white_bg', label: 'White Background' },
    { value: 'lifestyle', label: 'Lifestyle' },
    { value: 'closeup', label: 'Close-up' },
    { value: 'feature', label: 'Feature' },
    { value: 'size_spec', label: 'Size/Spec' },
  ];

  const typeColors: Record<string, string> = {
    main: 'bg-blue-100 text-blue-700',
    white_bg: 'bg-slate-100 text-slate-700',
    lifestyle: 'bg-emerald-100 text-emerald-700',
    closeup: 'bg-purple-100 text-purple-700',
    feature: 'bg-amber-100 text-amber-700',
    size_spec: 'bg-rose-100 text-rose-700',
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link
            href={`/products/${productId}`}
            className="p-2 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <svg className="w-5 h-5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Product Images &amp; Studio</h1>
            <p className="text-sm text-slate-500 mt-1">{images.length} of 8 images uploaded</p>
          </div>
        </div>

        <button
          onClick={handleGenerateMockup}
          disabled={isProcessing === 'mockup' || images.length >= 8}
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl hover:from-purple-500 hover:to-indigo-500 transition-all shadow-sm disabled:opacity-50"
        >
          {isProcessing === 'mockup' ? (
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          )}
          Generate Studio Mockup
        </button>
      </div>

      {/* Marketplace Compliance Banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 p-4 bg-gradient-to-r from-slate-50 via-indigo-50/30 to-slate-50 border border-slate-200 rounded-2xl">
        <div className="flex items-center gap-3">
          <span className="w-8 h-8 rounded-lg bg-orange-100 text-orange-700 flex items-center justify-center text-xs font-bold">AZ</span>
          <div>
            <p className="text-xs font-semibold text-slate-800">Amazon Standard</p>
            <p className="text-xs text-slate-500">Pure white background (#FFFFFF), 1000×1000px</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-bold">FK</span>
          <div>
            <p className="text-xs font-semibold text-slate-800">Flipkart Standard</p>
            <p className="text-xs text-slate-500">Minimum 500×500px, lifestyle shots encouraged</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="w-8 h-8 rounded-lg bg-pink-100 text-pink-700 flex items-center justify-center text-xs font-bold">MS</span>
          <div>
            <p className="text-xs font-semibold text-slate-800">Meesho Standard</p>
            <p className="text-xs text-slate-500">Uncluttered clear product focus, front view</p>
          </div>
        </div>
      </div>

      {/* Image type selector */}
      <div className="flex items-center gap-3">
        <span className="text-sm font-medium text-slate-700">Upload as:</span>
        <div className="flex gap-2 flex-wrap">
          {imageTypes.map((t) => (
            <button
              key={t.value}
              onClick={() => setImageType(t.value)}
              className={`px-3 py-1.5 text-xs font-medium rounded-full transition-all ${
                imageType === t.value
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Upload zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-2xl p-10 text-center transition-all cursor-pointer ${
          dragOver
            ? 'border-indigo-500 bg-indigo-50'
            : 'border-slate-300 hover:border-indigo-400 hover:bg-slate-50'
        }`}
      >
        <input
          type="file"
          multiple
          accept=".jpg,.jpeg,.png,.webp"
          onChange={(e) => e.target.files && handleUpload(e.target.files)}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        <div className="space-y-3">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-indigo-100 flex items-center justify-center">
            <svg className="w-7 h-7 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <p className="text-base font-medium text-slate-700">
              {isUploading ? 'Uploading...' : 'Drop images here or click to upload'}
            </p>
            <p className="text-sm text-slate-500 mt-1">
              JPG, PNG, WebP up to 10MB. Max 8 images per product.
            </p>
          </div>
        </div>
        {isUploading && (
          <div className="absolute inset-0 bg-white/80 backdrop-blur-sm rounded-2xl flex items-center justify-center">
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 border-3 border-indigo-500 border-t-transparent rounded-full animate-spin" />
              <span className="text-sm font-medium text-indigo-600">Uploading...</span>
            </div>
          </div>
        )}
      </div>

      {/* Image grid */}
      {images.length === 0 ? (
        <div className="text-center py-16 bg-slate-50 rounded-2xl border border-slate-200 space-y-3">
          <svg className="w-16 h-16 mx-auto text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <h3 className="text-lg font-semibold text-slate-700">No images yet</h3>
          <p className="text-sm text-slate-500 max-w-sm mx-auto">
            Upload real product photos or click &quot;Generate Studio Mockup&quot; to auto-create an Amazon-compliant catalog card.
          </p>
          <button
            onClick={handleGenerateMockup}
            disabled={isProcessing === 'mockup'}
            className="px-4 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-xl hover:bg-indigo-100 transition-colors"
          >
            Create First Studio Mockup
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {images.map((img, idx) => (
            <div
              key={img.id}
              className="group relative bg-white border border-slate-200 rounded-xl overflow-hidden hover:shadow-lg transition-all flex flex-col justify-between"
            >
              {/* Image display */}
              <div className="aspect-square bg-slate-100 relative">
                <img
                  src={`http://localhost:8000${img.url}`}
                  alt={img.filename}
                  className="w-full h-full object-contain p-2"
                />
                {img.is_primary && (
                  <div className="absolute top-2 left-2 px-2 py-1 bg-indigo-600 text-white text-xs font-medium rounded-md shadow-sm">
                    Primary
                  </div>
                )}
                <div className={`absolute top-2 right-2 px-2 py-1 text-xs font-medium rounded-md ${typeColors[img.image_type] || 'bg-slate-100 text-slate-600'}`}>
                  {img.image_type.replace('_', ' ')}
                </div>

                {/* Reorder arrows */}
                <div className="absolute bottom-2 left-2 flex gap-1 bg-slate-900/60 backdrop-blur-sm p-1 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={() => handleReorder(idx, 'left')}
                    disabled={idx === 0}
                    title="Move Left"
                    className="p-1 text-white hover:text-indigo-200 disabled:opacity-30"
                  >
                    ←
                  </button>
                  <span className="text-white text-xs px-1 self-center">{idx + 1}</span>
                  <button
                    onClick={() => handleReorder(idx, 'right')}
                    disabled={idx === images.length - 1}
                    title="Move Right"
                    className="p-1 text-white hover:text-indigo-200 disabled:opacity-30"
                  >
                    →
                  </button>
                </div>
              </div>

              {/* Actions */}
              <div className="p-3 space-y-2">
                <p className="text-xs text-slate-500 truncate" title={img.filename}>{img.filename}</p>
                <div className="flex gap-1.5 flex-wrap">
                  {!img.is_primary && (
                    <button
                      onClick={() => handleSetPrimary(img.id)}
                      className="flex-1 px-2 py-1.5 text-xs font-medium bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-100 transition-colors"
                    >
                      Primary
                    </button>
                  )}
                  {img.image_type !== 'white_bg' && (
                    <button
                      onClick={() => handleStudioWhiteBg(img.id)}
                      disabled={isProcessing === img.id || images.length >= 8}
                      title="Convert to Amazon pure white background"
                      className="px-2 py-1.5 text-xs font-medium bg-amber-50 text-amber-700 rounded-lg hover:bg-amber-100 transition-colors disabled:opacity-50"
                    >
                      {isProcessing === img.id ? '...' : 'White BG'}
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(img.id)}
                    className="px-2 py-1.5 text-xs font-medium bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
