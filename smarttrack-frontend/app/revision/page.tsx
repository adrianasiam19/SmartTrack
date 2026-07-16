'use client';

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, BookOpen, Clock, Star, ArrowLeft, MessageSquare, Sparkles, ChevronRight, X, Bookmark, HelpCircle, CheckCircle, Lightbulb, Award, AlertTriangle, TrendingUp, History, Loader2, Bot, Send, Plus, Zap } from 'lucide-react';
import Sidebar from '../components/Sidebar';
import BottomNav from '../components/BottomNav';
import AppLayout from '../components/AppLayout';
import { getCurrentUser, getAccessToken, getStoredUser, type UserProfile } from '../lib/authApi';
import { ALL_LESSONS, type Lesson } from '../lib/learningContent';
import { generateTopicContent, askAIQuestion, type TopicContent } from '../lib/revisionApi';

// ── Types ──────────────────────────────────────────────────────────────────
type ViewState = 'dashboard' | 'topic';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface BookmarkEntry {
  topic: string;
  addedAt: string;
}

interface HistoryEntry {
  topic: string;
  visitedAt: string;
  subject?: string;
}

// ── Constants ──────────────────────────────────────────────────────────────
const POPULAR_WASSCE_TOPICS = [
  { topic: 'Differentiation', subject: 'Elective Mathematics', icon: '∫' },
  { topic: 'Photosynthesis', subject: 'Biology', icon: '🌿' },
  { topic: 'Organic Chemistry', subject: 'Chemistry', icon: '⚗️' },
  { topic: 'Cell Division (Mitosis & Meiosis)', subject: 'Biology', icon: '🧬' },
  { topic: 'Trigonometry', subject: 'Core Mathematics', icon: '📐' },
  { topic: 'Probability', subject: 'Core Mathematics', icon: '🎲' },
  { topic: 'Genetics', subject: 'Biology', icon: '🧬' },
  { topic: 'Electromagnetism', subject: 'Physics', icon: '⚡' },
  { topic: 'Sets and Venn Diagrams', subject: 'Core Mathematics', icon: '🔢' },
  { topic: 'Chemical Bonding', subject: 'Chemistry', icon: '🔗' },
  { topic: 'Newton\'s Laws of Motion', subject: 'Physics', icon: '🏋️' },
  { topic: 'Logarithms and Indices', subject: 'Core Mathematics', icon: '📊' },
  { topic: 'Ecosystems', subject: 'Integrated Science', icon: '🌍' },
  { topic: 'Integration', subject: 'Elective Mathematics', icon: '∫' },
  { topic: 'Acids, Bases and Salts', subject: 'Chemistry', icon: '🧪' },
  { topic: 'Vectors', subject: 'Elective Mathematics', icon: '➡️' },
  { topic: 'Grammar and Sentence Structure', subject: 'English Language', icon: '📝' },
  { topic: 'Circulatory System', subject: 'Integrated Science', icon: '🫀' },
  { topic: 'Thermodynamics', subject: 'Physics', icon: '🔥' },
  { topic: 'Algebraic Expressions', subject: 'Core Mathematics', icon: '✏️' },
];

const SUBJECT_COLORS: Record<string, string> = {
  'Core Mathematics': '#4F46E5',
  'English Language': '#D97706',
  'Integrated Science': '#059669',
  'Social Studies': '#7C3AED',
  'Biology': '#16A34A',
  'Chemistry': '#0EA5E9',
  'Physics': '#6366F1',
  'Elective Mathematics': '#7C3AED',
};

const QUICK_ACTIONS = [
  { label: 'Explain this simply', icon: Lightbulb, prompt: 'Explain this topic in very simple language with everyday examples.' },
  { label: 'Give an example', icon: Plus, prompt: 'Give me another worked example on this topic.' },
  { label: 'Generate quiz', icon: HelpCircle, prompt: 'Generate 5 WASSCE-style multiple choice questions on this topic.' },
  { label: 'Summarise', icon: BookOpen, prompt: 'Give me a brief summary of this topic with key points.' },
  { label: 'Exam tips', icon: Award, prompt: 'What are the most important exam tips for this topic in WASSCE?' },
  { label: 'Compare topics', icon: TrendingUp, prompt: 'Compare this topic with related topics I should know for WASSCE.' },
];

// ── localStorage helpers ──────────────────────────────────────────────────
const STORAGE = {
  bookmarks: 'atlas_revision_bookmarks',
  history: 'atlas_revision_history',
  recentSearches: 'atlas_revision_recent',
};

function loadBookmarks(): BookmarkEntry[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = localStorage.getItem(STORAGE.bookmarks);
    return raw ? JSON.parse(raw) : [];
  } catch { return []; }
}

function saveBookmarks(bookmarks: BookmarkEntry[]) {
  localStorage.setItem(STORAGE.bookmarks, JSON.stringify(bookmarks));
}

function loadHistory(): HistoryEntry[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = localStorage.getItem(STORAGE.history);
    return raw ? JSON.parse(raw) : [];
  } catch { return []; }
}

function saveHistory(history: HistoryEntry[]) {
  localStorage.setItem(STORAGE.history, JSON.stringify(history));
}

function loadRecentSearches(): string[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = localStorage.getItem(STORAGE.recentSearches);
    return raw ? JSON.parse(raw) : [];
  } catch { return []; }
}

function saveRecentSearches(searches: string[]) {
  localStorage.setItem(STORAGE.recentSearches, JSON.stringify(searches));
}

// ── Subject badge component ──────────────────────────────────────────────
function SubjectBadge({ subject }: { subject: string }) {
  const color = SUBJECT_COLORS[subject] || '#6B7280';
  return (
    <span
      className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium"
      style={{
        backgroundColor: `${color}15`,
        color: color,
        border: `1px solid ${color}30`,
      }}
    >
      {subject}
    </span>
  );
}

