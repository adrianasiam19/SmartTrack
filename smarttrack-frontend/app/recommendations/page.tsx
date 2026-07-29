'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
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
import {
  getRecommendationHistory,
  getRecommendationEligibility,
  type RecommendationEligibility,
} from '../lib/phasesApi';

function formatApiDetail(detail: unknown): string {
  if (typeof detail === 'string') return detail;
  if (detail && typeof detail === 'object') {
    const d = detail as {
      message?: string;
      short_message?: string;
      title?: string;
      detail?: string;
      code?: string;
    };
    const parts: string[] = [];
    if (d.title) parts.push(d.title);
    if (d.message && d.message !== d.title) parts.push(d.message);
    else if (d.short_message && d.short_message !== d.title) parts.push(d.short_message);
    if (parts.length) return parts.join('\n\n');
    if (d.detail) return d.detail;
  }
  return 'Could not generate recommendations. Please try again.';
}

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

type ProgrammeCard = {
  programme: string;
  family?: string;
  cutoff?: number;
  demand?: string;
  aggregate?: number | null;
  overview?: string;
  required_skills?: string;
  career_opportunities?: string;
  why_recommended?: string;
  admission_insight?: string;
  method?: string;
  learn_more_url?: string | null;
};

type RecommendationPayload = {
  summary_message?: string;
  detailed_message?: string;
  grades_used?: number;
  suitable_programmes?: ProgrammeCard[];
  competitive_programmes?: ProgrammeCard[];
  recommendations?: ProgrammeCard[];
  admission_insights?: {
    aggregate?: number | null;
    complete?: boolean;
  };
  ml_alternate?: {
    enabled?: boolean;
    title?: string;
    disclaimer?: string;
    programmes?: ProgrammeCard[];
  } | null;
  primary_source?: string;
  used_fallback?: boolean;
  learner_notice?: string | null;
};

type PhaseRecommendation = {
  phase: number;
  phase_label: string;
  generated_at: string;
  programme_suggestions: ProgrammeCard[];
  rationale_summary: string;
  is_final: boolean;
};

function ProgrammeList({
  items,
  onSelect,
}: {
  items: ProgrammeCard[];
  onSelect: (p: ProgrammeCard) => void;
}) {
  if (!items.length) {
    return (
      <p className="text-sm text-[#94A3B8]">
        No programmes in this section yet.
      </p>
    );
  }
  return (
    <ul className="space-y-3">
      {items.map((p) => (
        <li key={`${p.programme}-${p.method || 'main'}`}>
          <button
            type="button"
            onClick={() => onSelect(p)}
            className="w-full text-left rounded-2xl border border-[#E2E8F0] bg-white px-5 py-4 hover:border-[#2563EB] hover:shadow-sm transition"
          >
            <p className="font-semibold text-[#1E293B]">{p.programme}</p>
            {p.family && (
              <p className="text-xs text-[#64748B] mt-1">{p.family}</p>
            )}
            {p.why_recommended && (
              <p className="text-sm text-[#475569] mt-2 line-clamp-2">
                {p.why_recommended}
              </p>
            )}
            <p className="text-xs font-medium text-[#2563EB] mt-3">View details →</p>
          </button>
        </li>
      ))}
    </ul>
  );
}

