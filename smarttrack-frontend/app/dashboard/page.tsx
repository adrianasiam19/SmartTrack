'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Flame, Target, BookOpen, Sparkles } from 'lucide-react';
import Sidebar from '../components/Sidebar';
import BottomNav from '../components/BottomNav';
import AppLayout from '../components/AppLayout';
import XpGauge from '../components/XpGauge';
import {
  getCurrentUser, getAccessToken, getStoredUser, UserProfile,
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
        const cached = getStoredUser();
        if (cached) setUser(cached);
        const fresh = await getCurrentUser();
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

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-24">
          <main className="flex-1 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10 pb-10">
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
                {user.programme || 'SHS Student'}
                {user.shs_level ? ` · ${user.shs_level}` : ''}
              </p>
            </motion.div>

            {/* XP & Level */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className="mb-8"
            >
              <XpGauge
                xp={user.xp}
                rank={user.rank}
                streak={user.streak}
              />
            </motion.div>

            {/* Quick Actions Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
              {/* Continue Learning */}
              <motion.button
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => router.push('/learning')}
                className="bg-white border border-[#E2E8F0] border-l-4 border-l-[#2563EB] rounded-xl p-5 text-left hover:shadow-md hover:border-[#BFDBFE] transition-all duration-200"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <BookOpen className="w-5 h-5 text-[#2563EB]" />
                      <h3 className="text-base font-semibold text-[#1E293B]">Continue Learning</h3>
                    </div>
                    <p className="text-sm text-[#475569]">Pick up where you left off with your lessons.</p>
                  </div>
                  <span className="flex-shrink-0 ml-4 px-4 py-2 text-xs font-semibold text-[#2563EB] bg-[#EFF6FF] rounded-lg">
                    Go
                  </span>
                </div>
              </motion.button>

              {/* Daily Challenge */}
              <motion.button
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.15 }}
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.99 }}
                onClick={() => router.push('/challenges/daily-streak')}
                className="bg-white border border-[#E2E8F0] border-l-4 border-l-[#F59E0B] rounded-xl p-5 text-left hover:shadow-md hover:border-[#FDE68A] transition-all duration-200"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <Flame className="w-5 h-5 text-[#F59E0B]" />
                      <h3 className="text-base font-semibold text-[#1E293B]">Daily Challenge</h3>
                    </div>
                    <p className="text-sm text-[#475569]">Complete today&apos;s challenge and keep your streak alive!</p>
                  </div>
                  <span className="flex-shrink-0 ml-4 px-4 py-2 text-xs font-semibold text-[#D97706] bg-[#FFFBEB] rounded-lg">
                    Start
                  </span>
                </div>
              </motion.button>
            </div>

            {/* Recommendation Readiness */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white border border-[#E2E8F0] rounded-xl p-6 mb-8"
            >
              <div className="flex items-center gap-3 mb-4">
                <Target className="w-5 h-5 text-[#7C3AED]" />
                <h2 className="text-lg font-semibold text-[#1E293B]">Recommendation Readiness</h2>
              </div>
              <p className="text-sm text-[#475569] mb-4">
                Complete challenges to help Atlas recommend the best university programmes for you.
              </p>
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-[#64748B]">Progress</span>
                    <span className="text-xs font-semibold text-[#2563EB]">{Math.min((user.xp / 500) * 100, 100)}%</span>
                  </div>
                  <div className="w-full bg-[#E2E8F0] rounded-full h-2 overflow-hidden">
                    <motion.div
                      initial={{ width: '0%' }}
                      animate={{ width: `${Math.min((user.xp / 500) * 100, 100)}%` }}
                      transition={{ duration: 0.8, ease: 'easeOut' }}
                      className="h-full bg-gradient-to-r from-[#2563EB] to-[#7C3AED] rounded-full"
                    />
                  </div>
                </div>
                <button
                  onClick={() => router.push('/challenges')}
                  className="flex-shrink-0 px-4 py-2 bg-[#2563EB] text-white text-xs font-semibold rounded-lg hover:bg-[#1D4ED8] transition-colors"
                >
                  Start Challenges
                </button>
              </div>
            </motion.div>

            {/* Fun Fact */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.25 }}
              className="bg-gradient-to-r from-[#EFF6FF] to-[#F5F3FF] border border-[#BFDBFE] rounded-xl p-5"
            >
              <div className="flex items-start gap-3">
                <Sparkles className="w-5 h-5 text-[#F59E0B] flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-semibold text-[#2563EB] uppercase tracking-wider mb-1">Did you know?</p>
                  <p className="text-sm text-[#475569] leading-relaxed">{funFact}</p>
                </div>
              </div>
            </motion.div>
          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}
