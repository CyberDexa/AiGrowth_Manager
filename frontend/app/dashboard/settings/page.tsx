'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { Settings, User, Building2, Bell, Lock, Palette, Trash2, Save, CheckCircle2, Share2 } from 'lucide-react';
import SocialConnections from './components/SocialConnections';

interface Business {
  id: number;
  name: string;
  industry?: string;
  target_audience?: string;
  marketing_goals?: string;
  description?: string;
  company_size?: string;
}

export default function SettingsPage() {
  const { getToken } = useAuth();
  const [activeTab, setActiveTab] = useState<'profile' | 'business' | 'social' | 'notifications' | 'preferences' | 'security'>('business');
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [selectedBusiness, setSelectedBusiness] = useState<Business | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  // Business form state
  const [businessForm, setBusinessForm] = useState({
    name: '',
    industry: '',
    target_audience: '',
    goals: '',
    website: '',
  });

  // Notification settings
  const [notifications, setNotifications] = useState({
    emailDigest: true,
    contentReminders: true,
    performanceAlerts: true,
    weeklyReports: true,
    aiSuggestions: true,
  });

  // Preferences
  const [preferences, setPreferences] = useState({
    timezone: 'America/New_York',
    dateFormat: 'MM/DD/YYYY',
    defaultPlatform: 'linkedin',
    autoPublish: false,
    aiAssistanceLevel: 'medium',
  });

  useEffect(() => {
    loadBusinesses();
  }, []);

  useEffect(() => {
    if (selectedBusiness) {
      setBusinessForm({
        name: selectedBusiness.name || '',
        industry: selectedBusiness.industry || '',
        target_audience: selectedBusiness.target_audience || '',
        goals: selectedBusiness.marketing_goals || '',
        website: selectedBusiness.description || '',
      });
    }
  }, [selectedBusiness]);

  const loadBusinesses = async () => {
    try {
      const token = await getToken();
      
      // Debug: Log token status
      console.log('Token exists:', !!token);
      console.log('API URL:', process.env.NEXT_PUBLIC_API_URL);
      
      if (!token) {
        console.error('No authentication token available');
        setLoading(false);
        return;
      }
      
      const url = `${process.env.NEXT_PUBLIC_API_URL}/api/v1/businesses/`;
      console.log('Fetching from:', url);
      
      // Add timeout for Render cold starts
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout
      
      const response = await fetch(url, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      console.log('Response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        setBusinesses(data);
        if (data.length > 0) {
          setSelectedBusiness(data[0]);
        }
      } else {
        const errorData = await response.text();
        console.error('API Error:', response.status, errorData);
      }
    } catch (error) {
      console.error('Failed to load businesses:', error);
      if (error instanceof Error) {
        console.error('Error details:', {
          message: error.message,
          name: error.name,
          stack: error.stack
        });
        
        // Show user-friendly error for timeout
        if (error.name === 'AbortError') {
          alert('⏰ Backend service is starting up (cold start). Please wait 30 seconds and refresh the page.');
        } else if (error.message === 'Failed to fetch') {
          alert('❌ Cannot connect to backend. Please check:\n1. Backend is running at ' + process.env.NEXT_PUBLIC_API_URL + '\n2. Check browser console for CORS errors\n3. Try refreshing in 30 seconds (cold start)');
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSaveBusiness = async () => {
    // Validate required fields
    if (!businessForm.name.trim()) {
      alert('Please enter a business name');
      return;
    }

    setSaving(true);
    setSaved(false);
    try {
      const token = await getToken();
      const goalsString = businessForm.goals.trim();

      const isCreating = !selectedBusiness || !selectedBusiness.id;
      const url = isCreating
        ? `${process.env.NEXT_PUBLIC_API_URL}/api/v1/businesses/`
        : `${process.env.NEXT_PUBLIC_API_URL}/api/v1/businesses/${selectedBusiness.id}`;
      
      const method = isCreating ? 'POST' : 'PUT';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: businessForm.name,
          industry: businessForm.industry || null,
          target_audience: businessForm.target_audience || null,
          marketing_goals: goalsString || null,
          description: businessForm.website || null,  // Using website field for description temporarily
        }),
      });

      if (response.ok) {
        setSaved(true);
        await loadBusinesses();
        setTimeout(() => setSaved(false), 3000);
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('Failed to save:', response.statusText, errorData);
        alert(`Failed to save business: ${errorData.detail || response.statusText}`);
      }
    } catch (error) {
      console.error('Failed to save business:', error);
      alert('Failed to save business. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const tabs = [
    { id: 'business', label: 'Business Profile', icon: Building2 },
    { id: 'social', label: 'Social Accounts', icon: Share2 },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'preferences', label: 'Preferences', icon: Palette },
    { id: 'security', label: 'Security', icon: Lock },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
          <p className="mt-1 text-gray-600">
            Manage your account settings and preferences
          </p>
        </div>

        <div className="flex gap-6">
          {/* Sidebar Navigation */}
          <div className="w-64 flex-shrink-0">
            <nav className="space-y-1">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`flex w-full items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition-colors ${
                      activeTab === tab.id
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    {tab.label}
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {/* Business Profile Tab */}
            {activeTab === 'business' && (
              <div className="rounded-lg border bg-white p-6">
                <div className="mb-6">
                  <h3 className="text-lg font-semibold">Business Profile</h3>
                  <p className="mt-1 text-sm text-gray-600">
                    Update your business information to get better AI recommendations
                  </p>
                </div>

                {businesses.length > 1 && (
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Select Business
                    </label>
                    <select
                      value={selectedBusiness?.id || ''}
                      onChange={(e) => {
                        const business = businesses.find(b => b.id === Number(e.target.value));
                        setSelectedBusiness(business || null);
                      }}
                      className="w-full rounded-lg border border-gray-300 px-4 py-2"
                    >
                      {businesses.map((business) => (
                        <option key={business.id} value={business.id}>
                          {business.name}
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Business Name
                    </label>
                    <input
                      type="text"
                      value={businessForm.name}
                      onChange={(e) => setBusinessForm({ ...businessForm, name: e.target.value })}
                      className="w-full rounded-lg border border-gray-300 px-4 py-2"
                      placeholder="My Awesome Business"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Industry
                    </label>
                    <input
                      type="text"
                      value={businessForm.industry}
                      onChange={(e) => setBusinessForm({ ...businessForm, industry: e.target.value })}
                      className="w-full rounded-lg border border-gray-300 px-4 py-2"
                      placeholder="e.g., Technology, Healthcare, Education"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Target Audience
                    </label>
                    <textarea
                      value={businessForm.target_audience}
                      onChange={(e) => setBusinessForm({ ...businessForm, target_audience: e.target.value })}
                      className="w-full rounded-lg border border-gray-300 px-4 py-2"
                      rows={3}
                      placeholder="Describe your ideal customer..."
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Business Goals (comma-separated)
                    </label>
                    <textarea
                      value={businessForm.goals}
                      onChange={(e) => setBusinessForm({ ...businessForm, goals: e.target.value })}
                      className="w-full rounded-lg border border-gray-300 px-4 py-2"
                      rows={2}
                      placeholder="Increase brand awareness, Generate leads, Build community"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Website
                    </label>
                    <input
                      type="url"
                      value={businessForm.website}
                      onChange={(e) => setBusinessForm({ ...businessForm, website: e.target.value })}
                      className="w-full rounded-lg border border-gray-300 px-4 py-2"
                      placeholder="https://yourwebsite.com"
                    />
                  </div>

                  <div className="flex items-center gap-3 pt-4">
                    <button
                      onClick={handleSaveBusiness}
                      disabled={saving || loading || !businessForm.name.trim()}
                      className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {saving ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          Saving...
                        </>
                      ) : (
                        <>
                          <Save className="h-4 w-4" />
                          {selectedBusiness ? 'Save Changes' : 'Create Business'}
                        </>
                      )}
                    </button>
                    {saved && (
                      <div className="flex items-center gap-2 text-green-600">
                        <CheckCircle2 className="h-5 w-5" />
                        <span className="text-sm font-medium">
                          {selectedBusiness ? 'Saved successfully!' : 'Business created successfully!'}
                        </span>
                      </div>
                    )}
                    {!loading && !selectedBusiness && (
                      <div className="text-sm text-blue-600 font-medium">
                        Fill in the form below to create your first business
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Social Accounts Tab */}
            {activeTab === 'social' && (
              <div className="rounded-lg border bg-white p-6">
                <SocialConnections businessId={selectedBusiness?.id || null} />
              </div>
            )}

            {/* Notifications Tab */}
            {activeTab === 'notifications' && (
              <div className="rounded-lg border bg-white p-6">
                <div className="mb-6">
                  <h3 className="text-lg font-semibold">Notification Preferences</h3>
                  <p className="mt-1 text-sm text-gray-600">
                    Choose how you want to be notified about your content and performance
                  </p>
                </div>

                <div className="space-y-4">
                  {Object.entries({
                    emailDigest: 'Daily Email Digest',
                    contentReminders: 'Content Creation Reminders',
                    performanceAlerts: 'Performance Alerts',
                    weeklyReports: 'Weekly Performance Reports',
                    aiSuggestions: 'AI Strategy Suggestions',
                  }).map(([key, label]) => (
                    <label key={key} className="flex items-center justify-between rounded-lg border p-4 hover:bg-gray-50 cursor-pointer">
                      <div>
                        <div className="font-medium text-gray-900">{label}</div>
                        <div className="text-sm text-gray-600">
                          {key === 'emailDigest' && 'Get a daily summary of your content performance'}
                          {key === 'contentReminders' && 'Reminders to create and publish content'}
                          {key === 'performanceAlerts' && 'Alerts when content performs exceptionally well or poorly'}
                          {key === 'weeklyReports' && 'Comprehensive weekly analytics reports'}
                          {key === 'aiSuggestions' && 'Receive AI-powered content and strategy suggestions'}
                        </div>
                      </div>
                      <input
                        type="checkbox"
                        checked={notifications[key as keyof typeof notifications]}
                        onChange={(e) => setNotifications({ ...notifications, [key]: e.target.checked })}
                        className="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                    </label>
                  ))}
                </div>

                <div className="flex items-center gap-3 pt-6">
                  <button className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700">
                    <Save className="h-4 w-4" />
                    Save Preferences
                  </button>
                </div>
              </div>
            )}

            {/* Preferences Tab */}
            {activeTab === 'preferences' && (
              <div className="rounded-lg border bg-white p-6">
                <div className="mb-6">
                  <h3 className="text-lg font-semibold">General Preferences</h3>
                  <p className="mt-1 text-sm text-gray-600">
                    Customize your experience with AI Growth Manager
                  </p>
                </div>

                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Timezone
                    </label>
                    <select
                      value={preferences.timezone}
                      onChange={(e) => setPreferences({ ...preferences, timezone: e.target.value })}
                      className="w-full rounded-lg border border-gray-300 px-4 py-2"
                    >
                      <option value="America/New_York">Eastern Time (ET)</option>
                      <option value="America/Chicago">Central Time (CT)</option>
                      <option value="America/Denver">Mountain Time (MT)</option>
                      <option value="America/Los_Angeles">Pacific Time (PT)</option>
                      <option value="Europe/London">London (GMT)</option>
                      <option value="Europe/Paris">Paris (CET)</option>
                      <option value="Asia/Tokyo">Tokyo (JST)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Date Format
                    </label>
                    <select
                      value={preferences.dateFormat}
                      onChange={(e) => setPreferences({ ...preferences, dateFormat: e.target.value })}
                      className="w-full rounded-lg border border-gray-300 px-4 py-2"
                    >
                      <option value="MM/DD/YYYY">MM/DD/YYYY (US)</option>
                      <option value="DD/MM/YYYY">DD/MM/YYYY (European)</option>
                      <option value="YYYY-MM-DD">YYYY-MM-DD (ISO)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Default Platform
                    </label>
                    <select
                      value={preferences.defaultPlatform}
                      onChange={(e) => setPreferences({ ...preferences, defaultPlatform: e.target.value })}
                      className="w-full rounded-lg border border-gray-300 px-4 py-2"
                    >
                      <option value="linkedin">LinkedIn</option>
                      <option value="twitter">Twitter/X</option>
                      <option value="facebook">Facebook</option>
                      <option value="instagram">Instagram</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      AI Assistance Level
                    </label>
                    <select
                      value={preferences.aiAssistanceLevel}
                      onChange={(e) => setPreferences({ ...preferences, aiAssistanceLevel: e.target.value })}
                      className="w-full rounded-lg border border-gray-300 px-4 py-2"
                    >
                      <option value="low">Low - Minimal suggestions</option>
                      <option value="medium">Medium - Balanced assistance</option>
                      <option value="high">High - Maximum AI guidance</option>
                    </select>
                    <p className="mt-1 text-sm text-gray-600">
                      Control how much AI assistance you receive when creating content
                    </p>
                  </div>

                  <label className="flex items-center justify-between rounded-lg border p-4 hover:bg-gray-50 cursor-pointer">
                    <div>
                      <div className="font-medium text-gray-900">Auto-Publish Approved Content</div>
                      <div className="text-sm text-gray-600">
                        Automatically publish content after your approval
                      </div>
                    </div>
                    <input
                      type="checkbox"
                      checked={preferences.autoPublish}
                      onChange={(e) => setPreferences({ ...preferences, autoPublish: e.target.checked })}
                      className="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                  </label>
                </div>

                <div className="flex items-center gap-3 pt-6">
                  <button className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700">
                    <Save className="h-4 w-4" />
                    Save Preferences
                  </button>
                </div>
              </div>
            )}

            {/* Security Tab */}
            {activeTab === 'security' && (
              <div className="space-y-6">
                <div className="rounded-lg border bg-white p-6">
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold">Account Security</h3>
                    <p className="mt-1 text-sm text-gray-600">
                      Manage your account security settings
                    </p>
                  </div>

                  <div className="space-y-4">
                    <div className="rounded-lg border p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-gray-900">Password</div>
                          <div className="text-sm text-gray-600">Last changed 30 days ago</div>
                        </div>
                        <button className="rounded-lg border px-4 py-2 text-sm font-medium hover:bg-gray-50">
                          Change Password
                        </button>
                      </div>
                    </div>

                    <div className="rounded-lg border p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-gray-900">Two-Factor Authentication</div>
                          <div className="text-sm text-gray-600">Add an extra layer of security</div>
                        </div>
                        <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
                          Enable 2FA
                        </button>
                      </div>
                    </div>

                    <div className="rounded-lg border p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-gray-900">Active Sessions</div>
                          <div className="text-sm text-gray-600">Manage your active login sessions</div>
                        </div>
                        <button className="rounded-lg border px-4 py-2 text-sm font-medium hover:bg-gray-50">
                          View Sessions
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="rounded-lg border border-red-200 bg-red-50 p-6">
                  <div className="mb-4">
                    <h3 className="text-lg font-semibold text-red-900">Danger Zone</h3>
                    <p className="mt-1 text-sm text-red-700">
                      Irreversible and destructive actions
                    </p>
                  </div>

                  <div className="space-y-3">
                    <div className="rounded-lg bg-white border border-red-200 p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-gray-900">Delete All Content</div>
                          <div className="text-sm text-gray-600">
                            Permanently delete all your generated content
                          </div>
                        </div>
                        <button className="rounded-lg border border-red-300 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-50">
                          Delete Content
                        </button>
                      </div>
                    </div>

                    <div className="rounded-lg bg-white border border-red-200 p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-gray-900">Delete Account</div>
                          <div className="text-sm text-gray-600">
                            Permanently delete your account and all data
                          </div>
                        </div>
                        <button className="flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700">
                          <Trash2 className="h-4 w-4" />
                          Delete Account
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
