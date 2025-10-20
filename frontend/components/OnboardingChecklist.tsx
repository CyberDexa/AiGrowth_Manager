'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useOnboarding } from '@/contexts/OnboardingContext';
import { 
  CheckCircle2, 
  Circle, 
  ChevronDown, 
  ChevronUp, 
  X,
  Sparkles,
  Trophy,
  Rocket
} from 'lucide-react';
import Confetti from 'react-confetti';

export default function OnboardingChecklist() {
  const { 
    steps, 
    isComplete, 
    showChecklist, 
    setShowChecklist 
  } = useOnboarding();
  
  const [isExpanded, setIsExpanded] = useState(true);
  const [showConfetti, setShowConfetti] = useState(false);
  const [windowSize, setWindowSize] = useState({ width: 0, height: 0 });

  // Track window size for confetti
  useEffect(() => {
    const updateWindowSize = () => {
      setWindowSize({ width: window.innerWidth, height: window.innerHeight });
    };
    
    updateWindowSize();
    window.addEventListener('resize', updateWindowSize);
    return () => window.removeEventListener('resize', updateWindowSize);
  }, []);

  // Show confetti when all steps complete
  useEffect(() => {
    if (isComplete && showChecklist) {
      setShowConfetti(true);
      setTimeout(() => setShowConfetti(false), 5000);
    }
  }, [isComplete, showChecklist]);

  if (!showChecklist) {
    return null;
  }

  const completedCount = steps.filter(s => s.completed).length;
  const progress = (completedCount / steps.length) * 100;

  return (
    <>
      {showConfetti && (
        <Confetti
          width={windowSize.width}
          height={windowSize.height}
          recycle={false}
          numberOfPieces={500}
          gravity={0.3}
        />
      )}
      
      <div className="fixed bottom-4 right-4 left-4 md:left-auto md:bottom-6 md:right-6 z-50 w-auto md:w-96 rounded-lg border border-gray-200 bg-white shadow-2xl max-w-md">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-200 p-4">
          <div className="flex items-center gap-2">
            {isComplete ? (
              <>
                <Trophy className="h-5 w-5 text-yellow-500" />
                <h3 className="font-semibold text-gray-900">All Done! 🎉</h3>
              </>
            ) : (
              <>
                <Rocket className="h-5 w-5 text-violet-600" />
                <h3 className="font-semibold text-gray-900">Getting Started</h3>
              </>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="rounded p-1 hover:bg-gray-100"
            >
              {isExpanded ? (
                <ChevronDown className="h-4 w-4 text-gray-600" />
              ) : (
                <ChevronUp className="h-4 w-4 text-gray-600" />
              )}
            </button>
            <button
              onClick={() => setShowChecklist(false)}
              className="rounded p-1 hover:bg-gray-100"
            >
              <X className="h-4 w-4 text-gray-600" />
            </button>
          </div>
        </div>

        {isExpanded && (
          <div className="p-4">
            {/* Progress */}
            <div className="mb-4">
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="font-medium text-gray-700">
                  {completedCount} of {steps.length} completed
                </span>
                <span className="text-gray-600">{Math.round(progress)}%</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-gray-200">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-violet-500 to-purple-500 transition-all duration-500"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            {/* Completion Message */}
            {isComplete ? (
              <div className="mb-4 rounded-lg bg-gradient-to-r from-violet-50 to-purple-50 p-4 text-center">
                <Sparkles className="mx-auto mb-2 h-8 w-8 text-violet-600" />
                <h4 className="mb-1 font-semibold text-gray-900">
                  Congratulations!
                </h4>
                <p className="text-sm text-gray-600">
                  You've completed the onboarding. Start growing your social media presence!
                </p>
              </div>
            ) : (
              <p className="mb-4 text-sm text-gray-600">
                Complete these steps to unlock the full power of AI Growth Manager
              </p>
            )}

            {/* Steps */}
            <div className="space-y-3">
              {steps.map((step, index) => (
                <div
                  key={step.id}
                  className={`rounded-lg border p-3 transition-all ${
                    step.completed
                      ? 'border-green-200 bg-green-50'
                      : 'border-gray-200 bg-white hover:border-violet-300 hover:bg-violet-50'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {/* Icon */}
                    <div className="mt-0.5">
                      {step.completed ? (
                        <CheckCircle2 className="h-5 w-5 text-green-600" />
                      ) : (
                        <Circle className="h-5 w-5 text-gray-400" />
                      )}
                    </div>

                    {/* Content */}
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4
                            className={`text-sm font-medium ${
                              step.completed ? 'text-green-900' : 'text-gray-900'
                            }`}
                          >
                            {step.title}
                          </h4>
                          <p
                            className={`mt-1 text-xs ${
                              step.completed ? 'text-green-700' : 'text-gray-600'
                            }`}
                          >
                            {step.description}
                          </p>
                        </div>
                        {!step.completed && (
                          <span className="ml-2 flex h-5 w-5 items-center justify-center rounded-full bg-violet-100 text-xs font-medium text-violet-700">
                            {index + 1}
                          </span>
                        )}
                      </div>

                      {/* Action Button */}
                      {!step.completed && step.actionUrl && (
                        <Link
                          href={step.actionUrl}
                          className="mt-2 inline-flex items-center gap-1 rounded bg-violet-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-violet-700"
                        >
                          {step.actionText || 'Get Started'}
                          <ChevronDown className="h-3 w-3 rotate-[-90deg]" />
                        </Link>
                      )}

                      {step.completed && (
                        <div className="mt-2 flex items-center gap-1 text-xs font-medium text-green-700">
                          <CheckCircle2 className="h-3 w-3" />
                          Completed
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Footer */}
            {!isComplete && (
              <div className="mt-4 rounded-lg bg-violet-50 p-3 text-center">
                <p className="text-xs text-violet-800">
                  💡 <strong>Pro tip:</strong> Complete all steps to maximize your results
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}
