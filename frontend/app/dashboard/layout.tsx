'use client';

import { useState } from 'react';
import { UserButton } from '@clerk/nextjs';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { BarChart3, BookmarkPlus, Calendar, FileText, Home, Settings, Target, Layers, Menu, X } from 'lucide-react';
import { OnboardingProvider } from '@/contexts/OnboardingContext';
import OnboardingChecklist from '@/components/OnboardingChecklist';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Home },
    { name: 'Strategies', href: '/dashboard/strategies', icon: Target },
    { name: 'Content', href: '/dashboard/content', icon: FileText },
    { name: 'Templates', href: '/dashboard/templates', icon: Layers },
    { name: 'Library', href: '/dashboard/library', icon: BookmarkPlus },
    { name: 'Calendar', href: '/dashboard/calendar', icon: Calendar },
    { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart3 },
    { name: 'Settings', href: '/dashboard/settings', icon: Settings },
  ];

  return (
    <OnboardingProvider>
      <div className="flex min-h-screen bg-gray-50">
        {/* Mobile Sidebar Overlay */}
        {mobileMenuOpen && (
          <div 
            className="fixed inset-0 z-40 bg-black bg-opacity-50 md:hidden"
            onClick={() => setMobileMenuOpen(false)}
          />
        )}

        {/* Sidebar */}
        <aside className={`
          fixed inset-y-0 left-0 z-50 w-64 transform bg-white border-r transition-transform duration-300 ease-in-out
          md:relative md:translate-x-0 md:flex md:flex-col
          ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}
        `}>
        <div className="flex h-16 items-center justify-between border-b px-6">
          <div className="flex items-center gap-2">
            <Target className="h-6 w-6 text-blue-600" />
            <span className="text-lg font-bold">AI Growth Manager</span>
          </div>
          <button
            onClick={() => setMobileMenuOpen(false)}
            className="md:hidden rounded-lg p-2 hover:bg-gray-100"
          >
            <X className="h-5 w-5 text-gray-600" />
          </button>
        </div>
        <nav className="flex-1 space-y-1 px-3 py-4">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium ${
                  isActive
                    ? 'bg-gray-100 text-gray-900'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`}
              >
                <item.icon className="h-5 w-5" />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex flex-1 flex-col">
        {/* Header */}
        <header className="flex h-16 items-center justify-between border-b bg-white px-4 md:px-6">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="md:hidden rounded-lg p-2 hover:bg-gray-100"
            >
              <Menu className="h-5 w-5 text-gray-600" />
            </button>
            <h1 className="text-lg md:text-xl font-semibold">
              {navigation.find((item) => item.href === pathname)?.name || 'Dashboard'}
            </h1>
          </div>
          <UserButton afterSignOutUrl="/" />
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto">{children}</main>
      </div>
    </div>

      {/* Onboarding Checklist */}
      <OnboardingChecklist />
    </OnboardingProvider>
  );
}
