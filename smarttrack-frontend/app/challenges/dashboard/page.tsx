'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';

interface DashboardData {
  radar_chart: Record<string, number>;
  behavioral_traits: Record<string, number>;
  overall_score: number;
  career_matches: Array<{ path: string; match: number }>;
}

export default function ChallengeDashboard() {
  const router = useRouter();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const mockData: DashboardData = {
      radar_chart: { "MATH": 0.8, "SCIENCE": 0.7, "VERBAL": 0.9, "GENERAL": 0.6, "LOGIC": 0.85 },
      behavioral_traits: { "Persistence": 0.85, "Processing Speed": 0.92, "Consistency": 0.78, "Risk Appetite": 0.45 },
      overall_score: 94.2,
      career_matches: [
        { path: "Software Engineering", match: 0.95 },
        { path: "Data Science", match: 0.88 },
        { path: "Business Analytics", match: 0.82 }
      ]
    };
    setTimeout(() => { setData(mockData); setLoading(false); }, 1500);
  }, []);

  if (loading) return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="w-10 h-10 border-3 border-[#4F46E5] border-t-transparent rounded-full animate-spin" />
        <p className="text-gray-500 text-sm font-medium">Analyzing your profile...</p>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#F8FAFC] p-6 md:p-12">
      <div className="max-w-6xl mx-auto">
        <header className="mb-10">
          <span className="text-[#4F46E5] text-xs font-bold tracking-[0.2em] uppercase mb-2 block">Challenge Result</span>
          <h1 className="text-3xl md:text-4xl font-bold text-[#1E293B] flex items-center gap-4">
            Cognitive Profile
            <button onClick={() => router.push('/challenges')}
              className="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium hover:bg-gray-50 transition-all">
              Back to Challenges
            </button>
          </h1>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-7 bg-white rounded-2xl border border-gray-200 p-8">
            <h3 className="text-lg font-bold text-[#1E293B] mb-6">Domain Proficiency</h3>
            <div className="aspect-square w-full max-w-md mx-auto relative flex items-center justify-center">
              <svg viewBox="0 0 200 200" className="w-full h-full">
                <polygon points="100,40 160,80 140,150 60,150 40,80" fill="rgba(79,70,229,0.1)" stroke="#4F46E5" strokeWidth="2" />
                <text x="100" y="30" textAnchor="middle" fill="#64748B" fontSize="10" fontWeight="bold">MATH</text>
                <text x="175" y="85" textAnchor="start" fill="#64748B" fontSize="10" fontWeight="bold">SCIENCE</text>
                <text x="150" y="165" textAnchor="middle" fill="#64748B" fontSize="10" fontWeight="bold">VERBAL</text>
                <text x="50" y="165" textAnchor="middle" fill="#64748B" fontSize="10" fontWeight="bold">GENERAL</text>
                <text x="25" y="85" textAnchor="end" fill="#64748B" fontSize="10" fontWeight="bold">LOGIC</text>
              </svg>
            </div>
          </div>

          <div className="lg:col-span-5 flex flex-col gap-8">
            <div className="bg-[#4F46E5] rounded-2xl p-8 text-white">
              <p className="text-xs font-bold tracking-widest uppercase mb-1 opacity-70">Composite Percentile</p>
              <div className="flex items-baseline gap-2">
                <h2 className="text-5xl font-black">{data?.overall_score}</h2>
                <span className="text-xl font-bold">th</span>
              </div>
              <p className="mt-4 text-sm font-medium leading-relaxed text-indigo-200">
                You are performing in the top 6% of students in your category nationwide.
              </p>
            </div>

            <div className="bg-white rounded-2xl border border-gray-200 p-8">
              <h3 className="text-lg font-bold text-[#1E293B] mb-6">Behavioral Intelligence</h3>
              {data && Object.entries(data.behavioral_traits).map(([label, val], idx) => (
                <div key={label} className="space-y-2 mb-4">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-500 font-medium">{label}</span>
                    <span className="text-[#1E293B] font-bold">{Math.round(val * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full transition-all duration-1000 ${idx % 2 === 0 ? 'bg-[#4F46E5]' : 'bg-[#D97706]'}`}
                      style={{ width: `${val * 100}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-8 flex flex-col md:flex-row gap-4">
          <button onClick={() => router.push('/challenges/leaderboard')}
            className="flex-1 bg-white border border-gray-200 text-[#1E293B] font-medium py-4 rounded-xl hover:bg-gray-50 transition-all flex items-center justify-center gap-3">
            See Global Rankings
          </button>
          <button onClick={() => router.push('/recommendations')}
            className="flex-1 bg-[#4F46E5] text-white font-medium py-4 rounded-xl hover:bg-[#4338CA] transition-all flex items-center justify-center gap-3">
            Career Recommendations
          </button>
        </div>
      </div>
    </div>
  );
}
