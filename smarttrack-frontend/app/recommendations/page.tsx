'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import Sidebar from '../components/Sidebar';
import BottomNav from '../components/BottomNav';
import AppLayout from '../components/AppLayout';
import { getAccessToken, getStoredUser, getCurrentUser, type UserProfile } from '../lib/authApi';

interface ReadinessItem { id: string; label: string; completed: boolean; }
interface ArenaStrength { name: string; level: 'Strong' | 'Moderate' | 'Developing' | 'Not Started'; description: string; }

function deriveArenaStrengths(user: UserProfile | null): ArenaStrength[] {
  if (!user) return [];
  const xp = user.xp || 0;
  const isScience = user.programme === 'General Science';
  const lvl = (s: number, m: number, d: number): ArenaStrength['level'] =>
    xp >= s ? 'Strong' : xp >= m ? 'Moderate' : xp >= d ? 'Developing' : 'Not Started';
  return [
    { name: 'Logic & Reasoning', level: lvl(200, 100, 30), description: 'Pattern recognition, deductive reasoning, and analytical problem-solving.' },
    { name: 'Scientific Thinking', level: isScience && xp >= 100 ? 'Moderate' : xp >= 200 ? 'Moderate' : 'Developing', description: 'Hypothesis formation, experimental design, and evidence-based analysis.' },
    { name: 'Quantitative Reasoning', level: lvl(200, 100, 30), description: 'Numerical problem-solving, percentages, ratios, and data analysis.' },
    { name: 'Communication', level: !isScience && xp >= 100 ? 'Moderate' : 'Developing', description: 'Reading comprehension, argument analysis, and clear expression of ideas.' },
  ];
}

function strengthColor(level: ArenaStrength['level']): string {
  const colors: Record<string, string> = {
    Strong: 'text-[#4F46E5] border-[#C7D2FE] bg-[#EEF2FF]',
    Moderate: 'text-[#D97706] border-[#FDE68A] bg-[#FFFBEB]',
    Developing: 'text-[#F43F5E] border-[#FFE4E6] bg-[#FFF1F2]',
    'Not Started': 'text-gray-400 border-gray-200 bg-gray-50',
  };
  return colors[level] || colors['Not Started'];
}

export default function RecommendationsPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [academicCompleted, setAcademicCompleted] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        if (!getAccessToken()) { router.push('/login'); return; }
        const cached = getStoredUser(); if (cached) setUser(cached);
        const fresh = await getCurrentUser(); setUser(fresh);
        setAcademicCompleted(localStorage.getItem('atlas_academic_data') === 'true');
      } catch { router.push('/login'); }
      finally { setLoading(false); }
    };
    load();
  }, [router]);

  const hasXP = (user?.xp || 0) > 0;
  const readinessItems: ReadinessItem[] = [
    { id: 'starter-arena', label: 'Starter Arena', completed: hasXP },
    { id: 'logic-arena', label: 'Logic Arena', completed: hasXP },
    { id: 'scientific-thinking', label: 'Scientific Thinking', completed: hasXP },
    { id: 'quantitative-sprint', label: 'Quantitative Sprint', completed: hasXP },
    { id: 'psychometric', label: 'Psychometric Profile', completed: false },
    { id: 'academic', label: 'Academic Results', completed: academicCompleted },
  ];
  const arenaStrengths = deriveArenaStrengths(user);
  const completedCount = readinessItems.filter((i) => i.completed).length;
  const confidence = Math.min(100, hasXP ? 40 : 10 + (academicCompleted ? 25 : 0));

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
                <h1 className="text-xl font-bold text-[#1E293B]">Programme Recommendations</h1>
                <p className="text-sm text-gray-500">{user?.programme || 'SHS Student'} · {user?.shs_level || 'Discover your path'}</p>
              </div>
              <div className="text-sm font-semibold text-[#4F46E5]">{user?.xp?.toLocaleString() || 0} XP</div>
            </div>

            <div className="space-y-6">
              <div className="bg-white border border-gray-200 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-[#1E293B] mb-1">Recommendation Readiness</h2>
                <p className="text-sm text-gray-500 mb-6">Complete challenges and upload academic results to unlock accurate recommendations.</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-6">
                  {readinessItems.map((item) => (
                    <div key={item.id} className={`flex items-center justify-between px-4 py-3 rounded-lg border transition-all ${item.completed ? 'bg-[#EEF2FF] border-[#C7D2FE]' : 'bg-white border-gray-200'}`}>
                      <span className={`text-sm font-medium ${item.completed ? 'text-[#4F46E5]' : 'text-gray-500'}`}>{item.label}</span>
                      <span className={`text-xs font-bold ${item.completed ? 'text-[#4F46E5]' : 'text-gray-300'}`}>{item.completed ? 'Done' : 'Pending'}</span>
                    </div>
                  ))}
                </div>
                <div className="bg-gray-50 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-[#1E293B]">Recommendation Confidence</span>
                    <span className="text-lg font-bold text-[#4F46E5]">{confidence}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                    <div className="h-2 rounded-full bg-[#4F46E5] transition-all duration-1000" style={{ width: `${confidence}%` }} />
                  </div>
                  <span className="text-xs text-gray-500">{completedCount} of {readinessItems.length} milestones complete</span>
                </div>
              </div>

              <div>
                <h2 className="text-lg font-semibold text-[#1E293B] mb-4">Cognitive Profile</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {arenaStrengths.map((strength) => (
                    <div key={strength.name} className="bg-white border border-gray-200 rounded-xl p-5">
                      <div className="flex items-start gap-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-1">
                            <h3 className="font-semibold text-[#1E293B] text-sm">{strength.name}</h3>
                            <span className={`inline-flex px-2 py-0.5 text-[10px] font-bold rounded-full border ${strengthColor(strength.level)}`}>{strength.level}</span>
                          </div>
                          <p className="text-xs text-gray-500">{strength.description}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {!academicCompleted && (
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-8 text-center">
                  <h2 className="text-xl font-bold text-[#1E293B] mb-2">Your profile is still being built.</h2>
                  <p className="text-gray-500 max-w-lg mx-auto mb-6 text-sm">Complete more challenges and upload your academic results to unlock accurate programme recommendations.</p>
                  <div className="flex flex-col sm:flex-row gap-3 justify-center">
                    <button onClick={() => router.push('/challenges')}
                      className="px-5 py-2.5 bg-[#4F46E5] text-white font-medium rounded-lg hover:bg-[#4338CA] transition-colors text-sm">
                      Complete Challenges
                    </button>
                    <button onClick={() => { localStorage.setItem('atlas_academic_data', 'true'); setAcademicCompleted(true); }}
                      className="px-5 py-2.5 border border-gray-200 text-gray-600 font-medium rounded-lg hover:bg-gray-50 transition-colors text-sm">
                      Upload WASSCE Results
                    </button>
                  </div>
                </div>
              )}

              {academicCompleted && (
                <div className="bg-white border border-gray-200 rounded-xl p-8 text-center">
                  <h3 className="text-lg font-semibold text-[#1E293B] mb-2">Recommendations are being generated...</h3>
                  <p className="text-gray-500 text-sm mb-6">Your cognitive profile and academic data are being processed.</p>
                  <button onClick={() => router.push('/challenges')}
                    className="px-5 py-2.5 bg-[#4F46E5] text-white font-medium rounded-lg hover:bg-[#4338CA] transition-colors text-sm">
                    Continue Building Your Profile
                  </button>
                </div>
              )}
            </div>
          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}
