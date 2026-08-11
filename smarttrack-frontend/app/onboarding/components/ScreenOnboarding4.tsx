'use client';

import { motion } from 'framer-motion';

interface Props {
  onNext: () => void;
}

export default function ScreenOnboarding4({ onNext }: Props) {
  return (
    <div className="min-h-screen bg-transparent flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-lg"
      >
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-8 sm:p-10 shadow-sm">
          <div className="w-16 h-16 bg-gradient-to-br from-[#7C3AED] to-[#6D28D9] rounded-2xl flex items-center justify-center mb-6 shadow-lg">
            <span className="text-2xl font-bold text-white">LG</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-bold text-[#1E293B] mb-4">
            Learn & Grow
          </h1>
          <p className="text-base text-[#475569] mb-6 leading-relaxed">
            Access lessons across all your SHS subjects — core and elective — tailored to your
            programme and learning path, not just a few core courses.
          </p>

          <div className="space-y-3 mb-8">
            {[
              { subject: 'Core & elective subjects', color: '#2563EB', bg: 'bg-[#EFF6FF]' },
              { subject: 'Maths, English, Science & more', color: '#D97706', bg: 'bg-[#FFFBEB]' },
              { subject: 'Arts, Business & technical paths', color: '#059669', bg: 'bg-[#F0FDF4]' },
              { subject: 'Matched to your programme', color: '#7C3AED', bg: 'bg-[#F5F3FF]' },
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 + i * 0.08 }}
                className={`flex items-center gap-3 p-3 rounded-xl ${item.bg} border border-[#E2E8F0]`}
              >
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm"
                  style={{ backgroundColor: item.color }}
                >
                  {item.subject.charAt(0)}
                </div>
                <span className="text-sm font-medium text-[#1E293B]">{item.subject}</span>
              </motion.div>
            ))}
          </div>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onNext}
            className="px-8 py-3.5 bg-[#2563EB] text-white font-bold text-base rounded-xl hover:bg-[#1D4ED8] transition-all shadow-lg shadow-[#2563EB]/25 w-full"
          >
            Ready to Learn!
          </motion.button>
        </div>
      </motion.div>
    </div>
  );
}
