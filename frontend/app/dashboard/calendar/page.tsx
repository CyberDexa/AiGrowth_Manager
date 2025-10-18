'use client';

import { useEffect, useState, useCallback } from 'react';
import { useAuth } from '@clerk/nextjs';
import { Calendar as BigCalendar, dateFnsLocalizer, Event } from 'react-big-calendar';
import { format, parse, startOfWeek, getDay } from 'date-fns';
import { enUS } from 'date-fns/locale';
import { Linkedin, Twitter, Facebook, Calendar as CalendarIcon, Clock, Plus, AlertCircle } from 'lucide-react';
import 'react-big-calendar/lib/css/react-big-calendar.css';

const locales = {
  'en-US': enUS,
};

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
});

interface ScheduledPost {
  id: number;
  content_text: string;
  platform: string;
  social_account_id: number;
  scheduled_for: string;
  status: string;
  celery_task_id: string | null;
  created_at: string;
}

interface CalendarEvent extends Event {
  id: number;
  post: ScheduledPost;
}

const getPlatformColor = (platform: string): string => {
  const colors: Record<string, string> = {
    twitter: '#1DA1F2',
    linkedin: '#0077B5',
    meta: '#E4405F',
    facebook: '#1877F2',
    instagram: '#E4405F',
  };
  return colors[platform.toLowerCase()] || '#6366f1';
};

const getPlatformIcon = (platform: string) => {
  const iconClass = "h-4 w-4";
  switch (platform.toLowerCase()) {
    case 'linkedin':
      return <Linkedin className={iconClass} />;
    case 'twitter':
      return <Twitter className={iconClass} />;
    case 'meta':
    case 'facebook':
    case 'instagram':
      return <Facebook className={iconClass} />;
    default:
      return <CalendarIcon className={iconClass} />;
  }
};

export default function CalendarPage() {
  const { getToken } = useAuth();
  const [posts, setPosts] = useState<ScheduledPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [businessId, setBusinessId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [updateLoading, setUpdateLoading] = useState(false);

  useEffect(() => {
    const storedBusiness = localStorage.getItem('selectedBusiness');
    if (storedBusiness) {
      const business = JSON.parse(storedBusiness);
      setBusinessId(business.id);
    }
  }, []);

  useEffect(() => {
    if (businessId) {
      loadScheduledPosts();
    }
  }, [businessId]);

  const loadScheduledPosts = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = await getToken();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v2/scheduled?business_id=${businessId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPosts(data.scheduled_posts || []);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to load scheduled posts');
      }
    } catch (error) {
      console.error('Error loading scheduled posts:', error);
      setError('Network error loading scheduled posts');
    } finally {
      setLoading(false);
    }
  };

  const updateScheduledTime = async (postId: number, newTime: Date) => {
    setUpdateLoading(true);
    try {
      const token = await getToken();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v2/scheduled/${postId}`,
        {
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            scheduled_for: newTime.toISOString(),
          }),
        }
      );

      if (response.ok) {
        const updatedPost = await response.json();
        setPosts(prev => prev.map(p => p.id === postId ? updatedPost : p));
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to update scheduled time');
        // Reload posts to revert UI changes
        await loadScheduledPosts();
      }
    } catch (error) {
      console.error('Error updating scheduled time:', error);
      setError('Network error updating scheduled time');
      await loadScheduledPosts();
    } finally {
      setUpdateLoading(false);
    }
  };

  const handleEventDrop = useCallback(({ event, start }: { event: CalendarEvent; start: Date }) => {
    const now = new Date();
    if (start <= now) {
      setError('Cannot schedule posts in the past');
      return;
    }
    updateScheduledTime(event.id, start);
  }, [businessId]);

  const events: CalendarEvent[] = posts.map(post => ({
    id: post.id,
    title: `${post.platform.toUpperCase()}: ${post.content_text.substring(0, 50)}...`,
    start: new Date(post.scheduled_for),
    end: new Date(post.scheduled_for),
    post,
  }));

  const eventStyleGetter = (event: CalendarEvent) => {
    const backgroundColor = getPlatformColor(event.post.platform);
    return {
      style: {
        backgroundColor,
        borderRadius: '5px',
        opacity: 0.8,
        color: 'white',
        border: '0',
        display: 'block',
        fontSize: '12px',
      },
    };
  };

  const CustomEvent = ({ event }: { event: CalendarEvent }) => {
    return (
      <div className="flex items-center gap-1 px-1">
        {getPlatformIcon(event.post.platform)}
        <span className="truncate text-xs">{event.title}</span>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Clock className="h-12 w-12 animate-spin mx-auto mb-4 text-violet-600" />
          <p className="text-gray-600">Loading calendar...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <CalendarIcon className="h-8 w-8 text-violet-600" />
              Content Calendar
            </h1>
            <p className="text-gray-600 mt-1">
              View and manage your scheduled posts
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">
              {posts.length} scheduled {posts.length === 1 ? 'post' : 'posts'}
            </span>
            <button
              onClick={loadScheduledPosts}
              disabled={loading}
              className="p-2 text-violet-600 hover:bg-violet-50 rounded-lg transition-colors"
              title="Refresh"
            >
              <Clock className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-red-900 font-medium">Error</p>
              <p className="text-red-700 text-sm">{error}</p>
              <button
                onClick={() => setError(null)}
                className="text-red-600 hover:text-red-800 text-sm mt-1 underline"
              >
                Dismiss
              </button>
            </div>
          </div>
        )}

        {/* Platform legend */}
        <div className="mt-4 flex items-center gap-4 text-sm">
          <span className="text-gray-600 font-medium">Platforms:</span>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: getPlatformColor('twitter') }}></div>
            <span className="text-gray-700">Twitter</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: getPlatformColor('linkedin') }}></div>
            <span className="text-gray-700">LinkedIn</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: getPlatformColor('meta') }}></div>
            <span className="text-gray-700">Meta</span>
          </div>
        </div>
      </div>

      {/* Calendar */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4" style={{ height: '700px' }}>
        {posts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <CalendarIcon className="h-16 w-16 text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No scheduled posts</h3>
            <p className="text-gray-600 mb-4">
              Schedule your first post to see it on the calendar
            </p>
            <button
              onClick={() => window.location.href = '/dashboard/content'}
              className="flex items-center gap-2 px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 transition-colors"
            >
              <Plus className="h-5 w-5" />
              Create Content
            </button>
          </div>
        ) : (
          <BigCalendar
            localizer={localizer}
            events={events}
            startAccessor="start"
            endAccessor="end"
            style={{ height: '100%' }}
            eventPropGetter={eventStyleGetter}
            components={{
              event: CustomEvent,
            }}
            onEventDrop={handleEventDrop}
            draggableAccessor={() => !updateLoading}
            resizable={false}
            views={['month', 'week', 'day', 'agenda']}
            defaultView="month"
          />
        )}
      </div>

      {/* Loading overlay */}
      {updateLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-20 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg flex items-center gap-3">
            <Clock className="h-6 w-6 animate-spin text-violet-600" />
            <span className="text-gray-700">Updating schedule...</span>
          </div>
        </div>
      )}
    </div>
  );
}
