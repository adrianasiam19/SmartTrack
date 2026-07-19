import { beforeEach, describe, expect, it } from 'vitest';

import {
  clearClientSession,
  getAuthEpoch,
  getStoredUser,
  resolvePostAuthDestination,
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
    onboarding_completed: false,
    starter_arena_completed: false,
    xp: 0,
    rank: 'Beginner',
    streak: 0,
    ...overrides,
  };
}

describe('resolvePostAuthDestination', () => {
  it('sends brand-new users to onboarding', () => {
    expect(
      resolvePostAuthDestination({
        onboarding_completed: false,
        starter_arena_completed: false,
      }),
    ).toBe('/onboarding');
  });

  it('sends walkthrough-complete users to Starter Arena only', () => {
    expect(
      resolvePostAuthDestination({
        onboarding_completed: true,
        starter_arena_completed: false,
      }),
    ).toBe('/challenges/arena?mode=placement');
  });

  it('sends fully onboarded returning users to the dashboard', () => {
    expect(
      resolvePostAuthDestination({
        onboarding_completed: true,
        starter_arena_completed: true,
      }),
    ).toBe('/dashboard');
  });

  it('never skips Starter Arena when the completion flag is missing', () => {
    expect(
      resolvePostAuthDestination({
        onboarding_completed: true,
        starter_arena_completed: undefined as unknown as boolean,
      }),
    ).toBe('/challenges/arena?mode=placement');
  });
});

describe('auth session isolation', () => {
  beforeEach(() => {
    window.localStorage.clear();
    window.sessionStorage.clear();
    clearClientSession();
  });

  it('bumps the auth epoch and wipes user-scoped keys on clear', () => {
    const before = getAuthEpoch();
    window.localStorage.setItem('atlas_academic_data', 'true');
    window.localStorage.setItem('atlas_completed_lessons', '["x"]');
    window.localStorage.setItem('atlas_revision_bookmarks', '[]');

    const after = clearClientSession();

    expect(after).toBe(before + 1);
    expect(window.localStorage.getItem('atlas_academic_data')).toBeNull();
    expect(window.localStorage.getItem('atlas_completed_lessons')).toBeNull();
    expect(window.localStorage.getItem('atlas_revision_bookmarks')).toBeNull();
  });

  it('refuses to cache a profile that does not match the access token subject', () => {
    storeTokens({
      access_token: makeJwt('user-b'),
      refresh_token: 'refresh-b',
    });

    const accepted = storeUser(makeUser({ id: 'user-a', onboarding_completed: true, starter_arena_completed: true }));
    expect(accepted).toBe(false);
    expect(getStoredUser()).toBeNull();

    const ok = storeUser(makeUser({ id: 'user-b' }));
    expect(ok).toBe(true);
    expect(getStoredUser()?.id).toBe('user-b');
  });

  it('ignores stale storeUser writes after the auth epoch changes', () => {
    storeTokens({
      access_token: makeJwt('user-a'),
      refresh_token: 'refresh-a',
    });
    const epochA = getAuthEpoch();
    storeUser(makeUser({ id: 'user-a', onboarding_completed: true, starter_arena_completed: true }), epochA);

    clearClientSession();
    storeTokens({
      access_token: makeJwt('user-b'),
      refresh_token: 'refresh-b',
    });
    storeUser(makeUser({ id: 'user-b', onboarding_completed: false, starter_arena_completed: false }));

    // A completion write that still holds User A's epoch must not poison User B.
    const poisoned = storeUser(
      makeUser({ id: 'user-b', onboarding_completed: true, starter_arena_completed: true }),
      epochA,
    );
    expect(poisoned).toBe(false);
    expect(getStoredUser()?.onboarding_completed).toBe(false);
    expect(getStoredUser()?.starter_arena_completed).toBe(false);
  });

  it('drops a cached profile when it no longer matches the current token', () => {
    storeTokens({
      access_token: makeJwt('user-a'),
      refresh_token: 'refresh-a',
    });
    storeUser(makeUser({ id: 'user-a', onboarding_completed: true, starter_arena_completed: true }));

    // Simulate a token swap without going through storeUser (race survivor).
    window.localStorage.setItem('accessToken', makeJwt('user-b'));
    window.localStorage.setItem('refreshToken', 'refresh-b');

    expect(getStoredUser()).toBeNull();
  });
});
