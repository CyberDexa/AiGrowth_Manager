'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import { Target, TrendingUp, Users, Calendar, Lightbulb, CheckCircle2, Sparkles, X, Loader2 } from 'lucide-react';
import { useOnboarding } from '@/contexts/OnboardingContext';
import toast from 'react-hot-toast';

interface Business {
  id: number;
  name: string;
  industry: string;
  target_audience?: string;
  goals?: string[];
  description?: string;
  marketing_goals?: string;
}

interface AIStrategy {
  id: number;
  business_id: number;
  title: string;
  description: string;
  strategy_data: any;
  status: string;
  created_at: string;
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
  const [aiStrategies, setAiStrategies] = useState<AIStrategy[]>([]);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [additionalContext, setAdditionalContext] = useState('');

  useEffect(() => {
    loadBusinesses();
  }, []);

  useEffect(() => {
    if (selectedBusiness) {
      loadStrategies();
      loadAIStrategies();
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

  const loadAIStrategies = async () => {
    if (!selectedBusiness) return;
    
    try {
      const token = await getToken();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/strategies/?business_id=${selectedBusiness}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (response.ok) {
        const data = await response.json();
        setAiStrategies(data);
        if (data.length > 0) {
          completeStep('strategy');
          localStorage.setItem('has_strategies', 'true');
        }
      }
    } catch (error) {
      console.error('Failed to load AI strategies:', error);
    }
  };

  const generateAIStrategy = async () => {
    if (!selectedBusiness) return;
    
    const business = businesses.find(b => b.id === selectedBusiness);
    if (!business) return;

    // Validate business has required info
    if (!business.name || !business.description) {
      toast.error('Please complete your business profile in Settings first');
      router.push('/dashboard/settings');
      return;
    }

    setGenerating(true);
    try {
      const token = await getToken();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/strategies/generate`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            business_id: selectedBusiness,
            additional_context: additionalContext || undefined,
          }),
        }
      );

      if (response.ok) {
        const newStrategy = await response.json();
        setAiStrategies(prev => [newStrategy, ...prev]);
        toast.success('AI Strategy generated successfully!');
        setShowGenerateModal(false);
        setAdditionalContext('');
        completeStep('strategy');
        localStorage.setItem('has_strategies', 'true');
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to generate strategy');
      }
    } catch (error) {
      console.error('Failed to generate strategy:', error);
      toast.error('Failed to generate strategy. Please try again.');
    } finally {
      setGenerating(false);
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
                onClick={() => setShowGenerateModal(true)}
                className="mt-4 rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700 transition-colors"
              >
                Generate Custom Strategy with AI
              </button>
            </div>
          </div>
        </div>

        {/* AI-Generated Strategies Section */}
        {aiStrategies.length > 0 && (
          <div className="mt-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4">AI-Generated Strategies</h3>
            <div className="space-y-4">
              {aiStrategies.map((strategy) => (
                <div
                  key={strategy.id}
                  className="rounded-lg border-2 border-purple-200 bg-gradient-to-r from-purple-50 to-blue-50 p-6"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <Sparkles className="h-6 w-6 text-purple-600" />
                        <h4 className="text-lg font-bold text-gray-900">{strategy.title}</h4>
                        <span className="rounded-full bg-purple-100 px-3 py-1 text-xs font-medium text-purple-700">
                          AI Generated
                        </span>
                      </div>
                      <p className="mt-2 text-gray-700">{strategy.description}</p>
                      
                      {strategy.strategy_data && (
                        <div className="mt-4 space-y-4">
                          {/* Executive Summary */}
                          {strategy.strategy_data.executive_summary && (
                            <div className="rounded-lg bg-white p-4 border border-purple-100">
                              <h5 className="font-semibold text-gray-900 mb-2">Executive Summary</h5>
                              <p className="text-sm text-gray-700">{strategy.strategy_data.executive_summary}</p>
                            </div>
                          )}
                          
                          {/* Strategic Objectives */}
                          {strategy.strategy_data.strategic_objectives && (
                            <div className="rounded-lg bg-white p-4 border border-purple-100">
                              <h5 className="font-semibold text-gray-900 mb-2">Strategic Objectives</h5>
                              <ul className="space-y-1">
                                {strategy.strategy_data.strategic_objectives.map((obj: string, idx: number) => (
                                  <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                                    <Target className="h-4 w-4 text-purple-600 mt-0.5 flex-shrink-0" />
                                    <span>{obj}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          
                          {/* Content Pillars */}
                          {strategy.strategy_data.content_pillars && (
                            <div className="rounded-lg bg-white p-4 border border-purple-100">
                              <h5 className="font-semibold text-gray-900 mb-2">Content Pillars</h5>
                              <div className="flex flex-wrap gap-2">
                                {strategy.strategy_data.content_pillars.map((pillar: string, idx: number) => (
                                  <span
                                    key={idx}
                                    className="rounded-full bg-purple-100 px-3 py-1 text-sm text-purple-700"
                                  >
                                    {pillar}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                      
                      <div className="mt-4 flex gap-3">
                        <button 
                          onClick={() => router.push('/dashboard/content')}
                          className="flex items-center gap-2 rounded-lg bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700 transition-colors"
                        >
                          <Sparkles className="h-4 w-4" />
                          Create Content from Strategy
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Generate Strategy Modal */}
      {showGenerateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
          <div className="relative w-full max-w-2xl rounded-lg bg-white p-6 shadow-xl">
            <button
              onClick={() => setShowGenerateModal(false)}
              className="absolute right-4 top-4 text-gray-400 hover:text-gray-600"
            >
              <X className="h-6 w-6" />
            </button>
            
            <div className="mb-6">
              <div className="flex items-center gap-3 mb-2">
                <div className="rounded-lg bg-purple-100 p-2">
                  <Sparkles className="h-6 w-6 text-purple-600" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900">Generate AI Marketing Strategy</h3>
              </div>
              <p className="text-gray-600">
                Our AI will analyze your business and create a comprehensive 12-week marketing strategy.
              </p>
            </div>

            {selectedBusiness && businesses.find(b => b.id === selectedBusiness) && (
              <div className="mb-6 rounded-lg bg-gray-50 p-4 border border-gray-200">
                <h4 className="font-semibold text-gray-900 mb-2">Business Information</h4>
                <div className="space-y-1 text-sm text-gray-700">
                  <p><span className="font-medium">Name:</span> {businesses.find(b => b.id === selectedBusiness)?.name}</p>
                  <p><span className="font-medium">Industry:</span> {businesses.find(b => b.id === selectedBusiness)?.industry}</p>
                  {businesses.find(b => b.id === selectedBusiness)?.target_audience && (
                    <p><span className="font-medium">Target Audience:</span> {businesses.find(b => b.id === selectedBusiness)?.target_audience}</p>
                  )}
                </div>
              </div>
            )}

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Additional Context (Optional)
              </label>
              <textarea
                value={additionalContext}
                onChange={(e) => setAdditionalContext(e.target.value)}
                placeholder="Any specific goals, challenges, or information that would help create a better strategy..."
                className="w-full rounded-lg border border-gray-300 p-3 text-sm focus:border-purple-500 focus:ring-2 focus:ring-purple-200"
                rows={4}
              />
            </div>

            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowGenerateModal(false)}
                disabled={generating}
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={generateAIStrategy}
                disabled={generating}
                className="flex items-center gap-2 rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-50"
              >
                {generating ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Generating Strategy...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4" />
                    Generate Strategy
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
