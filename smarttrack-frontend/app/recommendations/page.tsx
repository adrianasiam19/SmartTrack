'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import Sidebar from '../components/Sidebar';
import BottomNav from '../components/BottomNav';
import AppLayout from '../components/AppLayout';
import { getAccessToken, getStoredUser, getCurrentUser, type UserProfile } from '../lib/authApi';

export default function RecommendationsPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [academicCompleted, setAcademicCompleted] = useState(false);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);

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

  const handleUploadComplete = () => {
    localStorage.setItem('atlas_academic_data', 'true');
    setAcademicCompleted(true);
    setUploadModalOpen(false);
  };

  if (loading) return (
    <AppLayout>
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-10 h-10 border-4 border-[#2563EB] border-t-transparent rounded-full animate-spin" />
      </div>
    </AppLayout>
  );

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-20">
          <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-8 pb-8">
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8"
            >
              <div className="flex items-center justify-between gap-4">
                <div>
                  <h1 className="text-2xl font-bold text-[#1E293B]">Programme Recommendations</h1>
                  <p className="text-sm text-[#64748B] mt-1">
                    {user?.programme || 'SHS Student'}
                    {user?.shs_level ? ` · ${user.shs_level}` : ''}
                  </p>
                </div>
                <div className="flex items-center gap-2 bg-[#EEF2FF] border border-[#C7D2FE] rounded-xl px-4 py-2">
                  <span className="text-sm font-semibold text-[#2563EB]">
                    {user?.xp?.toLocaleString() || 0} XP
                  </span>
                </div>
              </div>
            </motion.div>

            {/* Single primary card: status + one upload section */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className="bg-white border border-[#BFDBFE] rounded-2xl p-8 lg:p-10 shadow-sm"
            >
              <div className="text-center mb-10">
                <p className="text-xs font-semibold tracking-wide uppercase text-[#2563EB] mb-3">
                  Recommendation Status
                </p>
                <div className="w-14 h-14 bg-gradient-to-br from-[#2563EB] to-[#7C3AED] rounded-2xl flex items-center justify-center mx-auto mb-5 shadow-lg shadow-[#2563EB]/20">
                  <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h2 className="text-xl font-bold text-[#1E293B] mb-3">
                  Your Recommendation Profile is Still Being Built
                </h2>
                <p className="text-sm text-[#64748B] max-w-xl mx-auto leading-relaxed">
                  Complete the required learning activities, challenge levels and upload your academic
                  results to unlock your personalised programme recommendations.
                </p>
              </div>

              <div className="border-t border-[#E2E8F0] pt-8">
                <h3 className="text-lg font-bold text-[#1E293B] mb-2 text-center sm:text-left">
                  Upload Your WASSCE or Academic Results
                </h3>
                <p className="text-sm text-[#64748B] mb-6 leading-relaxed text-center sm:text-left">
                  Atlas uses your academic results together with your learning progress and challenge
                  performance to improve recommendation accuracy.
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-8">
                  {[
                    { label: 'WASSCE Results', desc: 'Final exam results', icon: 'W' },
                    { label: 'SHS Academic Reports', desc: 'School term reports', icon: 'R' },
                    { label: 'School Transcript', desc: 'Optional', icon: 'T' },
                  ].map((doc) => (
                    <button
                      key={doc.label}
                      type="button"
                      onClick={() => setUploadModalOpen(true)}
                      className="flex items-center gap-3 px-4 py-3.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl hover:bg-[#EEF2FF] hover:border-[#C7D2FE] transition-all text-left"
                    >
                      <div className="w-10 h-10 bg-white border border-[#E2E8F0] rounded-lg flex items-center justify-center text-sm font-bold text-[#2563EB]">
                        {doc.icon}
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-[#1E293B]">{doc.label}</p>
                        <p className="text-xs text-[#64748B]">{doc.desc}</p>
                      </div>
                    </button>
                  ))}
                </div>

                <button
                  onClick={() => setUploadModalOpen(true)}
                  className={`w-full flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-semibold text-base transition-all duration-200 active:scale-[0.98] ${
                    academicCompleted
                      ? 'bg-[#EEF2FF] border border-[#C7D2FE] text-[#2563EB]'
                      : 'bg-gradient-to-r from-[#2563EB] to-[#1D4ED8] text-white shadow-lg shadow-[#2563EB]/20 hover:shadow-xl hover:from-[#3B82F6] hover:to-[#2563EB]'
                  }`}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
                    {academicCompleted ? (
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    ) : (
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                    )}
                  </svg>
                  {academicCompleted ? 'Results Uploaded ✓' : 'Upload Academic Results'}
                </button>
                {academicCompleted && (
                  <p className="text-xs text-[#64748B] text-center mt-3">
                    Your academic results have been uploaded. They are being processed alongside your learning profile.
                  </p>
                )}
              </div>
            </motion.div>
          </main>
        </div>
        <BottomNav />
      </div>

      {uploadModalOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          onClick={() => setUploadModalOpen(false)}
        >
          <div className="absolute inset-0 bg-[#1E293B]/60 backdrop-blur-sm" />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            className="relative bg-white rounded-2xl border border-[#BFDBFE] shadow-2xl p-8 w-full max-w-md"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => setUploadModalOpen(false)}
              className="absolute top-4 right-4 p-2 rounded-xl hover:bg-[#EEF2FF] text-[#475569] hover:text-[#2563EB] transition-all"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <div className="w-14 h-14 bg-gradient-to-br from-[#2563EB] to-[#7C3AED] rounded-2xl flex items-center justify-center mx-auto mb-5 shadow-lg shadow-[#2563EB]/20">
              <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
              </svg>
            </div>

            <h3 className="text-lg font-bold text-[#1E293B] text-center mb-2">Upload Academic Results</h3>
            <p className="text-sm text-[#64748B] text-center mb-6">
              Upload your WASSCE results, school report, or transcript as a PDF or image file.
            </p>

            <div
              className="border-2 border-dashed border-[#C7D2FE] rounded-xl p-8 text-center hover:border-[#2563EB] hover:bg-[#EEF2FF] transition-all cursor-pointer group mb-6"
              onClick={handleUploadComplete}
            >
              <div className="w-12 h-12 bg-[#EEF2FF] rounded-xl flex items-center justify-center mx-auto mb-3 group-hover:bg-[#DBEAFE] transition-all">
                <svg className="w-6 h-6 text-[#2563EB]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.233-2.33 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" />
                </svg>
              </div>
              <p className="text-sm font-semibold text-[#1E293B] mb-1">
                Click to upload or drag and drop
              </p>
              <p className="text-xs text-[#64748B]">PDF, PNG, or JPG (max 10MB)</p>
            </div>

            <button
              onClick={handleUploadComplete}
              className="w-full px-5 py-3 bg-[#EEF2FF] border border-[#C7D2FE] text-[#475569] rounded-xl hover:bg-[#DBEAFE] hover:text-[#2563EB] transition-all text-sm font-medium"
            >
              Use Sample Academic Record Instead
            </button>

            <p className="text-xs text-[#64748B] text-center mt-4">
              Your data is encrypted and used only for generating personalised recommendations.
            </p>
          </motion.div>
        </div>
      )}
    </AppLayout>
  );
}
