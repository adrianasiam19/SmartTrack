'use client';

/**
 * Competitive leaderboard is deferred for MVP.
 * Redirect learners to the Personal Progress Dashboard instead.
 */
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import AppLayout from '../../components/AppLayout';

export default function LeaderboardRedirectPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/dashboard#personal-progress');
  }, [router]);

  return (
    <AppLayout>
      <div className="flex min-h-screen items-center justify-center">
        <div className="max-w-sm px-6 text-center">
          <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-2 border-[#2563EB] border-t-transparent" />
          <p className="text-sm font-medium text-[#0F172A]">
            Taking you to Your Progress
          </p>
          <p className="mt-1.5 text-xs text-[#64748B]">
            Atlas focuses on your personal growth — not rankings against others.
          </p>
        </div>
      </div>
    </AppLayout>
  );
}
