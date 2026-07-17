'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import Sidebar from '../components/Sidebar';
import BottomNav from '../components/BottomNav';
import AppLayout from '../components/AppLayout';
import XpGauge from '../components/XpGauge';
import {
  getCurrentUser,
  getAccessToken,
  getStoredUser,
  resolvePostAuthDestination,
  UserProfile,
} from '../lib/authApi';

const FUN_FACTS = [
  'Did you know? The brain can process images in as little as 13 milliseconds!',
  'Regular practice improves memory retention by up to 50%.',
  'Students who set daily goals are 42% more likely to achieve them.',
  'Taking short breaks during study sessions boosts long-term retention.',
  'The SHS curriculum in Ghana covers over 30 subjects across all programmes.',
  'Active recall is one of the most effective learning techniques known.',
  'Your brain processes information faster when you\'re well-rested.',
  'Ghana has over 50 public universities and colleges for tertiary education.',
];

function getDailyFunFact(): string {
  const today = new Date();
  const dayOfYear = Math.floor((today.getTime() - new Date(today.getFullYear(), 0, 0).getTime()) / 86400000);
  return FUN_FACTS[dayOfYear % FUN_FACTS.length];
}

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [funFact] = useState(getDailyFunFact);

  useEffect(() => {
    const loadData = async () => {
      try {
        const token = getAccessToken();
        if (!token) { router.push('/login'); return; }

        // Paint immediately from the profile cached at login, then refresh.
        const cached = getStoredUser();
        if (cached) {
          const cachedDestination = resolvePostAuthDestination(cached);
          if (cachedDestination !== '/dashboard') {
            router.replace(cachedDestination);
            return;
          }
          setUser(cached);
          setLoading(false);
        }

        const fresh = await getCurrentUser();
        const destination = resolvePostAuthDestination(fresh);
        if (destination !== '/dashboard') {
          router.replace(destination);
          return;
        }
        setUser(fresh);
      } catch { router.push('/login'); }
      finally { setLoading(false); }
    };
    loadData();
  }, [router]);

  if (loading && !user) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="w-10 h-10 border-4 border-[#2563EB] border-t-transparent rounded-full animate-spin" />
        </div>
      </AppLayout>
    );
  }

  if (!user) return null;

  const firstName = user.full_name?.split(' ')[0] || 'there';
  const userXp = typeof user.xp === 'number' ? user.xp : 0;
  const userRank = user.rank || 'Beginner';
  const userStreak = typeof user.streak === 'number' ? user.streak : 0;
  const userProgramme = user.programme || 'SHS Student';

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-24">
          <main className="flex-1 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10 pb-10">
            {/* Welcome */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8"
            >
              <h1 className="text-3xl sm:text-4xl font-bold text-[#1E293B]">
                Welcome back,{' '}
                <span className="text-[#2563EB]">{firstName}</span>
              </h1>
              <p className="text-base text-[#475569] mt-2">
                {userProgramme}
                {user.shs_level ? ` · ${user.shs_level}` : ''}
              </p>
            </motion.div>

            {/* XP Overview & Level */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className="mb-8"
            >
              <XpGauge
                xp={userXp}
                rank={userRank}
                streak={userStreak}
              />
            </motion.div>

            {/* Daily Streak — Main Action Card */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="mb-8"
            >
              <motion.button
                whileHover={{ y: -3, scale: 1.01 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => router.push('/challenges/intro')}
                className="w-full bg-white border-2 border-[#BFDBFE] rounded-2xl p-6 sm:p-8 text-left hover:shadow-lg hover:border-[#2563EB] transition-all duration-200 group"
              >
                <div className="mb-5">
                  <h2 className="text-xl font-bold text-[#1E293B]">Daily Streak</h2>
                  <p className="text-sm text-[#64748B] mt-1">Complete today&apos;s challenge and keep your streak alive</p>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-[#EFF6FF] rounded-xl p-4 text-center border border-[#BFDBFE]">
                    <div className="text-xs font-semibold text-[#64748B] uppercase tracking-wider mb-1">Current Streak</div>
                    <div className="text-3xl font-black text-[#2563EB]">{userStreak}</div>
                    <div className="text-xs text-[#64748B] font-medium mt-1">{userStreak === 1 ? 'day' : 'days'}</div>
                  </div>
                  <div className="bg-[#EFF6FF] rounded-xl p-4 text-center border border-[#BFDBFE]">
                    <div className="text-xs font-semibold text-[#64748B] uppercase tracking-wider mb-1">Today&apos;s Status</div>
                    <div className="text-lg font-black text-[#1E293B]">Ready</div>
                    <div className="text-xs text-[#64748B] font-medium mt-1">3 levels</div>
                  </div>
                  <div className="bg-[#EFF6FF] rounded-xl p-4 text-center border border-[#BFDBFE]">
                    <div className="text-xs font-semibold text-[#64748B] uppercase tracking-wider mb-1">Challenge XP</div>
                    <div className="text-2xl font-black text-[#059669]">+450</div>
                    <div className="text-xs text-[#64748B] font-medium mt-1">max daily</div>
                  </div>
                </div>

                <div className="mt-5 bg-[#2563EB] text-white font-bold py-3.5 rounded-xl text-center">
                  Start Today&apos;s Challenge
                </div>
              </motion.button>
            </motion.div>

            {/* Fun Fact */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
              className="bg-gradient-to-r from-[#EFF6FF] to-[#F5F3FF] border border-[#BFDBFE] rounded-xl p-5"
            >
              <div>
                <p className="text-xs font-semibold text-[#2563EB] uppercase tracking-wider mb-1">Did you know?</p>
                <p className="text-sm text-[#475569] leading-relaxed">{funFact}</p>
              </div>
            </motion.div>
          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}
