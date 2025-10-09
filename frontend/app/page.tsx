import Link from 'next/link';
import { ArrowRight, Sparkles, Target, TrendingUp, Zap } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <header className="border-b bg-white/50 backdrop-blur-sm">
        <div className="container mx-auto flex items-center justify-between px-4 py-4">
          <div className="flex items-center space-x-2">
            <Sparkles className="h-8 w-8 text-blue-600" />
            <span className="text-xl font-bold">AI Growth Manager</span>
          </div>
          <nav className="hidden md:flex items-center space-x-6">
            <Link href="#features" className="text-gray-600 hover:text-gray-900">
              Features
            </Link>
            <Link href="#pricing" className="text-gray-600 hover:text-gray-900">
              Pricing
            </Link>
            <Link href="/sign-in" className="text-gray-600 hover:text-gray-900">
              Sign In
            </Link>
            <Link
              href="/sign-up"
              className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
            >
              Get Started
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="mx-auto max-w-4xl">
          <h1 className="text-5xl font-bold tracking-tight text-gray-900 sm:text-6xl">
            Your AI-Powered
            <span className="text-blue-600"> Marketing Team</span>
          </h1>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            Stop struggling with marketing. Our AI builds strategies, creates content,
            and runs campaigns automatically. Get more customers while you focus on
            building your business.
          </p>
          <div className="mt-10 flex items-center justify-center gap-x-6">
            <Link
              href="/sign-up"
              className="rounded-lg bg-blue-600 px-6 py-3 text-lg font-semibold text-white hover:bg-blue-700 flex items-center gap-2"
            >
              Start Free Trial
              <ArrowRight className="h-5 w-5" />
            </Link>
            <Link
              href="#features"
              className="text-lg font-semibold text-gray-900 hover:text-gray-700"
            >
              Learn more <span aria-hidden="true">→</span>
            </Link>
          </div>
          
          {/* Social Proof */}
          <div className="mt-10 flex items-center justify-center gap-x-8 text-sm text-gray-600">
            <div className="flex items-center gap-1">
              <span className="font-semibold text-gray-900">14-day</span> free trial
            </div>
            <div className="flex items-center gap-1">
              No credit card required
            </div>
            <div className="flex items-center gap-1">
              Cancel anytime
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="container mx-auto px-4 py-20">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">
            Everything you need to grow
          </h2>
          <p className="mt-4 text-lg text-gray-600">
            An autonomous AI marketing system that works 24/7
          </p>
        </div>

        <div className="mt-16 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {/* Feature 1 */}
          <div className="rounded-xl border bg-white p-8 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
              <Target className="h-6 w-6 text-blue-600" />
            </div>
            <h3 className="mt-4 text-xl font-semibold text-gray-900">
              AI Strategy Builder
            </h3>
            <p className="mt-2 text-gray-600">
              Describe your business and get a complete marketing strategy tailored
              to your goals and audience.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="rounded-xl border bg-white p-8 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-green-100">
              <Sparkles className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="mt-4 text-xl font-semibold text-gray-900">
              Content Generation
            </h3>
            <p className="mt-2 text-gray-600">
              Generate engaging posts, threads, and articles for all your social
              media platforms in seconds.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="rounded-xl border bg-white p-8 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-purple-100">
              <Zap className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="mt-4 text-xl font-semibold text-gray-900">
              Auto-Posting
            </h3>
            <p className="mt-2 text-gray-600">
              Schedule and publish content automatically to LinkedIn, Twitter,
              Facebook, and Instagram.
            </p>
          </div>

          {/* Feature 4 */}
          <div className="rounded-xl border bg-white p-8 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-orange-100">
              <TrendingUp className="h-6 w-6 text-orange-600" />
            </div>
            <h3 className="mt-4 text-xl font-semibold text-gray-900">
              Performance Analytics
            </h3>
            <p className="mt-2 text-gray-600">
              Track engagement, reach, and conversions. Know what's working and
              what's not.
            </p>
          </div>

          {/* Feature 5 */}
          <div className="rounded-xl border bg-white p-8 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-red-100">
              <Target className="h-6 w-6 text-red-600" />
            </div>
            <h3 className="mt-4 text-xl font-semibold text-gray-900">
              Smart Optimization
            </h3>
            <p className="mt-2 text-gray-600">
              AI learns from your results and continuously improves your content
              and posting times.
            </p>
          </div>

          {/* Feature 6 */}
          <div className="rounded-xl border bg-white p-8 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-indigo-100">
              <Sparkles className="h-6 w-6 text-indigo-600" />
            </div>
            <h3 className="mt-4 text-xl font-semibold text-gray-900">
              Multi-Platform Support
            </h3>
            <p className="mt-2 text-gray-600">
              Manage all your social media from one place. LinkedIn, Twitter, Meta,
              and more.
            </p>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="bg-gray-50 py-20">
        <div className="container mx-auto px-4">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900">
              Simple, transparent pricing
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              Start free, upgrade as you grow
            </p>
          </div>

          <div className="mt-16 grid gap-8 lg:grid-cols-3">
            {/* Free Plan */}
            <div className="rounded-xl border bg-white p-8 shadow-sm">
              <h3 className="text-xl font-semibold">Free</h3>
              <p className="mt-2 text-sm text-gray-600">Perfect to get started</p>
              <p className="mt-4 text-4xl font-bold">$0</p>
              <p className="text-gray-600">forever</p>
              <ul className="mt-6 space-y-3">
                <li className="flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  <span>10 AI-generated posts/month</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  <span>1 platform connection</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Basic analytics</span>
                </li>
              </ul>
              <Link
                href="/sign-up"
                className="mt-8 block rounded-lg border-2 border-gray-300 px-4 py-2 text-center font-semibold hover:border-gray-400"
              >
                Get Started
              </Link>
            </div>

            {/* Pro Plan */}
            <div className="rounded-xl border-2 border-blue-600 bg-white p-8 shadow-lg relative">
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 rounded-full bg-blue-600 px-3 py-1 text-sm font-semibold text-white">
                Most Popular
              </div>
              <h3 className="text-xl font-semibold">Pro</h3>
              <p className="mt-2 text-sm text-gray-600">For growing businesses</p>
              <p className="mt-4 text-4xl font-bold">$29</p>
              <p className="text-gray-600">per month</p>
              <ul className="mt-6 space-y-3">
                <li className="flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Unlimited AI posts</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  <span>3 platform connections</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Advanced analytics</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Auto-scheduling</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Priority support</span>
                </li>
              </ul>
              <Link
                href="/sign-up"
                className="mt-8 block rounded-lg bg-blue-600 px-4 py-2 text-center font-semibold text-white hover:bg-blue-700"
              >
                Start Free Trial
              </Link>
            </div>

            {/* Enterprise Plan */}
            <div className="rounded-xl border bg-white p-8 shadow-sm">
              <h3 className="text-xl font-semibold">Enterprise</h3>
              <p className="mt-2 text-sm text-gray-600">For larger teams</p>
              <p className="mt-4 text-4xl font-bold">$99</p>
              <p className="text-gray-600">per month</p>
              <ul className="mt-6 space-y-3">
                <li className="flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Everything in Pro</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Unlimited platforms</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Team collaboration</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  <span>API access</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  <span>Dedicated support</span>
                </li>
              </ul>
              <Link
                href="/sign-up"
                className="mt-8 block rounded-lg border-2 border-gray-300 px-4 py-2 text-center font-semibold hover:border-gray-400"
              >
                Contact Sales
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="mx-auto max-w-2xl">
          <h2 className="text-3xl font-bold text-gray-900">
            Ready to grow your business?
          </h2>
          <p className="mt-4 text-lg text-gray-600">
            Join hundreds of small businesses using AI to automate their marketing
          </p>
          <Link
            href="/sign-up"
            className="mt-8 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-8 py-4 text-lg font-semibold text-white hover:bg-blue-700"
          >
            Start Free Trial
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-gray-50">
        <div className="container mx-auto px-4 py-12">
          <div className="text-center text-sm text-gray-600">
            <p>&copy; 2025 AI Growth Manager. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
