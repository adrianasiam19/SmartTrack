'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Trophy, Target, BookOpen, Zap } from 'lucide-react';
import Sidebar from '../components/Sidebar';
import BottomNav from '../components/BottomNav';
import AppLayout from '../components/AppLayout';
import { getAccessToken, getStoredUser, getCurrentUser, type UserProfile } from '../lib/authApi';
import { SUBJECTS, type Subject } from './daily-streak/data/subjects';

const CHALLENGE_SUBJECTS: Subject[] = SUBJECTS;

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
      <div className="w-8 h-8 border-2 border-[#4F46E5] border-t-transparent rounded-full animate-spin" /></div></AppLayout>
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
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 bg-gradient-to-br from-[#F59E0B] to-[#D97706] rounded-xl flex items-center justify-center shadow-md">
                  <Trophy className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-2xl font-bold text-[#1E293B]">Challenges</h1>
              </div>

              {user && (
                <div className="flex items-center gap-4 mt-2">
                  <div className="flex items-center gap-1.5">
                    <Zap className="w-4 h-4 text-[#F59E0B]" />
                    <span className="text-sm font-semibold text-[#1E293B]">{userXp.toLocaleString()} XP</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Trophy className="w-4 h-4 text-[#7C3AED]" />
                    <span className="text-sm font-semibold text-[#475569]">{userRank}</span>
                  </div>
                </div>
              )}
            </motion.div>

            {/* How It Works */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className="bg-gradient-to-r from-[#EFF6FF] to-[#F5F3FF] border border-[#BFDBFE] rounded-xl p-6 mb-8"
            >
              <h2 className="text-base font-bold text-[#1E293B] mb-3">How Challenges Work</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {[
                  { icon: <BookOpen className="w-4 h-4 text-[#2563EB]" />, text: 'Complete daily challenge sets across core subjects' },
                  { icon: <Target className="w-4 h-4 text-[#7C3AED]" />, text: 'Challenges help strengthen your core academic skills' },
                  { icon: <Zap className="w-4 h-4 text-[#F59E0B]" />, text: 'Challenge performance earns you valuable XP' },
                  { icon: <Trophy className="w-4 h-4 text-[#D97706]" />, text: 'Earned XP contributes to your leaderboard ranking' },
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-2.5 bg-white/70 backdrop-blur-sm rounded-lg px-3.5 py-2.5 border border-[#E2E8F0]">
                    <div className="flex-shrink-0">{item.icon}</div>
                    <span className="text-sm text-[#475569]">{item.text}</span>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Challenge Sets */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <h2 className="text-lg font-bold text-[#1E293B] mb-4">Challenge Sets</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {CHALLENGE_SUBJECTS.map((subject, idx) => {
                  const totalLevels = subject.levels.length;
                  const completedCount = subject.levels.filter((l) => !l.locked).length;
                  return (
                    <motion.button
                      key={subject.id}
                      initial={{ opacity: 0, y: 15 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 + idx * 0.06 }}
                      whileHover={{ y: -2 }}
                      whileTap={{ scale: 0.99 }}
                      onClick={() => router.push(`/challenges/daily-streak/${subject.id}`)}
                      className="text-left bg-white border border-[#E2E8F0] border-l-4 rounded-xl p-5 hover:shadow-md hover:border-[#CBD5E1] transition-all duration-200"
                      style={{ borderLeftColor: subject.id === 'core-mathematics' ? '#2563EB' : subject.id === 'integrated-science' ? '#059669' : subject.id === 'english-language' ? '#7C3AED' : '#D97706' }}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1 min-w-0 mr-3">
                          <h3 className="text-base font-semibold text-[#1E293B]">{subject.name}</h3>
                          <p className="text-sm text-[#475569] mt-0.5">{subject.description}</p>
                        </div>
                        <div className="flex-shrink-0 text-right">
                          <span className="text-xs font-medium text-[#64748B]">
                            {completedCount}/{totalLevels}
                          </span>
                        </div>
                      </div>

                      {/* Progress bar */}
                      <div className="w-full h-1.5 bg-[#F1F5F9] rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all duration-500"
                          style={{
                            width: `${totalLevels > 0 ? (completedCount / totalLevels) * 100 : 0}%`,
                            backgroundColor: subject.id === 'core-mathematics' ? '#2563EB' : subject.id === 'integrated-science' ? '#059669' : subject.id === 'english-language' ? '#7C3AED' : '#D97706',
                          }}
                        />
                      </div>
                    </motion.button>
                  );
                })}
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
                <button onClick={() => router.push('/challenges/leaderboard')} className="text-[#4F46E5] hover:text-[#4338CA] font-medium underline underline-offset-2">leaderboard</button>.
              </p>
            </motion.div>
          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}
