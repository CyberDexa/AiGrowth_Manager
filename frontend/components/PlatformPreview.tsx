'use client';

import { Twitter, Linkedin, Facebook, Instagram } from 'lucide-react';

interface PlatformPreviewProps {
  content: string;
  platforms?: ('twitter' | 'linkedin' | 'facebook' | 'instagram')[];
  showAll?: boolean;
}

const CHAR_LIMITS = {
  twitter: 280,
  linkedin: 3000,
  facebook: 63206,
  instagram: 2200,
};

const PLATFORM_COLORS = {
  twitter: {
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    icon: 'text-blue-500',
    accent: 'bg-blue-500',
  },
  linkedin: {
    bg: 'bg-blue-50',
    border: 'border-blue-300',
    icon: 'text-blue-700',
    accent: 'bg-blue-700',
  },
  facebook: {
    bg: 'bg-blue-50',
    border: 'border-blue-400',
    icon: 'text-blue-600',
    accent: 'bg-blue-600',
  },
  instagram: {
    bg: 'bg-gradient-to-br from-purple-50 to-pink-50',
    border: 'border-pink-300',
    icon: 'text-pink-500',
    accent: 'bg-gradient-to-r from-purple-500 to-pink-500',
  },
};

const getPlatformIcon = (platform: string) => {
  switch (platform) {
    case 'twitter':
      return <Twitter className="h-5 w-5" />;
    case 'linkedin':
      return <Linkedin className="h-5 w-5" />;
    case 'facebook':
      return <Facebook className="h-5 w-5" />;
    case 'instagram':
      return <Instagram className="h-5 w-5" />;
    default:
      return null;
  }
};

const formatContent = (text: string, platform: string) => {
  // Highlight hashtags
  let formatted = text.replace(/#(\w+)/g, '<span class="text-blue-500 font-medium">#$1</span>');
  
  // Highlight mentions
  formatted = formatted.replace(/@(\w+)/g, '<span class="text-blue-500 font-medium">@$1</span>');
  
  // Make links clickable (basic URL detection)
  formatted = formatted.replace(
    /(https?:\/\/[^\s]+)/g,
    '<a href="$1" class="text-blue-500 underline" target="_blank" rel="noopener noreferrer">$1</a>'
  );
  
  return formatted;
};

const PlatformPreview = ({ content, platforms = ['twitter', 'linkedin', 'facebook'], showAll = false }: PlatformPreviewProps) => {
  const displayPlatforms = showAll ? ['twitter', 'linkedin', 'facebook', 'instagram'] : platforms;

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Platform Preview</h3>
      
      <div className="grid gap-4 md:grid-cols-2">
        {displayPlatforms.map((platform) => {
          const charLimit = CHAR_LIMITS[platform as keyof typeof CHAR_LIMITS];
          const charCount = content.length;
          const isOverLimit = charCount > charLimit;
          const colors = PLATFORM_COLORS[platform as keyof typeof PLATFORM_COLORS];
          const truncatedContent = isOverLimit ? content.slice(0, charLimit) : content;
          const formattedContent = formatContent(truncatedContent, platform);

          return (
            <div
              key={platform}
              className={`rounded-lg border-2 ${colors.border} ${colors.bg} p-4 transition-all hover:shadow-md`}
            >
              {/* Platform Header */}
              <div className="mb-3 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={colors.icon}>
                    {getPlatformIcon(platform)}
                  </div>
                  <span className="font-semibold capitalize text-gray-900">
                    {platform}
                  </span>
                </div>
                <div className={`text-xs font-medium ${isOverLimit ? 'text-red-600' : 'text-gray-600'}`}>
                  {charCount} / {charLimit.toLocaleString()}
                </div>
              </div>

              {/* Content Preview */}
              <div className="rounded-md bg-white p-3 shadow-sm">
                <div className="flex items-start gap-3">
                  {/* Avatar placeholder */}
                  <div className={`h-10 w-10 flex-shrink-0 rounded-full ${colors.accent}`}></div>
                  
                  {/* Content */}
                  <div className="flex-1 overflow-hidden">
                    <div className="mb-1 font-semibold text-gray-900">Your Business</div>
                    <div 
                      className="text-sm text-gray-800 whitespace-pre-wrap break-words"
                      dangerouslySetInnerHTML={{ __html: formattedContent }}
                    />
                    
                    {/* Truncation indicator */}
                    {isOverLimit && (
                      <div className="mt-2 text-xs text-red-600 font-medium">
                        ⚠️ Content will be truncated ({charCount - charLimit} chars over limit)
                      </div>
                    )}

                    {/* Platform-specific elements */}
                    {platform === 'twitter' && !isOverLimit && (
                      <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                        <span>💬 Reply</span>
                        <span>🔄 Retweet</span>
                        <span>❤️ Like</span>
                        <span>📊 Share</span>
                      </div>
                    )}

                    {platform === 'linkedin' && (
                      <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                        <span>👍 Like</span>
                        <span>💬 Comment</span>
                        <span>🔄 Repost</span>
                        <span>📤 Send</span>
                      </div>
                    )}

                    {platform === 'facebook' && (
                      <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                        <span>👍 Like</span>
                        <span>💬 Comment</span>
                        <span>↗️ Share</span>
                      </div>
                    )}

                    {platform === 'instagram' && (
                      <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                        <span>❤️ Like</span>
                        <span>💬 Comment</span>
                        <span>📤 Share</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Character limit bar */}
              <div className="mt-2">
                <div className="h-1 w-full overflow-hidden rounded-full bg-gray-200">
                  <div
                    className={`h-full transition-all ${
                      isOverLimit ? 'bg-red-500' : charCount > charLimit * 0.9 ? 'bg-yellow-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min((charCount / charLimit) * 100, 100)}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default PlatformPreview;
