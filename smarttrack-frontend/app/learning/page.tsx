'use client';

import { Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Loader2, Search, Sparkles } from 'lucide-react';
import Sidebar from '../components/Sidebar';
import BottomNav from '../components/BottomNav';
import AppLayout from '../components/AppLayout';
import AITutorLesson from '../components/AITutorLesson';
import {
  getAccessToken,
  getStoredUser,
  getCurrentUser,
  storeUser,
  type UserProfile,
} from '../lib/authApi';
import { ALL_LESSONS } from '../lib/learningContent';
import {
  completeCurriculumLesson,
  exploreCurriculumTopic,
  getLibraryHome,
  listTopicsBySubject,
  searchCurriculumTopics,
  type CurriculumTopic,
  type LibraryHome,
} from '../lib/learningApi';

type View = 'home' | 'subject' | 'topic';

const CORE_SUBJECTS = [
  { id: 'English Language', label: 'English Language', color: '#F59E0B' },
  { id: 'Core Mathematics', label: 'Core Mathematics', color: '#4F46E5' },
  { id: 'Integrated Science', label: 'Integrated Science', color: '#10B981' },
  { id: 'Social Studies', label: 'Social Studies', color: '#8B5CF6' },
] as const;

const ELECTIVE_CANDIDATES = [
  { id: 'Biology', label: 'Biology', color: '#22C55E' },
  { id: 'Chemistry', label: 'Chemistry', color: '#0EA5E9' },
  { id: 'Physics', label: 'Physics', color: '#6366F1' },
  { id: 'Additional Mathematics', label: 'Elective Mathematics', color: '#7C3AED' },
  { id: 'Elective Mathematics', label: 'Elective Mathematics', color: '#7C3AED' },
] as const;

function buildLocalRecommendations(completedIds: Set<string>): CurriculumTopic[] {
  const picks: CurriculumTopic[] = [];
  const seen = new Set<string>();
  const preferSubjects = [
    'Core Mathematics',
    'English Language',
    'Integrated Science',
    'Social Studies',
    'Biology',
    'Chemistry',
    'Physics',
    'Additional Mathematics',
  ];

  for (const subject of preferSubjects) {
    if (picks.length >= 6) break;
    const lesson = ALL_LESSONS.find(
      (l) => l.subject === subject && !completedIds.has(l.id) && !seen.has(l.id),
    );
    if (!lesson) continue;
    seen.add(lesson.id);
    picks.push({
      curriculum_id: lesson.id,
      title: lesson.title,
      subject: lesson.subject,
      shs_level: '',
      estimated_minutes: lesson.estimatedMinutes,
      difficulty: lesson.difficulty,
      xp_reward: lesson.xpReward,
      reason: 'Great place to start',
    });
  }

  if (picks.length < 6) {
    for (const lesson of ALL_LESSONS) {
      if (completedIds.has(lesson.id) || seen.has(lesson.id)) continue;
      seen.add(lesson.id);
      picks.push({
        curriculum_id: lesson.id,
        title: lesson.title,
        subject: lesson.subject,
        shs_level: '',
        estimated_minutes: lesson.estimatedMinutes,
        difficulty: lesson.difficulty,
        xp_reward: lesson.xpReward,
        reason: 'Great place to start',
      });
      if (picks.length >= 6) break;
    }
  }
  return picks;
}

function emptyLibrary(completedIds: Set<string>): LibraryHome {
  return {
    continue_learning: null,
    recommended: buildLocalRecommendations(completedIds),
    recent: [],
    bookmarks: [],
  };
}

const SUBJECTS_WITH_CONTENT = (() => {
  const counts = new Map<string, number>();
  for (const lesson of ALL_LESSONS) {
    counts.set(lesson.subject, (counts.get(lesson.subject) || 0) + 1);
  }
  return counts;
})();

function subjectHasContent(id: string) {
  return (SUBJECTS_WITH_CONTENT.get(id) || 0) > 0;
}

function LearningInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<View>('home');
  const [library, setLibrary] = useState<LibraryHome | null>(null);
  const [selectedSubject, setSelectedSubject] = useState<string | null>(null);
  const [subjectTopics, setSubjectTopics] = useState<CurriculumTopic[]>([]);
  const [topicsLoading, setTopicsLoading] = useState(false);
  const [activeTopicId, setActiveTopicId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<CurriculumTopic[]>([]);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchBusy, setSearchBusy] = useState(false);
  const [exploreBusy, setExploreBusy] = useState(false);
  const [highlight, setHighlight] = useState(0);
  const [showAllRecommended, setShowAllRecommended] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);
  const browseRef = useRef<HTMLElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  const bookmarkIds = useMemo(
    () => new Set((library?.bookmarks || []).map((b) => b.curriculum_id)),
    [library?.bookmarks],
  );

  const completedIds = useMemo(() => {
    const profile = (user?.learner_profile || {}) as { completed_lessons?: string[] };
    return new Set(Array.isArray(profile.completed_lessons) ? profile.completed_lessons : []);
  }, [user?.learner_profile]);

  const coreSubjects = useMemo(
    () => CORE_SUBJECTS.filter((s) => subjectHasContent(s.id)),
    [],
  );

  const electiveSubjects = useMemo(() => {
    const seen = new Set<string>();
    return ELECTIVE_CANDIDATES.filter((s) => {
      if (!subjectHasContent(s.id)) return false;
      if (seen.has(s.label)) return false;
      seen.add(s.label);
      return true;
    });
  }, []);

  const refreshLibrary = useCallback(async (signal?: AbortSignal) => {
    const profile = (getStoredUser()?.learner_profile || {}) as {
      completed_lessons?: string[];
    };
    const completed = new Set(
      Array.isArray(profile.completed_lessons) ? profile.completed_lessons : [],
    );
    setLibrary((prev) => (prev?.recommended?.length ? prev : emptyLibrary(completed)));
    try {
      const data = await getLibraryHome(signal);
      setLibrary({
        ...data,
        recommended:
          data.recommended?.length > 0
            ? data.recommended
            : emptyLibrary(completed).recommended,
      });
    } catch {
      setLibrary(emptyLibrary(completed));
    }
  }, []);

  useEffect(() => {
    const init = async () => {
      try {
        if (!getAccessToken()) {
          router.push('/login');
          return;
        }
        const cached = getStoredUser();
        if (cached) setUser(cached);
        const fresh = await getCurrentUser();
        setUser(fresh);
        storeUser(fresh);
        await refreshLibrary();
      } catch {
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };
    void init();
  }, [router, refreshLibrary]);

  useEffect(() => {
    const topic = searchParams.get('topic');
    if (!topic || loading) return;
    setActiveTopicId(topic);
    setView('topic');
  }, [searchParams, loading]);

  useEffect(() => {
    if (searchQuery.trim().length < 2) {
      setSearchResults([]);
      setSearchBusy(false);
      return;
    }
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setSearchBusy(true);
    const timer = window.setTimeout(() => {
      searchCurriculumTopics(searchQuery.trim(), controller.signal)
        .then((results) => {
          setSearchResults(results);
          setHighlight(0);
          setSearchOpen(true);
        })
        .catch((err) => {
          if (err instanceof Error && err.name !== 'AbortError') {
            setSearchResults([]);
          }
        })
        .finally(() => setSearchBusy(false));
    }, 280);
    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [searchQuery]);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setSearchOpen(false);
      }
    };
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, []);

  const openTopic = (curriculumId: string) => {
    setActiveTopicId(curriculumId);
    setView('topic');
    setSearchOpen(false);
    setSearchQuery('');
    router.replace(`/learning?topic=${encodeURIComponent(curriculumId)}`, {
      scroll: false,
    });
  };

  const exploreWithAtlas = async (rawQuery: string, subject?: string) => {
    const query = rawQuery.trim();
    if (query.length < 2 || exploreBusy) return;
    setExploreBusy(true);
    try {
      const topic = await exploreCurriculumTopic(query, subject);
      openTopic(topic.curriculum_id);
    } catch {
      setSearchOpen(true);
    } finally {
      setExploreBusy(false);
    }
  };

  const openSubject = async (subjectId: string) => {
    setSelectedSubject(subjectId);
    setView('subject');
    setTopicsLoading(true);
    try {
      const topics = await listTopicsBySubject(subjectId);
      setSubjectTopics(topics);
    } catch {
      setSubjectTopics(
        ALL_LESSONS.filter((l) => l.subject === subjectId).map((l) => ({
          curriculum_id: l.id,
          title: l.title,
          subject: l.subject,
          shs_level: '',
          estimated_minutes: l.estimatedMinutes,
          difficulty: l.difficulty,
          xp_reward: l.xpReward,
        })),
      );
    } finally {
      setTopicsLoading(false);
    }
  };

  const handleBack = () => {
    if (view === 'topic') {
      setActiveTopicId(null);
      if (selectedSubject) {
        setView('subject');
        router.replace('/learning', { scroll: false });
      } else {
        setView('home');
        router.replace('/learning', { scroll: false });
        void refreshLibrary();
      }
    } else if (view === 'subject') {
      setSelectedSubject(null);
      setSubjectTopics([]);
      setView('home');
      void refreshLibrary();
    }
  };

  const handleLessonComplete = async (xpEarned: number) => {
    if (!activeTopicId || !user) return;
    try {
      const result = await completeCurriculumLesson(activeTopicId);
      const updated = {
        ...user,
        xp: result.user_xp,
        rank: result.rank || user.rank,
      };
      setUser(updated);
      storeUser(updated);
    } catch {
      const updated = { ...user, xp: (user.xp || 0) + xpEarned };
      setUser(updated);
      storeUser(updated);
    }
    void refreshLibrary();
  };

  const subjectMatch = (query: string) => {
    const q = query.trim().toLowerCase();
    if (!q) return [];
    return [...coreSubjects, ...electiveSubjects].filter(
      (s) =>
        s.label.toLowerCase().includes(q) || s.id.toLowerCase().includes(q),
    );
  };

  const recommended = library?.recommended || [];
  const visibleRecommended = showAllRecommended ? recommended : recommended.slice(0, 6);

  const continueTopic = library?.continue_learning;
  const continueProgress = continueTopic
    ? completedIds.has(continueTopic.curriculum_id)
      ? 100
      : 45
    : 0;

  if (loading) {
    return (
      <div className="min-h-screen bg-transparent">
        <Sidebar />
        <main className="w-full max-w-5xl mx-auto px-4 pt-20 lg:pt-10 pb-28 text-[#64748B] flex items-center gap-2">
          <Loader2 className="w-4 h-4 animate-spin" /> Loading Learning Center…
        </main>
        <BottomNav />
      </div>
    );
  }

  if (view === 'topic' && activeTopicId) {
    return (
      <div className="min-h-screen bg-transparent">
        <Sidebar />
        <AppLayout>
          <main className="w-full max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10 pb-28">
            <AITutorLesson
              curriculumId={activeTopicId}
              onBack={handleBack}
              onComplete={(xp) => void handleLessonComplete(xp)}
              initiallyBookmarked={bookmarkIds.has(activeTopicId)}
              onOpenRelated={(id) => openTopic(id)}
            />
          </main>
        </AppLayout>
        <BottomNav />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-transparent">
      <Sidebar />
      <AppLayout>
        <main className="w-full max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10 pb-28">
          {view !== 'home' ? (
            <button
              type="button"
              onClick={handleBack}
              className="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-800 mb-5"
            >
              <ArrowLeft className="w-4 h-4" /> Back
            </button>
          ) : null}

          <AnimatePresence mode="wait">
            {view === 'home' ? (
              <motion.div
                key="home"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                className="space-y-8"
              >
                <header>
                  <p className="text-[11px] font-semibold tracking-[0.18em] uppercase text-[#4F46E5]">
                    Learning Center
                  </p>
                  <h1 className="mt-2 text-3xl sm:text-4xl font-bold tracking-tight text-slate-900">
                    What are we exploring today?
                  </h1>
                  <p className="mt-2 text-sm text-slate-500">
                    Search any subject or topic — available for every phase.
                  </p>
                </header>

                <div ref={searchRef} className="relative">
                  <div className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3.5 shadow-sm focus-within:border-[#4F46E5]/50 focus-within:ring-2 focus-within:ring-[#4F46E5]/10">
                    <Search className="w-5 h-5 text-slate-400 flex-shrink-0" />
                    <input
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      onFocus={() => searchQuery.trim().length >= 2 && setSearchOpen(true)}
                      onKeyDown={(e) => {
                        const subjects = subjectMatch(searchQuery);
                        const combined = [
                          ...subjects.map((s) => ({
                            type: 'subject' as const,
                            id: s.id,
                            label: s.label,
                          })),
                          ...searchResults.map((t) => ({
                            type: 'topic' as const,
                            id: t.curriculum_id,
                            label: t.title,
                          })),
                        ];
                        if (e.key === 'ArrowDown') {
                          e.preventDefault();
                          setHighlight((h) =>
                            Math.min(h + 1, Math.max(0, combined.length - 1)),
                          );
                        } else if (e.key === 'ArrowUp') {
                          e.preventDefault();
                          setHighlight((h) => Math.max(h - 1, 0));
                        } else if (e.key === 'Enter' && combined[highlight]) {
                          e.preventDefault();
                          const item = combined[highlight];
                          if (item.type === 'subject') void openSubject(item.id);
                          else openTopic(item.id);
                        }
                      }}
                      placeholder="Search any subject or topic..."
                      className="flex-1 bg-transparent text-[15px] text-slate-900 outline-none placeholder:text-slate-400"
                    />
                    {searchBusy ? (
                      <Loader2 className="w-4 h-4 animate-spin text-[#4F46E5]" />
                    ) : null}
                  </div>

                  {searchOpen && searchQuery.trim().length >= 2 ? (
                    <div className="absolute z-30 mt-2 w-full rounded-2xl border border-slate-200 bg-white shadow-xl overflow-hidden max-h-80 overflow-y-auto">
                      {subjectMatch(searchQuery).map((s, idx) => (
                        <button
                          key={`sub-${s.id}`}
                          type="button"
                          onClick={() => void openSubject(s.id)}
                          className={`w-full text-left px-4 py-3 text-sm border-b border-slate-50 ${
                            highlight === idx ? 'bg-indigo-50' : 'hover:bg-slate-50'
                          }`}
                        >
                          <span className="text-[10px] uppercase tracking-wide text-[#4F46E5] font-semibold">
                            Subject
                          </span>
                          <p className="font-medium text-slate-900">{s.label}</p>
                        </button>
                      ))}
                      {searchResults.map((t, i) => {
                        const idx = subjectMatch(searchQuery).length + i;
                        return (
                          <button
                            key={t.curriculum_id}
                            type="button"
                            onClick={() => openTopic(t.curriculum_id)}
                            className={`w-full text-left px-4 py-3 text-sm border-b border-slate-50 last:border-0 ${
                              highlight === idx ? 'bg-indigo-50' : 'hover:bg-slate-50'
                            }`}
                          >
                            <span className="text-[10px] uppercase tracking-wide text-slate-400 font-semibold">
                              Topic · {t.subject}
                            </span>
                            <p className="font-medium text-slate-900">{t.title}</p>
                          </button>
                        );
                      })}
                      {!searchBusy &&
                      subjectMatch(searchQuery).length === 0 &&
                      searchResults.length === 0 ? (
                        <div className="px-4 py-5 text-center space-y-3">
                          <p className="text-sm text-slate-500">
                            No catalogue match yet. Atlas AI can still teach this topic.
                          </p>
                          <button
                            type="button"
                            disabled={exploreBusy || searchQuery.trim().length < 2}
                            onClick={() => void exploreWithAtlas(searchQuery)}
                            className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#4F46E5] px-3.5 py-2 text-xs font-semibold text-white disabled:opacity-60"
                          >
                            {exploreBusy ? (
                              <>
                                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                                Preparing with Atlas AI…
                              </>
                            ) : (
                              <>
                                <Sparkles className="w-3.5 h-3.5" />
                                Teach “{searchQuery.trim()}” with Atlas AI
                              </>
                            )}
                          </button>
                        </div>
                      ) : null}
                    </div>
                  ) : null}
                </div>

                {continueTopic ? (
                  <button
                    type="button"
                    onClick={() => openTopic(continueTopic.curriculum_id)}
                    className="w-full rounded-2xl bg-gradient-to-r from-[#7C3AED] to-[#4F46E5] p-5 sm:p-6 text-left text-white shadow-sm hover:shadow-md transition-shadow"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                      <div className="flex-1 min-w-0">
                        <p className="text-[11px] font-semibold tracking-[0.14em] uppercase text-white/80">
                          Continue learning — {continueTopic.subject}
                        </p>
                        <h2 className="mt-2 text-xl sm:text-2xl font-bold leading-snug">
                          {continueTopic.title}
                        </h2>
                        <div className="mt-4 max-w-md">
                          <div className="h-1.5 rounded-full bg-white/25 overflow-hidden">
                            <div
                              className="h-full rounded-full bg-white transition-all"
                              style={{ width: `${continueProgress}%` }}
                            />
                          </div>
                          <p className="mt-2 text-xs text-white/80">
                            {continueProgress}% complete
                          </p>
                        </div>
                      </div>
                      <span className="inline-flex self-start sm:self-center items-center justify-center rounded-xl bg-white px-5 py-2.5 text-sm font-semibold text-[#4F46E5] shrink-0">
                        Resume
                      </span>
                    </div>
                  </button>
                ) : null}

                <section>
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-bold text-slate-900">Recommended for you</h2>
                    {recommended.length > 6 ? (
                      <button
                        type="button"
                        onClick={() => setShowAllRecommended((v) => !v)}
                        className="text-sm font-medium text-[#4F46E5] hover:text-[#4338CA]"
                      >
                        {showAllRecommended ? 'Show less' : 'See all'}
                      </button>
                    ) : recommended.length > 0 ? (
                      <button
                        type="button"
                        onClick={() =>
                          browseRef.current?.scrollIntoView({ behavior: 'smooth' })
                        }
                        className="text-sm font-medium text-[#4F46E5] hover:text-[#4338CA]"
                      >
                        See all
                      </button>
                    ) : null}
                  </div>

                  {visibleRecommended.length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                      {visibleRecommended.map((topic) => (
                        <button
                          key={topic.curriculum_id}
                          type="button"
                          onClick={() => openTopic(topic.curriculum_id)}
                          className="text-left rounded-2xl border border-slate-200 bg-white px-4 py-4 hover:border-slate-300 hover:shadow-sm transition-all"
                        >
                          <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-slate-400">
                            {topic.subject}
                          </p>
                          <p className="mt-2 text-[15px] font-semibold text-slate-900 leading-snug">
                            {topic.title}
                          </p>
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div className="rounded-2xl border border-dashed border-slate-200 bg-white px-5 py-6 text-sm text-slate-500">
                      Browse a subject below to start learning with Atlas AI.
                    </div>
                  )}
                </section>

                <section ref={browseRef} className="space-y-6">
                  <h2 className="text-lg font-bold text-slate-900">Browse by subject</h2>

                  <div>
                    <h3 className="text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400 mb-3">
                      Core subjects
                    </h3>
                    <div className="grid sm:grid-cols-2 gap-3">
                      {coreSubjects.map((subject) => (
                        <SubjectCard
                          key={subject.id}
                          label={subject.label}
                          color={subject.color}
                          count={SUBJECTS_WITH_CONTENT.get(subject.id) || 0}
                          onClick={() => void openSubject(subject.id)}
                        />
                      ))}
                    </div>
                  </div>

                  {electiveSubjects.length > 0 ? (
                    <div>
                      <h3 className="text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400 mb-3">
                        Elective subjects
                      </h3>
                      <div className="grid sm:grid-cols-2 gap-3">
                        {electiveSubjects.map((subject) => (
                          <SubjectCard
                            key={subject.id}
                            label={subject.label}
                            color={subject.color}
                            count={SUBJECTS_WITH_CONTENT.get(subject.id) || 0}
                            onClick={() => void openSubject(subject.id)}
                          />
                        ))}
                      </div>
                    </div>
                  ) : null}
                </section>
              </motion.div>
            ) : null}

            {view === 'subject' && selectedSubject ? (
              <motion.div
                key="subject"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
              >
                <p className="text-[11px] font-semibold tracking-[0.16em] uppercase text-[#4F46E5]">
                  Subject
                </p>
                <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
                  {selectedSubject}
                </h1>
                <p className="mt-2 text-sm text-slate-500">
                  Choose a topic to open lesson notes and Atlas AI.
                </p>

                {topicsLoading ? (
                  <div className="mt-8 flex items-center gap-2 text-sm text-slate-500">
                    <Loader2 className="w-4 h-4 animate-spin" /> Loading topics…
                  </div>
                ) : subjectTopics.length === 0 ? (
                  <div className="mt-8 space-y-3">
                    <p className="text-sm text-slate-500">
                      No catalogue topics loaded for this subject yet. Atlas AI can still
                      teach a topic you choose.
                    </p>
                    <button
                      type="button"
                      disabled={exploreBusy}
                      onClick={() =>
                        void exploreWithAtlas(
                          `${selectedSubject} fundamentals`,
                          selectedSubject,
                        )
                      }
                      className="inline-flex items-center gap-2 rounded-xl bg-[#4F46E5] px-3.5 py-2 text-xs font-semibold text-white disabled:opacity-60"
                    >
                      {exploreBusy ? (
                        <>
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          Preparing with Atlas AI…
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-3.5 h-3.5" />
                          Start with Atlas AI
                        </>
                      )}
                    </button>
                  </div>
                ) : (
                  <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {subjectTopics.map((topic) => (
                      <button
                        key={topic.curriculum_id}
                        type="button"
                        onClick={() => openTopic(topic.curriculum_id)}
                        className="w-full text-left rounded-2xl border border-slate-200 bg-white px-4 py-4 hover:border-slate-300 hover:shadow-sm transition-all"
                      >
                        <p className="font-semibold text-slate-900 text-[15px] leading-snug">
                          {topic.title}
                        </p>
                        <p className="text-xs text-slate-400 mt-1.5">
                          {topic.estimated_minutes} min
                        </p>
                      </button>
                    ))}
                  </div>
                )}
              </motion.div>
            ) : null}
          </AnimatePresence>
        </main>
      </AppLayout>
      <BottomNav />
    </div>
  );
}

function SubjectCard({
  label,
  color,
  count,
  onClick,
}: {
  label: string;
  color: string;
  count: number;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="text-left rounded-2xl border border-slate-200 bg-white px-4 py-4 hover:border-slate-300 hover:shadow-sm transition-all"
    >
      <div className="flex items-center gap-3.5">
        <div
          className="w-11 h-11 rounded-xl flex items-center justify-center text-white font-bold text-base flex-shrink-0"
          style={{ backgroundColor: color }}
        >
          {label.charAt(0)}
        </div>
        <div className="min-w-0">
          <p className="font-semibold text-slate-900 text-[15px] truncate">{label}</p>
          <p className="text-xs text-slate-400 mt-0.5">{count} topics</p>
        </div>
      </div>
    </button>
  );
}

export default function LearningPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-transparent flex items-center justify-center text-sm text-slate-500">
          Loading…
        </div>
      }
    >
      <LearningInner />
    </Suspense>
  );
}
