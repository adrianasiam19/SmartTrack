'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface XpGaugeProps {
  xp: number;
  rank: string;
  streak: number;
  xpForNextRank?: number;
}

const RANK_COLORS: Record<string, { text: string; bg: string; gradient: string; border: string; gauge: string }> = {
  Beginner: {
    text: 'text-[#64748B]',
    bg: 'bg-[#F1F5F9]',
    gradient: 'from-[#64748B] to-[#94A3B8]',
    border: 'border-[#CBD5E1]',
    gauge: '#64748B',
  },
  Bronze: {
    text: 'text-[#B45309]',
    bg: 'bg-[#FFFBEB]',
    gradient: 'from-[#D97706] to-[#F59E0B]',
    border: 'border-[#FDE68A]',
    gauge: '#D97706',
  },
  Silver: {
    text: 'text-[#4B5563]',
    bg: 'bg-[#F1F5F9]',
    gradient: 'from-[#6B7280] to-[#9CA3AF]',
    border: 'border-[#D1D5DB]',
    gauge: '#6B7280',
  },
  Gold: {
    text: 'text-[#B45309]',
    bg: 'bg-[#FEF3C7]',
    gradient: 'from-[#F59E0B] to-[#FBBF24]',
    border: 'border-[#FCD34D]',
    gauge: '#F59E0B',
  },
  'Elite Challenger': {
    text: 'text-[#7C3AED]',
    bg: 'bg-[#F5F3FF]',
    gradient: 'from-[#7C3AED] to-[#A78BFA]',
    border: 'border-[#C4B5FD]',
    gauge: '#7C3AED',
  },
};

const NEXT_RANK_THRESHOLDS: Record<string, number> = {
  Beginner: 100,
  Bronze: 250,
  Silver: 500,
  Gold: 1000,
  'Elite Challenger': 2000,
};

function getRankConfig(rank: string) {
  return RANK_COLORS[rank] || RANK_COLORS.Beginner;
}

function getXpForCurrentRank(rank: string): number {
  const rankOrder = ['Beginner', 'Bronze', 'Silver', 'Gold', 'Elite Challenger'];
  const idx = rankOrder.indexOf(rank);
  if (idx <= 0) return 0;
  let total = 0;
  for (let i = 0; i < idx; i++) {
    total += NEXT_RANK_THRESHOLDS[rankOrder[i]] || 100;
  }
  return total;
}

function getXpForNextRank(rank: string): number {
  return NEXT_RANK_THRESHOLDS[rank] || 100;
}

function getNextRank(rank: string): string {
  const rankOrder = ['Beginner', 'Bronze', 'Silver', 'Gold', 'Elite Challenger'];
  const idx = rankOrder.indexOf(rank);
  if (idx < 0 || idx >= rankOrder.length - 1) return 'Max';
  return rankOrder[idx + 1];
}

export default function XpGauge({
  xp = 0,
  rank = 'Beginner',
  streak = 0,
}: XpGaugeProps) {
  const [animatedXp, setAnimatedXp] = useState(0);

  useEffect(() => {
    const duration = 800;
    const steps = 20;
    const increment = xp / steps;
    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= xp) {
        setAnimatedXp(xp);
        clearInterval(timer);
      } else {
        setAnimatedXp(Math.round(current));
      }
    }, duration / steps);
    return () => clearInterval(timer);
  }, [xp]);

  const rankConfig = getRankConfig(rank);
  const xpForCurrent = getXpForCurrentRank(rank);
  const xpForNext = getXpForNextRank(rank);
  const nextRank = getNextRank(rank);
  const progressInRank = Math.min(xp - xpForCurrent, xpForNext);
  const progressPercent = Math.min(Math.round((progressInRank / xpForNext) * 100), 100);
  const isMaxRank = nextRank === 'Max';

  const size = 120;
  const strokeWidth = 10;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (progressPercent / 100) * circumference;

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white border border-[#E2E8F0] rounded-2xl p-6"
    >
      <div className="flex items-center gap-6">
        {/* Radial Gauge */}
        <div className="relative flex-shrink-0">
          <svg width={size} height={size} className="transform -rotate-90">
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke="#F1F5F9"
              strokeWidth={strokeWidth}
            />
            <motion.circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke={rankConfig.gauge}
              strokeWidth={strokeWidth}
              strokeLinecap="round"
              strokeDasharray={circumference}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset: offset }}
              transition={{ duration: 1, ease: 'easeOut' }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <motion.span
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.5, type: 'spring', stiffness: 200 }}
              className="text-2xl font-black text-[#1E293B]"
            >
              {progressPercent}
            </motion.span>
            <span className="text-[10px] text-[#64748B] font-medium">Progress</span>
          </div>
        </div>

        {/* Stats */}
        <div className="flex-1 min-w-0 space-y-3">
          {/* Current Rank */}
          <div>
            <span className="text-xs font-semibold text-[#64748B] uppercase tracking-wider">Current Rank</span>
            <div className="mt-1">
              <span className={`inline-block px-3 py-1 rounded-lg text-sm font-bold ${rankConfig.bg} ${rankConfig.text} border ${rankConfig.border}`}>
                {rank}
              </span>
            </div>
          </div>

          {/* XP Counter */}
          <div>
            <span className="text-xs font-semibold text-[#64748B] uppercase tracking-wider">Total XP</span>
            <div className="flex items-baseline gap-1 mt-1">
              <motion.span
                key={xp}
                initial={{ scale: 1.3 }}
                animate={{ scale: 1 }}
                className="text-3xl font-black text-[#1E293B]"
              >
                {animatedXp.toLocaleString()}
              </motion.span>
              <span className="text-sm text-[#64748B]">XP</span>
            </div>
          </div>

          {/* Next Rank */}
          <div>
            <span className="text-xs font-semibold text-[#64748B] uppercase tracking-wider">
              {isMaxRank ? 'Max Level' : `Next: ${nextRank}`}
            </span>
            {!isMaxRank && (
              <p className="text-sm text-[#64748B] mt-0.5">
                {xpForNext - progressInRank > 0
                  ? `${(xpForNext - progressInRank).toLocaleString()} XP needed`
                  : 'Ready to rank up!'}
              </p>
            )}
          </div>

          {/* Streak - only icon allowed */}
          <div className="flex items-center gap-2 pt-1">
            <svg className="w-4 h-4 text-[#F59E0B]" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 23c-3.866 0-7-3.134-7-7 0-3.866 3-8 7-13 4 5 7 9.134 7 13 0 3.866-3.134 7-7 7z" />
            </svg>
            <span className="text-sm font-bold text-[#1E293B]">{streak}</span>
            <span className="text-xs text-[#64748B]">{streak === 1 ? 'day' : 'days'} streak</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
