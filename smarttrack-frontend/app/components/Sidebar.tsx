'use client';

import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { useState, useEffect, useRef } from 'react';
import {
  logout,
  getAccessToken,
  getStoredUser,
  getCurrentUser,
  UserProfile,
} from '../lib/authApi';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: 'D' },
  { href: '/learning', label: 'Learning Center', icon: 'L' },
  { href: '/recommendations', label: 'Recommendations', icon: 'R' },
  { href: '/profile', label: 'Profile', icon: 'P' },
];

export default function Sidebar() {
  const router = useRouter();
  const pathname = usePathname();
  const [retracted, setRetracted] = useState(true);   // user's chosen state
  const [hoverExpanded, setHoverExpanded] = useState(false); // temporary hover override
  const [mobileOpen, setMobileOpen] = useState(false);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const sidebarRef = useRef<HTMLElement>(null);

  const hiddenPaths = ['/', '/login', '/register', '/onboarding'];
  if (hiddenPaths.some((p) => pathname === p || pathname.startsWith('/onboarding'))) {
    return null;
  }

  // Derived: sidebar is "open" = user pinned it OR hovering over collapsed sidebar
  const isExpanded = !retracted || hoverExpanded;

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

  const getInitials = (name: string | undefined) => {
    if (!name) return '?';
    return name.split(' ').filter(Boolean).map((n) => n[0]).join('').toUpperCase().slice(0, 2);
  };

  const handleLogout = async () => {
    try { await logout(); } catch {}
    setUser(null);
    router.push('/');
  };

  const isActive = (href: string) => {
    if (href === '/dashboard') return pathname === href;
    return pathname.startsWith(href);
  };

  const handleToggle = () => {
    setRetracted((prev) => !prev);
    // Clear hover state when toggling
    setHoverExpanded(false);
  };

  return (
    <>
      {/* ── Mobile overlay backdrop ── */}
      {mobileOpen && (
        <div className="fixed inset-0 bg-black/40 z-40 lg:hidden" onClick={() => setMobileOpen(false)} />
      )}

      {/* ── Mobile hamburger ── */}
      <button
        onClick={() => setMobileOpen(true)}
        className="lg:hidden fixed top-4 left-4 z-50 p-3 bg-white border border-[#BFDBFE] rounded-xl shadow-md text-[#2563EB] hover:bg-[#EFF6FF] transition-all"
        aria-label="Open navigation"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {/* ── Desktop sidebar ── */}
      <aside
        ref={sidebarRef}
        onMouseEnter={() => setHoverExpanded(true)}
        onMouseLeave={() => setHoverExpanded(false)}
        className={`
          hidden lg:flex flex-col h-screen sticky top-0 z-30
          bg-gradient-to-b from-white to-[#EEF2FF] border-r border-[#C7D2FE]
          transition-all duration-300 ease-[cubic-bezier(0.4,0,0.2,1)]
          ${isExpanded ? 'w-60' : 'w-16'}
          group
        `}
      >
        {/* ── Logo area ── */}
        <div className={`flex items-center border-b border-[#C7D2FE] ${isExpanded ? 'px-5' : 'justify-center'} py-5 h-16 relative`}>
          {isExpanded ? (
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-[#2563EB] to-[#7C3AED] rounded-xl flex items-center justify-center shadow-md shadow-[#2563EB]/20">
                <span className="text-white font-bold text-lg">A</span>
              </div>
              <span className="text-xl font-bold text-[#1E293B]">Atlas</span>
            </div>
          ) : (
            <div className="w-9 h-9 bg-gradient-to-br from-[#2563EB] to-[#7C3AED] rounded-xl flex items-center justify-center shadow-md">
              <span className="text-white font-bold text-base">A</span>
            </div>
          )}

          {/* ── Toggle button ── */}
          <button
            onClick={handleToggle}
            className={`
              absolute top-1/2 -translate-y-1/2 z-20
              flex items-center justify-center
              w-5 h-10 rounded-l-none rounded-r-md
              bg-[#EEF2FF] border border-[#C7D2FE] border-l-0
              text-[#475569] hover:text-[#2563EB] hover:bg-[#DBEAFE]
              transition-all duration-200
              ${isExpanded ? 'right-0 translate-x-[calc(100%)]' : '-right-0 translate-x-[calc(100%)]'}
              opacity-0 group-hover:opacity-100
              focus:opacity-100
              cursor-pointer
            `}
            aria-label={isExpanded ? 'Collapse sidebar' : 'Expand sidebar'}
            title={isExpanded ? 'Collapse sidebar' : 'Expand sidebar'}
          >
            <svg
              className="w-3 h-3 transition-transform duration-200"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {isExpanded ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M15 19l-7-7 7-7" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 5l7 7-7 7" />
              )}
            </svg>
          </button>
        </div>

        {/* ── Navigation ── */}
        <nav className="flex-1 py-5 px-2.5 space-y-1 overflow-y-auto overflow-x-hidden">
          {navItems.map((item) => {
            const active = isActive(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`
                  flex items-center rounded-xl transition-all duration-200
                  ${isExpanded ? 'px-4 py-3' : 'justify-center px-2 py-3.5'}
                  ${active
                    ? 'bg-[#2563EB] text-white font-bold shadow-md shadow-[#2563EB]/30'
                    : 'text-[#475569] hover:bg-[#EFF6FF] hover:text-[#2563EB]'
                  }
                  group/link
                `}
                title={!isExpanded ? item.label : undefined}
              >
                {/* Icon letter when collapsed */}
                {!isExpanded && (
                  <span className="text-sm font-bold">{item.icon}</span>
                )}
                {/* Label when expanded */}
                {isExpanded && (
                  <span className="text-base truncate">{item.label}</span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* ── User section ── */}
        <div className={`border-t border-[#C7D2FE] transition-all duration-300 ${isExpanded ? 'p-3' : 'py-3'}`}>
          {!loading && user ? (
            <div className="space-y-2">
              {/* Avatar row */}
              <div className={`flex items-center gap-3 ${!isExpanded ? 'justify-center' : ''}`}>
                <div className="w-9 h-9 bg-gradient-to-br from-[#2563EB] to-[#7C3AED] rounded-xl flex items-center justify-center text-white text-sm font-bold flex-shrink-0 shadow-sm">
                  {getInitials(user.full_name)}
                </div>
                {isExpanded && (
                  <div className="flex-1 min-w-0">
                    <p className="text-base font-bold text-[#1E293B] truncate">{user.full_name}</p>
                    <p className="text-sm text-[#475569] truncate">{user.programme || 'SHS Student'}</p>
                  </div>
                )}
              </div>

              {/* Sign out button */}
              {isExpanded && (
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-[#475569] hover:text-[#F43F5E] hover:bg-[#FFF1F2] rounded-xl transition-all"
                >
                  Sign Out
                </button>
              )}
              {!isExpanded && (
                <div className="flex justify-center">
                  <button
                    onClick={handleLogout}
                    className="text-[#475569] hover:text-[#F43F5E] transition-colors p-1"
                    title="Sign Out"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                  </button>
                </div>
              )}
            </div>
          ) : (
            !loading && isExpanded && (
              <Link href="/login" className="block text-center text-base text-[#2563EB] hover:text-[#1D4ED8] font-bold py-2">
                Sign In
              </Link>
            )
          )}
          {!loading && !user && !isExpanded && (
            <div className="flex justify-center">
              <Link href="/login" title="Sign In">
                <svg className="w-4 h-4 text-[#475569]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                </svg>
              </Link>
            </div>
          )}
        </div>
      </aside>

      {/* ── Mobile sidebar (overlay) ── */}
      <aside
        className={`
          lg:hidden fixed inset-y-0 left-0 z-50 w-72
          bg-white border-r border-[#C7D2FE]
          transform transition-transform duration-300 ease-in-out shadow-2xl
          ${mobileOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        <div className="flex flex-col h-full">
          <div className="flex items-center justify-between px-5 py-5 border-b border-[#C7D2FE]">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-[#4F46E5] to-[#D97706] rounded-xl flex items-center justify-center shadow-sm">
                <span className="text-white font-bold text-lg">A</span>
              </div>
              <span className="text-xl font-bold text-[#1E293B]">Atlas</span>
            </div>
            <button onClick={() => setMobileOpen(false)} className="p-2 rounded-xl hover:bg-[#EEF2FF] text-[#475569]">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <nav className="flex-1 py-5 px-3 space-y-1">
            {navItems.map((item) => {
              const active = isActive(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileOpen(false)}
                  className={`flex items-center px-4 py-3 rounded-xl transition-all text-base${
                    active
                      ? 'bg-[#2563EB] text-white font-bold shadow-md'
                      : 'text-[#475569] hover:bg-[#EFF6FF] hover:text-[#2563EB]'
                  }`}
                >
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          <div className="border-t border-[#C7D2FE] p-5">
            {user ? (
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-[#4F46E5] to-[#D97706] rounded-xl flex items-center justify-center text-white text-base font-bold flex-shrink-0">
                  {getInitials(user.full_name)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-base font-bold text-[#1E293B] truncate">{user.full_name}</p>
                  <button onClick={handleLogout} className="text-sm text-[#475569] hover:text-[#F43F5E]">
                    Sign Out
                  </button>
                </div>
              </div>
            ) : (
              <Link href="/login" className="text-base text-[#2563EB] hover:text-[#1D4ED8] font-bold">
                Sign In
              </Link>
            )}
          </div>
        </div>
      </aside>
    </>
  );
}
