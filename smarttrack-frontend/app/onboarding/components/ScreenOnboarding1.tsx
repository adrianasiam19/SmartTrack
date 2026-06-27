'use client';

import { motion } from 'framer-motion';

interface Props {
  onNext: () => void;
}

export default function ScreenOnboarding1({ onNext }: Props) {
  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-lg"
      >
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-8 sm:p-10 text-center shadow-sm">
          {/* Logo */}
          <div className="w-16 h-16 bg-gradient-to-br from-[#2563EB] to-[#7C3AED] rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
            <span className="text-white font-bold text-2xl">A</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-bold text-[#1E293B] mb-4">
            Welcome to Atlas
          </h1>
          <p className="text-base text-[#475569] mb-8 leading-relaxed max-w-sm mx-auto">
            Your intelligent learning companion for SHS students in Ghana. Discover your strengths, improve your skills, and find the perfect university program.
          </p>

          <div className="flex items-center justify-center gap-6 mb-8">
            <div className="text-center">
              <div className="w-10 h-10 bg-[#EFF6FF] rounded-xl flex items-center justify-center mx-auto mb-2">
                <span className="text-lg">🎯</span>
              </div>
              <p className="text-xs text-[#64748B]">Discover</p>
            </div>
            <div className="text-center">
              <div className="w-10 h-10 bg-[#F5F3FF] rounded-xl flex items-center justify-center mx-auto mb-2">
                <span className="text-lg">📚</span>
              </div>
              <p className="text-xs text-[#64748B]">Learn</p>
            </div>
            <div className="text-center">
              <div className="w-10 h-10 bg-[#FFFBEB] rounded-xl flex items-center justify-center mx-auto mb-2">
                <span className="text-lg">🚀</span>
              </div>
              <p className="text-xs text-[#64748B]">Grow</p>
            </div>
          </div>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onNext}
            className="px-8 py-3.5 bg-[#2563EB] text-white font-bold text-base rounded-xl hover:bg-[#1D4ED8] transition-all shadow-lg shadow-[#2563EB]/25 w-full"
          >
            Get Started
          </motion.button>
        </div>
      </motion.div>
    </div>
  );
}
