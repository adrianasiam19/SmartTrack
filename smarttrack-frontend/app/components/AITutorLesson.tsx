'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import {
  AlertTriangle,
  ArrowLeft,
  Brain,
  CheckCircle2,
  Lightbulb,
  Loader2,
  MapPin,
  RefreshCw,
  Send,
} from 'lucide-react';

import {
  askCurriculumTutor,
  getAITaughtLesson,
  type TaughtLessonResponse,
  type TutorMessage,
} from '../lib/learningApi';
import MarkdownRenderer from './MarkdownRenderer';

interface AITutorLessonProps {
  curriculumId: string;
  onBack: () => void;
  onComplete: (xpEarned: number) => void;
}

const QUICK_QUESTIONS = [
  'Explain this in simpler terms.',
  'Give me another example.',
  'Give me practice questions.',
  'Summarize this topic.',
  'What should I remember for WASSCE?',
  "Explain this like I'm a beginner.",
];

export default function AITutorLesson({
  curriculumId,
  onBack,
  onComplete,
}: AITutorLessonProps) {
  const [data, setData] = useState<TaughtLessonResponse | null>(null);
  const [lessonError, setLessonError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);
  const [messages, setMessages] = useState<TutorMessage[]>([]);
  const [input, setInput] = useState('');
  const [asking, setAsking] = useState(false);
  const [completed, setCompleted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const controller = new AbortController();
    setData(null);
    setLessonError(null);
    getAITaughtLesson(curriculumId, controller.signal)
      .then(setData)
      .catch((error) => {
        if (error instanceof Error && error.name !== 'AbortError') {
          setLessonError(error.message);
        }
      });
    return () => controller.abort();
  }, [curriculumId, reloadKey]);

  useEffect(() => {
    setMessages([]);
    setInput('');
    setCompleted(false);
  }, [curriculumId]);

  useEffect(() => {
    if (typeof messagesEndRef.current?.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, asking]);

  const askAtlas = useCallback(async (question: string) => {
    const trimmed = question.trim();
    if (!trimmed || asking) return;
    const userMessage: TutorMessage = { role: 'user', content: trimmed };
    const history = messages;
    setMessages((previous) => [...previous, userMessage]);
    setInput('');
    setAsking(true);
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

  if (lessonError) {
    return (
      <div className="max-w-xl mx-auto">
        <button onClick={onBack} className="flex items-center gap-2 text-sm text-gray-500 hover:text-[#1E293B] mb-5">
          <ArrowLeft className="w-4 h-4" /> Back to lessons
        </button>
        <div className="bg-white border border-red-200 rounded-2xl p-8 text-center">
          <AlertTriangle className="w-9 h-9 text-red-500 mx-auto mb-3" />
          <h2 className="font-bold text-[#1E293B] mb-2">Atlas could not prepare this lesson</h2>
          <p className="text-sm text-gray-500 mb-5">{lessonError}</p>
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
            <Brain className="w-7 h-7 text-[#4F46E5] animate-pulse" />
          </div>
          <h2 className="font-bold text-[#1E293B] mb-1">Atlas AI is preparing your lesson</h2>
          <p className="text-sm text-gray-500">Reading your official curriculum and turning it into a clear explanation…</p>
          <Loader2 className="w-5 h-5 text-[#4F46E5] animate-spin mx-auto mt-4" />
        </div>
      </div>
    );
  }

  const lesson = data.lesson;

  return (
    <div className="max-w-3xl mx-auto pb-10">
      <div className="flex items-center justify-between gap-3 mb-5">
        <button onClick={onBack} className="flex items-center gap-2 text-sm text-gray-500 hover:text-[#1E293B]">
          <ArrowLeft className="w-4 h-4" /> Back to lessons
        </button>
        <div className="flex items-center gap-2">
          <span className="px-2.5 py-1 rounded-lg bg-[#EEF2FF] text-[#4F46E5] text-xs font-bold">{data.shs_level}</span>
          <span className="text-xs text-gray-400">{data.estimated_minutes} min</span>
        </div>
      </div>

      <header className="bg-[#1E293B] text-white rounded-2xl p-7 sm:p-9 mb-5">
        <p className="text-xs font-bold tracking-widest uppercase text-indigo-300 mb-3">{data.subject}</p>
        <h1 className="text-2xl sm:text-3xl font-bold leading-tight">{lesson.topic_title}</h1>
        <p className="mt-4 text-slate-300 leading-relaxed">{lesson.simple_introduction}</p>
      </header>

      <LessonSection number="1" title="Main Explanation">
        <MarkdownRenderer content={lesson.main_explanation} />
      </LessonSection>

      <LessonSection number="2" title="Step-by-Step Examples">
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
              {example.answer && (
                <p className="mt-3 pt-3 border-t border-gray-200 text-sm font-semibold text-[#4F46E5]">
                  Answer: {example.answer}
                </p>
              )}
            </div>
          ))}
        </div>
      </LessonSection>

      {lesson.real_life_applications.length > 0 && (
        <LessonSection number="3" title="Real-Life Applications" icon={<MapPin className="w-4 h-4" />}>
          <BulletList items={lesson.real_life_applications} />
        </LessonSection>
      )}

      <LessonSection number="4" title="Important Points to Remember" icon={<Lightbulb className="w-4 h-4" />}>
        <BulletList items={lesson.important_points} />
      </LessonSection>

      <LessonSection number="5" title="Common Mistakes Students Make" icon={<AlertTriangle className="w-4 h-4" />}>
        <BulletList items={lesson.common_mistakes} tone="warning" />
      </LessonSection>

      <LessonSection number="6" title="Short Summary" icon={<CheckCircle2 className="w-4 h-4" />}>
        <p className="text-gray-600 leading-relaxed">{lesson.short_summary}</p>
      </LessonSection>

      <section className="bg-white border border-[#C7D2FE] rounded-2xl overflow-hidden mb-5">
        <div className="px-5 sm:px-6 py-5 bg-[#EEF2FF] border-b border-[#C7D2FE]">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-[#4F46E5] rounded-xl flex items-center justify-center text-white font-bold text-sm">A</div>
            <div>
              <h2 className="font-bold text-[#1E293B]">Ask Atlas AI</h2>
              <p className="text-xs text-gray-500">Ask anything about this lesson. Atlas stays within your curriculum.</p>
            </div>
          </div>
        </div>

        <div className="p-5 sm:p-6">
          {messages.length === 0 && (
            <div className="flex flex-wrap gap-2 mb-5">
              {QUICK_QUESTIONS.map((question) => (
                <button
                  key={question}
                  onClick={() => askAtlas(question)}
                  disabled={asking}
                  className="px-3 py-2 rounded-lg border border-gray-200 bg-white hover:border-[#4F46E5] hover:text-[#4F46E5] text-xs text-gray-600 transition-colors"
                >
                  {question}
                </button>
              ))}
            </div>
          )}

          {messages.length > 0 && (
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
              {asking && (
                <div className="mr-8 bg-gray-50 border border-gray-100 rounded-xl px-4 py-3 flex items-center gap-2 text-sm text-gray-500">
                  <Loader2 className="w-4 h-4 animate-spin text-[#4F46E5]" /> Atlas is thinking…
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}

          <div className="flex items-end gap-2 border border-gray-200 rounded-xl p-2 focus-within:border-[#4F46E5]">
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                  event.preventDefault();
                  askAtlas(input);
                }
              }}
              rows={2}
              maxLength={2000}
              placeholder="Ask for a simpler explanation, another example, or practice questions…"
              className="flex-1 resize-none bg-transparent px-2 py-1 text-sm text-[#1E293B] outline-none placeholder:text-gray-400"
              disabled={asking}
            />
            <button
              onClick={() => askAtlas(input)}
              disabled={!input.trim() || asking}
              className="p-2.5 rounded-lg bg-[#4F46E5] text-white disabled:opacity-40"
              aria-label="Send question"
            >
              {asking ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </section>

      <button
        onClick={completeLesson}
        disabled={completed}
        className="w-full py-3.5 rounded-xl bg-[#4F46E5] hover:bg-[#4338CA] text-white font-semibold transition-colors disabled:bg-emerald-600"
      >
        {completed ? `Lesson complete · +${data.xp_reward} XP` : 'Complete Lesson'}
      </button>
    </div>
  );
}

function LessonSection({
  number,
  title,
  icon,
  children,
}: {
  number: string;
  title: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <section className="bg-white border border-gray-200 rounded-2xl p-5 sm:p-7 mb-5">
      <div className="flex items-center gap-3 mb-5">
        <span className="w-8 h-8 rounded-lg bg-[#EEF2FF] text-[#4F46E5] flex items-center justify-center text-xs font-bold">
          {icon || number}
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
