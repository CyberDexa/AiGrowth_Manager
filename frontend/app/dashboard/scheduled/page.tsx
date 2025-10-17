'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@clerk/nextjs';
import { Calendar, Clock, Trash2, Loader2, AlertCircle, CheckCircle2, Linkedin, Twitter, Facebook, Instagram, ChevronLeft, ChevronRight } from 'lucide-react';

interface ScheduledPost {
  id: number;
  business_id: number;
  social_account_id: number;
  content_text: string;
  platform: string;
  scheduled_for: string;
  status: string;
  created_at: string;
  celery_task_id: string | null;
}

export default function ScheduledPostsPage() {
  const { getToken } = useAuth();
  const [businesses, setBusinesses] = useState<any[]>([]);
  const [selectedBusiness, setSelectedBusiness] = useState<number | null>(null);
  const [scheduledPosts, setScheduledPosts] = useState<ScheduledPost[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [viewMode, setViewMode] = useState<'calendar' | 'list'>('calendar');
  const [cancellingId, setCancellingId] = useState<number | null>(null);

  useEffect(() => {
    loadBusinesses();
  }, []);

  useEffect(() => {
    if (selectedBusiness) {
      loadScheduledPosts();
    }
  }, [selectedBusiness]);

  const loadBusinesses = async () => {
    try {
      const token = await getToken();
      if (!token) return;

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/businesses`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setBusinesses(data);
        if (data.length > 0) {
          setSelectedBusiness(data[0].id);
        }
      }
    } catch (err) {
      console.error('Failed to load businesses:', err);
    }
  };

  const loadScheduledPosts = async () => {
    if (!selectedBusiness) return;

    setLoading(true);
    setError(null);

    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Authentication required');
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v2/scheduled?business_id=${selectedBusiness}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to load scheduled posts');
      }

      const data = await response.json();
      setScheduledPosts(data.scheduled_posts || []);
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelPost = async (postId: number) => {
    if (!confirm('Are you sure you want to cancel this scheduled post?')) {
      return;
    }

    setCancellingId(postId);

    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Authentication required');
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v2/schedule/${postId}`,
        {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to cancel post');
      }

      // Reload posts
      await loadScheduledPosts();
    } catch (err: any) {
      alert(err.message || 'Failed to cancel post');
    } finally {
      setCancellingId(null);
    }
  };

  const platformConfig: Record<string, { name: string; icon: any; color: string; bgColor: string }> = {
    linkedin: { name: 'LinkedIn', icon: Linkedin, color: 'text-blue-700', bgColor: 'bg-blue-100' },
    twitter: { name: 'Twitter', icon: Twitter, color: 'text-sky-500', bgColor: 'bg-sky-100' },
    facebook: { name: 'Facebook', icon: Facebook, color: 'text-blue-600', bgColor: 'bg-blue-100' },
    instagram: { name: 'Instagram', icon: Instagram, color: 'text-pink-600', bgColor: 'bg-pink-100' }
  };

  // Get posts for current month
  const getMonthPosts = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    return scheduledPosts.filter(post => {
      const postDate = new Date(post.scheduled_for);
      return postDate.getFullYear() === year && postDate.getMonth() === month;
    });
  };

  // Get calendar days
  const getCalendarDays = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    const days: (Date | null)[] = [];
    
    // Add empty cells for days before month starts
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add days of month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }
    
    return days;
  };

  // Get posts for a specific day
  const getPostsForDay = (date: Date | null) => {
    if (!date) return [];
    
    return scheduledPosts.filter(post => {
      const postDate = new Date(post.scheduled_for);
      return (
        postDate.getFullYear() === date.getFullYear() &&
        postDate.getMonth() === date.getMonth() &&
        postDate.getDate() === date.getDate()
      );
    });
  };

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Scheduled Posts</h1>
          <p className="text-gray-600">Manage your scheduled social media posts</p>
        </div>

        {/* Business Selector */}
        {businesses.length > 0 && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Business
            </label>
            <select
              value={selectedBusiness || ''}
              onChange={(e) => setSelectedBusiness(Number(e.target.value))}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {businesses.map((business) => (
                <option key={business.id} value={business.id}>
                  {business.name}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* View Toggle */}
        <div className="mb-6 flex items-center gap-2">
          <button
            onClick={() => setViewMode('calendar')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              viewMode === 'calendar'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            <Calendar className="w-4 h-4 inline mr-2" />
            Calendar View
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              viewMode === 'list'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            List View
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            <span className="ml-3 text-gray-600">Loading scheduled posts...</span>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Calendar View */}
        {!loading && !error && viewMode === 'calendar' && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            {/* Calendar Header */}
            <div className="flex items-center justify-between mb-6">
              <button
                onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1))}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              
              <h2 className="text-xl font-bold text-gray-900">
                {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
              </h2>
              
              <button
                onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1))}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>

            {/* Calendar Grid */}
            <div className="grid grid-cols-7 gap-2">
              {/* Day headers */}
              {dayNames.map((day) => (
                <div key={day} className="text-center font-semibold text-gray-600 py-2">
                  {day}
                </div>
              ))}

              {/* Calendar days */}
              {getCalendarDays().map((date, index) => {
                const postsForDay = getPostsForDay(date);
                const isToday = date && 
                  date.toDateString() === new Date().toDateString();

                return (
                  <div
                    key={index}
                    className={`min-h-24 p-2 border rounded-lg ${
                      date ? 'bg-white' : 'bg-gray-50'
                    } ${isToday ? 'border-blue-500 border-2' : 'border-gray-200'}`}
                  >
                    {date && (
                      <>
                        <div className="text-sm font-semibold text-gray-700 mb-1">
                          {date.getDate()}
                        </div>
                        <div className="space-y-1">
                          {postsForDay.slice(0, 3).map((post) => {
                            const config = platformConfig[post.platform] || platformConfig.linkedin;
                            const Icon = config.icon;
                            const time = new Date(post.scheduled_for).toLocaleTimeString('en-US', {
                              hour: 'numeric',
                              minute: '2-digit',
                              hour12: true
                            });

                            return (
                              <div
                                key={post.id}
                                className={`text-xs p-1 rounded ${config.bgColor} cursor-pointer hover:opacity-80`}
                                title={`${time} - ${post.content_text.substring(0, 50)}...`}
                              >
                                <Icon className={`w-3 h-3 inline ${config.color}`} />
                                <span className="ml-1 text-gray-700">{time}</span>
                              </div>
                            );
                          })}
                          {postsForDay.length > 3 && (
                            <div className="text-xs text-gray-500">
                              +{postsForDay.length - 3} more
                            </div>
                          )}
                        </div>
                      </>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Summary */}
            <div className="mt-6 pt-6 border-t">
              <p className="text-sm text-gray-600">
                {getMonthPosts().length} posts scheduled for {monthNames[currentDate.getMonth()]}
              </p>
            </div>
          </div>
        )}

        {/* List View */}
        {!loading && !error && viewMode === 'list' && (
          <div className="space-y-4">
            {scheduledPosts.length === 0 ? (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  No Scheduled Posts
                </h3>
                <p className="text-gray-600">
                  Schedule your first post to see it here
                </p>
              </div>
            ) : (
              scheduledPosts.map((post) => {
                const config = platformConfig[post.platform] || platformConfig.linkedin;
                const Icon = config.icon;
                const scheduledDate = new Date(post.scheduled_for);

                return (
                  <div
                    key={post.id}
                    className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        {/* Platform Badge */}
                        <div className="inline-flex items-center gap-2 px-3 py-1 bg-gray-100 rounded-full text-sm mb-3">
                          <Icon className={`w-4 h-4 ${config.color}`} />
                          <span className="text-gray-700">{config.name}</span>
                        </div>

                        {/* Content */}
                        <p className="text-gray-800 mb-4 whitespace-pre-wrap">
                          {post.content_text.substring(0, 200)}
                          {post.content_text.length > 200 && '...'}
                        </p>

                        {/* Schedule Info */}
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            <span>
                              {scheduledDate.toLocaleDateString('en-US', {
                                weekday: 'short',
                                month: 'short',
                                day: 'numeric',
                                year: 'numeric'
                              })}
                            </span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            <span>
                              {scheduledDate.toLocaleTimeString('en-US', {
                                hour: 'numeric',
                                minute: '2-digit',
                                hour12: true
                              })}
                            </span>
                          </div>
                          <div>
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              post.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                              post.status === 'queued' ? 'bg-blue-100 text-blue-800' :
                              post.status === 'published' ? 'bg-green-100 text-green-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {post.status}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="ml-4">
                        {post.status === 'pending' || post.status === 'queued' ? (
                          <button
                            onClick={() => handleCancelPost(post.id)}
                            disabled={cancellingId === post.id}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                            title="Cancel scheduled post"
                          >
                            {cancellingId === post.id ? (
                              <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                              <Trash2 className="w-5 h-5" />
                            )}
                          </button>
                        ) : (
                          <CheckCircle2 className="w-5 h-5 text-green-600" />
                        )}
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        )}
      </div>
    </div>
  );
}
