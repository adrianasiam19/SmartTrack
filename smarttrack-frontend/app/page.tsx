'use client';

import Link from 'next/link';
import { AnimatePresence, motion } from 'framer-motion';
import { useState, useCallback } from 'react';
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
    <div className="min-h-screen bg-[#F8FAFC] overflow-hidden">
      {/* ── SPLIT-SCREEN HERO ── */}
      <section className="flex flex-col lg:flex-row h-screen">
        {/* ── LEFT PANEL (60%) - HERO IMAGE ── */}
        <div className="relative lg:w-[60%] h-[50vh] lg:h-screen overflow-hidden">
          {/* Background image - Academic campus building */}
          <div
            className="absolute inset-0 bg-cover bg-center bg-no-repeat"
            style={{
              backgroundImage: 'url("https://images.pexels.com/photos/8926544/pexels-photo-8926544.jpeg?auto=compress&cs=tinysrgb&w=1200&h=900&dpr=1")',
            }}
          />
          {/* Sophisticated gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-r from-[#1E3A8A]/85 via-[#2563EB]/70 to-[#7C3AED]/50" />

          {/* Subtle pattern overlay */}
          <div
            className="absolute inset-0 opacity-[0.04]"
            style={{
              backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.8) 1px, transparent 1px)',
              backgroundSize: '32px 32px',
            }}
          />

          {/* Content overlay */}
          <div className="relative z-10 flex flex-col justify-between h-full p-8 sm:p-12 lg:p-16 xl:p-20">
            {/* Logo */}
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="flex items-center gap-3"
            >
              <div className="w-10 h-10 bg-white/20 backdrop-blur-md rounded-xl flex items-center justify-center border border-white/20 shadow-lg">
                <span className="text-white font-bold text-lg">A</span>
              </div>
              <span className="text-2xl font-bold text-white tracking-tight">Atlas</span>
            </motion.div>

            {/* Center messaging */}
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
                className="text-base sm:text-lg text-[#BFDBFE] leading-relaxed max-w-lg font-light"
              >
                An intelligent platform for Ghanaian SHS students to discover their strengths,
                improve their skills, and explore academic paths that match their potential.
              </motion.p>
            </div>

            {/* Bottom spacer */}
            <div />
          </div>
        </div>

        {/* ── RIGHT PANEL (40%) - SIGN IN / CREATE ACCOUNT ── */}
        <div className="lg:w-[40%] flex items-center justify-center p-6 sm:p-8 lg:p-12 xl:p-16 bg-[#F8FAFC]">
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
    </div>
  );
}
