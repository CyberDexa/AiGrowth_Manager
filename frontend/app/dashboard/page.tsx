'use client';

import { UserButton } from '@clerk/nextjs';
import Link from 'next/link';
import { BarChart3, FileText, Home, Settings, Target } from 'lucide-react';

export default function DashboardPage() {
  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="hidden md:flex md:w-64 md:flex-col border-r bg-white">
        <div className="flex h-16 items-center gap-2 border-b px-6">
          <Target className="h-6 w-6 text-blue-600" />
          <span className="text-lg font-bold">AI Growth Manager</span>
        </div>
        <nav className="flex-1 space-y-1 px-3 py-4">
          <Link
            href="/dashboard"
            className="flex items-center gap-3 rounded-lg bg-gray-100 px-3 py-2 text-sm font-medium text-gray-900"
          >
            <Home className="h-5 w-5" />
            Dashboard
          </Link>
          <Link
            href="/strategies"
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900"
          >
            <Target className="h-5 w-5" />
            Strategies
          </Link>
          <Link
            href="/content"
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900"
          >
            <FileText className="h-5 w-5" />
            Content
          </Link>
          <Link
            href="/analytics"
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900"
          >
            <BarChart3 className="h-5 w-5" />
            Analytics
          </Link>
          <Link
            href="/settings"
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900"
          >
            <Settings className="h-5 w-5" />
            Settings
          </Link>
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex flex-1 flex-col">
        {/* Header */}
        <header className="flex h-16 items-center justify-between border-b bg-white px-6">
          <h1 className="text-xl font-semibold">Dashboard</h1>
          <UserButton afterSignOutUrl="/" />
        </header>

        {/* Page Content */}
        <main className="flex-1 p-6">
          <div className="mx-auto max-w-7xl">
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-gray-900">Welcome Back!</h2>
              <p className="mt-1 text-gray-600">
                Here's what's happening with your marketing today.
              </p>
            </div>

            {/* Stats Grid */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              <div className="rounded-lg border bg-white p-6">
                <div className="text-sm font-medium text-gray-600">Total Posts</div>
                <div className="mt-2 text-3xl font-bold">0</div>
                <p className="mt-1 text-xs text-gray-500">No posts created yet</p>
              </div>
              <div className="rounded-lg border bg-white p-6">
                <div className="text-sm font-medium text-gray-600">Reach</div>
                <div className="mt-2 text-3xl font-bold">0</div>
                <p className="mt-1 text-xs text-gray-500">Start posting to track reach</p>
              </div>
              <div className="rounded-lg border bg-white p-6">
                <div className="text-sm font-medium text-gray-600">Engagement</div>
                <div className="mt-2 text-3xl font-bold">0%</div>
                <p className="mt-1 text-xs text-gray-500">No engagement data yet</p>
              </div>
              <div className="rounded-lg border bg-white p-6">
                <div className="text-sm font-medium text-gray-600">Platforms</div>
                <div className="mt-2 text-3xl font-bold">0</div>
                <p className="mt-1 text-xs text-gray-500">Connect platforms to start</p>
              </div>
            </div>

            {/* Getting Started */}
            <div className="mt-8 rounded-lg border bg-white p-6">
              <h3 className="text-lg font-semibold">Getting Started</h3>
              <p className="mt-2 text-gray-600">
                Complete these steps to start automating your marketing:
              </p>
              <div className="mt-4 space-y-3">
                <div className="flex items-center gap-3 rounded-lg border p-4">
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-sm font-semibold text-blue-600">
                    1
                  </div>
                  <div>
                    <div className="font-medium">Describe your business</div>
                    <div className="text-sm text-gray-600">
                      Tell us about your business so AI can create a custom strategy
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3 rounded-lg border p-4">
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-gray-100 text-sm font-semibold text-gray-600">
                    2
                  </div>
                  <div>
                    <div className="font-medium">Connect social media accounts</div>
                    <div className="text-sm text-gray-600">
                      Link your LinkedIn, Twitter, and other platforms
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3 rounded-lg border p-4">
                  <div className="flex h-6 w-6 items-center justify-center rounded-full bg-gray-100 text-sm font-semibold text-gray-600">
                    3
                  </div>
                  <div>
                    <div className="font-medium">Generate your first content</div>
                    <div className="text-sm text-gray-600">
                      Let AI create engaging posts for your audience
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
