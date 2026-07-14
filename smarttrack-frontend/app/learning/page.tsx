'use client';

import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Lock, ChevronDown } from 'lucide-react';
import Sidebar from '../components/Sidebar';
import BottomNav from '../components/BottomNav';
import AppLayout from '../components/AppLayout';
import LessonPlayer from '../components/LessonPlayer';
import {
  getAccessToken, getStoredUser, getCurrentUser, updateUserProfile, storeUser,
  type UserProfile, type Programme, type SHSLevel,
} from '../lib/authApi';
import { ALL_LESSONS, getLessonById, type Lesson } from '../lib/learningContent';
import { getLearningStage, getCurrentZone, calculateZoneProgress } from '../lib/adaptiveEngine';

// ── Core Subjects ──────────────────────────────────────────────────────────
const SUBJECTS = [
  { id: 'Core Mathematics', label: 'Core Mathematics', description: 'Numbers, algebra, geometry, statistics and more', color: '#4F46E5' },
  { id: 'English Language', label: 'English Language', description: 'Comprehension, grammar, literature and writing', color: '#D97706' },
  { id: 'Integrated Science', label: 'Integrated Science', description: 'Scientific method, materials, force, energy and health', color: '#059669' },
  { id: 'Social Studies', label: 'Social Studies', description: 'Governance, history, economics and civic responsibility', color: '#7C3AED' },
] as const;

// ── Elective Subjects ─────────────────────────────────────────────────────
const ELECTIVE_SUBJECTS = [
  { id: 'Biology', label: 'Biology', description: 'Living organisms, cells, genetics and ecology', color: '#16A34A', icon: '🧬' },
] as const;

type SubjectId = (typeof SUBJECTS)[number]['id'] | (typeof ELECTIVE_SUBJECTS)[number]['id'];
type DrillView = 'subjects' | 'elective-subjects' | 'modules' | 'lessons' | 'coming-soon';

// ── Module definitions ────────────────────────────────────────────────────
const MODULE_NAMES: Record<string, Record<string, string>> = {
  'Core Mathematics': {
    m1: 'Number Sets',
    m2: 'Fractions and Percentages',
    m3: 'Algebraic Expressions and Factorisation',
    m4: 'Linear Equations, Relations and Functions',
    m5: 'Angles and the Pythagorean Theorem',
    m6: 'Vectors and Trigonometry',
    m7: 'Perimeter, Area and Volume',
    m8: 'Data Organisation, Analysis and Presentation',
    m9: 'Probability of Independent Events',
  },
  'English Language': {
    s5: 'Discourse and Conversation',
    s7: 'Oral Language, Reading and Grammar',
    s8: 'Forms of Verbs and Writing Strategies',
    s17: 'Conversation and Communication in Context',
    s18: 'Reading',
    s19: 'Subject and Predicate',
    s20: 'Text Types and Purposes',
    s21: 'Themes',
    s22: 'Ideas',
    s23: 'Analysing Non-Fiction Texts',
    s24: 'Article Writing',
  },
  'Integrated Science': {
    s1: 'Exploring Materials — Characteristics of Science',
    s2: 'Science and Materials in Nature',
    s3: 'Diffusion and Osmosis',
    s4: 'Reproduction in Plants and Humans',
    s5: 'Solar Panels',
    s6: 'Force',
    s7: 'Basic Electronics',
    s8: 'Promoting Health and Safety',
    s9: 'Production in Local Industry',
    gs: 'General Science Foundations',
  },
  'Social Studies': {
    s1: 'A Geographical and Historical Sketch of Africa',
    s2: 'Civic Ideals and Practices',
    s3: 'Indigenous Knowledge Systems',
    s4: 'Ethics and Human Values',
    s5: 'African Civilisations',
    s6: 'Revolutions That Changed the World',
    s7: 'Economic Activities in Africa',
    s8: 'Entrepreneurship, Workplace Culture and Productivity',
    s9: 'Consumer Rights, Protection and Responsibilities',
    s10: 'Financial Literacy',
  },
  'Biology': {
    s1: 'Introduction to Biology and the Scientific Method',
    s2: 'Fish Farming, Processing and Conservation',
    s3: 'Cell Biology',
    s4: 'Organisms',
    s5: 'Ecology',
  },
};

