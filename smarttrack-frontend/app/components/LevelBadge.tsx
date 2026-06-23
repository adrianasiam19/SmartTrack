'use client';

import { motion } from 'framer-motion';

interface LevelBadgeProps {
  rank: string;
  xp: number;
  xpForNext?: number;
  size?: 'sm' | 'md' | 'lg';
}

const RANK_CONFIG: Record<string, { label: string; colour: string; bgColour: string }> = {
  Beginner: { label: 'Beginner', colour: 'text-gray-400', bgColour: 'bg-gray-100' },
  'Rising Scholar': { label: 'Rising Scholar', colour: 'text-[#4F46E5]', bgColour: 'bg-[#EEF2FF]' },
  'Elite Challenger': { label: 'Elite Challenger', colour: 'text-[#D97706]', bgColour: 'bg-[#FFFBEB]' },
  'Logic Master': { label: 'Logic Master', colour: 'text-[#D97706]', bgColour: 'bg-[#FFFBEB]' },
  'Grand Scholar': { label: 'Grand Scholar', colour: 'text-[#F43F5E]', bgColour: 'bg-[#FFF1F2]' },
  'Atlas Prodigy': { label: 'Atlas Prodigy', colour: 'text-[#4F46E5]', bgColour: 'bg-[#EEF2FF]' },
  Legend: { label: 'Legend', colour: 'text-[#D97706]', bgColour: 'bg-[#FFFBEB]' },
};

export default function LevelBadge({
  rank,
  xp,
  xpForNext = 500,
  size = 'md',
}: LevelBadgeProps) {
  const config = RANK_CONFIG[rank] || RANK_CONFIG['Beginner'];
  const progress = Math.min(100, (xp % xpForNext) / xpForNext * 100);

  const sizeClasses = {
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };

  const titleSize = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-lg',
  };

  const xpSize = {
    sm: 'text-lg',
    md: 'text-xl',
    lg: 'text-3xl',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`${sizeClasses[size]} ${config.bgColour} rounded-xl border border-gray-200`}
    >
      <div className="flex items-center gap-3">
        <div className="flex-1 min-w-0">
          <p className={`${titleSize[size]} font-bold ${config.colour}`}>{config.label}</p>
          <div className="flex items-center gap-1 mt-0.5">
            <span className={`${xpSize[size]} font-black text-[#1E293B]`}>{xp.toLocaleString()}</span>
            <span className="text-xs text-gray-500">XP</span>
          </div>
        </div>
      </div>

      <div className="mt-2 w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 1, ease: 'easeOut' }}
          className="h-full bg-gradient-to-r from-[#4F46E5] to-[#D97706] rounded-full"
        />
      </div>
      <p className="text-[10px] text-gray-500 mt-1 text-right">
        {xpForNext - (xp % xpForNext)} XP to next rank
      </p>
    </motion.div>
  );
}
