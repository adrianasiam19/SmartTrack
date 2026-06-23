'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState } from 'react';

interface XPAnimationProps {
  xpGained: number;
  streak?: number;
  levelUp?: boolean;
  newRank?: string | null;
  isCorrect: boolean;
  onComplete?: () => void;
}

export default function XPAnimation({
  xpGained,
  streak,
  levelUp,
  newRank,
  isCorrect,
  onComplete,
}: XPAnimationProps) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      onComplete?.();
    }, 2200);
    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, scale: 0.5, y: 40 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.8, y: -40 }}
          transition={{ type: 'spring', stiffness: 300, damping: 20 }}
          className="text-center py-6"
        >
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.1, type: 'spring', stiffness: 400 }}
            className={`inline-flex items-center gap-3 text-4xl font-black mb-3 ${
              isCorrect ? 'text-[#4F46E5]' : 'text-red-500'
            }`}
          >
            {isCorrect ? (
              <>+{xpGained} XP</>
            ) : (
              <>+{Math.max(2, Math.floor(xpGained / 3))} XP</>
            )}
          </motion.div>

          {streak !== undefined && streak > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="flex items-center justify-center gap-2 text-[#D97706] font-bold text-lg mb-2"
            >
              {streak} day streak!
            </motion.div>
          )}

          {levelUp && (
            <motion.div
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5, type: 'spring', stiffness: 300 }}
              className="text-[#D97706] font-black text-xl mb-1"
            >
              LEVEL UP!
            </motion.div>
          )}

          {newRank && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
              className="text-[#4F46E5] font-bold text-lg"
            >
              New Rank: {newRank}
            </motion.div>
          )}

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.15 }}
            className={`text-lg font-medium mt-1 ${
              isCorrect ? 'text-[#4F46E5]' : 'text-gray-400'
            }`}
          >
            {isCorrect ? 'Correct!' : 'Almost there. Try again next time!'}
          </motion.div>

          <motion.div
            className="w-full max-w-xs h-1.5 bg-gray-100 rounded-full mx-auto mt-4 overflow-hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            <motion.div
              className={`h-full rounded-full ${isCorrect ? 'bg-[#4F46E5]' : 'bg-red-400/50'}`}
              initial={{ width: 0 }}
              animate={{ width: '100%' }}
              transition={{ duration: 1.5, ease: 'easeOut' }}
            />
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
