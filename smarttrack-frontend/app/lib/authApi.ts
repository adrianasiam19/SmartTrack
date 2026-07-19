/**
 * authApi.ts
 * ──────────
 * Authentication API utilities for communicating with the backend.
 *
 * Persistence rules:
 *   • Access + refresh tokens live in localStorage.
 *   • The user profile is stored as one canonical object under `atlasUser`,
 *     always shaped exactly like the backend `UserPublic` response.
 *   • Consumers should treat `getCurrentUser()` (backend) as the source of
 *     truth and use `getStoredUser()` only for instant first paint.
 *
 * Session isolation:
 *   • Every login/register/logout bumps an in-memory auth epoch.
 *   • Stale async writes from a previous user are ignored after the epoch changes.
 *   • Profiles are only cached when their `id` matches the JWT `sub`.
 *   • All Atlas user-scoped localStorage keys are wiped on auth transitions.
 */

const API_BASE_URL =
  (typeof process !== 'undefined' && process.env.NEXT_PUBLIC_API_URL) ||
  'http://localhost:8000/api/v1';

export type Programme = 'General Science' | 'General Arts' | 'Business' | 'Visual Arts' | 'Home Economics' | 'Technical';
export type SHSLevel = 'SHS 1' | 'SHS 2' | 'SHS 3' | 'Completed SHS';

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  is_verified: boolean;
  avatar_url: string | null;
  created_at: string;

  // SHS onboarding
  programme: Programme | null;
  shs_level: SHSLevel | null;
  school: string | null;
  onboarding_completed: boolean;
  starter_arena_completed: boolean;
  learner_profile?: Record<string, unknown> | null;

  // Gamification
  xp: number;
  rank: string;
  streak: number;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  programme: Programme;
  shs_level: SHSLevel;
  school?: string | null;
}

export interface LoginRequest {
  email: string;
  password: string;
}

const STORAGE_KEYS = {
  accessToken: 'accessToken',
  refreshToken: 'refreshToken',
  user: 'atlasUser',
} as const;

/** Exact keys that belong to a previous Atlas user/session. */
const USER_SCOPED_EXACT_KEYS = [
  STORAGE_KEYS.accessToken,
  STORAGE_KEYS.refreshToken,
  STORAGE_KEYS.user,
  'atlasUserEmail',
  'atlasChallengeData',
  'atlas_academic_data',
  'atlas_completed_lessons',
  'atlas_daily_streak_visited',
  'atlas_revision_bookmarks',
  'atlas_revision_history',
  'atlas_revision_recent',
] as const;

/**
 * In-memory generation counter. Incremented on every auth boundary so async
 * work started for User A cannot mutate User B's client state.
 */
let authEpoch = 0;

const isBrowser = (): boolean => typeof window !== 'undefined';

export const getAuthEpoch = (): number => authEpoch;

/** Decode the JWT `sub` claim without verifying the signature (client-side binding only). */
export const getTokenUserId = (): string | null => {
  const token = getAccessToken();
  if (!token) return null;
  try {
    const [, payloadPart] = token.split('.');
    if (!payloadPart) return null;
    const normalized = payloadPart.replace(/-/g, '+').replace(/_/g, '/');
    const padded = normalized.padEnd(normalized.length + ((4 - (normalized.length % 4)) % 4), '=');
    const payload = JSON.parse(atob(padded)) as { sub?: unknown };
    return typeof payload.sub === 'string' && payload.sub.length > 0 ? payload.sub : null;
  } catch {
    return null;
  }
};

const removeMatchingStorageKeys = (storage: Storage): void => {
  const keys: string[] = [];
  for (let i = 0; i < storage.length; i += 1) {
    const key = storage.key(i);
    if (!key) continue;
    const isExact = (USER_SCOPED_EXACT_KEYS as readonly string[]).includes(key);
    const isPrefixed =
      key.startsWith('atlas_') ||
      key.startsWith('atlasUser') ||
      key.startsWith('smarttrack_');
    if (isExact || isPrefixed) keys.push(key);
  }
  keys.forEach((key) => storage.removeItem(key));
};

/**
 * Wipe every piece of client auth + user-scoped state and invalidate in-flight writers.
 * Returns the new auth epoch.
 */
export const clearClientSession = (): number => {
  authEpoch += 1;
  if (!isBrowser()) return authEpoch;

  removeMatchingStorageKeys(window.localStorage);
  removeMatchingStorageKeys(window.sessionStorage);

  // Belt-and-braces for the canonical auth keys.
  window.localStorage.removeItem(STORAGE_KEYS.accessToken);
  window.localStorage.removeItem(STORAGE_KEYS.refreshToken);
  window.localStorage.removeItem(STORAGE_KEYS.user);

  return authEpoch;
};

