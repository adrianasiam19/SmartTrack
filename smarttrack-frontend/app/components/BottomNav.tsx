'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/learning', label: 'Learning' },
  { href: '/recommendations', label: 'Programs' },
  { href: '/profile', label: 'Profile' },
];

export default function BottomNav() {
  const pathname = usePathname();

  const hiddenPaths = ['/', '/login', '/register', '/onboarding'];
  if (hiddenPaths.some((p) => pathname === p || pathname.startsWith('/onboarding'))) {
    return null;
  }

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 lg:hidden">
      <div className="flex items-center justify-around h-14 px-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex flex-col items-center justify-center px-2 py-1 rounded-lg transition-all min-w-0 flex-1 ${
                isActive ? 'text-[#4F46E5]' : 'text-gray-400 hover:text-gray-600'
              }`}
            >
              <span className={`text-[11px] font-medium leading-tight ${
                isActive ? 'font-semibold' : ''
              }`}>
                {item.label}
              </span>
              {isActive && (
                <div className="mt-1 w-5 h-0.5 bg-[#4F46E5] rounded-full" />
              )}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
