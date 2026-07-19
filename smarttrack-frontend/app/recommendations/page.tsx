'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import Sidebar from '../components/Sidebar';
import BottomNav from '../components/BottomNav';
import AppLayout from '../components/AppLayout';
import {
  getAccessToken,
  getStoredUser,
  getCurrentUser,
  fetchWithAuth,
  type UserProfile,
} from '../lib/authApi';
import { getRecommendationHistory } from '../lib/phasesApi';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const ACADEMIC_FLAG_KEY = 'atlas_academic_data';
const ACADEMIC_FILE_KEY = 'atlas_academic_filename';
const MAX_FILE_BYTES = 10 * 1024 * 1024;
const ACCEPTED_TYPES = [
  'application/pdf',
  'image/png',
  'image/jpeg',
  'image/jpg',
  'image/webp',
];

type ProgrammeRecommendation = {
  programme_family: string;
  fit_score: number;
  fit_level: string;
  description: string;
  why_good_fit: string;
  foundation?: string;
};

type RecommendationPayload = {
  academic_score?: number;
  performance_level?: string;
  summary_message?: string;
  detailed_message?: string;
  recommendations?: ProgrammeRecommendation[];
  grades_used?: number;
};

type PhaseRecommendation = {
  phase: number;
  phase_label: string;
  generated_at: string;
  programme_suggestions: { programme: string; score: number }[];
  rationale_summary: string;
  is_final: boolean;
};