/** @deprecated Prefer clearClientSession — kept as a compatible alias. */
export const clearTokens = (): void => {
  clearClientSession();
};

export const storeTokens = (tokens: AuthTokens): void => {
  if (!isBrowser()) return;
  window.localStorage.setItem(STORAGE_KEYS.accessToken, tokens.access_token);
  window.localStorage.setItem(STORAGE_KEYS.refreshToken, tokens.refresh_token);
};

/**
 * Store the full user profile exactly as the backend returned it.
 * Refuses writes that belong to a previous auth epoch or a different JWT subject.
 */
export const storeUser = (user: UserProfile, epoch?: number): boolean => {
  if (!isBrowser()) return false;
  if (epoch !== undefined && epoch !== authEpoch) {
    console.warn('Ignored stale storeUser from a previous auth session');
    return false;
  }

  const tokenUserId = getTokenUserId();
  if (tokenUserId && user.id && user.id !== tokenUserId) {
    console.warn('Ignored storeUser for a profile that does not match the access token');
    return false;
  }

  window.localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(user));
  return true;
};

/** Retrieve cached user profile (may be stale; refetch when possible). */
export const getStoredUser = (): UserProfile | null => {
  if (!isBrowser()) return null;
  const raw = window.localStorage.getItem(STORAGE_KEYS.user);
  if (!raw) return null;
  try {
    const user = JSON.parse(raw) as UserProfile;
    const tokenUserId = getTokenUserId();
    // A cached profile that does not match the current token is poisoned — drop it.
    if (tokenUserId && user.id && user.id !== tokenUserId) {
      window.localStorage.removeItem(STORAGE_KEYS.user);
      return null;
    }
    return user;
  } catch {
    window.localStorage.removeItem(STORAGE_KEYS.user);
    return null;
  }
};

export const getAccessToken = (): string | null => {
  if (!isBrowser()) return null;
  return window.localStorage.getItem(STORAGE_KEYS.accessToken);
};

export const getRefreshToken = (): string | null => {
  if (!isBrowser()) return null;
  return window.localStorage.getItem(STORAGE_KEYS.refreshToken);
};

export const getAuthHeaders = (): HeadersInit => {
  const token = getAccessToken();
  if (!token) return { 'Content-Type': 'application/json' };
  return {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
};

/**
 * Attempt a fetch with automatic retry on network errors.
 * Returns [response, wasRetried].
 */
async function fetchWithRetry(
  url: string,
  options: RequestInit,
  maxRetries = 2,
  delayMs = 1000,
): Promise<[Response, boolean]> {
  let lastError: unknown;
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const res = await fetch(url, options);
      return [res, attempt > 0];
    } catch (err) {
      lastError = err;
      if (attempt < maxRetries) {
        console.warn(`fetch attempt ${attempt + 1} failed, retrying...`, err);
        await new Promise((r) => setTimeout(r, delayMs * (attempt + 1)));
      }
    }
  }
  throw lastError;
}

/**
 * Extract a human-friendly message from a fetch error.
 * The browser throws `TypeError: Failed to fetch` when the server is unreachable.
 */
export function getFetchErrorMessage(err: unknown): string {
  if (err instanceof TypeError && err.message === 'Failed to fetch') {
    return 'Unable to connect to the server. Please check that the backend is running (port 8000) and try again.';
  }
  if (err instanceof Error) return err.message;
  return 'An unexpected error occurred. Please try again.';
}

async function installAuthSession(tokens: AuthTokens): Promise<UserProfile | null> {
  const epoch = clearClientSession();
  storeTokens(tokens);
  try {
    const userProfile = await getCurrentUser(epoch);
    storeUser(userProfile, epoch);
    return userProfile;
  } catch (e) {
    console.warn('Failed to fetch user profile after auth transition:', e);
    return null;
  }
}

/** Canonical frontend redirect URI registered with Google Cloud Console. */
export const getGoogleRedirectUri = (): string => {
  if (typeof window === 'undefined') return 'http://localhost:3000/auth/callback';
  return `${window.location.origin}/auth/callback`;
};

/**
 * Start Google Sign-In: clear any previous session, fetch the consent URL,
 * then navigate to Google.
 */
