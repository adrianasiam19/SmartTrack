'use client';

import { ReactNode } from 'react';
import AppAuroraBackground from './components/AppAuroraBackground';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <>
      <AppAuroraBackground />
      <div className="relative z-10 min-h-screen bg-transparent">{children}</div>
    </>
  );
}
