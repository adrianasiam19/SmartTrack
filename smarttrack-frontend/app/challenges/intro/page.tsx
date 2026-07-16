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

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="w-8 h-8 border-2 border-[#2563EB] border-t-transparent rounded-full animate-spin" />
        </div>
      </AppLayout>
    );
  }

  const userStreak = user?.streak || 0;

  const benefits = [
    {
      title: 'Strengthen Core Skills',
      description: 'Challenges reinforce your understanding of key academic subjects and help you retain what you learn.',
    },
    {
      title: 'Build Consistency',
      description: 'Daily practice builds strong learning habits. The longer your streak, the sharper your skills become.',
    },
    {
      title: 'Earn Challenge XP',
      description: 'Each completed challenge level rewards you with XP. The harder the level, the more XP you earn.',
    },
    {
      title: 'Climb the Leaderboard',
      description: 'Challenge XP contributes to your leaderboard ranking. Compete with fellow students across Ghana.',
    },
  ];

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-24">
          <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10 pb-10">
            {/* Header */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8 text-center"
            >
              <h1 className="text-3xl sm:text-4xl font-bold text-[#1E293B] mb-3">
                Today&apos;s Challenge
              </h1>
              <p className="text-base text-[#475569] max-w-lg mx-auto">
                A guided challenge designed to strengthen your academic skills and build momentum.
              </p>
            </motion.div>

            {/* Streak indicator */}
            {userStreak > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 }}
                className="text-center mb-8"
              >
                <div className="inline-flex bg-[#EFF6FF] border border-[#BFDBFE] rounded-full px-5 py-2">
                  <span className="text-sm font-semibold text-[#2563EB]">
                    {userStreak} day streak! Keep it going!
                  </span>
                </div>
              </motion.div>
            )}

            {/* Benefits */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.08 }}
              className="mb-10"
            >
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {benefits.map((benefit, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 + i * 0.05 }}
                    className="bg-white border border-[#E2E8F0] rounded-xl p-5"
                  >
                    <h3 className="text-sm font-bold text-[#1E293B] mb-1">{benefit.title}</h3>
                    <p className="text-sm text-[#64748B] leading-relaxed">{benefit.description}</p>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* Challenge Structure Summary */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
              className="bg-gradient-to-r from-[#EFF6FF] to-[#F5F3FF] border border-[#BFDBFE] rounded-xl p-6 mb-8"
            >
              <h3 className="text-sm font-bold text-[#1E293B] mb-3">Challenge Structure</h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between bg-white/70 rounded-lg px-4 py-2.5 border border-[#BFDBFE]">
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-[#2563EB] rounded-full flex items-center justify-center">
                      <span className="text-xs font-bold text-white">1</span>
                    </div>
                    <span className="text-sm text-[#1E293B] font-medium">Level 1</span>
                  </div>
                  <span className="text-xs text-[#64748B]">100 XP</span>
                </div>
                <div className="flex items-center justify-between bg-white/70 rounded-lg px-4 py-2.5 border border-[#BFDBFE]">
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-[#7C3AED] rounded-full flex items-center justify-center">
                      <span className="text-xs font-bold text-white">2</span>
                    </div>
                    <span className="text-sm text-[#1E293B] font-medium">Level 2</span>
                  </div>
                  <span className="text-xs text-[#64748B]">150 XP</span>
                </div>
                <div className="flex items-center justify-between bg-white/70 rounded-lg px-4 py-2.5 border border-[#BFDBFE]">
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-[#D97706] rounded-full flex items-center justify-center">
                      <span className="text-xs font-bold text-white">3</span>
                    </div>
                    <span className="text-sm text-[#1E293B] font-medium">Level 3</span>
                  </div>
                  <span className="text-xs text-[#64748B]">200 XP</span>
                </div>
              </div>
              <p className="text-xs text-[#64748B] mt-3">
                Complete each level to unlock the next. Finish all three to mark today&apos;s challenge as complete.
              </p>
            </motion.div>

            {/* CTA */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-center"
            >
              <p className="text-sm text-[#64748B] mb-4">
                Completing challenges also helps Atlas build a stronger recommendation profile for you.
              </p>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => router.push('/challenges/play')}
                className="inline-flex px-10 py-4 bg-gradient-to-r from-[#2563EB] to-[#1D4ED8] text-white font-bold text-lg rounded-xl hover:from-[#3B82F6] hover:to-[#2563EB] shadow-lg shadow-[#2563EB]/25 hover:shadow-xl hover:shadow-[#2563EB]/30 transition-all duration-200"
              >
                START TODAY&apos;S CHALLENGE
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => router.push('/challenges/atlas')}
                className="inline-flex px-10 py-4 bg-gradient-to-r from-[#2563EB] to-[#1D4ED8] text-white font-bold text-lg rounded-xl hover:from-[#3B82F6] hover:to-[#2563EB] shadow-lg shadow-[#2563EB]/25 hover:shadow-xl hover:shadow-[#2563EB]/30 transition-all duration-200"
              >
                START TODAY'S CHALLENGE
              </motion.button>
}
