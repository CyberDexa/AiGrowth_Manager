'use client';

import { useState } from 'react';
import { Send, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { useAuth } from '@clerk/nextjs';

interface PublishNowButtonProps {
  content: string;
  platforms: ('linkedin' | 'twitter' | 'facebook' | 'instagram')[];
  businessId: number;
  platformParams?: Record<string, any>;
  onSuccess?: (results: any[]) => void;
  onError?: (error: string) => void;
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  className?: string;
}

export default function PublishNowButton({
  content,
  platforms,
  businessId,
  platformParams = {},
  onSuccess,
  onError,
  variant = 'primary',
  size = 'md',
  disabled = false,
  className = ''
}: PublishNowButtonProps) {
  const { getToken } = useAuth();
  const [publishing, setPublishing] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePublish = async () => {
    if (!content || platforms.length === 0) {
      const errorMsg = !content ? 'Content is required' : 'At least one platform must be selected';
      setError(errorMsg);
      onError?.(errorMsg);
      return;
    }

    setPublishing(true);
    setError(null);
    setSuccess(false);

    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v2/publish`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          content,
          platforms,
          platform_params: platformParams
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to publish content');
      }

      const data = await response.json();

      if (data.success) {
        setSuccess(true);
        onSuccess?.(data.results);

        // Reset success state after 3 seconds
        setTimeout(() => {
          setSuccess(false);
        }, 3000);

        // Open published posts in new tabs
        data.results.forEach((result: any) => {
          if (result.success && result.url) {
            window.open(result.url, '_blank');
          }
        });
      } else {
        throw new Error('Publishing failed');
      }
    } catch (err: any) {
      const errorMsg = err.message || 'An error occurred while publishing';
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setPublishing(false);
    }
  };

  // Variant styles
  const variantStyles = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    secondary: 'bg-gray-600 hover:bg-gray-700 text-white',
    outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50'
  };

  // Size styles
  const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };

  const buttonClass = `
    inline-flex items-center justify-center gap-2 
    rounded-lg font-medium transition-all
    ${variantStyles[variant]}
    ${sizeStyles[size]}
    ${disabled || publishing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
    ${success ? 'bg-green-600 hover:bg-green-600' : ''}
    ${error ? 'bg-red-600 hover:bg-red-600' : ''}
    ${className}
  `.trim();

  return (
    <div className="inline-block">
      <button
        onClick={handlePublish}
        disabled={disabled || publishing}
        className={buttonClass}
        title={`Publish to ${platforms.join(', ')}`}
      >
        {publishing && (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Publishing...</span>
          </>
        )}
        
        {!publishing && success && (
          <>
            <CheckCircle2 className="w-4 h-4" />
            <span>Published!</span>
          </>
        )}
        
        {!publishing && error && (
          <>
            <AlertCircle className="w-4 h-4" />
            <span>Failed</span>
          </>
        )}
        
        {!publishing && !success && !error && (
          <>
            <Send className="w-4 h-4" />
            <span>Publish Now</span>
          </>
        )}
      </button>

      {/* Error message */}
      {error && (
        <div className="mt-2 text-sm text-red-600">
          {error}
        </div>
      )}
    </div>
  );
}
