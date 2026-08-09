'use client';

/**
 * Personal Progress — clean overview matching the Dashboard visual system.
 * All values come from the live /progress/me payload (no mock defaults).
 */
import { motion } from 'framer-motion';
import type {
  FutureModules,
  MotivationalInsight,
  NextGoal,
  PersonalProgressStats,
  ProgressMeter,
  ProgressVisualizations,
  WeeklyProgressSummary,
} from '../lib/progressApi';
import ProgressExtensionSlot from './ProgressExtensionSlot';

type Props = {
  stats: PersonalProgressStats | null;
  weekly?: WeeklyProgressSummary | null;
  visualizations?: ProgressVisualizations | null;
  nextGoal?: NextGoal | null;
  insights?: MotivationalInsight[];
  futureModules?: FutureModules | null;
  loading?: boolean;
};

function Bar({
  pct,
  color = 'bg-[#2563EB]',
  track = 'bg-[#E2E8F0]',
}: {
  pct: number;
  color?: string;
  track?: string;
}) {
  const width = Math.min(100, Math.max(0, pct));
  return (
    <div className={`h-1.5 w-full overflow-hidden rounded-full ${track}`}>
      <motion.div
        className={`h-full rounded-full ${color}`}
        initial={{ width: 0 }}
        animate={{ width: `${width}%` }}
        transition={{ duration: 0.65, ease: 'easeOut' }}
      />
    </div>
  );
}

