'use client';

interface WatermarkProps {
  /** Lighter opacity for challenge pages. Default: false */
  isChallenge?: boolean;
}

export default function Watermark({ isChallenge = false }: WatermarkProps) {
  const opacity = isChallenge ? 'opacity-[0.03]' : 'opacity-[0.06]';

  return (
    <div
      className={`fixed inset-0 pointer-events-none z-0 overflow-hidden ${opacity}`}
      aria-hidden="true"
    >
      {/* Atlas brain/network pattern */}
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: `
            radial-gradient(circle at 20% 30%, #2563EB 0.5px, transparent 0.5px),
            radial-gradient(circle at 80% 70%, #7C3AED 0.5px, transparent 0.5px),
            radial-gradient(circle at 50% 50%, #F59E0B 0.5px, transparent 0.5px),
            radial-gradient(circle at 30% 80%, #2563EB 0.5px, transparent 0.5px),
            radial-gradient(circle at 70% 20%, #7C3AED 0.5px, transparent 0.5px),
            radial-gradient(circle at 10% 60%, #F59E0B 0.5px, transparent 0.5px),
            radial-gradient(circle at 90% 40%, #2563EB 0.5px, transparent 0.5px),
            radial-gradient(circle at 40% 10%, #7C3AED 0.5px, transparent 0.5px),
            radial-gradient(circle at 60% 90%, #F59E0B 0.5px, transparent 0.5px)
          `,
          backgroundSize: '80px 80px',
        }}
      />

      {/* Connecting lines (network pattern) */}
      <svg
        className="absolute inset-0 w-full h-full"
        viewBox="0 0 1440 900"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        preserveAspectRatio="none"
      >
        <line x1="288" y1="270" x2="1152" y2="630" stroke="#2563EB" strokeWidth="0.5" />
        <line x1="720" y1="450" x2="288" y2="270" stroke="#7C3AED" strokeWidth="0.5" />
        <line x1="1152" y1="630" x2="720" y2="450" stroke="#F59E0B" strokeWidth="0.5" />
        <line x1="288" y1="630" x2="1152" y2="270" stroke="#7C3AED" strokeWidth="0.5" />
        <line x1="432" y1="180" x2="1008" y2="720" stroke="#2563EB" strokeWidth="0.3" />
        <line x1="576" y1="720" x2="864" y2="180" stroke="#F59E0B" strokeWidth="0.3" />
      </svg>

      {/* Atlas brain logo - bottom right */}
      <div className="absolute bottom-6 right-6 flex items-center gap-2">
        <div className="w-8 h-8 rounded-lg border border-[#2563EB]/30 flex items-center justify-center">
          <span className="text-lg font-bold text-[#2563EB]" style={{ lineHeight: 1 }}>
            A
          </span>
        </div>
        <span className="text-sm font-semibold text-[#2563EB]" style={{ letterSpacing: '0.1em' }}>
          ATLAS
        </span>
      </div>

      {/* Educational/AI learning pattern - top right */}
      <div className="absolute top-8 right-8">
        <div className="flex gap-1.5">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-1 h-1 rounded-full"
              style={{
                backgroundColor: i === 0 ? '#2563EB' : i === 1 ? '#7C3AED' : '#F59E0B',
              }}
            />
          ))}
        </div>
      </div>

      {/* Educational/AI learning pattern - top left */}
      <div className="absolute top-12 left-12">
        <svg width="40" height="20" viewBox="0 0 40 20">
          <rect x="0" y="0" width="8" height="8" rx="1" fill="#2563EB" opacity="0.4" />
          <rect x="12" y="6" width="8" height="8" rx="1" fill="#7C3AED" opacity="0.3" />
          <rect x="24" y="0" width="8" height="8" rx="1" fill="#F59E0B" opacity="0.2" />
        </svg>
      </div>

      {/* Learning pattern - bottom left */}
      <div className="absolute bottom-12 left-12 flex gap-2">
        {[0, 1, 2, 3].map((i) => (
          <div
            key={i}
            className="w-2 h-8 rounded-full"
            style={{
              backgroundColor: i % 3 === 0 ? '#2563EB' : i % 3 === 1 ? '#7C3AED' : '#F59E0B',
              opacity: 0.2 + i * 0.1,
            }}
          />
        ))}
      </div>
    </div>
  );
}
