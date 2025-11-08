"use client";

import React, { useState } from 'react';
import { Sparkles, Loader2, RefreshCw, CheckCircle, AlertCircle, DollarSign } from 'lucide-react';

interface AIImageGeneratorProps {
  businessId: number;
  onGenerateSuccess?: (image: GeneratedImage) => void;
  onClose?: () => void;
}

interface GeneratedImage {
  id: number;
  storage_url: string;
  original_filename: string;
  width: number;
  height: number;
  ai_prompt: string;
  ai_model: string;
}

export default function AIImageGenerator({ 
  businessId, 
  onGenerateSuccess,
  onClose 
}: AIImageGeneratorProps) {
  const [prompt, setPrompt] = useState('');
  const [size, setSize] = useState<'1024x1024' | '1792x1024' | '1024x1792'>('1024x1024');
  const [generating, setGenerating] = useState(false);
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cost, setCost] = useState<number>(0.040);

  const sizes = [
    { value: '1024x1024', label: 'Square (1:1)', description: 'Instagram, Twitter', cost: 0.040 },
    { value: '1792x1024', label: 'Landscape (16:9)', description: 'LinkedIn, Twitter', cost: 0.080 },
    { value: '1024x1792', label: 'Portrait (9:16)', description: 'Instagram Stories', cost: 0.080 },
  ];

  const handleSizeChange = (newSize: string) => {
    setSize(newSize as typeof size);
    const selectedSize = sizes.find(s => s.value === newSize);
    if (selectedSize) {
      setCost(selectedSize.cost);
    }
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    setError(null);
    setGenerating(true);
    setGeneratedImage(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';
      const response = await fetch(`${apiUrl}/api/v1/images/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt.trim(),
          business_id: businessId,
          size: size,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Generation failed');
      }

      const data = await response.json();
      
      if (data.success && data.image) {
        setGeneratedImage(data.image.storage_url);
        
        // Call success callback
        if (onGenerateSuccess) {
          onGenerateSuccess(data.image);
        }
      } else {
        throw new Error('Generation failed - no image returned');
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate image');
    } finally {
      setGenerating(false);
    }
  };

  const handleRegenerate = () => {
    setGeneratedImage(null);
    setError(null);
  };

  const handleUseImage = () => {
    if (onClose) {
      onClose();
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center gap-2 mb-2">
          <Sparkles className="w-6 h-6 text-purple-600" />
          <h2 className="text-2xl font-bold text-gray-900">AI Image Generator</h2>
        </div>
        <p className="text-gray-600">Generate unique images using DALL-E 3</p>
      </div>

      {/* Prompt Input */}
      <div>
        <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-2">
          Describe the image you want to create
        </label>
        <textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Example: A modern office workspace with plants and natural lighting, professional photography style"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
          rows={4}
          maxLength={1000}
          disabled={generating}
        />
        <div className="flex justify-between items-center mt-1">
          <p className="text-sm text-gray-500">{prompt.length}/1000 characters</p>
          {prompt.length > 0 && (
            <button
              onClick={() => setPrompt('')}
              className="text-sm text-gray-500 hover:text-gray-700"
              disabled={generating}
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Size Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Image Size
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {sizes.map((sizeOption) => (
            <button
              key={sizeOption.value}
              onClick={() => handleSizeChange(sizeOption.value)}
              disabled={generating}
              className={`p-4 border-2 rounded-lg text-left transition-colors ${
                size === sizeOption.value
                  ? 'border-purple-600 bg-purple-50'
                  : 'border-gray-200 hover:border-gray-300'
              } ${generating ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <div className="font-medium text-gray-900">{sizeOption.label}</div>
              <div className="text-sm text-gray-600 mt-1">{sizeOption.description}</div>
              <div className="flex items-center gap-1 text-xs text-gray-500 mt-2">
                <DollarSign className="w-3 h-3" />
                <span>${sizeOption.cost.toFixed(3)}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={handleGenerate}
        disabled={generating || !prompt.trim()}
        className={`w-full py-3 px-6 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 ${
          generating || !prompt.trim()
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-700 hover:to-pink-700'
        }`}
      >
        {generating ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Generating image... (20-60 seconds)
          </>
        ) : (
          <>
            <Sparkles className="w-5 h-5" />
            Generate Image (${cost.toFixed(3)})
          </>
        )}
      </button>

      {/* Generated Image Preview */}
      {generatedImage && (
        <div className="space-y-4">
          <div className="border-2 border-green-500 rounded-lg p-4 bg-green-50">
            <div className="flex items-center gap-2 mb-3">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="font-medium text-green-900">Image generated successfully!</span>
            </div>
            <img
              src={generatedImage}
              alt="Generated"
              className="w-full rounded-lg shadow-lg"
            />
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleRegenerate}
              className="flex-1 py-2 px-4 border-2 border-gray-300 text-gray-700 rounded-lg hover:border-gray-400 transition-colors flex items-center justify-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Generate Again
            </button>
            <button
              onClick={handleUseImage}
              className="flex-1 py-2 px-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center justify-center gap-2"
            >
              <CheckCircle className="w-4 h-4" />
              Use This Image
            </button>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
          <div>
            <p className="text-red-800 font-medium">Generation failed</p>
            <p className="text-sm text-red-700">{error}</p>
            {error.includes('not configured') && (
              <p className="text-sm text-red-700 mt-1">
                Please add your OpenAI API key to the backend .env file.
              </p>
            )}
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm font-medium text-blue-900 mb-2">Tips for better results:</p>
        <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
          <li>Be specific and descriptive in your prompt</li>
          <li>Include style keywords like "professional", "minimalist", "vibrant"</li>
          <li>Mention photography/art style: "studio photography", "watercolor", etc.</li>
          <li>Specify lighting, colors, and composition details</li>
        </ul>
      </div>
    </div>
  );
}
