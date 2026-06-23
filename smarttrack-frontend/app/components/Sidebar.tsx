'use client';

import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { LogOut } from 'lucide-react';
import { useState, useEffect } from 'react';
import {
  logout,
  getAccessToken,
  getStoredUser,
  getCurrentUser,
  UserProfile,
} from '../lib/authApi';

const navItems = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/learning', label: 'Learning Center' },
  { href: '/challenges/daily-streak', label: 'Daily Streak' },
  { href: '/recommendations', label: 'Recommendations' },
  { href: '/profile', label: 'Profile' },
];

export default function Sidebar() {
  const router = useRouter();
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

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

  return (
    <>
      {mobileOpen && (
        <div className="fixed inset-0 bg-black/40 z-40 lg:hidden" onClick={() => setMobileOpen(false)} />
      )}

      <button
        onClick={() => setMobileOpen(true)}
        className="lg:hidden fixed top-4 left-4 z-50 p-3 bg-white border border-[#C7D2FE] rounded-xl shadow-md text-[#4F46E5] hover:bg-[#EEF2FF] transition-all"
        aria-label="Open navigation"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      <aside
        onMouseEnter={() => setCollapsed(false)}
        onMouseLeave={() => setCollapsed(true)}
        className={`
          hidden lg:flex flex-col h-screen sticky top-0 z-30
          bg-gradient-to-b from-white to-[#EEF2FF] border-r border-[#C7D2FE]
          transition-all duration-200 ease-in-out
          ${collapsed ? 'w-16' : 'w-60'}
        `}
      >
        <div className={`flex items-center border-b border-[#C7D2FE] ${collapsed ? 'justify-center' : 'px-5'} py-5 h-16`}>
          {collapsed ? (
            <div className="w-9 h-9 bg-gradient-to-br from-[#4F46E5] to-[#D97706] rounded-xl flex items-center justify-center shadow-md">
              <span className="text-white font-bold text-base">A</span>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-[#4F46E5] to-[#D97706] rounded-xl flex items-center justify-center shadow-md shadow-[#4F46E5]/20">
                <span className="text-white font-bold text-lg">A</span>
              </div>
              <span className="text-xl font-bold text-[#1E293B]">Atlas</span>
            </div>
          )}
        </div>

        <nav className="flex-1 py-5 px-2.5 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const active = isActive(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`
                  flex items-center rounded-xl transition-all
                  ${collapsed ? 'justify-center px-2 py-3.5' : 'px-4 py-3'}
                  ${active
                    ? 'bg-[#4F46E5] text-white font-bold shadow-md shadow-[#4F46E5]/30'
                    : 'text-[#475569] hover:bg-[#E0E7FF] hover:text-[#4F46E5]'
                  }
                `}
                title={collapsed ? item.label : undefined}
              >
                {!collapsed && (
                  <span className="text-base truncate">{item.label}</span>
                )}
                {collapsed && (
                  <span className="text-sm font-bold">{item.label.charAt(0)}</span>
                )}
              </Link>
            );
          })}
        </nav>

        <div className={`border-t border-[#C7D2FE] p-3 ${collapsed ? 'text-center' : ''}`}>
          {!loading && user ? (
            <div className="space-y-2">
              <div className={`flex items-center gap-3 ${collapsed ? 'justify-center' : ''}`}>
                <div className="w-9 h-9 bg-gradient-to-br from-[#4F46E5] to-[#D97706] rounded-xl flex items-center justify-center text-white text-sm font-bold flex-shrink-0 shadow-sm">
                  {getInitials(user.full_name)}
                </div>
                {!collapsed && (
                  <div className="flex-1 min-w-0">
                    <p className="text-base font-bold text-[#1E293B] truncate">{user.full_name}</p>
                    <p className="text-sm text-[#475569] truncate">{user.programme || 'SHS Student'}</p>
                  </div>
                )}
              </div>
              {!collapsed && (
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-[#475569] hover:text-[#F43F5E] hover:bg-[#FFF1F2] rounded-xl transition-all"
                >
                  <LogOut className="w-4 h-4" />
                  Sign Out
                </button>
              )}
            </div>
          ) : (
            !loading && !collapsed && (
              <Link href="/login" className="block text-center text-base text-[#4F46E5] hover:text-[#4338CA] font-bold py-2">
                Sign In
              </Link>
            )
          )}
          {collapsed && user && (
            <button onClick={handleLogout} className="mt-2 text-[#475569] hover:text-[#F43F5E]" title="Sign Out">
              <LogOut className="w-4 h-4 mx-auto" />
            </button>
          )}
        </div>
      </aside>

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
                  className={`flex items-center px-4 py-3 rounded-xl transition-all text-base ${
                    active
                      ? 'bg-[#4F46E5] text-white font-bold shadow-md'
                      : 'text-[#475569] hover:bg-[#EEF2FF] hover:text-[#4F46E5]'
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
              <Link href="/login" className="text-base text-[#4F46E5] hover:text-[#4338CA] font-bold">
                Sign In
              </Link>
            )}
          </div>
        </div>
      </aside>
    </>
  );
}
