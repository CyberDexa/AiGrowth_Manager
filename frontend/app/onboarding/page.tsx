'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
import { ArrowRight } from 'lucide-react';
import { api } from '@/lib/api';

export default function OnboardingPage() {
  const router = useRouter();
  const { getToken } = useAuth();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    businessName: '',
    businessDescription: '',
    targetAudience: '',
    goals: '',
  });

  const handleNext = async () => {
    if (step < 3) {
      setStep(step + 1);
    } else {
      // Complete onboarding - save to backend
      try {
        setLoading(true);
        setError(null);
        
        const token = await getToken();
        if (!token) {
          throw new Error('Authentication required');
        }

        await api.businesses.create({
          name: formData.businessName,
          description: formData.businessDescription,
          target_audience: formData.targetAudience,
          marketing_goals: formData.goals,
        }, token);

        // Success - redirect to dashboard
        router.push('/dashboard');
      } catch (err) {
        console.error('Failed to save business:', err);
        setError(err instanceof Error ? err.message : 'Failed to save business information');
        setLoading(false);
      }
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const updateFormData = (field: string, value: string) => {
    setFormData({ ...formData, [field]: value });
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-gray-50 to-white p-4">
      <div className="w-full max-w-2xl">
        {/* Progress Steps */}
        <div className="mb-8 flex items-center justify-center gap-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center gap-2">
              <div
                className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold ${
                  i === step
                    ? 'bg-blue-600 text-white'
                    : i < step
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}
              >
                {i < step ? '✓' : i}
              </div>
              {i < 3 && (
                <div className={`h-1 w-12 ${i < step ? 'bg-green-600' : 'bg-gray-200'}`} />
              )}
            </div>
          ))}
        </div>

        {/* Card */}
        <div className="rounded-xl border bg-white p-8 shadow-sm">
          {step === 1 && (
            <div>
              <h2 className="text-2xl font-bold">Tell us about your business</h2>
              <p className="mt-2 text-gray-600">
                Help us understand your business so we can create a personalized marketing
                strategy.
              </p>

              <div className="mt-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Business Name
                  </label>
                  <input
                    type="text"
                    value={formData.businessName}
                    onChange={(e) => updateFormData('businessName', e.target.value)}
                    className="mt-1 w-full rounded-lg border px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Acme Inc."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Business Description
                  </label>
                  <textarea
                    value={formData.businessDescription}
                    onChange={(e) => updateFormData('businessDescription', e.target.value)}
                    rows={4}
                    className="mt-1 w-full rounded-lg border px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="We provide..."
                  />
                </div>
              </div>
            </div>
          )}

          {step === 2 && (
            <div>
              <h2 className="text-2xl font-bold">Who is your target audience?</h2>
              <p className="mt-2 text-gray-600">
                Understanding your audience helps us create content that resonates.
              </p>

              <div className="mt-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Target Audience
                  </label>
                  <textarea
                    value={formData.targetAudience}
                    onChange={(e) => updateFormData('targetAudience', e.target.value)}
                    rows={4}
                    className="mt-1 w-full rounded-lg border px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Small business owners, entrepreneurs, etc."
                  />
                  <p className="mt-1 text-sm text-gray-500">
                    Describe demographics, interests, pain points
                  </p>
                </div>
              </div>
            </div>
          )}

          {step === 3 && (
            <div>
              <h2 className="text-2xl font-bold">What are your marketing goals?</h2>
              <p className="mt-2 text-gray-600">
                Let us know what you want to achieve with your marketing efforts.
              </p>

              <div className="mt-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Marketing Goals
                  </label>
                  <textarea
                    value={formData.goals}
                    onChange={(e) => updateFormData('goals', e.target.value)}
                    rows={4}
                    className="mt-1 w-full rounded-lg border px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Increase brand awareness, generate leads, etc."
                  />
                  <p className="mt-1 text-sm text-gray-500">
                    What do you want to accomplish in the next 3-6 months?
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mt-4 rounded-lg bg-red-50 p-4 text-sm text-red-600">
              {error}
            </div>
          )}

          {/* Actions */}
          <div className="mt-8 flex items-center justify-between">
            <button
              onClick={handleBack}
              disabled={step === 1 || loading}
              className="rounded-lg px-6 py-2 font-medium text-gray-700 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Back
            </button>
            <button
              onClick={handleNext}
              disabled={loading}
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-2 font-semibold text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <span className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  Saving...
                </>
              ) : (
                <>
                  {step === 3 ? 'Get Started' : 'Continue'}
                  <ArrowRight className="h-5 w-5" />
                </>
              )}
            </button>
          </div>
        </div>

        {/* Skip */}
        <div className="mt-4 text-center">
          <button
            onClick={() => router.push('/dashboard')}
            className="text-sm text-gray-600 hover:text-gray-900"
          >
            Skip for now
          </button>
        </div>
      </div>
    </div>
  );
}
