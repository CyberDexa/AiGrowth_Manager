'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@clerk/nextjs';
import { Plus, Pencil, Trash2, Copy, FileText, Sparkles } from 'lucide-react';
import HelpIcon from '@/components/HelpIcon';

interface Template {
  id: number;
  business_id: number;
  name: string;
  description?: string;
  category?: string;
  platform?: string;
  template_structure: string;
  placeholders?: Record<string, string>;
  is_public: boolean;
  use_count: number;
  created_at: string;
  updated_at: string;
}

const platformColors = {
  twitter: 'bg-blue-100 text-blue-800',
  linkedin: 'bg-blue-100 text-blue-900',
  facebook: 'bg-indigo-100 text-indigo-800',
  instagram: 'bg-pink-100 text-pink-800',
  null: 'bg-gray-100 text-gray-800',
};

const categoryColors = [
  'bg-purple-100 text-purple-800',
  'bg-green-100 text-green-800',
  'bg-yellow-100 text-yellow-800',
  'bg-red-100 text-red-800',
  'bg-teal-100 text-teal-800',
];

export default function TemplatesPage() {
  const { getToken } = useAuth();
  const [businesses, setBusinesses] = useState<any[]>([]);
  const [selectedBusiness, setSelectedBusiness] = useState<number | null>(null);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showUseModal, setShowUseModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  
  // Form states
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: '',
    platform: '',
    template_structure: '',
    placeholders: {} as Record<string, string>,
    is_public: false,
  });

  const [placeholderValues, setPlaceholderValues] = useState<Record<string, string>>({});
  const [generatedContent, setGeneratedContent] = useState<string>('');

  useEffect(() => {
    loadBusinesses();
  }, []);

  useEffect(() => {
    if (selectedBusiness) {
      loadTemplates();
    }
  }, [selectedBusiness]);

  const loadBusinesses = async () => {
    try {
      const token = await getToken();
      if (!token) return;

      const response = await fetch('/api/v1/businesses', {
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setBusinesses(data);
        
        // Auto-select first business
        if (data.length > 0 && !selectedBusiness) {
          setSelectedBusiness(data[0].id);
        }
      }
    } catch (err) {
      console.error('Failed to load businesses:', err);
    }
  };

  const loadTemplates = async () => {
    if (!selectedBusiness) return;

    try {
      setLoading(true);
      const token = await getToken();
      if (!token) return;

      const response = await fetch(
        `/api/v1/templates?business_id=${selectedBusiness}&include_public=true`,
        {
          headers: { 'Authorization': `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setTemplates(data.templates || []);
      }
    } catch (err) {
      console.error('Failed to load templates:', err);
      setError('Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTemplate = async () => {
    if (!selectedBusiness) return;

    try {
      const token = await getToken();
      if (!token) return;

      const response = await fetch('/api/v1/templates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...formData,
          business_id: selectedBusiness,
          platform: formData.platform || null,
        }),
      });

      if (response.ok) {
        setShowCreateModal(false);
        resetForm();
        loadTemplates();
      } else {
        setError('Failed to create template');
      }
    } catch (err) {
      console.error('Failed to create template:', err);
      setError('Failed to create template');
    }
  };

  const handleDeleteTemplate = async (templateId: number) => {
    if (!confirm('Are you sure you want to delete this template?')) return;

    try {
      const token = await getToken();
      if (!token) return;

      const response = await fetch(`/api/v1/templates/${templateId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.ok) {
        loadTemplates();
      }
    } catch (err) {
      console.error('Failed to delete template:', err);
      setError('Failed to delete template');
    }
  };

  const handleUseTemplate = async () => {
    if (!selectedTemplate) return;

    try {
      const token = await getToken();
      if (!token) return;

      const response = await fetch(`/api/v1/templates/${selectedTemplate.id}/use`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          placeholder_values: placeholderValues,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setGeneratedContent(data.content + (data.hashtags ? '\n\n' + data.hashtags : ''));
      }
    } catch (err) {
      console.error('Failed to use template:', err);
      setError('Failed to use template');
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      category: '',
      platform: '',
      template_structure: '',
      placeholders: {},
      is_public: false,
    });
  };

  const extractPlaceholders = (structure: string): string[] => {
    const regex = /\{\{(\w+)\}\}/g;
    const matches = structure.matchAll(regex);
    return Array.from(matches, m => m[1]);
  };

  const getCategoryColor = (index: number) => {
    return categoryColors[index % categoryColors.length];
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Content Templates</h1>
          <p className="text-sm text-gray-600">
            Create reusable content frameworks for faster content creation
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 rounded-lg bg-violet-600 px-4 py-2 text-white hover:bg-violet-700"
        >
          <Plus className="h-5 w-5" />
          New Template
        </button>
      </div>

      {/* Business Selector */}
      {businesses.length > 0 && (
        <div className="mb-6">
          <label className="mb-2 block text-sm font-medium text-gray-700">
            Select Business
          </label>
          <select
            value={selectedBusiness || ''}
            onChange={(e) => setSelectedBusiness(Number(e.target.value))}
            className="w-full rounded-lg border border-gray-300 px-4 py-2 focus:border-violet-500 focus:outline-none"
          >
            {businesses.map((biz) => (
              <option key={biz.id} value={biz.id}>
                {biz.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Templates Grid */}
      {loading ? (
        <div className="text-center text-gray-600">Loading templates...</div>
      ) : templates.length === 0 ? (
        <div className="rounded-lg border border-dashed border-gray-300 bg-gray-50 p-12 text-center">
          <FileText className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No templates yet</h3>
          <p className="mt-2 text-sm text-gray-600">
            Create your first template to speed up content creation
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="mt-4 inline-flex items-center gap-2 rounded-lg bg-violet-600 px-4 py-2 text-white hover:bg-violet-700"
          >
            <Plus className="h-5 w-5" />
            Create Template
          </button>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {templates.map((template, index) => (
            <div
              key={template.id}
              className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm hover:shadow-md transition-shadow"
            >
              {/* Header */}
              <div className="mb-3 flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">{template.name}</h3>
                  {template.description && (
                    <p className="mt-1 text-sm text-gray-600 line-clamp-2">
                      {template.description}
                    </p>
                  )}
                </div>
              </div>

              {/* Tags */}
              <div className="mb-3 flex flex-wrap gap-2">
                {template.category && (
                  <span className={`rounded-full px-2 py-1 text-xs font-medium ${getCategoryColor(index)}`}>
                    {template.category}
                  </span>
                )}
                {template.platform && (
                  <span className={`rounded-full px-2 py-1 text-xs font-medium ${platformColors[template.platform as keyof typeof platformColors] || platformColors.null}`}>
                    {template.platform}
                  </span>
                )}
                {template.is_public && (
                  <span className="rounded-full bg-blue-100 px-2 py-1 text-xs font-medium text-blue-800">
                    Public
                  </span>
                )}
              </div>

              {/* Template Preview */}
              <div className="mb-3 rounded bg-gray-50 p-3">
                <p className="text-sm text-gray-700 line-clamp-3">
                  {template.template_structure}
                </p>
              </div>

              {/* Stats */}
              <div className="mb-3 flex items-center gap-4 text-xs text-gray-600">
                <span>Used {template.use_count} times</span>
                {template.placeholders && Object.keys(template.placeholders).length > 0 && (
                  <span>{Object.keys(template.placeholders).length} placeholders</span>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    setSelectedTemplate(template);
                    setPlaceholderValues({});
                    setGeneratedContent('');
                    setShowUseModal(true);
                  }}
                  className="flex-1 flex items-center justify-center gap-1 rounded bg-violet-600 px-3 py-2 text-sm text-white hover:bg-violet-700"
                >
                  <Sparkles className="h-4 w-4" />
                  Use Template
                </button>
                <button
                  onClick={() => copyToClipboard(template.template_structure)}
                  className="rounded bg-gray-100 p-2 text-gray-600 hover:bg-gray-200"
                  title="Copy template"
                >
                  <Copy className="h-4 w-4" />
                </button>
                {template.business_id === selectedBusiness && (
                  <button
                    onClick={() => handleDeleteTemplate(template.id)}
                    className="rounded bg-red-50 p-2 text-red-600 hover:bg-red-100"
                    title="Delete template"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Template Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
          <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-lg bg-white p-6">
            <h2 className="mb-4 text-xl font-bold">Create New Template</h2>
            
            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Template Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-violet-500 focus:outline-none"
                  placeholder="e.g., Product Launch, Weekly Tips"
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Description
                </label>
                <input
                  type="text"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-violet-500 focus:outline-none"
                  placeholder="Brief description of this template"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Category
                  </label>
                  <input
                    type="text"
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-violet-500 focus:outline-none"
                    placeholder="e.g., Marketing, Education"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    Platform
                  </label>
                  <select
                    value={formData.platform}
                    onChange={(e) => setFormData({ ...formData, platform: e.target.value })}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-violet-500 focus:outline-none"
                  >
                    <option value="">All Platforms</option>
                    <option value="twitter">Twitter</option>
                    <option value="linkedin">LinkedIn</option>
                    <option value="facebook">Facebook</option>
                    <option value="instagram">Instagram</option>
                  </select>
                </div>
              </div>

              <div>
                <div className="mb-1 flex items-center gap-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Template Structure *
                  </label>
                  <HelpIcon 
                    content="Use {{variable_name}} syntax to create dynamic placeholders. Example: {{product_name}}, {{benefit}}, {{price}}. These will be filled in when you use the template."
                    side="right"
                  />
                </div>
                <p className="mb-2 text-xs text-gray-600">
                  Use {`{{placeholder_name}}`} for variables (e.g., {`{{product_name}}`}, {`{{benefit}}`})
                </p>
                <textarea
                  value={formData.template_structure}
                  onChange={(e) => setFormData({ ...formData, template_structure: e.target.value })}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-violet-500 focus:outline-none"
                  rows={8}
                  placeholder="Excited to announce {{product_name}}! 🎉&#10;&#10;{{product_name}} helps you {{benefit}}.&#10;&#10;Perfect for {{target_audience}}.&#10;&#10;#ProductLaunch #Innovation"
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_public"
                  checked={formData.is_public}
                  onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
                  className="rounded border-gray-300 text-violet-600 focus:ring-violet-500"
                />
                <label htmlFor="is_public" className="text-sm text-gray-700">
                  Make this template public (share with community)
                </label>
              </div>
            </div>

            <div className="mt-6 flex items-center justify-end gap-3">
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  resetForm();
                }}
                className="rounded-lg border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateTemplate}
                disabled={!formData.name || !formData.template_structure}
                className="rounded-lg bg-violet-600 px-4 py-2 text-white hover:bg-violet-700 disabled:bg-gray-400"
              >
                Create Template
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Use Template Modal */}
      {showUseModal && selectedTemplate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
          <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-lg bg-white p-6">
            <h2 className="mb-4 text-xl font-bold">Use Template: {selectedTemplate.name}</h2>
            
            <div className="mb-4 rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-700">{selectedTemplate.template_structure}</p>
            </div>

            <div className="mb-4 space-y-3">
              <h3 className="font-medium text-gray-900">Fill in placeholders:</h3>
              {extractPlaceholders(selectedTemplate.template_structure).map((placeholder) => (
                <div key={placeholder}>
                  <label className="mb-1 block text-sm font-medium text-gray-700">
                    {placeholder.replace(/_/g, ' ')}
                  </label>
                  <input
                    type="text"
                    value={placeholderValues[placeholder] || ''}
                    onChange={(e) => setPlaceholderValues({
                      ...placeholderValues,
                      [placeholder]: e.target.value,
                    })}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-violet-500 focus:outline-none"
                    placeholder={`Enter ${placeholder.replace(/_/g, ' ')}`}
                  />
                </div>
              ))}
            </div>

            {generatedContent && (
              <div className="mb-4">
                <h3 className="mb-2 font-medium text-gray-900">Generated Content:</h3>
                <div className="rounded-lg bg-green-50 border border-green-200 p-4">
                  <p className="whitespace-pre-wrap text-gray-900">{generatedContent}</p>
                </div>
                <button
                  onClick={() => copyToClipboard(generatedContent)}
                  className="mt-2 flex items-center gap-2 rounded bg-green-600 px-4 py-2 text-sm text-white hover:bg-green-700"
                >
                  <Copy className="h-4 w-4" />
                  Copy to Clipboard
                </button>
              </div>
            )}

            <div className="flex items-center justify-end gap-3">
              <button
                onClick={() => {
                  setShowUseModal(false);
                  setSelectedTemplate(null);
                  setPlaceholderValues({});
                  setGeneratedContent('');
                }}
                className="rounded-lg border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50"
              >
                Close
              </button>
              <button
                onClick={handleUseTemplate}
                disabled={extractPlaceholders(selectedTemplate.template_structure).some(
                  p => !placeholderValues[p]
                )}
                className="flex items-center gap-2 rounded-lg bg-violet-600 px-4 py-2 text-white hover:bg-violet-700 disabled:bg-gray-400"
              >
                <Sparkles className="h-5 w-5" />
                Generate Content
              </button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="fixed bottom-4 right-4 rounded-lg bg-red-100 px-4 py-3 text-red-800">
          {error}
        </div>
      )}
    </div>
  );
}
