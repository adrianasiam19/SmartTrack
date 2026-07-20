'use client';

import Link from 'next/link';
import { FormEvent, Suspense, useMemo, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Eye, EyeOff } from 'lucide-react';
import { resetPassword } from '../lib/authApi';

interface PasswordRequirement {
  label: string;
  met: boolean;
}

const getPasswordRequirements = (password: string): PasswordRequirement[] => [
  { label: 'At least 8 characters', met: password.length >= 8 },
  { label: 'One uppercase letter', met: /[A-Z]/.test(password) },
  { label: 'One lowercase letter', met: /[a-z]/.test(password) },
  { label: 'One number', met: /[0-9]/.test(password) },
  {
    label: 'One special character (@, #, !, etc.)',
    met: /[@#_!$%^&*\-+=[\]{};:'",.<>?/\\|`~()]/.test(password),
  },
];

function ResetPasswordInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get('token') || '';

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const requirements = useMemo(() => getPasswordRequirements(password), [password]);
  const allMet = requirements.every((r) => r.met);
  const passwordsMatch = !!password && password === confirmPassword;

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!token) {
      setError('This password reset link is invalid or has expired.');
      return;
    }
    if (!allMet) {
      setError('Please satisfy every password requirement.');
      return;
    }
    if (!passwordsMatch) {
      setError('Passwords do not match.');
      return;
    }

    setIsLoading(true);
    try {
      const result = await resetPassword(token, password);
      setSuccess(result.message || 'Your password has been updated.');
      setTimeout(() => router.replace('/login'), 1800);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to reset password.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-transparent flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-white border border-[#FECACA] rounded-2xl p-8 text-center">
          <h1 className="text-xl font-bold text-[#1E293B] mb-2">Invalid reset link</h1>
          <p className="text-sm text-[#DC2626] mb-6">
            This password reset link is invalid or has expired.
          </p>
          <Link href="/forgot-password" className="text-[#2563EB] font-semibold hover:underline">
            Request a new link
          </Link>
        </div>
      </div>
    );
  }

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
            <h1 className="text-2xl font-bold text-[#1E293B] mb-2">Choose a new password</h1>
            <p className="text-base text-[#475569]">Enter a strong password for your Atlas account.</p>
          </div>

          {success ? (
            <div className="p-4 rounded-xl bg-[#EEF2FF] border border-[#C7D2FE] text-center">
              <p className="text-sm text-[#1E293B]">{success}</p>
              <p className="text-xs text-[#64748B] mt-2">Redirecting to sign in…</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[#1E293B] mb-1.5">New password</label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    disabled={isLoading}
                    className="w-full px-4 pr-11 py-3 border border-[#CBD5E1] rounded-xl outline-none focus:ring-2 focus:ring-[#2563EB]"
                    placeholder="Create a strong password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((s) => !s)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                {password && (
                  <div className="mt-2 p-3.5 bg-[#EFF6FF] border border-[#BFDBFE] rounded-xl space-y-1.5">
                    {requirements.map((req) => (
                      <div key={req.label} className="flex items-center gap-2.5 text-sm">
                        <span
                          className={`w-4 h-4 rounded-full ${req.met ? 'bg-[#2563EB]' : 'bg-[#94A3B8]'}`}
                        />
                        <span className={req.met ? 'text-[#2563EB] font-medium' : 'text-[#475569]'}>
                          {req.label}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-[#1E293B] mb-1.5">
                  Confirm password
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  disabled={isLoading}
                  className={`w-full px-4 py-3 border rounded-xl outline-none focus:ring-2 focus:ring-[#2563EB] ${
                    confirmPassword && !passwordsMatch ? 'border-[#DC2626]' : 'border-[#CBD5E1]'
                  }`}
                  placeholder="Re-enter your password"
                />
              </div>

              {error && (
                <div className="p-3.5 rounded-xl bg-[#FEF2F2] border border-[#FECACA]">
                  <p className="text-sm text-[#DC2626]">{error}</p>
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading || !allMet || !passwordsMatch}
                className="w-full bg-gradient-to-r from-[#2563EB] to-[#1D4ED8] text-white py-3 rounded-xl font-semibold disabled:opacity-50"
              >
                {isLoading ? 'Updating…' : 'Update password'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-transparent flex items-center justify-center">
          <div className="w-12 h-12 border-4 border-[#2563EB] border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <ResetPasswordInner />
    </Suspense>
  );
}
