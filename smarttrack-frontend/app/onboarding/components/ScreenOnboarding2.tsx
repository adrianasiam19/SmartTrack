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

          <h1 className="text-3xl sm:text-4xl font-bold text-[#1E293B] mb-4">
            Starter Arena
          </h1>
          <p className="text-base text-[#475569] mb-6 leading-relaxed">
            Begin with a fun discovery challenge! Atlas will learn about your strengths, interests, and thinking style through:
          </p>

          <div className="space-y-3 mb-8">
            {[
              { icon: '🧠', label: 'Reasoning questions that test your logic' },
              { icon: '🔍', label: 'Pattern recognition challenges' },
              { icon: '💡', label: 'Quick insight prompts about your preferences' },
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