export const startGoogleSignIn = async (): Promise<void> => {
  clearClientSession();
  const redirectUri = getGoogleRedirectUri();
  let response: Response;
  try {
    [response] = await fetchWithRetry(
      `${API_BASE_URL}/auth/google/url?redirect_uri=${encodeURIComponent(redirectUri)}`,
      { method: 'GET' },
      1,
      500,
    );
  } catch (err) {
    throw new Error(getFetchErrorMessage(err));
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Google Sign-In is unavailable right now.');
  }

  const data = (await response.json()) as { url?: string };
  if (!data.url) {
    throw new Error('Google Sign-In is unavailable right now.');
  }
  window.location.href = data.url;
};

/**
 * Finish Google Sign-In after Google redirects back with an authorization code.
 */
export const completeGoogleSignIn = async (
  code: string,
  redirectUri: string = getGoogleRedirectUri(),
): Promise<UserProfile | null> => {
  let response: Response;
  try {
    [response] = await fetchWithRetry(
      `${API_BASE_URL}/auth/google/callback`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, redirect_uri: redirectUri }),
      },
      1,
      500,
    );
  } catch (err) {
    throw new Error(getFetchErrorMessage(err));
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Failed to complete Google Sign-In.');
  }

  const tokens: AuthTokens = await response.json();
  return installAuthSession(tokens);
};

export const requestPasswordReset = async (
  email: string,
): Promise<{ message: string; dev_reset_link?: string | null }> => {
  let response: Response;
  try {
    [response] = await fetchWithRetry(
      `${API_BASE_URL}/auth/forgot-password`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim().toLowerCase() }),
      },
      1,
      500,
    );
  } catch (err) {
    throw new Error(getFetchErrorMessage(err));
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Unable to send password reset email.');
  }

  return response.json();
};

export const resetPassword = async (
  token: string,
  password: string,
): Promise<{ message: string }> => {
  let response: Response;
  try {
    [response] = await fetchWithRetry(
      `${API_BASE_URL}/auth/reset-password`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, password }),
      },
      1,
      500,
    );
  } catch (err) {
    throw new Error(getFetchErrorMessage(err));
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Unable to reset password.');
  }

  return response.json();
};

/**
 * Register a new account.
 * Always starts from a clean client session so no previous user state can leak.
 * Returns the installed profile when available so callers can route immediately.
 */
export const register = async (data: RegisterRequest): Promise<UserProfile | null> => {
  // Drop any previous user before contacting the API so in-flight writers are invalidated early.
  clearClientSession();

  let response: Response;
  try {
    [response] = await fetchWithRetry(
      `${API_BASE_URL}/auth/register`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      },
    );
  } catch (err) {
    throw new Error(getFetchErrorMessage(err));
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Registration failed');
  }

  const tokens: AuthTokens = await response.json();
  return installAuthSession(tokens);
};

/**
 * Log in with email + password.
 * Retries automatically on transient network errors.
 * Returns the installed profile so the UI can navigate without a second /me fetch.
 */
export const login = async (data: LoginRequest): Promise<UserProfile | null> => {
  clearClientSession();

  let response: Response;
  try {
    [response] = await fetchWithRetry(
      `${API_BASE_URL}/auth/login`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      },
    );
  } catch (err) {
    throw new Error(getFetchErrorMessage(err));
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Login failed');
  }

  const tokens: AuthTokens = await response.json();
  return installAuthSession(tokens);
};

/**
 * fetchWithAuth — A fetch wrapper that automatically adds the auth header,
 * handles 401 by refreshing the access token, and retries the original request.
 *
 * If the refresh also fails the user is redirected to login.
 */
