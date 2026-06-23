'use client';

import { motion } from 'framer-motion';
import { ChevronRight } from 'lucide-react';
import type { ChallengeCategory } from '../lib/challengesApi';

interface ChallengeCardProps {
  category: ChallengeCategory;
  onPlay: (category: ChallengeCategory) => void;
  index?: number;
  isNew?: boolean;
  isStarter?: boolean;
}

export default function ChallengeCard({
  category,
  onPlay,
  index = 0,
  isNew = false,
  isStarter = false,
}: ChallengeCardProps) {
  const difficultyColors: Record<string, string> = {
    Beginner: 'text-[#4F46E5] border-[#C7D2FE] bg-[#EEF2FF]',
    Intermediate: 'text-[#D97706] border-[#FDE68A] bg-[#FFFBEB]',
    Advanced: 'text-[#F43F5E] border-[#FFE4E6] bg-[#FFF1F2]',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06 }}
      whileHover={{ y: -2 }}
      className={`group relative rounded-xl border transition-all duration-200 cursor-pointer overflow-hidden ${
        isStarter
          ? 'border-[#4F46E5] bg-[#EEF2FF] hover:shadow-md'
          : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
      }`}
      onClick={() => onPlay(category)}
    >
      <div className="relative p-5 z-10">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-sm font-bold ${
              isStarter ? 'bg-[#4F46E5] text-white' : 'bg-gray-100 text-gray-600'
            }`}>
              {category.title.charAt(0)}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-[#1E293B] text-sm">
                  {category.title}
                </h3>
                {isNew && (
                  <span className="px-1.5 py-0.5 text-[9px] font-bold bg-[#4F46E5] text-white rounded uppercase tracking-wider">
                    New
                  </span>
                )}
              </div>
              <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-medium rounded-full border mt-1 ${
                difficultyColors[category.difficulty] || difficultyColors.Beginner
              }`}>
                {category.difficulty}
              </span>
            </div>
          </div>
          <div className="text-xs text-gray-400 whitespace-nowrap">
            {category.estimated_time}
          </div>
        </div>

        <p className="text-sm text-gray-500 leading-relaxed mb-4 line-clamp-2">
          {category.description}
        </p>

        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400 uppercase tracking-wider font-medium">
            {category.domain}
          </span>

          {isStarter ? (
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-[#4F46E5] text-white text-xs font-semibold rounded-lg hover:bg-[#4338CA] transition-colors">
              Start Journey
              <ChevronRight className="w-3.5 h-3.5" />
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-xs font-medium text-[#4F46E5] group-hover:text-[#4338CA] transition-colors">
              Play
              <ChevronRight className="w-3.5 h-3.5" />
            </span>
          )}
        </div>
      </div>
    </motion.div>
  );
}
