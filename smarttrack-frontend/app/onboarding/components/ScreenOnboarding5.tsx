'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { updateUserProfile } from '../../lib/authApi';

interface Props {
  onComplete: () => void;
}

export default function ScreenOnboarding5({ onComplete }: Props) {
  const router = useRouter();
  const [status, setStatus] = useState('Preparing your experience...');

  useEffect(() => {
    let cancelled = false;

    const finishWalkthrough = async () => {
      try {
        setStatus('Saving your progress...');
        // Mark the welcome walkthrough complete before entering Starter Arena.
        // Starter Arena completion is a separate one-time flag.
        await updateUserProfile({ onboarding_completed: true });
        if (cancelled) return;
        onComplete();
        setStatus('Starting your discovery...');
        router.replace('/challenges/arena?mode=placement');
      } catch {
        if (cancelled) return;
        // Still continue — Starter Arena completion will also mark both flags.
        onComplete();
        router.replace('/challenges/arena?mode=placement');
      }
    };

    const timer = setTimeout(finishWalkthrough, 1200);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [onComplete, router]);

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-lg text-center"
      >
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-8 sm:p-10 shadow-sm">
          <h1 className="text-3xl sm:text-4xl font-bold text-[#1E293B] mb-4">
            Ready to Discover Yourself
          </h1>
          <p className="text-base text-[#475569] mb-4 leading-relaxed">
            Atlas will guide you through the Starter Arena — a short discovery experience to understand your strengths and interests.
          </p>
          <p className="text-sm text-[#94A3B8]">{status}</p>

          <div className="mt-6 max-w-xs mx-auto">
            <div className="h-1.5 bg-[#E2E8F0] rounded-full overflow-hidden">
              <motion.div
                initial={{ width: '0%' }}
                animate={{ width: '100%' }}
                transition={{ duration: 1.2, ease: 'easeInOut' }}
                className="h-full bg-[#2563EB] rounded-full"
              />
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
