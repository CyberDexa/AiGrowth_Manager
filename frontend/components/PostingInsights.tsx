'use client';

import React, { useState, useEffect } from 'react';
import { Clock, TrendingUp, Calendar, Lightbulb, Check, AlertCircle } from 'lucide-react';

interface TimeSlot {
  day: string;
  hour: number;
  avg_engagement_rate: number;
  post_count: number;
  confidence: string;
}

interface PlatformRecommendation {
  platform: string;
  best_times: TimeSlot[];
  overall_best_day: string;
  overall_best_hour: number;
  total_posts_analyzed: number;
  avg_engagement_rate: number;
  insights: string[];
}

interface RecommendationsData {
  recommendations: PlatformRecommendation[];
  business_id: number;
  analysis_period_days: number;
  last_updated: string;
}

interface PostingInsightsProps {
  businessId: number;
  getToken: () => Promise<string | null>;
}

const platformColors: Record<string, { bg: string; text: string; border: string }> = {
  twitter: { bg: 'bg-blue-50', text: 'text-blue-900', border: 'border-blue-200' },
  linkedin: { bg: 'bg-blue-50', text: 'text-blue-900', border: 'border-blue-200' },
  facebook: { bg: 'bg-indigo-50', text: 'text-indigo-900', border: 'border-indigo-200' },
  instagram: { bg: 'bg-pink-50', text: 'text-pink-900', border: 'border-pink-200' },
};

const confidenceColors: Record<string, string> = {
  high: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  low: 'bg-gray-100 text-gray-600',
};

const formatHour = (hour: number): string => {
  const period = hour >= 12 ? 'PM' : 'AM';
  const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
  return `${displayHour}:00 ${period}`;
};

const getDayAbbreviation = (day: string): string => {
  return day.substring(0, 3);
};

const PostingInsights = React.memo(({ businessId, getToken }: PostingInsightsProps) => {
  const [recommendations, setRecommendations] = useState<RecommendationsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadRecommendations();
  }, [businessId]);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      const token = await getToken();
      if (!token) return;

      const response = await fetch(
        `/api/v1/insights/recommendations?business_id=${businessId}&days=90`,
        {
          headers: { 'Authorization': `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setRecommendations(data);
      } else {
        setError('Failed to load recommendations');
      }
    } catch (err) {
      console.error('Failed to load recommendations:', err);
      setError('Failed to load recommendations');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="rounded-lg bg-white p-6 shadow">
        <div className="animate-pulse">
          <div className="mb-4 h-6 w-48 rounded bg-gray-200"></div>
          <div className="space-y-3">
            <div className="h-20 rounded bg-gray-100"></div>
            <div className="h-20 rounded bg-gray-100"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !recommendations) {
    return (
      <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-yellow-600" />
          <div>
            <h3 className="font-medium text-yellow-900">Recommendations Unavailable</h3>
            <p className="mt-1 text-sm text-yellow-700">
              {error || 'Unable to load posting recommendations. Publish more posts to get personalized insights.'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Clock className="h-5 w-5 text-violet-600" />
          <h2 className="text-lg font-semibold text-gray-900">Best Times to Post</h2>
        </div>
        <span className="text-xs text-gray-500">
          Last updated: {new Date(recommendations.last_updated).toLocaleDateString()}
        </span>
      </div>

      {/* Platform Cards */}
      <div className="grid gap-4 md:grid-cols-2">
        {recommendations.recommendations.map((rec) => {
          const colors = platformColors[rec.platform] || platformColors.twitter;
          
          return (
            <div
              key={rec.platform}
              className={`rounded-lg border ${colors.border} ${colors.bg} p-4`}
            >
              {/* Platform Header */}
              <div className="mb-3 flex items-center justify-between">
                <div>
                  <h3 className={`font-semibold capitalize ${colors.text}`}>
                    {rec.platform}
                  </h3>
                  <p className="text-xs text-gray-600">
                    {rec.total_posts_analyzed > 0
                      ? `Based on ${rec.total_posts_analyzed} posts`
                      : 'Industry benchmarks'}
                  </p>
                </div>
                {rec.total_posts_analyzed >= 10 && (
                  <div className="flex items-center gap-1 rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-800">
                    <Check className="h-3 w-3" />
                    Personalized
                  </div>
                )}
              </div>

              {/* Best Overall Time */}
              <div className="mb-3 rounded-lg bg-white p-3 shadow-sm">
                <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
                  <TrendingUp className="h-4 w-4 text-violet-600" />
                  Top Recommendation
                </div>
                <div className="mt-2 flex items-baseline gap-2">
                  <span className={`text-2xl font-bold ${colors.text}`}>
                    {formatHour(rec.overall_best_hour)}
                  </span>
                  <span className="text-sm text-gray-600">
                    on {rec.overall_best_day}s
                  </span>
                </div>
                {rec.avg_engagement_rate > 0 && (
                  <div className="mt-1 text-xs text-gray-600">
                    Avg. engagement: {rec.avg_engagement_rate.toFixed(1)}%
                  </div>
                )}
              </div>

              {/* Top 3 Time Slots */}
              {rec.best_times.length > 0 && (
                <div className="mb-3 space-y-2">
                  <div className="text-xs font-medium text-gray-700">
                    Other Great Times
                  </div>
                  {rec.best_times.slice(1, 4).map((slot, idx) => (
                    <div
                      key={`${slot.day}-${slot.hour}`}
                      className="flex items-center justify-between rounded bg-white px-3 py-2 text-sm"
                    >
                      <div className="flex items-center gap-2">
                        <Calendar className="h-3.5 w-3.5 text-gray-400" />
                        <span className="font-medium text-gray-700">
                          {getDayAbbreviation(slot.day)}
                        </span>
                        <span className="text-gray-600">
                          {formatHour(slot.hour)}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        {slot.avg_engagement_rate > 0 && (
                          <span className="text-xs text-gray-500">
                            {slot.avg_engagement_rate.toFixed(1)}%
                          </span>
                        )}
                        <span
                          className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                            confidenceColors[slot.confidence]
                          }`}
                        >
                          {slot.confidence}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Insights */}
              {rec.insights.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-1 text-xs font-medium text-gray-700">
                    <Lightbulb className="h-3.5 w-3.5 text-yellow-500" />
                    Insights
                  </div>
                  {rec.insights.map((insight, idx) => (
                    <div
                      key={idx}
                      className="rounded bg-white px-3 py-2 text-xs text-gray-600"
                    >
                      {insight}
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Analysis Period Info */}
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-3 text-center">
        <p className="text-xs text-gray-600">
          Analysis based on {recommendations.analysis_period_days} days of data.
          {recommendations.recommendations.some(r => r.total_posts_analyzed < 10) && (
            <span className="ml-1">
              Publish more posts to get more accurate personalized recommendations.
            </span>
          )}
        </p>
      </div>
    </div>
  );
});

PostingInsights.displayName = 'PostingInsights';

export default PostingInsights;
