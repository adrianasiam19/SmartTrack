import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  clearClientSession,
  getAccessToken,
  getCurrentUser,
  getStoredUser,
  storeTokens,
  storeUser,
  type UserProfile,
} from './authApi';

function makeJwt(sub: string): string {
  const header = btoa(JSON.stringify({ alg: 'none', typ: 'JWT' }));
  const payload = btoa(JSON.stringify({ sub, type: 'access' }));
  return `${header}.${payload}.sig`;
}

function makeUser(overrides: Partial<UserProfile> = {}): UserProfile {
  return {
    id: 'user-a',
    email: 'a@example.com',
    full_name: 'User A',
    is_verified: true,
    avatar_url: null,
    created_at: new Date().toISOString(),
    programme: 'General Science',
    shs_level: 'SHS 1',
    school: null,
    onboarding_completed: true,
    starter_arena_completed: true,
    xp: 12,
    rank: 'Beginner',
    streak: 1,
    ...overrides,
  };
}

describe('getCurrentUser refresh-on-401', () => {
  beforeEach(() => {
    clearClientSession();
    vi.unstubAllGlobals();
    storeTokens({
      access_token: makeJwt('user-a'),
      refresh_token: 'refresh-token-1',
      token_type: 'bearer',
    });
    storeUser(makeUser());
  });

  it('refreshes the access token and retries /users/me instead of wiping the session', async () => {
    const user = makeUser({ xp: 42 });
    const expiredAccess = makeJwt('user-a');
    const freshAccess = makeJwt('user-a'); // same sub; only the token string rotation matters for headers
    // Distinguish tokens with a different signature segment.
    const rotatedAccess = `${freshAccess}-rotated`;

    let meCalls = 0;
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes('/users/me')) {
        meCalls += 1;
        if (meCalls === 1) {
          return new Response(JSON.stringify({ detail: 'Unauthorized' }), { status: 401 });
        }
        return new Response(JSON.stringify(user), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/auth/refresh')) {
        return new Response(JSON.stringify({ access_token: rotatedAccess }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    // Ensure first request uses the expired access token we seeded.
    expect(getAccessToken()).toBe(expiredAccess);

    const result = await getCurrentUser();

    expect(result.xp).toBe(42);
    expect(getAccessToken()).toBe(rotatedAccess);
    expect(getStoredUser()?.xp).toBe(42);
    expect(meCalls).toBe(2);
    expect(fetchMock.mock.calls.some((c) => String(c[0]).includes('/auth/refresh'))).toBe(true);
  });

  it('clears the session only after refresh also fails', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes('/users/me')) {
        return new Response(JSON.stringify({ detail: 'Unauthorized' }), { status: 401 });
      }
      if (url.includes('/auth/refresh')) {
        return new Response(JSON.stringify({ detail: 'invalid' }), { status: 401 });
      }
      return new Response('not found', { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    await expect(getCurrentUser()).rejects.toThrow(/Unauthorized|Session expired/);
    expect(getAccessToken()).toBeNull();
    expect(getStoredUser()).toBeNull();
  });
});