function AccuracyRing({ meter }: { meter: ProgressMeter }) {
  const size = 112;
  const stroke = 9;
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const pct = Math.min(100, Math.max(0, meter.pct));
  const offset = c - (pct / 100) * c;
  const show = meter.current > 0 || pct > 0;

  return (
    <div className="flex h-full flex-col items-center justify-center rounded-2xl border border-[#E2E8F0] bg-white/95 px-4 py-6 shadow-sm backdrop-blur-sm">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={r}
            fill="none"
            stroke="#E2E8F0"
            strokeWidth={stroke}
          />
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={r}
            fill="none"
            stroke="#10B981"
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={c}
            initial={{ strokeDashoffset: c }}
            animate={{ strokeDashoffset: show ? offset : c }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-bold tabular-nums text-[#0F172A]">
            {show ? `${Math.round(pct)}%` : '—'}
          </span>
        </div>
      </div>
      <p className="mt-3 text-center text-sm text-[#64748B]">
        {meter.detail || 'Challenge accuracy'}
      </p>
    </div>
  );
}

function ProgressRow({
  label,
  pct,
  detail,
  color,
  track,
}: {
  label: string;
  pct: number;
  detail: string | null | undefined;
  color: string;
  track: string;
}) {
  return (
    <div>
      <div className="mb-1.5 flex items-end justify-between gap-3">
        <p className="text-sm font-semibold text-[#0F172A]">{label}</p>
        <p className="text-sm font-bold tabular-nums text-[#0F172A]">
          {Math.round(pct)}%
        </p>
      </div>
      <Bar pct={pct} color={color} track={track} />
      {detail ? (
        <p className="mt-1.5 text-xs text-[#64748B]">{detail}</p>
      ) : null}
    </div>
  );
}

export default function PersonalProgressPanel({
  stats,
  weekly,
  visualizations,
  nextGoal,
  insights = [],
  futureModules = null,
  loading,
}: Props) {
  if (loading && !stats) {
    return (
      <section className="mb-5 rounded-2xl border border-[#E2E8F0] bg-white/90 p-10 backdrop-blur-sm">
        <div className="flex items-center justify-center gap-2 text-sm text-[#94A3B8]">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-[#2563EB] border-t-transparent" />
          Loading your progress…
        </div>
      </section>
    );
  }

  if (!stats) return null;

  const xpMeter = visualizations?.xp_progress;
  const phaseMeter = visualizations?.phase_progress;
  const levelMeter = visualizations?.level_completion;
  const accuracyMeter = visualizations?.challenge_accuracy;
  const streakMeter = visualizations?.learning_streak;

  const xpCurrent = Math.round(xpMeter?.current ?? 0);
  const xpTarget = Math.max(1, Math.round(xpMeter?.target ?? 1));
  const xpPct = xpMeter?.pct ?? 0;
  const xpRemaining = Math.max(0, xpTarget - xpCurrent);

  const nextRankLabel = (() => {
    const detail = xpMeter?.detail || '';
    if (detail.includes('toward ')) {
      return detail.split('toward ').pop() || 'next rank';
    }
    return 'next rank';
  })();

  const bannerText =
    insights[0]?.message ||
    nextGoal?.message ||
    'Keep learning — every session strengthens your path.';
  const secondaryLine = insights[1]?.message || nextGoal?.reason || null;

  return (
    <motion.div
      id="personal-progress"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-5 space-y-4"
    >
      {/* Overview */}
      <section className="rounded-2xl border border-[#E2E8F0] bg-white/95 p-5 shadow-sm backdrop-blur-sm sm:p-6">
        <div className="flex items-start justify-between gap-4">
          <p className="text-[2rem] font-bold leading-none tracking-tight text-[#0F172A] sm:text-[2.25rem]">
            {xpCurrent.toLocaleString()}
            <span className="ml-2 text-sm font-medium text-[#94A3B8]">
              / {xpTarget.toLocaleString()} to next rank
            </span>
          </p>
          <div className="shrink-0 pt-1 text-right">
            <p className="text-sm text-[#64748B]">
              Longest streak{' '}
              <span className="font-semibold text-[#0F172A]">
                {stats.longest_streak_days} day
                {stats.longest_streak_days === 1 ? '' : 's'}
              </span>
            </p>
            <p className="mt-0.5 text-xs text-[#94A3B8]">
              Total XP {stats.total_xp.toLocaleString()} · {stats.rank}
            </p>
          </div>
        </div>

        <div className="mt-4 space-y-1.5">
          <Bar pct={xpPct} />
          <div className="flex justify-between text-xs text-[#64748B]">
            <span>
              {Math.round(xpPct)}% to {nextRankLabel}
            </span>
            <span>
              {xpRemaining > 0
                ? `${xpRemaining} XP to go`
                : 'Rank milestone reached'}
            </span>
          </div>
        </div>

        <div className="mt-5 grid grid-cols-3 divide-x divide-[#E2E8F0] border-t border-[#F1F5F9] pt-4">
          <div className="pr-3 text-center sm:text-left">
            <p className="text-xs text-[#94A3B8]">Challenges done</p>
            <p className="mt-1 text-xl font-bold tabular-nums text-[#0F172A]">
              {stats.challenges_completed}
            </p>
          </div>
          <div className="px-3 text-center">
            <p className="text-xs text-[#94A3B8]">Accuracy</p>
            <p className="mt-1 text-xl font-bold tabular-nums text-[#0F172A]">
              {stats.overall_accuracy_pct != null
                ? `${Math.round(stats.overall_accuracy_pct)}%`
                : '—'}
            </p>
          </div>
          <div className="pl-3 text-center sm:text-right">
            <p className="text-xs text-[#94A3B8]">Day streak</p>
            <p className="mt-1 text-xl font-bold tabular-nums text-[#0F172A]">
              {stats.current_streak_days}
            </p>
          </div>
        </div>

        <div className="mt-4 rounded-xl bg-[#EFF6FF] px-4 py-3">
          <p className="text-sm leading-relaxed text-[#1E40AF]">
            {bannerText}
            {secondaryLine ? (
              <>
                {' '}
                {secondaryLine}
              </>
            ) : null}
          </p>
        </div>
      </section>

      {/* Status badges */}
      <div className="flex flex-wrap items-center gap-x-5 gap-y-2 px-0.5 text-sm">
        <span className="inline-flex items-center gap-2 text-[#334155]">
          <span
            className={`h-2 w-2 rounded-full ${
              stats.psychometric_completed ? 'bg-[#10B981]' : 'bg-[#CBD5E1]'
            }`}
          />
          {stats.psychometric_completed
            ? 'Psychometric profile complete'
            : 'Psychometric profile incomplete'}
        </span>
        <span className="inline-flex items-center gap-2 text-[#334155]">
          <span
            className={`h-2 w-2 rounded-full ${
              stats.wassce_uploaded ? 'bg-[#10B981]' : 'bg-[#CBD5E1]'
            }`}
          />
          {stats.wassce_uploaded
            ? 'WASSCE results uploaded (refine)'
            : 'WASSCE optional — not required for matches'}
        </span>
      </div>

      {/* This Week */}
      {weekly ? (
        <section className="rounded-2xl border border-[#E2E8F0] bg-white/95 p-5 shadow-sm backdrop-blur-sm sm:p-6">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
            <div className="flex flex-wrap items-baseline gap-2">
              <h3 className="text-base font-bold text-[#0F172A]">This Week</h3>
              <span className="text-xs text-[#94A3B8]">
                {weekly.week_start} – {weekly.week_end}
              </span>
            </div>
            <span className="rounded-full bg-[#EFF6FF] px-2.5 py-1 text-xs font-semibold text-[#2563EB]">
              {weekly.xp_earned}/{weekly.xp_goal} XP
            </span>
          </div>
          <ul className="divide-y divide-[#F1F5F9]">
            {[
              {
                label: 'Challenges Completed',
                value: String(weekly.challenges_completed),
              },
              {
                label: 'Learning Center Topics Studied',
                value: String(weekly.learning_topics_studied),
              },
              { label: 'XP Earned', value: `+${weekly.xp_earned}` },
              {
                label: 'Accuracy',
                value:
                  weekly.accuracy_pct != null
                    ? `${weekly.accuracy_pct}%`
                    : '—',
              },
              {
                label: 'Learning Streak',
                value: `${weekly.learning_streak_days} Day${
                  weekly.learning_streak_days === 1 ? '' : 's'
                }`,
              },
            ].map((row) => (
              <li
                key={row.label}
                className="flex items-center justify-between gap-3 py-2.5 text-sm"
              >
                <span className="text-[#475569]">{row.label}</span>
                <span className="font-semibold tabular-nums text-[#0F172A]">
                  {row.value}
                </span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      {/* Accuracy + Streak */}
      {accuracyMeter && streakMeter ? (
        <div className="grid gap-4 sm:grid-cols-2">
          <AccuracyRing meter={accuracyMeter} />
          <div className="flex flex-col justify-between rounded-2xl border border-[#FDE68A]/80 bg-gradient-to-br from-[#FFFBEB] to-white p-5 shadow-sm">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-wider text-[#D97706]">
                Learning streak
              </p>
              <p className="mt-2 text-3xl font-bold tabular-nums text-[#92400E]">
                {Math.round(streakMeter.current)}{' '}
                <span className="text-base font-semibold text-[#B45309]">
                  day{Math.round(streakMeter.current) === 1 ? '' : 's'}
                </span>
              </p>
            </div>
            <div className="mt-4">
              <div className="inline-flex rounded-lg border border-[#FDE68A] bg-white/80 px-2.5 py-1.5 text-xs font-medium text-[#92400E]">
                Next milestone: {Math.round(streakMeter.target)} days
              </div>
              <div className="mt-3">
                <Bar
                  pct={streakMeter.pct}
                  color="bg-[#D97706]"
                  track="bg-[#FEF3C7]"
                />
              </div>
              {streakMeter.detail ? (
                <p className="mt-2 text-xs leading-relaxed text-[#B45309]">
                  {streakMeter.detail}
                </p>
              ) : null}
            </div>
          </div>
        </div>
      ) : null}

      {/* Progress breakdown */}
      {xpMeter && phaseMeter && levelMeter ? (
        <section className="space-y-5 rounded-2xl border border-[#E2E8F0] bg-white/95 p-5 shadow-sm backdrop-blur-sm sm:p-6">
          <ProgressRow
            label="XP Progress"
            pct={xpMeter.pct}
            detail={xpMeter.detail}
            color="bg-[#2563EB]"
            track="bg-[#DBEAFE]"
          />
          <ProgressRow
            label="Phase Progress"
            pct={phaseMeter.pct}
            detail={phaseMeter.detail}
            color="bg-[#2563EB]"
            track="bg-[#DBEAFE]"
          />
          <ProgressRow
            label="Level Completion"
            pct={levelMeter.pct}
            detail={levelMeter.detail}
            color="bg-[#10B981]"
            track="bg-[#D1FAE5]"
          />
        </section>
      ) : null}

      <ProgressExtensionSlot module={futureModules?.leaderboard ?? null} />
    </motion.div>
  );
}
