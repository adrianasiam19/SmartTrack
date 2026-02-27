'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FormEvent } from 'react';
import { motion } from 'framer-motion';
import { Brain, Mail, Lock, User } from 'lucide-react';

export default function Register() {
  const router = useRouter();

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-md"
      >
        <div className="bg-white/5 backdrop-blur-sm rounded-lg p-8 border border-white/10">
          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-3 mb-6">
              <div className="w-12 h-12 bg-gradient-to-br from-lime-500 to-emerald-600 rounded-lg flex items-center justify-center">
                <Brain className="w-7 h-7 text-white" />
              </div>
              <span className="text-2xl font-semibold text-white">SmartTrack</span>
            </div>
            <h1 className="text-2xl font-semibold text-white mb-2">Create Your Account</h1>
            <p className="text-gray-400">Start your journey to finding the perfect university program</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="fullname" className="block text-sm font-medium text-gray-300 mb-2">
                Full Name
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="text"
                  id="fullname"
                  className="w-full pl-11 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-lime-500 focus:border-transparent outline-none transition"
                  placeholder="Juan Dela Cruz"
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="email"
                  id="email"
                  className="w-full pl-11 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-lime-500 focus:border-transparent outline-none transition"
                  placeholder="your.email@example.com"
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="password"
                  id="password"
                  className="w-full pl-11 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-lime-500 focus:border-transparent outline-none transition"
                  placeholder="Create a strong password"
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="confirm-password" className="block text-sm font-medium text-gray-300 mb-2">
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="password"
                  id="confirm-password"
                  className="w-full pl-11 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-lime-500 focus:border-transparent outline-none transition"
                  placeholder="Re-enter your password"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-lime-500 text-white py-3 rounded-lg font-semibold hover:bg-lime-600 transition"
            >
              Register
            </button>
          </form>

          <p className="text-center text-gray-400 mt-6">
            Already have an account?{' '}
            <Link href="/login" className="text-lime-500 hover:text-lime-400 font-medium">
              Login here
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
