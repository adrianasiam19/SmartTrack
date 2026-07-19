'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import Sidebar from '../components/Sidebar';
import BottomNav from '../components/BottomNav';
import AppLayout from '../components/AppLayout';
import { getAccessToken, getStoredUser, getCurrentUser, type UserProfile } from '../lib/authApi';

export default function ChallengesHub() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

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

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="w-8 h-8 border-2 border-[#2563EB] border-t-transparent rounded-full animate-spin" />
        </div>
      </AppLayout>
    );
  }

  const userXp = typeof user?.xp === 'number' ? user.xp : 0;
  const userRank = user?.rank || 'Beginner';
  const userStreak = typeof user?.streak === 'number' ? user.streak : 0;

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-20">
          <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-8 pb-8">
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8"
            >
              <h1 className="text-2xl font-bold text-[#1E293B]">Challenges</h1>
              <div className="flex flex-wrap items-center gap-3 mt-2 text-sm text-[#475569]">
                <span className="font-semibold text-[#1E293B]">{userXp.toLocaleString()} XP</span>
                <span>{userRank}</span>
                <span>{userStreak} day streak</span>
              </div>
            </motion.div>

            <motion.button
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.99 }}
              onClick={() => router.push('/challenges/intro')}
              className="w-full bg-gradient-to-r from-[#2563EB] to-[#1D4ED8] rounded-2xl p-8 text-white text-left shadow-lg shadow-[#2563EB]/25 mb-6"
            >
              <h2 className="text-xl font-bold mb-2">Start today&apos;s challenge</h2>
              <p className="text-[#BFDBFE] text-sm">
                Live Atlas questions · 4 core subjects · 3 levels
              </p>
            </motion.button>

            <motion.button
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.99 }}
              onClick={() => router.push('/challenges/atlas?autostart=1')}
              className="w-full bg-white border border-[#C7D2FE] rounded-2xl p-6 text-left hover:border-[#2563EB] hover:shadow-md mb-8"
            >
              <h3 className="text-base font-bold text-[#1E293B]">Jump straight into questions</h3>
              <p className="text-sm text-[#64748B] mt-1">
                Skip the intro screen and begin Level 1 now.
              </p>
            </motion.button>

            <p className="text-center text-sm text-[#64748B]">
              Climb the{' '}
              <button
                type="button"
                onClick={() => router.push('/challenges/leaderboard')}
                className="text-[#2563EB] font-medium underline underline-offset-2"
              >
                leaderboard
              </button>{' '}
              as you earn XP.
            </p>
          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}
