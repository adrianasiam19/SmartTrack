'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import Sidebar from '../../components/Sidebar';
import BottomNav from '../../components/BottomNav';
import AppLayout from '../../components/AppLayout';
import { getAccessToken, getCurrentUser, getStoredUser, type UserProfile } from '../../lib/authApi';

export default function ChallengeIntro() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        if (!getAccessToken()) {
          router.push('/login');
          return;
        }
        const cached = getStoredUser();
        if (cached) setUser(cached);
        const fresh = await getCurrentUser();
        setUser(fresh);
      } catch {
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [router]);

  const startLiveChallenge = () => {
    setStarting(true);
    router.push('/challenges/atlas?autostart=1');
  };

  if (loading || starting) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen px-6">
          <div className="flex flex-col items-center gap-4 text-center">
            <div className="w-10 h-10 border-2 border-[#2563EB] border-t-transparent rounded-full animate-spin" />
            <p className="text-sm font-medium text-[#1E293B]">
              {starting ? "Atlas AI is preparing today's challenge…" : 'Loading…'}
            </p>
          </div>
        </div>
      </AppLayout>
    );
  }

  const userStreak = user?.streak || 0;

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-24">
          <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10 pb-10">
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8 text-center"
            >
              <h1 className="text-3xl sm:text-4xl font-bold text-[#1E293B] mb-3">
                Today&apos;s Challenge
              </h1>
              <p className="text-base text-[#475569] max-w-lg mx-auto">
                One live session: four core subjects, three difficulty levels, real questions from Atlas AI.
              </p>
            </motion.div>

            {userStreak > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center mb-8"
              >
                <div className="inline-flex bg-[#EFF6FF] border border-[#BFDBFE] rounded-full px-5 py-2">
                  <span className="text-sm font-semibold text-[#2563EB]">
                    {userStreak} day streak — keep it going
                  </span>
                </div>
              </motion.div>
            )}

            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.08 }}
              className="bg-white border border-[#BFDBFE] rounded-2xl p-6 mb-8"
            >
              <h2 className="text-sm font-bold text-[#1E293B] mb-4">How it works</h2>
              <ol className="space-y-3">
                {[
                  'Answer 6 questions per core subject (Maths, English, Science, Social Studies).',
                  'Finish all four subjects to complete a level.',
                  'Continue to Level 2 and Level 3 for harder questions and more XP.',
                ].map((step, i) => (
                  <li key={step} className="flex gap-3 text-sm text-[#475569]">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-[#2563EB] text-white text-xs font-bold flex items-center justify-center">
                      {i + 1}
                    </span>
                    <span className="pt-0.5">{step}</span>
                  </li>
                ))}
              </ol>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.12 }}
              className="text-center"
            >
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={startLiveChallenge}
                className="inline-flex px-10 py-3.5 bg-gradient-to-r from-[#2563EB] to-[#1D4ED8] text-white font-bold text-base rounded-xl shadow-lg shadow-[#2563EB]/25"
              >
                Start live challenge
              </motion.button>
              <p className="text-xs text-[#94A3B8] mt-4">
                Questions are generated for your SHS level — not empty placeholders.
              </p>
            </motion.div>
          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}
