import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Privacy Policy · Atlas',
  description: 'How Atlas collects, uses, and protects learner data.',
};

export default function PrivacyPage() {
  return (
    <main className="min-h-screen bg-[#F8FAFC] text-[#1E293B]">
      <div className="mx-auto max-w-2xl px-4 py-12 sm:py-16">
        <Link href="/" className="text-sm font-semibold text-[#2563EB] hover:underline">
          ← Back to Atlas
        </Link>
        <h1 className="mt-6 text-3xl font-bold tracking-tight">Privacy Policy</h1>
        <p className="mt-2 text-sm text-[#64748B]">Last updated: August 2026</p>

        <div className="mt-8 space-y-6 text-sm leading-relaxed text-[#475569]">
          <section>
            <h2 className="text-base font-semibold text-[#1E293B]">Who we are</h2>
            <p className="mt-2">
              Atlas (“we”, “us”) is a learning and university-programme guidance product for
              secondary students. This policy explains what data we collect when you use Atlas
              on the web, including when you sign in with Google.
            </p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#1E293B]">Information we collect</h2>
            <ul className="mt-2 list-disc space-y-1 pl-5">
              <li>Account details: name, email, school/programme (if you provide them).</li>
              <li>
                Google Sign-In: if you choose Google, we receive your Google account email,
                name, and profile picture when Google confirms the email is verified.
              </li>
              <li>
                Learning activity: challenge answers, progress, XP, and related telemetry used
                to personalise recommendations.
              </li>
              <li>
                Optional academic uploads (for example WASSCE results) that you choose to
                submit.
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#1E293B]">How we use information</h2>
            <ul className="mt-2 list-disc space-y-1 pl-5">
              <li>To create and secure your account and keep you signed in.</li>
              <li>To run challenges, learning lessons, and progress features.</li>
              <li>
                To generate programme and learning suggestions. These are guidance only and
                are not guarantees of admission or outcomes.
              </li>
              <li>To improve reliability, prevent abuse, and support you if something breaks.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#1E293B]">Sharing</h2>
            <p className="mt-2">
              We do not sell your personal data. We may use trusted infrastructure providers
              (hosting, database, email delivery, AI providers for lesson/challenge generation)
              solely to operate Atlas. Google processes sign-in according to Google’s policies
              when you use Google Sign-In.
            </p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#1E293B]">Security & retention</h2>
            <p className="mt-2">
              We use industry-standard protections such as encrypted transport (HTTPS in
              production), hashed passwords, and access controls. We keep account and progress
              data while your account is active, and remove or anonymise data when accounts are
              deleted or as required by law.
            </p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#1E293B]">Your choices</h2>
            <p className="mt-2">
              You can update profile details in Atlas, stop using Google Sign-In by using email
              and password instead (where available), and request account deletion by contacting
              us at the support email listed on the app or your school/project contact.
            </p>
          </section>

          <section>
            <h2 className="text-base font-semibold text-[#1E293B]">Contact</h2>
            <p className="mt-2">
              For privacy questions about Atlas, email{' '}
              <a
                href="mailto:yawasiamah18@gmail.com"
                className="text-[#2563EB] hover:underline"
              >
                yawasiamah18@gmail.com
              </a>
              . Use the same address on the Google OAuth consent screen.
            </p>
          </section>
        </div>

        <p className="mt-10 text-xs text-[#94A3B8]">
          Also see our{' '}
          <Link href="/terms" className="text-[#2563EB] hover:underline">
            Terms of Use
          </Link>
          .
        </p>
      </div>
    </main>
  );
}
