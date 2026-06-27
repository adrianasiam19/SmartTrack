'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import Sidebar from '../components/Sidebar';
import BottomNav from '../components/BottomNav';
import AppLayout from '../components/AppLayout';
import ChallengeCard from '../components/ChallengeCard';
import { getAccessToken, getStoredUser, getCurrentUser, type UserProfile } from '../lib/authApi';
import { ALL_CHALLENGE_CATEGORIES, STARTER_ARENA, type ChallengeCategory } from '../lib/challengesApi';
import { isCategoryAppropriateForLevel, getLearningStage } from '../lib/adaptiveEngine';

export default function ChallengesHub() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        if (!getAccessToken()) { router.push('/login'); return; }
        const cached = getStoredUser(); if (cached) setUser(cached);
        const fresh = await getCurrentUser(); setUser(fresh);
      } catch { router.push('/login'); }
      finally { setLoading(false); }
    };
    load();
  }, [router]);

  const handlePlay = (category: ChallengeCategory) => {
    if (category.id === 'starter-arena') router.push('/challenges/arena?mode=placement');
    else router.push(`/challenges/arena?domain=${category.domain}&category=${category.id}`);
  };

  const shsLevel = user?.shs_level || null;
  const stage = getLearningStage(user?.programme || null, shsLevel);
  const allCategories = ALL_CHALLENGE_CATEGORIES.filter((cat) => isCategoryAppropriateForLevel(cat, shsLevel));

  if (loading) return (
    <AppLayout><div className="flex items-center justify-center min-h-screen">
      <div className="w-8 h-8 border-2 border-[#4F46E5] border-t-transparent rounded-full animate-spin" /></div></AppLayout>
  );

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-20">
          <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-8 pb-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-xl font-bold text-[#1E293B]">Challenge Hub</h1>
                <p className="text-sm text-gray-500">{user?.programme || 'SHS Student'} · {user?.shs_level || 'Explore challenges'}{stage && ` · ${stage.title}`}</p>
              </div>
              {user && (
                <div className="flex items-center gap-3">
                  <div className="text-sm font-semibold text-[#2563EB]">{user.xp.toLocaleString()} XP</div>
                  <div className="text-sm font-semibold text-[#D97706]">{user.rank}</div>
                </div>
              )}
            </div>

            <section className="mb-10">
              <h2 className="text-lg font-bold text-[#1E293B] mb-1">Your Discovery Journey</h2>
              <p className="text-sm text-gray-500 mb-4">Let Atlas get to know you — then unlock the competitive arenas!</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <ChallengeCard category={STARTER_ARENA} onPlay={handlePlay} index={0} isNew isStarter />
              </div>
            </section>

            {allCategories.length > 0 && (
              <section>
                <h2 className="text-lg font-bold text-[#1E293B] mb-4">
                  All Challenge Arenas
                  {shsLevel && <span className="px-2.5 py-0.5 text-[10px] font-bold bg-[#EEF2FF] text-[#4F46E5] rounded-full border border-[#C7D2FE] ml-2">{shsLevel}</span>}
                </h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {allCategories.map((cat, idx) => <ChallengeCard key={cat.id} category={cat} onPlay={handlePlay} index={idx + 1} />)}
                </div>
              </section>
            )}

            <div className="text-center py-6 border-t border-gray-100 mt-8">
              <p className="text-gray-500 text-sm">
                Complete challenges to earn XP and climb the{' '}
                <button onClick={() => router.push('/challenges/leaderboard')} className="text-[#4F46E5] hover:text-[#4338CA] font-medium underline underline-offset-2">leaderboard</button>.
              </p>
            </div>
          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}
