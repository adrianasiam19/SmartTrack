'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import Sidebar from '../../components/Sidebar';
import BottomNav from '../../components/BottomNav';
import AppLayout from '../../components/AppLayout';

interface LeaderboardEntry {
  rank: number;
  user_name: string;
  xp: number;
  streak: number;
  school: string;
  programme: string;
  is_me?: boolean;
}

const LEAGUES = [
  { id: 'Overall', label: 'Overall' },
  { id: 'Science', label: 'Science' },
  { id: 'Arts', label: 'Arts' },
  { id: 'Logic', label: 'Logic' },
  { id: 'School', label: 'School' },
];

const MOCK_ENTRIES: LeaderboardEntry[] = [
  { rank: 1, user_name: 'Olawale J.', xp: 4985, streak: 45, school: 'Kings College', programme: 'General Science' },
  { rank: 2, user_name: 'Chidi E.', xp: 4962, streak: 38, school: 'Vivian Fowler', programme: 'General Arts' },
  { rank: 3, user_name: 'Amina B.', xp: 4945, streak: 32, school: 'Lekki British School', programme: 'General Science' },
  { rank: 4, user_name: 'You (Adrian)', xp: 4920, streak: 28, school: 'Accra Academy', programme: 'General Science', is_me: true },
  { rank: 5, user_name: 'Tobi A.', xp: 4890, streak: 21, school: 'Corona Sec', programme: 'General Arts' },
  { rank: 6, user_name: 'Zainab M.', xp: 4875, streak: 19, school: 'Grange School', programme: 'General Science' },
  { rank: 7, user_name: 'Emeka O.', xp: 4850, streak: 15, school: 'Igbobi College', programme: 'General Arts' },
  { rank: 8, user_name: 'Nkechi F.', xp: 4820, streak: 14, school: 'Queens College', programme: 'General Science' },
  { rank: 9, user_name: 'Kofi A.', xp: 4790, streak: 12, school: 'Presbyterian Boys', programme: 'General Arts' },
  { rank: 10, user_name: 'Adwoa S.', xp: 4750, streak: 10, school: 'Wesley Girls', programme: 'General Science' },
];

export default function LeaderboardPage() {
  const router = useRouter();
  const [selectedLeague, setSelectedLeague] = useState('Overall');
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const timer = setTimeout(() => { setEntries(MOCK_ENTRIES); setLoading(false); }, 800);
    return () => clearTimeout(timer);
  }, [selectedLeague]);

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-20">
          <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-8 pb-8">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <button onClick={() => router.push('/challenges')}
                  className="flex items-center gap-2 text-gray-400 hover:text-gray-600 transition-colors">
                  <span className="text-sm font-medium hidden sm:inline">Back</span>
                </button>
                <div>
                  <h1 className="text-xl font-bold text-[#1E293B]">Leaderboard</h1>
                  <p className="text-xs text-gray-500">Compete and climb the ranks</p>
                </div>
              </div>
              <div className="text-xs text-gray-500">
                Season 1
              </div>
            </div>

            <div className="flex gap-2 overflow-x-auto pb-4 mb-6 scrollbar-hide">
              {LEAGUES.map((league) => (
                <button
                  key={league.id}
                  onClick={() => setSelectedLeague(league.id)}
                  className={`px-4 py-2 rounded-lg border transition-all whitespace-nowrap text-sm ${
                    selectedLeague === league.id
                      ? 'bg-[#4F46E5] border-[#4F46E5] text-white font-medium'
                      : 'border-gray-200 text-gray-500 hover:border-gray-300 hover:text-gray-700 bg-white'
                  }`}
                >
                  {league.label}
                </button>
              ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              {entries.slice(0, 3).map((entry, idx) => {
                const isFirst = idx === 0;
                return (
                  <motion.div
                    key={entry.user_name}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    className={`relative p-5 rounded-xl border text-center ${
                      isFirst
                        ? 'bg-[#4F46E5] border-[#4F46E5] text-white'
                        : 'bg-white border-gray-200'
                    }`}
                  >
                    <div className="text-sm font-bold text-gray-400 mb-2">#{['1st', '2nd', '3rd'][idx]}</div>
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg mx-auto mb-2 ${
                      isFirst ? 'bg-white/20 text-white' : 'bg-gray-100 text-gray-600'
                    }`}>
                      {entry.user_name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                    </div>
                    <h3 className={`font-semibold ${isFirst ? 'text-white' : 'text-[#1E293B]'}`}>{entry.user_name}</h3>
                    <p className={`text-xs ${isFirst ? 'text-indigo-200' : 'text-gray-500'}`}>{entry.school}</p>
                    <div className="mt-2">
                      <p className={`text-xl font-bold ${isFirst ? 'text-white' : 'text-[#4F46E5]'}`}>{entry.xp.toLocaleString()}</p>
                      <p className={`text-[10px] uppercase tracking-widest ${isFirst ? 'text-indigo-200' : 'text-gray-400'}`}>XP</p>
                    </div>
                  </motion.div>
                );
              })}
            </div>

            <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
              {loading ? (
                <div className="p-12 text-center">
                  <div className="w-8 h-8 border-2 border-[#4F46E5] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
                  <p className="text-gray-500 text-sm">Loading rankings...</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-100">
                  <div className="flex items-center gap-4 px-5 py-3 text-xs text-gray-400 font-medium uppercase tracking-wider">
                    <span className="w-8 text-center">Rank</span>
                    <span className="flex-1">Player</span>
                    <span className="w-20 text-right">XP</span>
                  </div>

                  {entries.map((entry) => (
                    <div key={entry.rank}
                      className={`flex items-center gap-4 px-5 py-3.5 transition-colors ${
                        entry.is_me ? 'bg-[#EEF2FF]' : 'hover:bg-gray-50'
                      }`}
                    >
                      <div className="w-8 text-center">
                        <span className={`text-sm font-bold ${entry.rank <= 3 ? 'text-[#4F46E5]' : 'text-gray-400'}`}>
                          #{entry.rank}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <h4 className="text-sm font-medium text-[#1E293B] truncate">{entry.user_name}</h4>
                          {entry.is_me && (
                            <span className="px-1.5 py-0.5 text-[9px] font-bold bg-[#4F46E5] text-white rounded uppercase">You</span>
                          )}
                        </div>
                        <p className="text-xs text-gray-400 truncate">{entry.school}</p>
                      </div>
                      <div className="w-20 text-right">
                        <span className="text-sm font-semibold text-[#1E293B]">{entry.xp.toLocaleString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <p className="text-center text-xs text-gray-400 mt-4">
              Rankings update in real-time. Complete challenges to earn XP and climb the leaderboard!
            </p>
          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}
