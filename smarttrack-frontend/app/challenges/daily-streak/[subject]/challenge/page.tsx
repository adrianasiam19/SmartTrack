'use client';

import { Suspense, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import AppLayout from '../../../../components/AppLayout';

/**
 * Legacy daily-streak challenge route had an empty question bank.
 * Send students into the live Atlas Challenge Hub instead.
 */
function RedirectToAtlas() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const level = searchParams.get('level') || '1';
    const params = new URLSearchParams({
      autostart: '1',
      level,
    });
    router.replace(`/challenges/atlas?${params.toString()}`);
  }, [router, searchParams]);

  return (
    <AppLayout>
      <div className="flex min-h-screen items-center justify-center px-6">
        <div className="flex flex-col items-center gap-4 text-center">
          <div className="w-10 h-10 border-2 border-[#2563EB] border-t-transparent rounded-full animate-spin" />
          <p className="text-sm font-medium text-[#1E293B]">
            Opening live challenge questions…
          </p>
        </div>
      </div>
    </AppLayout>
  );
}

export default function DailyStreakChallengePage() {
  return (
    <Suspense
      fallback={
        <AppLayout>
          <div className="flex min-h-screen items-center justify-center">
            <div className="w-10 h-10 border-2 border-[#2563EB] border-t-transparent rounded-full animate-spin" />
          </div>
        </AppLayout>
      }
    >
      <RedirectToAtlas />
    </Suspense>
  );
}
