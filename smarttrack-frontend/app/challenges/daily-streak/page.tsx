'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import Sidebar from '../../components/Sidebar';
import BottomNav from '../../components/BottomNav';
import AppLayout from '../../components/AppLayout';
import { SUBJECTS } from './data/subjects';
import { getAccessToken, getCurrentUser, getStoredUser, type UserProfile } from '../../lib/authApi';
import { getDailyStreakProgress, type SubjectProgress } from '../../lib/dailyStreakApi';

const VISITED_KEY = 'atlas_daily_streak_visited';

function hasVisitedBefore(): boolean {
  if (typeof window === 'undefined') return false;
  return localStorage.getItem(VISITED_KEY) === 'true';
}

function markVisited(): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(VISITED_KEY, 'true');
  }
}

export default function DailyStreakPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [subjectsProgress, setSubjectsProgress] = useState<SubjectProgress[]>([]);
  const [isFirstVisit, setIsFirstVisit] = useState(!hasVisitedBefore());

  useEffect(() => {
    const load = async () => {
      try {
        if (!getAccessToken()) { router.push('/login'); return; }
        const cached = getStoredUser(); if (cached) setUser(cached);
        const fresh = await getCurrentUser(); setUser(fresh);

        const progressData = await getDailyStreakProgress();
        setSubjectsProgress(progressData.subjects);
      } catch {
        // Backend API unavailable — show subjects without live progress
      }
      finally { setLoading(false); }
    };
    load();
  }, [router]);

  // Mark as visited so returning users see the concise message instead of the intro
  useEffect(() => {
    if (isFirstVisit) markVisited();
  }, [isFirstVisit]);

  const getSubjectProgress = (subjectId: string) => {
    return subjectsProgress.find((s) => s.subject_id === subjectId);
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="w-8 h-8 border-2 border-[#4F46E5] border-t-transparent rounded-full animate-spin" />
        </div>
      </AppLayout>
    );
  }

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
                <svg className="w-6 h-6 text-[#F59E0B]" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 23c-3.866 0-7-3.134-7-7 0-3.866 3-8 7-13 4 5 7 9.134 7 13 0 3.866-3.134 7-7 7z" />
                </svg>
                <h1 className="text-2xl font-bold text-[#1E293B]">Daily Streak</h1>
              </div>

              {isFirstVisit ? (
                <div className="mt-4 bg-[#EEF2FF] border border-[#C7D2FE] rounded-xl p-5">
                  <h2 className="text-base font-semibold text-[#1E293B] mb-2">Welcome to Daily Streak</h2>
                  <p className="text-sm text-[#475569] leading-relaxed mb-3">
                    Daily Streak is a set of short, subject-based challenges designed to help you practice consistently. 
                    Each day, you can attempt one challenge per subject across Core Mathematics, English Language, 
                    Integrated Science, and Social Studies.
                  </p>
                  <p className="text-sm text-[#475569] leading-relaxed">
                    Completing challenges earns you XP, builds your streak, and helps Atlas understand your 
                    strengths so your programme recommendations become more accurate over time.
                  </p>
                </div>
              ) : (
                <p className="text-base text-[#475569] mt-1">
                  It&apos;s good to take daily challenges to strengthen your knowledge and keep your recommendations accurate.
                </p>
              )}
            </motion.div>

            {/* Live challenge — avoid the old empty subject banks */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className="mb-8"
            >
              <button
                type="button"
                onClick={() => router.push('/challenges/atlas?autostart=1')}
                className="w-full bg-gradient-to-r from-[#2563EB] to-[#1D4ED8] text-white rounded-2xl p-6 text-left shadow-lg shadow-[#2563EB]/20 hover:shadow-xl transition-all"
              >
                <h2 className="text-lg font-bold mb-1">Start today&apos;s live challenge</h2>
                <p className="text-sm text-[#BFDBFE]">
                  Real Atlas AI questions across all four core subjects — Levels 1 to 3.
                </p>
              </button>
            </motion.div>

            {/* Subjects */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <p className="sm:col-span-2 text-sm text-[#64748B]">
                Or pick a subject — starting a level opens the same live Atlas questions.
              </p>
              {SUBJECTS.map((subject, idx) => {
                const progress = getSubjectProgress(subject.id);
                const completedCount = progress
                  ? progress.levels.filter((l) => l.completed).length
                  : 0;
                const totalLevels = subject.levels.length;

                return (
                  <motion.button
                    key={subject.id}
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.06 }}
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


          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}
