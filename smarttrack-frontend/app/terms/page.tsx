import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Terms of Use · Atlas',
  description: 'Terms for using Atlas learning and programme guidance.',
};

export default function TermsPage() {
  return (
    <main className="min-h-screen bg-[#F8FAFC] text-[#1E293B]">
      <div className="mx-auto max-w-2xl px-4 py-12 sm:py-16">
        <Link href="/" className="text-sm font-semibold text-[#2563EB] hover:underline">
          ← Back to Atlas
        </Link>
        <h1 className="mt-6 text-3xl font-bold tracking-tight">Terms of Use</h1>
        <p className="mt-2 text-sm text-[#64748B]">Last updated: August 2026</p>

        <div className="mt-8 space-y-6 text-sm leading-relaxed text-[#475569]">
          <section>
            <h2 className="text-base font-semibold text-[#1E293B]">Acceptance</h2>
            <p className="mt-2">
              By creating an account or using Atlas, you agree to these terms and our{' '}
              <Link href="/privacy" className="text-[#2563EB] hover:underline">
                Privacy Policy
              </Link>
              .
            </p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#1E293B]">What Atlas provides</h2>
            <p className="mt-2">
              Atlas offers practice challenges, learning content, and university-programme
              suggestions for secondary learners. Content may include AI-assisted material.
            </p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#1E293B]">No guarantees</h2>
            <p className="mt-2">
              Recommendations, scores, and learning suggestions are <strong>not 100% certain</strong>{' '}
              and are <strong>not guarantees</strong> of exam results, university admission,
              scholarships, or career outcomes. Always verify official requirements with
              universities, WAEC/exam bodies, and qualified counsellors or teachers.
            </p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#1E293B]">Accounts</h2>
            <p className="mt-2">
              You must use a real email address you control. Google Sign-In is only accepted when
              Google confirms the account email is verified. Keep your login details private and
              do not share accounts.
            </p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#1E293B]">Acceptable use</h2>
            <p className="mt-2">
              Do not abuse the service (for example automated scraping, attacking the API, or
              uploading others’ academic documents without permission). We may suspend accounts
              that harm the platform or other learners.
            </p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#1E293B]">Contact</h2>
            <p className="mt-2">
              Questions about these terms:{' '}
              <a
                href="mailto:yawasiamah18@gmail.com"
                className="text-[#2563EB] hover:underline"
              >
                yawasiamah18@gmail.com
              </a>
              .
            </p>
          </section>
        </div>
      </div>
    </main>
  );
}
