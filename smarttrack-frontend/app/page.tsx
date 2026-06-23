'use client';

import Link from 'next/link';
import { AnimatePresence, motion } from 'framer-motion';
import { useState, useEffect, useCallback, useRef } from 'react';
import AtlasIntroAnimation from './components/AtlasIntroAnimation';

export default function Home() {
  const [showIntro, setShowIntro] = useState(true);

  const handleIntroFinish = useCallback(() => {
    setShowIntro(false);
  }, []);

  if (showIntro) {
    return <AtlasIntroAnimation onFinish={handleIntroFinish} />;
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC]">

      {/* ── SPLIT-SCREEN HERO ── */}
      <section className="flex flex-col lg:flex-row min-h-screen">

        {/* ── LEFT PANEL (60%) - IMAGE + TEXT ── */}
        <div className="relative lg:w-[60%] min-h-[60vh] lg:min-h-screen overflow-hidden">
          {/* Background image */}
          <div
            className="absolute inset-0 bg-cover bg-center bg-no-repeat"
            style={{
              backgroundImage: 'url("https://images.pexels.com/photos/11025022/pexels-photo-11025022.jpeg?auto=compress&cs=tinysrgb&w=1200&h=900&dpr=1")',
            }}
          />
          {/* Dark overlay */}
          <div className="absolute inset-0 bg-gradient-to-r from-[#1E3A8A]/85 via-[#2563EB]/70 to-[#7C3AED]/55" />

          {/* Subtle pattern overlay */}
          <div
            className="absolute inset-0 opacity-[0.04]"
            style={{
              backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.8) 1px, transparent 1px)',
              backgroundSize: '32px 32px',
            }}
          />

          {/* Content */}
          <div className="relative z-10 flex flex-col justify-between h-full p-10 lg:p-16 xl:p-20">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/20 backdrop-blur-md rounded-xl flex items-center justify-center border border-white/20 shadow-lg">
                <span className="text-white font-bold text-lg">A</span>
              </div>
              <span className="text-2xl font-bold text-white tracking-tight">Atlas</span>
            </div>

            {/* Center text */}
            <div className="max-w-xl">
              <motion.h1
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-black text-white leading-[1.1] tracking-tight mb-6"
              >
                Discover Your
                <br />
                Strengths.
                <br />
                <span className="text-[#F59E0B]">Shape Your Future.</span>
              </motion.h1>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.35 }}
                className="text-lg sm:text-xl text-[#BFDBFE] leading-relaxed max-w-lg font-light"
              >
                <span className="font-semibold text-white">Learn.</span>
                {' '}
                <span className="font-semibold text-white">Practice.</span>
                {' '}
                <span className="font-semibold text-[#F59E0B]">Get Recommended.</span>
              </motion.p>
            </div>

            {/* Bottom spacer */}
            <div />
          </div>
        </div>

        {/* ── RIGHT PANEL (40%) - AUTH CARD ── */}
        <div className="lg:w-[40%] flex items-center justify-center p-8 lg:p-12 xl:p-16 bg-[#F8FAFC]">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="w-full max-w-sm"
          >
            <div className="bg-white rounded-2xl border border-[#BFDBFE] p-8 lg:p-10 shadow-xl shadow-[#2563EB]/5">
              {/* Welcome */}
              <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-[#1E293B] mb-2">Welcome to Atlas</h2>
                <p className="text-[#475569]">Create an account or sign in to continue your journey.</p>
              </div>

              {/* CTA Buttons */}
              <div className="space-y-4">
                <Link
                  href="/register"
                  className="block w-full text-center px-6 py-3.5 bg-gradient-to-r from-[#2563EB] to-[#1D4ED8] text-white rounded-xl font-bold text-base hover:from-[#3B82F6] hover:to-[#2563EB] shadow-lg shadow-[#2563EB]/25 hover:shadow-xl hover:shadow-[#2563EB]/30 transition-all duration-200"
                >
                  Create Free Account
                </Link>
                <Link
                  href="/login"
                  className="block w-full text-center px-6 py-3.5 border-2 border-[#BFDBFE] text-[#2563EB] rounded-xl font-semibold text-base hover:bg-[#EFF6FF] hover:border-[#2563EB] transition-all duration-200"
                >
                  Sign In
                </Link>
              </div>

              {/* Divider */}
              <div className="relative my-8">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-[#E2E8F0]" />
                </div>
                <div className="relative flex justify-center">
                  <span className="bg-white px-4 text-sm text-[#94A3B8]">or continue with</span>
                </div>
              </div>

              {/* Google OAuth */}
              <Link
                href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/auth/google/login`}
                className="flex items-center justify-center gap-3 w-full px-6 py-3 border border-[#E2E8F0] rounded-xl text-[#475569] font-medium text-base hover:bg-[#F8FAFC] hover:border-[#CBD5E1] transition-all duration-200"
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                </svg>
                <span>Continue with Google</span>
              </Link>
            </div>

            {/* Trust indicator */}
            <p className="text-center text-sm text-[#94A3B8] mt-6">
              Free for SHS students in Ghana
            </p>
          </motion.div>
        </div>
      </section>

      {/* ── HOW ATLAS WORKS (PRODUCT SHOWCASE) ── */}
      <section className="py-20 lg:py-28 bg-[#F8FAFC]">
        <div className="max-w-7xl mx-auto px-6 lg:px-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <span className="inline-block px-4 py-1.5 bg-[#EFF6FF] border border-[#BFDBFE] rounded-full text-sm font-semibold text-[#2563EB] mb-4">
              Product Showcase
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-[#1E293B] mb-4">
              How Atlas Works
            </h2>
            <p className="text-lg text-[#475569] max-w-2xl mx-auto">
              A complete platform designed to help SHS students discover their strengths and find their path.
            </p>
          </motion.div>

          <div className="flex flex-col lg:flex-row items-center gap-12 lg:gap-16">
            {/* ── LEFT: AUTO-PLAYING PRODUCT DEMO ── */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="w-full lg:w-[55%]"
            >
              <AnimatedDemo />
            </motion.div>

            {/* ── RIGHT: EXPLANATION ── */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.15 }}
              className="w-full lg:w-[45%]"
            >
              <div className="space-y-8">
                {[
                  {
                    step: '01',
                    title: 'Create Your Profile',
                    desc: 'Atlas learns about your interests, strengths, and academic background.',
                    color: '#2563EB',
                    bg: 'bg-[#EFF6FF]',
                    border: 'border-[#BFDBFE]',
                  },
                  {
                    step: '02',
                    title: 'Learn and Practice',
                    desc: 'Access structured learning paths and educational challenges.',
                    color: '#7C3AED',
                    bg: 'bg-[#F5F3FF]',
                    border: 'border-[#DDD6FE]',
                  },
                  {
                    step: '03',
                    title: 'Track Your Progress',
                    desc: 'Earn XP, maintain streaks, and monitor your development.',
                    color: '#F59E0B',
                    bg: 'bg-[#FFFBEB]',
                    border: 'border-[#FDE68A]',
                  },
                  {
                    step: '04',
                    title: 'Receive Recommendations',
                    desc: 'Get personalized programme recommendations based on your performance and profile.',
                    color: '#2563EB',
                    bg: 'bg-[#EFF6FF]',
                    border: 'border-[#BFDBFE]',
                  },
                ].map((item, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.2 + idx * 0.1 }}
                    className="group relative pl-14"
                  >
                    {/* Step number */}
                    <div
                      className="absolute left-0 top-0 w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold text-sm shadow-md"
                      style={{ backgroundColor: item.color }}
                    >
                      {item.step}
                    </div>
                    {/* Connector line */}
                    {idx < 3 && (
                      <div className="absolute left-[19px] top-10 bottom-0 w-0.5 bg-[#E2E8F0]" />
                    )}
                    <h3 className="text-xl font-bold text-[#1E293B] mb-1.5 group-hover:text-[#2563EB] transition-colors">
                      {item.title}
                    </h3>
                    <p className="text-[#475569] leading-relaxed">
                      {item.desc}
                    </p>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ── WHY ATLAS? SECTION ── */}
      <section className="py-20 lg:py-28 bg-white">
        <div className="max-w-6xl mx-auto px-6 lg:px-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <span className="inline-block px-4 py-1.5 bg-[#EFF6FF] border border-[#BFDBFE] rounded-full text-sm font-semibold text-[#2563EB] mb-4">
              Why Atlas?
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold text-[#1E293B] mb-4">
              Everything you need to find your path
            </h2>
            <p className="text-lg text-[#475569] max-w-2xl mx-auto">
              Atlas helps SHS students discover their strengths and find university programs that truly fit.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-12">
            {[
              {
                title: 'Discover your strengths',
                desc: 'Understand your interests and abilities through interactive challenges and assessments.',
                gradient: 'from-[#2563EB] to-[#3B82F6]',
                icon: (
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                  </svg>
                ),
              },
              {
                title: 'Explore suitable programmes',
                desc: 'Receive personalized academic recommendations based on your unique profile and performance.',
                gradient: 'from-[#7C3AED] to-[#8B5CF6]',
                icon: (
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                  </svg>
                ),
              },
              {
                title: 'Learn and improve',
                desc: 'Build your skills through structured learning modules and engaging academic challenges.',
                gradient: 'from-[#F59E0B] to-[#FBBF24]',
                icon: (
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                  </svg>
                ),
              },
            ].map((item, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.12 }}
                className="group relative bg-[#F8FAFC] rounded-2xl border border-[#E2E8F0] p-8 hover:border-[#BFDBFE] hover:shadow-lg hover:shadow-[#2563EB]/5 transition-all duration-300"
              >
                {/* Checkmark icon */}
                <div className={`w-12 h-12 bg-gradient-to-br ${item.gradient} rounded-xl flex items-center justify-center mb-6 shadow-lg`}>
                  {item.icon}
                </div>
                <h3 className="text-xl font-bold text-[#1E293B] mb-3">{item.title}</h3>
                <p className="text-[#475569] leading-relaxed">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA SECTION ── */}
      <section className="py-20 lg:py-28 bg-gradient-to-r from-[#2563EB] to-[#7C3AED]">
        <div className="max-w-4xl mx-auto px-6 lg:px-10 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              Ready to discover your future?
            </h2>
            <p className="text-lg text-[#BFDBFE] mb-10 max-w-xl mx-auto">
              Join Atlas and take the first step toward finding the university program that fits you best.
            </p>              <Link
              href="/register"
              className="group inline-flex items-center gap-2 px-8 py-4 bg-[#F59E0B] text-white font-bold text-lg rounded-xl hover:bg-[#D97706] shadow-xl shadow-[#F59E0B]/25 hover:shadow-2xl hover:shadow-[#F59E0B]/40 transition-all duration-300"
            >
              Get Started Free
              <span className="text-xl group-hover:translate-x-1 transition-transform inline-block">{'\u2192'}</span>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer className="border-t border-[#E2E8F0] bg-white">
        <div className="max-w-7xl mx-auto px-6 lg:px-10 py-10">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-5">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-[#2563EB] to-[#7C3AED] rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">A</span>
              </div>
              <span className="text-lg font-bold text-[#1E293B]">Atlas</span>
            </div>
            <p className="text-base text-[#94A3B8]">&copy; {new Date().getFullYear()} Atlas. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

// ── ANIMATED PRODUCT DEMO ──

const screens = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    gradient: 'from-[#2563EB] to-[#3B82F6]',
    bg: 'bg-[#EFF6FF]',
  },
  {
    id: 'learning',
    label: 'Learning Center',
    gradient: 'from-[#7C3AED] to-[#8B5CF6]',
    bg: 'bg-[#F5F3FF]',
  },
  {
    id: 'challenges',
    label: 'Challenges',
    gradient: 'from-[#F59E0B] to-[#FBBF24]',
    bg: 'bg-[#FFFBEB]',
  },
  {
    id: 'recommendations',
    label: 'Recommendations',
    gradient: 'from-[#2563EB] to-[#7C3AED]',
    bg: 'bg-[#EFF6FF]',
  },
];

function AnimatedDemo() {
  const [activeIndex, setActiveIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const startInterval = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    intervalRef.current = setInterval(() => {
      setActiveIndex((prev) => (prev + 1) % screens.length);
    }, 4800);
  }, []);

  useEffect(() => {
    if (!isPaused) startInterval();
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, [isPaused, startInterval]);

  const goTo = (index: number) => {
    setActiveIndex(index);
    startInterval();
  };

  const current = screens[activeIndex];

  return (
    <div
      className="bg-white rounded-2xl shadow-2xl shadow-[#2563EB]/10 border border-[#E2E8F0] overflow-hidden"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      {/* Browser chrome */}
      <div className="flex items-center gap-2 px-5 py-3.5 bg-[#F8FAFC] border-b border-[#E2E8F0]">
        <div className="flex gap-1.5">
          <div className="w-3 h-3 rounded-full bg-[#F87171]" />
          <div className="w-3 h-3 rounded-full bg-[#FBBF24]" />
          <div className="w-3 h-3 rounded-full bg-[#34D399]" />
        </div>
        <div className="flex-1 flex justify-center">
          <div className="bg-white border border-[#E2E8F0] rounded-full px-4 py-1.5 text-xs text-[#94A3B8] font-mono flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#34D399]" />
            atlas.app/{current.id}
          </div>
        </div>
        {/* Screen indicator */}
        <div className="text-[10px] text-[#94A3B8] font-mono">
          {activeIndex + 1}/{screens.length}
        </div>
      </div>

      {/* Demo content area */}
      <div className="relative min-h-[340px] sm:min-h-[380px]">
        <AnimatePresence mode="wait">
          <motion.div
            key={current.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.35 }}
            className="absolute inset-0 p-6 sm:p-8"
          >
            {activeIndex === 0 && <DashboardScreen />}
            {activeIndex === 1 && <LearningScreen />}
            {activeIndex === 2 && <ChallengesScreen />}
            {activeIndex === 3 && <RecommendationsScreen />}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Navigation dots */}
      <div className="flex items-center justify-center gap-2 px-6 pb-5">
        {screens.map((screen, idx) => (
          <button
            key={screen.id}
            onClick={() => goTo(idx)}
            className={`transition-all duration-300 rounded-full ${
              idx === activeIndex
                ? 'w-8 h-2 bg-gradient-to-r ' + current.gradient
                : 'w-2 h-2 bg-[#CBD5E1] hover:bg-[#94A3B8]'
            }`}
            aria-label={`Show ${screen.label}`}
          />
        ))}
        {/* Pause indicator */}
        {isPaused && (
          <span className="ml-3 text-[10px] text-[#94A3B8] font-medium uppercase tracking-wider">
            Paused
          </span>
        )}
      </div>
    </div>
  );
}

/* ── DASHBOARD SCREEN ── */
function DashboardScreen() {
  return (
    <div className="space-y-5">
      {/* Welcome row */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
        className="flex items-center justify-between"
      >
        <div>
          <h3 className="text-lg font-bold text-[#1E293B]">Welcome back, Ama</h3>
          <p className="text-sm text-[#64748B]">Continue where you left off</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 bg-gradient-to-r from-[#2563EB]/10 to-[#7C3AED]/10 px-3 py-1.5 rounded-lg border border-[#BFDBFE]">
            <span className="text-sm font-bold text-[#2563EB]">1,280</span>
            <span className="text-xs text-[#64748B]">XP</span>
          </div>
          <div className="flex items-center gap-1.5 bg-[#FFF7ED] px-3 py-1.5 rounded-lg border border-[#FED7AA]">
            <span className="text-sm font-bold text-[#D97706]">7</span>
            <span className="text-xs text-[#D97706]">day streak</span>
          </div>
        </div>
      </motion.div>

      {/* Stats grid */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="grid grid-cols-3 gap-3"
      >
        {[
          { label: 'Challenges Done', value: '24', color: 'text-[#2563EB]', bar: 'w-[70%]' },
          { label: 'Lessons Completed', value: '18', color: 'text-[#7C3AED]', bar: 'w-[55%]' },
          { label: 'Programs Matched', value: '6', color: 'text-[#D97706]', bar: 'w-[40%]' },
        ].map((stat, i) => (
          <div key={i} className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
            <div className={`text-2xl font-black ${stat.color} mb-0.5`}>{stat.value}</div>
            <div className="text-xs text-[#64748B]">{stat.label}</div>
            <div className="mt-2 h-1.5 bg-[#E2E8F0] rounded-full overflow-hidden">
              <div className={`h-full ${stat.bar} bg-gradient-to-r from-[#2563EB] to-[#7C3AED] rounded-full`} />
            </div>
          </div>
        ))}
      </motion.div>

      {/* Weekly progress */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25 }}
        className="p-4 rounded-xl bg-gradient-to-r from-[#EFF6FF] to-[#F5F3FF] border border-[#BFDBFE]"
      >
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-semibold text-[#1E293B]">This Week&apos;s Progress</span>
          <span className="text-xs font-medium text-[#2563EB]">4 of 5 challenges</span>
        </div>
        <div className="h-3 bg-white rounded-full overflow-hidden border border-[#E2E8F0]">
          <motion.div
            initial={{ width: '0%' }}
            animate={{ width: '80%' }}
            transition={{ duration: 1, delay: 0.4, ease: 'easeOut' }}
            className="h-full bg-gradient-to-r from-[#2563EB] to-[#7C3AED] rounded-full"
          />
        </div>
      </motion.div>
    </div>
  );
}

