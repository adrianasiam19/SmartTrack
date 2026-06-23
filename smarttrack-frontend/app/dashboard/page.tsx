'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import Sidebar from '../components/Sidebar';
import BottomNav from '../components/BottomNav';
import AppLayout from '../components/AppLayout';
import XpGauge from '../components/XpGauge';
import {
  getCurrentUser, getAccessToken, getStoredUser, UserProfile,
} from '../lib/authApi';

interface ActionCard {
  title: string;
  description: string;
  href: string;
  buttonLabel: string;
  hasFireIcon?: boolean;
}

const ACTION_CARDS: ActionCard[] = [
  {
    title: 'Daily Streak',
    description: 'Maintain your learning streak and improve your recommendations.',
    href: '/challenges/daily-streak',
    buttonLabel: 'Continue',
    hasFireIcon: true,
  },
  {
    title: 'Programs',
    description: 'Discover university programs that match your strengths.',
    href: '/recommendations',
    buttonLabel: 'View Programs',
  },
  {
    title: 'Upload Academic Results',
    description: 'Add your WASSCE results for accurate recommendations.',
    href: '/recommendations',
    buttonLabel: 'Upload',
  },
  {
    title: 'Recommendation Progress',
    description: 'Track your progress toward personalised programme recommendations.',
    href: '/recommendations',
    buttonLabel: 'View Progress',
  },
];

const CARD_COLORS: Record<string, string> = {
  'Daily Streak': 'border-l-[#F59E0B]',
  'Programs': 'border-l-[#7C3AED]',
  'Upload Academic Results': 'border-l-[#059669]',
  'Recommendation Progress': 'border-l-[#4F46E5]',
};

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const token = getAccessToken();
        if (!token) { router.push('/login'); return; }
        const cached = getStoredUser();
        if (cached) setUser(cached);
        const fresh = await getCurrentUser();
        setUser(fresh);
      } catch { router.push('/login'); }
      finally { setLoading(false); }
    };
    loadData();
  }, [router]);

  if (loading && !user) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="w-10 h-10 border-4 border-[#4F46E5] border-t-transparent rounded-full animate-spin" />
        </div>
      </AppLayout>
    );
  }

  if (!user) return null;

  const firstName = user.full_name?.split(' ')[0] || 'there';

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-24">
          <main className="flex-1 max-w-4xl mx-auto px-6 lg:px-10 pt-24 lg:pt-10 pb-10">
            {/* Header */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-10"
            >
              <h1 className="text-3xl sm:text-4xl font-bold text-[#1E293B]">
                Welcome back,{' '}
                <span className="text-[#4F46E5]">{firstName}</span>
              </h1>
              <p className="text-base text-[#475569] mt-2">
                {user.programme || 'SHS Student'}
                {user.shs_level ? ` · ${user.shs_level}` : ''}
              </p>
            </motion.div>

            {/* XP Gauge */}
            <div className="mb-10">
              <XpGauge
                xp={user.xp}
                rank={user.rank}
                streak={user.streak}
              />
            </div>

            {/* Primary Actions */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
            >
              <h2 className="text-lg font-semibold text-[#1E293B] mb-5">
                What would you like to do?
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {ACTION_CARDS.map((card, idx) => (
                  <motion.button
                    key={card.title}
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 + idx * 0.05 }}
                    whileHover={{ y: -2 }}
                    whileTap={{ scale: 0.99 }}
                    onClick={() => router.push(card.href)}
                    className={`text-left bg-white border border-[#E2E8F0] border-l-4 ${CARD_COLORS[card.title]} rounded-xl p-5 hover:shadow-md hover:border-[#CBD5E1] transition-all duration-200`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          {card.hasFireIcon && (
                            <svg className="w-5 h-5 text-[#F59E0B] flex-shrink-0" viewBox="0 0 24 24" fill="currentColor">
                              <path d="M12 23c-3.866 0-7-3.134-7-7 0-3.866 3-8 7-13 4 5 7 9.134 7 13 0 3.866-3.134 7-7 7z" />
                            </svg>
                          )}
                          <h3 className="text-base font-semibold text-[#1E293B]">{card.title}</h3>
                        </div>
                        <p className="text-sm text-[#475569] leading-relaxed">{card.description}</p>
                      </div>
                      <div className="flex-shrink-0 ml-4">
                        <span className="inline-block px-4 py-2 text-xs font-semibold text-[#4F46E5] bg-[#EEF2FF] rounded-lg hover:bg-[#E0E7FF] transition-colors">
                          {card.buttonLabel}
                        </span>
                      </div>
                    </div>
                  </motion.button>
                ))}
              </div>
            </motion.div>
          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}
