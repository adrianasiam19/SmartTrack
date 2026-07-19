'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import {
  AlertTriangle,
  ArrowLeft,
  BookOpen,
  Bookmark,
  BookmarkCheck,
  CheckCircle2,
  Lightbulb,
  Loader2,
  MessageCircle,
  RefreshCw,
  Send,
} from 'lucide-react';

import {
  askCurriculumTutor,
  getAITaughtLesson,
  getRelatedTopics,
  toggleLearningBookmark,
  type CurriculumTopic,
  type TaughtLessonResponse,
  type TutorMessage,
} from '../lib/learningApi';
import MarkdownRenderer from './MarkdownRenderer';

type TopicTab = 'overview' | 'notes' | 'examples' | 'practice' | 'ai' | 'related';

interface AITutorLessonProps {
  curriculumId: string;
  onBack: () => void;
  onComplete: (xpEarned: number) => void;
  onOpenRelated?: (curriculumId: string) => void;
  initiallyBookmarked?: boolean;
}

const TABS: { id: TopicTab; label: string }[] = [
  { id: 'overview', label: 'Overview' },
  { id: 'notes', label: 'Lesson Notes' },
  { id: 'examples', label: 'Worked Examples' },
  { id: 'practice', label: 'Practice' },
  { id: 'ai', label: 'Atlas AI' },
  { id: 'related', label: 'Related' },
];

const QUICK_QUESTIONS = [
  'Explain this topic in simple terms.',
  'Give me WASSCE-style examples.',
  'Test me on this topic.',
  'What are common examination mistakes?',
  'Summarize the key points.',
];

