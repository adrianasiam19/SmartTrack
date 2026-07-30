/**
 * Tracks returning users after they log out once (persists across sessions).
 * Key avoids atlas_/smarttrack_ prefixes so clearClientSession keeps it.
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

/** True after this account has logged out at least once (then signed in again). */
export function hasPriorDashboardVisit(userId: string): boolean {
  if (!userId) return false;
  return Boolean(readReturningMap()[userId]);
}

/**
 * Call on logout so the next sign-in shows "Welcome back".
 * Do NOT call on first dashboard paint — that would flip the greeting mid-session.
 */
export function markDashboardVisited(userId: string): void {
  if (typeof window === 'undefined' || !userId) return;
  const map = readReturningMap();
  if (map[userId]) return;
  map[userId] = true;
  window.localStorage.setItem(RETURNING_DASHBOARD_KEY, JSON.stringify(map));
}