function extractModuleKey(lessonId: string): string | null {
  // coremath-m1t1 → m1, int-sci-s1t1 → s1, eng-lang-s5t1 → s5, soc-st-s1t1 → s1, gen-sci-s1 → gs
  const mathMatch = lessonId.match(/^coremath-(m\d+)/);
  if (mathMatch) return mathMatch[1];
  const intSciMatch = lessonId.match(/^int-sci-(s\d+)/);
  if (intSciMatch) return intSciMatch[1];
  const engMatch = lessonId.match(/^eng-lang-(s\d+)/);
  if (engMatch) return engMatch[1];
  const socStMatch = lessonId.match(/^soc-st-(s\d+)/);
  if (socStMatch) return socStMatch[1];
  const bioMatch = lessonId.match(/^bio-(s\d+)/);
  if (bioMatch) return bioMatch[1];
  const sciMatch = lessonId.match(/^gen-sci-(s\d+)/);
  if (sciMatch) return 'gs'; // all general science → one module
  return null;
}

function getModuleLabel(subject: string, moduleKey: string): string {
  return MODULE_NAMES[subject]?.[moduleKey] || `Module ${moduleKey.toUpperCase()}`;
}

// ── Helpers ───────────────────────────────────────────────────────────────
function getLessonsForSubject(subject: string, programmeFilter?: string | null): Lesson[] {
  // Map 'Integrated Science' to include 'General Science' lessons
  const subjects = subject === 'Integrated Science'
    ? ['Integrated Science', 'General Science']
    : [subject];
  let lessons = ALL_LESSONS.filter((l) => subjects.includes(l.subject));
  // Apply programme filter: only show 'Both' or matching programme
  if (programmeFilter) {
    lessons = lessons.filter((l) => l.programme === 'Both' || l.programme === programmeFilter);
  }
  return lessons;
}

function getModulesForLevel(subject: string, shsLevel: string, programmeFilter?: string | null): { key: string; label: string; lessons: Lesson[] }[] {
  const allLessons = getLessonsForSubject(subject, programmeFilter).filter((l) =>
    l.suggestedLevel === shsLevel || l.shsLevels?.includes(shsLevel)
  );
  const grouped = new Map<string, Lesson[]>();
  for (const lesson of allLessons) {
    const key = extractModuleKey(lesson.id) || 'other';
    if (!grouped.has(key)) grouped.set(key, []);
    grouped.get(key)!.push(lesson);
  }
  return Array.from(grouped.entries())
    .map(([key, lessons]) => ({ key, label: getModuleLabel(subject, key), lessons }))
    .filter((m) => m.lessons.length > 0);
}

const COMPLETED_KEY = 'atlas_completed_lessons';
function loadCompletedLessons(): Set<string> {
  if (typeof window === 'undefined') return new Set();
  try { const raw = localStorage.getItem(COMPLETED_KEY); return new Set<string>(raw ? JSON.parse(raw) : []); } catch { return new Set(); }
}
function saveCompletedLessons(set: Set<string>) { localStorage.setItem(COMPLETED_KEY, JSON.stringify([...set])); }

