/**
 * authApi.ts
 * ──────────
 * Authentication API utilities for communicating with the backend.
 *
 * Persistence rules:
 *   • Access + refresh tokens live in localStorage.
 *   • The user profile is stored as one canonical object under `atlasUser`,
 *     always shaped exactly like the backend `UserPublic` response.
 *     No more hardcoded names, no more `fullname` vs `full_name` drift.
 *   • Consumers should treat `getCurrentUser()` (backend) as the source of
 *     truth and use `getStoredUser()` only for instant first paint.
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

const isBrowser = (): boolean => typeof window !== 'undefined';

export const storeTokens = (tokens: AuthTokens): void => {
  if (!isBrowser()) return;
  localStorage.setItem(STORAGE_KEYS.accessToken, tokens.access_token);
  localStorage.setItem(STORAGE_KEYS.refreshToken, tokens.refresh_token);
};

/** Store the full user profile exactly as the backend returned it. */
export const storeUser = (user: UserProfile): void => {
  if (!isBrowser()) return;
  localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(user));
};

/** Retrieve cached user profile (may be stale; refetch when possible). */
export const getStoredUser = (): UserProfile | null => {
  if (!isBrowser()) return null;
  const raw = localStorage.getItem(STORAGE_KEYS.user);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as UserProfile;
  } catch {
    return null;
  }
};

export const getAccessToken = (): string | null => {
  if (!isBrowser()) return null;
  return localStorage.getItem(STORAGE_KEYS.accessToken);
};

export const getRefreshToken = (): string | null => {
  if (!isBrowser()) return null;
  return localStorage.getItem(STORAGE_KEYS.refreshToken);
};

/** Clear every piece of auth state — used on logout and on 401s. */
export const clearTokens = (): void => {
  if (!isBrowser()) return;
  localStorage.removeItem(STORAGE_KEYS.accessToken);
  localStorage.removeItem(STORAGE_KEYS.refreshToken);
  localStorage.removeItem(STORAGE_KEYS.user);
  // Legacy keys from earlier versions — clean them up so no stale data survives.
  localStorage.removeItem('atlasUserEmail');
  localStorage.removeItem('atlasChallengeData');
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
 * Register a new account.
 * After success: stores tokens, fetches user profile, caches it.
 */
export const register = async (data: RegisterRequest): Promise<AuthTokens> => {
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
  // Wipe any leftover state from a previous session, THEN store the new tokens.
  clearTokens();
  storeTokens(tokens);

  try {
    const userProfile = await getCurrentUser();
    storeUser(userProfile);
  } catch (e) {
    console.warn('Failed to fetch user profile after registration:', e);
  }

  return tokens;
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

/**
 * Log in with email + password.
 * Retries automatically on transient network errors.
 * Same persistence guarantees as `register`.
 */
export const login = async (data: LoginRequest): Promise<AuthTokens> => {
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
    // Network-level failure even after retries
    throw new Error(getFetchErrorMessage(err));
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Login failed');
  }

  const tokens: AuthTokens = await response.json();
  // Clear any previous user (different account) before installing new tokens.
  clearTokens();
  storeTokens(tokens);

  try {
    const userProfile = await getCurrentUser();
    storeUser(userProfile);
  } catch (e) {
    console.warn('Failed to fetch user profile after login:', e);
  }

  return tokens;
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
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
    // Merge any caller-provided headers last so they can override Content-Type
    if (options.headers) {
      const callerHeaders = options.headers as Record<string, string>;
      Object.assign(headers, callerHeaders);
    }
    return fetch(url, { ...options, headers });
  };

  // 1. First attempt with the current access token
  let token = getAccessToken();
  let res = await doFetch(token ?? undefined);

  // 2. If 401, try to refresh the token
  if (res.status === 401 && token) {
    try {
      const newToken = await refreshAccessToken();
      res = await doFetch(newToken);
    } catch {
      // Refresh failed — redirect to login
      if (typeof window !== 'undefined') {
        clearTokens();
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
 */
export const getCurrentUser = async (): Promise<UserProfile> => {
  let response: Response;
  try {
    [response] = await fetchWithRetry(
      `${API_BASE_URL}/users/me`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
      },
      1,  // fewer retries for profile fetch
      500,
    );
  } catch (err) {
    if (err instanceof TypeError) {
      throw new Error('Unable to connect to the server to load your profile.');
    }
    throw new Error('Failed to fetch user profile');
  }

  if (!response.ok) {
    if (response.status === 401) {
      clearTokens();
      throw new Error('Unauthorized');
    }
    throw new Error('Failed to fetch user profile');
  }

  const user = (await response.json()) as UserProfile;
  storeUser(user);
  return user;
};

export const logout = async (): Promise<void> => {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    clearTokens();
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
    clearTokens();
  }
};

export const refreshAccessToken = async (): Promise<string> => {
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
  } catch (err) {
    clearTokens();
    throw new Error('Unable to connect to the server. Please log in again.');
  }

  if (!response.ok) {
    clearTokens();
    throw new Error('Session expired. Please log in again.');
  }

  const data: { access_token: string } = await response.json();
  localStorage.setItem(STORAGE_KEYS.accessToken, data.access_token);
  return data.access_token;
};

export const updateUserProfile = async (data: Partial<Pick<UserProfile, 'full_name' | 'avatar_url' | 'programme' | 'shs_level' | 'school' | 'onboarding_completed'>>): Promise<UserProfile> => {
  let response: Response;
  try {
    [response] = await fetchWithRetry(
      `${API_BASE_URL}/users/me`,
      {
        method: 'PATCH',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      },
      1,
      500,
    );
  } catch (err) {
    throw new Error(getFetchErrorMessage(err));
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Failed to update profile');
  }

  const user = (await response.json()) as UserProfile;
  storeUser(user);
  return user;
};

export const isAuthenticated = (): boolean => !!getAccessToken();
