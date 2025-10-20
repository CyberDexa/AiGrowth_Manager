import Link from 'next/link';
import { 
  ArrowRight, 
  Sparkles, 
  Target, 
  TrendingUp, 
  Zap, 
  FileText, 
  Calendar, 
  BarChart3, 
  BookOpen, 
  Clock, 
  CheckCircle2 
} from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-violet-50 to-teal-50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white/80 backdrop-blur-md shadow-sm">
        <div className="container mx-auto flex items-center justify-between px-4 py-4">
          <div className="flex items-center space-x-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-violet-500 shadow-lg">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-violet-600 to-teal-600 bg-clip-text text-transparent">
              AI Growth Manager
            </span>
          </div>
          <nav className="hidden md:flex items-center space-x-6">
            <Link href="#features" className="text-gray-700 hover:text-violet-600 transition-colors font-medium">
              Features
            </Link>
            <Link href="#pricing" className="text-gray-700 hover:text-violet-600 transition-colors font-medium">
              Pricing
            </Link>
            <Link href="/sign-in" className="text-gray-700 hover:text-violet-600 transition-colors font-medium">
              Sign In
            </Link>
            <Link
              href="/sign-up"
              className="rounded-xl bg-gradient-to-r from-violet-600 to-violet-500 px-5 py-2.5 text-white hover:from-violet-700 hover:to-violet-600 transition-all shadow-md hover:shadow-lg font-semibold"
            >
              Get Started
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="mx-auto max-w-4xl">
          <div className="inline-block mb-6 rounded-full bg-gradient-to-r from-violet-100 to-teal-100 px-4 py-2 text-sm font-semibold text-violet-700">
            🚀 AI-Powered Marketing Automation
          </div>
          <h1 className="text-5xl font-bold tracking-tight text-gray-900 sm:text-6xl lg:text-7xl">
            Your AI-Powered
            <span className="block mt-2 bg-gradient-to-r from-violet-600 via-violet-500 to-teal-500 bg-clip-text text-transparent">
              Marketing Team
            </span>
          </h1>
          <p className="mt-8 text-xl leading-8 text-gray-700 max-w-3xl mx-auto">
            Stop struggling with marketing. Our AI builds strategies, creates content,
            and runs campaigns automatically. Get more customers while you focus on
            building your business.
          </p>
          <div className="mt-12 flex items-center justify-center gap-x-6">
            <Link
              href="/sign-up"
              className="group rounded-xl bg-gradient-to-r from-violet-600 to-violet-500 px-8 py-4 text-lg font-semibold text-white hover:from-violet-700 hover:to-violet-600 transition-all shadow-lg hover:shadow-xl flex items-center gap-2"
            >
              Start Free Trial
              <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              href="#features"
              className="text-lg font-semibold text-gray-800 hover:text-violet-600 transition-colors flex items-center gap-2"
            >
              Learn more 
              <span className="text-violet-500">→</span>
            </Link>
          </div>
          
          {/* Social Proof */}
          <div className="mt-12 flex flex-wrap items-center justify-center gap-8 text-sm text-gray-700">
            <div className="flex items-center gap-2 bg-white rounded-full px-4 py-2 shadow-sm">
              <span className="text-2xl">✨</span>
              <span className="font-semibold text-violet-600">14-day</span> free trial
            </div>
            <div className="flex items-center gap-2 bg-white rounded-full px-4 py-2 shadow-sm">
              <span className="text-2xl">🎯</span>
              No credit card required
            </div>
            <div className="flex items-center gap-2 bg-white rounded-full px-4 py-2 shadow-sm">
              <span className="text-2xl">🔓</span>
              Cancel anytime
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="container mx-auto px-4 py-20">
        <div className="text-center">
          <h2 className="text-4xl font-bold text-gray-900">
            Everything you need to grow your business
          </h2>
          <p className="mt-4 text-xl text-gray-700">
            A complete autonomous AI marketing system that works 24/7 so you don&apos;t have to
          </p>
        </div>

        <div className="mt-16 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {/* Feature 1: AI Strategy Generation - Coming Soon */}
          <div className="group rounded-2xl border-2 border-gray-200 bg-white p-8 hover:border-violet-300 hover:shadow-xl transition-all duration-300 relative">
            <div className="absolute top-4 right-4">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-violet-100 text-violet-700">
                Coming Soon
              </span>
            </div>
            <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-violet-600 shadow-lg group-hover:scale-110 transition-transform">
              <Target className="h-7 w-7 text-white" />
            </div>
            <h3 className="mt-6 text-xl font-bold text-gray-900">
              🎯 AI Strategy Generation
            </h3>
            <p className="mt-3 text-gray-700 leading-relaxed">
              Our AI will analyze your business and create a custom 12-week marketing
              strategy with content pillars, target audiences, and growth tactics tailored to your goals.
            </p>
          </div>

          {/* Feature 2: AI Content Creation */}
          <div className="group rounded-2xl border-2 border-gray-200 bg-white p-8 hover:border-teal-300 hover:shadow-xl transition-all duration-300">
            <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-teal-500 to-teal-600 shadow-lg group-hover:scale-110 transition-transform">
              <Sparkles className="h-7 w-7 text-white" />
            </div>
            <h3 className="mt-6 text-xl font-bold text-gray-900">
              ✨ AI Content Creation
            </h3>
            <p className="mt-3 text-gray-700 leading-relaxed">
              Generate platform-optimized posts in seconds. Our AI adapts content length
              and style for Twitter, LinkedIn, Facebook, and Instagram automatically.
            </p>
          </div>

          {/* Feature 3: Multi-Platform Publishing */}
          <div className="group rounded-2xl border-2 border-gray-200 bg-white p-8 hover:border-violet-300 hover:shadow-xl transition-all duration-300">
            <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-teal-500 shadow-lg group-hover:scale-110 transition-transform">
              <Zap className="h-7 w-7 text-white" />
            </div>
            <h3 className="mt-6 text-xl font-bold text-gray-900">
              ⚡ Multi-Platform Publishing
            </h3>
            <p className="mt-3 text-gray-700 leading-relaxed">
              Publish to all your social accounts with one click. Schedule posts or
              publish immediately to Twitter, LinkedIn, Facebook, and Instagram.
            </p>
          </div>

          {/* Feature 4: Content Templates */}
          <div className="group rounded-2xl border-2 border-gray-200 bg-white p-8 hover:border-teal-300 hover:shadow-xl transition-all duration-300">
            <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-teal-600 to-violet-500 shadow-lg group-hover:scale-110 transition-transform">
              <FileText className="h-7 w-7 text-white" />
            </div>
            <h3 className="mt-6 text-xl font-bold text-gray-900">
              📝 Content Templates
            </h3>
            <p className="mt-3 text-gray-700 leading-relaxed">
              Create reusable templates for product launches, promotions, and announcements.
              Fill in placeholders and generate consistent content in seconds.
            </p>
          </div>

          {/* Feature 5: Analytics Dashboard */}
          <div className="group rounded-2xl border-2 border-gray-200 bg-white p-8 hover:border-violet-300 hover:shadow-xl transition-all duration-300">
            <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-violet-700 shadow-lg group-hover:scale-110 transition-transform">
              <BarChart3 className="h-7 w-7 text-white" />
            </div>
            <h3 className="mt-6 text-xl font-bold text-gray-900">
              📊 Analytics Dashboard
            </h3>
            <p className="mt-3 text-gray-700 leading-relaxed">
              Track reach, engagement, and growth across all platforms. Beautiful charts
              show what content performs best and when to post for maximum impact.
            </p>
          </div>

          {/* Feature 6: Posting Time Recommendations */}
          <div className="group rounded-2xl border-2 border-gray-200 bg-white p-8 hover:border-teal-300 hover:shadow-xl transition-all duration-300">
            <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-teal-500 to-teal-700 shadow-lg group-hover:scale-110 transition-transform">
              <Clock className="h-7 w-7 text-white" />
            </div>
            <h3 className="mt-6 text-xl font-bold text-gray-900">
              ⏰ Smart Posting Times
            </h3>
            <p className="mt-3 text-gray-700 leading-relaxed">
              AI analyzes your audience engagement patterns and recommends the best times
              to post on each platform for maximum reach and interaction.
            </p>
          </div>

          {/* Feature 7: Content Library */}
          <div className="group rounded-2xl border-2 border-gray-200 bg-white p-8 hover:border-violet-300 hover:shadow-xl transition-all duration-300">
            <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-violet-500 shadow-lg group-hover:scale-110 transition-transform">
              <BookOpen className="h-7 w-7 text-white" />
            </div>
            <h3 className="mt-6 text-xl font-bold text-gray-900">
              📚 Content Library
            </h3>
            <p className="mt-3 text-gray-700 leading-relaxed">
              Save your best-performing content for reuse. Build a library of proven posts
              and adapt them for future campaigns.
            </p>
          </div>

          {/* Feature 8: Scheduled Calendar */}
          <div className="group rounded-2xl border-2 border-gray-200 bg-white p-8 hover:border-teal-300 hover:shadow-xl transition-all duration-300">
            <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-teal-600 to-teal-500 shadow-lg group-hover:scale-110 transition-transform">
              <Calendar className="h-7 w-7 text-white" />
            </div>
            <h3 className="mt-6 text-xl font-bold text-gray-900">
              📅 Visual Calendar
            </h3>
            <p className="mt-3 text-gray-700 leading-relaxed">
              See all your scheduled posts at a glance. Drag and drop to reschedule,
              edit upcoming content, and maintain a consistent posting rhythm.
            </p>
          </div>

          {/* Feature 9: Guided Onboarding */}
          <div className="group rounded-2xl border-2 border-gray-200 bg-white p-8 hover:border-violet-300 hover:shadow-xl transition-all duration-300">
            <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-teal-500 shadow-lg group-hover:scale-110 transition-transform">
              <CheckCircle2 className="h-7 w-7 text-white" />
            </div>
            <h3 className="mt-6 text-xl font-bold text-gray-900">
              ✅ Guided Onboarding
            </h3>
            <p className="mt-3 text-gray-700 leading-relaxed">
              Interactive checklist walks you through setup step-by-step. Connect accounts,
              create your first strategy, and publish content in under 10 minutes.
            </p>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="bg-gradient-to-br from-gray-50 to-violet-50/20 py-24">
        <div className="container mx-auto px-4">
          <div className="text-center">
            <h2 className="text-4xl font-bold text-gray-900">
              Simple, transparent pricing
            </h2>
            <p className="mt-4 text-xl text-gray-700">
              Start free, upgrade as you grow
            </p>
          </div>

          <div className="mt-16 grid gap-8 lg:grid-cols-3 max-w-6xl mx-auto">
            {/* Free Plan */}
            <div className="rounded-2xl border-2 border-gray-200 bg-white p-8 shadow-md hover:shadow-xl transition-all">
              <h3 className="text-2xl font-bold text-gray-900">Free</h3>
              <p className="mt-2 text-sm text-gray-700">Perfect to get started</p>
              <p className="mt-6 text-5xl font-bold text-gray-900">$0</p>
              <p className="text-gray-700 font-medium">forever</p>
              <ul className="mt-8 space-y-4">
                <li className="flex items-start gap-3">
                  <span className="text-xl text-teal-500">✓</span>
                  <span className="text-gray-800">10 AI-generated posts/month</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-xl text-teal-500">✓</span>
                  <span className="text-gray-800">1 platform connection</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-xl text-teal-500">✓</span>
                  <span className="text-gray-800">Basic analytics</span>
                </li>
              </ul>
              <Link
                href="/sign-up"
                className="mt-8 block rounded-xl border-2 border-gray-300 px-6 py-3 text-center font-semibold hover:border-violet-400 hover:bg-violet-50 transition-all"
              >
                Get Started
              </Link>
            </div>

            {/* Pro Plan */}
            <div className="rounded-2xl border-2 border-violet-500 bg-white p-8 shadow-xl relative transform lg:scale-105">
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 rounded-full bg-gradient-to-r from-violet-600 to-violet-500 px-4 py-1.5 text-sm font-bold text-white shadow-lg">
                Most Popular
              </div>
              <h3 className="text-2xl font-bold text-gray-900">Pro</h3>
              <p className="mt-2 text-sm text-gray-700">For growing businesses</p>
              <p className="mt-6 text-5xl font-bold bg-gradient-to-r from-violet-600 to-teal-600 bg-clip-text text-transparent">$29</p>
              <p className="text-gray-700 font-medium">per month</p>
              <ul className="mt-8 space-y-4">
                <li className="flex items-start gap-3">
                  <span className="text-xl text-violet-500">✓</span>
                  <span className="text-gray-800 font-medium">Unlimited AI posts</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-xl text-violet-500">✓</span>
                  <span className="text-gray-800 font-medium">3 platform connections</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-xl text-violet-500">✓</span>
                  <span className="text-gray-800 font-medium">Advanced analytics</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-xl text-violet-500">✓</span>
                  <span className="text-gray-800 font-medium">Auto-scheduling</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-xl text-violet-500">✓</span>
                  <span className="text-gray-800 font-medium">Priority support</span>
                </li>
              </ul>
              <Link
                href="/sign-up"
                className="mt-8 block rounded-xl bg-gradient-to-r from-violet-600 to-violet-500 px-6 py-3 text-center font-bold text-white hover:from-violet-700 hover:to-violet-600 shadow-lg hover:shadow-xl transition-all"
              >
                Start Free Trial
              </Link>
            </div>

            {/* Enterprise Plan */}
            <div className="rounded-2xl border-2 border-gray-200 bg-white p-8 shadow-md hover:shadow-xl transition-all">
              <h3 className="text-2xl font-bold text-gray-900">Enterprise</h3>
              <p className="mt-2 text-sm text-gray-700">For larger teams</p>
              <p className="mt-6 text-5xl font-bold text-gray-900">$99</p>
              <p className="text-gray-700 font-medium">per month</p>
              <ul className="mt-8 space-y-4">
                <li className="flex items-start gap-3">
                  <span className="text-xl text-teal-500">✓</span>
                  <span className="text-gray-800">Everything in Pro</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-xl text-teal-500">✓</span>
                  <span className="text-gray-800">Unlimited platforms</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-xl text-teal-500">✓</span>
                  <span className="text-gray-800">Team collaboration</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-xl text-teal-500">✓</span>
                  <span className="text-gray-800">API access</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-xl text-teal-500">✓</span>
                  <span className="text-gray-800">Dedicated support</span>
                </li>
              </ul>
              <Link
                href="/sign-up"
                className="mt-8 block rounded-xl border-2 border-gray-300 px-6 py-3 text-center font-semibold hover:border-violet-400 hover:bg-violet-50 transition-all"
              >
                Contact Sales
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-24 text-center">
        <div className="mx-auto max-w-3xl rounded-3xl bg-gradient-to-r from-violet-600 via-violet-500 to-teal-500 p-12 shadow-2xl">
          <h2 className="text-4xl font-bold text-white">
            Ready to grow your business?
          </h2>
          <p className="mt-4 text-xl text-violet-100">
            Join hundreds of small businesses using AI to automate their marketing
          </p>
          <Link
            href="/sign-up"
            className="mt-8 inline-flex items-center gap-2 rounded-xl bg-white px-8 py-4 text-lg font-bold text-violet-600 hover:bg-gray-50 shadow-xl transition-all hover:scale-105"
          >
            Start Free Trial
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white">
        <div className="container mx-auto px-4 py-12">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-violet-600 to-violet-500">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <span className="text-lg font-bold bg-gradient-to-r from-violet-600 to-teal-600 bg-clip-text text-transparent">
                AI Growth Manager
              </span>
            </div>
            <p className="text-sm text-gray-700">
              &copy; 2025 AI Growth Manager. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
