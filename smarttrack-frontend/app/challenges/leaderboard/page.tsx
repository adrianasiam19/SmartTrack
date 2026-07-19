'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import Sidebar from '../../components/Sidebar';
import BottomNav from '../../components/BottomNav';
import AppLayout from '../../components/AppLayout';
import { getAccessToken, getCurrentUser, getStoredUser, type UserProfile } from '../../lib/authApi';

export default function LeaderboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [entries, setEntries] = useState<any[]>([]);
  const [fetchError, setFetchError] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        if (!getAccessToken()) { router.push('/login'); return; }
        const cached = getStoredUser(); if (cached) setUser(cached);
        const fresh = await getCurrentUser(); setUser(fresh);

        // Try to fetch real leaderboard data from the API
        const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
        const res = await fetch(`${API_BASE}/challenges/leaderboard`, {
          headers: {
            Authorization: `Bearer ${getAccessToken()}`,
            'Content-Type': 'application/json',
          },
        });
        if (res.ok) {
          const data = await res.json();
          setEntries(Array.isArray(data) ? data : data.entries || []);
        } else {
          setFetchError(true);
        }
      } catch {
        setFetchError(true);
      }
      finally { setLoading(false); }
    };
    load();
  }, [router]);

  const isEmpty = entries.length === 0;

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-20">
          <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-8 pb-8">
            <div className="mb-6">
              <h1 className="text-xl font-bold text-[#1E293B]">Leaderboard</h1>
              <p className="text-xs text-gray-500">Real rankings from actual student activity</p>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-20">
                <div className="w-8 h-8 border-2 border-[#2563EB] border-t-transparent rounded-full animate-spin" />
              </div>
            ) : isEmpty ? (
              <div className="bg-white border border-[#E2E8F0] rounded-xl p-12 text-center">
                <h2 className="text-lg font-bold text-[#1E293B] mb-2">No Rankings Yet</h2>
                <p className="text-sm text-[#64748B] max-w-md mx-auto">
                  No rankings available yet. Complete challenges to become one of the first students on the leaderboard.
                </p>
                <button
                  onClick={() => router.push('/challenges')}
                  className="mt-6 px-6 py-3 bg-[#2563EB] text-white font-semibold rounded-xl hover:bg-[#1D4ED8] transition-all"
                >
                  Start a Challenge
                </button>
              </div>
            ) : (
              <div className="bg-white border border-[#E2E8F0] rounded-xl overflow-hidden">
                <div className="divide-y divide-gray-100">
                  <div className="flex items-center gap-4 px-5 py-3 text-xs text-gray-400 font-medium uppercase tracking-wider">
                    <span className="w-8 text-center">Rank</span>
                    <span className="flex-1">Player</span>
                    <span className="w-20 text-right">XP</span>
                  </div>

                  {entries.map((entry: any, idx: number) => {
                    const name = entry.user_name || entry.full_name || `Student ${idx + 1}`;
                    const xp = entry.xp || 0;
                    const rank = entry.rank || idx + 1;
                    const isMe = user && (entry.user_id === user.id || entry.is_me);
                    return (
                      <div key={rank}
                        className={`flex items-center gap-4 px-5 py-3.5 transition-colors ${
                          isMe ? 'bg-[#EEF2FF]' : 'hover:bg-gray-50'
                        }`}
                      >
                        <div className="w-8 text-center">
                          <span className={`text-sm font-bold ${rank <= 3 ? 'text-[#2563EB]' : 'text-gray-400'}`}>
                            #{rank}
                          </span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <h4 className="text-sm font-medium text-[#1E293B] truncate">{name}</h4>
                            {isMe && (
                              <span className="px-1.5 py-0.5 text-[9px] font-bold bg-[#2563EB] text-white rounded uppercase">You</span>
                            )}
                          </div>
                        </div>
                        <div className="w-20 text-right">
                          <span className="text-sm font-semibold text-[#1E293B]">{xp.toLocaleString()}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}
