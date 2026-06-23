'use client';

import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import type { Subject } from '../data/subjects';
import type { LevelProgress } from '../../../lib/dailyStreakApi';

interface DailyStreakCardProps {
  subject: Subject;
  index: number;
  streak?: number;
  xp?: number;
  liveLevels?: LevelProgress[];
}

export default function DailyStreakCard({ subject, index, streak = 0, xp = 0, liveLevels }: DailyStreakCardProps) {
  const router = useRouter();

  const mergedLevels = subject.levels.map((sl) => {
    const live = liveLevels?.find((lp) => lp.level_id === sl.id);
    return {
      ...sl,
      progress: live?.progress ?? sl.progress,
      locked: live?.locked ?? sl.locked,
      completed: live?.completed ?? false,
    };
  });

  const completedCount = mergedLevels.filter((l) => l.completed).length;
  const totalProgress = mergedLevels.length > 0
    ? Math.round(mergedLevels.reduce((sum, l) => sum + l.progress, 0) / mergedLevels.length)
    : 0;

  const SUBJECT_ACCENT: Record<string, string> = {
    'core-mathematics': '#2563EB',
    'integrated-science': '#059669',
    'english-language': '#7C3AED',
    'social-studies': '#D97706',
  };
  const accentColor = SUBJECT_ACCENT[subject.id] || '#2563EB';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08 }}
      whileHover={{ y: -4, scale: 1.01 }}
      className="group relative bg-white border border-[#E2E8F0] rounded-2xl overflow-hidden hover:shadow-lg transition-all duration-300 cursor-pointer"
      onClick={() => router.push(`/challenges/daily-streak/${subject.id}`)}
    >
      {/* Top accent bar */}
      <div className="h-1.5 w-full" style={{ backgroundColor: accentColor }} />

      <div className="p-5">
        {/* Header row */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-[#1E293B] text-base">{subject.shortName}</h3>
            <p className="text-xs text-[#64748B] mt-0.5">
              {completedCount}/{subject.levels.length} Levels
            </p>
          </div>

          {/* Streak indicator */}
          {streak > 0 && completedCount < subject.levels.length && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-[#FFFBEB] border border-[#FDE68A] rounded-full">
              <svg className="w-3.5 h-3.5 text-[#F59E0B]" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 23c-3.866 0-7-3.134-7-7 0-3.866 3-8 7-13 4 5 7 9.134 7 13 0 3.866-3.134 7-7 7z" />
              </svg>
              <span className="text-xs font-bold text-[#D97706]">{streak}</span>
            </div>
          )}
        </div>

        {/* Description */}
        <p className="text-sm text-[#475569] leading-relaxed mb-4 line-clamp-2">
          {subject.description}
        </p>

        {/* Progress bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs font-medium text-[#64748B]">Progress</span>
            <span className="text-xs font-semibold text-[#1E293B]">{totalProgress}%</span>
          </div>
          <div className="w-full h-2 bg-[#F1F5F9] rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{ width: `${totalProgress}%`, backgroundColor: accentColor }}
            />
          </div>
        </div>

        {/* Bottom row */}
        <div className="flex items-center justify-between">
          <div className="text-xs text-[#64748B]">
            XP Earned: <span className="text-sm font-bold text-[#1E293B]">{xp.toLocaleString()}</span>
          </div>

          <motion.span
            whileHover={{ gap: '10px' }}
            className="inline-flex items-center px-4 py-2 bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg text-xs font-semibold text-[#1E293B] group-hover:bg-[#EEF2FF] group-hover:border-[#C7D2FE] group-hover:text-[#4F46E5] transition-all"
          >
            {completedCount === subject.levels.length ? 'Review' : 'Continue'}
          </motion.span>
        </div>
      </div>
    </motion.div>
  );
}
