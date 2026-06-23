'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface AtlasIntroAnimationProps {
  onFinish: () => void;
}

const FEATURES = [
  {
    label: 'Learning Center',
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
      </svg>
    ),
  },
  {
    label: 'Challenges',
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 007.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721C7.456 2.41 9.71 2.25 12 2.25c2.291 0 4.545.16 6.75.47v1.516M18.75 4.236c.982.143 1.954.317 2.916.52A6.003 6.003 0 0016.27 9.728M18.75 4.236V4.5c0 2.108-.966 3.99-2.48 5.228m0 0a6.023 6.023 0 01-2.77.896m0 0a6.022 6.022 0 01-2.77-.896m0 0a6.023 6.023 0 01-2.77-.896" />
      </svg>
    ),
  },
  {
    label: 'Daily Streaks',
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15.362 5.214A8.252 8.252 0 0112 21 8.25 8.25 0 016.038 7.048 8.287 8.287 0 009 9.6a8.983 8.983 0 013.361-6.867 8.21 8.21 0 003 2.48z" />
      </svg>
    ),
  },
  {
    label: 'XP Progress',
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
      </svg>
    ),
  },
  {
    label: 'Recommendations',
    icon: (
      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
      </svg>
    ),
  },
];

export default function AtlasIntroAnimation({ onFinish }: AtlasIntroAnimationProps) {
  const [phase, setPhase] = useState(0);

  // ── TIMING ──
  useEffect(() => {
    if (phase === 0) {
      const t = setTimeout(() => setPhase(1), 1800);
      return () => clearTimeout(t);
    }
  }, [phase]);

  useEffect(() => {
    if (phase === 1) {
      const t = setTimeout(() => setPhase(2), 2000);
      return () => clearTimeout(t);
    }
  }, [phase]);

  useEffect(() => {
    if (phase === 2) {
      const t = setTimeout(() => setPhase(3), 2000);
      return () => clearTimeout(t);
    }
  }, [phase]);

  useEffect(() => {
    if (phase === 3) {
      const t = setTimeout(() => setPhase(4), 3000);
      return () => clearTimeout(t);
    }
  }, [phase]);

  useEffect(() => {
    if (phase === 4) {
      const t = setTimeout(() => onFinish(), 900);
      return () => clearTimeout(t);
    }
  }, [phase, onFinish]);

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center overflow-hidden bg-[#F8FAFC]">
      {/* ── ANIMATED GRADIENT BACKGROUND ── */}
      <motion.div
        className="absolute inset-0 opacity-[0.12]"
        animate={{
          background: [
            'radial-gradient(ellipse 80% 60% at 20% 50%, #4F46E5 0%, transparent 70%)',
            'radial-gradient(ellipse 80% 60% at 80% 50%, #7C3AED 0%, transparent 70%)',
            'radial-gradient(ellipse 80% 60% at 50% 30%, #C7D2FE 0%, transparent 70%)',
            'radial-gradient(ellipse 80% 60% at 20% 50%, #4F46E5 0%, transparent 70%)',
          ],
        }}
        transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut' }}
      />

      {/* ── SUBTLE GRID PATTERN ── */}
      <div
        className="absolute inset-0 opacity-[0.04]"
        style={{
          backgroundImage: `
            linear-gradient(rgba(79,70,229,0.08) 1px, transparent 1px),
            linear-gradient(90deg, rgba(79,70,229,0.08) 1px, transparent 1px)
          `,
          backgroundSize: '60px 60px',
        }}
      />

      {/* ── CONTENT ── */}
      <div className="relative z-10 w-full max-w-3xl mx-auto px-6 flex flex-col items-center justify-center min-h-screen">
        {/* ── PHASE 0: ATLAS LOGO ── */}
        {phase >= 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.01 }}
            className="flex flex-col items-center"
          >
            {/* Accent line */}
            <motion.div
              initial={{ scaleX: 0 }}
              animate={{ scaleX: phase >= 1 ? 0 : 1 }}
              transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
              style={{ originX: 0.5 }}
              className="w-12 h-[2px] bg-gradient-to-r from-[#4F46E5] via-[#7C3AED] to-[#C7D2FE] rounded-full mb-8"
            />

            {/* ATLAS main title */}
            <div className="flex items-center gap-1 sm:gap-2 mb-3">
              {['A', 'T', 'L', 'A', 'S'].map((char, i) => (
                <motion.span
                  key={i}
                  initial={{ opacity: 0, y: 40, filter: 'blur(12px)' }}
                  animate={{
                    opacity: phase >= 4 ? 0 : 1,
                    y: phase >= 4 ? -20 : 0,
                    filter: phase >= 4 ? 'blur(8px)' : 'blur(0px)',
                  }}
                  transition={{
                    duration: phase >= 4 ? 0.4 : 0.7,
                    delay: phase >= 4 ? i * 0.04 : 0.3 + i * 0.1,
                    ease: [0.16, 1, 0.3, 1],
                  }}
                  className="text-6xl sm:text-7xl md:text-8xl font-black tracking-[-0.05em] text-[#4F46E5]"
                >
                  {char}
                </motion.span>
              ))}
            </div>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 15 }}
              animate={{
                opacity: phase >= 4 ? 0 : phase >= 1 ? 0 : 1,
                y: phase >= 4 ? -15 : 0,
              }}
              transition={{ duration: 0.5, delay: 1.0, ease: [0.16, 1, 0.3, 1] }}
              className="text-sm text-[#94A3B8] font-light tracking-[0.25em] uppercase"
            >
              Discover Your Future
            </motion.p>
          </motion.div>
        )}

        {/* ── PHASE 1: FULL MEANING ── */}
        {phase >= 1 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{
              opacity: phase >= 4 ? 0 : phase >= 2 ? 0.5 : 1,
              y: phase >= 4 ? -30 : phase >= 2 ? -10 : 0,
            }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="flex flex-col items-center mt-8"
          >
            {/* Divider line */}
            <motion.div
              initial={{ scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={{ duration: 0.7, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
              style={{ originX: 0.5 }}
              className="w-8 h-[1.5px] bg-gradient-to-r from-[#4F46E5]/60 to-[#7C3AED]/60 rounded-full mb-6"
            />

            {/* Meaning words */}
            <div className="flex flex-wrap justify-center gap-x-6 gap-y-1.5">
              {[
                { word: 'Adaptive', color: '#4F46E5' },
                { word: 'Tutoring', color: '#7C3AED' },
                { word: 'Learning', color: '#4F46E5' },
                { word: 'Advisory', color: '#7C3AED' },
                { word: 'System', color: '#D97706' },
              ].map((item, i) => (
                <motion.span
                  key={i}
                  initial={{ opacity: 0, y: 20, filter: 'blur(6px)' }}
                  animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                  transition={{
                    duration: 0.5,
                    delay: 0.2 + i * 0.12,
                    ease: [0.16, 1, 0.3, 1],
                  }}
                  className="text-base sm:text-lg font-medium tracking-[-0.01em]"
                  style={{ color: item.color }}
                >
                  {item.word}
                  {i < 4 && (
                    <span className="ml-3 text-[#CBD5E1] font-light hidden sm:inline">·</span>
                  )}
                </motion.span>
              ))}
            </div>
          </motion.div>
        )}

        {/* ── PHASE 2: TAGLINE ── */}
        {phase >= 2 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{
              opacity: phase >= 4 ? 0 : 1,
              y: phase >= 4 ? -20 : 0,
            }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="flex flex-col items-center mt-10"
          >
            {/* Divider line */}
            <motion.div
              initial={{ scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={{ duration: 0.6, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
              style={{ originX: 0.5 }}
              className="w-8 h-[1.5px] bg-gradient-to-r from-[#D97706]/60 to-[#4F46E5]/60 rounded-full mb-6"
            />

            <motion.p
              initial={{ opacity: 0, y: 20, filter: 'blur(6px)' }}
              animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
              transition={{ duration: 0.6, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
              className="text-2xl sm:text-3xl md:text-4xl font-bold text-[#1E293B] text-center leading-[1.15] tracking-[-0.02em]"
            >
              Discover your{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#4F46E5] to-[#7C3AED]">
                strengths
              </span>
              .
            </motion.p>
            <motion.p
              initial={{ opacity: 0, y: 20, filter: 'blur(6px)' }}
              animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
              transition={{ duration: 0.6, delay: 0.35, ease: [0.16, 1, 0.3, 1] }}
              className="text-2xl sm:text-3xl md:text-4xl font-bold text-[#1E293B] text-center leading-[1.15] tracking-[-0.02em] mt-1"
            >
              Shape your{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#D97706] to-[#B45309]">
                future
              </span>
              .
            </motion.p>
          </motion.div>
        )}

        {/* ── PHASE 3: FEATURE PILLS ── */}
        {phase >= 3 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{
              opacity: phase >= 4 ? 0 : 1,
              y: phase >= 4 ? -15 : 0,
            }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            className="flex flex-col items-center mt-12"
          >
            {/* Divider line */}
            <motion.div
              initial={{ scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={{ duration: 0.5, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
              style={{ originX: 0.5 }}
              className="w-8 h-[1.5px] bg-gradient-to-r from-[#7C3AED]/60 to-[#D97706]/60 rounded-full mb-6"
            />

            <motion.p
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
              className="text-xs text-[#94A3B8] tracking-[0.15em] uppercase font-medium mb-5"
            >
              Everything you need
            </motion.p>

            <div className="flex flex-wrap justify-center gap-2.5 max-w-lg">
              {FEATURES.map((feature, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 15, scale: 0.9 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{
                    duration: 0.4,
                    delay: 0.15 + i * 0.08,
                    ease: [0.16, 1, 0.3, 1],
                  }}
                  className="group flex items-center gap-2 px-3.5 py-2 rounded-full bg-white border border-[#E2E8F0] hover:border-[#C7D2FE] hover:bg-[#EEF2FF] hover:shadow-sm transition-all duration-300 cursor-default"
                >
                  <span className="text-[#4F46E5] group-hover:text-[#4338CA] transition-colors">
                    {feature.icon}
                  </span>
                  <span className="text-xs font-medium text-[#475569] group-hover:text-[#1E293B] transition-colors">
                    {feature.label}
                  </span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* ── SKIP BUTTON ── */}
        {phase < 4 && (
          <button
            onClick={onFinish}
            className="absolute bottom-8 right-4 sm:right-8 z-20 px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm text-[#94A3B8] hover:text-[#4F46E5] hover:bg-[#EEF2FF] rounded-lg transition-all duration-200 font-medium"
          >
            Skip →
          </button>
        )}

        {/* ── PROGRESS INDICATOR ── */}
        <div className="hidden sm:flex absolute bottom-8 left-1/2 -translate-x-1/2 items-center gap-2">
          {[0, 1, 2, 3].map((p) => (
            <motion.div
              key={p}
              animate={{
                width: phase === p ? 20 : phase > p ? 4 : 4,
                opacity: phase >= p ? 1 : 0.2,
              }}
              transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
              className={`h-1 rounded-full ${
                phase > p
                  ? 'bg-gradient-to-r from-[#4F46E5] to-[#7C3AED]'
                  : phase === p
                  ? 'bg-gradient-to-r from-[#4F46E5] to-[#7C3AED]'
                  : 'bg-[#E2E8F0]'
              }`}
            />
          ))}
        </div>

        {/* ── BOTTOM BRANDING ── */}
        {phase < 4 && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="absolute bottom-8 left-4 sm:left-8 text-[10px] text-[#CBD5E1] tracking-[0.2em] uppercase font-medium"
          >
            Atlas
          </motion.p>
        )}
      </div>
    </div>
  );
}
