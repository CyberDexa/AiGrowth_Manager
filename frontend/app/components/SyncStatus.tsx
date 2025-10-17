"use client";

import React, { useState, useEffect } from 'react';
import { 
  RefreshCw, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  Loader2,
  Linkedin,
  Twitter,
  Facebook
} from 'lucide-react';
import useSWR from 'swr';

interface SyncStatusProps {
  businessId: number;
  apiToken: () => Promise<string | null>;
}

interface PlatformStatus {
  status: string;
  message: string;
  last_sync: string | null;
  token_expires_at: string | null;
  username: string;
}

interface SyncStatusData {
  business_id: number;
  overall_status: string;
  last_sync: string | null;
  connected_platforms: number;
  platforms: Record<string, PlatformStatus>;
  timestamp: string;
}

// Platform icons mapping
const platformIcons: Record<string, React.ElementType> = {
  linkedin: Linkedin,
  twitter: Twitter,
  meta: Facebook,
};

// Status colors
const statusColors: Record<string, string> = {
  success: 'text-green-500',
  error: 'text-red-500',
  idle: 'text-gray-500',
  syncing: 'text-blue-500',
};

// Status background colors
const statusBgColors: Record<string, string> = {
  success: 'bg-green-50 border-green-200',
  error: 'bg-red-50 border-red-200',
  idle: 'bg-gray-50 border-gray-200',
  syncing: 'bg-blue-50 border-blue-200',
};

export default function SyncStatus({ businessId, apiToken }: SyncStatusProps) {
  const [syncing, setSyncing] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  // Fetch sync status with auto-refresh every 30 seconds
  const { data: syncStatus, error, mutate } = useSWR<SyncStatusData>(
    businessId ? `sync-status-${businessId}` : null,
    async () => {
      const token = await apiToken();
      if (!token) {
        throw new Error('No authentication token available');
      }
      
      const response = await fetch(
        `http://localhost:8003/api/v1/analytics/sync-status/${businessId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch sync status');
      }
      
      return response.json();
    },
    {
      refreshInterval: 30000, // Refresh every 30 seconds
      revalidateOnFocus: true,
    }
  );

  const handleSyncNow = async () => {
    setSyncing(true);
    try {
      const token = await apiToken();
      if (!token) {
        throw new Error('No authentication token available');
      }
      
      const response = await fetch(
        `http://localhost:8003/api/v1/scheduler/trigger/${businessId}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.ok) {
        // Wait a moment then refresh status
        setTimeout(() => {
          mutate();
          setSyncing(false);
        }, 2000);
      } else {
        throw new Error('Failed to trigger sync');
      }
    } catch (err) {
      console.error('Sync error:', err);
      setSyncing(false);
    }
  };

  const formatTimeAgo = (timestamp: string | null): string => {
    if (!timestamp) return 'Never';
    
    const now = new Date();
    const then = new Date(timestamp);
    const seconds = Math.floor((now.getTime() - then.getTime()) / 1000);
    
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center space-x-2 text-red-700">
          <AlertCircle className="h-5 w-5" />
          <span className="font-medium">Failed to load sync status</span>
        </div>
      </div>
    );
  }

  if (!syncStatus) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <div className="flex items-center space-x-2 text-gray-600">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>Loading sync status...</span>
        </div>
      </div>
    );
  }

  const StatusIcon = 
    syncStatus.overall_status === 'success' ? CheckCircle :
    syncStatus.overall_status === 'error' ? AlertCircle :
    syncStatus.overall_status === 'syncing' ? Loader2 : Clock;

  const iconClass = syncStatus.overall_status === 'syncing' ? 'animate-spin' : '';

  return (
    <div className={`border rounded-lg p-4 ${statusBgColors[syncStatus.overall_status] || 'bg-white border-gray-200'}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-3">
          <StatusIcon className={`h-6 w-6 ${statusColors[syncStatus.overall_status]} ${iconClass}`} />
          <div>
            <h3 className="font-semibold text-gray-900">
              Sync Status
            </h3>
            <p className="text-sm text-gray-600">
              Last synced: {formatTimeAgo(syncStatus.last_sync)}
            </p>
          </div>
        </div>

        <button
          onClick={handleSyncNow}
          disabled={syncing || syncStatus.overall_status === 'syncing'}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          <RefreshCw className={`h-4 w-4 ${syncing ? 'animate-spin' : ''}`} />
          <span>{syncing ? 'Syncing...' : 'Sync Now'}</span>
        </button>
      </div>

      {/* Connected Platforms Count */}
      <div className="mb-3 pb-3 border-b border-gray-200">
        <span className="text-sm text-gray-600">
          {syncStatus.connected_platforms} {syncStatus.connected_platforms === 1 ? 'platform' : 'platforms'} connected
        </span>
      </div>

      {/* Platform Details Toggle */}
      {syncStatus.connected_platforms > 0 && (
        <>
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            {showDetails ? 'Hide' : 'Show'} platform details
          </button>

          {showDetails && (
            <div className="mt-4 space-y-3">
              {Object.entries(syncStatus.platforms).map(([platform, status]) => {
                const Icon = platformIcons[platform] || Facebook;
                const platformStatusColor = statusColors[status.status] || 'text-gray-500';
                
                return (
                  <div 
                    key={platform} 
                    className="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      <Icon className={`h-5 w-5 ${platformStatusColor}`} />
                      <div>
                        <p className="font-medium text-gray-900 capitalize">
                          {platform}
                        </p>
                        <p className="text-sm text-gray-600">
                          @{status.username}
                        </p>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <p className={`text-sm font-medium ${platformStatusColor}`}>
                        {status.message}
                      </p>
                      {status.last_sync && (
                        <p className="text-xs text-gray-500">
                          {formatTimeAgo(status.last_sync)}
                        </p>
                      )}
                      {status.status === 'error' && status.token_expires_at && (
                        <p className="text-xs text-red-600 mt-1">
                          Reconnect required
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}

      {/* No platforms connected message */}
      {syncStatus.connected_platforms === 0 && (
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-start space-x-3">
            <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
            <div>
              <p className="font-medium text-yellow-900">No platforms connected</p>
              <p className="text-sm text-yellow-700 mt-1">
                Connect your social media accounts in Settings to start tracking analytics.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
