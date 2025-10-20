'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

export interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  actionUrl?: string;
  actionText?: string;
}

interface OnboardingContextType {
  steps: OnboardingStep[];
  isComplete: boolean;
  showChecklist: boolean;
  setShowChecklist: (show: boolean) => void;
  completeStep: (stepId: string) => void;
  checkStepCompletion: () => Promise<void>;
  resetOnboarding: () => void;
}

const OnboardingContext = createContext<OnboardingContextType | undefined>(undefined);

const INITIAL_STEPS: OnboardingStep[] = [
  {
    id: 'business',
    title: 'Set up your business profile',
    description: 'Tell us about your business to get personalized content recommendations',
    completed: false,
    actionUrl: '/onboarding',
    actionText: 'Complete Setup',
  },
  {
    id: 'social_accounts',
    title: 'Connect social accounts',
    description: 'Link Twitter, LinkedIn, Facebook, or Instagram to start publishing',
    completed: false,
    actionUrl: '/dashboard/settings',
    actionText: 'Connect Accounts',
  },
  {
    id: 'strategy',
    title: 'Generate your first strategy',
    description: 'Let AI create a custom content strategy for your business',
    completed: false,
    actionUrl: '/dashboard/strategies',
    actionText: 'Create Strategy',
  },
  {
    id: 'content',
    title: 'Create your first content',
    description: 'Generate AI-powered posts tailored to your audience',
    completed: false,
    actionUrl: '/dashboard/content',
    actionText: 'Generate Content',
  },
  {
    id: 'publish',
    title: 'Publish your first post',
    description: 'Schedule or publish your content to social media',
    completed: false,
    actionUrl: '/dashboard/content',
    actionText: 'Publish Now',
  },
];

export function OnboardingProvider({ children }: { children: React.ReactNode }) {
  const [steps, setSteps] = useState<OnboardingStep[]>(INITIAL_STEPS);
  const [showChecklist, setShowChecklist] = useState(false);
  const [isComplete, setIsComplete] = useState(false);

  // Load saved progress from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('onboarding_progress');
    if (saved) {
      try {
        const savedSteps = JSON.parse(saved);
        setSteps(savedSteps);
        setIsComplete(savedSteps.every((s: OnboardingStep) => s.completed));
      } catch (e) {
        console.error('Failed to load onboarding progress:', e);
      }
    }
  }, []);

  // Save progress to localStorage whenever steps change
  useEffect(() => {
    localStorage.setItem('onboarding_progress', JSON.stringify(steps));
    setIsComplete(steps.every(s => s.completed));
  }, [steps]);

  // Auto-show checklist for new users
  useEffect(() => {
    const hasSeenChecklist = localStorage.getItem('has_seen_checklist');
    if (!hasSeenChecklist && !isComplete) {
      setShowChecklist(true);
      localStorage.setItem('has_seen_checklist', 'true');
    }
  }, [isComplete]);

  const completeStep = (stepId: string) => {
    setSteps(prev =>
      prev.map(step =>
        step.id === stepId ? { ...step, completed: true } : step
      )
    );
  };

  const checkStepCompletion = async () => {
    try {
      // Check business setup
      const businesses = localStorage.getItem('businesses');
      if (businesses) {
        const businessList = JSON.parse(businesses);
        if (businessList.length > 0) {
          completeStep('business');
        }
      }

      // Check social accounts (would need API call in real implementation)
      // For now, we'll check localStorage or could make API call
      
      // Check strategies
      const hasStrategies = localStorage.getItem('has_strategies');
      if (hasStrategies === 'true') {
        completeStep('strategy');
      }

      // Check content
      const hasContent = localStorage.getItem('has_content');
      if (hasContent === 'true') {
        completeStep('content');
      }

      // Check published posts
      const hasPublished = localStorage.getItem('has_published');
      if (hasPublished === 'true') {
        completeStep('publish');
      }
    } catch (e) {
      console.error('Failed to check onboarding completion:', e);
    }
  };

  const resetOnboarding = () => {
    setSteps(INITIAL_STEPS);
    localStorage.removeItem('onboarding_progress');
    localStorage.removeItem('has_seen_checklist');
    setIsComplete(false);
  };

  return (
    <OnboardingContext.Provider
      value={{
        steps,
        isComplete,
        showChecklist,
        setShowChecklist,
        completeStep,
        checkStepCompletion,
        resetOnboarding,
      }}
    >
      {children}
    </OnboardingContext.Provider>
  );
}

export function useOnboarding() {
  const context = useContext(OnboardingContext);
  if (context === undefined) {
    throw new Error('useOnboarding must be used within OnboardingProvider');
  }
  return context;
}
