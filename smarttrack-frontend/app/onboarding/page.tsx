'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { AnimatePresence, motion } from 'framer-motion';
import { getAccessToken, getCurrentUser, resolvePostAuthDestination } from '../lib/authApi';

import ScreenOnboarding1 from './components/ScreenOnboarding1';
import ScreenOnboarding2 from './components/ScreenOnboarding2';
import ScreenOnboarding3 from './components/ScreenOnboarding3';
import ScreenOnboarding4 from './components/ScreenOnboarding4';
import ScreenOnboarding5 from './components/ScreenOnboarding5';

type OnboardingStep =
  | 'welcome'
  | 'starter-arena'
  | 'earn-your-way'
  | 'learn-and-grow'
  | 'journey-starts';

const STEP_LABELS: Record<OnboardingStep, string> = {
  welcome: 'Welcome',
  'starter-arena': 'Starter Arena',
  'earn-your-way': 'Earn XP',
  'learn-and-grow': 'Learn & Grow',
  'journey-starts': 'Begin',
};

const STEP_ORDER: OnboardingStep[] = [
  'welcome',
  'starter-arena',
  'earn-your-way',
  'learn-and-grow',
  'journey-starts',
];

const pageVariants = {
  enter: (direction: number) => ({
    x: direction > 0 ? '30%' : '-30%',
    opacity: 0,
  }),
  center: {
    x: 0,
    opacity: 1,
  },
  exit: (direction: number) => ({
    x: direction > 0 ? '-20%' : '20%',
    opacity: 0,
  }),
};

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState<OnboardingStep>('welcome');
  const [direction, setDirection] = useState<number>(1);
  const [loading, setLoading] = useState(true);

  const currentStepIndex = STEP_ORDER.indexOf(step);

  useEffect(() => {
    const load = async () => {
      try {
        if (!getAccessToken()) {
          router.push('/login');
          return;
        }
        // Always trust the backend for the current token — never route from a
        // cached profile that may belong to a previous user.
        const fresh = await getCurrentUser();
        const destination = resolvePostAuthDestination(fresh);
        if (destination !== '/onboarding') {
          router.replace(destination);
          return;
        }
      } catch {
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [router]);

  const goToStep = useCallback((next: OnboardingStep) => {
    const nextIdx = STEP_ORDER.indexOf(next);
    const currIdx = STEP_ORDER.indexOf(step);
    setDirection(nextIdx > currIdx ? 1 : -1);
    setStep(next);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [step]);

  const handleWelcomeDone = useCallback(() => goToStep('starter-arena'), [goToStep]);
  const handleStarterArenaDone = useCallback(() => goToStep('earn-your-way'), [goToStep]);
  const handleEarnWayDone = useCallback(() => goToStep('learn-and-grow'), [goToStep]);
  const handleLearnGrowDone = useCallback(() => goToStep('journey-starts'), [goToStep]);
  const handleJourneyDone = useCallback(() => {
    // ScreenOnboarding5 handles the redirect itself
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-[#2563EB] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const renderStepIndicator = () => {
    return (
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="fixed top-0 left-0 right-0 z-50 flex justify-center pt-4 sm:pt-5 pointer-events-none"
      >
        <div className="flex items-center gap-2 sm:gap-3 bg-white/90 backdrop-blur-xl px-4 sm:px-6 py-2.5 sm:py-3 rounded-full border border-[#E2E8F0] shadow-sm pointer-events-auto">
          {STEP_ORDER.map((stepKey, idx) => {
            const isActive = idx === currentStepIndex;
            const isPast = idx < currentStepIndex;
            const label = STEP_LABELS[stepKey] || '';
            return (
              <div key={idx} className="flex items-center gap-2">
                <div
                  className={`w-2.5 h-2.5 rounded-full transition-all ${
                    isActive
                      ? 'bg-[#2563EB] shadow-[0_0_8px_rgba(37,99,235,0.6)]'
                      : isPast
                      ? 'bg-[#2563EB]/50'
                      : 'bg-[#E2E8F0]'
                  }`}
                />
                <span
                  className={`hidden sm:inline text-xs font-medium transition-colors ${
                    isActive ? 'text-[#2563EB]' : isPast ? 'text-[#2563EB]/60' : 'text-[#94A3B8]'
                  }`}
                >
                  {label}
                </span>
                {idx < STEP_ORDER.length - 1 && (
                  <div
                    className={`hidden sm:block w-4 sm:w-6 h-px ${
                      isPast ? 'bg-[#2563EB]/40' : 'bg-[#E2E8F0]'
                    }`}
                  />
                )}
              </div>
            );
          })}
          <span className="hidden lg:inline text-[10px] text-[#94A3B8] ml-1 font-medium">
            {currentStepIndex + 1} of {STEP_ORDER.length}
          </span>
        </div>
      </motion.div>
    );
  };

  return (
    <div className="overflow-x-hidden bg-[#F8FAFC]">
      <AnimatePresence mode="wait" custom={direction}>
        {step === 'welcome' && (
          <motion.div
            key="welcome"
            custom={direction}
            variants={pageVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          >
            {renderStepIndicator()}
            <ScreenOnboarding1 onNext={handleWelcomeDone} />
          </motion.div>
        )}
        {step === 'starter-arena' && (
          <motion.div
            key="starter-arena"
            custom={direction}
            variants={pageVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          >
            {renderStepIndicator()}
            <ScreenOnboarding2 onNext={handleStarterArenaDone} />
          </motion.div>
        )}
        {step === 'earn-your-way' && (
          <motion.div
            key="earn-your-way"
            custom={direction}
            variants={pageVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          >
            {renderStepIndicator()}
            <ScreenOnboarding3 onNext={handleEarnWayDone} />
          </motion.div>
        )}
        {step === 'learn-and-grow' && (
          <motion.div
            key="learn-and-grow"
            custom={direction}
            variants={pageVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          >
            {renderStepIndicator()}
            <ScreenOnboarding4 onNext={handleLearnGrowDone} />
          </motion.div>
        )}
        {step === 'journey-starts' && (
          <motion.div
            key="journey-starts"
            custom={direction}
            variants={pageVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          >
            <ScreenOnboarding5 onComplete={handleJourneyDone} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
