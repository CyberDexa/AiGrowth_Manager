'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { Linkedin, Twitter, Facebook, ExternalLink, RefreshCw, AlertCircle, CheckCircle2, Clock, TrendingUp, Calendar } from 'lucide-react';

interface PublishedPost {
  id: number;
  business_id: number;
  platform: string;
  status: string;
  content_text: string;
  platform_post_id: string | null;
  platform_post_url: string | null;
  scheduled_for: string | null;
  published_at: string | null;
  error_message: string | null;
  likes_count: number;
  comments_count: number;
  shares_count: number;
  impressions_count: number;
  created_at: string;
}

export default function PublishedPage() {
  const { getToken } = useAuth();
  const [posts, setPosts] = useState<PublishedPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState<string | null>(null);
  const [businessId, setBusinessId] = useState<number | null>(null);

  useEffect(() => {
    // Get business ID from local storage or API
    const storedBusiness = localStorage.getItem('selectedBusiness');
    if (storedBusiness) {
      const business = JSON.parse(storedBusiness);
      setBusinessId(business.id);
    }
  }, []);

  useEffect(() => {
    if (businessId) {
      loadPosts();
    }
  }, [businessId, selectedStatus]);

  const loadPosts = async () => {
    setLoading(true);
    try {
      const token = await getToken();
      const params = new URLSearchParams({ business_id: businessId!.toString() });
      if (selectedStatus) {
        params.append('status', selectedStatus);
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/publishing/posts?${params}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPosts(data.posts);
      }
    } catch (error) {
      console.error('Error loading posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = async (postId: number) => {
    try {
      const token = await getToken();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/publishing/posts/${postId}/retry`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        // Reload posts
        loadPosts();
      }
    } catch (error) {
      console.error('Error retrying post:', error);
    }
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'linkedin':
        return <Linkedin className="w-5 h-5" />;
      case 'twitter':
        return <Twitter className="w-5 h-5" />;
      case 'facebook':
      case 'meta':
        return <Facebook className="w-5 h-5" />;
      default:
        return null;
    }
  };

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case 'linkedin':
        return 'bg-blue-700';
      case 'twitter':
        return 'bg-sky-500';
      case 'facebook':
      case 'meta':
        return 'bg-blue-600';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'published':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
            <CheckCircle2 className="w-3 h-3" />
            Published
          </span>
        );
      case 'scheduled':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">
            <Clock className="w-3 h-3" />
            Scheduled
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-red-100 text-red-700 text-xs font-medium rounded-full">
            <AlertCircle className="w-3 h-3" />
            Failed
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full">
            <Clock className="w-3 h-3" />
            Pending
          </span>
        );
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
    }).format(date);
  };

  const getRelativeTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
  };

  if (!businessId) {
    return (
      <div className="p-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">Please select a business first.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Published Content</h1>
        <p className="text-gray-600">View and manage your published social media posts</p>
      </div>

      {/* Filters */}
      <div className="mb-6 flex items-center gap-2">
        <button
          onClick={() => setSelectedStatus(null)}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            selectedStatus === null
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
        >
          All
        </button>
        <button
          onClick={() => setSelectedStatus('published')}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            selectedStatus === 'published'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
        >
          Published
        </button>
        <button
          onClick={() => setSelectedStatus('scheduled')}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            selectedStatus === 'scheduled'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
        >
          Scheduled
        </button>
        <button
          onClick={() => setSelectedStatus('failed')}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            selectedStatus === 'failed'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
        >
          Failed
        </button>
      </div>

      {/* Posts List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading posts...</p>
        </div>
      ) : posts.length === 0 ? (
        <div className="text-center py-12">
          <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No published posts yet.</p>
          <p className="text-sm text-gray-500 mt-2">
            Create content in the Strategies section and publish it here.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {posts.map((post) => (
            <div key={post.id} className="bg-white border border-gray-200 rounded-lg p-6">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`${getPlatformColor(post.platform)} text-white p-2 rounded-lg`}>
                    {getPlatformIcon(post.platform)}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900 capitalize">{post.platform}</span>
                      {getStatusBadge(post.status)}
                    </div>
                    <p className="text-sm text-gray-500 mt-1">
                      {post.status === 'published' && post.published_at && (
                        <>Published {getRelativeTime(post.published_at)}</>
                      )}
                      {post.status === 'scheduled' && post.scheduled_for && (
                        <>Scheduled for {formatDate(post.scheduled_for)}</>
                      )}
                      {post.status === 'failed' && <>Failed to publish</>}
                      {post.status === 'pending' && <>Waiting to publish</>}
                    </p>
                  </div>
                </div>
              </div>

              {/* Content */}
              <div className="mb-4">
                <p className="text-gray-900 whitespace-pre-wrap line-clamp-4">{post.content_text}</p>
              </div>

              {/* Engagement Metrics (for published posts) */}
              {post.status === 'published' && (
                <div className="flex items-center gap-6 mb-4 text-sm text-gray-600">
                  <span>👍 {post.likes_count} likes</span>
                  <span>💬 {post.comments_count} comments</span>
                  <span>🔄 {post.shares_count} shares</span>
                  {post.impressions_count > 0 && <span>👁️ {post.impressions_count} impressions</span>}
                </div>
              )}

              {/* Error Message */}
              {post.status === 'failed' && post.error_message && (
                <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-3">
                  <div className="flex gap-2">
                    <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
                    <div>
                      <p className="text-sm font-medium text-red-800">Error</p>
                      <p className="text-sm text-red-700 mt-1">{post.error_message}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center gap-3">
                {post.status === 'published' && post.platform_post_url && (
                  <a
                    href={post.platform_post_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100"
                  >
                    <ExternalLink className="w-4 h-4" />
                    View on {post.platform.charAt(0).toUpperCase() + post.platform.slice(1)}
                  </a>
                )}
                {post.status === 'failed' && (
                  <button
                    onClick={() => handleRetry(post.id)}
                    className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                  >
                    <RefreshCw className="w-4 h-4" />
                    Retry
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
