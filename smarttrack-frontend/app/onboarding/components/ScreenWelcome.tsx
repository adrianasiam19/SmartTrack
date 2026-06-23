'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface ScreenWelcomeProps {
  onNext: () => void;
}

export default function ScreenWelcome({ onNext }: ScreenWelcomeProps) {
  const [showSubtitle, setShowSubtitle] = useState(false);
  const [showTagline, setShowTagline] = useState(false);
  const [showButton, setShowButton] = useState(false);

  useEffect(() => {
    const t1 = setTimeout(() => setShowSubtitle(true), 600);
    const t2 = setTimeout(() => setShowTagline(true), 1200);
    const t3 = setTimeout(() => setShowButton(true), 2000);
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); };
  }, []);

  useEffect(() => {
    if (!showButton) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onNext(); }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [showButton, onNext]);

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center relative overflow-hidden">
      {/* Premium animated background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{ scale: [1, 1.08, 1], x: [0, 30, 0], y: [0, -20, 0] }}
          transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute -top-40 -left-40 w-[500px] h-[500px] bg-[#2563EB]/5 rounded-full blur-3xl"
        />
        <motion.div
          animate={{ scale: [1, 1.12, 1], x: [0, -40, 0], y: [0, 30, 0] }}
          transition={{ duration: 14, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute -bottom-40 -right-40 w-[500px] h-[500px] bg-[#7C3AED]/5 rounded-full blur-3xl"
        />
        <motion.div
          animate={{ scale: [1, 1.05, 1], x: [0, -20, 0], y: [0, 40, 0] }}
          transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[#F59E0B]/3 rounded-full blur-3xl"
        />
        {/* Subtle grid pattern */}
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{ backgroundImage: 'radial-gradient(circle, #2563EB 1px, transparent 1px)', backgroundSize: '40px 40px' }}
        />
      </div>

      <div className="relative z-10 text-center px-6 max-w-2xl mx-auto">
        {/* Logo animation */}
        <motion.div
          initial={{ scale: 0, rotate: -20 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: 'spring', stiffness: 200, damping: 12, duration: 0.8 }}
          className="mb-10"
        >
          <div className="w-24 h-24 sm:w-28 sm:h-28 mx-auto bg-gradient-to-br from-[#2563EB] to-[#7C3AED] rounded-3xl flex items-center justify-center shadow-2xl shadow-[#2563EB]/25">
            <motion.span
              animate={{ scale: [1, 1.05, 1] }}
              transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
              className="text-white font-bold text-4xl sm:text-5xl"
            >
              A
            </motion.span>
          </div>
        </motion.div>

        {/* Main heading */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: 'easeOut' }}
        >
          <h1 className="text-5xl sm:text-6xl md:text-7xl font-black text-[#1E293B] tracking-tight leading-[1.1] mb-4">
            Welcome to{' '}
            <span className="bg-gradient-to-r from-[#2563EB] to-[#7C3AED] bg-clip-text text-transparent">
              Atlas
            </span>
          </h1>
        </motion.div>

        {/* Tagline */}
        <AnimatePresence>
          {showSubtitle && (
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
              className="text-xl sm:text-2xl text-[#475569] font-light mb-3"
            >
              Discover your strengths.
            </motion.p>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {showTagline && (
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
              className="text-xl sm:text-2xl text-[#475569] font-light mb-12"
            >
              <span className="text-[#2563EB] font-semibold">Shape</span> your future.
            </motion.p>
          )}
        </AnimatePresence>

        {/* CTA Button */}
        <AnimatePresence>
          {showButton && (
            <motion.div
              initial={{ opacity: 0, y: 20, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            >
              <motion.button
                whileHover={{ scale: 1.03, boxShadow: '0 20px 40px rgba(37, 99, 235, 0.25)' }}
                whileTap={{ scale: 0.97 }}
                onClick={onNext}
                className="px-10 py-4 bg-gradient-to-r from-[#2563EB] to-[#7C3AED] text-white font-bold text-lg rounded-2xl shadow-xl shadow-[#2563EB]/20 hover:shadow-2xl transition-all duration-300 inline-flex items-center gap-3 group"
              >
                <span>Get Started</span>
                <motion.span
                  animate={{ x: [0, 5, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                  className="inline-block"
                >
                  →
                </motion.span>
              </motion.button>

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="mt-6 text-sm text-[#94A3B8] font-medium"
              >
                Press <kbd className="px-2 py-0.5 bg-[#F1F5F9] border border-[#E2E8F0] rounded-md text-xs font-mono">Enter</kbd> to continue
              </motion.p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Bottom gradient fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[#F8FAFC] to-transparent pointer-events-none" />
    </div>
  );
}
