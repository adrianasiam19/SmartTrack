'use client';

import { Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowLeft,
  Bookmark,
  BookOpen,
  Clock,
  Loader2,
  Search,
  Sparkles,
} from 'lucide-react';
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
  getLibraryHome,
  listTopicsBySubject,
  searchCurriculumTopics,
  type CurriculumTopic,
  type LibraryHome,
} from '../lib/learningApi';

type View = 'home' | 'subject' | 'topic';

const CORE_SUBJECTS = [
  { id: 'English Language', label: 'English Language', color: '#D97706' },
  { id: 'Core Mathematics', label: 'Core Mathematics', color: '#4F46E5' },
  { id: 'Integrated Science', label: 'Integrated Science', color: '#059669' },
  { id: 'Social Studies', label: 'Social Studies', color: '#7C3AED' },
] as const;

const ELECTIVE_CANDIDATES = [
  { id: 'Biology', label: 'Biology', color: '#16A34A' },
  { id: 'Chemistry', label: 'Chemistry', color: '#0EA5E9' },
  { id: 'Physics', label: 'Physics', color: '#6366F1' },
  { id: 'Additional Mathematics', label: 'Elective Mathematics', color: '#7C3AED' },
  { id: 'Elective Mathematics', label: 'Elective Mathematics', color: '#7C3AED' },
] as const;

