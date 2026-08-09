'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import Sidebar from '../components/Sidebar';
import BottomNav from '../components/BottomNav';
import AppLayout from '../components/AppLayout';
import { getAccessToken } from '../lib/authApi';
import {
  listCourseDirectory,
  type ProgrammeBrief,
} from '../lib/courseDirectoryApi';

export default function CourseDirectoryPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [fields, setFields] = useState<string[]>([]);
  const [programmes, setProgrammes] = useState<ProgrammeBrief[]>([]);
  const [note, setNote] = useState('');
  const [activeField, setActiveField] = useState<string>('All');
  const [query, setQuery] = useState('');
  const [debouncedQ, setDebouncedQ] = useState('');

  useEffect(() => {
    const t = setTimeout(() => setDebouncedQ(query.trim()), 250);
    return () => clearTimeout(t);
  }, [query]);

  useEffect(() => {
    if (!getAccessToken()) {
      router.push('/login');
      return;
    }
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await listCourseDirectory({
          field: activeField === 'All' ? undefined : activeField,
          q: debouncedQ || undefined,
        });
        if (cancelled) return;
        setProgrammes(data.programmes || []);
        setFields(data.fields || []);
        setNote(data.note || '');
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Could not load programmes.');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    void load();
    return () => {
      cancelled = true;
    };
  }, [router, activeField, debouncedQ]);

  const fieldChips = useMemo(() => ['All', ...fields], [fields]);

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-20">
          <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-8 pb-28">
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8"
            >
              <p className="text-xs font-semibold uppercase tracking-wide text-[#4F46E5]">
                Explore universities
              </p>
              <h1 className="text-2xl sm:text-3xl font-bold text-[#1E293B] mt-1">
                Course Directory
              </h1>
              <p className="text-sm text-[#64748B] mt-2 max-w-2xl leading-relaxed">
                Learn what university programmes cover — topics, careers, helpful SHS
                subjects, and where they are commonly offered. This is a reference guide,
                not an admissions or cut-off checker.
              </p>
            </motion.div>

            <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center">
              <div className="relative flex-1">
                <input
                  type="search"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search programmes, topics, or careers…"
                  className="w-full rounded-xl border border-[#E2E8F0] bg-white px-4 py-3 text-sm text-[#1E293B] outline-none focus:border-[#2563EB] focus:ring-2 focus:ring-[#BFDBFE]"
                />
              </div>
              <p className="text-xs font-medium text-[#64748B] sm:whitespace-nowrap">
                {loading ? 'Loading…' : `${programmes.length} programme${programmes.length === 1 ? '' : 's'}`}
              </p>
            </div>

            <div className="mb-8 flex flex-wrap gap-2">
              {fieldChips.map((field) => {
                const active = activeField === field;
                return (
                  <button
                    key={field}
                    type="button"
                    onClick={() => setActiveField(field)}
                    className={`rounded-full px-3.5 py-1.5 text-xs font-semibold transition ${
                      active
                        ? 'bg-[#2563EB] text-white shadow-sm shadow-[#2563EB]/25'
                        : 'bg-[#EEF2FF] text-[#3730A3] hover:bg-[#E0E7FF]'
                    }`}
                  >
                    {field}
                  </button>
                );
              })}
            </div>

            {error && (
              <div className="mb-6 rounded-xl border border-[#FECACA] bg-[#FEF2F2] px-4 py-3 text-sm text-[#B91C1C]">
                {error}
              </div>
            )}

            {loading ? (
              <div className="flex justify-center py-20">
                <div className="h-10 w-10 animate-spin rounded-full border-4 border-[#2563EB] border-t-transparent" />
              </div>
            ) : programmes.length === 0 ? (
              <div className="rounded-2xl border border-[#E2E8F0] bg-white px-6 py-12 text-center">
                <p className="font-semibold text-[#1E293B]">No programmes match</p>
                <p className="mt-1 text-sm text-[#64748B]">
                  Try another field filter or clear your search.
                </p>
              </div>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2">
                {programmes.map((p, i) => (
                  <motion.div
                    key={p.slug}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: Math.min(i * 0.02, 0.3) }}
                  >
                    <Link
                      href={`/programmes/${p.slug}`}
                      className="block h-full rounded-2xl border border-[#E2E8F0] bg-white p-5 shadow-sm transition hover:border-[#2563EB] hover:shadow-md"
                    >
                      <div className="mb-3 flex flex-wrap items-center gap-2">
                        <span className="rounded-lg bg-[#EEF2FF] px-2.5 py-1 text-[11px] font-semibold text-[#4F46E5]">
                          {p.field}
                        </span>
                        {p.typical_duration && (
                          <span className="text-[11px] font-medium text-[#64748B]">
                            {p.typical_duration}
                          </span>
                        )}
                      </div>
                      <h2 className="text-base font-bold text-[#1E293B] leading-snug">
                        {p.name}
                      </h2>
                      <p className="mt-2 text-sm text-[#475569] line-clamp-3 leading-relaxed">
                        {p.brief}
                      </p>
                      {!!p.commonly_offered_at?.length && (
                        <p className="mt-3 text-xs text-[#64748B] line-clamp-1">
                          Often at: {p.commonly_offered_at.slice(0, 3).join(' · ')}
                          {p.commonly_offered_at.length > 3 ? '…' : ''}
                        </p>
                      )}
                      <p className="mt-3 text-xs font-semibold text-[#2563EB]">
                        View full details →
                      </p>
                    </Link>
                  </motion.div>
                ))}
              </div>
            )}

            {note && (
              <p className="mt-10 text-xs text-[#94A3B8] leading-relaxed max-w-3xl">
                {note}
              </p>
            )}
          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}
