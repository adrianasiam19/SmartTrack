'use client';

interface WatermarkProps {
  /** Kept for AppLayout compatibility; logo stays equally faint everywhere. */
  isChallenge?: boolean;
}

/**
 * Large faint ATLAS compass — centered on the main content column
 * (where the phase cards sit), not just the raw viewport.
 */
export default function Watermark({ isChallenge = false }: WatermarkProps) {
  const opacity = isChallenge ? 0.07 : 0.09;

  return (
    <div
      className="pointer-events-none fixed inset-0 z-[5] overflow-hidden"
      aria-hidden="true"
    >
      {/*
        Center on the dashboard content column (max-w-3xl ≈ 48rem),
        which is itself horizontally centered — so mid-page on all screens.
      */}
      <div className="absolute inset-0 flex items-center justify-center">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="/atlas-watermark.png?v=2"
          alt=""
          width={544}
          height={544}
          className="max-w-none select-none"
          style={{
            opacity,
            // Large enough to fill the page behind the phase cards.
            width: 'min(135vmin, 1100px)',
            height: 'min(135vmin, 1100px)',
          }}
        />
      </div>
    </div>
  );
}
