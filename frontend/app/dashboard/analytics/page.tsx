'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@clerk/nextjs';
import api from '@/lib/api';
import SyncStatus from '@/app/components/SyncStatus';
import PostingInsights from '@/components/PostingInsights';
import { 
  TrendingUp, 
  Users, 
  BarChart3, 
  Target,
  ArrowUp,
  ArrowDown,
  Lightbulb,
  Calendar as CalendarIcon,
  Clock,
  BookmarkPlus,
  Check
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface OverviewMetrics {
  total_posts: number;
  total_reach: number;
  total_engagement: number;
  avg_engagement_rate: number;
  growth_rate: number;
  top_platform: string;
  platform_breakdown: Record<string, any>;
}

interface ContentPerformance {
  id: number;
  platform: string;
  text: string;
  published_at: string;
  views: number;
  likes: number;
  shares: number;
  comments: number;
  engagement_rate: number;
}

interface Insight {
  title: string;
  description: string;
  priority: string;
}

export default function AnalyticsPage() {
  const { getToken } = useAuth();
  const [businesses, setBusinesses] = useState<any[]>([]);
  const [selectedBusiness, setSelectedBusiness] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState(30);

  // Analytics data
  const [overview, setOverview] = useState<OverviewMetrics | null>(null);
  const [contentPerformance, setContentPerformance] = useState<ContentPerformance[]>([]);
  const [platforms, setPlatforms] = useState<Record<string, any>>({});
  const [trends, setTrends] = useState<any[]>([]);
  const [insights, setInsights] = useState<any>(null);
  
  // Save to library state
  const [savingPostId, setSavingPostId] = useState<number | null>(null);
  const [savedPosts, setSavedPosts] = useState<Set<number>>(new Set());

  useEffect(() => {
    loadBusinesses();
  }, []);

  useEffect(() => {
    if (selectedBusiness) {
      loadAnalytics();
    }
  }, [selectedBusiness, timeRange]);

  const loadBusinesses = async () => {
    try {
      const token = await getToken();
      if (!token) return;
      
      const data = await api.businesses.list(token);
      setBusinesses(data);
      if (data.length > 0) {
        setSelectedBusiness(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load businesses:', err);
    }
  };

  const loadAnalytics = async () => {
    if (!selectedBusiness) return;
    
    try {
      setLoading(true);
      const token = await getToken();
      if (!token) return;

      // Calculate date range
      const end_date = new Date().toISOString().split('T')[0];
      const start_date = new Date(Date.now() - timeRange * 24 * 60 * 60 * 1000).toISOString().split('T')[0];

      // Use new comprehensive overview endpoint
      const params = new URLSearchParams({
        business_id: selectedBusiness.toString(),
        start_date,
        end_date,
        platform: 'all'
      });

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/analytics-simple/overview?${params}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        
        // Map new API response to existing state structure
        setOverview({
          total_posts: data.summary.total_posts,
          total_reach: data.summary.total_reach,
          total_engagement: data.summary.total_likes + data.summary.total_comments + data.summary.total_shares,
          avg_engagement_rate: data.summary.avg_engagement_rate,
          growth_rate: 0, // TODO: Calculate from previous period
          top_platform: Object.keys(data.by_platform || {})[0] || 'linkedin',
          platform_breakdown: data.by_platform || {}
        });

        // Map top posts to content performance
        setContentPerformance(data.top_posts.map((post: any) => ({
          id: post.id,
          platform: post.platform,
          text: post.content_preview,
          published_at: post.published_at,
          views: post.impressions,
          likes: post.likes_count,
          shares: post.shares_count,
          comments: post.comments_count,
          engagement_rate: post.engagement_rate
        })));

        // Map platform data
        setPlatforms(
          Object.entries(data.by_platform || {}).reduce((acc, [platform, metrics]: [string, any]) => ({
            ...acc,
            [platform]: {
              views: metrics.total_impressions || 0,
              engagement: metrics.total_engagement || 0,
              avg_engagement_rate: metrics.avg_engagement_rate || 0
            }
          }), {})
        );

        // Map trends data
        setTrends(data.trends.map((trend: any) => ({
          date: trend.date,
          views: trend.total_impressions || 0,
          engagement: trend.total_engagement || 0,
          posts: trend.posts_count || 0
        })));

        // Map insights from best times
        if (data.best_times && data.best_times.length > 0) {
          setInsights({
            best_posting_times: data.best_times.slice(0, 3).map((time: any) => ({
              day: time.day_of_week,
              time: time.best_hour ? `${time.best_hour}:00` : '10:00 AM',
              engagement: `+${time.avg_engagement_rate.toFixed(0)}%`
            })),
            top_content_types: [],
            recommendations: []
          });
        }
      }
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  const saveToLibrary = async (postId: number) => {
    if (!selectedBusiness || savingPostId) return;
    
    setSavingPostId(postId);
    try {
      const token = await getToken();
      if (!token) return;

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/content-library/save`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            source: 'published_post',
            item_id: postId
          })
        }
      );

      if (response.ok) {
        setSavedPosts(prev => new Set([...prev, postId]));
      } else {
        const error = await response.json();
        alert(`Failed to save: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Failed to save to library:', error);
      alert('Failed to save to library');
    } finally {
      setSavingPostId(null);
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const PLATFORM_COLORS: Record<string, string> = {
    linkedin: '#0A66C2',
    twitter: '#1DA1F2',
    facebook: '#4267B2',
    instagram: '#E4405F',
  };

  return (
    <div className="p-6">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
            <p className="mt-2 text-gray-600">Track your content performance and engagement</p>
          </div>

          <div className="flex gap-4">
            {/* Business Selector */}
            {businesses.length > 0 && (
              <select
                value={selectedBusiness || ''}
                onChange={(e) => setSelectedBusiness(Number(e.target.value))}
                className="rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
              >
                {businesses.map((business) => (
                  <option key={business.id} value={business.id}>
                    {business.name}
                  </option>
                ))}
              </select>
            )}

            {/* Time Range Selector */}
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(Number(e.target.value))}
              className="rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
              <option value={365}>Last year</option>
            </select>
          </div>
        </div>

        {/* Sync Status Widget */}
        {selectedBusiness && (
          <div className="mb-6">
            <SyncStatus 
              businessId={selectedBusiness} 
              apiToken={getToken}
            />
          </div>
        )}

        {loading && !overview ? (
          <div className="text-center py-12">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
            <p className="mt-4 text-gray-600">Loading analytics...</p>
          </div>
        ) : (
          <>
            {/* Overview Cards */}
            <div className="mb-8 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              {/* Total Posts */}
              <div className="rounded-lg border bg-white p-6 shadow-sm">
                <div className="flex items-center justify-between">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
                    <BarChart3 className="h-6 w-6 text-blue-600" />
                  </div>
                </div>
                <div className="mt-4">
                  <p className="text-sm font-medium text-gray-600">Total Posts</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">
                    {overview?.total_posts || 0}
                  </p>
                  <p className="mt-2 text-sm text-gray-500">
                    Last {timeRange} days
                  </p>
                </div>
              </div>

              {/* Total Reach */}
              <div className="rounded-lg border bg-white p-6 shadow-sm">
                <div className="flex items-center justify-between">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-green-100">
                    <Users className="h-6 w-6 text-green-600" />
                  </div>
                </div>
                <div className="mt-4">
                  <p className="text-sm font-medium text-gray-600">Total Reach</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">
                    {formatNumber(overview?.total_reach || 0)}
                  </p>
                  <p className="mt-2 text-sm text-gray-500">
                    Total views
                  </p>
                </div>
              </div>

              {/* Avg Engagement Rate */}
              <div className="rounded-lg border bg-white p-6 shadow-sm">
                <div className="flex items-center justify-between">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-purple-100">
                    <Target className="h-6 w-6 text-purple-600" />
                  </div>
                </div>
                <div className="mt-4">
                  <p className="text-sm font-medium text-gray-600">Avg Engagement</p>
                  <p className="mt-2 text-3xl font-bold text-gray-900">
                    {overview?.avg_engagement_rate?.toFixed(1) || 0}%
                  </p>
                  <p className="mt-2 text-sm text-gray-500">
                    Engagement rate
                  </p>
                </div>
              </div>

              {/* Growth Rate */}
              <div className="rounded-lg border bg-white p-6 shadow-sm">
                <div className="flex items-center justify-between">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-orange-100">
                    <TrendingUp className="h-6 w-6 text-orange-600" />
                  </div>
                </div>
                <div className="mt-4">
                  <p className="text-sm font-medium text-gray-600">Growth Rate</p>
                  <p className="mt-2 flex items-center text-3xl font-bold text-gray-900">
                    {overview?.growth_rate && overview.growth_rate > 0 ? '+' : ''}
                    {overview?.growth_rate?.toFixed(1) || 0}%
                    {overview?.growth_rate && overview.growth_rate > 0 ? (
                      <ArrowUp className="ml-2 h-6 w-6 text-green-500" />
                    ) : overview?.growth_rate && overview.growth_rate < 0 ? (
                      <ArrowDown className="ml-2 h-6 w-6 text-red-500" />
                    ) : null}
                  </p>
                  <p className="mt-2 text-sm text-gray-500">
                    vs previous period
                  </p>
                </div>
              </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              {/* Engagement Trends Chart */}
              <div className="rounded-lg border bg-white p-6 shadow-sm">
                <h3 className="mb-4 text-lg font-semibold">Engagement Trends</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="date" 
                      tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="views" stroke="#3B82F6" strokeWidth={2} name="Views" />
                    <Line type="monotone" dataKey="engagement" stroke="#10B981" strokeWidth={2} name="Engagement" />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Platform Comparison */}
              <div className="rounded-lg border bg-white p-6 shadow-sm">
                <h3 className="mb-4 text-lg font-semibold">Platform Performance</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={Object.entries(platforms).map(([platform, data]) => ({
                    platform: platform.charAt(0).toUpperCase() + platform.slice(1),
                    engagement: data.engagement,
                    views: data.views,
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="platform" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="views" fill="#3B82F6" name="Views" />
                    <Bar dataKey="engagement" fill="#10B981" name="Engagement" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Posting Time Recommendations */}
            {selectedBusiness && (
              <div className="mt-6">
                <PostingInsights 
                  businessId={selectedBusiness} 
                  getToken={getToken}
                />
              </div>
            )}

            {/* Content Performance Table */}
            <div className="mt-6 rounded-lg border bg-white shadow-sm">
              <div className="border-b border-gray-200 p-6">
                <h3 className="text-lg font-semibold">Top Performing Content</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                        Content
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                        Platform
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                        Views
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                        Engagement
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                        Rate
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 bg-white">
                    {contentPerformance.length > 0 ? (
                      contentPerformance.map((content) => (
                        <tr key={content.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4">
                            <div className="max-w-md">
                              <p className="truncate text-sm font-medium text-gray-900">
                                {content.text}
                              </p>
                              <p className="text-xs text-gray-500">
                                {content.published_at && new Date(content.published_at).toLocaleDateString()}
                              </p>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <span className="inline-flex rounded-full px-2 py-1 text-xs font-semibold" style={{
                              backgroundColor: PLATFORM_COLORS[content.platform] + '20',
                              color: PLATFORM_COLORS[content.platform]
                            }}>
                              {content.platform.charAt(0).toUpperCase() + content.platform.slice(1)}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900">
                            {formatNumber(content.views)}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900">
                            {formatNumber(content.likes + content.shares + content.comments)}
                          </td>
                          <td className="px-6 py-4 text-sm font-semibold text-gray-900">
                            {content.engagement_rate.toFixed(1)}%
                          </td>
                          <td className="px-6 py-4">
                            <button
                              onClick={() => saveToLibrary(content.id)}
                              disabled={savingPostId === content.id || savedPosts.has(content.id)}
                              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                                savedPosts.has(content.id)
                                  ? 'bg-green-100 text-green-700 cursor-default'
                                  : 'bg-blue-50 text-blue-700 hover:bg-blue-100 disabled:opacity-50'
                              }`}
                            >
                              {savingPostId === content.id ? (
                                <>
                                  <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                                  Saving...
                                </>
                              ) : savedPosts.has(content.id) ? (
                                <>
                                  <Check className="w-4 h-4" />
                                  Saved
                                </>
                              ) : (
                                <>
                                  <BookmarkPlus className="w-4 h-4" />
                                  Save
                                </>
                              )}
                            </button>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                          No content performance data available yet.
                          <br />
                          <span className="text-sm">Publish some content to see analytics here!</span>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* AI Insights */}
            {insights && (
              <div className="mt-6 rounded-lg border bg-gradient-to-br from-blue-50 to-purple-50 p-6 shadow-sm">
                <div className="mb-4 flex items-center gap-2">
                  <Lightbulb className="h-6 w-6 text-purple-600" />
                  <h3 className="text-lg font-semibold">AI-Powered Insights</h3>
                </div>

                <div className="grid gap-6 lg:grid-cols-2">
                  {/* Best Posting Times */}
                  <div className="rounded-lg bg-white p-4 shadow-sm">
                    <div className="mb-3 flex items-center gap-2">
                      <Clock className="h-5 w-5 text-blue-600" />
                      <h4 className="font-semibold">Best Posting Times</h4>
                    </div>
                    <div className="space-y-2">
                      {insights.best_posting_times?.map((time: any, index: number) => (
                        <div key={index} className="flex items-center justify-between rounded-lg bg-gray-50 p-3">
                          <div>
                            <p className="font-medium text-gray-900">{time.day}</p>
                            <p className="text-sm text-gray-600">{time.time}</p>
                          </div>
                          <span className="rounded-full bg-green-100 px-3 py-1 text-sm font-semibold text-green-700">
                            {time.engagement}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Recommendations */}
                  <div className="rounded-lg bg-white p-4 shadow-sm">
                    <div className="mb-3 flex items-center gap-2">
                      <Target className="h-5 w-5 text-purple-600" />
                      <h4 className="font-semibold">Recommendations</h4>
                    </div>
                    <div className="space-y-3">
                      {insights.recommendations?.map((rec: Insight, index: number) => (
                        <div 
                          key={index} 
                          className={`rounded-lg border-l-4 p-3 ${
                            rec.priority === 'high' ? 'border-red-500 bg-red-50' :
                            rec.priority === 'medium' ? 'border-yellow-500 bg-yellow-50' :
                            'border-blue-500 bg-blue-50'
                          }`}
                        >
                          <p className="font-semibold text-gray-900">{rec.title}</p>
                          <p className="mt-1 text-sm text-gray-700">{rec.description}</p>
                        </div>
                      ))}
                      {!insights.recommendations || insights.recommendations.length === 0 && (
                        <p className="text-sm text-gray-600">
                          Great job! Keep posting consistently to maintain your performance.
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
