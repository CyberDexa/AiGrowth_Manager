"use client";

import React, { useState, useEffect } from 'react';
import { Search, Image as ImageIcon, Sparkles, Trash2, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';

interface ImageLibraryProps {
  businessId: number;
  onSelectImage?: (image: LibraryImage) => void;
  selectionMode?: boolean;
}

interface LibraryImage {
  id: number;
  storage_url: string;
  original_filename: string;
  width: number;
  height: number;
  size_mb: number;
  ai_generated: boolean;
  ai_prompt?: string;
  created_at: string;
}

interface ImageListResponse {
  images: LibraryImage[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export default function ImageLibrary({ 
  businessId, 
  onSelectImage,
  selectionMode = false 
}: ImageLibraryProps) {
  const [images, setImages] = useState<LibraryImage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterAI, setFilterAI] = useState<boolean | null>(null);
  const [selectedImageId, setSelectedImageId] = useState<number | null>(null);

  const fetchImages = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        business_id: businessId.toString(),
        page: page.toString(),
        page_size: '20',
      });

      if (searchQuery) {
        params.append('search', searchQuery);
      }

      if (filterAI !== null) {
        params.append('ai_generated', filterAI.toString());
      }

      const response = await fetch(`http://localhost:8003/api/v1/images?${params}`);

      if (!response.ok) {
        throw new Error('Failed to fetch images');
      }

      const data: ImageListResponse = await response.json();
      setImages(data.images);
      setTotalPages(data.total_pages);
      setTotal(data.total);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load images');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchImages();
  }, [businessId, page, searchQuery, filterAI]);

  const handleDelete = async (imageId: number) => {
    if (!confirm('Are you sure you want to delete this image?')) {
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8003/api/v1/images/${imageId}`,
        { method: 'DELETE' }
      );

      if (!response.ok) {
        throw new Error('Failed to delete image');
      }

      // Refresh images
      fetchImages();

    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete image');
    }
  };

  const handleSelectImage = (image: LibraryImage) => {
    if (selectionMode && onSelectImage) {
      setSelectedImageId(image.id);
      onSelectImage(image);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className="w-full space-y-6">
      {/* Header & Filters */}
      <div className="space-y-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search images by filename..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setPage(1);
            }}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2">
          <button
            onClick={() => {
              setFilterAI(null);
              setPage(1);
            }}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filterAI === null
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All Images ({total})
          </button>
          <button
            onClick={() => {
              setFilterAI(false);
              setPage(1);
            }}
            className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
              filterAI === false
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <ImageIcon className="w-4 h-4" />
            Uploaded
          </button>
          <button
            onClick={() => {
              setFilterAI(true);
              setPage(1);
            }}
            className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
              filterAI === true
                ? 'bg-purple-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            AI Generated
          </button>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-center">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && images.length === 0 && (
        <div className="text-center py-12">
          <ImageIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-600 text-lg">No images found</p>
          <p className="text-gray-500 text-sm mt-1">
            {searchQuery || filterAI !== null
              ? 'Try adjusting your filters'
              : 'Upload or generate your first image'}
          </p>
        </div>
      )}

      {/* Image Grid */}
      {!loading && images.length > 0 && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {images.map((image) => (
              <div
                key={image.id}
                onClick={() => handleSelectImage(image)}
                className={`group relative aspect-square rounded-lg overflow-hidden border-2 transition-all ${
                  selectionMode
                    ? selectedImageId === image.id
                      ? 'border-blue-500 ring-2 ring-blue-500'
                      : 'border-gray-200 hover:border-blue-300 cursor-pointer'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <img
                  src={image.storage_url}
                  alt={image.original_filename}
                  className="w-full h-full object-cover"
                />
                
                {/* Overlay on Hover */}
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all flex items-center justify-center">
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity space-y-2">
                    {!selectionMode && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(image.id);
                        }}
                        className="p-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    )}
                  </div>
                </div>

                {/* AI Badge */}
                {image.ai_generated && (
                  <div className="absolute top-2 left-2 px-2 py-1 bg-purple-600 text-white text-xs font-medium rounded-full flex items-center gap-1">
                    <Sparkles className="w-3 h-3" />
                    AI
                  </div>
                )}

                {/* Image Info */}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity">
                  <p className="text-white text-xs font-medium truncate">
                    {image.original_filename}
                  </p>
                  <p className="text-gray-300 text-xs mt-1">
                    {image.width}x{image.height} · {image.size_mb.toFixed(2)}MB
                  </p>
                  <p className="text-gray-400 text-xs">{formatDate(image.created_at)}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between pt-4">
              <p className="text-sm text-gray-600">
                Page {page} of {totalPages} · {total} total images
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
