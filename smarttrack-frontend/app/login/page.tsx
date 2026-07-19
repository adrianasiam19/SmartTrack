'use client';

import { useEffect, useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { Eye, EyeOff, WifiOff, RefreshCw } from 'lucide-react';
import Link from 'next/link';
import {
  clearClientSession,
  login,
  resolvePostAuthDestination,
  startGoogleSignIn,
} from '../lib/authApi';

export default function Login() {
  const router = useRouter();
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [isNetworkError, setIsNetworkError] = useState(false);

  // Warm the common post-login routes so navigation feels instant.
  useEffect(() => {
    router.prefetch('/dashboard');
    router.prefetch('/onboarding');
    router.prefetch('/challenges/arena?mode=placement');
  }, [router]);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setIsNetworkError(false);
    setIsLoading(true);
    try {
      const formData = new FormData(e.currentTarget);
      const user = await login({
        email: formData.get('email') as string,
        password: formData.get('password') as string,
      });
      // Navigate immediately — login() already loaded and cached the profile.
      router.replace(resolvePostAuthDestination(user));
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setError(message);
      setIsNetworkError(message.toLowerCase().includes('connect to the server'));
      setIsLoading(false);
    }
  };

  const handleGoogle = async () => {
    setError('');
    setIsGoogleLoading(true);
    try {
      await startGoogleSignIn();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Google Sign-In failed');
      setIsGoogleLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center p-4">
      <div className="w-full max-w-md animate-fade-in">
        <div className="flex justify-center mb-8">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-[#2563EB] to-[#7C3AED] rounded-xl flex items-center justify-center shadow-lg shadow-[#2563EB]/20">
              <span className="text-white font-bold text-lg">A</span>
            </div>
            <span className="text-2xl font-bold text-[#1E293B]">Atlas</span>
          </Link>
        </div>

        <div className="bg-white rounded-2xl border border-[#BFDBFE] p-8 lg:p-10 shadow-xl shadow-[#2563EB]/5">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-[#1E293B] mb-2">Welcome back</h1>
            <p className="text-base text-[#475569]">Sign in to continue your learning journey</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-[#1E293B] mb-1.5">
                Email
              </label>
              <input
                type="email"
                name="email"
                id="email"
                required
                disabled={isLoading || isGoogleLoading}
                className="w-full px-4 py-3 bg-white border border-[#CBD5E1] rounded-xl text-[#1E293B] placeholder-[#94A3B8] focus:ring-2 focus:ring-[#2563EB] focus:border-transparent outline-none transition text-base"
                placeholder="your.email@example.com"
              />
            </div>
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label htmlFor="password" className="block text-sm font-medium text-[#1E293B]">
                  Password
                </label>
                <Link
                  href="/forgot-password"
                  onClick={() => clearClientSession()}
                  className="text-sm font-medium text-[#2563EB] hover:text-[#1D4ED8]"
                >
                  Forgot Password?
                </Link>
              </div>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  id="password"
                  required
                  disabled={isLoading || isGoogleLoading}
                  className="w-full px-4 pr-11 py-3 bg-white border border-[#CBD5E1] rounded-xl text-[#1E293B] placeholder-[#94A3B8] focus:ring-2 focus:ring-[#2563EB] focus:border-transparent outline-none transition text-base"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((s) => !s)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>
            {error && (
              <div
                className={`p-3.5 rounded-xl ${
                  isNetworkError
                    ? 'bg-[#FFFBEB] border border-[#FDE68A]'
                    : 'bg-[#FEF2F2] border border-[#FECACA]'
                }`}
              >
                <div className="flex items-start gap-2.5">
                  {isNetworkError && <WifiOff className="w-5 h-5 text-[#D97706] mt-0.5 shrink-0" />}
                  <div className="flex-1">
                    <p className={`text-sm ${isNetworkError ? 'text-[#92400E]' : 'text-[#DC2626]'}`}>
                      {error}
                    </p>
                    {isNetworkError && (
                      <button
                        type="button"
                        onClick={() => {
                          setError('');
                          setIsNetworkError(false);
                        }}
                        className="mt-2 inline-flex items-center gap-1.5 text-xs font-medium text-[#D97706] hover:text-[#92400E] transition-colors"
                      >
                        <RefreshCw className="w-3.5 h-3.5" />
                        Dismiss & try again
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )}
            <button
              type="submit"
              disabled={isLoading || isGoogleLoading}
              className="w-full bg-gradient-to-r from-[#2563EB] to-[#1D4ED8] text-white py-3 rounded-xl font-semibold text-base hover:from-[#3B82F6] hover:to-[#2563EB] shadow-lg shadow-[#2563EB]/25 hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-[#E2E8F0]" />
            </div>
            <div className="relative flex justify-center">
              <span className="bg-white px-3 text-sm text-[#94A3B8]">or</span>
            </div>
          </div>

          <button
            type="button"
            onClick={handleGoogle}
            disabled={isLoading || isGoogleLoading}
            className="flex items-center justify-center gap-3 w-full px-6 py-3 border border-[#E2E8F0] rounded-xl text-[#475569] font-medium text-base hover:bg-[#F8FAFC] hover:border-[#CBD5E1] transition-all duration-200 disabled:opacity-50"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            <span>{isGoogleLoading ? 'Redirecting to Google…' : 'Continue with Google'}</span>
          </button>

          <p className="text-center text-sm text-[#64748B] mt-6">
            Don&apos;t have an account?{' '}
            <Link href="/register" className="text-[#2563EB] hover:text-[#1D4ED8] font-semibold">
              Create one
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
