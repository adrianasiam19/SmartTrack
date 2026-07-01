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
  const [saving, setSaving] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const completeOnboarding = async () => {
      try {
        await updateUserProfile({ onboarding_completed: true });
        setSaving(false);
      } catch {
        setError('Could not save your progress. You can continue anyway.');
        setSaving(false);
      }
    };
    completeOnboarding();
  }, []);

  useEffect(() => {
    if (!saving) {
      const timer = setTimeout(() => {
        onComplete();
        router.push('/dashboard');
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [saving, router, onComplete]);

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-lg text-center"
      >
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-8 sm:p-10 shadow-sm">
          <div className="w-20 h-20 bg-gradient-to-br from-[#2563EB] to-[#7C3AED] rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
            <span className="text-4xl">🚀</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-bold text-[#1E293B] mb-4">
            Your Journey Starts Now!
          </h1>
          <p className="text-base text-[#475569] mb-4 leading-relaxed">
            Atlas is ready. Your challenges, lessons, and personalised recommendations are waiting.
          </p>

          {error && (
            <p className="text-sm text-[#DC2626] mb-2">{error}</p>
          )}

          {saving ? (
            <div className="flex items-center justify-center gap-2 text-sm text-[#94A3B8]">
              <div className="w-4 h-4 border-2 border-[#2563EB] border-t-transparent rounded-full animate-spin" />
              <span>Setting up your profile...</span>
            </div>
          ) : (
            <p className="text-sm text-[#94A3B8]">
              Taking you to your dashboard...
            </p>
          )}

          <div className="mt-6 max-w-xs mx-auto">
            <div className="h-1.5 bg-[#E2E8F0] rounded-full overflow-hidden">
              <motion.div
                initial={{ width: '0%' }}
                animate={{ width: saving ? '40%' : '100%' }}
                transition={{ duration: saving ? 1.5 : 1.5, ease: 'easeInOut' }}
                className="h-full bg-gradient-to-r from-[#2563EB] to-[#7C3AED] rounded-full"
              />
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
