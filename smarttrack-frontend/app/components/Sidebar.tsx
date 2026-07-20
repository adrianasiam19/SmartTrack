'use client';

import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import {
  logout,
  getAccessToken,
  getStoredUser,
  getCurrentUser,
  UserProfile,
} from '../lib/authApi';

function buildNavItems() {
  return [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/challenges', label: 'Challenges' },
    { href: '/learning', label: 'Learning' },
    { href: '/recommendations', label: 'Recommendations' },
    { href: '/profile', label: 'Profile' },
  ];
}

export default function Sidebar() {
  const router = useRouter();
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const sidebarRef = useRef<HTMLElement>(null);

  const navItems = useMemo(() => buildNavItems(), []);

  const hiddenPaths = ['/', '/login', '/register', '/onboarding'];
  if (hiddenPaths.some((p) => pathname === p || pathname.startsWith('/onboarding'))) {
    return null;
  }

  useEffect(() => {
    const loadUser = async () => {
      try {
        if (!getAccessToken()) { setUser(null); return; }
        const cached = getStoredUser();
        if (cached) setUser(cached);
        const fresh = await getCurrentUser();
        setUser(fresh);
      } catch { setUser(null); }
      finally { setLoading(false); }
    };
    loadUser();
  }, [pathname]);

  // Close sidebar when route changes
  useEffect(() => {
    setIsOpen(false);
  }, [pathname]);

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setIsOpen(false);
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  const getInitials = (name: string | undefined) => {
    if (!name) return '?';
    return name.split(' ').filter(Boolean).map((n) => n[0]).join('').toUpperCase().slice(0, 2);
  };

  const handleLogout = async () => {
    try { await logout(); } catch {}
    setUser(null);
    setIsOpen(false);
    router.replace('/login');
  };

  const handleToggle = useCallback(() => {
    setIsOpen((prev) => !prev);
  }, []);

  const handleClose = useCallback(() => {
    setIsOpen(false);
  }, []);

  const isActive = (href: string) => {
    if (href === '/dashboard') return pathname === href;
    return pathname.startsWith(href);
  };

  return (
    <>
      {/* ── Hamburger trigger button ── */}
      <button
        onClick={handleToggle}
        className={`
          fixed top-4 left-4 z-50
          flex items-center justify-center
          w-11 h-11
          bg-white border border-[#BFDBFE] rounded-xl
          shadow-md shadow-[#2563EB]/10
          text-[#2563EB] hover:bg-[#EFF6FF] hover:shadow-lg
          active:scale-95
          transition-all duration-200 ease-out
          ${isOpen ? 'opacity-0 pointer-events-none scale-90' : 'opacity-100'}
        `}
        aria-label="Open navigation menu"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
          <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
        </svg>
      </button>

      {/* ── Backdrop overlay ── */}
      <div
        className={`
          fixed inset-0 z-40
          bg-gradient-to-r from-[#1E293B]/60 to-[#475569]/30
          backdrop-blur-[2px]
          transition-all duration-300 ease-out
          ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}
        `}
        onClick={handleClose}
        aria-hidden="true"
      />

      {/* ── Sidebar panel ── */}
      <aside
        ref={sidebarRef}
        className={`
          fixed top-0 left-0 z-50 h-full
          w-72 max-w-[85vw]
          bg-white border-r border-[#C7D2FE]
          shadow-2xl shadow-[#1E293B]/20
          transform transition-all duration-300 ease-[cubic-bezier(0.32,0.72,0,1)]
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
        aria-label="Sidebar navigation"
      >
        <div className="flex flex-col h-full">
          {/* ── Header with logo + close ── */}
          <div className="flex items-center justify-between px-5 py-5 border-b border-[#C7D2FE] flex-shrink-0">
            <Link href="/dashboard" onClick={handleClose} className="flex items-center gap-3 group">
              <div className="w-10 h-10 bg-gradient-to-br from-[#2563EB] to-[#7C3AED] rounded-xl flex items-center justify-center shadow-md shadow-[#2563EB]/20 group-hover:shadow-lg group-hover:shadow-[#2563EB]/30 transition-shadow">
                <span className="text-white font-bold text-lg">A</span>
              </div>
              <span className="text-xl font-bold text-[#1E293B]">Atlas</span>
            </Link>
            <button
              onClick={handleClose}
              className="p-2 rounded-xl hover:bg-[#EEF2FF] text-[#475569] hover:text-[#2563EB] transition-all active:scale-90"
              aria-label="Close navigation menu"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* ── Navigation links ── */}
          <nav className="flex-1 py-5 px-3 space-y-1 overflow-y-auto">
            {navItems.map((item) => {
              const active = isActive(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={handleClose}
                  className={`
                    flex items-center gap-3 px-4 py-3 rounded-xl
                    transition-all duration-200 text-base
                    ${active
                      ? 'bg-[#2563EB] text-white font-bold shadow-md shadow-[#2563EB]/30'
                      : 'text-[#475569] hover:bg-[#EFF6FF] hover:text-[#2563EB]'
                    }
                  `}
                >
                  {/* Icon */}
                  <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5">
                    {item.href === '/dashboard' && (
                      <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12l8.954-8.955a1.126 1.126 0 011.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
                    )}
                    {item.href === '/challenges' && (
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
                    )}
                    {(item.href === '/learning') && (
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
                    )}
                    {item.href === '/recommendations' && (
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    )}
                    {item.href === '/profile' && (
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
                    )}
                  </svg>
                  <span className="truncate">{item.label}</span>

                  {/* Active indicator dot */}
                  {active && (
                    <span className="ml-auto w-1.5 h-1.5 rounded-full bg-white/80 flex-shrink-0" />
                  )}
                </Link>
              );
            })}
          </nav>

          {/* ── User section ── */}
          <div className="border-t border-[#C7D2FE] p-5 flex-shrink-0">
            {!loading && user ? (
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-[#2563EB] to-[#7C3AED] rounded-xl flex items-center justify-center text-white text-base font-bold flex-shrink-0 shadow-sm">
                    {getInitials(user.full_name)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-base font-bold text-[#1E293B] truncate">{user.full_name}</p>
                    <p className="text-sm text-[#475569] truncate">{user.programme || 'Student'}</p>
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center justify-center gap-2 px-3 py-2.5 text-sm font-medium text-[#475569] hover:text-[#DC2626] hover:bg-[#FEF2F2] rounded-xl transition-all active:scale-[0.98]"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
                  </svg>
                  Sign Out
                </button>
              </div>
            ) : (
              !loading && (
                <Link
                  href="/login"
                  onClick={handleClose}
                  className="flex items-center justify-center gap-2 w-full px-3 py-2.5 text-sm font-semibold text-[#2563EB] hover:text-[#1D4ED8] hover:bg-[#EFF6FF] rounded-xl transition-all"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
                  </svg>
                  Sign In
                </Link>
              )
            )}
          </div>
        </div>
      </aside>
    </>
  );
}
