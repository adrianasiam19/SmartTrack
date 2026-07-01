'use client';

import { motion } from 'framer-motion';

interface Props {
  onNext: () => void;
}

export default function ScreenOnboarding3({ onNext }: Props) {
  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-lg"
      >
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-8 sm:p-10 shadow-sm">
          <div className="w-16 h-16 bg-gradient-to-br from-[#F59E0B] to-[#D97706] rounded-2xl flex items-center justify-center mb-6 shadow-lg">
            <span className="text-2xl font-bold text-white">XP</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-bold text-[#1E293B] mb-4">
            Earn Your Way
          </h1>
          <p className="text-base text-[#475569] mb-6 leading-relaxed">
            Complete challenges to earn XP, build your streak, and climb the leaderboard. The more you learn, the more you grow!
          </p>

          <div className="grid grid-cols-3 gap-4 mb-8">
            {[
              { value: 'XP', label: 'Experience Points', color: 'text-[#2563EB]', bg: 'bg-[#EFF6FF]' },
              { value: 'Days', label: 'Daily Streak', color: 'text-[#D97706]', bg: 'bg-[#FFFBEB]' },
              { value: 'Rank', label: 'Leaderboard', color: 'text-[#7C3AED]', bg: 'bg-[#F5F3FF]' },
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + i * 0.1 }}
                className={`${item.bg} rounded-xl p-4 text-center border border-[#E2E8F0]`}
              >
                <div className={`text-2xl font-bold ${item.color} mb-1`}>{item.value}</div>
                <div className="text-xs text-[#64748B]">{item.label}</div>
              </motion.div>
            ))}
          </div>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onNext}
            className="px-8 py-3.5 bg-[#2563EB] text-white font-bold text-base rounded-xl hover:bg-[#1D4ED8] transition-all shadow-lg shadow-[#2563EB]/25 w-full"
          >
            Let&apos;s Go!
          </motion.button>
        </div>
      </motion.div>
    </div>
  );
}
