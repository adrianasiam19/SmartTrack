'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import Sidebar from '../components/Sidebar';
import BottomNav from '../components/BottomNav';
import {
  getProgression,
  PhasePublic,
  startLevel,
  replayLevel,
} from '../lib/phasesApi';
import { getAccessToken } from '../lib/authApi';

function phaseStatusLabel(status: string) {
  return status.replace(/_/g, ' ');
}

function levelStatusLabel(status: string, starting: boolean, done: boolean) {
  if (starting) return 'Starting…';
  if (done) return 'Replay';
  return status.replace(/_/g, ' ');
}

export default function ChallengesHomePage() {
  const router = useRouter();
  const [phases, setPhases] = useState<PhasePublic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [starting, setStarting] = useState<number | null>(null);
  const [selectedPhaseId, setSelectedPhaseId] = useState<number | null>(null);

  const load = useCallback(async () => {
    try {
      if (!getAccessToken()) {
        router.push('/login');
        return;
      }
      const data = await getProgression();
      setPhases(data.phases);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load');
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    load();
  }, [load]);

  const selectedPhase = useMemo(
    () => phases.find((p) => p.id === selectedPhaseId) ?? null,
    [phases, selectedPhaseId],
  );

  const onStart = async (levelId: number, status: string) => {
    if (status === 'locked') return;
    setStarting(levelId);
    setError('');
    try {
      const session =
        status === 'completed'
          ? await replayLevel(levelId)
          : await startLevel(levelId);
      sessionStorage.setItem('atlasPhaseSession', JSON.stringify(session));
      router.push(`/challenges/play?session=${session.session_id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not start level');
    } finally {
      setStarting(null);
    }
  };

  const completedCount = (phase: PhasePublic) =>
    phase.levels.filter((l) => l.status === 'completed').length;

  const phaseLocked = (phase: PhasePublic) => phase.status === 'locked';

  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <main className="w-full max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10 pb-28">
        {!selectedPhase ? (
          <>
            <h1 className="text-2xl font-semibold text-[#0F172A]">Challenges</h1>
            <p className="mt-2 text-[#64748B]">
              Choose a phase to open its levels. Complete levels in order to unlock
              the next ones.
            </p>
          </>
        ) : (
          <>
            <button
              type="button"
              onClick={() => setSelectedPhaseId(null)}
              className="inline-flex items-center gap-2 rounded-full border border-[#BFDBFE] bg-white px-4 py-2 text-sm font-semibold text-[#2563EB] shadow-sm transition hover:border-[#2563EB] hover:bg-[#EFF6FF]"
            >
              <span aria-hidden className="text-base leading-none">←</span>
              All phases
            </button>
            <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between rounded-3xl border border-[#BFDBFE] bg-gradient-to-br from-[#EFF6FF] to-white px-5 py-5 sm:px-6">
              <div className="min-w-0">
                <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#0F172A]">
                  {selectedPhase.name}
                </h1>
                <p className="mt-1.5 text-sm sm:text-base text-[#64748B]">
                  {selectedPhase.description}
                </p>
              </div>
              <span className="self-start shrink-0 rounded-full border border-[#BFDBFE] bg-white px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-[#2563EB]">
                {phaseStatusLabel(selectedPhase.status)}
              </span>
            </div>
          </>
        )}

        {error ? (
          <p className="mt-4 text-sm text-red-600">{error}</p>
        ) : null}

        {loading ? (
          <p className="mt-8 text-[#64748B]">Loading progression…</p>
        ) : !selectedPhase ? (
          <div className="mt-10 grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
            {phases.map((phase) => {
              const locked = phaseLocked(phase);
              const done = completedCount(phase);
              const total = phase.levels.length || 10;
              const progress = total > 0 ? Math.round((done / total) * 100) : 0;
              const completed = phase.status === 'completed';
              return (
                <button
                  key={phase.id}
                  type="button"
                  onClick={() => setSelectedPhaseId(phase.id)}
                  className={`group flex min-h-[280px] sm:min-h-[320px] flex-col rounded-3xl border px-5 py-6 sm:px-6 sm:py-7 text-left transition duration-200 hover:-translate-y-1 hover:shadow-lg ${
                    locked
                      ? 'border-slate-200 bg-gradient-to-b from-slate-50 to-slate-100/80 hover:border-slate-300'
                      : completed
                        ? 'border-emerald-200 bg-gradient-to-b from-emerald-50 to-white hover:border-emerald-400'
                        : 'border-[#BFDBFE] bg-gradient-to-b from-[#EFF6FF] to-white hover:border-[#2563EB]'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <span
                      className={`inline-flex h-12 w-12 items-center justify-center rounded-2xl text-lg font-bold ${
                        locked
                          ? 'bg-slate-200 text-slate-500'
                          : completed
                            ? 'bg-emerald-100 text-emerald-700'
                            : 'bg-[#2563EB] text-white shadow-md shadow-[#2563EB]/25'
                      }`}
                    >
                      {phase.number}
                    </span>
                    <span
                      className={`rounded-full px-3 py-1 text-[11px] font-semibold uppercase tracking-wider ${
                        locked
                          ? 'bg-slate-200/80 text-slate-500'
                          : completed
                            ? 'bg-emerald-100 text-emerald-700'
                            : 'bg-white text-[#2563EB] border border-[#BFDBFE]'
                      }`}
                    >
                      {phaseStatusLabel(phase.status)}
                    </span>
                  </div>

                  <div className="mt-8 flex-1">
                    <h2
                      className={`text-2xl font-bold tracking-tight ${
                        locked ? 'text-slate-500' : 'text-[#0F172A]'
                      }`}
                    >
                      {phase.name}
                    </h2>
                    <p
                      className={`mt-3 text-base leading-relaxed ${
                        locked ? 'text-slate-400' : 'text-[#64748B]'
                      }`}
                    >
                      {phase.description ||
                        'Mixed-subject challenges across 10 levels.'}
                    </p>
                  </div>

                  <div className="mt-8 space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span
                        className={
                          locked ? 'text-slate-400' : 'font-medium text-[#475569]'
                        }
                      >
                        {done} of {total} levels
                      </span>
                      <span
                        className={
                          locked ? 'text-slate-400' : 'font-semibold text-[#1E3A8A]'
                        }
                      >
                        {progress}%
                      </span>
                    </div>
                    <div
                      className={`h-2.5 w-full overflow-hidden rounded-full ${
                        locked ? 'bg-slate-200' : 'bg-[#DBEAFE]'
                      }`}
                    >
                      <div
                        className={`h-full rounded-full transition-all ${
                          locked
                            ? 'bg-slate-300'
                            : completed
                              ? 'bg-emerald-500'
                              : 'bg-[#2563EB]'
                        }`}
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                    <span
                      className={`mt-1 inline-flex w-full items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold transition ${
                        locked
                          ? 'bg-slate-200 text-slate-500'
                          : completed
                            ? 'bg-emerald-600 text-white group-hover:bg-emerald-700'
                            : 'bg-[#2563EB] text-white shadow-sm shadow-[#2563EB]/20 group-hover:bg-[#1D4ED8]'
                      }`}
                    >
                      {locked ? 'Preview levels' : 'Open levels'}
                      <span aria-hidden>→</span>
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        ) : (
          <div className="mt-8">
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
              {selectedPhase.levels.map((level) => {
                const locked = level.status === 'locked';
                const done = level.status === 'completed';
                const available =
                  level.status === 'available' ||
                  level.status === 'in_progress' ||
                  done;
                return (
                  <button
                    key={level.id}
                    type="button"
                    disabled={locked || starting === level.id}
                    onClick={() => onStart(level.id, level.status)}
                    className={`rounded-xl border px-3 py-4 text-left transition ${
                      locked
                        ? 'border-slate-200 bg-slate-50 text-slate-400 cursor-not-allowed'
                        : done
                          ? 'border-emerald-200 bg-emerald-50 hover:border-emerald-400'
                          : available
                            ? 'border-blue-200 bg-white hover:border-blue-500'
                            : 'border-slate-200 bg-white'
                    }`}
                  >
                    <div className="text-sm font-medium">
                      Level {level.number}
                    </div>
                    <div className="text-xs mt-1 capitalize">
                      {levelStatusLabel(
                        level.status,
                        starting === level.id,
                        done,
                      )}
                    </div>
                  </button>
                );
              })}
            </div>

            {selectedPhase.levels.every((l) => l.status === 'completed') ? (
              <Link
                href={`/challenges/checkpoint?phase=${selectedPhase.number}`}
                className="inline-block mt-6 text-sm font-medium text-[#2563EB]"
              >
                Open Phase {selectedPhase.number} psychometric checkpoint →
              </Link>
            ) : null}
          </div>
        )}
      </main>
      <BottomNav />
    </div>
  );
}
