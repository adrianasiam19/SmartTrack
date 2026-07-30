'use client';

import { ReactNode } from 'react';

interface AppLayoutProps {
  children: ReactNode;
  /** Kept for call-site compatibility; watermark is applied globally. */
  isChallenge?: boolean;
}

export default function AppLayout({ children }: AppLayoutProps) {
  // Transparent so the global ATLAS watermark can show through; body supplies the page tint.
  return <div className="relative min-h-screen bg-transparent">{children}</div>;
}
