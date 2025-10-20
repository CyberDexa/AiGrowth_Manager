'use client';

import { useState, useEffect } from 'react';
import { X, Linkedin, Twitter, Facebook, Instagram, Send, Calendar, AlertCircle, CheckCircle2, Loader2, Image as ImageIcon, RotateCcw } from 'lucide-react';
import { useAuth } from '@clerk/nextjs';
import ImageSelector from '@/app/components/ImageSelector';
import PlatformPreview from '@/components/PlatformPreview';
import { useOnboarding } from '@/contexts/OnboardingContext';

interface PublishContentModalProps {
  isOpen: boolean;
  onClose: () => void;
  content: string;
  businessId: number | null;
  strategyId?: number;
  onSuccess?: () => void;
}

type Platform = 'linkedin' | 'twitter' | 'facebook' | 'instagram';
type PublishMode = 'now' | 'schedule';

const PublishContentModal = ({
  isOpen,
  onClose,
  content,
  businessId,
  strategyId,
  onSuccess
}: PublishContentModalProps) => {
  const { getToken } = useAuth();
  const { completeStep } = useOnboarding();
  const [editedContent, setEditedContent] = useState(content);
  const [selectedPlatform, setSelectedPlatform] = useState<Platform>('linkedin');
  const [publishMode, setPublishMode] = useState<PublishMode>('now');
  const [scheduledDate, setScheduledDate] = useState('');
  const [scheduledTime, setScheduledTime] = useState('');
  const [publishing, setPublishing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [selectedImageData, setSelectedImageData] = useState<any>(null);
  const [showImageSelector, setShowImageSelector] = useState(false);

  // Update edited content when content prop changes
  useEffect(() => {
    setEditedContent(content);
  }, [content]);

  if (!isOpen) return null;

  const platformConfig = {
    linkedin: {
      name: 'LinkedIn',
      icon: Linkedin,
      color: 'bg-blue-700',
      textColor: 'text-blue-700',
      available: true,
      maxChars: 3000,
    },
    twitter: {
      name: 'Twitter',
      icon: Twitter,
      color: 'bg-sky-500',
      textColor: 'text-sky-500',
      available: true,
      maxChars: 280,
    },
    facebook: {
      name: 'Facebook',
      icon: Facebook,
      color: 'bg-blue-600',
      textColor: 'text-blue-600',
      available: true,
      maxChars: 63206,
    },
    instagram: {
      name: 'Instagram',
      icon: Instagram,
      color: 'bg-pink-600',
      textColor: 'text-pink-600',
      available: true,
      maxChars: 2200,
      requiresImage: true,
    },
  };

  const currentPlatform = platformConfig[selectedPlatform];
  const characterCount = editedContent.length;
  const maxCharacters = currentPlatform.maxChars;
  const isContentValid = characterCount > 0 && characterCount <= maxCharacters;
  
  // Twitter thread detection
  const isTwitterThread = selectedPlatform === 'twitter' && characterCount > 280;
  const twitterThreadCount = isTwitterThread ? Math.ceil(characterCount / 270) : 0;

  const handlePublish = async () => {
    if (!businessId) {
      setError('No business selected');
      return;
    }

    if (!isContentValid) {
      setError('Content is invalid. Please check the character count.');
      return;
    }

    // Validate Instagram requires image
    if (selectedPlatform === 'instagram' && !selectedImage) {
      setError('Instagram posts require an image. Please add an image.');
      setShowImageSelector(true);
      return;
    }

    setPublishing(true);
    setError(null);

    try {
      // Get authentication token
      const token = await getToken();
      if (!token) {
        throw new Error('Authentication required. Please sign in.');
      }

      const payload: any = {
        business_id: businessId,
        content_text: editedContent,
      };

      if (strategyId) {
        payload.strategy_id = strategyId;
      }

      // Add image URL if selected
      if (selectedImage) {
        payload.content_images = [selectedImage];
      }

      if (publishMode === 'schedule' && scheduledDate && scheduledTime) {
        payload.scheduled_for = `${scheduledDate}T${scheduledTime}:00Z`;
      }

      console.log('Publishing to platform:', selectedPlatform);
      console.log('Token present:', !!token);
      console.log('Business ID:', businessId);
      console.log('Payload:', payload);

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/publishing/${selectedPlatform}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        console.error('Error response:', errorData);
        throw new Error(errorData.detail || 'Failed to publish content');
      }

      const data = await response.json();

      setSuccess(true);
      
      // Mark publish step as complete
      completeStep('publish');
      localStorage.setItem('has_published', 'true');
      
      // Show success message for 2 seconds, then close
      setTimeout(() => {
        if (onSuccess) onSuccess();
        onClose();
        
        // If published (not scheduled), open post in new tab
        if (data.platform_post_url && publishMode === 'now') {
          window.open(data.platform_post_url, '_blank');
        }
      }, 2000);

    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred');
    } finally {
      setPublishing(false);
    }
  };

  const handleClose = () => {
    if (!publishing) {
      setError(null);
      setSuccess(false);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-900">Publish Content</h2>
          <button
            onClick={handleClose}
            disabled={publishing}
            className="text-gray-400 hover:text-gray-600 disabled:opacity-50"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6">
          {/* Platform Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Select Platform
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {(Object.entries(platformConfig) as [Platform, typeof platformConfig.linkedin][]).map(
                ([platform, config]) => {
                  const Icon = config.icon;
                  const isSelected = selectedPlatform === platform;
                  const isAvailable = config.available;

                  return (
                    <button
                      key={platform}
                      onClick={() => isAvailable && setSelectedPlatform(platform)}
                      disabled={!isAvailable || publishing}
                      className={`
                        relative p-4 rounded-lg border-2 transition-all
                        ${isSelected ? 'border-blue-600 bg-blue-50' : 'border-gray-200 bg-white'}
                        ${isAvailable ? 'hover:border-blue-400 cursor-pointer' : 'opacity-50 cursor-not-allowed'}
                        disabled:opacity-50 disabled:cursor-not-allowed
                      `}
                    >
                      <div className="flex flex-col items-center space-y-2">
                        <div className={`${config.color} text-white p-3 rounded-full`}>
                          <Icon className="w-6 h-6" />
                        </div>
                        <span className="text-sm font-medium text-gray-900">{config.name}</span>
                        {!isAvailable && (
                          <span className="text-xs text-gray-500">Coming Soon</span>
                        )}
                      </div>
                      {isSelected && (
                        <div className="absolute top-2 right-2">
                          <CheckCircle2 className="w-5 h-5 text-blue-600" />
                        </div>
                      )}
                    </button>
                  );
                }
              )}
            </div>
          </div>

          {/* Image Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Image {selectedPlatform === 'instagram' && <span className="text-red-600">*</span>}
            </label>
            
            {!selectedImage ? (
              <button
                onClick={() => setShowImageSelector(true)}
                disabled={publishing}
                type="button"
                className="w-full py-3 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-400 transition-colors flex items-center justify-center gap-2 text-gray-600 hover:text-blue-600 disabled:opacity-50"
              >
                <ImageIcon className="w-5 h-5" />
                <span>Add Image</span>
              </button>
            ) : (
              <div className="relative">
                <img src={selectedImage} alt="Selected" className="w-full rounded-lg max-h-64 object-cover" />
                <button
                  onClick={() => {
                    setSelectedImage(null);
                    setSelectedImageData(null);
                  }}
                  disabled={publishing}
                  type="button"
                  className="absolute top-2 right-2 p-2 bg-red-600 text-white rounded-full hover:bg-red-700 disabled:opacity-50"
                >
                  <X className="w-4 h-4" />
                </button>
                {selectedImageData && (
                  <div className="mt-2 text-xs text-gray-500">
                    {selectedImageData.original_filename} • {selectedImageData.width}x{selectedImageData.height}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Content Editor */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-700">
                Edit Content
              </label>
              {editedContent !== content && (
                <button
                  onClick={() => setEditedContent(content)}
                  disabled={publishing}
                  className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 disabled:opacity-50"
                >
                  <RotateCcw className="w-3 h-3" />
                  Reset to original
                </button>
              )}
            </div>
            <textarea
              value={editedContent}
              onChange={(e) => setEditedContent(e.target.value)}
              disabled={publishing}
              className="w-full border border-gray-300 rounded-lg p-4 bg-white min-h-[150px] max-h-[300px] resize-y focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:bg-gray-50"
              placeholder="Edit your content here..."
            />
            <div className="mt-2 space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className={`${characterCount > maxCharacters ? 'text-red-600' : 'text-gray-500'}`}>
                  {characterCount} / {maxCharacters} characters
                </span>
                {characterCount > maxCharacters && (
                  <span className="text-red-600 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    Content exceeds maximum length
                  </span>
                )}
              </div>
              {isTwitterThread && (
                <div className="flex items-center gap-2 text-sm text-sky-600 bg-sky-50 rounded-md px-3 py-2">
                  <Twitter className="w-4 h-4" />
                  <span>This will be posted as a {twitterThreadCount}-tweet thread</span>
                </div>
              )}
              {selectedPlatform === 'instagram' && !selectedImage && (
                <div className="flex items-center gap-2 text-sm text-amber-600 bg-amber-50 rounded-md px-3 py-2">
                  <AlertCircle className="w-4 h-4" />
                  <span>Instagram requires an image. Click "Add Image" above to select or generate one.</span>
                </div>
              )}
            </div>
          </div>

          {/* Platform Preview */}
          {editedContent && (
            <PlatformPreview 
              content={editedContent} 
              platforms={[selectedPlatform]}
            />
          )}

          {/* Publishing Options */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Publishing Options
            </label>
            <div className="space-y-3">
              <label className="flex items-center space-x-3">
                <input
                  type="radio"
                  value="now"
                  checked={publishMode === 'now'}
                  onChange={() => setPublishMode('now')}
                  disabled={publishing}
                  className="w-4 h-4 text-blue-600"
                />
                <span className="text-gray-900">Publish Now</span>
              </label>
              <label className="flex items-center space-x-3">
                <input
                  type="radio"
                  value="schedule"
                  checked={publishMode === 'schedule'}
                  onChange={() => setPublishMode('schedule')}
                  disabled={publishing}
                  className="w-4 h-4 text-blue-600"
                />
                <span className="text-gray-900">Schedule for Later</span>
              </label>

              {publishMode === 'schedule' && (
                <div className="ml-7 mt-3 grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Date</label>
                    <input
                      type="date"
                      value={scheduledDate}
                      onChange={(e) => setScheduledDate(e.target.value)}
                      disabled={publishing}
                      min={new Date().toISOString().split('T')[0]}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Time</label>
                    <input
                      type="time"
                      value={scheduledTime}
                      onChange={(e) => setScheduledTime(e.target.value)}
                      disabled={publishing}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex gap-3">
              <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-blue-800">
                <p className="font-medium mb-1">Publishing Information</p>
                <p>
                  Content will be posted to your connected {platformConfig[selectedPlatform].name} account.
                  {publishMode === 'schedule' && ' You can view and manage scheduled posts in the Published section.'}
                </p>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-red-800">Publishing Failed</p>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex gap-3">
                <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-green-800">
                    {publishMode === 'now' ? 'Published Successfully!' : 'Scheduled Successfully!'}
                  </p>
                  <p className="text-sm text-green-700 mt-1">
                    {publishMode === 'now'
                      ? `Your content has been posted to ${platformConfig[selectedPlatform].name}.`
                      : `Your content has been scheduled for ${scheduledDate} at ${scheduledTime}.`}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t bg-gray-50">
          <button
            onClick={handleClose}
            disabled={publishing}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handlePublish}
            disabled={publishing || !isContentValid || (publishMode === 'schedule' && (!scheduledDate || !scheduledTime))}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {publishing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Publishing...
              </>
            ) : publishMode === 'now' ? (
              <>
                <Send className="w-4 h-4" />
                Publish to {platformConfig[selectedPlatform].name}
              </>
            ) : (
              <>
                <Calendar className="w-4 h-4" />
                Schedule Post
              </>
            )}
          </button>
        </div>

        {/* Image Selector Modal */}
        {businessId && (
          <ImageSelector
            businessId={businessId}
            isOpen={showImageSelector}
            onClose={() => setShowImageSelector(false)}
            onSelectImage={(imageUrl, imageData) => {
              setSelectedImage(imageUrl);
              setSelectedImageData(imageData);
              setShowImageSelector(false);
            }}
            requireImage={selectedPlatform === 'instagram'}
          />
        )}
      </div>
    </div>
  );
};

export default PublishContentModal;
