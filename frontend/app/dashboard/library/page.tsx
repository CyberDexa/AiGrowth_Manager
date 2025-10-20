'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@clerk/nextjs';
import { BookmarkPlus, Search, Twitter, Linkedin, Facebook, Instagram, Heart, MessageCircle, Share2, Eye, Copy, Trash2 } from 'lucide-react';

interface LibraryItem {
  id: number;
  source: 'content' | 'published_post';
  platform: string;
  text: string;
  hashtags?: string;
  media_urls?: string[];
  saved_at: string;
  created_at: string;
  likes_count?: number;
  comments_count?: number;
  shares_count?: number;
  impressions_count?: number;
}

interface LibraryStats {
  total_items: number;
  ai_generated_count: number;
  published_count: number;
  by_platform: Record<string, number>;
}

const platformConfig = {
  twitter: { name: 'Twitter', icon: Twitter, color: 'text-sky-500', bg: 'bg-sky-50' },
  linkedin: { name: 'LinkedIn', icon: Linkedin, color: 'text-blue-700', bg: 'bg-blue-50' },
  facebook: { name: 'Facebook', icon: Facebook, color: 'text-blue-600', bg: 'bg-blue-50' },
  instagram: { name: 'Instagram', icon: Instagram, color: 'text-pink-500', bg: 'bg-pink-50' },
};

