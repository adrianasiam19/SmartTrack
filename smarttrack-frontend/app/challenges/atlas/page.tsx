'use client';

import { Suspense, useCallback, useEffect, useRef, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import Sidebar from '../../components/Sidebar';
import BottomNav from '../../components/BottomNav';
import AppLayout from '../../components/AppLayout';
import { getAccessToken, getCurrentUser, getStoredUser, fetchWithAuth } from '../../lib/authApi';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

type LevelId = 1 | 2 | 3;

type LevelMeta = {
  label: string;
  difficulty: string;
  timer: number;
  xpMax: number;
};

const LEVEL_META: Record<LevelId, LevelMeta> = {
  1: { label: 'Level 1', difficulty: 'Easy', timer: 180, xpMax: 30 },
  2: { label: 'Level 2', difficulty: 'Moderate', timer: 180, xpMax: 30 },
  3: { label: 'Level 3', difficulty: 'Difficult', timer: 240, xpMax: 30 },
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
  subject_performance?: Array<{
    subject: string;
    correct: number;
    total: number;
    accuracy: number;
    xp: number;
  }>;
  total_xp?: number;
  accuracy?: number;
  strongest_subject?: string;
  weakest_subject?: string;
};

type Screen =
  | 'auth'
  | 'welcome'
  | 'generating'
  | 'subject_intro'
  | 'question'
  | 'subject_summary'
  | 'level_complete'
  | 'final_summary';

const QUESTION_TYPE_BADGES: Record<string, { label: string; color: string; bg: string }> = {
  mcq: { label: 'Multiple Choice', color: 'text-blue-700', bg: 'bg-blue-50' },
  'fill-blank': { label: 'Fill in the Blank', color: 'text-emerald-700', bg: 'bg-emerald-50' },
  'short-answer': { label: 'Short Answer', color: 'text-purple-700', bg: 'bg-purple-50' },
  'true-false': { label: 'True or False', color: 'text-amber-700', bg: 'bg-amber-50' },
  matching: { label: 'Matching', color: 'text-rose-700', bg: 'bg-rose-50' },
  order: { label: 'Arrange in Order', color: 'text-cyan-700', bg: 'bg-cyan-50' },
  scenario: { label: 'Scenario', color: 'text-indigo-700', bg: 'bg-indigo-50' },
};

function LoadingScreen({ message }: { message: string }) {
  return (
    <AppLayout>
      <div className="flex items-center justify-center min-h-screen px-6">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col items-center gap-5 text-center max-w-md"
        >
          <div className="w-12 h-12 border-[3px] border-[#2563EB] border-t-transparent rounded-full animate-spin" />
          <div>
            <p className="text-base font-semibold text-[#1E293B] mb-1">{message}</p>
            <p className="text-sm text-[#64748B]">
              Atlas AI is preparing personalised WASSCE-style questions for you.
            </p>
          </div>
        </motion.div>
      </div>
    </AppLayout>
  );
}

function AtlasChallengeContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const autostart = searchParams.get('autostart') === '1';

  const [screen, setScreen] = useState<Screen>(autostart ? 'generating' : 'auth');
  const [loadingStage, setLoadingStage] = useState(
    autostart ? 'Atlas AI is generating personalised questions' : 'Loading your challenge',
  );
  const [user, setUser] = useState<AtlasUser | null>(null);

  const [session, setSession] = useState<AtlasSession | null>(null);
  const [questions, setQuestions] = useState<any[]>([]);
  const [subject, setSubject] = useState('');
  const [subjectIndex, setSubjectIndex] = useState(0);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [remaining, setRemaining] = useState(0);
  const [totalXp, setTotalXp] = useState(0);

  const [feedback, setFeedback] = useState<any | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [textAnswer, setTextAnswer] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [sessionSummary, setSessionSummary] = useState<AtlasSummary | null>(null);
  const [finalSummary, setFinalSummary] = useState<AtlasSummary | null>(null);
  const [pendingContinuationAction, setPendingContinuationAction] = useState<
    'continueSubject' | 'continueLevel' | null
  >(null);

  // Per-question interaction state
  const [matchingPairs, setMatchingPairs] = useState<Record<string, string>>({});
  const [selectedLeft, setSelectedLeft] = useState<string | null>(null);
  const [orderItems, setOrderItems] = useState<string[]>([]);

  // Refs — keep timer / submit callbacks stable and race-free
  const timerRef = useRef<number | null>(null);
  const startTimeRef = useRef(0);
  const isSubmittingRef = useRef(false);
  const feedbackRef = useRef(false);
  const hasAutostartedRef = useRef(false);
  const submitAnswerRef = useRef<(answer: string) => Promise<void>>(async () => {});

  const stopTimer = useCallback(() => {
    if (timerRef.current) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const startTimer = useCallback(
    (seconds: number) => {
      stopTimer();
      setRemaining(seconds);
      startTimeRef.current = Date.now();
      timerRef.current = window.setInterval(() => {
        setRemaining((r) => {
          if (r <= 1) {
            if (timerRef.current) {
              window.clearInterval(timerRef.current);
              timerRef.current = null;
            }
            // Only auto-submit unanswered questions
            if (!isSubmittingRef.current && !feedbackRef.current) {
              void submitAnswerRef.current('');
            }
            return 0;
          }
          return r - 1;
        });
      }, 1000) as unknown as number;
    },
    [stopTimer],
  );

  // Auth bootstrap
  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        if (!getAccessToken()) {
          router.push('/login');
          return;
        }
        const cached = getStoredUser();
        if (cached && !cancelled) setUser(cached as AtlasUser);
        const fresh = await getCurrentUser();
        if (!cancelled) setUser(fresh as AtlasUser);

        // If not autostarting, show welcome once auth is ready
        if (!autostart && !cancelled) {
          setScreen('welcome');
        }
      } catch {
        if (!cancelled) router.push('/login');
      }
    };
    load();
    return () => {
      cancelled = true;
      stopTimer();
    };
  }, [router, autostart, stopTimer]);

  // Reset per-question UI when the question changes
  useEffect(() => {
    const q = questions[questionIndex];
    setSelectedAnswer(null);
    setTextAnswer('');
    setMatchingPairs({});
    setSelectedLeft(null);
    setFeedback(null);
    feedbackRef.current = false;
    isSubmittingRef.current = false;
    setIsSubmitting(false);
    setErrorMessage(null);
    if (q?.items && q.question_type === 'order') {
      setOrderItems([...q.items]);
    } else {
      setOrderItems([]);
    }
  }, [questionIndex, session?.session_id, questions]);

  const fetchSessionSummary = useCallback(async (sessionId: string) => {
    try {
      const params = new URLSearchParams({ session_id: sessionId });
      const res = await fetchWithAuth(`${API_BASE}/challenge-hub/summary?${params.toString()}`, {
        method: 'GET',
      });
      if (!res.ok) throw new Error('Summary fetch failed');
      const data = await res.json();
      setSessionSummary(data.summary || null);
    } catch (e) {
      console.error('Failed to fetch session summary', e);
    }
  }, []);

  const completeSessionAndFetchSummary = useCallback(async (sessionId: string) => {
    try {
      const res = await fetchWithAuth(`${API_BASE}/challenge-hub/complete`, {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId }),
      });
      if (!res.ok) throw new Error('Complete failed');
      const data = await res.json();
      setFinalSummary(data.summary || null);
      setScreen('final_summary');
    } catch (e) {
      console.error(e);
      setErrorMessage('Failed to finalise the challenge session. Please try again.');
    }
  }, []);

  const handleSubmitAnswer = useCallback(
    async (userAnswer: string) => {
      if (!session) return;
      // Guard against double submit / timer race
      if (isSubmittingRef.current || feedbackRef.current) return;

      isSubmittingRef.current = true;
      setIsSubmitting(true);
      setErrorMessage(null);
      stopTimer();

      const currentSubject = subject;
      const qi = questionIndex;
      const timeTaken = Math.max(0, (Date.now() - startTimeRef.current) / 1000);
      const currentSession = session;

      try {
        const res = await fetchWithAuth(`${API_BASE}/challenge-hub/submit`, {
          method: 'POST',
          body: JSON.stringify({
            session_id: currentSession.session_id,
            subject: currentSubject,
            question_index: qi,
            user_answer: (userAnswer || '').toString(),
            time_taken_seconds: timeTaken,
          }),
        });

        if (!res.ok) {
          let detail = 'Submit failed';
          try {
            const errBody = await res.json();
            detail = errBody?.detail || `HTTP ${res.status}: ${res.statusText}`;
          } catch {
            detail = `HTTP ${res.status}: ${res.statusText}`;
          }
          throw new Error(detail);
        }

        const data = await res.json();
        const r = data.result;
        if (!r) throw new Error('Invalid response from server');

        feedbackRef.current = true;
        setFeedback(r);
        setTotalXp(r.total_xp || 0);

        // Show feedback briefly, then advance
        window.setTimeout(async () => {
          if (r.session_complete) {
            await completeSessionAndFetchSummary(currentSession.session_id);
            return;
          }

          if (r.level_complete) {
            await fetchSessionSummary(currentSession.session_id);
            setPendingContinuationAction('continueLevel');
            setScreen('level_complete');
            return;
          }

          if (r.subject_complete) {
            await fetchSessionSummary(currentSession.session_id);
            setPendingContinuationAction('continueSubject');
            setScreen('subject_summary');
            return;
          }

          // Next question
          setQuestionIndex((q) => q + 1);
          setScreen('question');
          startTimer(currentSession.timer_seconds || LEVEL_META[currentSession.challenge_level].timer);
        }, 1600);
      } catch (e: any) {
        console.error('Submit error:', e);
        setErrorMessage(e?.message || 'Failed to submit answer');
        // Allow retry
        isSubmittingRef.current = false;
        setIsSubmitting(false);
        feedbackRef.current = false;
        const timerSecs =
          currentSession.timer_seconds || LEVEL_META[currentSession.challenge_level].timer;
        startTimer(Math.max(timerSecs, 30));
      }
    },
    [
      session,
      subject,
      questionIndex,
      stopTimer,
      startTimer,
      completeSessionAndFetchSummary,
      fetchSessionSummary,
    ],
  );

  // Keep ref in sync so the timer callback always calls the latest submit
  useEffect(() => {
    submitAnswerRef.current = handleSubmitAnswer;
  }, [handleSubmitAnswer]);

  const startChallenge = useCallback(
    async (level: LevelId = 1) => {
      setScreen('generating');
      setLoadingStage('Atlas AI is generating personalised questions');
      setErrorMessage(null);
      setFinalSummary(null);
      setSessionSummary(null);
      setFeedback(null);
      feedbackRef.current = false;
      isSubmittingRef.current = false;
      stopTimer();

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
        setRemaining(s.timer_seconds ?? LEVEL_META[level].timer);
        setTotalXp(0);
        setPendingContinuationAction(null);
        setScreen('subject_intro');
      } catch (e: any) {
        console.error(e);
        const detail = e?.message || 'Could not start challenge. Ensure backend is running.';
        setErrorMessage(
          detail.includes('Failed to start') || detail.includes('generate challenge')
            ? 'Unable to generate today’s challenge at the moment. Please try again in a few moments.'
            : detail,
        );
        setScreen('welcome');
      }
    },
    [stopTimer],
  );

  // Autostart once auth is ready — never flash the welcome screen
  useEffect(() => {
    if (!autostart || hasAutostartedRef.current) return;
    if (!getAccessToken()) return;
    hasAutostartedRef.current = true;
    void startChallenge(1);
  }, [autostart, startChallenge]);

  const startCurrentSubject = () => {
    if (!session) return;
    setFeedback(null);
    feedbackRef.current = false;
    isSubmittingRef.current = false;
    setIsSubmitting(false);
    setSelectedAnswer(null);
    setTextAnswer('');
    setScreen('question');
    const timer = session.timer_seconds ?? LEVEL_META[session.challenge_level].timer;
    startTimer(timer);
  };

  const fetchCurrentSubject = async () => {
    if (!session) return;
    setScreen('generating');
    setLoadingStage(`Preparing ${session.current_subject || 'next subject'}`);
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
      setFeedback(null);
      feedbackRef.current = false;
      setPendingContinuationAction(null);
      setScreen('subject_intro');
    } catch (e) {
      console.error(e);
      setErrorMessage('Could not load the next subject. Please try again.');
      setScreen('subject_summary');
    }
  };

  const continueLevel = async () => {
    if (!session) return;
    setScreen('generating');
    setLoadingStage('Atlas AI is preparing the next challenge level');
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
      setScreen('subject_intro');
    } catch (e) {
      console.error(e);
      setErrorMessage('Unable to continue to the next level. Please try again.');
      setScreen('level_complete');
    }
  };

  const handleContinueFromSummary = () => {
    if (pendingContinuationAction === 'continueLevel') {
      void continueLevel();
    } else {
      void fetchCurrentSubject();
    }
  };

  const onSelectOption = (key: string) => {
    if (feedback || isSubmitting) return;
    setSelectedAnswer(key);
  };

  const onClickSubmit = () => {
    if (feedback || isSubmitting || !session) return;
    const q = questions[questionIndex];
    if (!q) return;
    const qtype = q.question_type || 'mcq';

    if (qtype === 'mcq' || qtype === 'scenario' || qtype === 'true-false') {
      if (!selectedAnswer) {
        setErrorMessage('Please select an answer before submitting.');
        return;
      }
      void handleSubmitAnswer(selectedAnswer);
      return;
    }

    if (qtype === 'fill-blank' || qtype === 'short-answer') {
      if (!textAnswer.trim()) {
        setErrorMessage('Please type an answer before submitting.');
        return;
      }
      void handleSubmitAnswer(textAnswer);
      return;
    }

    if (qtype === 'matching') {
      const needed = (q.left_items || []).length;
      if (Object.keys(matchingPairs).length < needed) {
        setErrorMessage('Please match all items before submitting.');
        return;
      }
      void handleSubmitAnswer(JSON.stringify(matchingPairs));
      return;
    }

    if (qtype === 'order') {
      const currentOrder = orderItems.map((item) => q.items.indexOf(item));
      void handleSubmitAnswer(JSON.stringify(currentOrder));
      return;
    }

    void handleSubmitAnswer(textAnswer);
  };

  // ── Screens ────────────────────────────────────────────────────────────

  if (screen === 'auth' || screen === 'generating') {
    return <LoadingScreen message={loadingStage} />;
  }

  if (screen === 'welcome') {
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
                <div className="w-16 h-16 bg-gradient-to-br from-[#2563EB] to-[#7C3AED] rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-[#2563EB]/20">
                  <span className="text-2xl font-bold text-white">A</span>
                </div>

                <h1 className="text-3xl sm:text-4xl font-bold text-[#1E293B] mb-4">
                  Welcome to Today&apos;s Challenge
                </h1>

                <p className="text-[#475569] mb-3 leading-relaxed max-w-lg mx-auto">
                  Today&apos;s challenge covers the{' '}
                  <strong className="text-[#1E293B]">four Core Subjects</strong>.
                </p>
                <p className="text-[#475569] mb-6 leading-relaxed max-w-lg mx-auto">
                  Atlas will use today&apos;s performance to personalise future learning
                  recommendations.
                </p>

                {errorMessage && (
                  <div className="mb-6 max-w-md mx-auto rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {errorMessage}
                  </div>
                )}

                <motion.button
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.97 }}
                  onClick={() => void startChallenge(1)}
                  className="px-10 py-4 bg-gradient-to-r from-[#2563EB] to-[#1D4ED8] text-white font-bold text-lg rounded-xl shadow-lg shadow-[#2563EB]/25"
                >
                  Start Challenge
                </motion.button>
              </motion.div>
            </main>
          </div>
          <BottomNav />
        </div>
      </AppLayout>
    );
  }

  if (screen === 'subject_intro' && session) {
    const levelMeta = LEVEL_META[session.challenge_level];
    return (
      <AppLayout>
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex-1 lg:pb-0 pb-24">
            <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10">
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white border rounded-3xl p-8 shadow-sm"
              >
                <div className="text-sm uppercase tracking-[0.2em] text-blue-600 mb-3">
                  {levelMeta.label}
                </div>
                <h1 className="text-3xl font-bold mb-3">
                  Today we are starting with {subject}.
                </h1>
                <p className="text-gray-600 mb-4">
                  You will answer 6 {levelMeta.difficulty.toLowerCase()} questions. Earn XP for
                  every correct response.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                  <div className="p-4 bg-gray-50 rounded-2xl text-center">
                    <div className="text-sm text-gray-500">Questions</div>
                    <div className="text-xl font-bold">{questions.length || 6}</div>
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
                <button
                  onClick={startCurrentSubject}
                  className="px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition-colors"
                >
                  Start {subject}
                </button>
              </motion.div>
            </main>
          </div>
          <BottomNav />
        </div>
      </AppLayout>
    );
  }

  if (screen === 'level_complete' && session) {
    return (
      <AppLayout>
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex-1 lg:pb-0 pb-24">
            <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10">
              <div className="bg-white border rounded-2xl p-6">
                <h2 className="text-2xl font-bold mb-2">
                  Level {session.challenge_level} Complete
                </h2>
                <p className="text-gray-600 mb-4">
                  Nice work — you completed all 4 subjects for this level.
                </p>
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
                  <button
                    onClick={() => router.push('/challenges/intro')}
                    className="px-6 py-3 border border-gray-200 rounded-xl"
                  >
                    Exit challenge
                  </button>
                  <button
                    onClick={() => void continueLevel()}
                    className="px-6 py-3 bg-blue-600 text-white rounded-xl"
                  >
                    Continue to Level {session.challenge_level + 1}
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

  if (screen === 'final_summary' && finalSummary) {
    const recLessons = (finalSummary.weak_topics ?? []).map((t: string) => ({
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
                    {finalSummary.subject_performance?.map((s) => (
                      <div
                        key={s.subject}
                        className="flex items-center justify-between bg-gray-50 p-3 rounded-lg"
                      >
                        <div>
                          <div className="font-medium">{s.subject}</div>
                          <div className="text-xs text-gray-500">
                            {s.correct} correct / {s.total}
                          </div>
                        </div>
                        <div className="text-sm font-semibold">{s.accuracy}%</div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mb-4">
                  <h3 className="text-lg font-semibold">Recommended Lessons</h3>
                  <div className="mt-2 space-y-2">
                    {recLessons.length === 0 && (
                      <div className="text-sm text-gray-500">No recommendations — great job!</div>
                    )}
                    {recLessons.map((r) => (
                      <div
                        key={r.topic}
                        className="flex items-center justify-between bg-white p-3 rounded-lg border"
                      >
                        <div className="text-sm">{r.topic}</div>
                        <div className="flex gap-2">
                          <a href={r.learningLink} className="text-sm text-blue-600 underline">
                            Learning
                          </a>
                          {user?.shs_level === 'SHS 3' && (
                            <a href={r.revisionLink} className="text-sm text-purple-600 underline">
                              SHS3 Revision
                            </a>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-6 flex flex-wrap gap-3">
                  <button
                    onClick={() => router.push('/dashboard')}
                    className="px-6 py-3 bg-blue-600 text-white rounded-xl"
                  >
                    Go to Dashboard
                  </button>
                  <button
                    onClick={() => router.push('/challenges/leaderboard')}
                    className="px-6 py-3 border border-gray-200 rounded-xl"
                  >
                    Leaderboard
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

  if (screen === 'subject_summary') {
    const perf =
      sessionSummary?.subject_performance?.find((s) => s.subject === subject) || null;
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
                    <div className="text-2xl font-bold">
                      {perf ? `${perf.accuracy}%` : '0%'}
                    </div>
                  </div>
                </div>
                {errorMessage && (
                  <div className="mb-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {errorMessage}
                  </div>
                )}
                <div className="mt-6 text-center">
                  <button
                    onClick={handleContinueFromSummary}
                    className="px-6 py-3 bg-blue-600 text-white rounded-xl"
                  >
                    {pendingContinuationAction === 'continueLevel'
                      ? 'Continue to next level →'
                      : 'Continue →'}
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

  // ── Question screen ────────────────────────────────────────────────────
  const currentQ = questions[questionIndex] || null;
  if (!currentQ || !session) {
    return <LoadingScreen message="Loading question…" />;
  }

  // Normalise LLM variants (true_false → true-false, fill_blank → fill-blank, etc.)
  const rawType = String(currentQ.question_type || 'mcq').toLowerCase().replace(/_/g, '-');
  const qtypeAliases: Record<string, string> = {
    truefalse: 'true-false',
    'true-or-false': 'true-false',
    fillblank: 'fill-blank',
    'fill-in-the-blank': 'fill-blank',
    shortanswer: 'short-answer',
    'multiple-choice': 'mcq',
    arrange: 'order',
    'arrange-in-order': 'order',
    interpretation: 'scenario',
    comprehension: 'scenario',
  };
  const qtype = qtypeAliases[rawType] || rawType;
  const badge = QUESTION_TYPE_BADGES[qtype] || {
    label: qtype,
    color: 'text-gray-700',
    bg: 'bg-gray-50',
  };
  const locked = !!feedback || isSubmitting;

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-24">
          <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10">
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="text-sm text-[#64748B]">Subject</div>
                <div className="text-lg font-semibold text-[#1E293B]">{subject}</div>
              </div>
              <div className="text-right">
                <div className="text-sm text-[#64748B]">Time left</div>
                <div
                  className={`text-lg font-mono font-bold ${
                    remaining <= 10 ? 'text-red-500' : 'text-[#1E293B]'
                  }`}
                >
                  {remaining}s
                </div>
              </div>
            </div>

            <div className="mb-5">
              <div className="flex items-center justify-between text-xs text-[#64748B] mb-1.5">
                <span>Challenge Progress</span>
                <span>
                  {Math.min(
                    Math.round(((subjectIndex * 6 + questionIndex) / 24) * 100),
                    100,
                  )}
                  %
                </span>
              </div>
              <div className="w-full bg-[#E2E8F0] rounded-full h-2.5 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{
                    width: `${Math.min(
                      Math.round(((subjectIndex * 6 + questionIndex) / 24) * 100),
                      100,
                    )}%`,
                  }}
                  transition={{ duration: 0.4, ease: 'easeOut' }}
                  className="h-full rounded-full bg-gradient-to-r from-[#2563EB] to-[#7C3AED]"
                />
              </div>
            </div>

            <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 mb-4 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <div className="text-sm text-gray-500">
                  Question {questionIndex + 1} of {questions.length}
                </div>
                <div
                  className={`text-xs font-medium px-3 py-1 rounded-full ${badge.bg} ${badge.color}`}
                >
                  {badge.label}
                </div>
              </div>

              <h3 className="text-base md:text-lg font-medium text-[#1E293B] mb-5 leading-relaxed">
                {currentQ.question}
              </h3>

              {/* MCQ / Scenario */}
              {(qtype === 'mcq' || qtype === 'scenario') && (
                <div className="space-y-3">
                  {currentQ.options && typeof currentQ.options === 'object' ? (
                    Object.entries(currentQ.options).map(([k, v]: any) => {
                      const isSelected = selectedAnswer === k;
                      return (
                        <button
                          key={k}
                          type="button"
                          onClick={() => onSelectOption(k)}
                          disabled={locked}
                          className={`w-full text-left px-5 py-4 rounded-xl border-2 transition-all duration-150 disabled:cursor-not-allowed flex items-center gap-4 ${
                            isSelected
                              ? 'border-[#2563EB] bg-[#F8FAFF] ring-1 ring-[#2563EB]/30'
                              : 'border-[#E2E8F0] bg-white hover:border-[#2563EB] hover:bg-[#F8FAFF]'
                          } ${locked ? 'opacity-70' : ''}`}
                        >
                          <span
                            className={`w-8 h-8 rounded-full border-2 flex items-center justify-center text-sm font-bold ${
                              isSelected
                                ? 'border-[#2563EB] text-[#2563EB] bg-blue-50'
                                : 'border-[#CBD5E1] text-[#64748B]'
                            }`}
                          >
                            {k}
                          </span>
                          <span className="text-[#334155]">{v}</span>
                        </button>
                      );
                    })
                  ) : (
                    <p className="text-sm text-red-500">No options available for this question.</p>
                  )}
                </div>
              )}

              {/* True / False */}
              {qtype === 'true-false' && (
                <div className="grid grid-cols-2 gap-4">
                  {(
                    [
                      { key: 'A', label: 'True', icon: '✓', active: 'border-emerald-400 bg-emerald-50' },
                      { key: 'B', label: 'False', icon: '✗', active: 'border-red-400 bg-red-50' },
                    ] as const
                  ).map((opt) => {
                    const isSelected = selectedAnswer === opt.key;
                    return (
                      <button
                        key={opt.key}
                        type="button"
                        onClick={() => onSelectOption(opt.key)}
                        disabled={locked}
                        className={`flex flex-col items-center gap-3 px-6 py-8 border-2 rounded-2xl transition-all duration-150 disabled:cursor-not-allowed ${
                          isSelected
                            ? opt.active
                            : 'border-[#E2E8F0] bg-white hover:border-[#94A3B8]'
                        } ${locked ? 'opacity-70' : ''}`}
                      >
                        <span className="text-3xl">{opt.icon}</span>
                        <span className="text-lg font-semibold text-[#1E293B]">{opt.label}</span>
                      </button>
                    );
                  })}
                </div>
              )}

              {/* Fill in the Blank */}
              {qtype === 'fill-blank' && (
                <input
                  type="text"
                  value={textAnswer}
                  onChange={(e) => setTextAnswer(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') onClickSubmit();
                  }}
                  placeholder="Type your answer here…"
                  disabled={locked}
                  autoFocus
                  className="w-full px-4 py-3.5 border-2 border-[#E2E8F0] rounded-xl focus:border-[#2563EB] focus:ring-2 focus:ring-[#2563EB]/20 outline-none transition-all text-lg disabled:opacity-60"
                />
              )}

              {/* Short Answer */}
              {qtype === 'short-answer' && (
                <textarea
                  value={textAnswer}
                  onChange={(e) => setTextAnswer(e.target.value)}
                  placeholder="Type your answer in one sentence…"
                  disabled={locked}
                  autoFocus
                  className="w-full px-4 py-3.5 border-2 border-[#E2E8F0] rounded-xl focus:border-[#2563EB] focus:ring-2 focus:ring-[#2563EB]/20 outline-none transition-all min-h-[100px] resize-none disabled:opacity-60"
                />
              )}

              {/* Matching */}
              {qtype === 'matching' && (
                <div className="space-y-4">
                  <p className="text-sm text-[#64748B]">
                    Click a left item, then click a right item to create a match.
                  </p>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      {(currentQ.left_items || []).map((item: string, idx: number) => {
                        const matchedRight = matchingPairs[String(idx)];
                        const isSelected = selectedLeft === String(idx);
                        return (
                          <button
                            key={`left_${idx}`}
                            type="button"
                            onClick={() => {
                              if (locked) return;
                              setSelectedLeft(isSelected ? null : String(idx));
                            }}
                            disabled={locked}
                            className={`w-full text-left px-4 py-3 rounded-xl border-2 text-sm transition-all ${
                              matchedRight
                                ? 'border-emerald-300 bg-emerald-50'
                                : isSelected
                                  ? 'border-[#2563EB] bg-[#F8FAFF]'
                                  : 'border-[#E2E8F0] bg-white hover:border-[#94A3B8]'
                            }`}
                          >
                            <span className="font-semibold text-xs text-[#64748B] mr-2">
                              {idx + 1}.
                            </span>
                            {item}
                            {matchedRight && (
                              <span className="float-right text-xs text-emerald-600 font-medium">
                                → {parseInt(matchedRight, 10) + 1}
                              </span>
                            )}
                          </button>
                        );
                      })}
                    </div>
                    <div className="space-y-2">
                      {(currentQ.right_items || []).map((item: string, idx: number) => {
                        const isMatched = Object.values(matchingPairs).includes(String(idx));
                        const matchedBy = Object.entries(matchingPairs).find(
                          ([, v]) => v === String(idx),
                        )?.[0];
                        return (
                          <button
                            key={`right_${idx}`}
                            type="button"
                            onClick={() => {
                              if (locked || !selectedLeft || isMatched) return;
                              setMatchingPairs((prev) => ({
                                ...prev,
                                [selectedLeft]: String(idx),
                              }));
                              setSelectedLeft(null);
                            }}
                            disabled={locked || !selectedLeft || isMatched}
                            className={`w-full text-left px-4 py-3 rounded-xl border-2 text-sm transition-all ${
                              isMatched
                                ? 'border-emerald-300 bg-emerald-50 opacity-60'
                                : selectedLeft && !isMatched
                                  ? 'border-[#2563EB] bg-[#F8FAFF] cursor-pointer'
                                  : 'border-[#E2E8F0] bg-white'
                            }`}
                          >
                            {matchedBy !== undefined && (
                              <span className="font-semibold text-xs text-emerald-600 mr-2">
                                {parseInt(matchedBy, 10) + 1} →
                              </span>
                            )}
                            {item}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      setMatchingPairs({});
                      setSelectedLeft(null);
                    }}
                    disabled={locked}
                    className="px-4 py-2 border border-[#E2E8F0] rounded-xl text-sm text-[#64748B] hover:bg-gray-50 disabled:opacity-40"
                  >
                    Reset matches
                  </button>
                </div>
              )}

              {/* Order */}
              {qtype === 'order' && (
                <div className="space-y-3">
                  <p className="text-sm text-[#64748B]">
                    Use the arrows to arrange the items in the correct order.
                  </p>
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
                            type="button"
                            onClick={() => {
                              if (idx === 0 || locked) return;
                              const next = [...orderItems];
                              [next[idx - 1], next[idx]] = [next[idx], next[idx - 1]];
                              setOrderItems(next);
                            }}
                            disabled={idx === 0 || locked}
                            className="w-8 h-7 flex items-center justify-center rounded-lg border border-[#E2E8F0] hover:bg-gray-50 text-[#64748B] disabled:opacity-30"
                          >
                            ↑
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              if (idx === orderItems.length - 1 || locked) return;
                              const next = [...orderItems];
                              [next[idx], next[idx + 1]] = [next[idx + 1], next[idx]];
                              setOrderItems(next);
                            }}
                            disabled={idx === orderItems.length - 1 || locked}
                            className="w-8 h-7 flex items-center justify-center rounded-lg border border-[#E2E8F0] hover:bg-gray-50 text-[#64748B] disabled:opacity-30"
                          >
                            ↓
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Unknown type fallback */}
              {!['mcq', 'scenario', 'true-false', 'fill-blank', 'short-answer', 'matching', 'order'].includes(
                qtype,
              ) && (
                <textarea
                  value={textAnswer}
                  onChange={(e) => setTextAnswer(e.target.value)}
                  placeholder="Type your answer…"
                  disabled={locked}
                  className="w-full px-4 py-3.5 border-2 border-[#E2E8F0] rounded-xl outline-none min-h-[80px] resize-none"
                />
              )}

              {/* Submit Answer — always present */}
              {!feedback && (
                <div className="mt-6 flex flex-wrap items-center gap-3">
                  <button
                    type="button"
                    onClick={onClickSubmit}
                    disabled={isSubmitting}
                    className="px-6 py-3 bg-[#2563EB] text-white font-semibold rounded-xl hover:bg-[#1D4ED8] transition-colors disabled:opacity-50"
                  >
                    {isSubmitting ? 'Submitting…' : 'Submit Answer'}
                  </button>
                  <button
                    type="button"
                    onClick={() => void handleSubmitAnswer('')}
                    disabled={isSubmitting}
                    className="px-5 py-3 border-2 border-[#E2E8F0] rounded-xl text-sm text-[#64748B] hover:bg-gray-50 disabled:opacity-50"
                  >
                    Skip Question
                  </button>
                </div>
              )}
            </div>

            {errorMessage && (
              <div className="mb-4 rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
                {errorMessage}
              </div>
            )}

            {feedback && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`p-5 rounded-xl border-2 mb-4 ${
                  feedback.is_correct
                    ? 'bg-emerald-50 border-emerald-200'
                    : 'bg-red-50 border-red-200'
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xl">{feedback.is_correct ? '✅' : '❌'}</span>
                  <span className="font-bold text-lg">
                    {feedback.is_correct ? 'Correct!' : 'Incorrect'}
                  </span>
                </div>
                <div className="text-sm font-medium mb-2">
                  {feedback.xp_earned > 0
                    ? `+${feedback.xp_earned} XP`
                    : `${feedback.xp_earned} XP`}
                  <span className="text-[#64748B] ml-2">· Total {totalXp} XP</span>
                </div>
                <div className="text-sm text-[#475569] leading-relaxed">
                  {feedback.explanation}
                </div>
              </motion.div>
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
    <Suspense
      fallback={
        <AppLayout>
          <div className="flex items-center justify-center min-h-screen">
            <div className="w-8 h-8 border-2 border-[#2563EB] border-t-transparent rounded-full animate-spin" />
          </div>
        </AppLayout>
      }
    >
      <AtlasChallengeContent />
    </Suspense>
  );
}
