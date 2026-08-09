'use client';

import Link from 'next/link';
import { FormEvent, useState } from 'react';
import { requestPasswordReset } from '../lib/authApi';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [devLink, setDevLink] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setDevLink(null);

    const trimmed = email.trim().toLowerCase();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
      setError('Please enter a valid email address.');
      return;
    }

    setIsLoading(true);
    try {
      const result = await requestPasswordReset(trimmed);
      setSuccess(
        result.message ||
          'Password reset instructions have been sent to your email address.',
      );
      if (result.dev_reset_link) setDevLink(result.dev_reset_link);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to send reset email.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-transparent flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="flex justify-center mb-8">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-[#2563EB] to-[#7C3AED] rounded-xl flex items-center justify-center shadow-lg shadow-[#2563EB]/20">
              <span className="text-white font-bold text-lg">A</span>
            </div>
            <span className="text-2xl font-bold text-[#1E293B]">Atlas</span>
          </Link>
        </div>

        <div className="bg-white rounded-2xl border border-[#BFDBFE] p-8 shadow-xl shadow-[#2563EB]/5">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-[#1E293B] mb-2">Forgot password?</h1>
            <p className="text-base text-[#475569]">
              Enter your registered email and we&apos;ll send reset instructions.
            </p>
          </div>

          {success ? (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-[#EEF2FF] border border-[#C7D2FE]">
                <p className="text-sm text-[#1E293B] leading-relaxed">{success}</p>
              </div>
              {devLink && (
                <div className="p-4 rounded-xl bg-[#FFFBEB] border border-[#FDE68A]">
                  <p className="text-xs text-[#92400E] mb-2">
                    Development mode — use this link (not shown in production):
                  </p>
                  <Link href={devLink} className="text-sm text-[#2563EB] break-all underline">
                    {devLink}
                  </Link>
                </div>
              )}
              <Link
                href="/login"
                className="block w-full text-center px-5 py-3 rounded-xl bg-[#2563EB] text-white font-semibold hover:bg-[#1D4ED8] transition"
              >
                Back to Sign In
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-[#1E293B] mb-1.5">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={isLoading}
                  className="w-full px-4 py-3 bg-white border border-[#CBD5E1] rounded-xl text-[#1E293B] placeholder-[#94A3B8] focus:ring-2 focus:ring-[#2563EB] focus:border-transparent outline-none transition text-base"
                  placeholder="your.email@example.com"
                />
              </div>

              {error && (
                <div className="p-3.5 rounded-xl bg-[#FEF2F2] border border-[#FECACA]">
                  <p className="text-sm text-[#DC2626]">{error}</p>
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-[#2563EB] to-[#1D4ED8] text-white py-3 rounded-xl font-semibold text-base hover:from-[#3B82F6] hover:to-[#2563EB] shadow-lg shadow-[#2563EB]/25 transition-all disabled:opacity-50"
              >
                {isLoading ? 'Sending…' : 'Send reset instructions'}
              </button>

              <p className="text-center text-sm text-[#64748B]">
                Remembered your password?{' '}
                <Link href="/login" className="text-[#2563EB] font-semibold hover:underline">
                  Sign in
                </Link>
              </p>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
