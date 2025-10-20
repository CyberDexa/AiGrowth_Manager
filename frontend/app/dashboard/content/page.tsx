'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@clerk/nextjs';
import api from '@/lib/api';
import { Pencil, Trash2, Calendar, Copy, CheckCircle, Send, BookmarkPlus, Check } from 'lucide-react';
import CalendarView from '@/components/CalendarView';
import PublishContentModal from '../strategies/components/PublishContentModal';
import { useOnboarding } from '@/contexts/OnboardingContext';

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

export default function ContentPage() {
  const { getToken } = useAuth();
  const { completeStep } = useOnboarding();
  const [businesses, setBusinesses] = useState<any[]>([]);
  const [selectedBusiness, setSelectedBusiness] = useState<number | null>(null);
  const [content, setContent] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'generate' | 'library' | 'calendar'>('generate');

  // Form state for content generation
  const [platform, setPlatform] = useState('linkedin');
  const [contentType, setContentType] = useState('post');
  const [tone, setTone] = useState('professional');
  const [topic, setTopic] = useState('');
  const [numPosts, setNumPosts] = useState(1);
  const [generatedContent, setGeneratedContent] = useState<any[]>([]);

  // Content Library state
  const [savingContentId, setSavingContentId] = useState<number | null>(null);
  const [savedContent, setSavedContent] = useState<Set<number>>(new Set());

  // Edit modal state
  const [editingContent, setEditingContent] = useState<ContentItem | null>(null);
  const [editText, setEditText] = useState('');
  const [editHashtags, setEditHashtags] = useState('');
  const [editScheduledFor, setEditScheduledFor] = useState('');
  const [editStatus, setEditStatus] = useState('draft');
  const [saving, setSaving] = useState(false);

  // Publish modal state
  const [publishModalOpen, setPublishModalOpen] = useState(false);
  const [contentToPublish, setContentToPublish] = useState<string>('');

  useEffect(() => {
    loadBusinesses();
  }, []);

  useEffect(() => {
    if (selectedBusiness) {
      loadContent();
    }
  }, [selectedBusiness]);

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

  const loadContent = async () => {
    if (!selectedBusiness) return;
    
    try {
      setLoading(true);
      const token = await getToken();
      if (!token) return;
      
      const data = await api.content.list({ business_id: selectedBusiness }, token);
      setContent(data);
    } catch (err) {
      console.error('Failed to load content:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateContent = async () => {
    if (!selectedBusiness) {
      setError('Please select a business first');
      return;
    }

    try {
      setGenerating(true);
      setError(null);
      const token = await getToken();
      if (!token) {
        setError('Authentication required');
        return;
      }

      const result = await api.content.generate(
        {
          business_id: selectedBusiness,
          platform,
          content_type: contentType,
          tone,
          topic: topic || undefined,
          num_posts: numPosts,
        },
        token
      );

      if (result.success) {
        setGeneratedContent(result.content);
        setActiveTab('library');
        
        // Mark content step as complete
        completeStep('content');
        localStorage.setItem('has_content', 'true');
      } else {
        setError('Failed to generate content');
      }
    } catch (err) {
      console.error('Failed to generate content:', err);
      setError(err instanceof Error ? err.message : 'Failed to generate content');
    } finally {
      setGenerating(false);
    }
  };

  const handleSaveContent = async (contentData: any, scheduledFor?: string, index?: number) => {
    try {
      const token = await getToken();
      if (!token || !selectedBusiness) return;

      const result = await api.content.create(
        {
          business_id: selectedBusiness,
          platform: contentData.platform || platform,
          content_type: contentType,
          tone,
          text: contentData.text,
          hashtags: contentData.hashtags,
          scheduled_for: scheduledFor,
        },
        token
      );

      // Update generatedContent with the ID from saved content
      if (result && result.id !== undefined && index !== undefined) {
        setGeneratedContent(prev => 
          prev.map((item, i) => i === index ? { ...item, id: result.id } : item)
        );
      }

      // Reload content list
      await loadContent();
    } catch (err) {
      console.error('Failed to save content:', err);
      setError('Failed to save content');
    }
  };

  const saveToLibrary = async (contentId: number) => {
    try {
      setSavingContentId(contentId);
      const token = await getToken();
      if (!token) return;

      const response = await fetch('/api/v1/content-library/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          source: 'content',
          item_id: contentId,
        }),
      });

      if (response.ok) {
        setSavedContent(prev => new Set([...prev, contentId]));
      } else {
        console.error('Failed to save to library:', await response.text());
        setError('Failed to save to library');
      }
    } catch (err) {
      console.error('Failed to save to library:', err);
      setError('Failed to save to library');
    } finally {
      setSavingContentId(null);
    }
  };

  const handleEditContent = (item: ContentItem) => {
    setEditingContent(item);
    setEditText(item.text);
    setEditHashtags(item.hashtags || '');
    setEditScheduledFor(item.scheduled_for || '');
    setEditStatus(item.status);
  };

  const handleUpdateContent = async () => {
    if (!editingContent) return;

    try {
      setSaving(true);
      const token = await getToken();
      if (!token) return;

      await api.content.update(
        editingContent.id,
        {
          text: editText,
          hashtags: editHashtags || undefined,
          scheduled_for: editScheduledFor || undefined,
          status: editStatus,
        },
        token
      );

      // Reload content list
      await loadContent();
      setEditingContent(null);
      setError(null);
    } catch (err) {
      console.error('Failed to update content:', err);
      setError('Failed to update content');
    } finally {
      setSaving(false);
    }
  };

  const handlePublishContent = (item: ContentItem) => {
    const fullContent = item.text + (item.hashtags ? '\n\n' + item.hashtags : '');
    setContentToPublish(fullContent);
    setPublishModalOpen(true);
  };

  const handlePublishSuccess = () => {
    // Reload content to update status
    loadContent();
  };

  const handleDeleteContent = async (id: number) => {
    if (!confirm('Are you sure you want to delete this content?')) return;

    try {
      const token = await getToken();
      if (!token) return;

      await api.content.delete(id, token);
      await loadContent();
    } catch (err) {
      console.error('Failed to delete content:', err);
      setError('Failed to delete content');
    }
  };

  const handleCopyContent = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      // Could add a toast notification here
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div className="p-6">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Content Calendar</h1>
          <p className="mt-2 text-gray-600">Generate and manage your social media content with AI</p>
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
              className="rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
            >
              {businesses.map((business) => (
                <option key={business.id} value={business.id}>
                  {business.name}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Tabs */}
        <div className="mb-6 border-b border-gray-200">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('generate')}
              className={`border-b-2 pb-4 text-sm font-medium ${
                activeTab === 'generate'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
              }`}
            >
              ✨ Generate Content
            </button>
            <button
              onClick={() => setActiveTab('library')}
              className={`border-b-2 pb-4 text-sm font-medium ${
                activeTab === 'library'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
              }`}
            >
              📚 Content Library ({content.length})
            </button>
            <button
              onClick={() => setActiveTab('calendar')}
              className={`border-b-2 pb-4 text-sm font-medium ${
                activeTab === 'calendar'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
              }`}
            >
              📅 Calendar View
            </button>
          </nav>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 rounded-lg bg-red-50 p-4 text-red-800">
            {error}
          </div>
        )}

        {/* Tab Content */}
        {activeTab === 'generate' && (
          <div className="rounded-lg bg-white p-6 shadow">
            <h2 className="mb-4 text-xl font-semibold">Generate AI Content</h2>
            
            <div className="grid gap-6 md:grid-cols-2">
              {/* Platform */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Platform *
                </label>
                <select
                  value={platform}
                  onChange={(e) => setPlatform(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
                >
                  <option value="linkedin">LinkedIn</option>
                  <option value="twitter">Twitter</option>
                  <option value="facebook">Facebook</option>
                  <option value="instagram">Instagram</option>
                </select>
              </div>

              {/* Content Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Content Type
                </label>
                <select
                  value={contentType}
                  onChange={(e) => setContentType(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
                >
                  <option value="post">Post</option>
                  <option value="thread">Thread</option>
                  <option value="article">Article</option>
                  <option value="story">Story</option>
                </select>
              </div>

              {/* Tone */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tone
                </label>
                <select
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
                >
                  <option value="professional">Professional</option>
                  <option value="casual">Casual</option>
                  <option value="educational">Educational</option>
                  <option value="promotional">Promotional</option>
                  <option value="inspirational">Inspirational</option>
                </select>
              </div>

              {/* Number of Posts */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Posts
                </label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={numPosts}
                  onChange={(e) => setNumPosts(Number(e.target.value))}
                  className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
                />
              </div>

              {/* Topic */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Topic (Optional)
                </label>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g., AI automation in marketing"
                  className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
                />
              </div>
            </div>

            <button
              onClick={handleGenerateContent}
              disabled={generating || !selectedBusiness}
              className="mt-6 rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 disabled:bg-gray-400"
            >
              {generating ? '✨ Generating...' : '✨ Generate Content'}
            </button>

            {/* Generated Content Preview */}
            {generatedContent.length > 0 && (
              <div className="mt-8">
                <h3 className="mb-4 text-lg font-semibold">Generated Content</h3>
                <div className="space-y-4">
                  {generatedContent.map((item, index) => (
                    <div key={index} className="rounded-lg border border-gray-200 p-4">
                      <div className="mb-2 flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-500">
                          Post {index + 1}
                        </span>
                                                <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleSaveContent(item, undefined, index)}
                            className="rounded bg-blue-600 px-3 py-1 text-sm text-white hover:bg-blue-700"
                          >
                            Save as Draft
                          </button>
                          {item.id && savedContent.has(item.id) ? (
                            <span className="inline-flex items-center gap-1 rounded bg-green-100 px-3 py-1 text-sm font-medium text-green-800">
                              <Check className="h-3.5 w-3.5" />
                              Saved
                            </span>
                          ) : (
                            <button
                              onClick={() => item.id && saveToLibrary(item.id)}
                              disabled={!item.id || savingContentId === item.id}
                              className="inline-flex items-center gap-1 rounded bg-green-600 px-3 py-1 text-sm text-white hover:bg-green-700 disabled:bg-gray-400"
                            >
                              {savingContentId === item.id ? (
                                <>
                                  <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
                                  Saving...
                                </>
                              ) : (
                                <>
                                  <BookmarkPlus className="h-3.5 w-3.5" />
                                  Save to Library
                                </>
                              )}
                            </button>
                          )}
                        </div>
                      </div>
                      <p className="whitespace-pre-wrap text-gray-900">{item.text}</p>
                      {item.hashtags && (
                        <p className="mt-2 text-sm text-blue-600">{item.hashtags}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'library' && (
          <div className="rounded-lg bg-white p-6 shadow">
            <h2 className="mb-4 text-xl font-semibold">Content Library</h2>
            
            {loading ? (
              <div className="text-center text-gray-600">Loading...</div>
            ) : content.length === 0 ? (
              <div className="text-center text-gray-600">
                No content yet. Generate some content to get started!
              </div>
            ) : (
              <div className="space-y-4">
                {content.map((item) => (
                  <div key={item.id} className="rounded-lg border border-gray-200 p-4 hover:border-gray-300 transition-colors">
                    <div className="mb-3 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="rounded bg-blue-100 px-2 py-1 text-xs font-medium text-blue-800">
                          {item.platform}
                        </span>
                        <span className={`rounded px-2 py-1 text-xs font-medium ${
                          item.status === 'published' ? 'bg-green-100 text-green-800' :
                          item.status === 'scheduled' ? 'bg-purple-100 text-purple-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {item.status}
                        </span>
                        {item.scheduled_for && (
                          <span className="flex items-center gap-1 text-xs text-gray-600">
                            <Calendar className="h-3 w-3" />
                            {new Date(item.scheduled_for).toLocaleDateString()} {new Date(item.scheduled_for).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handlePublishContent(item)}
                          className="rounded px-3 py-2 text-white bg-blue-600 hover:bg-blue-700 flex items-center gap-2 text-sm font-medium"
                          title="Publish to social media"
                        >
                          <Send className="h-4 w-4" />
                          Publish
                        </button>
                        <button
                          onClick={() => handleCopyContent(item.text + (item.hashtags ? '\n\n' + item.hashtags : ''))}
                          className="rounded p-2 text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                          title="Copy to clipboard"
                        >
                          <Copy className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleEditContent(item)}
                          className="rounded p-2 text-blue-600 hover:bg-blue-50 hover:text-blue-700"
                          title="Edit content"
                        >
                          <Pencil className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteContent(item.id)}
                          className="rounded p-2 text-red-600 hover:bg-red-50 hover:text-red-700"
                          title="Delete content"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                    <p className="whitespace-pre-wrap text-gray-900 leading-relaxed">{item.text}</p>
                    {item.hashtags && (
                      <p className="mt-3 text-sm text-blue-600 font-medium">{item.hashtags}</p>
                    )}
                    <div className="mt-3 pt-3 border-t border-gray-100 text-xs text-gray-500">
                      Created: {new Date(item.created_at).toLocaleDateString()} at {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'calendar' && (
          <CalendarView content={content} onEditContent={handleEditContent} />
        )}

        {/* Edit Modal */}
        {editingContent && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
            <div className="w-full max-w-2xl rounded-lg bg-white p-6 shadow-xl">
              <div className="mb-4 flex items-center justify-between">
                <h3 className="text-xl font-semibold">Edit Content</h3>
                <button
                  onClick={() => setEditingContent(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                {/* Platform & Status badges */}
                <div className="flex items-center gap-2">
                  <span className="rounded bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800">
                    {editingContent.platform}
                  </span>
                  <span className="rounded bg-gray-100 px-3 py-1 text-sm font-medium text-gray-800">
                    {editingContent.content_type}
                  </span>
                </div>

                {/* Content Text */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Content Text
                  </label>
                  <textarea
                    value={editText}
                    onChange={(e) => setEditText(e.target.value)}
                    rows={8}
                    className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
                    placeholder="Enter your content..."
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    {editText.length} characters
                  </p>
                </div>

                {/* Hashtags */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Hashtags
                  </label>
                  <input
                    type="text"
                    value={editHashtags}
                    onChange={(e) => setEditHashtags(e.target.value)}
                    className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
                    placeholder="#marketing #AI #growth"
                  />
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  {/* Status */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Status
                    </label>
                    <select
                      value={editStatus}
                      onChange={(e) => setEditStatus(e.target.value)}
                      className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
                    >
                      <option value="draft">Draft</option>
                      <option value="scheduled">Scheduled</option>
                      <option value="published">Published</option>
                    </select>
                  </div>

                  {/* Schedule Date/Time */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Schedule For (Optional)
                    </label>
                    <input
                      type="datetime-local"
                      value={editScheduledFor}
                      onChange={(e) => setEditScheduledFor(e.target.value)}
                      className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
                    />
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex justify-end gap-3 pt-4">
                  <button
                    onClick={() => setEditingContent(null)}
                    className="rounded-lg border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleUpdateContent}
                    disabled={saving}
                    className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:bg-gray-400"
                  >
                    {saving ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Publish Content Modal */}
        <PublishContentModal
          isOpen={publishModalOpen}
          onClose={() => setPublishModalOpen(false)}
          content={contentToPublish}
          businessId={selectedBusiness}
          onSuccess={handlePublishSuccess}
        />
      </div>
    </div>
  );
}