/* ── LEARNING SCREEN ── */
function LearningScreen() {
  return (
    <div className="space-y-4">
      <motion.h3
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
        className="text-lg font-bold text-[#1E293B]"
      >
        My Learning Modules
      </motion.h3>

      <div className="grid grid-cols-2 gap-3">
        {[
          { subject: 'Core Mathematics', progress: 72, color: '#2563EB', bg: 'bg-[#EFF6FF]', border: 'border-[#BFDBFE]' },
          { subject: 'Integrated Science', progress: 58, color: '#7C3AED', bg: 'bg-[#F5F3FF]', border: 'border-[#DDD6FE]' },
          { subject: 'English Language', progress: 85, color: '#D97706', bg: 'bg-[#FFFBEB]', border: 'border-[#FDE68A]' },
          { subject: 'Social Studies', progress: 41, color: '#2563EB', bg: 'bg-[#EFF6FF]', border: 'border-[#BFDBFE]' },
        ].map((module, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + i * 0.08 }}
            className={`p-3.5 rounded-xl ${module.bg} ${module.border} border`}
          >
            <div className="text-sm font-semibold text-[#1E293B] mb-2">{module.subject}</div>
            <div className="h-2 bg-white rounded-full overflow-hidden border border-[#E2E8F0]">
              <motion.div
                initial={{ width: '0%' }}
                animate={{ width: `${module.progress}%` }}
                transition={{ duration: 1, delay: 0.3 + i * 0.1, ease: 'easeOut' }}
                className="h-full rounded-full"
                style={{ backgroundColor: module.color }}
              />
            </div>
            <div className="flex justify-between mt-1.5">
              <span className="text-[10px] text-[#64748B]">Progress</span>
              <span className="text-[10px] font-semibold" style={{ color: module.color }}>{module.progress}%</span>
            </div>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="flex items-center gap-2 text-xs text-[#2563EB] font-medium pt-1"
      >
        <span className="w-1.5 h-1.5 rounded-full bg-[#2563EB]" />
        Next lesson: Algebra Fundamentals &mdash; 12 min read
      </motion.div>
    </div>
  );
}

/* ── CHALLENGES SCREEN ── */
function ChallengesScreen() {
  return (
    <div className="space-y-4">
      <motion.h3
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
        className="text-lg font-bold text-[#1E293B]"
      >
        Challenge Arena
      </motion.h3>

      <div className="space-y-3">
        {[
          { title: 'Scientific Thinking', desc: 'Analyze data and draw conclusions', difficulty: 'Medium', questions: '12 questions', gradient: 'from-[#2563EB] to-[#3B82F6]', badge: 'bg-[#DBEAFE] text-[#2563EB]' },
          { title: 'Logical Puzzles', desc: 'Solve pattern recognition problems', difficulty: 'Hard', questions: '8 questions', gradient: 'from-[#7C3AED] to-[#8B5CF6]', badge: 'bg-[#EDE9FE] text-[#7C3AED]' },
          { title: 'Verbal Reasoning', desc: 'Comprehension and critical thinking', difficulty: 'Easy', questions: '15 questions', gradient: 'from-[#F59E0B] to-[#FBBF24]', badge: 'bg-[#FEF3C7] text-[#D97706]' },
        ].map((challenge, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 + i * 0.1 }}
            className="flex items-center gap-4 p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] hover:border-[#BFDBFE] transition-colors"
          >
            <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${challenge.gradient} flex items-center justify-center flex-shrink-0`}>
              <span className="text-white font-bold text-sm">{i + 1}</span>
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-semibold text-[#1E293B]">{challenge.title}</div>
              <div className="text-xs text-[#64748B]">{challenge.desc}</div>
            </div>
            <div className="text-right flex-shrink-0">
              <div className={`px-2 py-0.5 rounded-md text-xs font-semibold ${challenge.badge}`}>
                {challenge.difficulty}
              </div>
              <div className="text-[10px] text-[#94A3B8] mt-0.5">{challenge.questions}</div>
            </div>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="flex items-center justify-between text-xs pt-1"
      >
        <span className="text-[#64748B]">500 XP available today</span>
        <span className="text-[#2563EB] font-medium">View all &rarr;</span>
      </motion.div>
    </div>
  );
}

/* ── RECOMMENDATIONS SCREEN ── */
function RecommendationsScreen() {
  return (
    <div className="space-y-4">
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
        className="flex items-center justify-between"
      >
        <h3 className="text-lg font-bold text-[#1E293B]">Your Matches</h3>
        <span className="text-xs font-medium text-[#2563EB]">Based on your profile</span>
      </motion.div>

      <div className="space-y-3">
        {[
          { name: 'Medicine & Surgery', match: 94, uni: 'University of Ghana', gradient: 'from-[#2563EB] to-[#3B82F6]' },
          { name: 'Computer Engineering', match: 87, uni: 'Kwame Nkrumah Univ.', gradient: 'from-[#7C3AED] to-[#8B5CF6]' },
          { name: 'Biochemistry', match: 81, uni: 'Univ. of Cape Coast', gradient: 'from-[#F59E0B] to-[#FBBF24]' },
          { name: 'Business Administration', match: 76, uni: 'KNUST', gradient: 'from-[#2563EB] to-[#7C3AED]' },
        ].map((program, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 + i * 0.08 }}
            className="flex items-center gap-4 p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]"
          >
            {/* Match percentage circle */}
            <div className="relative w-12 h-12 flex-shrink-0">
              <svg className="w-12 h-12" viewBox="0 0 48 48">
                <circle cx="24" cy="24" r="20" fill="none" stroke="#E2E8F0" strokeWidth="3" />
                <motion.circle
                  cx="24" cy="24" r="20"
                  fill="none"
                  stroke={program.match >= 90 ? '#2563EB' : program.match >= 80 ? '#7C3AED' : '#F59E0B'}
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeDasharray={`${2 * Math.PI * 20}`}
                  initial={{ strokeDashoffset: 2 * Math.PI * 20 }}
                  animate={{ strokeDashoffset: 2 * Math.PI * 20 * (1 - program.match / 100) }}
                  transition={{ duration: 1.2, delay: 0.3 + i * 0.1, ease: 'easeOut' }}
                  transform="rotate(-90, 24, 24)"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xs font-bold text-[#1E293B]">{program.match}%</span>
              </div>
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-semibold text-[#1E293B]">{program.name}</div>
              <div className="text-xs text-[#64748B]">{program.uni}</div>
            </div>
            <div className={`px-2.5 py-1 rounded-lg bg-gradient-to-br ${program.gradient} text-white text-xs font-semibold flex-shrink-0`}>
              Match
            </div>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.45 }}
        className="text-center pt-1"
      >
        <span className="text-xs text-[#64748B]">
          Explore <span className="text-[#2563EB] font-medium">12 more programs</span> tailored to your strengths
        </span>
      </motion.div>
    </div>
  );
}
