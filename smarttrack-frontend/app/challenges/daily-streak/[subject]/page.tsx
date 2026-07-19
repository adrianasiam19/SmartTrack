'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
import Sidebar from '../../../components/Sidebar';
import BottomNav from '../../../components/BottomNav';
import AppLayout from '../../../components/AppLayout';
import { getSubjectById, type Subject } from '../data/subjects';
import { getAccessToken, getCurrentUser, getStoredUser, type UserProfile } from '../../../lib/authApi';
import {
  getDailyStreakProgress,
  type LevelProgress,
  type SubjectProgress,
} from '../../../lib/dailyStreakApi';

export default function DailyStreakSubjectPage() {
  const params = useParams();
  const router = useRouter();
  const subjectId = params.subject as string;
  const subject = getSubjectById(subjectId as any);

  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [subjectProgress, setSubjectProgress] = useState<SubjectProgress | null>(null);
  const [selectedLevel, setSelectedLevel] = useState<(LevelProgress & { label: string; name: string; xpReward: number }) | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        if (!getAccessToken()) { router.push('/login'); return; }
        const cached = getStoredUser(); if (cached) setUser(cached);
        const fresh = await getCurrentUser(); setUser(fresh);

        const progressData = await getDailyStreakProgress();
        const found = progressData.subjects.find((s) => s.subject_id === subjectId);
        if (found) setSubjectProgress(found);
      } catch {
        // Backend API unavailable — show levels without live progress
      }
      finally { setLoading(false); }
    };
    load();
  }, [router, subjectId]);

  const handleStartLevel = (level: LevelProgress & { label: string; name: string; xpReward: number }) => {
    setSelectedLevel(level);
    // Live questions live in Atlas Challenge Hub (daily-streak banks were empty stubs).
    const params = new URLSearchParams({
      autostart: '1',
      level: String(level.level_id),
    });
    router.push(`/challenges/atlas?${params.toString()}`);
  };

  const getMergedLevels = (): (LevelProgress & { label: string; name: string; xpReward: number })[] => {
    if (!subject) return [];
    return subject.levels.map((sl) => {
      const bp = subjectProgress?.levels.find((lp) => lp.level_id === sl.id);
      return {
        level_id: sl.id,
        progress: bp?.progress ?? sl.progress,
        completed: bp?.completed ?? false,
        locked: bp?.locked ?? sl.locked,
        label: sl.label,
        name: sl.name,
        xpReward: sl.xpReward,
      };
    });
  };

  const mergedLevels = getMergedLevels();
  const totalProgress = mergedLevels.length > 0
    ? Math.round(mergedLevels.reduce((sum, l) => sum + l.progress, 0) / mergedLevels.length)
    : 0;

  if (!subject) {
    return (
      <AppLayout>
        <div className="flex min-h-screen items-center justify-center">
          <div className="text-center">
            <h2 className="text-xl font-bold text-[#1E293B] mb-2">Subject Not Found</h2>
            <button onClick={() => router.push('/challenges/daily-streak')} className="text-[#2563EB] underline underline-offset-2">
              Back to Daily Streak
            </button>
          </div>
        </div>
      </AppLayout>
    );
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="w-8 h-8 border-2 border-[#4F46E5] border-t-transparent rounded-full animate-spin" />
        </div>
      </AppLayout>
    );
  }

  const SUBJECT_COLORS: Record<string, string> = {
    'core-mathematics': '#2563EB',
    'integrated-science': '#059669',
    'english-language': '#7C3AED',
    'social-studies': '#D97706',
  };
  const accentColor = SUBJECT_COLORS[subjectId] || '#2563EB';

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-20">
          <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-8 pb-8">
            {/* Back button */}
            <motion.button
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              onClick={() => router.push('/challenges/daily-streak')}
              className="inline-flex items-center gap-2 text-sm text-[#64748B] hover:text-[#1E293B] transition-colors mb-6"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Daily Streak
            </motion.button>

            {/* Subject header */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6"
            >
              <h1
                className="text-2xl sm:text-3xl font-bold text-[#1E293B]"
                style={{ color: accentColor }}
              >
                {subject.name}
              </h1>
              <p className="text-base text-[#475569] mt-1">{subject.description}</p>
            </motion.div>

            {/* Overall progress bar */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className="mb-8"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-[#64748B]">Overall Progress</span>
                <span className="text-sm font-bold" style={{ color: accentColor }}>{totalProgress}%</span>
              </div>
              <div className="w-full h-3 bg-[#F1F5F9] rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{ width: `${totalProgress}%`, backgroundColor: accentColor }}
                />
              </div>
            </motion.div>

            {/* XP & Streak summary — clean cards, no decorative icons */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.08 }}
              className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8"
            >
              <div className="bg-white border border-[#E2E8F0] rounded-xl p-4">
                <p className="text-xs font-semibold text-[#64748B] uppercase tracking-wider">Current XP</p>
                <p className="text-lg font-bold text-[#1E293B] mt-1">{user?.xp?.toLocaleString() || 0}</p>
              </div>
              <div className="bg-white border border-[#E2E8F0] rounded-xl p-4">
                <p className="text-xs font-semibold text-[#64748B] uppercase tracking-wider">Daily Streak</p>
                <p className="text-lg font-bold text-[#1E293B] mt-1">{user?.streak || 0} {(user?.streak || 0) === 1 ? 'day' : 'days'}</p>
              </div>
              <div className="bg-white border border-[#E2E8F0] rounded-xl p-4">
                <p className="text-xs font-semibold text-[#64748B] uppercase tracking-wider">Next Level</p>
                <p className="text-lg font-bold text-[#1E293B] mt-1">250 XP</p>
              </div>
            </motion.div>

            {/* Level progression */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.12 }}
              className="mb-8"
            >
              <h2 className="text-lg font-bold text-[#1E293B] mb-4">Challenge Progression</h2>
              <div className="space-y-4">
                {mergedLevels.map((level, idx) => (
                  <LevelCard
                    key={level.level_id}
                    level={level}
                    accentColor={accentColor}
                    index={idx}
                    onStart={() => handleStartLevel(level)}
                  />
                ))}
              </div>
            </motion.div>



          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}