// ── Main Component ────────────────────────────────────────────────────────
export default function RevisionHub() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  // Navigation state
  const [view, setView] = useState<ViewState>('dashboard');
  const [currentTopic, setCurrentTopic] = useState<string>('');
  const [topicContent, setTopicContent] = useState<TopicContent | null>(null);
  const [contentLoading, setContentLoading] = useState(false);
  const [contentError, setContentError] = useState<string | null>(null);

  // Search
  const [searchQuery, setSearchQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const [filteredSuggestions, setFilteredSuggestions] = useState<typeof POPULAR_WASSCE_TOPICS>([]);

  // Local content search results
  const [localContentMatches, setLocalContentMatches] = useState<Lesson[]>([]);

  // Bookmarks & History (localStorage)
  const [bookmarks, setBookmarks] = useState<BookmarkEntry[]>([]);
  const [revisionHistory, setRevisionHistory] = useState<HistoryEntry[]>([]);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  // AI Tutor
  const [aiOpen, setAiOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Active section for topic view
  const [activeSection, setActiveSection] = useState<string>('explanation');

  // ── Auth ────────────────────────────────────────────────────────────────
  useEffect(() => {
    const init = async () => {
      try {
        if (!getAccessToken()) { router.push('/login'); return; }
        const cached = getStoredUser();
        if (cached) setUser(cached);
        const fresh = await getCurrentUser();
        setUser(fresh);

        // Load local data
        setBookmarks(loadBookmarks());
        setRevisionHistory(loadHistory());
        setRecentSearches(loadRecentSearches());

        // Check URL params for topic
        const params = new URLSearchParams(window.location.search);
        const topicParam = params.get('topic');
        if (topicParam) {
          handleTopicSelect(decodeURIComponent(topicParam));
        }
      } catch { router.push('/login'); }
      finally { setLoading(false); }
    };
    init();
  }, [router]);

  // ── Scroll chat to bottom ──────────────────────────────────────────────
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  // ── Close search suggestions on outside click ──────────────────────────
  useEffect(() => {
    if (!showSuggestions) return;
    const handleClick = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [showSuggestions]);

  // ── Filter suggestions on search ───────────────────────────────────────
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredSuggestions([]);
      return;
    }
    const q = searchQuery.toLowerCase();
    const filtered = POPULAR_WASSCE_TOPICS.filter(
      (t) => t.topic.toLowerCase().includes(q) || t.subject.toLowerCase().includes(q)
    ).slice(0, 8);
    setFilteredSuggestions(filtered);
    setShowSuggestions(filtered.length > 0);
  }, [searchQuery]);

  // ── Handle topic selection ─────────────────────────────────────────────
  const handleTopicSelect = useCallback(async (topic: string) => {
    setCurrentTopic(topic);
    setView('topic');
    setContentLoading(true);
    setContentError(null);
    setAiOpen(false);
    setChatMessages([]);
    setLocalContentMatches([]);

    // Step 1: Search Atlas' own database for matching lessons
    const topicLower = topic.toLowerCase();
    const matchingLessons = ALL_LESSONS.filter(l =>
      l.title.toLowerCase().includes(topicLower) ||
      l.subject.toLowerCase().includes(topicLower)
    );
    const uniqueSubjects = [...new Set(matchingLessons.map(l => l.subject))];
    setLocalContentMatches(matchingLessons.slice(0, 5));

    // Step 2: Check saved section progress for this topic
    const savedSection = localStorage.getItem(`atlas_revision_section_${topic}`);
    if (savedSection) {
      setActiveSection(savedSection);
    } else {
      setActiveSection('explanation');
    }

    // Add to recent searches
    const updatedRecent = [topic, ...recentSearches.filter(s => s !== topic)].slice(0, 10);
    setRecentSearches(updatedRecent);
    saveRecentSearches(updatedRecent);

    // Add to history
    const historyEntry: HistoryEntry = {
      topic,
      visitedAt: new Date().toISOString(),
      subject: uniqueSubjects[0] || undefined,
    };
    const updatedHistory = [historyEntry, ...revisionHistory.filter(h => h.topic !== topic)].slice(0, 50);
    setRevisionHistory(updatedHistory);
    saveHistory(updatedHistory);

    // Step 3: Generate AI content (always generate, local content shown as supplement)
    try {
      const result = await generateTopicContent(topic);
      if (result.success && result.data) {
        // If we found local matches, add the subject from curriculum
        if (uniqueSubjects.length > 0) {
          result.data.subject = uniqueSubjects[0];
        }
        setTopicContent(result.data);
      } else {
        // If AI fails but we have local matches, create a minimal topic content
        if (matchingLessons.length > 0) {
          setTopicContent({
            title: topic,
            subject: uniqueSubjects[0] || 'General',
            explanation: `This topic is covered in the Atlas curriculum. Click on the related lessons below to study it in detail.`,
            key_concepts: [],
            formulae: [],
            worked_examples: [],
            common_mistakes: [],
            exam_tips: ['Check the related curriculum lessons for structured learning on this topic.'],
            practice_questions: [],
            summary: `This topic is covered in the ${uniqueSubjects.join(', ')} curriculum.`,
          });
        } else {
          setContentError(result.error || 'Failed to generate content');
        }
      }
    } catch (err) {
      // If error but we have local matches, show them as fallback
      if (matchingLessons.length > 0) {
        setTopicContent({
          title: topic,
          subject: uniqueSubjects[0] || 'General',
          explanation: `This topic is covered in the Atlas curriculum under ${uniqueSubjects.join(', ')}. Please refer to the related lessons below.`,
          key_concepts: [],
          formulae: [],
          worked_examples: [],
          common_mistakes: [],
          exam_tips: ['Study the related lessons for comprehensive coverage.'],
          practice_questions: [],
          summary: `Found in ${uniqueSubjects.join(', ')} curriculum.`,
        });
      } else {
        setContentError(err instanceof Error ? err.message : 'An unexpected error occurred');
      }
    } finally {
      setContentLoading(false);
    }
  }, [recentSearches, revisionHistory]);

  // ── Handle search ─────────────────────────────────────────────────────
  const handleSearch = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    handleTopicSelect(searchQuery.trim());
    setSearchQuery('');
    setShowSuggestions(false);
  }, [searchQuery, handleTopicSelect]);

  const handleSuggestionClick = useCallback((topic: string) => {
    setSearchQuery('');
    setShowSuggestions(false);
    handleTopicSelect(topic);
  }, [handleTopicSelect]);

  // ── Back to dashboard ──────────────────────────────────────────────────
  const handleBackToDashboard = useCallback(() => {
    setView('dashboard');
    setCurrentTopic('');
    setTopicContent(null);
    setAiOpen(false);
    setChatMessages([]);
  }, []);

  // ── Bookmarks ──────────────────────────────────────────────────────────
  const isBookmarked = (topic: string) => bookmarks.some(b => b.topic === topic);

  const toggleBookmark = useCallback((topic: string) => {
    if (isBookmarked(topic)) {
      const updated = bookmarks.filter(b => b.topic !== topic);
      setBookmarks(updated);
      saveBookmarks(updated);
    } else {
      const entry: BookmarkEntry = { topic, addedAt: new Date().toISOString() };
      const updated = [entry, ...bookmarks];
      setBookmarks(updated);
      saveBookmarks(updated);
    }
  }, [bookmarks]);

  // ── AI Tutor ───────────────────────────────────────────────────────────
  const handleSendChat = useCallback(async () => {
    if (!chatInput.trim() || chatLoading || !currentTopic) return;

    const userMessage = chatInput.trim();
    setChatInput('');
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setChatLoading(true);

    const historyForApi = chatMessages.map(msg => ({
      role: msg.role,
      content: msg.content,
    }));

    try {
      const result = await askAIQuestion(currentTopic, userMessage, historyForApi);
      if (result.success && result.response) {
        setChatMessages(prev => [...prev, { role: 'assistant', content: result.response! }]);
      } else {
        setChatMessages(prev => [...prev, { role: 'assistant', content: result.error || 'Sorry, I couldn\'t process that. Please try again.' }]);
      }
    } catch (err) {
      setChatMessages(prev => [...prev, { role: 'assistant', content: 'An error occurred. Please try again.' }]);
    } finally {
      setChatLoading(false);
    }
  }, [chatInput, chatLoading, currentTopic, chatMessages]);

  const handleQuickAction = useCallback(async (prompt: string) => {
    if (!currentTopic) return;
    setChatMessages(prev => [...prev, { role: 'user', content: prompt }]);
    setChatLoading(true);

    const historyForApi = chatMessages.map(msg => ({
      role: msg.role,
      content: msg.content,
    }));
    historyForApi.push({ role: 'user', content: prompt });

    try {
      const result = await askAIQuestion(currentTopic, prompt, historyForApi);
      if (result.success && result.response) {
        setChatMessages(prev => [...prev, { role: 'assistant', content: result.response! }]);
      } else {
        setChatMessages(prev => [...prev, { role: 'assistant', content: result.error || 'Sorry, I couldn\'t process that.' }]);
      }
    } catch {
      setChatMessages(prev => [...prev, { role: 'assistant', content: 'An error occurred.' }]);
    } finally {
      setChatLoading(false);
    }
  }, [currentTopic, chatMessages]);

  // ── Loading state ──────────────────────────────────────────────────────
  if (loading) return (
    <AppLayout>
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-10 h-10 border-4 border-[#2563EB] border-t-transparent rounded-full animate-spin" />
      </div>
    </AppLayout>
  );
  if (!user) return null;

  const firstName = user.full_name?.split(' ')[0] || 'there';

  // ── Topic View ──────────────────────────────────────────────────────────
  if (view === 'topic') {
    return (
      <AppLayout>
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex-1 lg:pb-0 pb-20">
            <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-6 pb-8">

              {/* Back button + topic title */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <button
                    onClick={handleBackToDashboard}
                    className="p-2 rounded-xl hover:bg-gray-100 text-gray-400 transition-colors"
                  >
                    <ArrowLeft className="w-5 h-5" />
                  </button>
                  <div>
                    <h1 className="text-xl sm:text-2xl font-bold text-[#1E293B]">
                      {topicContent?.title || currentTopic}
                    </h1>
                    {topicContent?.subject && (
                      <SubjectBadge subject={topicContent.subject} />
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => toggleBookmark(currentTopic)}
                    className={`p-2 rounded-xl transition-colors ${
                      isBookmarked(currentTopic)
                        ? 'text-amber-500 bg-amber-50 hover:bg-amber-100'
                        : 'text-gray-400 hover:bg-gray-100'
                    }`}
                  >
                    <Bookmark className={`w-5 h-5 ${isBookmarked(currentTopic) ? 'fill-current' : ''}`} />
                  </button>
                  <button
                    onClick={() => setAiOpen(!aiOpen)}
                    className={`p-2 rounded-xl transition-colors ${
                      aiOpen
                        ? 'text-[#2563EB] bg-[#EFF6FF]'
                        : 'text-gray-400 hover:bg-gray-100'
                    }`}
                  >
                    <Bot className="w-5 h-5" />
                  </button>
                </div>
              </div>

              <div className="flex gap-6">
                {/* Main content area */}
                <div className={`flex-1 min-w-0 ${aiOpen ? 'hidden lg:block' : ''}`}>
                  {contentLoading ? (
                    /* Loading skeleton */
                    <div className="space-y-6 animate-pulse">
                      <div className="h-8 bg-gray-200 rounded-lg w-3/4" />
                      <div className="h-4 bg-gray-200 rounded w-1/4" />
                      <div className="space-y-3">
                        <div className="h-4 bg-gray-200 rounded" />
                        <div className="h-4 bg-gray-200 rounded w-5/6" />
                        <div className="h-4 bg-gray-200 rounded w-4/6" />
                        <div className="h-4 bg-gray-200 rounded w-3/4" />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="h-32 bg-gray-200 rounded-xl" />
                        <div className="h-32 bg-gray-200 rounded-xl" />
                      </div>
                      <div className="h-48 bg-gray-200 rounded-xl" />
                    </div>
                  ) : contentError ? (
                    <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center">
                      <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-3" />
                      <h2 className="text-lg font-bold text-red-700 mb-2">Generation Failed</h2>
                      <p className="text-red-600 mb-4">{contentError}</p>
                      <button
                        onClick={() => handleTopicSelect(currentTopic)}
                        className="px-5 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                      >
                        Try Again
                      </button>
                    </div>
                  ) : topicContent ? (
                    <>
                      {/* AI source badge */}
                      {topicContent._source && (
                        <div className="flex items-center gap-2 text-xs text-gray-400 mb-4">
                          <Sparkles className="w-3 h-3" />
                          <span>Generated by AI</span>
                        </div>
                      )}

                      {/* Sticky section tabs */}
                      <div className="sticky top-16 z-20 -mx-4 px-4 bg-[#F8FAFC] border-b border-gray-200 mb-6 overflow-x-auto">
                        <div className="flex gap-1 py-2 min-w-max">
                          {[
                            { id: 'explanation', label: 'Explanation' },
                            { id: 'concepts', label: 'Key Concepts' },
                            { id: 'formulae', label: 'Formulae' },
                            { id: 'examples', label: 'Worked Examples' },
                            { id: 'mistakes', label: 'Mistakes' },
                            { id: 'tips', label: 'Exam Tips' },
                            { id: 'practice', label: 'Practice' },
                            { id: 'summary', label: 'Summary' },
                          ].map(section => (
                            <button
                              key={section.id}
                              onClick={() => {
                                setActiveSection(section.id);
                                localStorage.setItem(`atlas_revision_section_${currentTopic}`, section.id);
                              }}
                              className={`px-3 py-1.5 rounded-lg text-sm whitespace-nowrap transition-colors ${
                                activeSection === section.id
                                  ? 'bg-[#2563EB] text-white font-medium'
                                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                              }`}
                            >
                              {section.label}
                            </button>
                          ))}
                        </div>
                      </div>

                      <div className="space-y-8">
                        {/* ── Local Curriculum Matches ── */}
                        {localContentMatches.length > 0 && (
                          <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-white border border-[#C7D2FE] rounded-xl p-6"
                          >
                            <h2 className="text-lg font-bold text-[#1E293B] mb-4 flex items-center gap-2">
                              <BookOpen className="w-5 h-5 text-[#2563EB]" />
                              Found in Atlas Curriculum
                            </h2>
                            <p className="text-xs text-gray-500 mb-4">
                              This topic is also covered in the following lessons:
                            </p>
                            <div className="space-y-3">
                              {localContentMatches.map((lesson, i) => (
                                <div key={i} className="flex items-start gap-3 p-3 bg-[#F8FAFC] rounded-lg border border-gray-100">
                                  <div className="w-8 h-8 rounded-lg bg-[#EEF2FF] flex items-center justify-center flex-shrink-0">
                                    <BookOpen className="w-4 h-4 text-[#4F46E5]" />
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <p className="text-sm font-semibold text-[#1E293B]">{lesson.title}</p>
                                    <p className="text-xs text-gray-500">{lesson.subject}</p>
                                  </div>
                                </div>
                              ))}
                            </div>
                            <p className="text-xs text-gray-400 mt-3">
                              You can find these in the Learning Center for structured study.
                            </p>
                          </motion.div>
                        )}

                        {/* ── Explanation Section ── */}
                        <motion.div
                          id="explanation"
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="bg-white border border-gray-200 rounded-xl p-6"
                        >
                          <h2 className="text-lg font-bold text-[#1E293B] mb-4 flex items-center gap-2">
                            <BookOpen className="w-5 h-5 text-[#2563EB]" />
                            Explanation
                          </h2>
                          <div className="prose prose-sm max-w-none text-[#475569] leading-relaxed whitespace-pre-line">
                            {topicContent.explanation}
                          </div>
                        </motion.div>

                        {/* ── Key Concepts Section ── */}
                        {topicContent.key_concepts.length > 0 && (
                          <motion.div
                            id="concepts"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-white border border-gray-200 rounded-xl p-6"
                          >
                            <h2 className="text-lg font-bold text-[#1E293B] mb-4 flex items-center gap-2">
                              <Lightbulb className="w-5 h-5 text-amber-500" />
                              Key Concepts
                            </h2>
                            <div className="grid sm:grid-cols-2 gap-3">
                              {topicContent.key_concepts.map((concept, i) => (
                                <div key={i} className="flex items-start gap-3 p-3 bg-[#F8FAFC] rounded-lg border border-gray-100">
                                  <div className="w-6 h-6 rounded-full bg-[#2563EB]/10 text-[#2563EB] flex items-center justify-center text-xs font-bold flex-shrink-0">
                                    {i + 1}
                                  </div>
                                  <p className="text-sm text-[#475569]">{concept}</p>
                                </div>
                              ))}
                            </div>
                          </motion.div>
                        )}

                        {/* ── Formulae Section ── */}
                        {topicContent.formulae.length > 0 && (
                          <motion.div
                            id="formulae"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-white border border-gray-200 rounded-xl p-6"
                          >
                            <h2 className="text-lg font-bold text-[#1E293B] mb-4 flex items-center gap-2">
                              <Zap className="w-5 h-5 text-purple-500" />
                              Important Formulae
                            </h2>
                            <div className="grid sm:grid-cols-2 gap-4">
                              {topicContent.formulae.map((f, i) => (
                                <div key={i} className="bg-gradient-to-br from-[#F5F3FF] to-[#EDE9FE] border border-[#DDD6FE] rounded-lg p-4">
                                  <p className="text-xs font-medium text-[#7C3AED] mb-1">{f.title}</p>
                                  <p className="text-sm font-mono font-bold text-[#1E293B]">{f.formula}</p>
                                </div>
                              ))}
                            </div>
                          </motion.div>
                        )}

                        {/* ── Worked Examples Section ── */}
                        {topicContent.worked_examples.length > 0 && (
                          <motion.div
                            id="examples"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-white border border-gray-200 rounded-xl p-6"
                          >
                            <h2 className="text-lg font-bold text-[#1E293B] mb-4 flex items-center gap-2">
                              <CheckCircle className="w-5 h-5 text-green-500" />
                              Worked Examples
                            </h2>
                            <div className="space-y-4">
                              {topicContent.worked_examples.map((ex, i) => (
                                <div key={i} className="border border-gray-200 rounded-lg overflow-hidden">
                                  <div className="bg-gradient-to-r from-[#F0FDF4] to-[#DCFCE7] p-4 border-b border-gray-200">
                                    <p className="text-xs font-bold text-green-700 mb-1">Question {i + 1}</p>
                                    <p className="text-sm text-[#1E293B]">{ex.question}</p>
                                  </div>
                                  <div className="bg-[#FAFAFA] p-4">
                                    <p className="text-xs font-bold text-[#475569] mb-1">Solution</p>
                                    <p className="text-sm text-[#1E293B] whitespace-pre-line">{ex.solution}</p>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </motion.div>
                        )}

                        {/* ── Common Mistakes Section ── */}
                        {topicContent.common_mistakes.length > 0 && (
                          <motion.div
                            id="mistakes"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-white border border-gray-200 rounded-xl p-6"
                          >
                            <h2 className="text-lg font-bold text-[#1E293B] mb-4 flex items-center gap-2">
                              <AlertTriangle className="w-5 h-5 text-red-500" />
                              Common Mistakes
                            </h2>
                            <div className="space-y-3">
                              {topicContent.common_mistakes.map((mistake, i) => (
                                <div key={i} className="flex items-start gap-3 p-3 bg-red-50 border border-red-100 rounded-lg">
                                  <AlertTriangle className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" />
                                  <p className="text-sm text-red-700">{mistake}</p>
                                </div>
                              ))}
                            </div>
                          </motion.div>
                        )}

                        {/* ── Exam Tips Section ── */}
                        {topicContent.exam_tips.length > 0 && (
                          <motion.div
                            id="tips"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-white border border-gray-200 rounded-xl p-6"
                          >
                            <h2 className="text-lg font-bold text-[#1E293B] mb-4 flex items-center gap-2">
                              <Award className="w-5 h-5 text-amber-500" />
                              WASSCE Exam Tips
                            </h2>
                            <div className="space-y-3">
                              {topicContent.exam_tips.map((tip, i) => (
                                <div key={i} className="flex items-start gap-3 p-3 bg-amber-50 border border-amber-100 rounded-lg">
                                  <Award className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
                                  <p className="text-sm text-amber-800">{tip}</p>
                                </div>
                              ))}
                            </div>
                          </motion.div>
                        )}

                        {/* ── Practice Questions Section ── */}
                        {topicContent.practice_questions.length > 0 && (
                          <motion.div
                            id="practice"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-white border border-gray-200 rounded-xl p-6"
                          >
                            <h2 className="text-lg font-bold text-[#1E293B] mb-4 flex items-center gap-2">
                              <HelpCircle className="w-5 h-5 text-[#2563EB]" />
                              Practice Questions
                            </h2>
                            <div className="space-y-6">
                              {topicContent.practice_questions.map((q, i) => (
                                <PracticeQuestionCard key={i} question={q} index={i} />
                              ))}
                            </div>
                          </motion.div>
                        )}

                        {/* ── Summary Section ── */}
                        {topicContent.summary && (
                          <motion.div
                            id="summary"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-gradient-to-br from-[#EEF2FF] to-[#E0E7FF] border border-[#C7D2FE] rounded-xl p-6"
                          >
                            <h2 className="text-lg font-bold text-[#1E293B] mb-3 flex items-center gap-2">
                              <Sparkles className="w-5 h-5 text-[#2563EB]" />
                              Summary
                            </h2>
                            <p className="text-sm text-[#1E293B] leading-relaxed whitespace-pre-line">
                              {topicContent.summary}
                            </p>
                          </motion.div>
                        )}

                        {/* ── AI Follow-up section ── */}
                        <div className="bg-white border border-gray-200 rounded-xl p-6">
                          <h2 className="text-lg font-bold text-[#1E293B] mb-4 flex items-center gap-2">
                            <Bot className="w-5 h-5 text-[#2563EB]" />
                            Ask Atlas AI
                          </h2>
                          <p className="text-sm text-gray-500 mb-4">
                            Get personalised help with this topic. Ask me anything!
                          </p>
                          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                            {QUICK_ACTIONS.slice(0, 6).map((action, i) => (
                              <button
                                key={i}
                                onClick={() => {
                                  setAiOpen(true);
                                  handleQuickAction(action.prompt);
                                }}
                                className="flex items-center gap-2 px-3 py-2.5 text-sm text-[#475569] bg-[#F8FAFC] border border-gray-200 rounded-lg hover:bg-[#EFF6FF] hover:border-[#BFDBFE] hover:text-[#2563EB] transition-all"
                              >
                                <action.icon className="w-4 h-4 flex-shrink-0" />
                                <span className="truncate">{action.label}</span>
                              </button>
                            ))}
                          </div>
                        </div>
                      </div>
                    </>
                  ) : null}
                </div>

                {/* ── AI Tutor Panel (sidebar) ── */}
                {aiOpen && (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="w-full lg:w-96 flex-shrink-0"
                  >
                    <div className="sticky top-20 bg-white border border-gray-200 rounded-xl overflow-hidden flex flex-col"
                      style={{ maxHeight: 'calc(100vh - 8rem)' }}>
                      {/* AI Tutor header */}
                      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gradient-to-r from-[#EFF6FF] to-[#F5F3FF]">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 bg-gradient-to-br from-[#2563EB] to-[#7C3AED] rounded-lg flex items-center justify-center">
                            <Bot className="w-4 h-4 text-white" />
                          </div>
                          <div>
                            <p className="text-sm font-bold text-[#1E293B]">Atlas AI Tutor</p>
                            <p className="text-xs text-gray-500">Revising: {currentTopic}</p>
                          </div>
                        </div>
                        <button
                          onClick={() => setAiOpen(false)}
                          className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>

                      {/* Chat messages */}
                      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
                        {chatMessages.length === 0 ? (
                          <div className="text-center py-8">
                            <Bot className="w-12 h-12 text-[#2563EB]/30 mx-auto mb-3" />
                            <p className="text-sm text-gray-400 mb-2">Ask me anything about</p>
                            <p className="text-sm font-bold text-[#1E293B]">{currentTopic}</p>
                            <div className="mt-6 space-y-2">
                              {QUICK_ACTIONS.slice(0, 4).map((action, i) => (
                                <button
                                  key={i}
                                  onClick={() => handleQuickAction(action.prompt)}
                                  className="w-full text-left px-3 py-2 text-xs text-[#475569] bg-[#F8FAFC] border border-gray-200 rounded-lg hover:bg-[#EFF6FF] hover:border-[#BFDBFE] transition-all"
                                >
                                  <action.icon className="w-3.5 h-3.5 inline mr-1.5 text-[#2563EB]" />
                                  {action.label}
                                </button>
                              ))}
                            </div>
                          </div>
                        ) : (
                          chatMessages.map((msg, i) => (
                            <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}>
                              {msg.role === 'assistant' && (
                                <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#2563EB] to-[#7C3AED] flex items-center justify-center flex-shrink-0 mt-0.5">
                                  <Bot className="w-3.5 h-3.5 text-white" />
                                </div>
                              )}
                              <div className={`max-w-[85%] rounded-xl px-4 py-2.5 text-sm ${
                                msg.role === 'user'
                                  ? 'bg-[#2563EB] text-white'
                                  : 'bg-[#F8FAFC] border border-gray-200 text-[#1E293B]'
                              }`}>
                                <p className="whitespace-pre-line leading-relaxed">{msg.content}</p>
                              </div>
                              {msg.role === 'user' && (
                                <div className="w-7 h-7 rounded-full bg-[#2563EB] flex items-center justify-center flex-shrink-0 mt-0.5">
                                  <span className="text-white text-xs font-bold">
                                    {user.full_name?.charAt(0) || 'U'}
                                  </span>
                                </div>
                              )}
                            </div>
                          ))
                        )}
                        {chatLoading && (
                          <div className="flex gap-3">
                            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#2563EB] to-[#7C3AED] flex items-center justify-center flex-shrink-0">
                              <Bot className="w-3.5 h-3.5 text-white" />
                            </div>
                            <div className="bg-[#F8FAFC] border border-gray-200 rounded-xl px-4 py-3">
                              <div className="flex gap-1">
                                <div className="w-2 h-2 bg-[#2563EB]/40 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                <div className="w-2 h-2 bg-[#2563EB]/40 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                <div className="w-2 h-2 bg-[#2563EB]/40 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                              </div>
                            </div>
                          </div>
                        )}
                        <div ref={chatEndRef} />
                      </div>

                      {/* Chat input */}
                      <div className="border-t border-gray-200 p-3">
                        <form
                          onSubmit={(e) => { e.preventDefault(); handleSendChat(); }}
                          className="flex gap-2"
                        >
                          <input
                            type="text"
                            value={chatInput}
                            onChange={(e) => setChatInput(e.target.value)}
                            placeholder="Ask about this topic..."
                            className="flex-1 px-3 py-2 text-sm bg-[#F8FAFC] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
                            disabled={chatLoading}
                          />
                          <button
                            type="submit"
                            disabled={!chatInput.trim() || chatLoading}
                            className="px-3 py-2 bg-[#2563EB] text-white rounded-lg hover:bg-[#1D4ED8] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <Send className="w-4 h-4" />
                          </button>
                        </form>
                      </div>
                    </div>
                  </motion.div>
                )}
              </div>

            </div>
          </div>
          <BottomNav />
        </div>
      </AppLayout>
    );
  }

  // ── DASHBOARD VIEW ──────────────────────────────────────────────────────
  const greeting = (() => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  })();

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-20">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-8 pb-8">

            {/* ── Header ── */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8"
            >
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 bg-gradient-to-br from-[#2563EB] to-[#7C3AED] rounded-xl flex items-center justify-center shadow-lg shadow-[#2563EB]/20">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl sm:text-3xl font-bold text-[#1E293B]">
                    WASSCE Revision Hub
                  </h1>
                  <p className="text-sm text-[#475569]">
                    {greeting}, {firstName} · SHS 3
                  </p>
                </div>
              </div>
            </motion.div>

            {/* ── Search Bar ── */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className="relative mb-8"
              ref={searchRef}
            >
              <form onSubmit={handleSearch}>
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    ref={searchInputRef}
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onFocus={() => {
                      if (searchQuery.trim() && filteredSuggestions.length > 0) {
                        setShowSuggestions(true);
                      }
                    }}
                    placeholder="Search any WASSCE topic..."
                    className="w-full pl-12 pr-12 py-4 bg-white border-2 border-[#BFDBFE] rounded-2xl text-base text-[#1E293B] placeholder-gray-400 focus:outline-none focus:border-[#2563EB] focus:ring-4 focus:ring-[#2563EB]/10 transition-all shadow-sm"
                  />
                  {searchQuery && (
                    <button
                      type="button"
                      onClick={() => { setSearchQuery(''); setShowSuggestions(false); }}
                      className="absolute right-4 top-1/2 -translate-y-1/2 p-1 rounded-lg hover:bg-gray-100 text-gray-400"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </form>

              {/* Search suggestions dropdown */}
              <AnimatePresence>
                {showSuggestions && (
                  <motion.div
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -5 }}
                    className="absolute z-30 mt-2 w-full bg-white border border-gray-200 rounded-xl shadow-xl overflow-hidden"
                  >
                    {filteredSuggestions.map((s, i) => (
                      <button
                        key={i}
                        onClick={() => handleSuggestionClick(s.topic)}
                        className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-[#F8FAFC] transition-colors border-b border-gray-100 last:border-0"
                      >
                        <span className="text-lg">{s.icon}</span>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-[#1E293B] truncate">{s.topic}</p>
                          <p className="text-xs text-gray-400">{s.subject}</p>
                        </div>
                        <ChevronRight className="w-4 h-4 text-gray-300 flex-shrink-0" />
                      </button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Recent searches chips */}
              {recentSearches.length > 0 && !searchQuery && (
                <div className="flex items-center gap-2 mt-3 flex-wrap">
                  <Clock className="w-3.5 h-3.5 text-gray-400" />
                  {recentSearches.slice(0, 5).map((s, i) => (
                    <button
                      key={i}
                      onClick={() => handleTopicSelect(s)}
                      className="px-3 py-1 text-xs text-[#475569] bg-white border border-gray-200 rounded-full hover:bg-[#F8FAFC] hover:border-gray-300 transition-colors"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}
            </motion.div>

            <div className="grid lg:grid-cols-3 gap-6">
              {/* ── Main content (2/3) ── */}
              <div className="lg:col-span-2 space-y-6">

                {/* ── Popular WASSCE Topics ── */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                >
                  <div className="flex items-center gap-2 mb-4">
                    <TrendingUp className="w-4 h-4 text-[#2563EB]" />
                    <h2 className="text-sm font-bold uppercase tracking-wider text-gray-400">Popular WASSCE Topics</h2>
                  </div>
                  <div className="grid sm:grid-cols-2 gap-3">
                    {POPULAR_WASSCE_TOPICS.slice(0, 8).map((item, i) => (
                      <motion.button
                        key={i}
                        whileHover={{ scale: 1.01, y: -2 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => handleTopicSelect(item.topic)}
                        className="text-left bg-white border border-gray-200 rounded-xl p-4 hover:border-[#BFDBFE] hover:shadow-md transition-all group"
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-xl">{item.icon}</span>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-semibold text-[#1E293B] truncate group-hover:text-[#2563EB] transition-colors">
                              {item.topic}
                            </p>
                            <SubjectBadge subject={item.subject} />
                          </div>
                          <ChevronRight className="w-4 h-4 text-gray-300 group-hover:text-[#2563EB] transition-colors flex-shrink-0" />
                        </div>
                      </motion.button>
                    ))}
                  </div>
                </motion.div>

                {/* ── Continue Revising (History) ── */}
                {revisionHistory.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.15 }}
                  >
                    <div className="flex items-center gap-2 mb-4">
                      <History className="w-4 h-4 text-amber-500" />
                      <h2 className="text-sm font-bold uppercase tracking-wider text-gray-400">Continue Revising</h2>
                    </div>
                    <div className="flex gap-3 overflow-x-auto pb-2 -mx-2 px-2">
                      {revisionHistory.slice(0, 6).map((entry, i) => (
                        <motion.button
                          key={i}
                          whileHover={{ y: -2 }}
                          onClick={() => handleTopicSelect(entry.topic)}
                          className="flex-shrink-0 w-48 bg-white border border-gray-200 rounded-xl p-4 text-left hover:border-[#BFDBFE] hover:shadow-md transition-all"
                        >
                          <BookOpen className="w-5 h-5 text-[#2563EB] mb-2" />
                          <p className="text-sm font-semibold text-[#1E293B] truncate">{entry.topic}</p>
                          {entry.subject && <SubjectBadge subject={entry.subject} />}
                          <p className="text-xs text-gray-400 mt-2">
                            {new Date(entry.visitedAt).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}
                          </p>
                        </motion.button>
                      ))}
                    </div>
                  </motion.div>
                )}

                {/* ── All topics grid ── */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  <div className="flex items-center gap-2 mb-4">
                    <BookOpen className="w-4 h-5 text-green-500" />
                    <h2 className="text-sm font-bold uppercase tracking-wider text-gray-400">Browse All Topics</h2>
                  </div>
                  <div className="grid sm:grid-cols-2 gap-3">
                    {POPULAR_WASSCE_TOPICS.slice(8, 20).map((item, i) => (
                      <motion.button
                        key={i}
                        whileHover={{ scale: 1.01, y: -1 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => handleTopicSelect(item.topic)}
                        className="text-left bg-white border border-gray-200 rounded-xl p-3.5 hover:border-[#BFDBFE] hover:shadow-sm transition-all group"
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-lg">{item.icon}</span>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-semibold text-[#1E293B] truncate group-hover:text-[#2563EB] transition-colors">
                              {item.topic}
                            </p>
                            <p className="text-xs text-gray-400">{item.subject}</p>
                          </div>
                        </div>
                      </motion.button>
                    ))}
                  </div>
                </motion.div>
              </div>

              {/* ── Sidebar (1/3) ── */}
              <div className="space-y-6">

                {/* ── Bookmarks ── */}
                <motion.div
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.15 }}
                  className="bg-white border border-gray-200 rounded-xl p-5"
                >
                  <div className="flex items-center gap-2 mb-4">
                    <Bookmark className="w-4 h-4 text-amber-500" />
                    <h3 className="text-sm font-bold text-[#1E293B]">Bookmarks</h3>
                  </div>
                  {bookmarks.length === 0 ? (
                    <p className="text-xs text-gray-400">
                      Bookmark topics to quickly access them later.
                    </p>
                  ) : (
                    <div className="space-y-2">
                      {bookmarks.slice(0, 5).map((b, i) => (
                        <button
                          key={i}
                          onClick={() => handleTopicSelect(b.topic)}
                          className="w-full text-left flex items-center gap-2 px-3 py-2 text-sm text-[#475569] hover:text-[#2563EB] bg-[#F8FAFC] hover:bg-[#EFF6FF] rounded-lg transition-colors truncate"
                        >
                          <Bookmark className="w-3 h-3 text-amber-400 fill-current flex-shrink-0" />
                          <span className="truncate">{b.topic}</span>
                        </button>
                      ))}
                      {bookmarks.length > 5 && (
                        <p className="text-xs text-gray-400 text-center pt-1">
                          +{bookmarks.length - 5} more
                        </p>
                      )}
                    </div>
                  )}
                </motion.div>

                {/* ── Quick Stats ── */}
                <motion.div
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 }}
                  className="bg-white border border-gray-200 rounded-xl p-5"
                >
                  <div className="flex items-center gap-2 mb-4">
                    <Zap className="w-4 h-4 text-[#2563EB]" />
                    <h3 className="text-sm font-bold text-[#1E293B]">Your Stats</h3>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">Topics revised</span>
                      <span className="font-bold text-[#1E293B]">{revisionHistory.length}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">Bookmarked</span>
                      <span className="font-bold text-[#1E293B]">{bookmarks.length}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">Streak</span>
                      <span className="font-bold text-[#1E293B]">{user.streak || 0} days</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">XP</span>
                      <span className="font-bold text-[#2563EB]">{user.xp || 0}</span>
                    </div>
                  </div>
                </motion.div>

                {/* ── Revision Tips ── */}
                <motion.div
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.25 }}
                  className="bg-gradient-to-br from-[#EEF2FF] to-[#E0E7FF] border border-[#C7D2FE] rounded-xl p-5"
                >
                  <div className="flex items-center gap-2 mb-3">
                    <Lightbulb className="w-4 h-5 text-amber-500" />
                    <h3 className="text-sm font-bold text-[#1E293B]">WASSCE Tip</h3>
                  </div>
                  <p className="text-xs text-[#475569] leading-relaxed">
                    Focus on understanding concepts rather than memorising. Past questions are your best friend —
                    practice with them regularly!
                  </p>
                </motion.div>

              </div>
            </div>

          </div>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}

// ── Practice Question Card ──────────────────────────────────────────────────
function PracticeQuestionCard({ question, index }: { question: TopicContent['practice_questions'][0]; index: number }) {
  const [revealed, setRevealed] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);

  const handleSelect = (option: string) => {
    if (revealed) return;
    setSelected(option);
    setRevealed(true);
  };

  const isCorrect = selected === question.correct_answer;

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <div className="p-4">
        <p className="text-xs font-bold text-[#475569] mb-2">Question {index + 1}</p>
        <p className="text-sm text-[#1E293B] mb-4">{question.question}</p>
        <div className="space-y-2">
          {question.options.map((option, oi) => {
            const isSelected = selected === option;
            const isRightAnswer = option === question.correct_answer;
            let optionStyle = 'border-gray-200 hover:border-gray-300 bg-white';

            if (revealed) {
              if (isRightAnswer) {
                optionStyle = 'border-green-400 bg-green-50';
              } else if (isSelected && !isRightAnswer) {
                optionStyle = 'border-red-400 bg-red-50';
              } else {
                optionStyle = 'border-gray-100 bg-gray-50 opacity-60';
              }
            }

            return (
              <button
                key={oi}
                onClick={() => handleSelect(option)}
                className={`w-full text-left flex items-center gap-3 px-3 py-2.5 text-sm border rounded-lg transition-all ${optionStyle}`}
                disabled={revealed}
              >
                <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                  revealed && isRightAnswer
                    ? 'bg-green-500 text-white'
                    : revealed && isSelected && !isRightAnswer
                    ? 'bg-red-500 text-white'
                    : 'bg-gray-100 text-gray-500'
                }`}>
                  {String.fromCharCode(65 + oi)}
                </span>
                <span className="text-[#1E293B]">{option}</span>
              </button>
            );
          })}
        </div>
        {revealed && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className={`mt-4 p-3 rounded-lg text-sm ${isCorrect ? 'bg-green-50 border border-green-200' : 'bg-amber-50 border border-amber-200'}`}
          >
            <div className="flex items-start gap-2">
              {isCorrect ? (
                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
              ) : (
                <HelpCircle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
              )}
              <div>
                <p className="font-medium text-xs mb-1">
                  {isCorrect ? 'Correct!' : `The correct answer is ${question.correct_answer}`}
                </p>
                <p className="text-xs text-[#475569]">{question.explanation}</p>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
