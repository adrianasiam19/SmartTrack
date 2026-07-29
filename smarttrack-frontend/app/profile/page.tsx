'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '../components/Sidebar';
import BottomNav from '../components/BottomNav';
import AppLayout from '../components/AppLayout';
import { getCurrentUser, getAccessToken, getStoredUser, phaseLabelFromLevel, UserProfile } from '../lib/authApi';
import { getProgression, PhasePublic } from '../lib/phasesApi';
import { motion } from 'framer-motion';

type ChallengeStage = {
  hasStarted: boolean;
  phaseLabel: string;
  headline: string;
  detail: string;
  cta: string;
};

function buildChallengeStage(
  phases: PhasePublic[],
  currentPhaseNumber: number,
  currentLevelNumber: number
): ChallengeStage {
  const completedLevels = phases.flatMap((p) =>
    p.levels.filter((l) => l.status === 'completed').map((l) => ({ phase: p.number, level: l.number }))
  );
  const inProgressLevels = phases.flatMap((p) =>
    p.levels.filter((l) => l.status === 'in_progress' || l.status === 'available')
  );
  const completedPhases = phases.filter(
    (p) => p.status === 'completed' || p.levels.every((l) => l.status === 'completed')
  );
  const hasStarted =
    completedLevels.length > 0 ||
    inProgressLevels.length > 0 ||
    phases.some((p) => p.status === 'completed' || p.status === 'in_progress');

  if (!hasStarted) {
    return {
      hasStarted: false,
      phaseLabel: 'Not started',
      headline: 'No challenges yet',
      detail: 'Start Phase 1 to begin tracking your progress here.',
      cta: 'Start Your First Challenge',
    };
  }

  const allDone =
    phases.length > 0 &&
    phases.every(
      (p) => p.status === 'completed' || p.levels.every((l) => l.status === 'completed')
    );

  if (allDone) {
    const last = phases[phases.length - 1];
    return {
      hasStarted: true,
      phaseLabel: 'Completed',
      headline: `You've finished Phase ${last?.number ?? currentPhaseNumber}`,
      detail: 'All phases are complete. You can replay levels anytime from Challenges.',
      cta: 'View challenges',
    };
  }

  const latestCompletedPhase = completedPhases.sort((a, b) => b.number - a.number)[0];
  const activePhase =
    phases.find((p) => p.number === currentPhaseNumber) ||
    phases.find((p) => p.status === 'in_progress') ||
    phases.find((p) => p.levels.some((l) => l.status === 'available' || l.status === 'in_progress'));

  const phaseNum = activePhase?.number ?? currentPhaseNumber;
  const levelNum = currentLevelNumber;
  const phaseFullyDone = latestCompletedPhase?.number === phaseNum;

  let headline: string;
  let detail: string;

  if (latestCompletedPhase && !phaseFullyDone && latestCompletedPhase.number < phaseNum) {
    headline = `Phase ${latestCompletedPhase.number} complete`;
    detail = `Continue with Phase ${phaseNum}, Level ${levelNum}.`;
  } else if (activePhase?.status === 'completed' || phaseFullyDone) {
    headline = `Phase ${phaseNum} complete`;
    detail = `Ready to continue into the next phase.`;
  } else {
    headline = `Phase ${phaseNum}, Level ${levelNum}`;
    const doneInPhase = activePhase?.levels.filter((l) => l.status === 'completed').length ?? 0;
    const totalInPhase = activePhase?.levels.length ?? 10;
    detail =
      doneInPhase > 0
        ? `${doneInPhase}/${totalInPhase} levels done in this phase — keep going.`
        : 'Continue from Challenges to keep progressing.';
  }

  return {
    hasStarted: true,
    phaseLabel: `Phase ${phaseNum}`,
    headline,
    detail,
    cta: 'Continue challenges',
  };
}

