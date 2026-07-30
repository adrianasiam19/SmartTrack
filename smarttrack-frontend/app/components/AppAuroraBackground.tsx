"use client";

import { AuroraBackground } from "@/components/ui/aurora-background";

/**
 * Fixed aurora layer behind all app content.
 */
export default function AppAuroraBackground() {
  return (
    <AuroraBackground
      aria-hidden
      showRadialGradient
      className="pointer-events-none fixed inset-0 z-0 !h-full min-h-dvh !items-stretch !justify-start"
    />
  );
}
