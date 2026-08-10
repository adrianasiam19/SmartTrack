'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import Sidebar from '../../components/Sidebar';
import BottomNav from '../../components/BottomNav';
import AppLayout from '../../components/AppLayout';
import { getAccessToken } from '../../lib/authApi';
import {
  getCourseProgramme,
  type ProgrammeDetail,
} from '../../lib/courseDirectoryApi';

function ChipList({ items, tone = 'blue' }: { items: string[]; tone?: 'blue' | 'indigo' | 'slate' }) {
  const styles =
    tone === 'indigo'
      ? 'bg-[#EEF2FF] text-[#3730A3]'
      : tone === 'slate'
        ? 'bg-[#F1F5F9] text-[#334155]'
        : 'bg-[#EFF6FF] text-[#1D4ED8]';
  if (!items.length) return <p className="text-sm text-[#94A3B8]">Not listed.</p>;
  return (
    <ul className="flex flex-wrap gap-2">
      {items.map((item) => (
        <li key={item} className={`rounded-lg px-2.5 py-1 text-xs font-medium ${styles}`}>
          {item}
        </li>
      ))}
    </ul>
  );
}

export default function ProgrammeDetailPage() {
  const router = useRouter();
  const params = useParams();
  const slug = String(params?.slug || '');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [programme, setProgramme] = useState<ProgrammeDetail | null>(null);

  useEffect(() => {
    if (!getAccessToken()) {
      router.push('/login');
      return;
    }
    if (!slug) return;
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await getCourseProgramme(slug);
        if (!cancelled) setProgramme(data);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Could not load programme.');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    void load();
    return () => {
      cancelled = true;
    };
  }, [router, slug]);

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-20">
          <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-8 pb-28">
            <Link
              href="/programmes"
              className="inline-flex text-sm font-semibold text-[#2563EB] hover:underline mb-6"
            >
              ← Back to Course Directory
            </Link>

            {loading ? (
              <div className="flex justify-center py-20">
                <div className="h-10 w-10 animate-spin rounded-full border-4 border-[#2563EB] border-t-transparent" />
              </div>
            ) : error || !programme ? (
              <div className="rounded-2xl border border-[#FECACA] bg-[#FEF2F2] px-5 py-8 text-center">
                <p className="font-semibold text-[#991B1B]">{error || 'Programme not found'}</p>
                <Link href="/programmes" className="mt-3 inline-block text-sm font-semibold text-[#2563EB]">
                  Browse all programmes
                </Link>
              </div>
            ) : (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                <div className="mb-6 flex flex-wrap gap-2">
                  <span className="rounded-lg bg-[#EEF2FF] px-2.5 py-1 text-xs font-semibold text-[#4F46E5]">
                    {programme.field}
                  </span>
                  {programme.level && (
                    <span className="rounded-lg bg-[#F1F5F9] px-2.5 py-1 text-xs font-medium text-[#475569]">
                      {programme.level}
                    </span>
                  )}
                  {programme.typical_duration && (
                    <span className="rounded-lg bg-[#EFF6FF] px-2.5 py-1 text-xs font-medium text-[#1D4ED8]">
                      {programme.typical_duration}
                    </span>
                  )}
                </div>

                <h1 className="text-2xl sm:text-3xl font-bold text-[#1E293B] leading-tight">
                  {programme.name}
                </h1>
                <p className="mt-3 text-sm sm:text-base text-[#475569] leading-relaxed">
                  {programme.brief}
                </p>

                <section className="mt-8 rounded-2xl border border-[#E2E8F0] bg-white p-5 sm:p-6">
                  <h2 className="text-lg font-bold text-[#1E293B] mb-2">Detailed overview</h2>
                  <p className="text-sm text-[#475569] leading-relaxed whitespace-pre-line">
                    {programme.detailed_overview || programme.brief}
                  </p>
                </section>

                <section className="mt-5 rounded-2xl border border-[#E2E8F0] bg-white p-5 sm:p-6">
                  <h2 className="text-lg font-bold text-[#1E293B] mb-3">Core topics you may study</h2>
                  <ChipList items={programme.core_topics || []} tone="blue" />
                </section>

                <section className="mt-5 rounded-2xl border border-[#E2E8F0] bg-white p-5 sm:p-6">
                  <h2 className="text-lg font-bold text-[#1E293B] mb-3">Career paths</h2>
                  <ChipList items={programme.career_paths || []} tone="indigo" />
                </section>

                <section className="mt-5 rounded-2xl border border-[#E2E8F0] bg-white p-5 sm:p-6">
                  <h2 className="text-lg font-bold text-[#1E293B] mb-3">Helpful SHS subjects</h2>
                  <p className="text-xs text-[#64748B] mb-3">
                    Useful preparation subjects — not formal admission requirements.
                  </p>
                  <ChipList items={programme.related_shs_subjects || []} tone="slate" />
                </section>

                <section className="mt-5 rounded-2xl border border-[#E2E8F0] bg-white p-5 sm:p-6">
                  <h2 className="text-lg font-bold text-[#1E293B] mb-3">
                    Where it&apos;s offered
                  </h2>
                  <p className="text-xs text-[#64748B] mb-3">
                    University listings from catalogue sources where available. Always confirm
                    current offerings and entry rules on the official site.
                  </p>
                  {(programme.offerings || []).length > 0 ? (
                    <ul className="space-y-4">
                      {programme.offerings!.map((offering) => (
                        <li
                          key={`${offering.university}-${offering.programme_name || ''}`}
                          className="rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] px-4 py-3"
                        >
                          <div className="flex flex-wrap items-baseline justify-between gap-2">
                            <p className="text-sm font-semibold text-[#1E293B]">
                              {offering.university}
                            </p>
                            {offering.source_url ? (
                              <a
                                href={offering.source_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs font-medium text-[#1D4ED8] underline"
                              >
                                Official page
                              </a>
                            ) : null}
                          </div>
                          {offering.programme_name ? (
                            <p className="mt-1 text-sm text-[#334155]">
                              {offering.programme_name}
                            </p>
                          ) : null}
                          {(offering.department || offering.duration) && (
                            <p className="mt-1 text-xs text-[#64748B]">
                              {[offering.department, offering.duration].filter(Boolean).join(' · ')}
                            </p>
                          )}
                          {offering.overview ? (
                            <p className="mt-2 text-sm text-[#475569] leading-relaxed whitespace-pre-line">
                              {offering.overview}
                            </p>
                          ) : null}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <ChipList items={programme.commonly_offered_at || []} tone="blue" />
                  )}
                </section>

                <div className="mt-8 rounded-xl border border-[#FDE68A] bg-[#FFFBEB] px-4 py-3 text-sm text-[#92400E]">
                  Course Directory is for learning about programmes only. For personalised
                  matches and admission cut-offs, use{' '}
                  <Link href="/recommendations" className="font-semibold underline">
                    Recommendations
                  </Link>
                  .
                </div>
              </motion.div>
            )}
          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}
