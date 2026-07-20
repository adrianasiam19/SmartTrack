/**
 * Tracks whether a user has visited the dashboard before (persists across logout).
 * Key intentionally avoids atlas_/smarttrack_ prefixes so clearClientSession keeps it.
 */
const RETURNING_DASHBOARD_KEY = 'returningDashboardUsers';

function readReturningMap(): Record<string, true> {
  if (typeof window === 'undefined') return {};
  try {
    const raw = window.localStorage.getItem(RETURNING_DASHBOARD_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw) as unknown;
    return parsed && typeof parsed === 'object' ? (parsed as Record<string, true>) : {};
  } catch {
    return {};
  }
}

/** True if this account has opened the dashboard on a prior session. */
export function hasPriorDashboardVisit(userId: string): boolean {
  if (!userId) return false;
  return Boolean(readReturningMap()[userId]);
}

/** Remember that this account has seen the dashboard (call after first welcome). */
export function markDashboardVisited(userId: string): void {
  if (typeof window === 'undefined' || !userId) return;
  const map = readReturningMap();
  if (map[userId]) return;
  map[userId] = true;
  window.localStorage.setItem(RETURNING_DASHBOARD_KEY, JSON.stringify(map));
}
