'use client';

/** Shared honesty notice for AI / guidance surfaces. */
export default function GuidanceDisclaimer({
  className = '',
  compact = false,
}: {
  className?: string;
  compact?: boolean;
}) {
  return (
    <div
      className={`rounded-xl border border-[#FDE68A] bg-[#FFFBEB] px-4 py-3 ${className}`}
      role="note"
    >
      {!compact && (
        <p className="text-sm font-semibold text-[#92400E] mb-1">Important notice</p>
      )}
      <p className={`leading-relaxed text-[#78350F] ${compact ? 'text-xs' : 'text-sm'}`}>
        {compact ? (
          <>
            Atlas guidance is supportive and <strong>not 100% certain</strong>. Use it
            alongside teachers, counsellors, and official university information.
          </>
        ) : (
          <>
            Atlas uses your activity, preferences, and (when available) academic results to
            suggest programmes and learning paths. These suggestions are{' '}
            <strong>not guarantees</strong> of admission, grades, or career outcomes. Always
            confirm cut-offs and requirements with the universities and with a trusted
            counsellor or teacher.
          </>
        )}
      </p>
    </div>
  );
}
