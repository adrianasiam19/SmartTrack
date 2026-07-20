'use client';

import { usePathname } from 'next/navigation';
import Watermark from './Watermark';

/**
 * Shows the ATLAS watermark on every route except the public home landing
 * (intro video + sign-in / create-account screen at `/`).
 */
export default function GlobalWatermark() {
  const pathname = usePathname();
  if (pathname === '/') return null;
  return <Watermark />;
}