export default function RecommendationsPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generateError, setGenerateError] = useState('');
  const [result, setResult] = useState<RecommendationPayload | null>(null);
  const [phaseHistory, setPhaseHistory] = useState<PhaseRecommendation[]>([]);

  useEffect(() => {
    const load = async () => {
      try {
        if (!getAccessToken()) {
          router.push('/login');
          return;
        }
        const cached = getStoredUser();
        if (cached) setUser(cached);
        const fresh = await getCurrentUser();
        setUser(fresh);

        const profileUpload = (fresh.learner_profile as { academic_upload?: { filename?: string } } | null)
          ?.academic_upload;
        if (profileUpload?.filename) {
          setUploadedFileName(profileUpload.filename);
        } else if (localStorage.getItem(ACADEMIC_FLAG_KEY) === 'true') {
          setUploadedFileName(localStorage.getItem(ACADEMIC_FILE_KEY));
        }

        try {
          const history = await getRecommendationHistory();
          setPhaseHistory(Array.isArray(history) ? history : history?.items || []);
        } catch {
          // Phase history optional until checkpoints completed
        }
      } catch {
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [router]);

  const openFilePicker = () => {
    setUploadError('');
    setGenerateError('');
    fileInputRef.current?.click();
  };

  const handleFileSelected = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file) return;

    setUploadError('');
    setUploadMessage('');
    setResult(null);

    const typeOk =
      ACCEPTED_TYPES.includes(file.type) ||
      /\.(pdf|png|jpe?g|webp)$/i.test(file.name);
    if (!typeOk) {
      setUploadError('Please choose a PDF, PNG, or JPG file.');
      return;
    }
    if (file.size > MAX_FILE_BYTES) {
      setUploadError('That file is too large. Please choose a file under 10MB.');
      return;
    }

    setIsUploading(true);
    try {
      const form = new FormData();
      form.append('file', file);
      const res = await fetchWithAuth(`${API_BASE}/challenges/academic/upload`, {
        method: 'POST',
        body: form,
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data?.detail || 'Upload failed. Please try again.');
      }

      const filename = data.filename || file.name;
      localStorage.setItem(ACADEMIC_FLAG_KEY, 'true');
      localStorage.setItem(ACADEMIC_FILE_KEY, filename);
      setUploadedFileName(filename);
      setUploadMessage(
        data.message ||
          (data.grades_extracted
            ? 'Upload saved and grades detected.'
            : 'Upload saved. Tap Get Recommendations when you are ready.'),
      );
      try {
        const fresh = await getCurrentUser();
        setUser(fresh);
      } catch {
        // Non-fatal
      }
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleGetRecommendations = async () => {
    if (!uploadedFileName) {
      setGenerateError('Upload your academic results first.');
      return;
    }
    setGenerateError('');
    setIsGenerating(true);
    try {
      const res = await fetchWithAuth(`${API_BASE}/challenges/recommendations/generate`, {
        method: 'GET',
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(
          data?.detail || 'Could not generate recommendations. Please try again.',
        );
      }
      setResult(data);
    } catch (err) {
      setGenerateError(
        err instanceof Error ? err.message : 'Could not generate recommendations.',
      );
    } finally {
      setIsGenerating(false);
    }
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="w-10 h-10 border-4 border-[#2563EB] border-t-transparent rounded-full animate-spin" />
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-20">
          <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-8 pb-28">
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8"
            >
              <div className="flex items-center justify-between gap-4">
                <div>
                  <h1 className="text-2xl font-bold text-[#1E293B]">Programme Recommendations</h1>
                  <p className="text-sm text-[#64748B] mt-1">
                    {user?.programme || 'Student'}
                  </p>
                </div>
                <div className="flex items-center gap-2 bg-[#EEF2FF] border border-[#C7D2FE] rounded-xl px-4 py-2">
                  <span className="text-sm font-semibold text-[#2563EB]">
                    {user?.xp?.toLocaleString() || 0} XP
                  </span>
                </div>
              </div>
            </motion.div>

            {phaseHistory.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8 space-y-4"
              >
                <h2 className="text-lg font-bold text-[#1E293B]">Phase guidance history</h2>
                {phaseHistory.map((item) => (
                  <div
                    key={`${item.phase}-${item.generated_at}`}
                    className="bg-white border border-[#E2E8F0] rounded-2xl p-5"
                  >
                    <div className="flex items-center justify-between gap-3 mb-2">
                      <p className="font-semibold text-[#1E293B]">{item.phase_label}</p>
                      <span className="text-xs font-medium text-[#64748B]">
                        {item.is_final ? 'Final' : 'Interim'}
                      </span>
                    </div>
                    <p className="text-sm text-[#475569] mb-3">{item.rationale_summary}</p>
                    <ul className="space-y-1">
                      {(item.programme_suggestions || []).slice(0, 5).map((s) => (
                        <li key={s.programme} className="text-sm text-[#1E293B]">
                          {s.programme}
                          <span className="text-[#64748B]"> · score {Math.round(s.score * 100) / 100}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </motion.div>
            )}

            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-br from-white to-[#EEF2FF] border border-[#BFDBFE] rounded-2xl p-8 lg:p-10 text-center shadow-sm"
            >
              <div className="w-16 h-16 bg-gradient-to-br from-[#2563EB] to-[#7C3AED] rounded-2xl flex items-center justify-center mx-auto mb-5 shadow-lg shadow-[#2563EB]/20">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>

              <h2 className="text-xl font-bold text-[#1E293B] mb-3">
                Unlock Your Programme Matches
              </h2>
              <p className="text-sm text-[#64748B] max-w-lg mx-auto mb-8 leading-relaxed">
                Upload your WASSCE or academic results, then press Get Recommendations.
                Atlas will combine your results with your learning profile to rank programme families.
              </p>

              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.png,.jpg,.jpeg,.webp,application/pdf,image/png,image/jpeg,image/webp"
                className="hidden"
                onChange={(e) => void handleFileSelected(e)}
              />

              <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
                <button
                  type="button"
                  onClick={openFilePicker}
                  disabled={isUploading || isGenerating}
                  className={`inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-semibold transition-all duration-200 active:scale-[0.98] disabled:opacity-60 ${
                    uploadedFileName
                      ? 'bg-[#EEF2FF] border border-[#C7D2FE] text-[#2563EB]'
                      : 'bg-gradient-to-r from-[#2563EB] to-[#1D4ED8] text-white shadow-lg shadow-[#2563EB]/20 hover:shadow-xl hover:from-[#3B82F6] hover:to-[#2563EB]'
                  }`}
                >
                  {isUploading
                    ? 'Uploading…'
                    : uploadedFileName
                      ? 'Replace Results'
                      : 'Upload WASSCE or Academic Results'}
                </button>

                <button
                  type="button"
                  onClick={() => void handleGetRecommendations()}
                  disabled={!uploadedFileName || isUploading || isGenerating}
                  className="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-semibold text-white bg-gradient-to-r from-[#7C3AED] to-[#5B21B6] shadow-lg shadow-[#7C3AED]/20 hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-[0.98]"
                >
                  {isGenerating ? 'Generating…' : 'Get Recommendations'}
                </button>
              </div>

              {uploadedFileName && (
                <p className="text-sm text-[#2563EB] mt-4">
                  Uploaded: <span className="font-medium">{uploadedFileName}</span>
                </p>
              )}
              {uploadMessage && (
                <p className="text-sm text-[#059669] mt-3">{uploadMessage}</p>
              )}
              {uploadError && (
                <p className="text-sm text-[#DC2626] mt-4">{uploadError}</p>
              )}
              {generateError && (
                <p className="text-sm text-[#DC2626] mt-4">{generateError}</p>
              )}
            </motion.div>

            {result?.recommendations && result.recommendations.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-8 space-y-4"
              >
                <div className="bg-white border border-[#BFDBFE] rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-[#1E293B] mb-2">Your Matches</h3>
                  {result.summary_message && (
                    <p className="text-sm text-[#64748B] mb-4">{result.summary_message}</p>
                  )}
                  <div className="flex flex-wrap gap-3 text-sm">
                    {typeof result.academic_score === 'number' && (
                      <span className="px-3 py-1.5 rounded-lg bg-[#EEF2FF] text-[#2563EB] font-semibold">
                        Score {result.academic_score}%
                      </span>
                    )}
                    {result.performance_level && (
                      <span className="px-3 py-1.5 rounded-lg bg-[#F0FDF4] text-[#059669] font-semibold">
                        {result.performance_level}
                      </span>
                    )}
                    {typeof result.grades_used === 'number' && (
                      <span className="px-3 py-1.5 rounded-lg bg-[#FFF7ED] text-[#C2410C] font-semibold">
                        {result.grades_used} grade{result.grades_used === 1 ? '' : 's'} used
                      </span>
                    )}
                  </div>
                </div>

                {result.recommendations.map((rec) => (
                  <div
                    key={rec.programme_family}
                    className="bg-white border border-[#E2E8F0] rounded-2xl p-5"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <h4 className="text-base font-bold text-[#1E293B]">
                          {rec.programme_family}
                        </h4>
                        <p className="text-xs font-semibold text-[#7C3AED] mt-1">
                          {rec.fit_level}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-[#2563EB]">{rec.fit_score}</div>
                        <div className="text-[11px] text-[#64748B]">fit score</div>
                      </div>
                    </div>
                    <p className="text-sm text-[#475569] mt-3">{rec.description}</p>
                    <p className="text-sm text-[#64748B] mt-2">{rec.why_good_fit}</p>
                    {rec.foundation && (
                      <p className="text-xs text-[#94A3B8] mt-2">Foundation: {rec.foundation}</p>
                    )}
                  </div>
                ))}
              </motion.div>
            )}
          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}
