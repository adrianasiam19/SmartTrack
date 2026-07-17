import { describe, expect, it } from 'vitest';

import { resolvePostAuthDestination } from './authApi';

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

  it('treats legacy completed profiles without the new flag as returning users', () => {
    expect(
      resolvePostAuthDestination({
        onboarding_completed: true,
        starter_arena_completed: undefined as unknown as boolean,
      }),
    ).toBe('/dashboard');
  });
});
