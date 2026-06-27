'use client';

import { ReactNode } from 'react';
import Watermark from './Watermark';

interface AppLayoutProps {
  children: ReactNode;
  /** Use lighter watermark opacity for challenge pages */
  isChallenge?: boolean;
}

export default function AppLayout({ children, isChallenge = false }: AppLayoutProps) {
  return (
    <div className="min-h-screen bg-[#F8FAFC] relative">
      <Watermark isChallenge={isChallenge} />
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
}
