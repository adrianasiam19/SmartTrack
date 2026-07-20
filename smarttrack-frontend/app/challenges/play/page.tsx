'use client';

import { Suspense, useEffect, useMemo, useRef, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Sidebar from '../../components/Sidebar';
import BottomNav from '../../components/BottomNav';
import {
  completePhaseSession,
  startLevel,
  submitPhaseAnswer,
} from '../../lib/phasesApi';
import { getCurrentUser, getStoredUser, storeUser } from '../../lib/authApi';

const QUESTION_TIMEOUT = 60;

type Q = {
  id: number;
  subject: string;
  question_text: string;
  options: Record<string, string> | null;
  difficulty?: number;
};

type SessionPayload = {
  session_id: number;
  level_id: number;
  phase_number: number;
  level_number: number;
  questions: Q[];
};

async function syncUserFromServer(partial?: {
  xp?: number | null;
  rank?: string | null;
}) {
  try {
    if (partial?.xp != null || partial?.rank) {
      const cached = getStoredUser();
      if (cached) {
        storeUser({
          ...cached,
          xp: partial.xp ?? cached.xp,
          rank: partial.rank ?? cached.rank,
        });
      }
    }
    const fresh = await getCurrentUser();
    storeUser(fresh);
    return fresh;
  } catch {
    return null;
  }
}

function PhasePlayInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [session, setSession] = useState<SessionPayload | null>(null);
  const [index, setIndex] = useState(0);
  const [selected, setSelected] = useState('');
  const [feedback, setFeedback] = useState('');
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);
  const [timeLeft, setTimeLeft] = useState(QUESTION_TIMEOUT);
  const [userXp, setUserXp] = useState<number | null>(null);
  const [startingNext, setStartingNext] = useState(false);
  const [actionError, setActionError] = useState('');
  const [result, setResult] = useState<{
    passed: boolean;
    score: number;
    next?: string | null;
    phase_number?: number | null;
    level_id?: number | null;
    next_level_id?: number | null;
    next_level_number?: number | null;
    learning_nudge?: {
      subject: string;
      message?: string;
      curriculum_id?: string | null;
      topic_title?: string | null;
    } | null;
    session_xp?: number;
    user_xp?: number | null;
    rank?: string | null;
  } | null>(null);

  const selectedRef = useRef('');
  const indexRef = useRef(0);
  const sessionRef = useRef<SessionPayload | null>(null);
  const questionStartRef = useRef(Date.now());
  /** Prevents double submit (manual + timeout) for the same question */
  const lockRef = useRef(false);
  const advanceTimerRef = useRef<number | null>(null);

  useEffect(() => {
    const raw = sessionStorage.getItem('atlasPhaseSession');
    if (!raw) {
      router.replace('/challenges');
      return;
    }
    try {
      setSession(JSON.parse(raw) as SessionPayload);
    } catch {
      router.replace('/challenges');
    }
    const cached = getStoredUser();
    if (cached) setUserXp(cached.xp ?? 0);
  }, [router, searchParams]);

  useEffect(() => {
    selectedRef.current = selected;
  }, [selected]);

  useEffect(() => {
    indexRef.current = index;
  }, [index]);

  useEffect(() => {
    sessionRef.current = session;
  }, [session]);

  const question = useMemo(() => session?.questions[index] ?? null, [session, index]);

  const options = useMemo(() => {
    if (!question?.options) return [] as { key: string; text: string }[];
    return Object.entries(question.options).map(([key, text]) => ({
      key,
      text: String(text),
    }));
  }, [question]);

  // Reset UI + start a clean 60s countdown for each question
  useEffect(() => {
    if (!question || done) return;

    lockRef.current = false;
    questionStartRef.current = Date.now();
    setSelected('');
    setFeedback('');
    setBusy(false);
    setTimeLeft(QUESTION_TIMEOUT);

    if (advanceTimerRef.current != null) {
      window.clearTimeout(advanceTimerRef.current);
      advanceTimerRef.current = null;
    }

    const id = window.setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          window.clearInterval(id);
          return 0;
        }
        return t - 1;
      });
    }, 1000);

    return () => window.clearInterval(id);
  }, [question?.id, done]);

  async function goNextOrFinish(
    sessionData: SessionPayload,
    currentIndex: number,
    res: {
      user_xp?: number;
      rank?: string;
      xp_earned: number;
      is_correct: boolean;
    },
    timedOut: boolean,
  ) {
    if (typeof res.user_xp === 'number') {
      setUserXp(res.user_xp);
      void syncUserFromServer({ xp: res.user_xp, rank: res.rank });
    }

    const xpBit = res.xp_earned > 0 ? ` · +${res.xp_earned} XP` : '';
    setFeedback(
      timedOut
        ? `Time's up${xpBit}`
        : res.is_correct
          ? `Correct${xpBit}`
          : `Not quite — keep going${xpBit}`,
    );

    if (currentIndex + 1 < sessionData.questions.length) {
      advanceTimerRef.current = window.setTimeout(() => {
        advanceTimerRef.current = null;
        setIndex(currentIndex + 1);
      }, 500);
      return;
    }

    const complete = await completePhaseSession(sessionData.session_id);
    setFeedback('');
    setResult({
      ...complete,
      level_id: complete.level_id ?? sessionData.level_id,
    });
    setDone(true);
    if (typeof complete.user_xp === 'number') {
      setUserXp(complete.user_xp);
      void syncUserFromServer({
        xp: complete.user_xp,
        rank: complete.rank,
      });
    }
    sessionStorage.removeItem('atlasPhaseSession');
  }

  async function submitCurrent(timedOut: boolean) {
    const sessionData = sessionRef.current;
    const currentIndex = indexRef.current;
    const currentQuestion = sessionData?.questions[currentIndex];
    if (!sessionData || !currentQuestion) return;

    // Only one submit path may run per question
    if (lockRef.current) return;
    lockRef.current = true;

    const answer = selectedRef.current.trim();
    if (!timedOut && !answer) {
      lockRef.current = false;
      return;
    }

    setBusy(true);
    setFeedback('');
    const elapsed = Math.min(
      QUESTION_TIMEOUT,
      (Date.now() - questionStartRef.current) / 1000,
    );

    try {
      const res = await submitPhaseAnswer(
        sessionData.session_id,
        currentQuestion.id,
        answer || 'timeout',
        elapsed,
      );
      await goNextOrFinish(sessionData, currentIndex, res, timedOut);
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Submit failed';
      // Already saved on server (e.g. timeout raced with click) → still advance
      if (/already answered/i.test(message)) {
        await goNextOrFinish(
          sessionData,
          currentIndex,
          {
            is_correct: false,
            xp_earned: 0,
          },
          timedOut,
        );
      } else {
        lockRef.current = false;
        setFeedback(message);
      }
    } finally {
      setBusy(false);
    }
  }

  // Timer expiry: move on if the user hasn't submitted yet
  useEffect(() => {
    if (done || !question) return;
    if (timeLeft !== 0) return;
    if (lockRef.current) return;
    void submitCurrent(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps -- only react to timer hitting 0
  }, [timeLeft, question?.id, done]);

  if (!session || !question) {
    return (
      <div className="min-h-screen bg-transparent">
        <Sidebar />
        <main className="w-full max-w-2xl mx-auto px-4 sm:px-6 pt-20 lg:pt-10 pb-28 text-[#64748B]">
          Loading session…
        </main>
        <BottomNav />
      </div>
    );
  }

  if (done && result) {
    const busyAction = startingNext;

    const onContinueNextLevel = async () => {
      if (!result.next_level_id || busyAction) return;
      setStartingNext(true);
      setActionError('');
      try {
        const sessionPayload = await startLevel(result.next_level_id);
        sessionStorage.setItem('atlasPhaseSession', JSON.stringify(sessionPayload));
        window.location.href = `/challenges/play?session=${sessionPayload.session_id}`;
      } catch (e) {
        setActionError(
          e instanceof Error ? e.message : 'Could not start next level',
        );
        setStartingNext(false);
      }
    };

    const hasPrimary =
      result.next === 'psychometric_checkpoint' || !!result.next_level_id;

    return (
      <div className="min-h-screen bg-transparent">
        <Sidebar />
        <main className="w-full max-w-xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10 pb-28">
          <h1 className="text-2xl font-semibold text-[#0F172A]">
            Level complete
          </h1>
          <p className="mt-3 text-[#64748B]">
            Score {(result.score * 100).toFixed(0)}% — keep going. Difficulty
            adapts by subject for your next level.
          </p>
          {typeof result.session_xp === 'number' ? (
            <p className="mt-2 text-sm font-medium text-[#2563EB]">
              Session XP: +{result.session_xp}
              {typeof result.user_xp === 'number'
                ? ` · Total ${result.user_xp.toLocaleString()} XP`
                : ''}
            </p>
          ) : null}
          {result.learning_nudge?.subject ? (
            <p className="mt-3 text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
              Tip: review{' '}
              {result.learning_nudge.topic_title ||
                result.learning_nudge.subject.replace(/_/g, ' ')}{' '}
              in the Learning Center.
              {result.learning_nudge.curriculum_id ? (
                <>
                  {' '}
                  <button
                    type="button"
                    className="font-semibold text-[#2563EB] underline"
                    onClick={() =>
                      router.push(
                        `/learning?topic=${encodeURIComponent(
                          result.learning_nudge!.curriculum_id!,
                        )}`,
                      )
                    }
                  >
                    Open topic
                  </button>
                </>
              ) : (
                <>
                  {' '}
                  <button
                    type="button"
                    className="font-semibold text-[#2563EB] underline"
                    onClick={() => router.push('/learning')}
                  >
                    Open Learning Center
                  </button>
                </>
              )}
            </p>
          ) : null}
          {actionError ? (
            <p className="mt-3 text-sm text-red-600">{actionError}</p>
          ) : null}
          <div className="mt-6 flex flex-col sm:flex-row gap-3">
            {result.next === 'psychometric_checkpoint' ? (
              <button
                type="button"
                className="rounded-lg bg-[#2563EB] text-white px-4 py-2.5 font-medium"
                onClick={() =>
                  router.push(
                    `/challenges/checkpoint?phase=${result.phase_number}`,
                  )
                }
              >
                Continue to psychometric checkpoint
              </button>
            ) : null}
            {result.next_level_id ? (
              <button
                type="button"
                disabled={busyAction}
                className="rounded-lg bg-[#2563EB] text-white px-4 py-2.5 font-medium disabled:opacity-50"
                onClick={() => void onContinueNextLevel()}
              >
                {startingNext ? 'Starting…' : 'Continue to next level'}
              </button>
            ) : null}
            <button
              type="button"
              className={`rounded-lg px-4 py-2.5 font-medium ${
                hasPrimary
                  ? 'border border-slate-200 bg-white text-[#0F172A] hover:bg-slate-50'
                  : 'bg-[#2563EB] text-white'
              }`}
              onClick={() => router.push('/challenges')}
            >
              Back to Phase map
            </button>
          </div>
        </main>
        <BottomNav />
      </div>
    );
  }

  const timerPercent = (timeLeft / QUESTION_TIMEOUT) * 100;
  const timerColour =
    timeLeft <= 10 ? 'bg-red-500' : timeLeft <= 20 ? 'bg-[#D97706]' : 'bg-[#4F46E5]';

  return (
    <div className="min-h-screen bg-transparent">
      <Sidebar />
      <main className="w-full max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10 pb-28">
        <div className="flex items-center justify-between gap-3">
          <p className="text-sm text-[#64748B]">
            Phase {session.phase_number} · Level {session.level_number} ·{' '}
            {index + 1}/{session.questions.length} · {QUESTION_TIMEOUT}s each
          </p>
          {userXp != null ? (
            <p className="text-sm font-semibold text-[#2563EB]">
              {userXp.toLocaleString()} XP
            </p>
          ) : null}
        </div>

        <div className="mt-3 flex items-center justify-between gap-2">
          <p className="text-xs uppercase tracking-wide text-[#94A3B8]">
            {question.subject.replace(/_/g, ' ')}
          </p>
          <span
            className={`text-xs font-mono font-semibold ${
              timeLeft <= 10 ? 'text-red-500' : 'text-[#64748B]'
            }`}
          >
            {timeLeft}s
          </span>
        </div>
        <div
          className={`mt-1.5 w-full bg-gray-100 rounded-full h-1.5 ${
            timeLeft <= 10 && !busy ? 'animate-pulse' : ''
          }`}
        >
          <div
            className={`h-1.5 rounded-full transition-[width] duration-1000 linear ${timerColour}`}
            style={{ width: `${Math.max(0, timerPercent)}%` }}
          />
        </div>

        <h1 className="mt-4 text-xl font-semibold text-[#0F172A]">
          {question.question_text}
        </h1>
        <div className="mt-6 space-y-3">
          {options.map((opt) => (
            <button
              key={opt.key}
              type="button"
              disabled={busy}
              onClick={() => setSelected(opt.key)}
              className={`w-full text-left rounded-xl border px-4 py-3 transition ${
                selected === opt.key
                  ? 'border-[#2563EB] bg-[#EFF6FF]'
                  : 'border-slate-200 bg-white hover:border-slate-300'
              }`}
            >
              <span className="font-medium mr-2">{opt.key}.</span>
              {opt.text}
            </button>
          ))}
        </div>
        {feedback ? (
          <p className="mt-4 text-sm text-[#475569]">{feedback}</p>
        ) : null}
        <button
          type="button"
          disabled={!selected || busy}
          onClick={() => void submitCurrent(false)}
          className="mt-6 rounded-lg bg-[#2563EB] text-white px-5 py-2.5 disabled:opacity-50"
        >
          {busy ? 'Saving…' : 'Submit answer'}
        </button>
      </main>
      <BottomNav />
    </div>
  );
}

export default function PhasePlayPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center text-[#64748B]">
          Loading…
        </div>
      }
    >
      <PhasePlayInner />
    </Suspense>
  );
}
