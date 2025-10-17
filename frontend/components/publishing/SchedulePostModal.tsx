'use client';

import { useState, useEffect } from 'react';
import { X, Calendar, Clock, Loader2, CheckCircle2, AlertCircle, Linkedin, Twitter, Facebook, Instagram } from 'lucide-react';
import { useAuth } from '@clerk/nextjs';

interface SchedulePostModalProps {
  isOpen: boolean;
  onClose: () => void;
  content: string;
  platforms: ('linkedin' | 'twitter' | 'facebook' | 'instagram')[];
  businessId: number;
  platformParams?: Record<string, any>;
  onScheduled?: (scheduledPostId: number) => void;
  onError?: (error: string) => void;
}

export default function SchedulePostModal({
  isOpen,
  onClose,
  content,
  platforms,
  businessId,
  platformParams = {},
  onScheduled,
  onError
}: SchedulePostModalProps) {
  const { getToken } = useAuth();
  const [scheduledDate, setScheduledDate] = useState('');
  const [scheduledTime, setScheduledTime] = useState('');
  const [scheduling, setScheduling] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset state when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      // Set default to tomorrow at 9 AM
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      tomorrow.setHours(9, 0, 0, 0);

      setScheduledDate(tomorrow.toISOString().split('T')[0]);
      setScheduledTime('09:00');
      setError(null);
      setSuccess(false);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const platformConfig: Record<string, { name: string; icon: any; color: string }> = {
    linkedin: { name: 'LinkedIn', icon: Linkedin, color: 'text-blue-700' },
    twitter: { name: 'Twitter', icon: Twitter, color: 'text-sky-500' },
    facebook: { name: 'Facebook', icon: Facebook, color: 'text-blue-600' },
    instagram: { name: 'Instagram', icon: Instagram, color: 'text-pink-600' }
  };

  const handleSchedule = async () => {
    if (!scheduledDate || !scheduledTime) {
      const errorMsg = 'Please select both date and time';
      setError(errorMsg);
      onError?.(errorMsg);
      return;
    }

    // Validate future date
    const scheduledDateTime = new Date(`${scheduledDate}T${scheduledTime}:00`);
    const now = new Date();

    if (scheduledDateTime <= now) {
      const errorMsg = 'Scheduled time must be in the future';
      setError(errorMsg);
      onError?.(errorMsg);
      return;
    }

    setScheduling(true);
    setError(null);

    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v2/schedule`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          content,
          platforms,
          scheduled_for: `${scheduledDate}T${scheduledTime}:00Z`,
          platform_params: platformParams
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to schedule post');
      }

      const data = await response.json();

      if (data.success) {
        setSuccess(true);
        onScheduled?.(data.scheduled_post_id);

        // Close modal after 2 seconds
        setTimeout(() => {
          onClose();
        }, 2000);
      } else {
        throw new Error('Scheduling failed');
      }
    } catch (err: any) {
      const errorMsg = err.message || 'An error occurred while scheduling';
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setScheduling(false);
    }
  };

  // Get min date (today)
  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center gap-3">
            <Calendar className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-bold text-gray-900">Schedule Post</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            disabled={scheduling}
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Platforms */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Publishing to:
            </label>
            <div className="flex flex-wrap gap-2">
              {platforms.map((platform) => {
                const config = platformConfig[platform];
                const Icon = config.icon;
                return (
                  <div
                    key={platform}
                    className="inline-flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-full text-sm"
                  >
                    <Icon className={`w-4 h-4 ${config.color}`} />
                    <span className="text-gray-700">{config.name}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Content Preview */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Content:
            </label>
            <div className="p-4 bg-gray-50 rounded-lg border border-gray-200 max-h-40 overflow-y-auto">
              <p className="text-sm text-gray-800 whitespace-pre-wrap">
                {content.substring(0, 200)}
                {content.length > 200 && '...'}
              </p>
              <p className="text-xs text-gray-500 mt-2">
                {content.length} characters
              </p>
            </div>
          </div>

          {/* Date Picker */}
          <div>
            <label htmlFor="scheduled-date" className="block text-sm font-medium text-gray-700 mb-2">
              <Calendar className="w-4 h-4 inline mr-1" />
              Date
            </label>
            <input
              id="scheduled-date"
              type="date"
              value={scheduledDate}
              onChange={(e) => setScheduledDate(e.target.value)}
              min={today}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={scheduling}
            />
          </div>

          {/* Time Picker */}
          <div>
            <label htmlFor="scheduled-time" className="block text-sm font-medium text-gray-700 mb-2">
              <Clock className="w-4 h-4 inline mr-1" />
              Time
            </label>
            <input
              id="scheduled-time"
              type="time"
              value={scheduledTime}
              onChange={(e) => setScheduledTime(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={scheduling}
            />
          </div>

          {/* Preview Scheduled DateTime */}
          {scheduledDate && scheduledTime && (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Will publish on:</strong>
                <br />
                {new Date(`${scheduledDate}T${scheduledTime}:00`).toLocaleString('en-US', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: 'numeric',
                  minute: '2-digit',
                  hour12: true
                })}
              </p>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-2">
              <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-green-800">
                Post scheduled successfully! It will be published at the scheduled time.
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 bg-gray-50 border-t">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            disabled={scheduling}
          >
            Cancel
          </button>
          <button
            onClick={handleSchedule}
            disabled={scheduling || !scheduledDate || !scheduledTime}
            className="inline-flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {scheduling ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Scheduling...</span>
              </>
            ) : success ? (
              <>
                <CheckCircle2 className="w-4 h-4" />
                <span>Scheduled!</span>
              </>
            ) : (
              <>
                <Calendar className="w-4 h-4" />
                <span>Schedule Post</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
