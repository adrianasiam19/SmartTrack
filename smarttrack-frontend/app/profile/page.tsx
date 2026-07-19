'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '../components/Sidebar';
import BottomNav from '../components/BottomNav';
import AppLayout from '../components/AppLayout';
import { getCurrentUser, getAccessToken, getAuthHeaders, getStoredUser, phaseLabelFromLevel, UserProfile } from '../lib/authApi';
import { motion } from 'framer-motion';

interface ChallengeScore { score_percentage: number; performance_level: string; total_questions: number; correct_answers: number; }

export default function Profile() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [challengeScore, setChallengeScore] = useState<ChallengeScore | null>(null);
  const [loading, setLoading] = useState(true);

  const getInitials = (name: string | undefined) => name?.split(' ').filter(Boolean).map((n) => n[0]).join('').toUpperCase().slice(0, 2) || '?';

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        if (!getAccessToken()) { router.push('/login'); return; }
        const cached = getStoredUser(); if (cached) setUser(cached);
        const backendUser = await getCurrentUser(); setUser(backendUser);
        const statusRes = await fetch('http://localhost:8000/api/v1/challenges/completion-status', { method: 'GET', headers: getAuthHeaders() });
        if (statusRes.ok) {
          const statusData = await statusRes.json();
          if (statusData.is_fully_completed) {
            const scoreRes = await fetch('http://localhost:8000/api/v1/challenges/score', { method: 'GET', headers: getAuthHeaders() });
            if (scoreRes.ok) setChallengeScore(await scoreRes.json());
          }
        }
      } catch { /* ignore */ }
      finally { setLoading(false); }
    };
    load();
  }, [router]);

  const getMemberSince = (dateString: string) => {
    try { return new Date(dateString).toLocaleDateString('en-US', { month: 'long', year: 'numeric' }); } catch { return 'Recently'; }
  };

  if (loading) return (
    <AppLayout>
      <div className="flex min-h-screen"><Sidebar /><main className="flex-1 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-[#4F46E5] border-t-transparent rounded-full animate-spin" /></main></div>
    </AppLayout>
  );

  if (!user) return (
    <AppLayout>
      <div className="flex min-h-screen"><Sidebar /><main className="flex-1 flex items-center justify-center">
        <p className="text-gray-500">Please log in to view your profile</p></main></div>
    </AppLayout>
  );

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-20">
          <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-8 pb-28">
            <div className="mb-6">
              <h1 className="text-xl font-bold text-[#1E293B]">Profile</h1>
              <p className="text-sm text-gray-500">Your account and challenge information</p>
            </div>

            <div className="space-y-6">
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                className="bg-white border border-gray-200 rounded-xl p-6">
                <div className="flex items-start gap-5 mb-6">
                  <div className="w-16 h-16 bg-gradient-to-br from-[#4F46E5] to-[#D97706] rounded-xl flex items-center justify-center text-white text-xl font-bold shadow-sm">
                    {getInitials(user.full_name)}
                  </div>
                  <div className="flex-1">
                    <h2 className="text-xl font-semibold text-[#1E293B]">{user.full_name}</h2>
                    <p className="text-sm text-gray-500 mb-2">{user.email}</p>
                    <p className="text-xs text-gray-400">Member since {getMemberSince(user.created_at || '')}</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
                  <div className="bg-[#EEF2FF] rounded-xl p-4">
                    <p className="text-xs text-gray-500 mb-1">Total XP</p>
                    <p className="text-2xl font-bold text-[#4F46E5]">{user.xp ?? 0}</p>
                  </div>
                  <div className="bg-[#FFFBEB] rounded-xl p-4">
                    <p className="text-xs text-gray-500 mb-1">Rank</p>
                    <p className="text-2xl font-bold text-[#D97706]">{user.rank ?? 'Beginner'}</p>
                  </div>
                  <div className="bg-[#FFF1F2] rounded-xl p-4">
                    <p className="text-xs text-gray-500 mb-1">Streak</p>
                    <p className="text-2xl font-bold text-[#F43F5E]">{(user.streak ?? 0)} {(user.streak ?? 0) === 1 ? 'day' : 'days'}</p>
                  </div>
                </div>

                <div className="grid sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Full Name</label>
                    <input type="text" value={user.full_name || ''} readOnly className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-[#1E293B] text-sm" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Email</label>
                    <input type="email" value={user.email || ''} readOnly className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-[#1E293B] text-sm" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Programme</label>
                    <div className="px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-sm text-[#1E293B]">
                      <span>{user.programme || 'Not set'}</span>
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Phase</label>
                    <div className="px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-sm text-[#1E293B]">
                      <span>{phaseLabelFromLevel(user.shs_level)}</span>
                    </div>
                  </div>
                </div>
              </motion.div>

              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
                className="bg-white border border-gray-200 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-[#1E293B] mb-6">Challenge History</h2>

                {!challengeScore ? (
                  <div className="py-8 text-center">
                    <p className="text-gray-500 text-sm mb-4">No completed challenges yet.</p>
                    <button onClick={() => router.push('/challenges')}
                      className="px-4 py-2 bg-[#4F46E5] text-white text-sm font-medium rounded-lg hover:bg-[#4338CA] transition-colors">
                      Start Your First Challenge
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 bg-[#EEF2FF] rounded-xl border border-[#C7D2FE]">
                      <div>
                        <h3 className="font-semibold text-[#1E293B] text-sm">Completed Challenge</h3>
                        <p className="text-xs text-gray-500 mt-1">Completed recently</p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-[#4F46E5]">{challengeScore.score_percentage}%</div>
                        <p className="text-xs text-gray-500">{challengeScore.performance_level}</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-3">
                      <div className="text-center p-3 bg-gray-50 rounded-lg">
                        <p className="text-gray-500 text-xs mb-1">Total</p>
                        <p className="text-lg font-semibold text-[#1E293B]">{challengeScore.total_questions}</p>
                      </div>
                      <div className="text-center p-3 bg-gray-50 rounded-lg">
                        <p className="text-gray-500 text-xs mb-1">Correct</p>
                        <p className="text-lg font-semibold text-[#4F46E5]">{challengeScore.correct_answers}</p>
                      </div>
                      <div className="text-center p-3 bg-gray-50 rounded-lg">
                        <p className="text-gray-500 text-xs mb-1">Performance</p>
                        <p className="text-lg font-semibold text-[#1E293B]">{challengeScore.performance_level}</p>
                      </div>
                    </div>
                  </div>
                )}
              </motion.div>
            </div>
          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}
