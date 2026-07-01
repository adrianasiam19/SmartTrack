'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';

interface Props {
  onComplete: () => void;
}

export default function ScreenOnboarding5({ onComplete }: Props) {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setReady(true);
    }, 1500);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (ready) {
      onComplete();
      router.push('/challenges/arena?mode=placement');
    }
  }, [ready, router, onComplete]);

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
          <p className="text-sm text-[#94A3B8]">
            {ready ? 'Starting your discovery...' : 'Preparing your experience...'}
          </p>

          <div className="mt-6 max-w-xs mx-auto">
            <div className="h-1.5 bg-[#E2E8F0] rounded-full overflow-hidden">
              <motion.div
                initial={{ width: '0%' }}
                animate={{ width: ready ? '100%' : '60%' }}
                transition={{ duration: 1.5, ease: 'easeInOut' }}
                className="h-full bg-[#2563EB] rounded-full"
              />
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
