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
import GuidanceDisclaimer from '../components/GuidanceDisclaimer';

function formatApiDetail(detail: unknown): string {
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === 'string') return item;
        if (item && typeof item === 'object' && 'msg' in item) {
          return String((item as { msg?: string }).msg || '');
        }
        return '';
      })
      .filter(Boolean)
      .join('\n') || 'Something went wrong. Please try again.';
  }
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

type PendingGrade = { subject: string; grade: string };

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
  rank?: number;
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
  recommendation_kind?: string;
  wassce_used?: boolean;
  used_fallback?: boolean;
  learner_notice?: string | null;
  behavioural_baseline?: string[];
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
      {items.map((p, index) => (
        <li key={`${p.programme}-${p.method || 'main'}-${p.rank || index}`}>
          <button
            type="button"
            onClick={() => onSelect(p)}
            className="w-full text-left rounded-2xl border border-[#E2E8F0] bg-white px-5 py-4 hover:border-[#2563EB] hover:shadow-sm transition"
          >
            <div className="flex items-start gap-3">
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-[#EEF2FF] text-sm font-bold text-[#2563EB]">
                {p.rank ?? index + 1}
              </span>
              <div className="min-w-0 flex-1">
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
              </div>
            </div>
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
  const [pendingGrades, setPendingGrades] = useState<PendingGrade[] | null>(null);
  const [pendingFilename, setPendingFilename] = useState<string | null>(null);
  const [pendingStoredName, setPendingStoredName] = useState<string | null>(null);
  const [pendingCandidateName, setPendingCandidateName] = useState<string | null>(null);
  const [isConfirming, setIsConfirming] = useState(false);
  const [isRemoving, setIsRemoving] = useState(false);
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

        const profile = fresh.learner_profile as {
          academic_upload?: { filename?: string; confirmed?: boolean };
          academic_upload_pending?: {
            filename?: string;
            stored_name?: string;
            grades?: PendingGrade[];
            candidate_name?: string;
          };
        } | null;
        const profileUpload = profile?.academic_upload;
        const pending = profile?.academic_upload_pending;
        if (pending?.grades?.length) {
          setPendingGrades(pending.grades);
          setPendingFilename(pending.filename || null);
          setPendingStoredName(pending.stored_name || null);
          setPendingCandidateName(pending.candidate_name || null);
        }
        if (profileUpload?.filename && profileUpload.confirmed !== false) {
          setUploadedFileName(profileUpload.filename);
        } else if (!pending?.grades?.length && localStorage.getItem(ACADEMIC_FLAG_KEY) === 'true') {
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
        throw new Error(formatApiDetail(data?.detail) || 'Upload failed. Please try again.');
      }

      const records = Array.isArray(data.records) ? (data.records as PendingGrade[]) : [];
      if (data.needs_confirmation && records.length > 0) {
        setPendingGrades(records);
        setPendingFilename(data.filename || file.name);
        setPendingStoredName(data.stored_name || null);
        setPendingCandidateName(data.candidate_name || null);
        setUploadMessage(
          data.message ||
            'Review the grades below and confirm before Atlas uses them.',
        );
        return;
      }

      // Legacy fallback if an older server still auto-saves.
      const filename = data.filename || file.name;
      localStorage.setItem(ACADEMIC_FLAG_KEY, 'true');
      localStorage.setItem(ACADEMIC_FILE_KEY, filename);
      setUploadedFileName(filename);
      setPendingGrades(null);
      setUploadMessage(data.message || 'Upload saved.');
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

  const handleConfirmGrades = async () => {
    if (!pendingGrades?.length) return;
    setIsConfirming(true);
    setUploadError('');
    try {
      const res = await fetchWithAuth(`${API_BASE}/challenges/academic/confirm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          records: pendingGrades.map((g) => ({
            subject: g.subject,
            grade: g.grade,
            exam_type: 'WASSCE',
          })),
          filename: pendingFilename || undefined,
          stored_name: pendingStoredName || undefined,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(formatApiDetail(data?.detail) || 'Could not confirm grades.');
      }
      const filename = data.filename || pendingFilename || 'WASSCE results';
      localStorage.setItem(ACADEMIC_FLAG_KEY, 'true');
      localStorage.setItem(ACADEMIC_FILE_KEY, filename);
      setUploadedFileName(filename);
      setPendingGrades(null);
      setPendingFilename(null);
      setPendingStoredName(null);
      setPendingCandidateName(null);
      setUploadMessage(
        data.message ||
          'WASSCE grades saved. Tap Get Recommendations to refine your matches.',
      );
      try {
        const fresh = await getCurrentUser();
        setUser(fresh);
        const elig = await getRecommendationEligibility();
        setEligibility(elig);
      } catch {
        // Non-fatal
      }
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Could not confirm grades.');
    } finally {
      setIsConfirming(false);
    }
  };

  const handleDiscardPending = async () => {
    setUploadError('');
    try {
      await fetchWithAuth(`${API_BASE}/challenges/academic/pending`, {
        method: 'DELETE',
      });
    } catch {
      // Still clear local preview
    }
    setPendingGrades(null);
    setPendingFilename(null);
    setPendingStoredName(null);
    setPendingCandidateName(null);
    setUploadMessage('Upload cancelled. Your previous results (if any) are unchanged.');
  };

  const handleRemoveResults = async () => {
    if (
      !window.confirm(
        'Remove your WASSCE results from Atlas? Recommendations will use your Atlas activity only.',
      )
    ) {
      return;
    }
    setIsRemoving(true);
    setUploadError('');
    try {
      const res = await fetchWithAuth(`${API_BASE}/challenges/academic`, {
        method: 'DELETE',
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(formatApiDetail(data?.detail) || 'Could not remove results.');
      }
      localStorage.removeItem(ACADEMIC_FLAG_KEY);
      localStorage.removeItem(ACADEMIC_FILE_KEY);
      setUploadedFileName(null);
      setPendingGrades(null);
      setPendingFilename(null);
      setPendingStoredName(null);
      setPendingCandidateName(null);
      setUploadMessage(data.message || 'WASSCE results removed.');
      setResult(null);
      try {
        const fresh = await getCurrentUser();
        setUser(fresh);
        const elig = await getRecommendationEligibility();
        setEligibility(elig);
      } catch {
        // Non-fatal
      }
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Could not remove results.');
    } finally {
      setIsRemoving(false);
    }
  };

  const handleGetRecommendations = async () => {
    if (eligibility && !eligibility.eligible) {
      setGenerateError(eligibility.message);
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
      try {
        const history = await getRecommendationHistory();
        const items: PhaseRecommendation[] = Array.isArray(history)
          ? history
          : history?.items || [];
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
  const allPhasesDone = Boolean(eligibility?.all_phases_completed);
  const wassceRecommended = Boolean(eligibility?.wassce_recommended_now);
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
              <GuidanceDisclaimer className="mt-4" />
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
                        Complete this phase checkpoint again to refresh behavioural programme matches.
                      </p>
                    ) : (
                      <ol className="space-y-2 list-none">
                        {(item.programme_suggestions || []).slice(0, 6).map((s, idx) => (
                          <li key={s.programme}>
                            <button
                              type="button"
                              onClick={() => setSelected(s)}
                              className="text-left text-sm font-medium text-[#1E293B] hover:text-[#2563EB] flex items-center gap-2"
                            >
                              <span className="text-[#2563EB] font-bold w-5">
                                {s.rank ?? idx + 1}.
                              </span>
                              {s.programme}
                            </button>
                          </li>
                        ))}
                      </ol>
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
                  ? allPhasesDone
                    ? 'Your matches — refine with WASSCE (optional)'
                    : 'Your programme matches from Atlas'
                  : 'Recommendations unlock with progress'}
              </h2>
              <p className="text-sm text-[#64748B] max-w-lg mx-auto mb-4 leading-relaxed">
                Atlas builds recommendations from your journey. WASSCE is optional and used
                at the end to refine admission insights:
              </p>
              <ul className="text-sm text-[#475569] max-w-md mx-auto mb-6 space-y-1.5 text-left list-disc list-inside">
                <li>Psychometric Profile</li>
                <li>Challenge Performance &amp; subject strengths</li>
                <li>Learning Centre activity</li>
                <li>
                  WASSCE / academic results — optional refine after all phases
                </li>
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

              {phaseUnlocked && (allPhasesDone || wassceRecommended) && (
                <div className="max-w-lg mx-auto mb-6 rounded-xl border border-[#BFDBFE] bg-[#EFF6FF] px-5 py-4 text-left">
                  <p className="text-sm font-semibold text-[#1E40AF]">
                    Optional: upload WASSCE to refine your matches
                  </p>
                  <p className="text-sm text-[#1E3A8A] mt-2 leading-relaxed">
                    You already have behavioural recommendations from Atlas. Uploading results
                    lets Atlas tweak the ranking with your aggregate and university cut-offs.
                    This is never compulsory.
                  </p>
                </div>
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
                  onClick={() => void handleGetRecommendations()}
                  disabled={
                    isUploading || isGenerating || isConfirming || isRemoving || !phaseUnlocked
                  }
                  className="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-semibold text-white bg-gradient-to-r from-[#2563EB] to-[#1D4ED8] shadow-lg shadow-[#2563EB]/20 hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-[0.98]"
                >
                  {isGenerating ? 'Generating…' : 'Get Recommendations'}
                </button>

                <button
                  type="button"
                  onClick={openFilePicker}
                  disabled={isUploading || isGenerating || isConfirming || isRemoving}
                  className={`inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-semibold transition-all duration-200 active:scale-[0.98] disabled:opacity-60 ${
                    allPhasesDone || uploadedFileName
                      ? 'bg-gradient-to-r from-[#7C3AED] to-[#5B21B6] text-white shadow-lg shadow-[#7C3AED]/20'
                      : 'bg-[#EEF2FF] border border-[#C7D2FE] text-[#2563EB]'
                  }`}
                >
                  {isUploading
                    ? 'Uploading…'
                    : uploadedFileName
                      ? 'Replace Results'
                      : allPhasesDone
                        ? 'Upload WASSCE to refine'
                        : 'Upload WASSCE (optional)'}
                </button>

                {uploadedFileName && !pendingGrades && (
                  <button
                    type="button"
                    onClick={() => void handleRemoveResults()}
                    disabled={isUploading || isGenerating || isConfirming || isRemoving}
                    className="inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-semibold border border-[#FECACA] bg-white text-[#B91C1C] hover:bg-[#FEF2F2] disabled:opacity-60 transition-all active:scale-[0.98]"
                  >
                    {isRemoving ? 'Removing…' : 'Remove Results'}
                  </button>
                )}
              </div>

              {pendingGrades && pendingGrades.length > 0 && (
                <div className="max-w-lg mx-auto mt-6 rounded-xl border border-[#C7D2FE] bg-white px-5 py-4 text-left">
                  <p className="text-sm font-semibold text-[#1E40AF]">
                    Confirm these WASSCE grades
                  </p>
                  <p className="text-xs text-[#64748B] mt-1 mb-3">
                    {pendingFilename
                      ? `From “${pendingFilename}”. `
                      : ''}
                    {pendingCandidateName
                      ? `Candidate name matched: ${pendingCandidateName}. `
                      : ''}
                    Atlas will not use them until you confirm.
                  </p>
                  <ul className="divide-y divide-[#E2E8F0] text-sm mb-4 max-h-56 overflow-y-auto">
                    {pendingGrades.map((g) => (
                      <li
                        key={`${g.subject}-${g.grade}`}
                        className="flex items-center justify-between py-2 gap-3"
                      >
                        <span className="text-[#334155]">{g.subject}</span>
                        <span className="font-semibold text-[#1E293B] tabular-nums">
                          {g.grade}
                        </span>
                      </li>
                    ))}
                  </ul>
                  <div className="flex flex-col sm:flex-row gap-2">
                    <button
                      type="button"
                      onClick={() => void handleConfirmGrades()}
                      disabled={isConfirming || isUploading}
                      className="inline-flex flex-1 items-center justify-center px-4 py-2.5 rounded-xl font-semibold text-white bg-[#059669] hover:bg-[#047857] disabled:opacity-60"
                    >
                      {isConfirming ? 'Saving…' : 'Confirm & save'}
                    </button>
                    <button
                      type="button"
                      onClick={() => void handleDiscardPending()}
                      disabled={isConfirming || isUploading}
                      className="inline-flex flex-1 items-center justify-center px-4 py-2.5 rounded-xl font-semibold border border-[#E2E8F0] text-[#475569] hover:bg-[#F8FAFC] disabled:opacity-60"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              {uploadedFileName && !pendingGrades && (
                <p className="text-sm text-[#2563EB] mt-4">
                  Saved: <span className="font-medium">{uploadedFileName}</span>
                  {' — '}tap Get Recommendations again to apply the refine.
                </p>
              )}
              {uploadMessage && (
                <p className="text-sm text-[#059669] mt-3 whitespace-pre-line">{uploadMessage}</p>
              )}
              {uploadError && (
                <p className="text-sm text-[#DC2626] mt-4 whitespace-pre-line">{uploadError}</p>
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
                    {result.wassce_used
                      ? 'Refined with WASSCE'
                      : 'Programme Match (from Atlas activity)'}
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
                    {result.wassce_used ? (
                      <span className="px-3 py-1.5 rounded-lg bg-[#DCFCE7] text-[#166534] font-semibold">
                        Academic refine applied
                      </span>
                    ) : (
                      <span className="px-3 py-1.5 rounded-lg bg-[#EEF2FF] text-[#3730A3] font-semibold">
                        Behavioural match · no WASSCE required
                      </span>
                    )}
                    {typeof result.grades_used === 'number' && result.grades_used > 0 && (
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
                  <h3 className="text-lg font-bold text-[#1E293B]">
                    {result.wassce_used ? 'Refined programme ranking' : 'Ranked programmes'}
                  </h3>
                  <p className="text-sm text-[#64748B]">
                    Listed in order of recommendation strength (1 = strongest match). No
                    percentages are shown.
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
