'use client';

import { motion } from 'framer-motion';

interface StreakIndicatorProps {
  streak: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export default function StreakIndicator({
  streak,
  size = 'md',
  showLabel = true,
}: StreakIndicatorProps) {
  const sizeClasses = {
    sm: 'text-sm gap-1',
    md: 'text-lg gap-1.5',
    lg: 'text-2xl gap-2',
  };

  const textSizes = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  };

  const getColour = () => {
    if (streak >= 30) return 'text-[#D97706]';
    if (streak >= 14) return 'text-[#D97706]';
    if (streak >= 7) return 'text-[#D97706]';
    if (streak >= 3) return 'text-[#4F46E5]';
    return 'text-gray-400';
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`flex items-center ${sizeClasses[size]} ${getColour()}`}
      title={`${streak} day streak`}
    >
      <span className={`font-black ${getColour()}`}>{streak}</span>
      {showLabel && (
        <span className={`${textSizes[size]} font-medium opacity-70`}>
          {streak === 1 ? 'day' : 'days'}
        </span>
      )}
    </motion.div>
  );
}
