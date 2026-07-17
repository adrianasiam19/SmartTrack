'use client';

import { Suspense, useEffect, useState, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import Sidebar from '../../components/Sidebar';
import BottomNav from '../../components/BottomNav';
import AppLayout from '../../components/AppLayout';
import { getAccessToken, getCurrentUser, getStoredUser, fetchWithAuth } from '../../lib/authApi';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1');

const SUBJECT_PROGRESS = [
  'Core Mathematics',
  'English Language',
  'Integrated Science',
  'Social Studies',
] as const;

type LevelId = 1 | 2 | 3;

type LevelMeta = {
  label: string;
  difficulty: string;
  timer: number;
  xpMax: number;
};

const LEVEL_META: Record<LevelId, LevelMeta> = {
  1: { label: 'Level 1', difficulty: 'Easy', timer: 120, xpMax: 30 },
  2: { label: 'Level 2', difficulty: 'Moderate', timer: 120, xpMax: 30 },
  3: { label: 'Level 3', difficulty: 'Difficult', timer: 180, xpMax: 30 },
};

type AtlasSession = {
  session_id: string;
  current_subject: string;
  current_subject_index: number;
  questions: any[];
  timer_seconds?: number;
  challenge_level: LevelId;
  total_xp?: number;
};

type AtlasUser = {
  streak?: number;
  shs_level?: string;
};

type AtlasSummary = {
  weak_topics?: string[];
  subject_performance?: Array<{ subject: string; correct: number; total: number; accuracy: number; xp: number }>;
  total_xp?: number;
  accuracy?: number;
  strongest_subject?: string;
  weakest_subject?: string;
};

function AtlasChallengeContent() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<AtlasUser | null>(null);

  // Session state
  const [session, setSession] = useState<AtlasSession | null>(null);
  const [questions, setQuestions] = useState<any[]>([]);
  const [subject, setSubject] = useState<string>('');
  const [subjectIndex, setSubjectIndex] = useState<number>(0);
  const [questionIndex, setQuestionIndex] = useState<number>(0);
  const [remaining, setRemaining] = useState<number>(0);
  const timerRef = useRef<number | null>(null);
  const startTimeRef = useRef<number>(0);

  const [totalXp, setTotalXp] = useState(0);
  const [feedback, setFeedback] = useState<any | null>(null);
  const [showSubjectSummary, setShowSubjectSummary] = useState(false);
  const [showSubjectIntro, setShowSubjectIntro] = useState(false);
  const [showLevelComplete, setShowLevelComplete] = useState(false);
  const [pendingContinuationAction, setPendingContinuationAction] = useState<'continueSubject' | 'continueLevel' | null>(null);
  const [isLoadingLevel, setIsLoadingLevel] = useState(false);
  const [loadingStage, setLoadingStage] = useState<string | null>(null);
  const [finalSummary, setFinalSummary] = useState<AtlasSummary | null>(null);
  const [sessionSummary, setSessionSummary] = useState<AtlasSummary | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // ── Per-question interaction state (kept unconditionally for Rules of Hooks) ─
  const [matchingPairs, setMatchingPairs] = useState<Record<string, string>>({});
  const [selectedLeft, setSelectedLeft] = useState<string | null>(null);
  const [orderItems, setOrderItems] = useState<string[]>([]);

  // Must be defined before early return for the useEffect below
  const currentQuestionForEffect = questions[questionIndex] || null;
  const qtypeForEffect = currentQuestionForEffect?.question_type || 'mcq';

  // Reset per-question UI state when question changes
  useEffect(() => {
    if (!currentQuestionForEffect) return;
    setMatchingPairs({});
    setSelectedLeft(null);
    if (currentQuestionForEffect.items && qtypeForEffect === 'order') {
      setOrderItems([...currentQuestionForEffect.items]);
    }
  }, [questionIndex, session?.session_id]);

  const searchParams = useSearchParams();

  useEffect(() => {
    const load = async () => {
      try {
        if (!getAccessToken()) { router.push('/login'); return; }
        const cached = getStoredUser(); if (cached) setUser(cached as any);
        const fresh = await getCurrentUser(); setUser(fresh as any);
      } catch {
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };
    load();
    return () => { if (timerRef.current) window.clearInterval(timerRef.current); };
  }, [router]);

  useEffect(() => {
    const autostart = searchParams.get('autostart');
    if (autostart === '1' && !session && !loading) {
      startChallenge(1);
    }
  }, [searchParams, session, loading]);

  // Start a new challenge session
  const startChallenge = async (level = 1) => {
    setLoading(true);
    setErrorMessage(null);
    setShowSubjectIntro(false);
    setShowSubjectSummary(false);
    setShowLevelComplete(false);
    setFinalSummary(null);
    try {
      setLoadingStage('Preparing Core Mathematics');
      const res = await fetchWithAuth(`${API_BASE}/challenge-hub/start`, {
        method: 'POST',
        body: JSON.stringify({ challenge_level: level }),
      });
      if (!res.ok) throw new Error('Failed to start');
      const data = await res.json();
      const s = data.session as AtlasSession;
      if (!s || !s.questions || s.questions.length === 0) {
        throw new Error('Failed to generate challenge questions.');
      }
      setSession(s);
      setSubject(s.current_subject);
      setSubjectIndex(s.current_subject_index || 0);
      setQuestions(s.questions || []);
      setQuestionIndex(0);
      setRemaining(s.timer_seconds ?? LEVEL_META[level as LevelId].timer);
      setTotalXp(0);
      setPendingContinuationAction(null);
      setShowSubjectIntro(true);
    } catch (e: any) {
      console.error(e);
      const detail = e?.message || 'Could not start challenge. Ensure backend is running.';
      setErrorMessage(
        detail.includes('Failed to start') || detail.includes('generate challenge')
          ? 'Unable to generate today’s challenge at the moment. Please try again in a few moments.'
          : detail
      );
    } finally {
      setLoading(false);
      setLoadingStage(null);
    }
  };

  const startTimer = (seconds: number) => {
    if (timerRef.current) window.clearInterval(timerRef.current);
    setRemaining(seconds);
    startTimeRef.current = Date.now();
    timerRef.current = window.setInterval(() => {
      setRemaining((r) => {
        if (r <= 1) {
          if (timerRef.current) window.clearInterval(timerRef.current);
          // Auto-submit empty answer
          handleSubmitAnswer('');
          return 0;
        }
        return r - 1;
      });
    }, 1000) as unknown as number;
  };

  const handleSubmitAnswer = async (userAnswer: string) => {
    if (!session) return;
    const currentSubject = subject;
    const qi = questionIndex;
    const timeTaken = (Date.now() - startTimeRef.current) / 1000;
    // Stop timer
    if (timerRef.current) window.clearInterval(timerRef.current);

    try {
      const res = await fetchWithAuth(`${API_BASE}/challenge-hub/submit`, {
        method: 'POST',
        body: JSON.stringify({
          session_id: session.session_id,
          subject: currentSubject,
          question_index: qi,
          user_answer: (userAnswer || '').toString(),
          time_taken_seconds: timeTaken,
        }),
      });
      if (!res.ok) throw new Error('Submit failed');
      const data = await res.json();
      const r = data.result;
      setFeedback(r);
      setTotalXp(r.total_xp || 0);

      // Show explanation for 2s then move on
      setTimeout(async () => {
        if (r.session_complete) {
          // Finalise session
          await completeSessionAndFetchSummary();
          return;
        }

        if (r.level_complete) {
          await fetchSessionSummary();
          setPendingContinuationAction('continueLevel');
          setShowLevelComplete(true);
          setShowSubjectSummary(false);
          return;
        }

        if (r.subject_complete) {
          await fetchSessionSummary();
          setPendingContinuationAction('continueSubject');
          setShowSubjectSummary(true);
          return;
        }

        // Advance to next question locally
        setQuestionIndex((q) => q + 1);
        // restart timer
        startTimer(session.timer_seconds || 120);
      }, 1500);

    } catch (e) {
      console.error(e);
      alert('Failed to submit answer');
    }
  };

  const fetchCurrentSubject = async () => {
    if (!session) return;
    try {
      const res = await fetchWithAuth(`${API_BASE}/challenge-hub/questions`, {
        method: 'POST',
        body: JSON.stringify({ session_id: session.session_id }),
      });
      if (!res.ok) throw new Error('No subject');
      const data = await res.json();
      const d = data.data;
      setSubject(d.subject);
      setSubjectIndex(d.subject_index);
      setQuestions(d.questions || []);
      setQuestionIndex(0);
      setShowSubjectSummary(false);
      setFeedback(null);
      setPendingContinuationAction(null);
      setShowSubjectIntro(true);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchSessionSummary = async () => {
    if (!session) return;
    try {
      const params = new URLSearchParams({ session_id: session.session_id });
      const res = await fetchWithAuth(`${API_BASE}/challenge-hub/summary?${params.toString()}`, {
        method: 'GET',
      });
      if (!res.ok) throw new Error('Summary fetch failed');
      const data = await res.json();
      setSessionSummary(data.summary || null);
    } catch (e) {
      console.error('Failed to fetch session summary', e);
    }
  };

  const startCurrentSubject = () => {
    if (!session) return;
    setShowSubjectIntro(false);
    setShowSubjectSummary(false);
    setShowLevelComplete(false);
    setFeedback(null);
    const timer = session.timer_seconds ?? LEVEL_META[session.challenge_level].timer;
    startTimer(timer);
  };

  const continueLevel = async () => {
    if (!session) return;
    setIsLoadingLevel(true);
    setLoadingStage('Preparing next challenge level');
    setErrorMessage(null);
    try {
      const res = await fetchWithAuth(`${API_BASE}/challenge-hub/continue`, {
        method: 'POST',
        body: JSON.stringify({ session_id: session.session_id }),
      });

      if (!res.ok) throw new Error('Failed to continue level');
      const data = await res.json();
      const s = data.session as AtlasSession;
      if (!s || !s.questions || s.questions.length === 0) {
        throw new Error('Failed to generate next level questions.');
      }

      setSession(s);
      setSubject(s.current_subject);
      setSubjectIndex(s.current_subject_index || 0);
      setQuestions(s.questions || []);
      setQuestionIndex(0);
      setRemaining(s.timer_seconds ?? LEVEL_META[s.challenge_level].timer);
      setTotalXp(s.total_xp || totalXp);
      setPendingContinuationAction(null);
      setShowLevelComplete(false);
      setShowSubjectIntro(true);
    } catch (e: any) {
      console.error(e);
      setErrorMessage('Unable to continue to the next level. Please try again.');
    } finally {
      setIsLoadingLevel(false);
      setLoadingStage(null);
    }
  };

  const handleContinueFromSummary = () => {
    if (pendingContinuationAction === 'continueLevel') {
      continueLevel();
    } else {
      fetchCurrentSubject();
    }
  };

  const completeSessionAndFetchSummary = async () => {
    if (!session) return;
    try {
      const res = await fetchWithAuth(`${API_BASE}/challenge-hub/complete`, {
        method: 'POST',
        body: JSON.stringify({ session_id: session.session_id }),
      });
      if (!res.ok) throw new Error('Complete failed');
      const data = await res.json();
      setFinalSummary(data.summary || null);
    } catch (e) {
      console.error(e);
      alert('Failed to complete session');
    }
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center gap-5"
          >
            <div className="w-12 h-12 border-[3px] border-[#2563EB] border-t-transparent rounded-full animate-spin" />
            {loadingStage && (
              <motion.p
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-sm text-[#64748B]"
              >
                {loadingStage}…
              </motion.p>
            )}
          </motion.div>
        </div>
      </AppLayout>
    );
  }

  // If no session yet, show welcome/start page
  if (!session) {
    return (
      <AppLayout>
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex-1 lg:pb-0 pb-24">
            <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center py-12"
              >
                {/* Logo icon */}
                <div className="w-16 h-16 bg-gradient-to-br from-[#2563EB] to-[#7C3AED] rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-[#2563EB]/20">
                  <span className="text-2xl font-bold text-white">A</span>
                </div>

                <h1 className="text-3xl sm:text-4xl font-bold text-[#1E293B] mb-4">
                  Welcome to Today&apos;s Challenge
                </h1>

                <p className="text-[#475569] mb-3 leading-relaxed max-w-lg mx-auto">
                  Today&apos;s challenge consists of the{" "}
                  <strong className="text-[#1E293B]">four Core Subjects</strong>.
                </p>

                <p className="text-[#475569] mb-3 leading-relaxed max-w-lg mx-auto">
                  Strong performance in the Core Subjects builds a solid academic{" "}
                  foundation for <strong className="text-[#1E293B]">WASSCE</strong> and{" "}
                  <strong className="text-[#1E293B]">university admission</strong>.
                </p>

                <p className="text-[#475569] mb-6 leading-relaxed max-w-lg mx-auto">
                  Atlas will use today&apos;s performance to personalise future{" "}
                  learning recommendations.
                </p>

                {errorMessage && (
                  <div className="mb-6 max-w-md mx-auto rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {errorMessage}
                  </div>
                )}

                <div className="flex flex-col items-center gap-4 mb-6">
                  <motion.button
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={() => startChallenge(1)}
                    className="px-10 py-4 bg-gradient-to-r from-[#2563EB] to-[#1D4ED8] text-white font-bold text-lg rounded-xl hover:from-[#3B82F6] hover:to-[#2563EB] shadow-lg shadow-[#2563EB]/25 hover:shadow-xl hover:shadow-[#2563EB]/30 transition-all duration-200"
                  >
                    Start Challenge
                  </motion.button>

                  <div className="flex items-center gap-4 text-sm text-[#64748B]">
                    <span className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-[#2563EB]"></span>
                      4 Core Subjects
                    </span>
                    <span className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-[#059669]"></span>
                      24 Questions
                    </span>
                    <span className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-[#D97706]"></span>
                      3 Levels
                    </span>
                  </div>
                </div>

                <p className="text-sm text-[#64748B]">Good luck!</p>
              </motion.div>
            </main>
          </div>
          <BottomNav />
        </div>
      </AppLayout>
    );
  }

  // If final summary exists, show final screen
  if (showSubjectIntro && session) {
    const levelMeta = LEVEL_META[session.challenge_level] || { label: `Level ${session.challenge_level}`, difficulty: 'Unknown', timer: session.timer_seconds ?? 120, xpMax: 0 };
    return (
      <AppLayout>
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex-1 lg:pb-0 pb-24">
            <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10">
              <div className="bg-white border rounded-3xl p-8 shadow-sm">
                <div className="text-sm uppercase tracking-[0.2em] text-blue-600 mb-3">{levelMeta.label}</div>
                <h1 className="text-3xl font-bold mb-3">Get ready for {subject}</h1>
                <p className="text-gray-600 mb-4">You are now doing {levelMeta.difficulty} questions for {subject}. Answer 6 questions carefully and earn XP for every correct response.</p>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                  <div className="p-4 bg-gray-50 rounded-2xl text-center">
                    <div className="text-sm text-gray-500">Questions</div>
                    <div className="text-xl font-bold">6</div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-2xl text-center">
                    <div className="text-sm text-gray-500">Timer</div>
                    <div className="text-xl font-bold">{session.timer_seconds}s</div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-2xl text-center">
                    <div className="text-sm text-gray-500">Current XP</div>
                    <div className="text-xl font-bold">{totalXp}</div>
                  </div>
                </div>
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <button onClick={startCurrentSubject} className="px-6 py-3 bg-blue-600 text-white rounded-xl">Start {subject}</button>
                  <button onClick={() => { setShowSubjectIntro(false); startTimer(session.timer_seconds ?? 120); }} className="px-6 py-3 border border-gray-200 rounded-xl">Skip intro</button>
                </div>
              </div>
            </main>
          </div>
          <BottomNav />
        </div>
      </AppLayout>
    );
  }

  if (showLevelComplete && session) {
    const levelLabel = `Level ${session.challenge_level} Complete`;
    return (
      <AppLayout>
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex-1 lg:pb-0 pb-24">
            <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10">
              <div className="bg-white border rounded-2xl p-6">
                <h2 className="text-2xl font-bold mb-2">{levelLabel}</h2>
                <p className="text-gray-600 mb-4">Nice work — you completed all 4 subjects for this level.</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-500">Total XP so far</div>
                    <div className="text-3xl font-bold">{totalXp}</div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-500">Next level</div>
                    <div className="text-3xl font-bold">Level {session.challenge_level + 1}</div>
                  </div>
                </div>
                {errorMessage && (
                  <div className="mb-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {errorMessage}
                  </div>
                )}
                <div className="flex flex-col gap-3 sm:flex-row sm:justify-between">
                  <button onClick={() => router.push('/challenges/intro')} className="px-6 py-3 border border-gray-200 rounded-xl">Exit challenge</button>
                  <button onClick={continueLevel} disabled={isLoadingLevel} className="px-6 py-3 bg-blue-600 text-white rounded-xl">
                    {isLoadingLevel ? 'Preparing next level…' : 'Continue to Level ' + (session.challenge_level + 1)}
                  </button>
                </div>
              </div>
            </main>
          </div>
          <BottomNav />
        </div>
      </AppLayout>
    );
  }

  if (finalSummary) {
    const recLessons = (finalSummary?.weak_topics ?? []).map((t: string) => ({
      topic: t,
      learningLink: `/learning?topic=${encodeURIComponent(t)}`,
      revisionLink: `/revision?topic=${encodeURIComponent(t)}`,
    }));

    return (
      <AppLayout>
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex-1 lg:pb-0 pb-24">
            <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10">
              <div className="bg-white border rounded-2xl p-6">
                <h1 className="text-2xl font-bold mb-2">Challenge Summary</h1>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
                  <div className="p-4 bg-gray-50 rounded-lg text-center">
                    <div className="text-sm text-gray-500">Total XP</div>
                    <div className="text-xl font-bold">{finalSummary.total_xp}</div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg text-center">
                    <div className="text-sm text-gray-500">Accuracy</div>
                    <div className="text-xl font-bold">{finalSummary.accuracy}%</div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg text-center">
                    <div className="text-sm text-gray-500">Daily Streak</div>
                    <div className="text-xl font-bold">{user?.streak ?? 0} days</div>
                  </div>
                </div>

                <div className="mb-4">
                  <h3 className="text-lg font-semibold">Performance by Subject</h3>
                  <div className="mt-2 space-y-2">
                    {finalSummary.subject_performance?.map((s: any) => (
                      <div key={s.subject} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                        <div>
                          <div className="font-medium">{s.subject}</div>
                          <div className="text-xs text-gray-500">{s.correct} correct / {s.total}</div>
                        </div>
                        <div className="text-sm font-semibold">{s.accuracy}%</div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mb-4">
                  <h3 className="text-lg font-semibold">Strongest Subject</h3>
                  <p className="text-sm text-gray-700">{finalSummary.strongest_subject || '—'}</p>
                </div>

                <div className="mb-4">
                  <h3 className="text-lg font-semibold">Weakest Subject</h3>
                  <p className="text-sm text-gray-700">{finalSummary.weakest_subject || '—'}</p>
                </div>

                <div className="mb-4">
                  <h3 className="text-lg font-semibold">Topics Requiring Improvement</h3>
                  <p className="text-sm text-gray-700">{(finalSummary.weak_topics && finalSummary.weak_topics.join(', ')) || 'None'}</p>
                </div>

                <div className="mb-4">
                  <h3 className="text-lg font-semibold">Recommended Lessons (Learning Center)</h3>
                  <div className="mt-2 space-y-2">
                    {recLessons.length === 0 && <div className="text-sm text-gray-500">No recommendations — great job!</div>}
                    {recLessons.map((r: { topic: string; learningLink: string; revisionLink: string }) => (
                      <div key={r.topic} className="flex items-center justify-between bg-white p-3 rounded-lg border">
                        <div className="text-sm">{r.topic}</div>
                        <div className="flex gap-2">
                          <a href={r.learningLink} className="text-sm text-blue-600 underline">Learning</a>
                          {/* Show revision link only for SHS 3 students */}
                          {user?.shs_level === 'SHS 3' && (
                            <a href={r.revisionLink} className="text-sm text-purple-600 underline">SHS3 Revision</a>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-6 flex gap-3">
                  <button onClick={() => router.push('/dashboard')} className="px-6 py-3 bg-blue-600 text-white rounded-xl">Go to Dashboard</button>
                  <button onClick={() => router.push('/challenges/leaderboard')} className="px-6 py-3 border border-gray-200 rounded-xl">Leaderboard</button>
                  <button onClick={() => router.push('/learning')} className="px-6 py-3 border border-gray-200 rounded-xl">Explore Learning Center</button>
                </div>
              </div>
            </main>
          </div>
          <BottomNav />
        </div>
      </AppLayout>
    );
  }

  // If showing subject summary
  if (showSubjectSummary) {
    const perf = sessionSummary?.subject_performance?.find((s: any) => s.subject === subject) || null;
    return (
      <AppLayout>
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex-1 lg:pb-0 pb-24">
            <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10">
              <div className="bg-white border rounded-xl p-6">
                <h2 className="text-xl font-bold mb-2">Subject Completed — {subject}</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-500">XP Earned</div>
                    <div className="text-2xl font-bold">{perf ? perf.xp : 0}</div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-500">Accuracy</div>
                    <div className="text-2xl font-bold">{perf ? `${perf.accuracy}%` : '0%'}</div>
                  </div>
                </div>

                <div className="mb-4">
                  <div className="text-sm text-gray-500">Correct Answers</div>
                  <div className="text-lg font-semibold">{perf ? perf.correct : 0} / {perf ? perf.total : 6}</div>
                </div>

                <div className="mb-4">
                  <div className="text-sm text-gray-500">Strong Topics</div>
                  <div className="text-sm text-gray-700">{sessionSummary?.strongest_subject || '—'}</div>
                </div>

                <div className="mb-4">
                  <div className="text-sm text-gray-500">Weak Topics</div>
                  <div className="text-sm text-gray-700">{(sessionSummary?.weak_topics && sessionSummary.weak_topics.join(', ')) || '—'}</div>
                </div>

                <div className="mt-6 text-center">
                  <button onClick={handleContinueFromSummary} className="px-6 py-3 bg-blue-600 text-white rounded-xl">
                    {pendingContinuationAction === 'continueLevel' ? 'Continue to next level →' : 'Continue →'}
                  </button>
                </div>
              </div>
            </main>
          </div>
          <BottomNav />
        </div>
      </AppLayout>
    );
  }

  const currentQ = questions[questionIndex] || null;
  if (!currentQ) {
    return (
      <AppLayout>
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex-1 lg:pb-0 pb-24">
            <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10">
              <div className="flex items-center justify-center py-20">
                <div className="flex flex-col items-center gap-4">
                  <div className="w-10 h-10 border-[3px] border-[#2563EB] border-t-transparent rounded-full animate-spin" />
                  <p className="text-sm text-[#64748B]">Loading question…</p>
                </div>
              </div>
            </main>
          </div>
          <BottomNav />
        </div>
      </AppLayout>
    );
  }

  const qtype = currentQ.question_type || 'mcq';

  const QUESTION_TYPE_BADGES: Record<string, { label: string; color: string; bg: string }> = {
    mcq: { label: 'Multiple Choice', color: 'text-blue-700', bg: 'bg-blue-50' },
    'fill-blank': { label: 'Fill in the Blank', color: 'text-emerald-700', bg: 'bg-emerald-50' },
    'short-answer': { label: 'Short Answer', color: 'text-purple-700', bg: 'bg-purple-50' },
    'true-false': { label: 'True or False', color: 'text-amber-700', bg: 'bg-amber-50' },
    matching: { label: 'Matching', color: 'text-rose-700', bg: 'bg-rose-50' },
    order: { label: 'Arrange in Order', color: 'text-cyan-700', bg: 'bg-cyan-50' },
    scenario: { label: 'Scenario', color: 'text-indigo-700', bg: 'bg-indigo-50' },
  };

  const badge = QUESTION_TYPE_BADGES[qtype] || { label: qtype, color: 'text-gray-700', bg: 'bg-gray-50' };

  const getQuestionTypeIcon = (t: string) => {
    const icons: Record<string, string> = {
      mcq: '○',
      'fill-blank': '___',
      'short-answer': 'Aa',
      'true-false': '✓✗',
      matching: '⇄',
      order: '⇅',
      scenario: '📖',
    };
    return icons[t] || '?';
  };

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-24">
          <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10">
            {/* Header: Subject + Timer */}
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="text-sm text-[#64748B]">Subject</div>
                <div className="text-lg font-semibold text-[#1E293B]">{subject}</div>
              </div>
              <div className="text-right">
                <div className="text-sm text-[#64748B]">Time left</div>
                <div className="text-lg font-mono font-bold text-[#1E293B]">{remaining}s</div>
              </div>
            </div>

            {/* Overall Progress Bar */}
            <div className="mb-5">
              <div className="flex items-center justify-between text-xs text-[#64748B] mb-1.5">
                <span>Challenge Progress</span>
                <span>{Math.min(Math.round(((subjectIndex * 6 + questionIndex) / 24) * 100), 100)}%</span>
              </div>
              <div className="w-full bg-[#E2E8F0] rounded-full h-2.5 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(Math.round(((subjectIndex * 6 + questionIndex) / 24) * 100), 100)}%` }}
                  transition={{ duration: 0.5, ease: "easeOut" }}
                  className="h-full rounded-full bg-gradient-to-r from-[#2563EB] to-[#7C3AED]"
                />
              </div>
            </div>

            <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 mb-4 shadow-sm">
              {/* Question header with type badge */}
              <div className="flex items-center justify-between mb-3">
                <div className="text-sm text-gray-500">Question {questionIndex + 1} of {questions.length}</div>
                <div className={`text-xs font-medium px-3 py-1 rounded-full ${badge.bg} ${badge.color} flex items-center gap-1.5`}>
                  <span className="text-sm font-mono">{getQuestionTypeIcon(qtype)}</span>
                  {badge.label}
                </div>
              </div>

              {/* Question text */}
              <h3 className="text-base md:text-lg font-medium text-[#1E293B] mb-5 leading-relaxed">{currentQ.question}</h3>

              {/* ── Render by type ──────────────────────────────────────── */}
              {qtype === 'mcq' || qtype === 'scenario' ? (
                /* MCQ / Scenario — radio-button style options */
                <div className="space-y-3">
                  {currentQ.options && typeof currentQ.options === 'object' ? (
                    Object.entries(currentQ.options).map(([k, v]: any) => (
                      <motion.button
                        key={k}
                        whileHover={{ scale: 1.01 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => handleSubmitAnswer(k)}
                        disabled={!!feedback}
                        className="w-full text-left px-5 py-4 bg-white border-2 border-[#E2E8F0] rounded-xl hover:border-[#2563EB] hover:bg-[#F8FAFF] transition-all duration-150 disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-4 group"
                      >
                        <span className="w-8 h-8 rounded-full border-2 border-[#CBD5E1] flex items-center justify-center text-sm font-bold text-[#64748B] group-hover:border-[#2563EB] group-hover:text-[#2563EB] transition-colors">{k}</span>
                        <span className="text-[#334155] group-hover:text-[#1E293B]">{v}</span>
                      </motion.button>
                    ))
                  ) : (
                    <p className="text-sm text-red-500">No options available for this question.</p>
                  )}
                </div>
              ) : qtype === 'fill-blank' ? (
                /* Fill in the Blank — text input */
                <div className="space-y-4">
                  <div className="relative">
                    <input
                      id={`fill_blank_${questionIndex}`}
                      type="text"
                      placeholder="Type your answer here…"
                      className="w-full px-4 py-3.5 border-2 border-[#E2E8F0] rounded-xl focus:border-[#2563EB] focus:ring-2 focus:ring-[#2563EB]/20 outline-none transition-all text-lg"
                      autoFocus
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          const el = document.getElementById(`fill_blank_${questionIndex}`) as HTMLInputElement | null;
                          handleSubmitAnswer(el?.value || '');
                        }
                      }}
                    />
                  </div>
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => {
                      const el = document.getElementById(`fill_blank_${questionIndex}`) as HTMLInputElement | null;
                      handleSubmitAnswer(el?.value || '');
                    }}
                    disabled={!!feedback}
                    className="px-6 py-3 bg-[#2563EB] text-white font-semibold rounded-xl hover:bg-[#1D4ED8] transition-colors disabled:opacity-50"
                  >
                    Submit Answer
                  </motion.button>
                </div>
              ) : qtype === 'short-answer' ? (
                /* Short Answer — textarea */
                <div className="space-y-4">
                  <textarea
                    id={`short_answer_${questionIndex}`}
                    placeholder="Type your answer in one sentence…"
                    className="w-full px-4 py-3.5 border-2 border-[#E2E8F0] rounded-xl focus:border-[#2563EB] focus:ring-2 focus:ring-[#2563EB]/20 outline-none transition-all min-h-[100px] resize-none"
                    autoFocus
                  />
                  <div className="flex gap-3">
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => {
                        const el = document.getElementById(`short_answer_${questionIndex}`) as HTMLTextAreaElement | null;
                        handleSubmitAnswer(el?.value || '');
                      }}
                      disabled={!!feedback}
                      className="px-6 py-3 bg-[#2563EB] text-white font-semibold rounded-xl hover:bg-[#1D4ED8] transition-colors disabled:opacity-50"
                    >
                      Submit Answer
                    </motion.button>
                  </div>
                </div>
              ) : qtype === 'true-false' ? (
                /* True or False — two large buttons */
                <div className="grid grid-cols-2 gap-4">
                  <motion.button
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleSubmitAnswer('A')}
                    disabled={!!feedback}
                    className="flex flex-col items-center gap-3 px-6 py-8 border-2 border-[#E2E8F0] rounded-2xl bg-white hover:border-emerald-400 hover:bg-emerald-50 transition-all duration-150 disabled:opacity-50"
                  >
                    <span className="text-3xl">✓</span>
                    <span className="text-lg font-semibold text-[#1E293B]">True</span>
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleSubmitAnswer('B')}
                    disabled={!!feedback}
                    className="flex flex-col items-center gap-3 px-6 py-8 border-2 border-[#E2E8F0] rounded-2xl bg-white hover:border-red-400 hover:bg-red-50 transition-all duration-150 disabled:opacity-50"
                  >
                    <span className="text-3xl">✗</span>
                    <span className="text-lg font-semibold text-[#1E293B]">False</span>
                  </motion.button>
                </div>
              ) : qtype === 'matching' ? (
                /* Matching — two columns, create pairs */
                <div className="space-y-4">
                  <p className="text-sm text-[#64748B]">Click a left item, then click a right item to create a match.</p>
                  <div className="grid grid-cols-2 gap-4">
                    {/* Left column */}
                    <div className="space-y-2">
                      {(currentQ.left_items || []).map((item: string, idx: number) => {
                        const matchedRight = matchingPairs[String(idx)];
                        const isSelected = selectedLeft === String(idx);
                        return (
                          <motion.button
                            key={`left_${idx}`}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => {
                              if (feedback) return;
                              setSelectedLeft(isSelected ? null : String(idx));
                            }}
                            className={`w-full text-left px-4 py-3 rounded-xl border-2 text-sm transition-all ${
                              matchedRight
                                ? 'border-emerald-300 bg-emerald-50'
                                : isSelected
                                ? 'border-[#2563EB] bg-[#F8FAFF]'
                                : 'border-[#E2E8F0] bg-white hover:border-[#94A3B8]'
                            } disabled:opacity-50`}
                            disabled={!!feedback}
                          >
                            <span className="font-semibold text-xs text-[#64748B] mr-2">{idx + 1}.</span>
                            {item}
                            {matchedRight && (
                              <span className="float-right text-xs text-emerald-600 font-medium">
                                → {parseInt(matchedRight) + 1}
                              </span>
                            )}
                          </motion.button>
                        );
                      })}
                    </div>
                    {/* Right column */}
                    <div className="space-y-2">
                      {(currentQ.right_items || []).map((item: string, idx: number) => {
                        const isMatched = Object.values(matchingPairs).includes(String(idx));
                        const matchedBy = Object.entries(matchingPairs).find(([, v]) => v === String(idx))?.[0];
                        return (
                          <motion.button
                            key={`right_${idx}`}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => {
                              if (feedback || !selectedLeft || isMatched) return;
                              setMatchingPairs((prev) => ({ ...prev, [selectedLeft]: String(idx) }));
                              setSelectedLeft(null);
                            }}
                            className={`w-full text-left px-4 py-3 rounded-xl border-2 text-sm transition-all ${
                              isMatched
                                ? 'border-emerald-300 bg-emerald-50 opacity-60'
                                : selectedLeft && !isMatched
                                ? 'border-[#2563EB] bg-[#F8FAFF] cursor-pointer hover:border-[#1D4ED8]'
                                : 'border-[#E2E8F0] bg-white'
                            } disabled:opacity-50`}
                            disabled={!!feedback || !selectedLeft || isMatched}
                          >
                            {matchedBy !== undefined && (
                              <span className="font-semibold text-xs text-emerald-600 mr-2">
                                {parseInt(matchedBy) + 1} →
                              </span>
                            )}
                            {item}
                          </motion.button>
                        );
                      })}
                    </div>
                  </div>
                  {/* Submit matching */}
                  <div className="flex gap-3 pt-2">
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => {
                        handleSubmitAnswer(JSON.stringify(matchingPairs));
                      }}
                      disabled={!!feedback || Object.keys(matchingPairs).length < (currentQ.left_items || []).length}
                      className="px-6 py-3 bg-[#2563EB] text-white font-semibold rounded-xl hover:bg-[#1D4ED8] transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                    >
                      Submit Matches ({Object.keys(matchingPairs).length}/{(currentQ.left_items || []).length})
                    </motion.button>
                    <button
                      onClick={() => { setMatchingPairs({}); setSelectedLeft(null); }}
                      disabled={!!feedback}
                      className="px-4 py-3 border border-[#E2E8F0] rounded-xl text-sm text-[#64748B] hover:bg-gray-50 transition-colors disabled:opacity-40"
                    >
                      Reset
                    </button>
                  </div>
                </div>
              ) : qtype === 'order' ? (
                /* Arrange in Order — up/down buttons */
                <div className="space-y-3">
                  <p className="text-sm text-[#64748B]">Use the arrows to arrange the items in the correct order.</p>
                  <div className="space-y-2">
                    {orderItems.map((item: string, idx: number) => (
                      <div
                        key={`order_${idx}_${item}`}
                        className="flex items-center gap-3 px-4 py-3 bg-white border-2 border-[#E2E8F0] rounded-xl"
                      >
                        <span className="w-7 h-7 rounded-full bg-[#2563EB] text-white text-xs font-bold flex items-center justify-center flex-shrink-0">
                          {idx + 1}
                        </span>
                        <span className="flex-1 text-sm text-[#334155]">{item}</span>
                        <div className="flex flex-col gap-1">
                          <button
                            onClick={() => {
                              if (idx === 0) return;
                              const newOrder = [...orderItems];
                              [newOrder[idx - 1], newOrder[idx]] = [newOrder[idx], newOrder[idx - 1]];
                              setOrderItems(newOrder);
                            }}
                            disabled={idx === 0 || !!feedback}
                            className="w-8 h-7 flex items-center justify-center rounded-lg border border-[#E2E8F0] hover:bg-gray-50 text-[#64748B] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                            aria-label="Move up"
                          >
                            ↑
                          </button>
                          <button
                            onClick={() => {
                              if (idx === orderItems.length - 1) return;
                              const newOrder = [...orderItems];
                              [newOrder[idx], newOrder[idx + 1]] = [newOrder[idx + 1], newOrder[idx]];
                              setOrderItems(newOrder);
                            }}
                            disabled={idx === orderItems.length - 1 || !!feedback}
                            className="w-8 h-7 flex items-center justify-center rounded-lg border border-[#E2E8F0] hover:bg-gray-50 text-[#64748B] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                            aria-label="Move down"
                          >
                            ↓
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-3 pt-2">
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => {
                        // Find the current order by mapping original indices
                        const currentOrder = orderItems.map((item) => currentQ.items.indexOf(item));
                        handleSubmitAnswer(JSON.stringify(currentOrder));
                      }}
                      disabled={!!feedback}
                      className="px-6 py-3 bg-[#2563EB] text-white font-semibold rounded-xl hover:bg-[#1D4ED8] transition-colors disabled:opacity-50"
                    >
                      Submit Order
                    </motion.button>
                    <button
                      onClick={() => {
                        if (currentQ.items) setOrderItems([...currentQ.items]);
                      }}
                      disabled={!!feedback}
                      className="px-4 py-3 border border-[#E2E8F0] rounded-xl text-sm text-[#64748B] hover:bg-gray-50 transition-colors disabled:opacity-40"
                    >
                      Reset
                    </button>
                  </div>
                </div>
              ) : (
                /* Fallback: generic text input for unknown types */
                <div className="space-y-4">
                  <textarea
                    id={`generic_answer_${questionIndex}`}
                    placeholder="Type your answer…"
                    className="w-full px-4 py-3.5 border-2 border-[#E2E8F0] rounded-xl focus:border-[#2563EB] focus:ring-2 focus:ring-[#2563EB]/20 outline-none transition-all min-h-[80px] resize-none"
                    autoFocus
                  />
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => {
                      const el = document.getElementById(`generic_answer_${questionIndex}`) as HTMLTextAreaElement | null;
                      handleSubmitAnswer(el?.value || '');
                    }}
                    disabled={!!feedback}
                    className="px-6 py-3 bg-[#2563EB] text-white font-semibold rounded-xl hover:bg-[#1D4ED8] transition-colors disabled:opacity-50"
                  >
                    Submit Answer
                  </motion.button>
                </div>
              )}
            </div>

            {/* Feedback */}
            {feedback && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`p-5 rounded-xl border-2 mb-4 ${
                  feedback.is_correct ? 'bg-emerald-50 border-emerald-200' : 'bg-red-50 border-red-200'
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xl">{feedback.is_correct ? '✅' : '❌'}</span>
                  <span className="font-bold text-lg">{feedback.is_correct ? 'Correct!' : 'Incorrect'}</span>
                </div>
                <div className="text-sm font-medium mb-2">
                  {feedback.xp_earned > 0 ? `+${feedback.xp_earned} XP` : `${feedback.xp_earned} XP`}
                </div>
                <div className="text-sm text-[#475569] leading-relaxed">{feedback.explanation}</div>
              </motion.div>
            )}

            {/* Skip button */}
            {!feedback && (
              <div className="flex justify-center">
                <button
                  onClick={() => handleSubmitAnswer('')}
                  className="px-6 py-2.5 border-2 border-[#E2E8F0] rounded-xl text-sm text-[#64748B] hover:bg-gray-50 hover:border-[#CBD5E1] transition-all"
                >
                  Skip Question
                </button>
              </div>
            )}
          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}

export default function AtlasChallengePage() {
  return (
    <Suspense fallback={
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="w-8 h-8 border-2 border-[#2563EB] border-t-transparent rounded-full animate-spin" />
        </div>
      </AppLayout>
    }>
      <AtlasChallengeContent />
    </Suspense>
  );
}
