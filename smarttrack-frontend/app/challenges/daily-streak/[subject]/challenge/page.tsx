'use client';

import { Suspense, useEffect, useState } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
import Sidebar from '../../../../components/Sidebar';
import BottomNav from '../../../../components/BottomNav';
import AppLayout from '../../../../components/AppLayout';
import { getSubjectById } from '../../data/subjects';
import { getAccessToken } from '../../../../lib/authApi';

const TOTAL_QUESTIONS = 10;

interface PlaceholderQuestion {
  id: number;
  text: string;
  options: string[];
}

function generatePlaceholderQuestions(_subjectName: string, _levelLabel: string): PlaceholderQuestion[] {
  return [];
}

function ChallengeContent() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const subjectId = params.subject as string;
  const subject = getSubjectById(subjectId as any);

  const levelName = searchParams.get('name') || 'Level 1';
  const levelLabel = searchParams.get('label') || 'Foundation';
  const xpReward = parseInt(searchParams.get('xp') || '100', 10);

  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<(number | null)[]>(new Array(TOTAL_QUESTIONS).fill(null));
  const [submitted, setSubmitted] = useState(false);

  const questions = generatePlaceholderQuestions(subject?.shortName || 'Subject', levelLabel);

  // Guard: if no questions, show empty state
  if (questions.length === 0) {
    return (
      <AppLayout>
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex-1 lg:pb-0 pb-24">
            <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center py-20"
              >
                <div className="w-16 h-16 bg-[#EEF2FF] rounded-2xl flex items-center justify-center mx-auto mb-4 border border-[#C7D2FE]">
                  <span className="text-2xl font-bold text-[#4F46E5]">!</span>
                </div>
                <h2 className="text-xl font-bold text-[#1E293B] mb-2">No Questions Available</h2>
                <p className="text-sm text-[#64748B] mb-6 max-w-sm mx-auto">
                  Challenge content is being prepared. Check back later or explore other areas of the app.
                </p>
                <div className="flex gap-3 justify-center">
                  <button
                    onClick={() => router.push('/dashboard')}
                    className="px-6 py-3 bg-[#2563EB] text-white font-semibold rounded-xl hover:bg-[#1D4ED8] transition-all"
                  >
                    Go to Dashboard
                  </button>
                  <button
                    onClick={() => router.back()}
                    className="px-6 py-3 border-2 border-[#E2E8F0] text-[#475569] font-semibold rounded-xl hover:bg-[#F8FAFC] transition-all"
                  >
                    Go Back
                  </button>
                </div>
              </motion.div>
            </main>
          </div>
          <BottomNav />
        </div>
      </AppLayout>
    );
  }

  const handleSelect = (questionIndex: number, optionIndex: number) => {
    if (submitted) return;
    const newAnswers = [...answers];
    newAnswers[questionIndex] = optionIndex;
    setAnswers(newAnswers);
  };

  const handleSubmit = () => {
    setSubmitted(true);
  };

  const answeredCount = answers.filter((a) => a !== null).length;

  const SUBJECT_ACCENT: Record<string, string> = {
    'core-mathematics': '#2563EB',
    'integrated-science': '#059669',
    'english-language': '#7C3AED',
    'social-studies': '#D97706',
  };
  const accentColor = SUBJECT_ACCENT[subjectId] || '#2563EB';

  if (!subject) {
    return (
      <AppLayout>
        <div className="flex min-h-screen items-center justify-center">
          <div className="text-center">
            <h2 className="text-xl font-bold text-[#1E293B] mb-2">Challenge Not Found</h2>
            <button onClick={() => router.push('/challenges/daily-streak')} className="text-[#2563EB] underline underline-offset-2">
              Back to Daily Streak
            </button>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-24">
          <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-8 pb-8">
            {/* Back button */}
            <motion.button
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              onClick={() => router.push(`/challenges/daily-streak/${subjectId}`)}
              className="inline-flex items-center gap-2 text-sm text-[#64748B] hover:text-[#1E293B] transition-colors mb-6"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to {subject.shortName}
            </motion.button>

            {/* Challenge header */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-bold text-[#1E293B]">
                    {levelName} — {levelLabel}
                  </h1>
                  <p className="text-base text-[#475569] mt-1">{subject.name}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs font-semibold text-[#64748B] uppercase tracking-wider">Reward</p>
                  <p className="text-xl font-bold" style={{ color: accentColor }}>{xpReward} XP</p>
                </div>
              </div>
            </motion.div>

            {/* Progress bar */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className="mb-8"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-[#64748B]">
                  Question {submitted ? TOTAL_QUESTIONS : Math.min(currentQuestion + 1, TOTAL_QUESTIONS)} of {TOTAL_QUESTIONS}
                </span>
                <span className="text-sm font-medium text-[#64748B]">
                  {answeredCount}/{TOTAL_QUESTIONS} answered
                </span>
              </div>
              <div className="w-full h-2.5 bg-[#F1F5F9] rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{ width: `${(answeredCount / TOTAL_QUESTIONS) * 100}%`, backgroundColor: accentColor }}
                />
              </div>
            </motion.div>

            {/* Question navigation dots */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.08 }}
              className="flex flex-wrap gap-2 mb-8"
            >
              {questions.map((q, idx) => (
                <button
                  key={q.id}
                  onClick={() => setCurrentQuestion(idx)}
                  className={`w-8 h-8 rounded-lg text-xs font-semibold transition-all ${
                    answers[idx] !== null
                      ? 'text-white'
                      : currentQuestion === idx
                        ? 'border-2'
                        : 'bg-[#F1F5F9] text-[#64748B] hover:bg-[#E2E8F0]'
                  }`}
                  style={
                    answers[idx] !== null
                      ? { backgroundColor: accentColor }
                      : currentQuestion === idx
                        ? { borderColor: accentColor, color: accentColor }
                        : {}
                  }
                >
                  {q.id}
                </button>
              ))}
            </motion.div>

            {/* Current question */}
            {!submitted ? (
              <motion.div
                key={currentQuestion}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.2 }}
              >
                <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 mb-6">
                  <p className="text-sm text-[#64748B] font-medium mb-3">Question {currentQuestion + 1}</p>
                  <p className="text-base text-[#1E293B] leading-relaxed mb-6">
                    {questions[currentQuestion].text}
                  </p>

                  <div className="space-y-3">
                    {questions[currentQuestion].options.map((option, optIdx) => (
                      <button
                        key={optIdx}
                        onClick={() => handleSelect(currentQuestion, optIdx)}
                        className={`w-full text-left px-5 py-3.5 rounded-xl border transition-all ${
                          answers[currentQuestion] === optIdx
                            ? 'border-2 text-white'
                            : 'border-[#E2E8F0] hover:border-[#CBD5E1] hover:bg-[#F8FAFC] text-[#1E293B]'
                        }`}
                        style={
                          answers[currentQuestion] === optIdx
                            ? { borderColor: accentColor, backgroundColor: accentColor }
                            : {}
                        }
                      >
                        <div className="flex items-center gap-3">
                          <span className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                            answers[currentQuestion] === optIdx
                              ? 'bg-white/20 text-white'
                              : 'bg-[#F1F5F9] text-[#64748B]'
                          }`}>
                            {String.fromCharCode(65 + optIdx)}
                          </span>
                          <span className="text-sm">{option}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Navigation buttons */}
                <div className="flex items-center justify-between">
                  <button
                    onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                    disabled={currentQuestion === 0}
                    className="px-5 py-2.5 text-sm font-medium text-[#64748B] hover:text-[#1E293B] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                  >
                    Previous
                  </button>

                  <div className="flex gap-3">
                    {currentQuestion < TOTAL_QUESTIONS - 1 ? (
                      <button
                        onClick={() => setCurrentQuestion(currentQuestion + 1)}
                        className="px-6 py-2.5 text-sm font-semibold text-white rounded-xl hover:shadow-md transition-all"
                        style={{ backgroundColor: accentColor }}
                      >
                        Next
                      </button>
                    ) : (
                      <button
                        onClick={handleSubmit}
                        disabled={answeredCount < TOTAL_QUESTIONS}
                        className="px-6 py-2.5 text-sm font-semibold text-white rounded-xl hover:shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        style={{ backgroundColor: accentColor }}
                      >
                        Submit Challenge
                      </button>
                    )}
                  </div>
                </div>
              </motion.div>
            ) : (
              /* Submitted state */
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-white border border-[#E2E8F0] rounded-2xl p-8 text-center"
              >
                <h2 className="text-xl font-bold text-[#1E293B] mb-2">Challenge Submitted</h2>
                <p className="text-sm text-[#475569] mb-6">
                  Your answers have been recorded. Results and XP will be available once the question bank is connected.
                </p>
                <div className="flex items-center justify-center gap-6 mb-6">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-[#1E293B]">{answeredCount}</p>
                    <p className="text-xs text-[#64748B]">Answered</p>
                  </div>
                  <div className="w-px h-10 bg-[#E2E8F0]" />
                  <div className="text-center">
                    <p className="text-2xl font-bold" style={{ color: accentColor }}>{xpReward} XP</p>
                    <p className="text-xs text-[#64748B]">Reward</p>
                  </div>
                </div>
                <div className="flex gap-3 justify-center">
                  <button
                    onClick={() => router.push(`/challenges/daily-streak/${subjectId}`)}
                    className="px-6 py-2.5 text-sm font-semibold rounded-xl border border-[#E2E8F0] text-[#64748B] hover:bg-[#F8FAFC] transition-all"
                  >
                    Back to Challenges
                  </button>
                  <button
                    onClick={() => router.push('/dashboard')}
                    className="px-6 py-2.5 text-sm font-semibold text-white rounded-xl hover:shadow-md transition-all"
                    style={{ backgroundColor: accentColor }}
                  >
                    Go to Dashboard
                  </button>
                </div>
              </motion.div>
            )}

            {/* Structure info note */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="mt-8 bg-[#EEF2FF] border border-[#C7D2FE] rounded-xl p-4"
            >
              <p className="text-xs text-[#475569]">
                This is a structural preview. Each daily challenge consists of {TOTAL_QUESTIONS} multiple-choice questions 
                with one correct answer. Live questions will be pulled from the question bank once connected.
              </p>
            </motion.div>
          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}

export default function ChallengePage() {
  const router = useRouter();

  useEffect(() => {
    if (!getAccessToken()) {
      router.push('/login');
    }
  }, [router]);

  return (
    <Suspense fallback={
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="w-8 h-8 border-2 border-[#4F46E5] border-t-transparent rounded-full animate-spin" />
        </div>
      </AppLayout>
    }>
      <ChallengeContent />
    </Suspense>
  );
}
