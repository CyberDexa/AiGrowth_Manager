"use client";

import React, { useState } from 'react';
import { X, Upload, Sparkles, Image as ImageIcon } from 'lucide-react';
import ImageUploader from './ImageUploader';
import AIImageGenerator from './AIImageGenerator';
import ImageLibrary from './ImageLibrary';

interface ImageSelectorProps {
  businessId: number;
  isOpen: boolean;
  onClose: () => void;
  onSelectImage: (imageUrl: string, imageData: any) => void;
  requireImage?: boolean;
}

type Tab = 'library' | 'upload' | 'generate';

export default function ImageSelector({
  businessId,
  isOpen,
  onClose,
  onSelectImage,
  requireImage = false
}: ImageSelectorProps) {
  const [activeTab, setActiveTab] = useState<Tab>('library');

  if (!isOpen) return null;

  const handleImageSelected = (imageUrl: string, imageData: any) => {
    onSelectImage(imageUrl, imageData);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {requireImage ? 'Select Image (Required)' : 'Select Image'}
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Choose from library, upload new, or generate with AI
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-6 h-6 text-gray-600" />
          </button>
        </div>

        {/* Tabs */}
        <div className="px-6 pt-4 border-b border-gray-200">
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('library')}
              className={`flex items-center gap-2 px-4 py-2 rounded-t-lg font-medium transition-colors ${
                activeTab === 'library'
                  ? 'bg-blue-50 text-blue-700 border-b-2 border-blue-700'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <ImageIcon className="w-5 h-5" />
              Image Library
            </button>
            <button
              onClick={() => setActiveTab('upload')}
              className={`flex items-center gap-2 px-4 py-2 rounded-t-lg font-medium transition-colors ${
                activeTab === 'upload'
                  ? 'bg-green-50 text-green-700 border-b-2 border-green-700'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <Upload className="w-5 h-5" />
              Upload New
            </button>
            <button
              onClick={() => setActiveTab('generate')}
              className={`flex items-center gap-2 px-4 py-2 rounded-t-lg font-medium transition-colors ${
                activeTab === 'generate'
                  ? 'bg-purple-50 text-purple-700 border-b-2 border-purple-700'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <Sparkles className="w-5 h-5" />
              Generate with AI
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'library' && (
            <ImageLibrary
              businessId={businessId}
              selectionMode={true}
              onSelectImage={(image) => handleImageSelected(image.storage_url, image)}
            />
          )}

          {activeTab === 'upload' && (
            <ImageUploader
              businessId={businessId}
              onUploadSuccess={(image) => handleImageSelected(image.storage_url, image)}
            />
          )}

          {activeTab === 'generate' && (
            <AIImageGenerator
              businessId={businessId}
              onGenerateSuccess={(image) => handleImageSelected(image.storage_url, image)}
            />
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">
              {activeTab === 'library' && 'Select an image from your library'}
              {activeTab === 'upload' && 'Upload a new image (max 10MB)'}
              {activeTab === 'generate' && 'Generate a unique image with AI ($0.04-0.12 per image)'}
            </p>
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 hover:bg-gray-200 rounded-lg transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
