'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { updateUserProfile } from '../../lib/authApi';

interface ScreenProfileReadyProps {
  onComplete: () => void;
}

export default function ScreenProfileReady({ onComplete }: ScreenProfileReadyProps) {
  const router = useRouter();
  const [phase, setPhase] = useState<'ready' | 'redirect'>('ready');

  const handleGoToDashboard = async () => {
    setPhase('redirect');
    try {
      await updateUserProfile({ onboarding_completed: true });
    } catch {
      // Continue anyway
    }
    setTimeout(() => {
      onComplete();
      router.push('/dashboard');
    }, 800);
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center relative overflow-hidden py-12 px-4 sm:px-6">
      {/* Background */}
      <div className="absolute inset-0 pointer-events-none">
        <motion.div
          animate={{ scale: [1, 1.08, 1] }}
          transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-r from-[#2563EB]/5 to-[#7C3AED]/5 rounded-full blur-3xl"
        />
      </div>

      <div className="relative z-10 w-full max-w-lg mx-auto text-center">
        {phase === 'ready' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            {/* Logo */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 200, damping: 12, delay: 0.1 }}
              className="w-24 h-24 mx-auto bg-gradient-to-br from-[#2563EB] to-[#7C3AED] rounded-3xl flex items-center justify-center shadow-2xl shadow-[#2563EB]/25 mb-8"
            >
              <motion.span
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                className="text-white font-bold text-3xl"
              >
                A
              </motion.span>
            </motion.div>

            <h2 className="text-3xl sm:text-4xl font-bold text-[#1E293B] mb-3">
              You&apos;re All Set!
            </h2>
            <p className="text-lg text-[#475569] mb-8">
              Atlas has your profile ready. Start exploring and your experience will grow with you.
            </p>

            {/* Quick summary */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white rounded-2xl border border-[#E2E8F0] p-5 mb-8 shadow-sm text-left"
            >
              <div className="space-y-3">
                <p className="text-sm font-semibold text-[#1E293B] mb-2">
                  What happens next?
                </p>
                {[
                  { text: 'Complete daily challenges to earn XP', icon: '⭐' },
                  { text: 'Learn at your own pace', icon: '📚' },
                  { text: 'Get personalized recommendations', icon: '🎯' },
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center gap-3">
                    <span className="text-base">{item.icon}</span>
                    <span className="text-sm text-[#475569]">{item.text}</span>
                  </div>
                ))}
              </div>
            </motion.div>

            <motion.button
              whileHover={{ scale: 1.03, boxShadow: '0 20px 40px rgba(37, 99, 235, 0.25)' }}
              whileTap={{ scale: 0.97 }}
              onClick={handleGoToDashboard}
              className="px-10 py-4 bg-gradient-to-r from-[#2563EB] to-[#7C3AED] text-white font-bold text-lg rounded-2xl shadow-xl shadow-[#2563EB]/20 hover:shadow-2xl transition-all duration-300"
            >
              Go to Dashboard
            </motion.button>
          </motion.div>
        )}

        {phase === 'redirect' && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
              className="w-16 h-16 mx-auto border-4 border-[#2563EB] border-t-transparent rounded-full mb-6"
            />
            <p className="text-lg font-semibold text-[#1E293B]">Preparing your Dashboard...</p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