export async function fetchWithAuth(
  url: string,
  options: RequestInit = {},
): Promise<Response> {
  const doFetch = (token?: string): Promise<Response> => {
    const isFormData =
      typeof FormData !== 'undefined' && options.body instanceof FormData;
    const headers: Record<string, string> = {
      ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
    if (options.headers) {
      const callerHeaders = options.headers as Record<string, string>;
      Object.assign(headers, callerHeaders);
    }
    // Let the browser set multipart boundary for FormData uploads.
    if (isFormData) {
      delete headers['Content-Type'];
    }
    return fetch(url, { ...options, headers });
  };

  let token = getAccessToken();
  let res = await doFetch(token ?? undefined);

  if (res.status === 401 && token) {
    try {
      const newToken = await refreshAccessToken();
      res = await doFetch(newToken);
    } catch {
      if (typeof window !== 'undefined') {
        clearClientSession();
        window.location.href = '/login';
      }
      throw new Error('Session expired. Please log in again.');
    }
  }

  return res;
}

/**
 * Fetch the authenticated user from the backend.
 * The backend is the source of truth — also keeps localStorage in sync.
 *
 * On 401, tries a refresh-token rotation before clearing the client session.
 * That prevents mid-session login kicks when only the short-lived access token expired.
 */
export const getCurrentUser = async (epoch: number = authEpoch): Promise<UserProfile> => {
  const requestProfile = async (): Promise<Response> => {
    const [response] = await fetchWithRetry(
      `${API_BASE_URL}/users/me`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
      },
      1,
      500,
    );
    return response;
  };

  let response: Response;
  try {
    response = await requestProfile();
  } catch (err) {
    if (err instanceof TypeError) {
      throw new Error('Unable to connect to the server to load your profile.');
    }
    throw new Error('Failed to fetch user profile');
  }

  if (epoch !== authEpoch) {
    throw new Error('Auth session changed');
  }

  if (response.status === 401) {
    try {
      await refreshAccessToken();
      if (epoch !== authEpoch) {
        throw new Error('Auth session changed');
      }
      response = await requestProfile();
    } catch (refreshErr) {
      if (refreshErr instanceof Error && refreshErr.message === 'Auth session changed') {
        throw refreshErr;
      }
      // refreshAccessToken clears on hard failure; keep this as a safety net.
      if (epoch === authEpoch) {
        clearClientSession();
      }
      throw new Error('Unauthorized');
    }
  }

  if (epoch !== authEpoch) {
    throw new Error('Auth session changed');
  }

  if (!response.ok) {
    if (response.status === 401) {
      if (epoch === authEpoch) clearClientSession();
      throw new Error('Unauthorized');
    }
    throw new Error('Failed to fetch user profile');
  }

  const user = (await response.json()) as UserProfile;
  if (epoch !== authEpoch) {
    throw new Error('Auth session changed');
  }
  storeUser(user, epoch);
  return user;
};

export const logout = async (): Promise<void> => {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    clearClientSession();
    return;
  }

  try {
    await fetchWithRetry(
      `${API_BASE_URL}/auth/logout`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      },
      1,
      500,
    );
  } catch (error) {
    console.error('Logout error (server unreachable):', error);
  } finally {
    clearClientSession();
  }
};

export const refreshAccessToken = async (): Promise<string> => {
  const epoch = authEpoch;
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }

  let response: Response;
  try {
    [response] = await fetchWithRetry(
      `${API_BASE_URL}/auth/refresh`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      },
      1,
      500,
    );
  } catch {
    clearClientSession();
    throw new Error('Unable to connect to the server. Please log in again.');
  }

  if (!response.ok) {
    clearClientSession();
    throw new Error('Session expired. Please log in again.');
  }

  if (epoch !== authEpoch) {
    throw new Error('Auth session changed');
  }

  const data: { access_token: string } = await response.json();
  if (!isBrowser()) return data.access_token;
  window.localStorage.setItem(STORAGE_KEYS.accessToken, data.access_token);
  return data.access_token;
};

export const updateUserProfile = async (
  data: Partial<
    Pick<
      UserProfile,
      | 'full_name'
      | 'avatar_url'
      | 'programme'
      | 'shs_level'
      | 'school'
      | 'onboarding_completed'
      | 'starter_arena_completed'
    >
  >,
): Promise<UserProfile> => {
  const epoch = authEpoch;
  const expectedUserId = getTokenUserId();

  let response: Response;
  try {
    // Use refresh-aware helper so expired access tokens don't fail profile updates.
    response = await fetchWithAuth(`${API_BASE_URL}/users/me`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  } catch (err) {
    throw new Error(getFetchErrorMessage(err));
  }

  if (epoch !== authEpoch) {
    throw new Error('Auth session changed');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Failed to update profile');
  }

  const user = (await response.json()) as UserProfile;
  if (epoch !== authEpoch) {
    throw new Error('Auth session changed');
  }
  if (expectedUserId && user.id !== expectedUserId) {
    throw new Error('Auth session changed');
  }

  storeUser(user, epoch);
  return user;
};

/**
 * Decide where an authenticated user should go next.
 * Decisions must be based only on the currently authenticated user's flags.
 *
 * New users: onboarding → Starter Arena → dashboard (each step only once).
 * Returning users: dashboard.
 */
export function resolvePostAuthDestination(
  user: Pick<UserProfile, 'onboarding_completed' | 'starter_arena_completed'> | null | undefined,
): '/onboarding' | '/challenges/arena?mode=placement' | '/dashboard' {
  if (!user) return '/onboarding';
  if (!user.onboarding_completed) return '/onboarding';
  // New accounts always persist an explicit boolean. Treat any non-true value
  // as "Starter Arena still required" so a missing/stale field never skips it.
  if (user.starter_arena_completed !== true) {
    return '/challenges/arena?mode=placement';
  }
  return '/dashboard';
}

export const isAuthenticated = (): boolean => !!getAccessToken();
