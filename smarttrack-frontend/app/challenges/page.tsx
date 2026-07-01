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
        if (!getAccessToken()) { router.push('/login'); return; }
        const cached = getStoredUser(); if (cached) setUser(cached);
        const fresh = await getCurrentUser(); setUser(fresh);
      } catch { router.push('/login'); }
      finally { setLoading(false); }
    };
    load();
  }, [router]);

  const userXp = typeof user?.xp === 'number' ? user.xp : 0;
  const userRank = user?.rank || 'Beginner';

  if (loading) return (
    <AppLayout><div className="flex items-center justify-center min-h-screen">
      <div className="w-8 h-8 border-2 border-[#2563EB] border-t-transparent rounded-full animate-spin" /></div></AppLayout>
  );

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-20">
          <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-8 pb-8">
            {/* Header */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8"
            >
              <h1 className="text-2xl font-bold text-[#1E293B]">Challenges</h1>

              {user && (
                <div className="flex items-center gap-4 mt-2">
                  <span className="text-sm font-semibold text-[#1E293B]">{userXp.toLocaleString()} XP</span>
                  <span className="text-sm text-[#475569]">{userRank}</span>
                </div>
              )}
            </motion.div>

            {/* Start Challenge CTA */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className="mb-8"
            >
              <motion.button
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => router.push('/challenges/intro')}
                className="w-full bg-gradient-to-r from-[#2563EB] to-[#1D4ED8] rounded-2xl p-8 text-white text-left hover:shadow-xl hover:shadow-[#2563EB]/25 transition-all duration-200"
              >
                <h2 className="text-xl font-bold mb-2">Start Today&apos;s Challenge</h2>
                <p className="text-[#BFDBFE] text-sm mb-4">
                  A guided 3-level challenge to strengthen your core academic skills.
                </p>
                <div className="flex items-center gap-4 text-sm">
                  <div className="flex items-center gap-1.5 bg-white/10 rounded-lg px-3 py-1.5">
                    <span>3 Levels</span>
                  </div>
                  <div className="flex items-center gap-1.5 bg-white/10 rounded-lg px-3 py-1.5">
                    <span>Up to 450 XP</span>
                  </div>
                </div>
              </motion.button>
            </motion.div>

            {/* How It Works */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-gradient-to-r from-[#EFF6FF] to-[#F5F3FF] border border-[#BFDBFE] rounded-xl p-6 mb-8"
            >
              <h2 className="text-base font-bold text-[#1E293B] mb-3">How Challenges Work</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {[
                  'Complete daily challenge sets across core subjects',
                  'Challenges help strengthen your core academic skills',
                  'Challenge performance earns you valuable XP',
                  'Earned XP contributes to your leaderboard ranking',
                ].map((text, i) => (
                  <div key={i} className="bg-white/70 backdrop-blur-sm rounded-lg px-3.5 py-2.5 border border-[#E2E8F0]">
                    <span className="text-sm text-[#475569]">{text}</span>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Leaderboard Link */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-center py-6 border-t border-gray-100 mt-8"
            >
              <p className="text-gray-500 text-sm">
                Complete challenges to earn XP and climb the{' '}
                <button onClick={() => router.push('/challenges/leaderboard')} className="text-[#2563EB] hover:text-[#1D4ED8] font-medium underline underline-offset-2">leaderboard</button>.
              </p>
            </motion.div>
          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}
