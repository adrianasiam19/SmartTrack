"use client";

import { AuroraBackground } from "@/components/ui/aurora-background";
import { usePathname } from "next/navigation";

/**
 * Fixed aurora layer behind app content.
 * Skipped on `/` so the intro landing keeps its own full-bleed look.
 */
export default function AppAuroraBackground() {
  const pathname = usePathname();
  if (pathname === "/") return null;

  return (
    <AuroraBackground
      aria-hidden
      showRadialGradient
      className="pointer-events-none fixed inset-0 z-0 !h-full min-h-dvh !items-stretch !justify-start"
    />
  );
}
