'use client';

import { motion } from 'framer-motion';

interface Props {
  onNext: () => void;
}

export default function ScreenOnboarding2({ onNext }: Props) {
  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-lg"
      >
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-8 sm:p-10 shadow-sm">
          <div className="w-16 h-16 bg-gradient-to-br from-[#2563EB] to-[#3B82F6] rounded-2xl flex items-center justify-center mb-6 shadow-lg">
            <span className="text-2xl">🌟</span>
          </div>

          <p className="text-xs font-semibold text-[#2563EB] uppercase tracking-wider mb-2">
            Step 2 of 5
          </p>

          <h1 className="text-3xl sm:text-4xl font-bold text-[#1E293B] mb-4">
            Starter Arena
          </h1>
          <p className="text-base text-[#475569] mb-2 leading-relaxed">
            Before Atlas can guide you, it first needs to understand you.
          </p>
          <p className="text-base text-[#475569] mb-6 leading-relaxed">
            The Starter Arena is a short discovery experience designed to learn how you think, what interests you, and where your natural strengths may lie.
          </p>

          <p className="text-sm font-semibold text-[#1E293B] mb-3">
            You will encounter:
          </p>

          <div className="space-y-3 mb-8">
            {[
              { icon: '🧠', label: 'Reasoning activities' },
              { icon: '🔍', label: 'Logic-based questions' },
              { icon: '🔮', label: 'Pattern recognition exercises' },
              { icon: '💡', label: 'Quick Insight questions' },
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 + i * 0.1 }}
                className="flex items-center gap-3 p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]"
              >
                <span className="text-lg">{item.icon}</span>
                <span className="text-sm text-[#475569]">{item.label}</span>
              </motion.div>
            ))}
          </div>

          <div className="bg-[#EFF6FF] border border-[#BFDBFE] rounded-xl p-4 mb-6">
            <p className="text-sm text-[#475569] leading-relaxed">
              Throughout the experience, Atlas will occasionally ask psychometric questions that help build a deeper understanding of your interests, preferences, and thinking style.
            </p>
          </div>

          <div className="bg-[#F0FDF4] border border-[#BBF7D0] rounded-xl p-4 mb-8">
            <p className="text-sm text-[#475569] leading-relaxed">
              There are no timers and no pressure. The goal is not to test what you know. The goal is to understand who you are. Atlas uses these insights to personalise your journey from the very beginning.
            </p>
          </div>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onNext}
            className="px-8 py-3.5 bg-[#2563EB] text-white font-bold text-base rounded-xl hover:bg-[#1D4ED8] transition-all shadow-lg shadow-[#2563EB]/25 w-full"
          >
            Sounds Fun!
          </motion.button>
        </div>
      </motion.div>
    </div>
  );
}