/** Individual level card with lock/progress state — no icons */
function LevelCard({
  level,
  accentColor,
  index,
  onStart,
}: {
  level: LevelProgress & { label: string; name: string; xpReward: number };
  accentColor: string;
  index: number;
  onStart: () => void;
}) {
  const STATUS_LABELS: Record<string, { text: string; style: string }> = {
    locked: { text: 'Locked', style: 'text-gray-400 border-gray-200 bg-gray-50' },
    completed: { text: 'Completed', style: 'text-[#059669] border-[#059669]/30 bg-[#F0FDF4]' },
    available: { text: 'Available', style: '' },
  };
  const statusKey = level.locked ? 'locked' : level.completed ? 'completed' : 'available';
  const statusStyle = statusKey === 'available'
    ? `text-white border-transparent`
    : STATUS_LABELS[statusKey].style;

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.15 + index * 0.06 }}
      className={`rounded-2xl border transition-all duration-200 ${
        level.locked
          ? 'bg-[#F8FAFC] border-[#E2E8F0] opacity-70'
          : level.completed
            ? 'bg-white border-[#059669]/20'
            : 'bg-white border-[#E2E8F0] hover:border-gray-300 hover:shadow-sm'
      }`}
    >
      <div className="p-5">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <h3 className="font-bold text-[#1E293B] text-sm">{level.name}</h3>
              <span className={`px-2 py-0.5 text-[10px] font-medium rounded-full border ${statusStyle}`}
                style={statusKey === 'available' ? { backgroundColor: accentColor } : {}}
              >
                {level.completed ? 'Completed' : level.locked ? 'Locked' : level.label}
              </span>
            </div>
            <p className="text-xs text-[#64748B]">{level.xpReward} XP on completion</p>
          </div>

          {/* Action button */}
          {level.locked ? (
            <span className="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-400 text-xs font-semibold rounded-lg cursor-not-allowed">
              Locked
            </span>
          ) : level.completed ? (
            <span className="inline-flex items-center px-4 py-2 bg-[#F0FDF4] text-[#059669] text-xs font-semibold rounded-lg">
              Done
            </span>
          ) : (
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onStart}
              className="inline-flex items-center px-5 py-2.5 text-white text-xs font-bold rounded-xl hover:shadow-md transition-all"
              style={{ backgroundColor: accentColor }}
            >
              {level.progress > 0 ? 'Continue' : 'Start Challenge'}
            </motion.button>
          )}
        </div>

        {/* Progress bar */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-[#64748B]">Progress</span>
            <span className="text-xs font-semibold text-[#1E293B]">{level.progress}%</span>
          </div>
          <div className="w-full h-2 bg-[#F1F5F9] rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-700"
              style={{
                width: `${level.progress}%`,
                backgroundColor: level.locked ? '#CBD5E1' : accentColor,
                opacity: level.locked ? 0.3 : 1,
              }}
            />
          </div>
        </div>
      </div>
    </motion.div>
  );
}
