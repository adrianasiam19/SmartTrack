'use client';

import { ReactNode } from 'react';
import GlobalWatermark from './components/GlobalWatermark';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <>
      {/* Page content first; watermark is fixed and paints above backgrounds. */}
      <div className="relative min-h-screen">{children}</div>
      <GlobalWatermark />
    </>
  );
}
