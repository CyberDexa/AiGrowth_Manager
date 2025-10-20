'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { Linkedin, Twitter, Facebook, CheckCircle2, XCircle, ExternalLink, Loader2 } from 'lucide-react';
import { useOnboarding } from '@/contexts/OnboardingContext';

interface SocialAccount {
  id: number;
  platform: string;
  platform_user_id: string;
  platform_username: string;
  is_active: boolean;
  created_at: string;
  token_expires_at?: string;
}

interface SocialConnectionsProps {
  businessId: number | null;
}

export default function SocialConnections({ businessId }: SocialConnectionsProps) {
  const { getToken } = useAuth();
  const { completeStep } = useOnboarding();
  const [accounts, setAccounts] = useState<SocialAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState<string | null>(null);

  useEffect(() => {
    if (businessId) {
      loadAccounts();
    }
  }, [businessId]);

  const loadAccounts = async () => {
    if (!businessId) return;

    try {
      setLoading(true);
      const token = await getToken();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/social/accounts?business_id=${businessId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setAccounts(data);
        
        // Check if any accounts are connected and mark step complete
        if (data.length > 0 && data.some((acc: SocialAccount) => acc.is_active)) {
          completeStep('social_accounts');
          localStorage.setItem('has_social_accounts', 'true');
        }
      }
    } catch (error) {
      console.error('Failed to load social accounts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (platform: string) => {
    // Debug logging
    console.log('🔍 handleConnect called:', { platform, businessId });
    
    if (!businessId) {
      console.error('❌ No business ID available');
      alert('Please create a business first');
      return;
    }

    setConnecting(platform);
    
    try {
      const token = await getToken();
      const url = `${process.env.NEXT_PUBLIC_API_URL}/api/v1/oauth/${platform}/authorize?business_id=${businessId}`;
      
      console.log('🌐 OAuth request URL:', url);
      
      // Step 1: Get OAuth authorization URL from backend (authenticated endpoint)
      const response = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('❌ OAuth authorization failed:', {
          status: response.status,
          statusText: response.statusText,
          error: errorData
        });
        throw new Error(`Failed to get authorization URL: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('✅ Got authorization URL:', data);
      
      // Step 2: Redirect user to OAuth provider (LinkedIn, Twitter, Facebook)
      window.location.href = data.authorization_url;
    } catch (error) {
      console.error('Failed to initiate OAuth:', error);
      setConnecting(null);
      alert('Failed to connect. Please try again.');
    }
  };

  const handleDisconnect = async (platform: string) => {
    if (!businessId) return;

    if (!confirm(`Are you sure you want to disconnect your ${platform} account?`)) {
      return;
    }

    try {
      const token = await getToken();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/social/${platform}/disconnect?business_id=${businessId}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        await loadAccounts();
      } else {
        alert('Failed to disconnect account');
      }
    } catch (error) {
      console.error('Failed to disconnect:', error);
      alert('Failed to disconnect account');
    }
  };

  const getAccount = (platform: string) => {
    // Database stores 'meta' but frontend uses 'meta' as the platform identifier
    return accounts.find((acc) => acc.platform === platform && acc.is_active);
  };

  const isConnected = (platform: string) => {
    return !!getAccount(platform);
  };

  const PlatformCard = ({ platform, icon: Icon, color, displayName }: {
    platform: string;
    icon: any;
    color: string;
    displayName: string;
  }) => {
    const account = getAccount(platform);
    const connected = isConnected(platform);

    return (
      <div className="rounded-lg border bg-white p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={`rounded-lg ${color} p-3`}>
              <Icon className="h-6 w-6 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">{displayName}</h3>
              {connected && account && (
                <p className="text-sm text-gray-600">{account.platform_username}</p>
              )}
            </div>
          </div>
          
          {connected ? (
            <div className="flex items-center gap-2 text-green-600">
              <CheckCircle2 className="h-5 w-5" />
              <span className="text-sm font-medium">Connected</span>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-gray-400">
              <XCircle className="h-5 w-5" />
              <span className="text-sm font-medium">Not Connected</span>
            </div>
          )}
        </div>

        <div className="mt-4">
          {connected && account ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Connected on:</span>
                <span className="font-medium text-gray-900">
                  {new Date(account.created_at).toLocaleDateString()}
                </span>
              </div>
              {account.token_expires_at && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Token expires:</span>
                  <span className={`font-medium ${
                    new Date(account.token_expires_at) > new Date() 
                      ? 'text-green-600' 
                      : 'text-red-600'
                  }`}>
                    {new Date(account.token_expires_at).toLocaleString()}
                  </span>
                </div>
              )}
              <button
                onClick={() => handleDisconnect(platform)}
                className="w-full rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-100 transition-colors"
              >
                Disconnect
              </button>
            </div>
          ) : (
            <button
              onClick={() => handleConnect(platform)}
              disabled={connecting === platform || !businessId}
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {connecting === platform ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Connecting...
                </>
              ) : (
                <>
                  <ExternalLink className="h-4 w-4" />
                  Connect {displayName}
                </>
              )}
            </button>
          )}
        </div>
      </div>
    );
  };

  if (!businessId) {
    return (
      <div className="rounded-lg border bg-yellow-50 p-6 text-center">
        <p className="text-yellow-800">
          Please create a business first to connect social accounts.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900">Connected Social Accounts</h3>
        <p className="mt-1 text-sm text-gray-600">
          Link your social media accounts to enable automated content publishing and analytics tracking.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-1 lg:grid-cols-2">
        <PlatformCard
          platform="linkedin"
          icon={Linkedin}
          color="bg-blue-700"
          displayName="LinkedIn"
        />
        
        <PlatformCard
          platform="twitter"
          icon={Twitter}
          color="bg-sky-500"
          displayName="Twitter / X"
        />
        
        <PlatformCard
          platform="meta"
          icon={Facebook}
          color="bg-blue-600"
          displayName="Facebook / Instagram"
        />
      </div>

      <div className="rounded-lg border bg-blue-50 p-4">
        <h4 className="font-medium text-blue-900">ℹ️ About Social Connections</h4>
        <ul className="mt-2 space-y-1 text-sm text-blue-800">
          <li>• Connecting accounts allows AI Growth Manager to post content on your behalf</li>
          <li>• Your access tokens are encrypted and stored securely</li>
          <li>• You can disconnect at any time</li>
          <li>• Tokens expire after 60 days - you'll need to reconnect</li>
        </ul>
      </div>
    </div>
  );
}