function ProgrammeDetailModal({
  programme,
  onClose,
}: {
  programme: ProgrammeCard | null;
  onClose: () => void;
}) {
  if (!programme) return null;
  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 bg-black/40"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          initial={{ y: 40, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 40, opacity: 0 }}
          className="w-full max-w-lg max-h-[85vh] overflow-y-auto rounded-2xl bg-white p-6 shadow-xl"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex items-start justify-between gap-3 mb-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-[#2563EB]">
                Programme details
              </p>
              <h3 className="text-xl font-bold text-[#1E293B] mt-1">
                {programme.programme}
              </h3>
              {programme.family && (
                <p className="text-sm text-[#64748B] mt-1">{programme.family}</p>
              )}
            </div>
            <button
              type="button"
              onClick={onClose}
              className="text-[#64748B] hover:text-[#1E293B] text-sm font-medium"
            >
              Close
            </button>
          </div>

          <div className="space-y-4 text-sm text-[#475569]">
            <section>
              <h4 className="font-semibold text-[#1E293B] mb-1">Overview</h4>
              <p>{programme.overview || 'A programme matched to your Atlas profile.'}</p>
            </section>
            <section>
              <h4 className="font-semibold text-[#1E293B] mb-1">Required skills</h4>
              <p>{programme.required_skills || 'Strong foundations and consistent practice.'}</p>
            </section>
            <section>
              <h4 className="font-semibold text-[#1E293B] mb-1">Career opportunities</h4>
              <p>
                {programme.career_opportunities ||
                  'Related professional and further-study pathways.'}
              </p>
            </section>
            <section>
              <h4 className="font-semibold text-[#1E293B] mb-1">Why Atlas recommended it</h4>
              <p>
                {programme.why_recommended ||
                  'Matched to your academic results, psychometric profile, and challenge performance.'}
              </p>
            </section>
            <section>
              <h4 className="font-semibold text-[#1E293B] mb-1">Admission insight</h4>
              <p>
                {programme.admission_insight ||
                  'Use this as guidance while you explore admission options.'}
              </p>
            </section>
          </div>

          <button
            type="button"
            disabled
            className="mt-6 w-full rounded-xl bg-[#EEF2FF] text-[#2563EB] font-semibold py-3 opacity-80 cursor-not-allowed"
            title="Coming soon"
          >
            Learn More
          </button>
          <p className="text-[11px] text-center text-[#94A3B8] mt-2">
            Official university links will be added in a future update.
          </p>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

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
  const [selected, setSelected] = useState<ProgrammeCard | null>(null);
  const [eligibility, setEligibility] = useState<RecommendationEligibility | null>(
    null,
  );

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
          const elig = await getRecommendationEligibility();
          setEligibility(elig);
        } catch {
          // optional — generate still gated on backend
        }

        try {
          const history = await getRecommendationHistory();
          const items: PhaseRecommendation[] = Array.isArray(history)
            ? history
            : history?.items || [];
          // Extra client guard: one card per phase number
          const byPhase = new Map<number, PhaseRecommendation>();
          for (const item of items) {
            const existing = byPhase.get(item.phase);
            if (
              !existing ||
              new Date(item.generated_at).getTime() >
                new Date(existing.generated_at).getTime()
            ) {
              byPhase.set(item.phase, item);
            }
          }
          setPhaseHistory(
            Array.from(byPhase.values()).sort((a, b) => a.phase - b.phase),
          );
        } catch {
          // optional
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
    if (eligibility && !eligibility.eligible) {
      setGenerateError(eligibility.message);
      return;
    }
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
        if (data?.detail?.eligibility) {
          setEligibility(data.detail.eligibility as RecommendationEligibility);
        }
        throw new Error(formatApiDetail(data?.detail));
      }
      setResult(data);
      try {
        const elig = await getRecommendationEligibility();
        setEligibility(elig);
      } catch {
        // non-fatal
      }
    } catch (err) {
      setGenerateError(
        err instanceof Error ? err.message : 'Could not generate recommendations.',
      );
    } finally {
      setIsGenerating(false);
    }
  };

  // Optimistic when eligibility has not loaded; backend remains the hard gate.
  const phaseUnlocked = !eligibility || eligibility.eligible;
  const focus = eligibility?.mandatory?.focus_phase;
  const learningDone = Boolean(
    eligibility?.recommended?.learning_center_lesson_completed,
  );

  const suitable =
    result?.suitable_programmes ||
    result?.recommendations ||
    [];
  const competitive = result?.competitive_programmes || [];

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
                  <h1 className="text-2xl font-bold text-[#1E293B]">
                    Programme Recommendations
                  </h1>
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
                <h2 className="text-lg font-bold text-[#1E293B]">Phase guidance</h2>
                <p className="text-sm text-[#64748B]">
                  Insights from your phase checkpoints — one summary per phase.
                </p>
                {phaseHistory.map((item) => (
                  <div
                    key={`phase-${item.phase}`}
                    className="bg-white border border-[#E2E8F0] rounded-2xl p-5"
                  >
                    <div className="flex items-center justify-between gap-3 mb-2">
                      <p className="font-semibold text-[#1E293B]">{item.phase_label}</p>
                      <span className="text-xs font-medium text-[#64748B]">
                        {item.is_final ? 'Final' : 'Interim'}
                      </span>
                    </div>
                    <p className="text-sm text-[#475569] mb-3">{item.rationale_summary}</p>
                    {(item.programme_suggestions || []).length === 0 ? (
                      <p className="text-sm text-[#94A3B8]">
                        Upload your results to unlock specific programme matches for this phase.
                      </p>
                    ) : (
                      <ul className="space-y-2">
                        {(item.programme_suggestions || []).slice(0, 6).map((s) => (
                          <li key={s.programme}>
                            <button
                              type="button"
                              onClick={() => setSelected(s)}
                              className="text-left text-sm font-medium text-[#1E293B] hover:text-[#2563EB]"
                            >
                              {s.programme}
                            </button>
                          </li>
                        ))}
                      </ul>
                    )}
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
                {phaseUnlocked
                  ? 'Unlock Your Programme Matches'
                  : 'Recommendations unlock with progress'}
              </h2>
              <p className="text-sm text-[#64748B] max-w-lg mx-auto mb-4 leading-relaxed">
                Atlas recommendations are based on three signals only:
              </p>
              <ul className="text-sm text-[#475569] max-w-md mx-auto mb-6 space-y-1.5 text-left list-disc list-inside">
                <li>Academic Results (uploaded WASSCE / academic results)</li>
                <li>Psychometric Profile</li>
                <li>Challenge Performance</li>
              </ul>

              {!phaseUnlocked && (
                <div className="max-w-lg mx-auto mb-8 rounded-xl border border-[#FDE68A] bg-[#FFFBEB] px-5 py-4 text-left">
                  <p className="text-sm font-semibold text-[#92400E]">
                    {eligibility?.title || 'You are not yet eligible for a recommendation.'}
                  </p>
                  <p className="text-sm text-[#78350F] mt-2 whitespace-pre-line leading-relaxed">
                    {eligibility?.message ||
                      'You are making great progress!\n\nComplete the remaining levels in this phase to unlock your personalised programme recommendations.\n\nWe also recommend exploring at least one lesson in the Learning Center to strengthen your learner profile and improve future recommendations.'}
                  </p>
                  {focus && (
                    <p className="text-xs font-medium text-[#92400E] mt-3">
                      Phase {focus.number} ({focus.name}): {focus.levels_completed} of{' '}
                      {focus.levels_total} levels complete
                      {focus.levels_remaining > 0
                        ? ` · ${focus.levels_remaining} remaining`
                        : ''}
                    </p>
                  )}
                  <a
                    href="/challenges"
                    className="inline-block mt-3 text-sm font-semibold text-[#2563EB] hover:underline"
                  >
                    Continue challenges →
                  </a>
                </div>
              )}

              {phaseUnlocked && !learningDone && (
                <p className="text-sm text-[#64748B] max-w-lg mx-auto mb-6 leading-relaxed">
                  Tip: explore at least one lesson in the{' '}
                  <a href="/learning" className="font-semibold text-[#2563EB] hover:underline">
                    Learning Center
                  </a>{' '}
                  to strengthen your learner profile. This is recommended, not required.
                </p>
              )}

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
                  disabled={isUploading || isGenerating}
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
                <p className="text-sm text-[#78350F] mt-4 whitespace-pre-line text-left max-w-lg mx-auto bg-[#FFFBEB] border border-[#FDE68A] rounded-xl px-4 py-3">
                  {generateError}
                </p>
              )}
            </motion.div>

            {result && (
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-8 space-y-8"
              >
                <div className="bg-white border border-[#BFDBFE] rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-[#1E293B] mb-2">
                    Admission Insights
                  </h3>
                  {result.summary_message && (
                    <p className="text-sm text-[#64748B] mb-4">{result.summary_message}</p>
                  )}
                  {result.learner_notice ? (
                    <p className="text-sm text-[#92400E] bg-[#FFFBEB] border border-[#FDE68A] rounded-xl px-4 py-3 mb-4 whitespace-pre-line">
                      {result.learner_notice}
                    </p>
                  ) : null}
                  <div className="flex flex-wrap gap-3 text-sm">
                    {typeof result.grades_used === 'number' && (
                      <span className="px-3 py-1.5 rounded-lg bg-[#FFF7ED] text-[#C2410C] font-semibold">
                        {result.grades_used} grade{result.grades_used === 1 ? '' : 's'} used
                      </span>
                    )}
                    {typeof result.admission_insights?.aggregate === 'number' && (
                      <span className="px-3 py-1.5 rounded-lg bg-[#FEF3C7] text-[#92400E] font-semibold">
                        Aggregate {result.admission_insights.aggregate}
                        {result.admission_insights.complete === false ? ' (provisional)' : ''}
                      </span>
                    )}
                  </div>
                </div>

                <section className="space-y-3">
                  <h3 className="text-lg font-bold text-[#1E293B]">Recommended Programmes</h3>
                  <p className="text-sm text-[#64748B]">
                    Strong profile matches whose admission points sit close to your aggregate.
                  </p>
                  <ProgrammeList items={suitable} onSelect={setSelected} />
                </section>

                {competitive.length > 0 && (
                  <section className="space-y-3">
                    <h3 className="text-lg font-bold text-[#1E293B]">Competitive Programmes</h3>
                    <p className="text-sm text-[#64748B]">
                      These programmes match your interests and strengths. However, admission
                      through the regular stream may be competitive with your current aggregate.
                      You may wish to explore fee-paying or self-financing options where available.
                    </p>
                    <ProgrammeList items={competitive} onSelect={setSelected} />
                  </section>
                )}
              </motion.div>
            )}
          </main>
        </div>
        <BottomNav />
      </div>

      <ProgrammeDetailModal programme={selected} onClose={() => setSelected(null)} />
    </AppLayout>
  );
}