export default function ContentLibraryPage() {
  const { getToken } = useAuth();
  const [items, setItems] = useState<LibraryItem[]>([]);
  const [stats, setStats] = useState<LibraryStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [businessId, setBusinessId] = useState<number | null>(null);
  
  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState<string>('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  
  // UI state
  const [copyingId, setCopyingId] = useState<number | null>(null);
  const [removingId, setRemovingId] = useState<number | null>(null);

  useEffect(() => {
    loadBusiness();
  }, []);

  useEffect(() => {
    if (businessId) {
      loadLibraryItems();
      loadLibraryStats();
    }
  }, [businessId, searchQuery, selectedPlatform, page]);

  const loadBusiness = async () => {
    try {
      const savedBusiness = localStorage.getItem('selectedBusiness');
      if (savedBusiness) {
        const business = JSON.parse(savedBusiness);
        setBusinessId(business.id);
        return;
      }

      const token = await getToken();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/businesses`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        if (Array.isArray(data) && data.length > 0) {
          setBusinessId(data[0].id);
          localStorage.setItem('selectedBusiness', JSON.stringify(data[0]));
        }
      }
    } catch (error) {
      console.error('Failed to load business:', error);
    }
  };

  const loadLibraryItems = async () => {
    if (!businessId) return;
    
    setLoading(true);
    try {
      const token = await getToken();
      const params = new URLSearchParams({
        business_id: businessId.toString(),
        page: page.toString(),
        page_size: '12'
      });
      
      if (selectedPlatform) params.append('platform', selectedPlatform);
      if (searchQuery) params.append('search', searchQuery);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/content-library?${params}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      if (response.ok) {
        const data = await response.json();
        setItems(data.items);
        setTotal(data.total);
      }
    } catch (error) {
      console.error('Failed to load library items:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadLibraryStats = async () => {
    if (!businessId) return;
    
    try {
      const token = await getToken();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/content-library/stats?business_id=${businessId}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to load library stats:', error);
    }
  };

  const copyToClipboard = async (item: LibraryItem) => {
    setCopyingId(item.id);
    try {
      const fullText = item.hashtags 
        ? `${item.text}\n\n${item.hashtags}`
        : item.text;
      await navigator.clipboard.writeText(fullText);
      
      setTimeout(() => setCopyingId(null), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
      setCopyingId(null);
    }
  };

  const removeFromLibrary = async (item: LibraryItem) => {
    if (!confirm('Remove this item from your library?')) return;
    
    setRemovingId(item.id);
    try {
      const token = await getToken();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/content-library/${item.source}/${item.id}`,
        {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (response.ok) {
        loadLibraryItems();
        loadLibraryStats();
      }
    } catch (error) {
      console.error('Failed to remove item:', error);
    } finally {
      setRemovingId(null);
    }
  };

  const getPlatformIcon = (platform: string) => {
    const config = platformConfig[platform as keyof typeof platformConfig];
    if (!config) return null;
    const Icon = config.icon;
    return <Icon className="w-5 h-5" />;
  };

  if (loading && items.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Content Library</h1>
        <p className="text-gray-600 mt-2">
          Save and reuse your best-performing content
        </p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Saved</p>
                <p className="text-3xl font-bold text-gray-900">{stats.total_items}</p>
              </div>
              <BookmarkPlus className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">AI Generated</p>
                <p className="text-3xl font-bold text-purple-600">{stats.ai_generated_count}</p>
              </div>
              <BookmarkPlus className="w-8 h-8 text-purple-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Published</p>
                <p className="text-3xl font-bold text-green-600">{stats.published_count}</p>
              </div>
              <BookmarkPlus className="w-8 h-8 text-green-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div>
              <p className="text-sm text-gray-600 mb-2">By Platform</p>
              <div className="space-y-1">
                {Object.entries(stats.by_platform).map(([platform, count]) => (
                  <div key={platform} className="flex items-center justify-between text-sm">
                    <span className="capitalize">{platform}</span>
                    <span className="font-semibold">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search in saved content..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setPage(1);
                }}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <select
            value={selectedPlatform}
            onChange={(e) => {
              setSelectedPlatform(e.target.value);
              setPage(1);
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Platforms</option>
            <option value="twitter">Twitter</option>
            <option value="linkedin">LinkedIn</option>
            <option value="facebook">Facebook</option>
            <option value="instagram">Instagram</option>
          </select>
        </div>
      </div>

      {/* Content Grid */}
      {items.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <BookmarkPlus className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No saved content yet</h3>
          <p className="text-gray-600">
            Save your best posts to quickly reuse them later
          </p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {items.map((item) => {
              const config = platformConfig[item.platform as keyof typeof platformConfig];
              const Icon = config?.icon;

              return (
                <div
                  key={`${item.source}-${item.id}`}
                  className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow"
                >
                  {/* Header */}
                  <div className={`${config?.bg} px-4 py-3 rounded-t-lg flex items-center justify-between`}>
                    <div className="flex items-center gap-2">
                      {Icon && <Icon className={`w-5 h-5 ${config.color}`} />}
                      <span className="font-semibold text-gray-900">{config?.name}</span>
                    </div>
                    <span className="text-xs text-gray-600">
                      {new Date(item.saved_at).toLocaleDateString()}
                    </span>
                  </div>

                  {/* Content */}
                  <div className="p-4">
                    <p className="text-gray-800 line-clamp-4 mb-3">{item.text}</p>
                    
                    {item.hashtags && (
                      <p className="text-blue-600 text-sm mb-3">{item.hashtags}</p>
                    )}

                    {/* Engagement Stats (for published posts) */}
                    {item.source === 'published_post' && (
                      <div className="flex items-center gap-4 text-sm text-gray-600 mb-3 pt-3 border-t">
                        {item.likes_count !== undefined && (
                          <div className="flex items-center gap-1">
                            <Heart className="w-4 h-4" />
                            <span>{item.likes_count}</span>
                          </div>
                        )}
                        {item.comments_count !== undefined && (
                          <div className="flex items-center gap-1">
                            <MessageCircle className="w-4 h-4" />
                            <span>{item.comments_count}</span>
                          </div>
                        )}
                        {item.shares_count !== undefined && (
                          <div className="flex items-center gap-1">
                            <Share2 className="w-4 h-4" />
                            <span>{item.shares_count}</span>
                          </div>
                        )}
                        {item.impressions_count !== undefined && (
                          <div className="flex items-center gap-1">
                            <Eye className="w-4 h-4" />
                            <span>{item.impressions_count}</span>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Source Badge */}
                    <div className="flex items-center justify-between">
                      <span className={`text-xs px-2 py-1 rounded ${
                        item.source === 'published_post' 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-purple-100 text-purple-700'
                      }`}>
                        {item.source === 'published_post' ? 'Published' : 'AI Generated'}
                      </span>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2 mt-4 pt-4 border-t">
                      <button
                        onClick={() => copyToClipboard(item)}
                        disabled={copyingId === item.id}
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                      >
                        <Copy className="w-4 h-4" />
                        {copyingId === item.id ? 'Copied!' : 'Copy'}
                      </button>
                      <button
                        onClick={() => removeFromLibrary(item)}
                        disabled={removingId === item.id}
                        className="px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 disabled:opacity-50 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Pagination */}
          {total > 12 && (
            <div className="flex justify-center gap-2 mt-8">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 hover:bg-gray-50"
              >
                Previous
              </button>
              <span className="px-4 py-2 text-gray-700">
                Page {page} of {Math.ceil(total / 12)}
              </span>
              <button
                onClick={() => setPage(p => p + 1)}
                disabled={page >= Math.ceil(total / 12)}
                className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 hover:bg-gray-50"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
