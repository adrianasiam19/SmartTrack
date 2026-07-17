'use client';

import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import {
  completeGoogleSignIn,
  getGoogleRedirectUri,
  resolvePostAuthDestination,
} from '../../lib/authApi';

function GoogleCallbackInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;

    const finish = async () => {
      const oauthError = searchParams.get('error');
      const code = searchParams.get('code');

      if (oauthError) {
        setError('Google Sign-In was cancelled or denied. Please try again.');
        return;
      }
      if (!code) {
        setError('Missing authorization code from Google. Please try again.');
        return;
      }

      try {
        const user = await completeGoogleSignIn(code, getGoogleRedirectUri());
        if (cancelled) return;
        router.replace(resolvePostAuthDestination(user));
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : 'Google Sign-In failed.');
      }
    };

    finish();
    return () => {
      cancelled = true;
    };
  }, [router, searchParams]);

  if (error) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-white border border-[#FECACA] rounded-2xl p-8 text-center shadow-sm">
          <h1 className="text-xl font-bold text-[#1E293B] mb-2">Google Sign-In failed</h1>
          <p className="text-sm text-[#DC2626] mb-6">{error}</p>
          <div className="flex flex-col gap-3">
            <Link
              href="/login"
              className="px-5 py-3 rounded-xl bg-[#2563EB] text-white font-semibold hover:bg-[#1D4ED8] transition"
            >
              Back to Sign In
            </Link>
            <Link href="/register" className="text-sm text-[#2563EB] font-medium hover:underline">
              Create an account instead
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center p-4">
      <div className="text-center">
        <div className="w-12 h-12 border-4 border-[#2563EB] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-sm text-[#64748B]">Completing Google Sign-In…</p>
      </div>
    </div>
  );
}

export default function GoogleCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
          <div className="w-12 h-12 border-4 border-[#2563EB] border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <GoogleCallbackInner />
    </Suspense>
  );
}