// ── Page Component ────────────────────────────────────────────────────────
export default function Learning() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<DrillView>('subjects');
  const [selectedSubject, setSelectedSubject] = useState<SubjectId | null>(null);
  const [selectedLevel, setSelectedLevel] = useState<string | null>(null);
  const [selectedModule, setSelectedModule] = useState<{ key: string; label: string } | null>(null);
  const [activeLesson, setActiveLesson] = useState<Lesson | null>(null);
  const [completedLessons, setCompletedLessons] = useState<Set<string>>(new Set());
  const [onboardingProg, setOnboardingProg] = useState<Programme>('General Science');
  const [onboardingLevel, setOnboardingLevel] = useState<SHSLevel>('SHS 1');
  const [onboardingSaving, setOnboardingSaving] = useState(false);
  const [onboardingError, setOnboardingError] = useState<string | null>(null);
  const [progDropdownOpen, setProgDropdownOpen] = useState(false);
  const progDropdownRef = useRef<HTMLDivElement>(null);

  // Close programme dropdown on outside click
  useEffect(() => {
    if (!progDropdownOpen) return;
    const handleClick = (e: MouseEvent) => {
      if (progDropdownRef.current && !progDropdownRef.current.contains(e.target as Node)) {
        setProgDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [progDropdownOpen]);

  const programme: 'Science' | 'Arts' | null = user?.programme === 'General Science' ? 'Science' : user?.programme === 'General Arts' ? 'Arts' : null;
  const shsLevel = user?.shs_level || null;
  const stage = getLearningStage(user?.programme || null, shsLevel);
  const currentZone = getCurrentZone(user?.programme || null, shsLevel);
  const zoneProgress = currentZone ? calculateZoneProgress(user?.xp || 0, currentZone) : 0;

  useEffect(() => {
    const init = async () => {
      try {
        if (!getAccessToken()) { router.push('/login'); return; }
        const cached = getStoredUser(); if (cached) setUser(cached);
        const fresh = await getCurrentUser(); setUser(fresh);
        setCompletedLessons(loadCompletedLessons());
      } catch { router.push('/login'); }
      finally { setLoading(false); }
    };
    init();
  }, [router]);

  // ── Drill-down navigation ────────────────────────────────────────────────
  const handleSelectSubject = (subject: SubjectId) => {
    setSelectedSubject(subject);
    setSelectedModule(null);
    // Auto-navigate based on student's registered SHS level
    if (shsLevel) {
      const levelLessons = getLessonsForSubject(subject, programme)
        .filter(l => l.suggestedLevel === shsLevel || l.shsLevels?.includes(shsLevel));
      if (levelLessons.length > 0) {
        setSelectedLevel(shsLevel);
        setView('modules');
      } else {
        setSelectedLevel(null);
        setView('coming-soon');
      }
    } else {
      setSelectedLevel(null);
      setView('coming-soon');
    }
  };

  const handleSelectModule = (key: string, label: string) => {
    setSelectedModule({ key, label });
    setView('lessons');
  };

  const handleBack = () => {
    if (view === 'lessons') { setView('modules'); setSelectedModule(null); }
    else if (view === 'modules') { setView('subjects'); setSelectedSubject(null); setSelectedLevel(null); }
    else if (view === 'elective-subjects') { setView('subjects'); }
    else if (view === 'coming-soon') { setView('subjects'); setSelectedSubject(null); }
  };

  const handleSelectLesson = useCallback((lessonId: string) => {
    const lesson = getLessonById(lessonId);
    if (lesson) { setActiveLesson(lesson); }
  }, []);

  const handleLessonComplete = useCallback((xpEarned: number) => {
    if (!activeLesson || !user) return;
    const newCompleted = new Set(completedLessons);
    newCompleted.add(activeLesson.id);
    setCompletedLessons(newCompleted); saveCompletedLessons(newCompleted);
    const updatedUser = { ...user, xp: user.xp + xpEarned };
    setUser(updatedUser); storeUser(updatedUser);
    setTimeout(() => { setActiveLesson(null); }, 500);
  }, [activeLesson, completedLessons, user]);

  const handleBackToPath = useCallback(() => { setActiveLesson(null); }, []);

  // ── Breadcrumb ───────────────────────────────────────────────────────────
  const breadcrumb = useMemo(() => {
    const parts: { label: string; action: () => void }[] = [{ label: 'Learning Center', action: () => { setView('subjects'); setSelectedSubject(null); setSelectedLevel(null); setSelectedModule(null); } }];
    if (view === 'elective-subjects') parts.push({ label: 'Elective Subjects', action: () => { setView('subjects'); } });
    if (selectedSubject && view !== 'elective-subjects') parts.push({ label: selectedSubject, action: () => { setView('subjects'); setSelectedSubject(null); setSelectedLevel(null); setSelectedModule(null); } });
    if (selectedLevel && view !== 'coming-soon') parts.push({ label: selectedLevel, action: () => { setView('modules'); setSelectedModule(null); } });
    if (selectedModule) parts.push({ label: selectedModule.label, action: () => { setView('lessons'); } });
    return parts;
  }, [selectedSubject, selectedLevel, selectedModule, view]);

  // ── Current level lessons for display ────────────────────────────────────
  const currentModuleLessons = useMemo(() => {
    if (!selectedSubject || !selectedLevel || !selectedModule) return [];
    return getModulesForLevel(selectedSubject, selectedLevel, programme)
      .find((m) => m.key === selectedModule.key)?.lessons || [];
  }, [selectedSubject, selectedLevel, selectedModule, programme]);

  const isLessonUnlocked = (lesson: Lesson): boolean => {
    if (lesson.prerequisites.length === 0) return true;
    return lesson.prerequisites.every((preId) => completedLessons.has(preId));
  };

  if (loading) return (
    <AppLayout><div className="flex items-center justify-center min-h-screen">
      <div className="w-8 h-8 border-2 border-[#4F46E5] border-t-transparent rounded-full animate-spin" /></div></AppLayout>
  );
  if (!user) return null;

  // ── Active lesson view ──────────────────────────────────────────────────
  if (activeLesson) {
    return (
      <AppLayout>
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex-1 lg:pb-0 pb-20">
            <main className="flex-1 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-8 pb-8">
              <LessonPlayer lesson={activeLesson} onComplete={handleLessonComplete} onBack={handleBackToPath} />
            </main>
          </div>
          <BottomNav />
        </div>
      </AppLayout>
    );
  }

  // ── Stats summary bar ──────────────────────────────────────────────────
  const totalLessons = ALL_LESSONS.length;
  const totalCompleted = completedLessons.size;

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-20">
          <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-8 pb-8">

            {/* ── Header ── */}
            <div className="mb-6">
              <div className="flex items-center gap-3">
                {view !== 'subjects' && (
                  <button onClick={handleBack} className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 transition-colors">
                    <ArrowLeft className="w-5 h-5" />
                  </button>
                )}
                <div>
                  <h1 className="text-xl font-bold text-[#1E293B]">Learning Center</h1>
                  <p className="text-xs text-gray-500">{totalCompleted} of {totalLessons} lessons completed</p>
                </div>
              </div>
            </div>

            {/* ── Stats bar ── */}
            <div className="grid grid-cols-4 gap-3 mb-6">
              <div className="bg-white border border-gray-200 rounded-xl p-3 text-center">
                <p className="text-xl font-bold text-[#4F46E5]">{totalCompleted}</p>
                <p className="text-xs text-gray-500">Done</p>
              </div>
              <div className="bg-white border border-gray-200 rounded-xl p-3 text-center">
                <p className="text-xl font-bold text-[#D97706]">{user.streak}</p>
                <p className="text-xs text-gray-500">Streak</p>
              </div>
              <div className="bg-white border border-gray-200 rounded-xl p-3 text-center">
                <p className="text-xl font-bold text-[#F43F5E]">{Math.round((totalCompleted / Math.max(1, totalLessons)) * 100)}%</p>
                <p className="text-xs text-gray-500">Progress</p>
              </div>
              <div className="bg-white border border-gray-200 rounded-xl p-3 text-center">
                <p className="text-xl font-bold text-[#1E293B]">{shsLevel || '\u2014'}</p>
                <p className="text-xs text-gray-500">Level</p>
              </div>
            </div>

            {/* ── Breadcrumb ── */}
            {view !== 'subjects' && (
              <div className="flex items-center gap-1.5 text-xs text-gray-400 mb-4 flex-wrap">
                {breadcrumb.map((crumb, idx) => (
                  <span key={idx} className="flex items-center gap-1.5">
                    {idx > 0 && <span>/</span>}
                    <button onClick={crumb.action} className="hover:text-[#4F46E5] transition-colors">
                      {crumb.label}
                    </button>
                  </span>
                ))}
              </div>
            )}

            {/* ── Zone/Stage info (visible on subjects view) ── */}
            {view === 'subjects' && stage && (
              <div className="bg-white border border-gray-200 rounded-xl p-5 mb-6">
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-[#1E293B]">{stage.title}</h3>
                      <span className="px-2 py-0.5 text-[10px] font-bold bg-[#EEF2FF] text-[#4F46E5] rounded uppercase">{shsLevel}</span>
                    </div>
                    <p className="text-sm text-gray-500">{stage.description}</p>
                  </div>
                  {currentZone && (
                    <div className="text-right">
                      <p className="text-xs text-gray-500">Zone Progress</p>
                      <p className="text-xl font-bold text-[#4F46E5]">{zoneProgress}%</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* ── Programme setup (only on subjects view, if missing) ── */}
            {view === 'subjects' && (!programme || !shsLevel) && (
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-6 mb-6">
                <div className="flex items-start gap-4">
                  <div className="flex-1">
                    <h2 className="font-semibold text-[#1E293B] mb-1">Set Up Your Learning Path</h2>
                    <p className="text-sm text-gray-500 mb-4">Tell us your programme and SHS level for the right lessons.</p>
                    <div className="grid sm:grid-cols-2 gap-3 mb-4">
                      <div className="relative" ref={progDropdownRef}>
                        <button
                          type="button"
                          onClick={() => setProgDropdownOpen(!progDropdownOpen)}
                          className="w-full flex items-center justify-between px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-[#1E293B] transition"
                        >
                          <span>{onboardingProg}</span>
                          <ChevronDown className={`w-3.5 h-3.5 text-gray-400 transition-transform ${progDropdownOpen ? 'rotate-180' : ''}`} />
                        </button>
                        {progDropdownOpen && (
                          <div className="absolute z-20 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden">
                            {(['General Science', 'General Arts', 'Business', 'Visual Arts', 'Home Economics', 'Technical'] as const).map((p) => {
                              const isAvailable = p === 'General Science';
                              const isSelected = onboardingProg === p;
                              return (
                                <button
                                  key={p}
                                  type="button"
                                  disabled={!isAvailable}
                                  onClick={() => {
                                    if (isAvailable) {
                                      setOnboardingProg(p);
                                      setProgDropdownOpen(false);
                                    }
                                  }}
                                  className={`w-full flex items-center gap-2 px-3 py-2.5 text-left text-sm transition ${
                                    isSelected ? 'bg-[#EEF2FF] text-[#4F46E5] font-medium' : ''
                                  } ${
                                    isAvailable
                                      ? 'hover:bg-gray-50 cursor-pointer text-[#1E293B]'
                                      : 'text-gray-400 cursor-not-allowed'
                                  }`}
                                >
                                  <span className="flex-1">{p}</span>
                                  {!isAvailable && <Lock className="w-3 h-3 text-gray-300" />}
                                </button>
                              );
                            })}
                          </div>
                        )}
                      </div>
                      <select value={onboardingLevel} onChange={(e) => setOnboardingLevel(e.target.value as SHSLevel)}
                        className="px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-[#1E293B]">
                        <option value="SHS 1">SHS 1</option><option value="SHS 2">SHS 2</option><option value="SHS 3">SHS 3</option><option value="Completed SHS">Completed SHS</option>
                      </select>
                    </div>
                    {onboardingError && <p className="text-xs text-red-500 mb-2">{onboardingError}</p>}
                    <button onClick={async () => {
                      setOnboardingSaving(true); setOnboardingError(null);
                      try { const updated = await updateUserProfile({ programme: onboardingProg, shs_level: onboardingLevel }); setUser(updated); }
                      catch (err) { setOnboardingError(err instanceof Error ? err.message : 'Failed to save'); }
                      finally { setOnboardingSaving(false); }
                    }} disabled={onboardingSaving}
                      className="px-4 py-2 bg-[#4F46E5] text-white text-sm font-medium rounded-lg hover:bg-[#4338CA] transition-colors disabled:opacity-50">
                      {onboardingSaving ? 'Saving...' : 'Get Started'}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* ── Content area ── */}
            <AnimatePresence mode="wait">
              {/* ── Subjects View ── */}
              {view === 'subjects' && (
                <motion.div key="subjects" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  {/* Core Subjects section */}
                  <div className="mb-2">
                    <h2 className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-3">Core Subjects</h2>
                    <div className="grid sm:grid-cols-2 gap-4">
                      {SUBJECTS.map((subject) => {
                        const levelLessons = shsLevel
                          ? getLessonsForSubject(subject.id, programme).filter(
                              (l) => l.suggestedLevel === shsLevel || l.shsLevels?.includes(shsLevel)
                            )
                          : [];
                        const lessons = shsLevel ? levelLessons : getLessonsForSubject(subject.id, programme);
                        const completed = lessons.filter((l) => completedLessons.has(l.id)).length;
                        const hasContent = lessons.length > 0;
                        return (
                          <button
                            key={subject.id}
                            onClick={() => hasContent && handleSelectSubject(subject.id)}
                            disabled={!hasContent}
                            className={`text-left bg-white border rounded-xl p-5 transition-all duration-200 ${
                              hasContent
                                ? 'border-gray-200 hover:border-gray-300 hover:shadow-sm cursor-pointer'
                                : 'border-gray-100 opacity-50 cursor-default'
                            }`}
                          >
                            <div className="flex items-start gap-4">
                              <div
                                className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold text-base flex-shrink-0"
                                style={{ backgroundColor: subject.color }}
                              >
                                {subject.label.charAt(0)}
                              </div>
                              <div className="flex-1 min-w-0">
                                <h3 className="font-semibold text-[#1E293B]">{subject.label}</h3>
                                <p className="text-xs text-gray-500 mt-0.5">{subject.description}</p>
                                {hasContent ? (
                                  <div className="flex items-center gap-2 mt-2">
                                    <div className="flex-1 bg-gray-100 rounded-full h-1 overflow-hidden">
                                      <div className="h-full bg-[#4F46E5] rounded-full transition-all"
                                        style={{ width: `${(completed / Math.max(1, lessons.length)) * 100}%` }} />
                                    </div>
                                    <span className="text-xs text-gray-400 flex-shrink-0">{completed}/{lessons.length}</span>
                                  </div>
                                ) : (
                                  <p className="text-xs text-gray-400 mt-2 italic">Coming soon</p>
                                )}
                              </div>
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  {/* Divider */}
                  <div className="relative my-8">
                    <div className="absolute inset-0 flex items-center">
                      <div className="w-full border-t border-gray-200" />
                    </div>
                    <div className="relative flex justify-center">
                      <span className="bg-gray-50 px-3 text-xs text-gray-400 font-medium">Elective Subjects</span>
                    </div>
                  </div>

                  {/* View Elective Subjects button */}
                  <button
                    onClick={() => setView('elective-subjects')}
                    className="w-full text-left bg-white border-2 border-dashed border-gray-200 rounded-xl p-5 transition-all duration-200 hover:border-[#4F46E5]/40 hover:bg-[#EEF2FF]/30 cursor-pointer group"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-xl bg-[#EEF2FF] flex items-center justify-center text-[#4F46E5] font-bold text-base flex-shrink-0 group-hover:bg-[#4F46E5] group-hover:text-white transition-colors">
                        +
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-[#1E293B] group-hover:text-[#4F46E5] transition-colors">Explore Elective Subjects</h3>
                        <p className="text-xs text-gray-500 mt-0.5">Biology, Chemistry, Physics, Elective Mathematics and more</p>
                      </div>
                      <svg className="w-5 h-5 text-gray-300 group-hover:text-[#4F46E5] transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </button>
                </motion.div>
              )}

              {/* ── Elective Subjects View ── */}
              {view === 'elective-subjects' && (
                <motion.div key="elective-subjects" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                  <h2 className="text-sm font-bold uppercase tracking-widest text-gray-400 mb-3">Science Electives</h2>
                  <div className="grid sm:grid-cols-2 gap-4">
                    {ELECTIVE_SUBJECTS.map((subject) => {
                      const levelLessons = shsLevel
                        ? getLessonsForSubject(subject.id, programme).filter(
                            (l) => l.suggestedLevel === shsLevel || l.shsLevels?.includes(shsLevel)
                          )
                        : [];
                      const lessons = shsLevel ? levelLessons : getLessonsForSubject(subject.id, programme);
                      const completed = lessons.filter((l) => completedLessons.has(l.id)).length;
                      const hasContent = lessons.length > 0;
                      return (
                        <button
                          key={subject.id}
                          onClick={() => hasContent && handleSelectSubject(subject.id)}
                          disabled={!hasContent}
                          className={`text-left bg-white border rounded-xl p-5 transition-all duration-200 ${
                            hasContent
                              ? 'border-gray-200 hover:border-gray-300 hover:shadow-sm cursor-pointer'
                              : 'border-gray-100 opacity-50 cursor-default'
                          }`}
                        >
                          <div className="flex items-start gap-4">
                            <div
                              className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold text-base flex-shrink-0"
                              style={{ backgroundColor: subject.color }}
                            >
                              {subject.icon}
                            </div>
                            <div className="flex-1 min-w-0">
                              <h3 className="font-semibold text-[#1E293B]">{subject.label}</h3>
                              <p className="text-xs text-gray-500 mt-0.5">{subject.description}</p>
                              {hasContent ? (
                                <div className="flex items-center gap-2 mt-2">
                                  <div className="flex-1 bg-gray-100 rounded-full h-1 overflow-hidden">
                                    <div className="h-full bg-[#4F46E5] rounded-full transition-all"
                                      style={{ width: `${(completed / Math.max(1, lessons.length)) * 100}%` }} />
                                  </div>
                                  <span className="text-xs text-gray-400 flex-shrink-0">{completed}/{lessons.length}</span>
                                </div>
                              ) : (
                                <p className="text-xs text-gray-400 mt-2 italic">Coming soon</p>
                              )}
                            </div>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </motion.div>
              )}

              {/* ── Coming Soon View ── */}
              {view === 'coming-soon' && selectedSubject && (
                <motion.div key="coming-soon" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                  <div className="bg-white border border-gray-200 rounded-xl p-10 text-center">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-amber-100 flex items-center justify-center">
                      <svg className="w-8 h-8 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                      </svg>
                    </div>
                    <h2 className="text-xl font-bold text-[#1E293B] mb-2">
                      {selectedSubject} — {shsLevel || 'Content'}
                    </h2>
                    <p className="text-gray-500 mb-4 max-w-md mx-auto">
                      Learning content for <strong>{shsLevel || 'your level'}</strong> in <strong>{selectedSubject}</strong> is not yet available. We are working on adding it soon!
                    </p>
                    <button
                      onClick={() => { setView('subjects'); setSelectedSubject(null); }}
                      className="px-5 py-2 bg-[#4F46E5] text-white text-sm font-medium rounded-lg hover:bg-[#4338CA] transition-colors"
                    >
                      Back to Subjects
                    </button>
                  </div>
                </motion.div>
              )}

              {/* ── Modules View ── */}
              {view === 'modules' && selectedSubject && selectedLevel && (
                <motion.div key="modules" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                  <div className="grid sm:grid-cols-2 gap-4">
                    {getModulesForLevel(selectedSubject, selectedLevel, programme).map((mod) => {
                      const completed = mod.lessons.filter((l) => completedLessons.has(l.id)).length;
                      const firstUnlocked = mod.lessons.find((l) => isLessonUnlocked(l));
                      const allLocked = !firstUnlocked;
                      return (
                        <button
                          key={mod.key}
                          onClick={() => !allLocked && handleSelectModule(mod.key, mod.label)}
                          disabled={allLocked}
                          className={`text-left bg-white border rounded-xl p-5 transition-all duration-200 ${
                            !allLocked
                              ? 'border-gray-200 hover:border-gray-300 hover:shadow-sm cursor-pointer'
                              : 'border-gray-100 opacity-40 cursor-default'
                          }`}
                        >
                          <div className="flex items-start justify-between gap-3">
                            <div className="flex-1 min-w-0">
                              <h3 className="font-semibold text-[#1E293B]">{mod.label}</h3>
                              <p className="text-xs text-gray-500 mt-1">{mod.lessons.length} lessons</p>
                            </div>
                            <span className="text-xs font-medium text-[#4F46E5] flex-shrink-0">{completed}/{mod.lessons.length}</span>
                          </div>
                          <div className="mt-3 w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
                            <div className="h-full bg-[#4F46E5] rounded-full transition-all"
                              style={{ width: `${(completed / Math.max(1, mod.lessons.length)) * 100}%` }} />
                          </div>
                          {allLocked && <p className="text-xs text-gray-400 mt-2 italic">Complete previous lessons to unlock</p>}
                        </button>
                      );
                    })}
                  </div>
                </motion.div>
              )}

              {/* ── Lessons View ── */}
              {view === 'lessons' && selectedSubject && selectedLevel && selectedModule && (
                <motion.div key="lessons" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                  <div className="space-y-3">
                    {currentModuleLessons.map((lesson, idx) => {
                      const isCompleted = completedLessons.has(lesson.id);
                      const unlocked = isLessonUnlocked(lesson);
                      const locked = !unlocked && !isCompleted;
                      return (
                        <button
                          key={lesson.id}
                          onClick={() => !locked && handleSelectLesson(lesson.id)}
                          disabled={locked}
                          className={`w-full text-left p-4 rounded-xl border transition-all duration-200 ${
                            isCompleted
                              ? 'bg-[#EEF2FF] border-[#C7D2FE]'
                              : locked
                              ? 'bg-gray-50 border-gray-200 opacity-40 cursor-not-allowed'
                              : 'bg-white border-gray-200 hover:bg-gray-50 hover:border-gray-300'
                          }`}
                        >
                          <div className="flex items-center gap-3">
                            {/* Status indicator */}
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                              isCompleted
                                ? 'bg-[#4F46E5]'
                                : locked
                                ? 'bg-gray-200'
                                : 'bg-gray-100 border border-gray-300'
                            }`}>
                              {isCompleted ? (
                                <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" />
                                </svg>
                              ) : locked ? (
                                <span className="text-xs font-bold text-gray-400">!</span>
                              ) : (
                                <span className="text-xs font-bold text-gray-500">{idx + 1}</span>
                              )}
                            </div>

                            {/* Content */}
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-0.5">
                                <span className={`text-xs font-bold uppercase tracking-wider ${
                                  isCompleted ? 'text-[#4F46E5]' : 'text-gray-500'
                                }`}>
                                  {lesson.subject}
                                </span>
                                {isCompleted && <span className="text-xs text-[#4F46E5]">Done</span>}
                              </div>
                              <p className={`font-semibold truncate ${isCompleted ? 'text-[#1E293B]' : locked ? 'text-gray-400' : 'text-[#1E293B]'}`}>
                                {lesson.title}
                              </p>
                              {/* Difficulty dots */}
                              <div className="flex items-center gap-1 mt-1">
                                {Array.from({ length: 5 }).map((_, d) => (
                                  <div key={d} className={`w-1.5 h-1.5 rounded-full ${
                                    d < lesson.difficulty ? 'bg-[#4F46E5]/70' : 'bg-gray-300'
                                  }`} />
                                ))}
                              </div>
                            </div>

                            {/* XP & Time */}
                            <div className="text-right flex-shrink-0">
                              <span className="text-sm font-bold text-gray-500">{lesson.xpReward} XP</span>
                              <div className="text-xs text-gray-400 mt-0.5">{lesson.estimatedMinutes} min</div>
                            </div>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}
