'use client';

import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface ContentItem {
  id: number;
  business_id: number;
  platform: string;
  content_type: string;
  tone: string;
  text: string;
  hashtags?: string;
  status: string;
  scheduled_for?: string;
  created_at: string;
}

interface CalendarViewProps {
  content: ContentItem[];
  onEditContent: (item: ContentItem) => void;
}

export default function CalendarView({ content, onEditContent }: CalendarViewProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [calendarDays, setCalendarDays] = useState<Date[]>([]);

  useEffect(() => {
    generateCalendarDays();
  }, [currentDate]);

  const generateCalendarDays = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    // First day of month
    const firstDay = new Date(year, month, 1);
    // Last day of month
    const lastDay = new Date(year, month + 1, 0);
    
    // Start from the previous month to fill the week
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - startDate.getDay());
    
    // End on the next month to fill the week
    const endDate = new Date(lastDay);
    endDate.setDate(endDate.getDate() + (6 - endDate.getDay()));
    
    const days: Date[] = [];
    const current = new Date(startDate);
    
    while (current <= endDate) {
      days.push(new Date(current));
      current.setDate(current.getDate() + 1);
    }
    
    setCalendarDays(days);
  };

  const getContentForDate = (date: Date) => {
    return content.filter(item => {
      if (!item.scheduled_for) return false;
      const scheduledDate = new Date(item.scheduled_for);
      return scheduledDate.toDateString() === date.toDateString();
    });
  };

  const previousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const isToday = (date: Date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  const isCurrentMonth = (date: Date) => {
    return date.getMonth() === currentDate.getMonth();
  };

  const getPlatformColor = (platform: string) => {
    const colors: Record<string, string> = {
      linkedin: 'bg-blue-500',
      twitter: 'bg-sky-500',
      facebook: 'bg-indigo-500',
      instagram: 'bg-pink-500',
    };
    return colors[platform.toLowerCase()] || 'bg-gray-500';
  };

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <div className="rounded-lg bg-white p-6 shadow">
      {/* Calendar Header */}
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-xl font-semibold">
          {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
        </h2>
        <div className="flex gap-2">
          <button
            onClick={previousMonth}
            className="rounded p-2 hover:bg-gray-100"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <button
            onClick={() => setCurrentDate(new Date())}
            className="rounded px-3 py-2 text-sm font-medium hover:bg-gray-100"
          >
            Today
          </button>
          <button
            onClick={nextMonth}
            className="rounded p-2 hover:bg-gray-100"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-px bg-gray-200 rounded-lg overflow-hidden">
        {/* Day Headers */}
        {dayNames.map((day) => (
          <div
            key={day}
            className="bg-gray-50 px-2 py-3 text-center text-xs font-semibold text-gray-700"
          >
            {day}
          </div>
        ))}

        {/* Calendar Days */}
        {calendarDays.map((date, index) => {
          const dayContent = getContentForDate(date);
          const isCurrentDay = isToday(date);
          const inCurrentMonth = isCurrentMonth(date);

          return (
            <div
              key={index}
              className={`min-h-[120px] bg-white p-2 ${
                !inCurrentMonth ? 'bg-gray-50' : ''
              }`}
            >
              <div className="mb-1 flex items-center justify-between">
                <span
                  className={`text-sm font-medium ${
                    isCurrentDay
                      ? 'flex h-6 w-6 items-center justify-center rounded-full bg-blue-600 text-white'
                      : inCurrentMonth
                      ? 'text-gray-900'
                      : 'text-gray-400'
                  }`}
                >
                  {date.getDate()}
                </span>
                {dayContent.length > 0 && (
                  <span className="text-xs text-gray-500">
                    {dayContent.length}
                  </span>
                )}
              </div>

              {/* Content Items */}
              <div className="space-y-1">
                {dayContent.slice(0, 3).map((item) => (
                  <button
                    key={item.id}
                    onClick={() => onEditContent(item)}
                    className="w-full text-left"
                  >
                    <div
                      className={`rounded px-2 py-1 text-xs truncate ${getPlatformColor(
                        item.platform
                      )} text-white hover:opacity-80`}
                      title={item.text}
                    >
                      {new Date(item.scheduled_for!).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}{' '}
                      - {item.platform}
                    </div>
                  </button>
                ))}
                {dayContent.length > 3 && (
                  <div className="text-xs text-gray-500 px-2">
                    +{dayContent.length - 3} more
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="mt-6 flex items-center gap-4 text-sm">
        <span className="font-medium text-gray-700">Platforms:</span>
        <div className="flex gap-3">
          <div className="flex items-center gap-1">
            <div className="h-3 w-3 rounded bg-blue-500"></div>
            <span className="text-gray-600">LinkedIn</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="h-3 w-3 rounded bg-sky-500"></div>
            <span className="text-gray-600">Twitter</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="h-3 w-3 rounded bg-indigo-500"></div>
            <span className="text-gray-600">Facebook</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="h-3 w-3 rounded bg-pink-500"></div>
            <span className="text-gray-600">Instagram</span>
          </div>
        </div>
      </div>
    </div>
  );
}
