'use client';

/**
 * Stage 5 — modular mount point for optional Progress Dashboard extensions.
 *
 * When `future_modules.leaderboard.enabled` is false (MVP default), this
 * renders nothing. Flip the backend flag + supply payload later to mount
 * rankings here without changing Stages 1–4 layout contracts.
 */
import type { ReactNode } from 'react';
import type { LeaderboardModuleConfig } from '../lib/progressApi';

type Props = {
  module?: LeaderboardModuleConfig | null;
  /** Optional custom UI when the module is enabled. */
  children?: ReactNode;
};

/**
 * Host for a future leaderboard. Safe no-op until payload exists.
 * Replace / extend this when shipping competitive rankings.
 */
export function LeaderboardModuleHost({
  module,
}: {
  module: LeaderboardModuleConfig;
}) {
  if (!module.enabled || !module.payload) {
    return null;
  }

  // Future: map module.payload.entries into a rankings UI.
  // Kept intentionally empty so enabling the flag alone cannot leak rankings.
  return (
    <section
      data-progress-module="leaderboard"
      data-mount-point={module.mount_point}
      data-module-version={module.version}
      className="border-t border-[#F1F5F9] px-4 py-5 sm:px-6"
      aria-hidden
    />
  );
}

export default function ProgressExtensionSlot({ module, children }: Props) {
  if (!module?.enabled) {
    return null;
  }

  return (
    <div
      data-progress-extension="leaderboard"
      data-mount-point={module.mount_point}
      data-enabled="true"
    >
      {children ?? <LeaderboardModuleHost module={module} />}
    </div>
  );
}
