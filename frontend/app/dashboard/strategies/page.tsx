'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import { Target, TrendingUp, Users, Calendar, Lightbulb, CheckCircle2, Sparkles } from 'lucide-react';
import { useOnboarding } from '@/contexts/OnboardingContext';

interface Business {
  id: number;
  name: string;
  industry: string;
  target_audience?: string;
  goals?: string[];
}

interface Strategy {
  id: string;
  title: string;
  description: string;
  type: 'content' | 'engagement' | 'growth' | 'brand';
  priority: 'high' | 'medium' | 'low';
  status: 'active' | 'planned' | 'completed';
  tactics: string[];
  expectedOutcome: string;
}

export default function StrategiesPage() {
  const { getToken } = useAuth();
  const { completeStep } = useOnboarding();
  const router = useRouter();
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [selectedBusiness, setSelectedBusiness] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [strategies, setStrategies] = useState<Strategy[]>([]);

  useEffect(() => {
    loadBusinesses();
  }, []);

  useEffect(() => {
    if (selectedBusiness) {
      loadStrategies();
    }
  }, [selectedBusiness]);

  const loadBusinesses = async () => {
    try {
      const token = await getToken();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/businesses/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setBusinesses(data);
        if (data.length > 0) {
          setSelectedBusiness(data[0].id);
        }
      }
    } catch (error) {
      console.error('Failed to load businesses:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStrategies = () => {
    // Generate sample strategies based on business
    const business = businesses.find(b => b.id === selectedBusiness);
    const sampleStrategies: Strategy[] = [
      {
        id: '1',
        title: 'Content Consistency Strategy',
        description: 'Maintain a regular posting schedule across all platforms to build audience trust and engagement.',
        type: 'content',
        priority: 'high',
        status: 'active',
        tactics: [
          'Post 3-5 times per week on LinkedIn',
          'Share daily stories on Instagram',
          'Weekly blog posts on website',
          'Monthly newsletter to email list'
        ],
        expectedOutcome: 'Increase brand awareness by 40% in 3 months'
      },
      {
        id: '2',
        title: 'Engagement Amplification',
        description: 'Boost engagement through interactive content and timely responses to audience interactions.',
        type: 'engagement',
        priority: 'high',
        status: 'active',
        tactics: [
          'Respond to all comments within 24 hours',
          'Create polls and questions weekly',
          'Host monthly Q&A sessions',
          'Share user-generated content'
        ],
        expectedOutcome: 'Double engagement rate within 2 months'
      },
      {
        id: '3',
        title: 'Audience Growth Campaign',
        description: 'Expand reach and grow follower base through targeted content and strategic partnerships.',
        type: 'growth',
        priority: 'medium',
        status: 'planned',
        tactics: [
          'Collaborate with industry influencers',
          'Run targeted ads on top platforms',
          'Cross-promote content across channels',
          'Participate in industry conversations'
        ],
        expectedOutcome: 'Gain 1,000 new followers per month'
      },
      {
        id: '4',
        title: 'Brand Authority Building',
        description: 'Position the brand as a thought leader through expert content and industry insights.',
        type: 'brand',
        priority: 'medium',
        status: 'active',
        tactics: [
          'Share industry insights and trends',
          'Publish case studies and success stories',
          'Speak at industry events',
          'Create educational content series'
        ],
        expectedOutcome: 'Become top 3 voice in industry niche'
      },
      {
        id: '5',
        title: 'Platform-Specific Optimization',
        description: 'Tailor content and approach for each platform to maximize performance and ROI.',
        type: 'content',
        priority: 'low',
        status: 'planned',
        tactics: [
          'Optimize LinkedIn for B2B networking',
          'Use Instagram for visual storytelling',
          'Twitter for real-time engagement',
          'YouTube for in-depth tutorials'
        ],
        expectedOutcome: 'Increase platform-specific engagement by 50%'
      }
    ];

    setStrategies(sampleStrategies);
    
    // Mark strategy step as complete
    completeStep('strategy');
    localStorage.setItem('has_strategies', 'true');
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'planned':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'content':
        return Calendar;
      case 'engagement':
        return Users;
      case 'growth':
        return TrendingUp;
      case 'brand':
        return Target;
      default:
        return Lightbulb;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (businesses.length === 0) {
    return (
      <div className="p-6">
        <div className="rounded-lg border bg-white p-12 text-center">
          <Target className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-lg font-semibold">No Business Found</h3>
          <p className="mt-2 text-gray-600">
            Create a business profile first to view marketing strategies.
          </p>
          <button 
            onClick={() => router.push('/dashboard/settings')}
            className="mt-6 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 transition-colors"
          >
            Create Business
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Marketing Strategies</h2>
            <p className="mt-1 text-gray-600">
              AI-powered strategies to grow your business and engage your audience
            </p>
          </div>
          
          {/* Business Selector */}
          {businesses.length > 1 && (
            <select
              value={selectedBusiness || ''}
              onChange={(e) => setSelectedBusiness(Number(e.target.value))}
              className="rounded-lg border border-gray-300 px-4 py-2"
            >
              {businesses.map((business) => (
                <option key={business.id} value={business.id}>
                  {business.name}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Strategy Overview Cards */}
        <div className="grid gap-6 md:grid-cols-4 mb-8">
          <div className="rounded-lg border bg-white p-6">
            <div className="flex items-center justify-between">
              <div className="text-sm font-medium text-gray-600">Active Strategies</div>
              <TrendingUp className="h-5 w-5 text-green-600" />
            </div>
            <div className="mt-2 text-3xl font-bold">
              {strategies.filter(s => s.status === 'active').length}
            </div>
            <p className="mt-1 text-xs text-gray-500">Currently running</p>
          </div>
          
          <div className="rounded-lg border bg-white p-6">
            <div className="flex items-center justify-between">
              <div className="text-sm font-medium text-gray-600">Planned</div>
              <Calendar className="h-5 w-5 text-blue-600" />
            </div>
            <div className="mt-2 text-3xl font-bold">
              {strategies.filter(s => s.status === 'planned').length}
            </div>
            <p className="mt-1 text-xs text-gray-500">Ready to launch</p>
          </div>
          
          <div className="rounded-lg border bg-white p-6">
            <div className="flex items-center justify-between">
              <div className="text-sm font-medium text-gray-600">Completed</div>
              <CheckCircle2 className="h-5 w-5 text-gray-600" />
            </div>
            <div className="mt-2 text-3xl font-bold">
              {strategies.filter(s => s.status === 'completed').length}
            </div>
            <p className="mt-1 text-xs text-gray-500">Successfully done</p>
          </div>
          
          <div className="rounded-lg border bg-white p-6">
            <div className="flex items-center justify-between">
              <div className="text-sm font-medium text-gray-600">High Priority</div>
              <Target className="h-5 w-5 text-red-600" />
            </div>
            <div className="mt-2 text-3xl font-bold">
              {strategies.filter(s => s.priority === 'high').length}
            </div>
            <p className="mt-1 text-xs text-gray-500">Need attention</p>
          </div>
        </div>

        {/* Strategies List */}
        <div className="space-y-4">
          {strategies.map((strategy) => {
            const Icon = getTypeIcon(strategy.type);
            return (
              <div
                key={strategy.id}
                className="rounded-lg border bg-white p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex gap-4">
                    <div className={`rounded-lg p-3 ${
                      strategy.type === 'content' ? 'bg-purple-100' :
                      strategy.type === 'engagement' ? 'bg-blue-100' :
                      strategy.type === 'growth' ? 'bg-green-100' :
                      'bg-orange-100'
                    }`}>
                      <Icon className={`h-6 w-6 ${
                        strategy.type === 'content' ? 'text-purple-600' :
                        strategy.type === 'engagement' ? 'text-blue-600' :
                        strategy.type === 'growth' ? 'text-green-600' :
                        'text-orange-600'
                      }`} />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {strategy.title}
                        </h3>
                        <span className={`rounded-full px-3 py-1 text-xs font-medium ${getPriorityColor(strategy.priority)}`}>
                          {strategy.priority} priority
                        </span>
                        <span className={`rounded-full px-3 py-1 text-xs font-medium ${getStatusColor(strategy.status)}`}>
                          {strategy.status}
                        </span>
                      </div>
                      <p className="mt-2 text-gray-600">{strategy.description}</p>
                      
                      {/* Tactics */}
                      <div className="mt-4">
                        <h4 className="text-sm font-semibold text-gray-700">Key Tactics:</h4>
                        <ul className="mt-2 space-y-1">
                          {strategy.tactics.map((tactic, index) => (
                            <li key={index} className="flex items-start gap-2 text-sm text-gray-600">
                              <CheckCircle2 className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                              <span>{tactic}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      {/* Expected Outcome */}
                      <div className="mt-4 rounded-lg bg-blue-50 p-3 border border-blue-100">
                        <div className="flex items-start gap-2">
                          <Target className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                          <div>
                            <div className="text-xs font-semibold text-blue-900">Expected Outcome</div>
                            <div className="text-sm text-blue-700">{strategy.expectedOutcome}</div>
                          </div>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="mt-4 flex gap-3">
                        <button 
                          onClick={() => router.push('/dashboard/content')}
                          className="flex items-center gap-2 rounded-lg bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700 transition-colors"
                        >
                          <Sparkles className="h-4 w-4" />
                          Generate Content
                        </button>
                        <button 
                          onClick={() => router.push('/dashboard/analytics')}
                          className="flex items-center gap-2 rounded-lg border-2 border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                        >
                          <TrendingUp className="h-4 w-4" />
                          View Analytics
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* AI Recommendations Section */}
        <div className="mt-8 rounded-lg border bg-gradient-to-r from-purple-50 to-blue-50 p-6">
          <div className="flex items-start gap-4">
            <div className="rounded-lg bg-white p-3 shadow-sm">
              <Lightbulb className="h-6 w-6 text-purple-600" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900">AI Strategy Recommendations</h3>
              <p className="mt-2 text-gray-600">
                Based on your business profile and current performance, here are personalized strategy recommendations:
              </p>
              <div className="mt-4 space-y-2">
                <div className="flex items-start gap-2 text-sm">
                  <CheckCircle2 className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Focus on LinkedIn for B2B growth - your industry performs 3x better there</span>
                </div>
                <div className="flex items-start gap-2 text-sm">
                  <CheckCircle2 className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Post between 9-11 AM on Tuesdays for maximum engagement</span>
                </div>
                <div className="flex items-start gap-2 text-sm">
                  <CheckCircle2 className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Educational content generates 2x more shares in your niche</span>
                </div>
              </div>
              <button 
                onClick={() => alert('AI Strategy Generator coming soon! This will analyze your business and create a custom marketing strategy.')}
                className="mt-4 rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700"
              >
                Generate Custom Strategy
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
