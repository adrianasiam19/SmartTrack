'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/challenges', label: 'Challenges' },
  { href: '/learning', label: 'Learning' },
  { href: '/recommendations', label: 'Recommendations' },
  { href: '/profile', label: 'Profile' },
];

export default function BottomNav() {
  const pathname = usePathname();

  const hiddenPaths = ['/', '/login', '/register', '/onboarding'];
  if (hiddenPaths.some((p) => pathname === p || pathname.startsWith('/onboarding'))) {
    return null;
  }

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-50 border-t border-gray-200 bg-white/95 backdrop-blur-sm lg:hidden"
      style={{ paddingBottom: 'env(safe-area-inset-bottom, 0px)' }}
    >
      <div className="flex h-14 items-stretch justify-around px-1">
        {NAV_ITEMS.map((item) => {
          const isActive =
            pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex flex-1 flex-col items-center justify-center px-1 py-1 rounded-lg transition-all min-w-0 ${
                isActive ? 'text-[#4F46E5]' : 'text-gray-400 hover:text-gray-600'
              }`}
            >
              <span
                className={`text-[10px] sm:text-[11px] font-medium leading-tight truncate ${
                  isActive ? 'font-semibold' : ''
                }`}
              >
                {item.label}
              </span>
              {isActive ? (
                <div className="mt-1 w-5 h-0.5 bg-[#4F46E5] rounded-full" />
              ) : null}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