/** Local fallback when /learning/library is empty or unavailable */
function buildLocalRecommendations(
  completedIds: Set<string>,
): CurriculumTopic[] {
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
      (l) =>
        l.subject === subject &&
        !completedIds.has(l.id) &&
        !seen.has(l.id),
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
  const [highlight, setHighlight] = useState(0);
  const searchRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  const bookmarkIds = useMemo(
    () => new Set((library?.bookmarks || []).map((b) => b.curriculum_id)),
    [library?.bookmarks],
  );

  const coreSubjects = useMemo(
    () => CORE_SUBJECTS.filter((s) => subjectHasContent(s.id)),
    [],
  );

  const electiveSubjects = useMemo(() => {
    const seen = new Set<string>();
    return ELECTIVE_CANDIDATES.filter((s) => {
      if (!subjectHasContent(s.id)) return false;
      // Deduplicate Elective/Additional Mathematics labels
      const key = s.label;
      if (seen.has(key)) return false;
      seen.add(key);
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
    // Always show starter suggestions immediately (no Phase 1 required)
    setLibrary((prev) =>
      prev?.recommended?.length
        ? prev
        : emptyLibrary(completed),
    );
    try {
      const data = await getLibraryHome(signal);
      // Prefer API IDs only — local ALL_LESSONS IDs can 404 on /teach if DB is empty
      setLibrary({
        ...data,
        recommended:
          data.recommended?.length > 0
            ? data.recommended
            : [],
      });
    } catch {
      // Offline / API down: show starter cards, but teach may still fail without seed
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

  // Deep-link: /learning?topic=curriculum_id
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
    // Reflect in URL for shareable deep links
    router.replace(`/learning?topic=${encodeURIComponent(curriculumId)}`, {
      scroll: false,
    });
  };

  const openSubject = async (subjectId: string) => {
    setSelectedSubject(subjectId);
    setView('subject');
    setTopicsLoading(true);
    try {
      const topics = await listTopicsBySubject(subjectId);
      setSubjectTopics(topics);
    } catch {
      // Fallback to local bundle
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

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F8FAFC]">
        <Sidebar />
        <main className="w-full max-w-4xl mx-auto px-4 pt-20 lg:pt-10 pb-28 text-[#64748B] flex items-center gap-2">
          <Loader2 className="w-4 h-4 animate-spin" /> Loading Learning Center…
        </main>
        <BottomNav />
      </div>
    );
  }

  if (view === 'topic' && activeTopicId) {
    return (
      <div className="min-h-screen bg-[#F8FAFC]">
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
    <div className="min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <AppLayout>
        <main className="w-full max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10 pb-28">
          {view !== 'home' ? (
            <button
              type="button"
              onClick={handleBack}
              className="flex items-center gap-2 text-sm text-gray-500 hover:text-[#1E293B] mb-4"
            >
              <ArrowLeft className="w-4 h-4" /> Back
            </button>
          ) : null}

          <AnimatePresence mode="wait">
            {view === 'home' ? (
              <motion.div
                key="home"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
              >
                <h1 className="text-2xl font-semibold text-[#0F172A]">Learning Center</h1>
                <p className="mt-1 text-sm text-[#64748B]">
                  Search any subject or topic — available for every phase.
                </p>

                {/* Search */}
                <div ref={searchRef} className="relative mt-6">
                  <div className="flex items-center gap-2 rounded-2xl border border-gray-200 bg-white px-4 py-3 shadow-sm focus-within:border-[#4F46E5]">
                    <Search className="w-5 h-5 text-gray-400 flex-shrink-0" />
                    <input
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      onFocus={() => searchQuery.trim().length >= 2 && setSearchOpen(true)}
                      onKeyDown={(e) => {
                        const subjects = subjectMatch(searchQuery);
                        const combined = [
                          ...subjects.map((s) => ({ type: 'subject' as const, id: s.id, label: s.label })),
                          ...searchResults.map((t) => ({
                            type: 'topic' as const,
                            id: t.curriculum_id,
                            label: t.title,
                          })),
                        ];
                        if (e.key === 'ArrowDown') {
                          e.preventDefault();
                          setHighlight((h) => Math.min(h + 1, Math.max(0, combined.length - 1)));
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
                      className="flex-1 bg-transparent text-sm text-[#0F172A] outline-none placeholder:text-gray-400"
                    />
                    {searchBusy ? <Loader2 className="w-4 h-4 animate-spin text-[#4F46E5]" /> : null}
                  </div>

                  {searchOpen && searchQuery.trim().length >= 2 ? (
                    <div className="absolute z-30 mt-2 w-full rounded-xl border border-gray-200 bg-white shadow-lg overflow-hidden max-h-80 overflow-y-auto">
                      {subjectMatch(searchQuery).map((s, idx) => (
                        <button
                          key={`sub-${s.id}`}
                          type="button"
                          onClick={() => void openSubject(s.id)}
                          className={`w-full text-left px-4 py-3 text-sm border-b border-gray-50 ${
                            highlight === idx ? 'bg-[#EEF2FF]' : 'hover:bg-gray-50'
                          }`}
                        >
                          <span className="text-[10px] uppercase tracking-wide text-[#4F46E5] font-semibold">
                            Subject
                          </span>
                          <p className="font-medium text-[#0F172A]">{s.label}</p>
                        </button>
                      ))}
                      {searchResults.map((t, i) => {
                        const idx = subjectMatch(searchQuery).length + i;
                        return (
                          <button
                            key={t.curriculum_id}
                            type="button"
                            onClick={() => openTopic(t.curriculum_id)}
                            className={`w-full text-left px-4 py-3 text-sm border-b border-gray-50 last:border-0 ${
                              highlight === idx ? 'bg-[#EEF2FF]' : 'hover:bg-gray-50'
                            }`}
                          >
                            <span className="text-[10px] uppercase tracking-wide text-gray-400 font-semibold">
                              Topic · {t.subject}
                            </span>
                            <p className="font-medium text-[#0F172A]">{t.title}</p>
                          </button>
                        );
                      })}
                      {!searchBusy &&
                      subjectMatch(searchQuery).length === 0 &&
                      searchResults.length === 0 ? (
                        <p className="px-4 py-6 text-sm text-gray-500 text-center">
                          No matches. Try “Photosynthesis” or “Quadratic Equations”.
                        </p>
                      ) : null}
                    </div>
                  ) : null}
                </div>

                {/* Continue */}
                {library?.continue_learning ? (
                  <section className="mt-8">
                    <SectionTitle icon={<BookOpen className="w-4 h-4" />} title="Continue Learning" />
                    <TopicCard
                      topic={library.continue_learning}
                      onClick={() => openTopic(library.continue_learning!.curriculum_id)}
                    />
                  </section>
                ) : null}

                {/* Recommended */}
                <section className="mt-8">
                  <SectionTitle icon={<Sparkles className="w-4 h-4" />} title="Recommended for You" />
                  {(library?.recommended?.length || 0) > 0 ? (
                    <div className="grid sm:grid-cols-2 gap-3">
                      {library!.recommended.map((topic) => (
                        <TopicCard
                          key={topic.curriculum_id}
                          topic={topic}
                          onClick={() => openTopic(topic.curriculum_id)}
                        />
                      ))}
                    </div>
                  ) : (
                    <div className="rounded-xl border border-dashed border-gray-200 bg-white px-4 py-5 text-sm text-gray-500">
                      <p>
                        Starter topics will appear here. After you play Challenges, recommendations
                        become personalised from your weak subjects.
                      </p>
                      <div className="mt-3 flex flex-wrap gap-2">
                        <button
                          type="button"
                          onClick={() => void openSubject('Core Mathematics')}
                          className="rounded-lg bg-[#4F46E5] px-3 py-1.5 text-xs font-semibold text-white"
                        >
                          Browse Core Mathematics
                        </button>
                        <button
                          type="button"
                          onClick={() => router.push('/challenges')}
                          className="rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-semibold text-[#0F172A]"
                        >
                          Play a challenge
                        </button>
                      </div>
                    </div>
                  )}
                </section>

                {/* Recent */}
                {(library?.recent?.length || 0) > 0 ? (
                  <section className="mt-8">
                    <SectionTitle icon={<Clock className="w-4 h-4" />} title="Recent Learning" />
                    <div className="grid sm:grid-cols-2 gap-3">
                      {library!.recent.map((topic) => (
                        <TopicCard
                          key={topic.curriculum_id}
                          topic={topic}
                          onClick={() => openTopic(topic.curriculum_id)}
                        />
                      ))}
                    </div>
                  </section>
                ) : null}

                {/* Saved */}
                {(library?.bookmarks?.length || 0) > 0 ? (
                  <section className="mt-8">
                    <SectionTitle icon={<Bookmark className="w-4 h-4" />} title="Saved Topics" />
                    <div className="grid sm:grid-cols-2 gap-3">
                      {library!.bookmarks.map((topic) => (
                        <TopicCard
                          key={topic.curriculum_id}
                          topic={topic}
                          onClick={() => openTopic(topic.curriculum_id)}
                        />
                      ))}
                    </div>
                  </section>
                ) : null}

                {/* Browse */}
                <section className="mt-10">
                  <h2 className="text-sm font-semibold text-[#0F172A] mb-4">Browse by Subject</h2>
                  <h3 className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-3">
                    Core Subjects
                  </h3>
                  <div className="grid sm:grid-cols-2 gap-3 mb-8">
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

                  {electiveSubjects.length > 0 ? (
                    <>
                      <h3 className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-3">
                        Elective Subjects
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
                    </>
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
                <h1 className="text-2xl font-semibold text-[#0F172A]">{selectedSubject}</h1>
                <p className="mt-1 text-sm text-[#64748B]">
                  Choose a topic to open lesson notes and Atlas AI.
                </p>

                {topicsLoading ? (
                  <div className="mt-8 flex items-center gap-2 text-sm text-gray-500">
                    <Loader2 className="w-4 h-4 animate-spin" /> Loading topics…
                  </div>
                ) : subjectTopics.length === 0 ? (
                  <p className="mt-8 text-sm text-gray-500">No topics available yet for this subject.</p>
                ) : (
                  <div className="mt-6 space-y-2">
                    {subjectTopics.map((topic) => (
                      <button
                        key={topic.curriculum_id}
                        type="button"
                        onClick={() => openTopic(topic.curriculum_id)}
                        className="w-full text-left rounded-xl border border-gray-200 bg-white px-4 py-3.5 hover:border-[#4F46E5]/40 hover:shadow-sm transition-all"
                      >
                        <p className="font-medium text-[#0F172A]">{topic.title}</p>
                        <p className="text-xs text-gray-400 mt-0.5">
                          {topic.estimated_minutes} min · {topic.xp_reward} XP
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

function SectionTitle({
  icon,
  title,
}: {
  icon: React.ReactNode;
  title: string;
}) {
  return (
    <div className="flex items-center gap-2 mb-3">
      <span className="text-[#4F46E5]">{icon}</span>
      <h2 className="text-sm font-semibold text-[#0F172A]">{title}</h2>
    </div>
  );
}

function TopicCard({
  topic,
  onClick,
}: {
  topic: CurriculumTopic;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="text-left rounded-xl border border-gray-200 bg-white p-4 hover:border-[#4F46E5]/40 hover:shadow-sm transition-all"
    >
      <p className="text-[10px] uppercase tracking-wide text-gray-400 font-semibold">
        {topic.subject}
      </p>
      <p className="mt-1 font-medium text-[#0F172A] text-sm leading-snug">{topic.title}</p>
      {topic.reason ? (
        <p className="mt-2 text-xs text-[#4F46E5]">{topic.reason}</p>
      ) : null}
    </button>
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
      className="text-left rounded-xl border border-gray-200 bg-white p-4 hover:border-gray-300 hover:shadow-sm transition-all"
    >
      <div className="flex items-center gap-3">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold text-sm flex-shrink-0"
          style={{ backgroundColor: color }}
        >
          {label.charAt(0)}
        </div>
        <div>
          <p className="font-semibold text-[#0F172A] text-sm">{label}</p>
          <p className="text-xs text-gray-400 mt-0.5">{count} topics</p>
        </div>
      </div>
    </button>
  );
}

export default function LearningPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center text-sm text-gray-500">
          Loading…
        </div>
      }
    >
      <LearningInner />
    </Suspense>
  );
}
