'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Flame, Target, Sparkles, Zap, ArrowRight } from 'lucide-react';
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
                onClick={() => router.push('/challenges')}
                className="w-full bg-gradient-to-br from-[#FFFBEB] to-[#FEF3C7] border-2 border-[#FDE68A] rounded-2xl p-6 sm:p-8 text-left hover:shadow-lg hover:border-[#F59E0B] transition-all duration-200"
              >
                <div className="flex items-center gap-4 mb-5">
                  <div className="w-14 h-14 bg-gradient-to-br from-[#F59E0B] to-[#D97706] rounded-2xl flex items-center justify-center shadow-md">
                    <Flame className="w-7 h-7 text-white" />
                  </div>
                  <div className="flex-1">
                    <h2 className="text-xl font-bold text-[#1E293B]">Daily Streak</h2>
                    <p className="text-sm text-[#92400E]">Complete today&apos;s challenge and keep your streak alive</p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-white/70 backdrop-blur-sm rounded-xl p-4 text-center border border-[#FDE68A]">
                    <div className="text-2xl font-black text-[#D97706]">{userStreak}</div>
                    <div className="text-xs text-[#92400E] font-medium mt-1">Day Streak</div>
                  </div>
                  <div className="bg-white/70 backdrop-blur-sm rounded-xl p-4 text-center border border-[#FDE68A]">
                    <div className="flex items-center justify-center gap-1 text-2xl font-black text-[#059669]">
                      <Zap className="w-5 h-5" />
                      <span>+50</span>
                    </div>
                    <div className="text-xs text-[#92400E] font-medium mt-1">XP Available</div>
                  </div>
                  <div className="bg-white/70 backdrop-blur-sm rounded-xl p-4 text-center border border-[#FDE68A]">
                    <div className="text-xl font-black text-[#2563EB]">Today</div>
                    <div className="text-xs text-[#92400E] font-medium mt-1">Challenge</div>
                  </div>
                </div>

                <div className="mt-5 flex items-center justify-center gap-2 bg-[#F59E0B] text-white font-bold py-3 rounded-xl hover:bg-[#D97706] transition-colors">
                  <span>Start Today&apos;s Challenge</span>
                  <ArrowRight className="w-4 h-4" />
                </div>
              </motion.button>
            </motion.div>

            {/* Recommendation Readiness */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
              className="bg-white border border-[#E2E8F0] rounded-xl p-6 mb-8"
            >
              <div className="flex items-center gap-3 mb-4">
                <Target className="w-5 h-5 text-[#7C3AED]" />
                <h2 className="text-lg font-semibold text-[#1E293B]">Recommendation Readiness</h2>
              </div>
              <p className="text-sm text-[#475569] mb-4">
                Complete challenges to help Atlas recommend the best university programmes for you. The more challenges you complete, the more accurate your recommendations become.
              </p>
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-[#64748B]">Progress</span>
                    <span className="text-xs font-semibold text-[#2563EB]">{Math.min(Math.round((userXp / 500) * 100), 100)}%</span>
                  </div>
                  <div className="w-full bg-[#E2E8F0] rounded-full h-2.5 overflow-hidden">
                    <motion.div
                      initial={{ width: '0%' }}
                      animate={{ width: `${Math.min((userXp / 500) * 100, 100)}%` }}
                      transition={{ duration: 0.8, ease: 'easeOut' }}
                      className="h-full bg-gradient-to-r from-[#2563EB] to-[#7C3AED] rounded-full"
                    />
                  </div>
                </div>
                <button
                  onClick={() => router.push('/challenges')}
                  className="flex-shrink-0 px-5 py-2.5 bg-[#2563EB] text-white text-xs font-semibold rounded-lg hover:bg-[#1D4ED8] transition-colors"
                >
                  View Challenges
                </button>
              </div>
            </motion.div>

            {/* Fun Fact */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
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
