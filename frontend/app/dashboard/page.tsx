'use client';

import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const router = useRouter();
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-violet-50 to-teal-50 p-6">
      <div className="mx-auto max-w-7xl">
        {/* Hero Header with Gradient */}
        <div className="mb-8 rounded-2xl bg-gradient-to-r from-violet-600 via-violet-500 to-teal-500 p-8 text-white shadow-xl">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold">Welcome Back! 👋</h2>
              <p className="mt-2 text-violet-100">
                Here's what's happening with your marketing today.
              </p>
            </div>
            <div className="hidden md:block">
              <div className="rounded-full bg-white/20 backdrop-blur-sm px-6 py-3">
                <p className="text-sm font-medium">AI Growth Manager</p>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Grid - Modern Cards */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
          <div className="group relative overflow-hidden rounded-2xl border border-gray-200 bg-white p-6 shadow-md hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
            <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-violet-400/20 to-transparent rounded-bl-full"></div>
            <div className="relative">
              <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <span className="text-2xl">📊</span>
                Total Posts
              </div>
              <div className="mt-3 text-4xl font-bold bg-gradient-to-r from-violet-600 to-violet-400 bg-clip-text text-transparent">0</div>
              <p className="mt-2 text-xs text-gray-600">No posts created yet</p>
            </div>
          </div>

          <div className="group relative overflow-hidden rounded-2xl border border-gray-200 bg-white p-6 shadow-md hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
            <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-teal-400/20 to-transparent rounded-bl-full"></div>
            <div className="relative">
              <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <span className="text-2xl">📈</span>
                Reach
              </div>
              <div className="mt-3 text-4xl font-bold bg-gradient-to-r from-teal-600 to-teal-400 bg-clip-text text-transparent">0</div>
              <p className="mt-2 text-xs text-gray-600">Start posting to track reach</p>
            </div>
          </div>

          <div className="group relative overflow-hidden rounded-2xl border border-gray-200 bg-white p-6 shadow-md hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
            <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-violet-400/20 to-transparent rounded-bl-full"></div>
            <div className="relative">
              <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <span className="text-2xl">💬</span>
                Engagement
              </div>
              <div className="mt-3 text-4xl font-bold bg-gradient-to-r from-violet-600 to-teal-500 bg-clip-text text-transparent">0%</div>
              <p className="mt-2 text-xs text-gray-600">No engagement data yet</p>
            </div>
          </div>

          <div className="group relative overflow-hidden rounded-2xl border border-gray-200 bg-white p-6 shadow-md hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
            <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-teal-400/20 to-transparent rounded-bl-full"></div>
            <div className="relative">
              <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <span className="text-2xl">🔗</span>
                Platforms
              </div>
              <div className="mt-3 text-4xl font-bold bg-gradient-to-r from-teal-600 to-violet-500 bg-clip-text text-transparent">0</div>
              <p className="mt-2 text-xs text-gray-600">Connect platforms to start</p>
            </div>
          </div>
        </div>

        {/* Getting Started - Premium Card */}
        <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-lg">
          <div className="flex items-center gap-3 mb-6">
            <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-violet-600 text-white text-2xl shadow-lg">
              🚀
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-900">Getting Started</h3>
              <p className="text-gray-700">
                Complete these steps to start automating your marketing
              </p>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="group flex items-start gap-4 rounded-xl border-2 border-violet-300 bg-gradient-to-r from-violet-50 to-transparent p-5 transition-all hover:border-violet-400 hover:shadow-md">
              <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-violet-600 to-violet-500 text-lg font-bold text-white shadow-lg">
                1
              </div>
              <div className="flex-1">
                <div className="font-semibold text-gray-900 text-lg">Describe your business</div>
                <div className="mt-1 text-gray-700">
                  Tell us about your business so AI can create a custom strategy
                </div>
              </div>
              <button 
                onClick={() => router.push('/dashboard/settings')}
                className="opacity-0 group-hover:opacity-100 transition-opacity px-4 py-2 rounded-lg bg-violet-600 text-white font-medium hover:bg-violet-700"
              >
                Start →
              </button>
            </div>

            <div className="group flex items-start gap-4 rounded-xl border-2 border-gray-200 bg-white p-5 transition-all hover:border-violet-300 hover:shadow-md">
              <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-gray-200 text-lg font-bold text-gray-700">
                2
              </div>
              <div className="flex-1">
                <div className="font-semibold text-gray-900 text-lg">Connect social media accounts</div>
                <div className="mt-1 text-gray-700">
                  Link your LinkedIn, Twitter, and other platforms
                </div>
              </div>
              <button 
                onClick={() => router.push('/dashboard/settings')}
                className="opacity-0 group-hover:opacity-100 transition-opacity px-4 py-2 rounded-lg border-2 border-gray-300 text-gray-700 font-medium hover:bg-gray-50"
              >
                Connect
              </button>
            </div>

            <div className="group flex items-start gap-4 rounded-xl border-2 border-gray-200 bg-white p-5 transition-all hover:border-violet-300 hover:shadow-md">
              <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-gray-200 text-lg font-bold text-gray-700">
                3
              </div>
              <div className="flex-1">
                <div className="font-semibold text-gray-900 text-lg">Generate your first content</div>
                <div className="mt-1 text-gray-700">
                  Let AI create engaging posts for your audience
                </div>
              </div>
              <button 
                onClick={() => router.push('/dashboard/strategies')}
                className="opacity-0 group-hover:opacity-100 transition-opacity px-4 py-2 rounded-lg border-2 border-gray-300 text-gray-700 font-medium hover:bg-gray-50"
              >
                Create
              </button>
            </div>
          </div>
        </div>

        {/* Quick Actions - New Section */}
        <div className="mt-8 grid gap-6 md:grid-cols-3">
          <button 
            onClick={() => router.push('/dashboard/strategies')}
            className="group rounded-2xl border-2 border-dashed border-gray-300 bg-white p-6 text-left hover:border-violet-400 hover:bg-violet-50 transition-all duration-300"
          >
            <div className="text-3xl mb-3">✨</div>
            <h4 className="font-semibold text-gray-900 mb-2">Generate AI Content</h4>
            <p className="text-sm text-gray-700">Create engaging posts with AI assistance</p>
          </button>

          <button 
            onClick={() => router.push('/dashboard/analytics')}
            className="group rounded-2xl border-2 border-dashed border-gray-300 bg-white p-6 text-left hover:border-teal-400 hover:bg-teal-50 transition-all duration-300"
          >
            <div className="text-3xl mb-3">📊</div>
            <h4 className="font-semibold text-gray-900 mb-2">View Analytics</h4>
            <p className="text-sm text-gray-700">Track your social media performance</p>
          </button>

          <button 
            onClick={() => router.push('/dashboard/scheduled')}
            className="group rounded-2xl border-2 border-dashed border-gray-300 bg-white p-6 text-left hover:border-violet-400 hover:bg-violet-50 transition-all duration-300"
          >
            <div className="text-3xl mb-3">📅</div>
            <h4 className="font-semibold text-gray-900 mb-2">Schedule Posts</h4>
            <p className="text-sm text-gray-700">Plan your content calendar ahead</p>
          </button>
        </div>
      </div>
    </div>
  );
}
