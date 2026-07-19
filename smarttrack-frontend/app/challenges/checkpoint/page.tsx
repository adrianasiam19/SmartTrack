'use client';

import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Sidebar from '../../components/Sidebar';
import BottomNav from '../../components/BottomNav';
import {
  answerCheckpoint,
  completeCheckpoint,
  startCheckpoint,
} from '../../lib/phasesApi';

type Opt = { id: number; label: string; text: string };
type Q = {
  id: number;
  category: string;
  text: string;
  options: Opt[];
};

function CheckpointInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const phaseNumber = Number(searchParams.get('phase') || '1');

  const [questions, setQuestions] = useState<Q[]>([]);
  const [index, setIndex] = useState(0);
  const [phaseLabel, setPhaseLabel] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [recommendation, setRecommendation] = useState<{
    phase_label: string;
    rationale_summary: string;
    programme_suggestions: { programme: string; score: number }[];
    is_final: boolean;
  } | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const data = await startCheckpoint(phaseNumber);
        setQuestions(data.questions);
        setPhaseLabel(data.phase_label);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to load checkpoint');
      }
    })();
  }, [phaseNumber]);

  const q = questions[index];

  const onPick = async (optionId: number) => {
    if (!q || busy) return;
    setBusy(true);
    setError('');
    try {
      await answerCheckpoint(phaseNumber, q.id, optionId);
      if (index + 1 < questions.length) {
        setIndex((i) => i + 1);
      } else {
        const done = await completeCheckpoint(phaseNumber);
        if (done.complete && done.recommendation) {
          setRecommendation(done.recommendation);
        } else {
          setError(
            `Need ${done.required} answers; have ${done.answered}.`,
          );
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed');
    } finally {
      setBusy(false);
    }
  };

  if (recommendation) {
    return (
      <div className="min-h-screen bg-[#F8FAFC]">
        <Sidebar />
        <main className="w-full max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10 pb-28">
          <p className="text-sm text-[#2563EB] font-medium">
            This recommendation reflects your progress through{' '}
            {recommendation.phase_label}
          </p>
          <h1 className="mt-2 text-2xl font-semibold text-[#0F172A]">
            {recommendation.is_final
              ? 'Your final programme recommendation'
              : 'Updated recommendation'}
          </h1>
          <p className="mt-4 text-[#475569]">
            {recommendation.rationale_summary}
          </p>
          <ul className="mt-6 space-y-2">
            {recommendation.programme_suggestions.map((s) => (
              <li
                key={s.programme}
                className="rounded-lg border border-slate-200 bg-white px-4 py-3"
              >
                {s.programme}
                <span className="text-[#64748B]"> · {s.score}</span>
              </li>
            ))}
          </ul>
          <button
            type="button"
            className="mt-8 rounded-lg bg-[#1E3A8A] text-white px-4 py-2"
            onClick={() => router.push('/recommendations')}
          >
            View recommendation history
          </button>
        </main>
        <BottomNav />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="w-full max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10 pb-28">
        <h1 className="text-2xl font-semibold text-[#0F172A]">
          {phaseLabel || `Phase ${phaseNumber}`} checkpoint
        </h1>
        <p className="mt-2 text-sm text-[#64748B]">
          No right or wrong answers — help Atlas understand how you think.
          {q ? ` (${index + 1}/${questions.length})` : ''}
        </p>
        {error ? <p className="mt-4 text-sm text-red-600">{error}</p> : null}
        {!q ? (
          <p className="mt-8 text-[#64748B]">Loading questions…</p>
        ) : (
          <>
            <p className="mt-6 text-xs uppercase tracking-wide text-[#94A3B8]">
              {q.category}
            </p>
            <h2 className="mt-2 text-lg font-medium text-[#0F172A]">{q.text}</h2>
            <div className="mt-6 space-y-3">
              {q.options.map((opt) => (
                <button
                  key={opt.id}
                  type="button"
                  disabled={busy}
                  onClick={() => onPick(opt.id)}
                  className="w-full text-left rounded-xl border border-slate-200 bg-white px-4 py-3 hover:border-[#2563EB] disabled:opacity-50"
                >
                  <span className="font-medium mr-2">{opt.label}.</span>
                  {opt.text}
                </button>
              ))}
            </div>
          </>
        )}
      </main>
      <BottomNav />
    </div>
  );
}

export default function CheckpointPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center text-[#64748B]">
          Loading checkpoint…
        </div>
      }
    >
      <CheckpointInner />
    </Suspense>
  );
}