export default function Profile() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [phases, setPhases] = useState<PhasePublic[]>([]);
  const [currentPhaseNumber, setCurrentPhaseNumber] = useState(1);
  const [currentLevelNumber, setCurrentLevelNumber] = useState(1);
  const [loading, setLoading] = useState(true);

  const getInitials = (name: string | undefined) =>
    name?.split(' ').filter(Boolean).map((n) => n[0]).join('').toUpperCase().slice(0, 2) || '?';

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        if (!getAccessToken()) {
          router.push('/login');
          return;
        }
        const cached = getStoredUser();
        if (cached) setUser(cached);
        const backendUser = await getCurrentUser();
        setUser(backendUser);

        try {
          const progression = await getProgression();
          setPhases(progression.phases || []);
          setCurrentPhaseNumber(progression.current_phase_number || 1);
          setCurrentLevelNumber(progression.current_level_number || 1);
        } catch {
          setPhases([]);
        }
      } catch {
        /* ignore */
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [router]);

  const getMemberSince = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    } catch {
      return 'Recently';
    }
  };

  const stage = buildChallengeStage(phases, currentPhaseNumber, currentLevelNumber);
  const phaseFieldLabel =
    stage.hasStarted
      ? stage.phaseLabel
      : phaseLabelFromLevel(user?.shs_level) !== 'Not set'
        ? phaseLabelFromLevel(user?.shs_level)
        : 'Not started';

  if (loading)
    return (
      <AppLayout>
        <div className="flex min-h-screen">
          <Sidebar />
          <main className="flex-1 flex items-center justify-center">
            <div className="w-8 h-8 border-2 border-[#4F46E5] border-t-transparent rounded-full animate-spin" />
          </main>
        </div>
      </AppLayout>
    );

  if (!user)
    return (
      <AppLayout>
        <div className="flex min-h-screen">
          <Sidebar />
          <main className="flex-1 flex items-center justify-center">
            <p className="text-gray-500">Please log in to view your profile</p>
          </main>
        </div>
      </AppLayout>
    );

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-20">
          <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-8 pb-28">
            <div className="mb-6">
              <h1 className="text-xl font-bold text-[#1E293B]">Profile</h1>
              <p className="text-sm text-gray-500">Your account and challenge information</p>
            </div>

            <div className="space-y-6">
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white border border-gray-200 rounded-xl p-6"
              >
                <div className="flex items-start gap-5 mb-6">
                  <div className="w-16 h-16 bg-gradient-to-br from-[#4F46E5] to-[#D97706] rounded-xl flex items-center justify-center text-white text-xl font-bold shadow-sm">
                    {getInitials(user.full_name)}
                  </div>
                  <div className="flex-1">
                    <h2 className="text-xl font-semibold text-[#1E293B]">{user.full_name}</h2>
                    <p className="text-sm text-gray-500 mb-2">{user.email}</p>
                    <p className="text-xs text-gray-400">
                      Member since {getMemberSince(user.created_at || '')}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
                  <div className="bg-[#EEF2FF] rounded-xl p-4">
                    <p className="text-xs text-gray-500 mb-1">Total XP</p>
                    <p className="text-2xl font-bold text-[#4F46E5]">{user.xp ?? 0}</p>
                  </div>
                  <div className="bg-[#FFFBEB] rounded-xl p-4">
                    <p className="text-xs text-gray-500 mb-1">Rank</p>
                    <p className="text-2xl font-bold text-[#D97706]">{user.rank ?? 'Beginner'}</p>
                  </div>
                  <div className="bg-[#FFF1F2] rounded-xl p-4">
                    <p className="text-xs text-gray-500 mb-1">Streak</p>
                    <p className="text-2xl font-bold text-[#F43F5E]">
                      {user.streak ?? 0} {(user.streak ?? 0) === 1 ? 'day' : 'days'}
                    </p>
                  </div>
                </div>

                <div className="grid sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Full Name</label>
                    <input
                      type="text"
                      value={user.full_name || ''}
                      readOnly
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-[#1E293B] text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Email</label>
                    <input
                      type="email"
                      value={user.email || ''}
                      readOnly
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-[#1E293B] text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Programme</label>
                    <div className="px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-sm text-[#1E293B]">
                      <span>{user.programme || 'Not set'}</span>
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Phase</label>
                    <div className="px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-sm text-[#1E293B]">
                      <span>{phaseFieldLabel}</span>
                    </div>
                  </div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-white border border-gray-200 rounded-xl p-6"
              >
                <h2 className="text-lg font-semibold text-[#1E293B] mb-6">Challenge History</h2>

                {!stage.hasStarted ? (
                  <div className="py-8 text-center">
                    <p className="text-gray-500 text-sm mb-4">{stage.detail}</p>
                    <button
                      onClick={() => router.push('/challenges')}
                      className="px-4 py-2 bg-[#4F46E5] text-white text-sm font-medium rounded-lg hover:bg-[#4338CA] transition-colors"
                    >
                      {stage.cta}
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="p-4 bg-[#EEF2FF] rounded-xl border border-[#C7D2FE]">
                      <h3 className="font-semibold text-[#1E293B] text-sm">{stage.headline}</h3>
                      <p className="text-xs text-gray-500 mt-1">{stage.detail}</p>
                    </div>
                    <button
                      onClick={() => router.push('/challenges')}
                      className="w-full px-4 py-2 border border-[#C7D2FE] text-[#4F46E5] text-sm font-medium rounded-lg hover:bg-[#EEF2FF] transition-colors"
                    >
                      {stage.cta}
                    </button>
                  </div>
                )}
              </motion.div>
            </div>
          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}
