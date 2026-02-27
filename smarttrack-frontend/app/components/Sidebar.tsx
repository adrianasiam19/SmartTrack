'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, FileEdit, BookOpen, Target, User, Brain, Settings, X } from 'lucide-react';
import ThemeToggle from './ThemeToggle';
import { useState } from 'react';

export default function Sidebar() {
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navItems = [
    { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { href: '/assessment', icon: FileEdit, label: 'Assessment' },
    { href: '/learning', icon: BookOpen, label: 'Learning' },
    { href: '/recommendations', icon: Target, label: 'Programs' },
    { href: '/profile', icon: User, label: 'Profile' },
  ];

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white/10 backdrop-blur-xl rounded-xl border border-white/10 text-white"
      >
        {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Brain className="w-6 h-6" />}
      </button>

      {/* Overlay for mobile */}
      {isMobileMenuOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-40
        w-64 bg-white/5 backdrop-blur-2xl border-r border-white/10 
        transform transition-transform duration-300 ease-in-out
        ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="p-4 lg:p-6 h-full flex flex-col">
          {/* Logo */}
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-gradient-to-br from-lime-400 to-emerald-500 rounded-xl flex items-center justify-center shadow-lg shadow-lime-500/30">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-semibold text-white">SmartTrack</span>
          </div>

          {/* Navigation */}
          <nav className="space-y-2 flex-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all group relative ${
                    isActive
                      ? 'bg-lime-400 text-gray-900 shadow-lg shadow-lime-500/30'
                      : 'text-gray-300 hover:bg-white/10 hover:text-white'
                  }`}
                >
                  {isActive && (
                    <div className="absolute inset-0 bg-lime-400 rounded-xl blur-xl opacity-50"></div>
                  )}
                  
                  <Icon className={`w-5 h-5 relative z-10 ${isActive ? 'text-gray-900' : ''}`} />
                  <span className={`relative z-10 font-medium ${isActive ? 'text-gray-900' : ''}`}>
                    {item.label}
                  </span>
                </Link>
              );
            })}
          </nav>

          {/* Bottom section */}
          <div className="mt-auto space-y-4">
            <div className="flex items-center justify-between">
              <Settings className="w-5 h-5 text-gray-400 hover:text-white transition-colors cursor-pointer" />
              <ThemeToggle />
            </div>
            
            {/* User card */}
            <div className="bg-white/5 backdrop-blur-xl rounded-xl p-3 border border-white/10">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-lime-400 to-emerald-500 rounded-lg flex items-center justify-center text-gray-900 font-semibold text-sm flex-shrink-0">
                  JD
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-white truncate">Juan Dela Cruz</p>
                  <p className="text-xs text-gray-400 truncate">Grade 12 Student</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
