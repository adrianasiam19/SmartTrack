'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FormEvent, useEffect, useMemo, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Eye, EyeOff, Lock, ChevronDown } from 'lucide-react';
import { clearClientSession, register, startGoogleSignIn, Programme } from '../lib/authApi';

interface PasswordRequirement { label: string; met: boolean; }

// All programmes — only General Science is available for now
const ALL_PROGRAMMES: Programme[] = ['General Science', 'General Arts', 'Business', 'Visual Arts', 'Home Economics', 'Technical'];
const AVAILABLE_PROGRAMME: Programme = 'General Science';

const getPasswordRequirements = (password: string): PasswordRequirement[] => [
  { label: 'At least 8 characters', met: password.length >= 8 },
  { label: 'One uppercase letter', met: /[A-Z]/.test(password) },
  { label: 'One lowercase letter', met: /[a-z]/.test(password) },
  { label: 'One number', met: /[0-9]/.test(password) },
  { label: 'One special character (@, #, !, etc.)', met: /[@#_!$%^&*\-+=[\]{};:'\",.<>?/\\|`~()]/.test(password) },
];

const isPasswordStrong = (password: string): boolean => getPasswordRequirements(password).every((r) => r.met);

export default function Register() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [programme, setProgramme] = useState<Programme | ''>('');
  const [school, setSchool] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [progDropdownOpen, setProgDropdownOpen] = useState(false);
  const progDropdownRef = useRef<HTMLDivElement>(null);

  // Creating an account must never inherit another user's client session.
  useEffect(() => {
    clearClientSession();
  }, []);

  // Close programme dropdown on outside click
  useEffect(() => {
    if (!progDropdownOpen) return;
    const handleClick = (e: MouseEvent) => {
      if (progDropdownRef.current && !progDropdownRef.current.contains(e.target as Node)) {
        setProgDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [progDropdownOpen]);

  const passwordRequirements = useMemo(() => getPasswordRequirements(password), [password]);
  const passwordsMatch = !!password && password === confirmPassword;
  const formReady = fullName.trim().length >= 2 && !!email && !!programme && isPasswordStrong(password) && passwordsMatch;

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    if (!isPasswordStrong(password)) { setError('Please satisfy every password requirement before continuing.'); return; }
    if (!passwordsMatch) { setError('Passwords do not match.'); return; }
    if (!programme) { setError('Please choose your programme.'); return; }
    setIsLoading(true);
    try {
      await register({ email: email.trim(), password, full_name: fullName.trim(), programme, school: school.trim() || null });
      router.push('/onboarding');
    } catch (err) { setError(err instanceof Error ? err.message : 'Registration failed'); }
    finally { setIsLoading(false); }
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

  const inputBase = 'w-full px-4 py-3 bg-white border border-[#CBD5E1] rounded-xl text-[#1E293B] placeholder-[#94A3B8] focus:ring-2 focus:ring-[#2563EB] focus:border-transparent outline-none transition text-base';

  return (
    <div className="min-h-screen bg-transparent flex items-center justify-center p-4 py-10">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
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
            <h1 className="text-2xl font-bold text-[#1E293B] mb-2">Create your account</h1>
            <p className="text-base text-[#475569]">Set up your profile and start your journey.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Full Name</label>
              <input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} className={inputBase} placeholder="e.g. Ama Owusu" required disabled={isLoading} />
            </div>
            <div>
              <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Email</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className={inputBase} placeholder="your.email@example.com" required disabled={isLoading} />
            </div>
            <div className="relative" ref={progDropdownRef}>
              <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Programme</label>
              <button
                type="button"
                onClick={() => !isLoading && setProgDropdownOpen(!progDropdownOpen)}
                className={`w-full flex items-center justify-between px-4 py-3 bg-white border rounded-xl text-base transition ${programme ? 'text-[#1E293B]' : 'text-[#94A3B8]'} ${progDropdownOpen ? 'ring-2 ring-[#2563EB] border-transparent' : 'border-[#CBD5E1]'}`}
              >
                <span>{programme || 'Choose your programme'}</span>
                <ChevronDown className={`w-4 h-4 text-[#94A3B8] transition-transform ${progDropdownOpen ? 'rotate-180' : ''}`} />
              </button>
              {progDropdownOpen && (
                <div className="absolute z-20 mt-1 w-full bg-white border border-[#E2E8F0] rounded-xl shadow-lg overflow-hidden">
                  {ALL_PROGRAMMES.map((p) => {
                    const isAvailable = p === AVAILABLE_PROGRAMME;
                    const isSelected = programme === p;
                    return (
                      <button
                        key={p}
                        type="button"
                        disabled={!isAvailable}
                        onClick={() => {
                          if (isAvailable) {
                            setProgramme(p);
                            setProgDropdownOpen(false);
                          }
                        }}
                        className={`w-full flex items-center gap-3 px-4 py-3 text-left text-sm transition ${
                          isSelected ? 'bg-[#EEF2FF] text-[#2563EB] font-medium' : ''
                        } ${
                          isAvailable
                            ? 'hover:bg-[#F8FAFC] cursor-pointer text-[#1E293B]'
                            : 'text-[#94A3B8] cursor-not-allowed'
                        }`}
                      >
                        <span className="flex-1">{p}</span>
                        {!isAvailable && <Lock className="w-3.5 h-3.5 text-[#CBD5E1]" />}
                        {isSelected && isAvailable && (
                          <svg className="w-4 h-4 text-[#2563EB]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 13l4 4L19 7" />
                          </svg>
                        )}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-[#1E293B] mb-1.5">School Name <span className="text-[#94A3B8] font-normal">(optional)</span></label>
              <input type="text" value={school} onChange={(e) => setSchool(e.target.value)} className={inputBase} placeholder="e.g. Achimota School" disabled={isLoading} />
            </div>
            <div>
              <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Password</label>
              <div className="relative">
                <input type={showPassword ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 pr-11 py-3 bg-white border border-[#CBD5E1] rounded-xl text-[#1E293B] placeholder-[#94A3B8] focus:ring-2 focus:ring-[#2563EB] focus:border-transparent outline-none transition text-base"
                  placeholder="Create a strong password" required disabled={isLoading} />
                <button type="button" onClick={() => setShowPassword((s) => !s)} className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              {password && (
                <div className="mt-2 p-3.5 bg-[#EFF6FF] border border-[#BFDBFE] rounded-xl space-y-1.5">
                  {passwordRequirements.map((req) => (
                    <div key={req.label} className="flex items-center gap-2.5 text-sm">
                      <span className={`w-4 h-4 rounded-full flex items-center justify-center ${req.met ? 'bg-[#2563EB]' : 'bg-[#94A3B8]'}`}>
                        {req.met && <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" /></svg>}
                      </span>
                      <span className={req.met ? 'text-[#2563EB] font-medium' : 'text-[#475569]'}>{req.label}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-[#1E293B] mb-1.5">Confirm Password</label>
              <div className="relative">
                <input type={showConfirmPassword ? 'text' : 'password'} value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)}
                  className={`w-full px-4 pr-11 py-3 bg-white border rounded-xl text-[#1E293B] placeholder-[#94A3B8] focus:ring-2 focus:ring-[#2563EB] focus:border-transparent outline-none transition text-base ${confirmPassword && password !== confirmPassword ? 'border-[#DC2626]' : 'border-[#CBD5E1]'}`}
                  placeholder="Re-enter your password" required disabled={isLoading} />
                <button type="button" onClick={() => setShowConfirmPassword((s) => !s)} className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                  {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              {confirmPassword && password !== confirmPassword && (
                <p className="text-sm text-[#DC2626] mt-1.5 font-medium">Passwords do not match</p>
              )}
            </div>
            {error && (
              <div className="p-3.5 bg-[#FEF2F2] border border-[#FECACA] rounded-xl">
                <p className="text-sm text-[#DC2626]">{error}</p>
              </div>
            )}
            <button type="submit" disabled={isLoading || !formReady}
              className="w-full bg-gradient-to-r from-[#2563EB] to-[#1D4ED8] text-white py-3 rounded-xl font-semibold text-base hover:from-[#3B82F6] hover:to-[#2563EB] shadow-lg shadow-[#2563EB]/25 hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed">
              {isLoading ? 'Creating your profile...' : 'Create Account'}
            </button>
          </form>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-[#E2E8F0]" />
            </div>
            <div className="relative flex justify-center">
              <span className="bg-white px-3 text-sm text-[#94A3B8]">or</span>
            </div>
          </div>

          {/* Google OAuth */}
          <button
            type="button"
            onClick={handleGoogle}
            disabled={isLoading || isGoogleLoading}
            className="flex items-center justify-center gap-3 w-full px-6 py-3 border border-[#E2E8F0] rounded-xl text-[#475569] font-medium text-base hover:bg-[#F8FAFC] hover:border-[#CBD5E1] transition-all duration-200 disabled:opacity-50"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            <span>{isGoogleLoading ? 'Redirecting to Google…' : 'Continue with Google'}</span>
          </button>

          <p className="text-center text-sm text-[#64748B] mt-6">
            Already have an account?{' '}<Link href="/login" className="text-[#2563EB] hover:text-[#1D4ED8] font-semibold">Sign in</Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