export default function AITutorLesson({
  curriculumId,
  onBack,
  onComplete,
  onOpenRelated,
  initiallyBookmarked = false,
}: AITutorLessonProps) {
  const [tab, setTab] = useState<TopicTab>('overview');
  const [data, setData] = useState<TaughtLessonResponse | null>(null);
  const [lessonError, setLessonError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);
  const [messages, setMessages] = useState<TutorMessage[]>([]);
  const [input, setInput] = useState('');
  const [asking, setAsking] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [bookmarked, setBookmarked] = useState(initiallyBookmarked);
  const [bookmarkBusy, setBookmarkBusy] = useState(false);
  const [related, setRelated] = useState<CurriculumTopic[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const controller = new AbortController();
    setData(null);
    setLessonError(null);
    setTab('overview');
    getAITaughtLesson(curriculumId, controller.signal)
      .then(setData)
      .catch((error) => {
        if (error instanceof Error && error.name !== 'AbortError') {
          setLessonError(error.message);
        }
      });
    getRelatedTopics(curriculumId, controller.signal)
      .then(setRelated)
      .catch(() => setRelated([]));
    return () => controller.abort();
  }, [curriculumId, reloadKey]);

  useEffect(() => {
    setMessages([]);
    setInput('');
    setCompleted(false);
    setBookmarked(initiallyBookmarked);
  }, [curriculumId, initiallyBookmarked]);

  useEffect(() => {
    if (typeof messagesEndRef.current?.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, asking]);

  const askTutor = useCallback(async (question: string) => {
    const trimmed = question.trim();
    if (!trimmed || asking) return;
    const userMessage: TutorMessage = { role: 'user', content: trimmed };
    const history = messages;
    setMessages((previous) => [...previous, userMessage]);
    setInput('');
    setAsking(true);
    setTab('ai');
    try {
      const response = await askCurriculumTutor(curriculumId, trimmed, history);
      setMessages((previous) => [
        ...previous,
        { role: 'assistant', content: response },
      ]);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: 'assistant',
          content: error instanceof Error
            ? error.message
            : 'Atlas AI could not answer right now. Please try again.',
        },
      ]);
    } finally {
      setAsking(false);
    }
  }, [asking, curriculumId, messages]);

  const completeLesson = () => {
    if (!data || completed) return;
    setCompleted(true);
    onComplete(data.xp_reward);
  };

  const onToggleBookmark = async () => {
    if (bookmarkBusy) return;
    setBookmarkBusy(true);
    try {
      const res = await toggleLearningBookmark(curriculumId);
      setBookmarked(res.bookmarked);
    } catch {
      // keep prior state
    } finally {
      setBookmarkBusy(false);
    }
  };

  if (lessonError) {
    return (
      <div className="max-w-xl mx-auto">
        <button onClick={onBack} className="flex items-center gap-2 text-sm text-gray-500 hover:text-[#1E293B] mb-5">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        <div className="bg-white border border-red-200 rounded-2xl p-8 text-center">
          <AlertTriangle className="w-9 h-9 text-red-500 mx-auto mb-3" />
          <h2 className="font-bold text-[#1E293B] mb-2">Atlas AI could not prepare this lesson</h2>
          <p className="text-sm text-gray-500 mb-5">
            {/lesson not found/i.test(lessonError)
              ? 'This topic is missing from the curriculum catalogue. Go back and pick another topic, or refresh Learning Center.'
              : lessonError}
          </p>
          <button
            onClick={() => setReloadKey((value) => value + 1)}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#4F46E5] text-white text-sm font-semibold"
          >
            <RefreshCw className="w-4 h-4" /> Try again
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="max-w-xl mx-auto min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <div className="w-14 h-14 rounded-2xl bg-[#EEF2FF] flex items-center justify-center mx-auto mb-4">
            <BookOpen className="w-7 h-7 text-[#4F46E5] animate-pulse" />
          </div>
          <h2 className="font-bold text-[#1E293B] mb-1">Atlas AI is preparing your lesson</h2>
          <p className="text-sm text-gray-500">Reading the curriculum and building a clear explanation…</p>
          <Loader2 className="w-5 h-5 text-[#4F46E5] animate-spin mx-auto mt-4" />
        </div>
      </div>
    );
  }

  const lesson = data.lesson;

  return (
    <div className="max-w-3xl mx-auto pb-28">
      <div className="flex items-center justify-between gap-3 mb-5">
        <button onClick={onBack} className="flex items-center gap-2 text-sm text-gray-500 hover:text-[#1E293B]">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{data.estimated_minutes} min</span>
          <button
            type="button"
            onClick={() => void onToggleBookmark()}
            disabled={bookmarkBusy}
            className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 bg-white px-2.5 py-1.5 text-xs font-medium text-[#1E293B] hover:border-[#4F46E5] hover:text-[#4F46E5] disabled:opacity-50"
          >
            {bookmarked ? (
              <BookmarkCheck className="w-3.5 h-3.5 text-[#4F46E5]" />
            ) : (
              <Bookmark className="w-3.5 h-3.5" />
            )}
            {bookmarked ? 'Saved' : 'Save'}
          </button>
        </div>
      </div>

      <header className="bg-[#1E293B] text-white rounded-2xl p-7 sm:p-9 mb-5">
        <p className="text-xs font-bold tracking-widest uppercase text-indigo-300 mb-3">{data.subject}</p>
        <h1 className="text-2xl sm:text-3xl font-bold leading-tight">{lesson.topic_title}</h1>
        <p className="mt-4 text-slate-300 leading-relaxed">{lesson.simple_introduction}</p>
      </header>

      <div className="flex gap-1 overflow-x-auto mb-5 pb-1 border-b border-gray-200">
        {TABS.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setTab(item.id)}
            className={`flex-shrink-0 px-3 py-2 text-sm font-medium rounded-t-lg transition-colors ${
              tab === item.id
                ? 'text-[#4F46E5] border-b-2 border-[#4F46E5]'
                : 'text-gray-500 hover:text-[#1E293B]'
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>

      {tab === 'overview' ? (
        <div className="space-y-5">
          <Panel title="Overview">
            <p className="text-gray-600 leading-relaxed">{lesson.simple_introduction}</p>
            <p className="mt-4 text-gray-600 leading-relaxed">{lesson.short_summary}</p>
          </Panel>
          {lesson.important_points.length > 0 ? (
            <Panel title="Key points" icon={<Lightbulb className="w-4 h-4" />}>
              <BulletList items={lesson.important_points} />
            </Panel>
          ) : null}
        </div>
      ) : null}

      {tab === 'notes' ? (
        <Panel title="Lesson Notes">
          <MarkdownRenderer content={lesson.main_explanation} />
          {lesson.real_life_applications.length > 0 ? (
            <div className="mt-6 pt-6 border-t border-gray-100">
              <h3 className="font-semibold text-[#1E293B] mb-3">Real-life applications</h3>
              <BulletList items={lesson.real_life_applications} />
            </div>
          ) : null}
          {lesson.common_mistakes.length > 0 ? (
            <div className="mt-6 pt-6 border-t border-gray-100">
              <h3 className="font-semibold text-[#1E293B] mb-3">Common mistakes</h3>
              <BulletList items={lesson.common_mistakes} tone="warning" />
            </div>
          ) : null}
        </Panel>
      ) : null}

      {tab === 'examples' ? (
        <Panel title="Worked Examples">
          {lesson.step_by_step_examples.length === 0 ? (
            <p className="text-sm text-gray-500">No worked examples for this topic yet. Ask Atlas AI for one.</p>
          ) : (
            <div className="space-y-4">
              {lesson.step_by_step_examples.map((example, index) => (
                <div key={`${example.title}-${index}`} className="rounded-xl bg-gray-50 border border-gray-100 p-5">
                  <h3 className="font-semibold text-[#1E293B] mb-3">{example.title}</h3>
                  <ol className="space-y-2">
                    {example.steps.map((step, stepIndex) => (
                      <li key={stepIndex} className="flex gap-3 text-sm text-gray-600">
                        <span className="w-6 h-6 rounded-full bg-[#EEF2FF] text-[#4F46E5] flex items-center justify-center text-xs font-bold flex-shrink-0">
                          {stepIndex + 1}
                        </span>
                        <span className="pt-0.5">{step}</span>
                      </li>
                    ))}
                  </ol>
                  {example.answer ? (
                    <p className="mt-3 pt-3 border-t border-gray-200 text-sm font-semibold text-[#4F46E5]">
                      Answer: {example.answer}
                    </p>
                  ) : null}
                </div>
              ))}
            </div>
          )}
        </Panel>
      ) : null}

      {tab === 'practice' ? (
        <Panel title="Practice Questions">
          <p className="text-sm text-gray-500 mb-4">
            Ask Atlas AI to generate practice questions on this topic.
          </p>
          <div className="flex flex-wrap gap-2">
            {[
              'Test me on this topic with 5 multiple-choice questions.',
              'Give me 3 short-answer practice questions.',
              'What are common examination mistakes?',
            ].map((prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() => void askTutor(prompt)}
                disabled={asking}
                className="px-3 py-2 rounded-lg border border-gray-200 bg-white hover:border-[#4F46E5] hover:text-[#4F46E5] text-xs text-gray-600 transition-colors"
              >
                {prompt}
              </button>
            ))}
          </div>
          {messages.length > 0 ? (
            <p className="mt-4 text-xs text-[#4F46E5]">
              Answers appear in the Atlas AI tab.
            </p>
          ) : null}
        </Panel>
      ) : null}

      {tab === 'ai' ? (
        <section className="bg-white border border-[#C7D2FE] rounded-2xl overflow-hidden mb-5">
          <div className="px-5 sm:px-6 py-5 bg-[#EEF2FF] border-b border-[#C7D2FE]">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 bg-[#4F46E5] rounded-xl flex items-center justify-center text-white">
                <MessageCircle className="w-5 h-5" />
              </div>
              <div>
                <h2 className="font-bold text-[#1E293B]">Atlas AI</h2>
                <p className="text-xs text-gray-500">Need clarity? Ask Atlas AI anything about this topic.</p>
              </div>
            </div>
          </div>

          <div className="p-5 sm:p-6">
            {messages.length === 0 ? (
              <div className="flex flex-wrap gap-2 mb-5">
                {QUICK_QUESTIONS.map((question) => (
                  <button
                    key={question}
                    type="button"
                    onClick={() => void askTutor(question)}
                    disabled={asking}
                    className="px-3 py-2 rounded-lg border border-gray-200 bg-white hover:border-[#4F46E5] hover:text-[#4F46E5] text-xs text-gray-600 transition-colors"
                  >
                    {question}
                  </button>
                ))}
              </div>
            ) : null}

            {messages.length > 0 ? (
              <div className="max-h-96 overflow-y-auto space-y-3 mb-4 pr-1">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`rounded-xl px-4 py-3 text-sm ${
                      message.role === 'user'
                        ? 'ml-8 bg-[#4F46E5] text-white'
                        : 'mr-8 bg-gray-50 border border-gray-100 text-[#1E293B]'
                    }`}
                  >
                    {message.role === 'assistant'
                      ? <MarkdownRenderer content={message.content} compact />
                      : message.content}
                  </div>
                ))}
                {asking ? (
                  <div className="mr-8 bg-gray-50 border border-gray-100 rounded-xl px-4 py-3 flex items-center gap-2 text-sm text-gray-500">
                    <Loader2 className="w-4 h-4 animate-spin text-[#4F46E5]" /> Atlas AI is thinking…
                  </div>
                ) : null}
                <div ref={messagesEndRef} />
              </div>
            ) : null}

            <AskComposer
              input={input}
              setInput={setInput}
              asking={asking}
              onAsk={askTutor}
              placeholder="Ask for a simpler explanation, another example, or a quiz…"
            />
          </div>
        </section>
      ) : null}

      {tab === 'related' ? (
        <Panel title="Related Topics">
          {related.length === 0 ? (
            <p className="text-sm text-gray-500">No related topics found yet.</p>
          ) : (
            <div className="space-y-2">
              {related.map((topic) => (
                <button
                  key={topic.curriculum_id}
                  type="button"
                  onClick={() => onOpenRelated?.(topic.curriculum_id)}
                  className="w-full text-left rounded-xl border border-gray-200 bg-white px-4 py-3 hover:border-[#4F46E5]/40 transition-colors"
                >
                  <p className="font-medium text-[#1E293B] text-sm">{topic.title}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{topic.subject}</p>
                </button>
              ))}
            </div>
          )}
        </Panel>
      ) : null}

      <button
        type="button"
        onClick={completeLesson}
        disabled={completed}
        className="w-full py-3.5 rounded-xl bg-[#4F46E5] hover:bg-[#4338CA] text-white font-semibold transition-colors disabled:bg-emerald-600 flex items-center justify-center gap-2 mb-5"
      >
        {completed ? (
          <>
            <CheckCircle2 className="w-4 h-4" />
            Lesson complete · +{data.xp_reward} XP
          </>
        ) : (
          'Complete Lesson'
        )}
      </button>

      {tab !== 'ai' ? (
        <div className="fixed bottom-16 left-0 right-0 z-30 px-4 pointer-events-none sm:bottom-4">
          <div className="max-w-3xl mx-auto pointer-events-auto rounded-2xl border border-[#C7D2FE] bg-white/95 backdrop-blur shadow-lg p-3">
            <p className="text-xs font-medium text-[#4F46E5] mb-2 px-1">
              Need clarity? Ask Atlas AI about this lesson
            </p>
            <AskComposer
              input={input}
              setInput={setInput}
              asking={asking}
              onAsk={askTutor}
              placeholder="e.g. Explain this in simpler terms…"
            />
          </div>
        </div>
      ) : null}
    </div>
  );
}

function AskComposer({
  input,
  setInput,
  asking,
  onAsk,
  placeholder,
}: {
  input: string;
  setInput: (value: string) => void;
  asking: boolean;
  onAsk: (question: string) => void | Promise<void>;
  placeholder: string;
}) {
  return (
    <div className="flex items-end gap-2 border border-gray-200 rounded-xl p-2 focus-within:border-[#4F46E5] bg-white">
      <textarea
        value={input}
        onChange={(event) => setInput(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            void onAsk(input);
          }
        }}
        rows={2}
        maxLength={2000}
        placeholder={placeholder}
        className="flex-1 resize-none bg-transparent px-2 py-1 text-sm text-[#1E293B] outline-none placeholder:text-gray-400"
        disabled={asking}
      />
      <button
        type="button"
        onClick={() => void onAsk(input)}
        disabled={!input.trim() || asking}
        className="p-2.5 rounded-lg bg-[#4F46E5] text-white disabled:opacity-40"
        aria-label="Send question"
      >
        {asking ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
      </button>
    </div>
  );
}

function Panel({
  title,
  icon,
  children,
}: {
  title: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <section className="bg-white border border-gray-200 rounded-2xl p-5 sm:p-7 mb-5">
      <div className="flex items-center gap-3 mb-5">
        <span className="w-8 h-8 rounded-lg bg-[#EEF2FF] text-[#4F46E5] flex items-center justify-center text-xs font-bold">
          {icon || title.charAt(0)}
        </span>
        <h2 className="font-bold text-lg text-[#1E293B]">{title}</h2>
      </div>
      {children}
    </section>
  );
}

function BulletList({ items, tone = 'default' }: { items: string[]; tone?: 'default' | 'warning' }) {
  return (
    <ul className="space-y-3">
      {items.map((item, index) => (
        <li key={index} className="flex gap-3 text-sm text-gray-600 leading-relaxed">
          <span className={`mt-2 w-1.5 h-1.5 rounded-full flex-shrink-0 ${tone === 'warning' ? 'bg-amber-500' : 'bg-[#4F46E5]'}`} />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}
