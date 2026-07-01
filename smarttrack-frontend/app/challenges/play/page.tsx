'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import Sidebar from '../../components/Sidebar';
import BottomNav from '../../components/BottomNav';
import AppLayout from '../../components/AppLayout';
import { getAccessToken } from '../../lib/authApi';

// ── Types ──────────────────────────────────────────────────────────────────

interface Question {
  id: number;
  text: string;
  subject: string;
  options: string[];
  correctIndex: number;
}

interface LevelConfig {
  id: number;
  name: string;
  label: string;
  xpReward: number;
  color: string;
  bgColor: string;
}

// ── Level Definitions ──────────────────────────────────────────────────────

const LEVELS: LevelConfig[] = [
  { id: 1, name: 'Level 1', label: 'Core Skills', xpReward: 100, color: '#2563EB', bgColor: '#EFF6FF' },
  { id: 2, name: 'Level 2', label: 'Language & Society', xpReward: 150, color: '#7C3AED', bgColor: '#F5F3FF' },
  { id: 3, name: 'Level 3', label: 'Mastery', xpReward: 200, color: '#D97706', bgColor: '#FFFBEB' },
];

// ── Question Banks ─────────────────────────────────────────────────────────

const LEVEL_1_QUESTIONS: Question[] = [
  {
    id: 1, subject: 'Core Mathematics',
    text: 'If 3x + 7 = 22, what is the value of x?',
    options: ['3', '5', '7', '15'],
    correctIndex: 1,
  },
  {
    id: 2, subject: 'Integrated Science',
    text: 'Which of the following is the chemical symbol for sodium chloride?',
    options: ['NaCl', 'NaOH', 'H₂O', 'CO₂'],
    correctIndex: 0,
  },
  {
    id: 3, subject: 'Core Mathematics',
    text: 'What is the area of a rectangle with length 8 cm and width 5 cm?',
    options: ['13 cm²', '26 cm²', '40 cm²', '45 cm²'],
    correctIndex: 2,
  },
  {
    id: 4, subject: 'Integrated Science',
    text: 'The process by which plants make their own food using sunlight is called:',
    options: ['Respiration', 'Photosynthesis', 'Digestion', 'Fermentation'],
    correctIndex: 1,
  },
  {
    id: 5, subject: 'Core Mathematics',
    text: 'Simplify: 2(x + 3) - 4 = 8. What is x?',
    options: ['1', '2', '3', '4'],
    correctIndex: 2,
  },
];

const LEVEL_2_QUESTIONS: Question[] = [
  {
    id: 1, subject: 'English Language',
    text: 'Choose the correct word: The team ___ playing well today.',
    options: ['is', 'are', 'were', 'am'],
    correctIndex: 0,
  },
  {
    id: 2, subject: 'Social Studies',
    text: 'Which of the following is the highest mountain in Africa?',
    options: ['Mount Kenya', 'Mount Kilimanjaro', 'Mount Everest', 'Mount Atlas'],
    correctIndex: 1,
  },
  {
    id: 3, subject: 'English Language',
    text: 'What is the opposite of "generous"?',
    options: ['Kind', 'Stingy', 'Brave', 'Honest'],
    correctIndex: 1,
  },
  {
    id: 4, subject: 'Social Studies',
    text: 'Ghana gained independence from British colonial rule in which year?',
    options: ['1945', '1951', '1957', '1963'],
    correctIndex: 2,
  },
  {
    id: 5, subject: 'English Language',
    text: 'Identify the figure of speech: "The wind whispered through the trees."',
    options: ['Simile', 'Metaphor', 'Personification', 'Hyperbole'],
    correctIndex: 2,
  },
];

const LEVEL_3_QUESTIONS: Question[] = [
  {
    id: 1, subject: 'Core Mathematics',
    text: 'A student scored 18 out of 25 in a test. What is the percentage score?',
    options: ['62%', '68%', '72%', '80%'],
    correctIndex: 2,
  },
  {
    id: 2, subject: 'English Language',
    text: 'Which sentence uses the correct punctuation?',
    options: [
      'Where are you going?',
      'Where are you going.',
      'where are you going?',
      'Where are you Going?',
    ],
    correctIndex: 0,
  },
  {
    id: 3, subject: 'Integrated Science',
    text: 'What is the primary function of red blood cells?',
    options: [
      'Fight infection',
      'Carry oxygen',
      'Clot blood',
      'Produce hormones',
    ],
    correctIndex: 1,
  },
  {
    id: 4, subject: 'Social Studies',
    text: 'Which principle of democracy ensures that citizens have a say in how they are governed?',
    options: ['Rule of law', 'Separation of powers', 'Representation', 'Fundamental rights'],
    correctIndex: 2,
  },
  {
    id: 5, subject: 'Core Mathematics',
    text: 'Calculate the mean of the following numbers: 4, 8, 12, 16, 20.',
    options: ['10', '12', '14', '16'],
    correctIndex: 1,
  },
];

const LEVEL_QUESTIONS: Record<number, Question[]> = {
  1: LEVEL_1_QUESTIONS,
  2: LEVEL_2_QUESTIONS,
  3: LEVEL_3_QUESTIONS,
};

// ── Level Transition Screen ────────────────────────────────────────────────

function LevelCompleteScreen({
  level,
  xpEarned,
  onNext,
  isLast,
  onSeeResults,
}: {
  level: LevelConfig;
  xpEarned: number;
  onNext: () => void;
  isLast: boolean;
  onSeeResults?: () => void;
}) {
  const router = useRouter();

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="flex flex-col items-center justify-center py-16 px-6"
    >
      <div className="w-20 h-20 bg-gradient-to-br from-[#059669] to-[#34D399] rounded-2xl flex items-center justify-center mb-6 shadow-lg">
        <span className="text-4xl font-bold text-white">✓</span>
      </div>

      <h2 className="text-2xl font-bold text-[#1E293B] mb-2">{level.name} Complete!</h2>
      <p className="text-base text-[#475569] mb-6">You earned <span className="font-bold text-[#059669]">{xpEarned} XP</span></p>

      <div className="flex gap-3">
        <button
          onClick={() => router.push('/challenges/intro')}
          className="px-6 py-3 border-2 border-[#E2E8F0] text-[#475569] font-semibold rounded-xl hover:bg-[#F8FAFC] transition-all"
        >
          Exit
        </button>
        {!isLast && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onNext}
            className="inline-flex items-center gap-2 px-8 py-3.5 text-white font-bold rounded-xl hover:shadow-md transition-all"
            style={{ backgroundColor: level.color }}
          >
            Continue to Next Level
          </motion.button>
        )}
        {isLast && onSeeResults && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onSeeResults}
            className="inline-flex items-center gap-2 px-8 py-3.5 text-white font-bold rounded-xl hover:shadow-md transition-all"
            style={{ backgroundColor: '#059669' }}
          >
            See Results
          </motion.button>
        )}
      </div>
    </motion.div>
  );
}

// ── All Levels Complete ────────────────────────────────────────────────────

function AllCompleteScreen({ totalXp }: { totalXp: number }) {
  const router = useRouter();

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="flex flex-col items-center justify-center py-16 px-6"
    >
      <div className="w-24 h-24 bg-gradient-to-br from-[#F59E0B] to-[#D97706] rounded-2xl flex items-center justify-center mb-6 shadow-lg">
        <span className="text-4xl font-bold text-white">🏆</span>
      </div>

      <h2 className="text-3xl font-bold text-[#1E293B] mb-2">Today&apos;s Challenge Complete!</h2>
      <p className="text-base text-[#475569] mb-2">Amazing work! You have completed all three levels.</p>
      <p className="text-lg font-bold text-[#059669] mb-8">Total XP Earned: {totalXp}</p>

      <div className="flex gap-4">
        <button
          onClick={() => router.push('/dashboard')}
          className="px-6 py-3 bg-[#2563EB] text-white font-bold rounded-xl hover:bg-[#1D4ED8] transition-all shadow-md hover:shadow-lg"
        >
          Go to Dashboard
        </button>
        <button
          onClick={() => router.push('/challenges/leaderboard')}
          className="px-6 py-3 border-2 border-[#E2E8F0] text-[#475569] font-semibold rounded-xl hover:bg-[#F8FAFC] transition-all"
        >
          View Leaderboard
        </button>
      </div>
    </motion.div>
  );
}

// ── Main Challenge Play Component ──────────────────────────────────────────

function ChallengePlayContent() {
  const router = useRouter();

  // Challenge state
  const [currentLevelIndex, setCurrentLevelIndex] = useState(0);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, number | null>>({});
  const [levelComplete, setLevelComplete] = useState(false);
  const [allComplete, setAllComplete] = useState(false);
  const [totalXp, setTotalXp] = useState(0);
  const [currentLevelXp, setCurrentLevelXp] = useState(0);

  const currentLevel = LEVELS[currentLevelIndex];
  const questions = LEVEL_QUESTIONS[currentLevel.id];
  const currentQuestion = questions[currentQuestionIndex];

  const answerKey = `${currentLevel.id}-${currentQuestionIndex}`;
  const selectedAnswer = selectedAnswers[answerKey] ?? null;

  const allQuestionsAnswered = questions.every((_, idx) => {
    const key = `${currentLevel.id}-${idx}`;
    return selectedAnswers[key] !== undefined && selectedAnswers[key] !== null;
  });

  const handleSelect = (optionIndex: number) => {
    if (levelComplete || allComplete) return;
    setSelectedAnswers((prev) => ({ ...prev, [answerKey]: optionIndex }));
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex((prev) => prev + 1);
    }
  };

  const handlePrevQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex((prev) => prev - 1);
    }
  };

  const handleSubmitLevel = useCallback(() => {
    // Calculate XP for this level based on correct answers
    let correctCount = 0;
    questions.forEach((q, idx) => {
      const key = `${currentLevel.id}-${idx}`;
      if (selectedAnswers[key] === q.correctIndex) {
        correctCount++;
      }
    });
    const xpForLevel = Math.round((currentLevel.xpReward * correctCount) / questions.length);
    setCurrentLevelXp(xpForLevel);
    setTotalXp((prev) => prev + xpForLevel);
    setLevelComplete(true);
  }, [currentLevel, questions, selectedAnswers]);

  // If it's the last level, mark all complete after level complete
  useEffect(() => {
    if (levelComplete && currentLevelIndex >= LEVELS.length - 1) {
      const timer = setTimeout(() => {
        setAllComplete(true);
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [levelComplete, currentLevelIndex]);

  const handleNextLevel = () => {
    if (currentLevelIndex < LEVELS.length - 1) {
      setCurrentLevelIndex((prev) => prev + 1);
      setCurrentQuestionIndex(0);
      setLevelComplete(false);
    }
  };

  const progressPercent = currentLevelIndex * (100 / LEVELS.length) +
    (currentQuestionIndex / questions.length) * (100 / LEVELS.length);

  const answeredCount = questions.filter((_, idx) => {
    const key = `${currentLevel.id}-${idx}`;
    return selectedAnswers[key] !== undefined && selectedAnswers[key] !== null;
  }).length;

  if (allComplete) {
    return (
      <AppLayout>
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex-1 lg:pb-0 pb-24">
            <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10">
              <AllCompleteScreen totalXp={totalXp} />
            </main>
          </div>
          <BottomNav />
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-24">
          <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-8 pb-8">
            {/* Global progress */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mb-8"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {LEVELS.map((lvl, idx) => (
                    <div key={lvl.id} className="flex items-center gap-1">
                      <div
                        className={`w-2.5 h-2.5 rounded-full ${
                          idx < currentLevelIndex
                            ? 'bg-[#059669]'
                            : idx === currentLevelIndex
                              ? 'shadow-[0_0_6px_rgba(37,99,235,0.5)]'
                              : 'bg-[#E2E8F0]'
                        }`}
                        style={idx === currentLevelIndex ? { backgroundColor: currentLevel.color } : {}}
                      />
                      <span
                        className={`text-[10px] font-medium ${
                          idx <= currentLevelIndex ? 'text-[#1E293B]' : 'text-[#94A3B8]'
                        }`}
                      >
                        {lvl.name}
                      </span>
                      {idx < LEVELS.length - 1 && (
                        <div className={`w-4 h-px ${idx < currentLevelIndex ? 'bg-[#059669]' : 'bg-[#E2E8F0]'}`} />
                      )}
                    </div>
                  ))}
                </div>
                <span className="text-xs font-medium text-[#64748B]">
                  {answeredCount}/{questions.length} answered
                </span>
              </div>
              <div className="w-full h-2 bg-[#F1F5F9] rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${progressPercent}%`,
                    backgroundColor: currentLevel.color,
                  }}
                />
              </div>
            </motion.div>

            <AnimatePresence mode="wait">
              {levelComplete ? (
                <LevelCompleteScreen
                  key={`complete-${currentLevel.id}`}
                  level={currentLevel}
                  xpEarned={currentLevelXp}
                  onNext={handleNextLevel}
                  isLast={currentLevelIndex >= LEVELS.length - 1}
                  onSeeResults={() => setAllComplete(true)}
                />
              ) : (
                <motion.div
                  key={`level-${currentLevel.id}-q-${currentQuestionIndex}`}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.2 }}
                >
                  {/* Level header */}
                  <div className="mb-6">
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className="text-xs font-bold uppercase tracking-wider"
                        style={{ color: currentLevel.color }}
                      >
                        {currentLevel.name} — {currentLevel.label}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <h2 className="text-lg font-bold text-[#1E293B]">
                        {currentQuestion.subject}
                      </h2>
                      <div>
                        <span className="text-sm font-semibold text-[#1E293B]">
                          +{currentLevel.xpReward} XP
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Question card */}
                  <div className="bg-white border border-[#E2E8F0] rounded-2xl p-6 sm:p-8 mb-6">
                    {/* Subject tag */}
                    <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold mb-4"
                      style={{
                        backgroundColor: currentLevel.bgColor,
                        color: currentLevel.color,
                      }}
                    >
                      <span>{currentQuestion.subject}</span>
                    </div>

                    <p className="text-base sm:text-lg text-[#1E293B] leading-relaxed mb-6">
                      {currentQuestion.text}
                    </p>

                    <div className="space-y-3">
                      {currentQuestion.options.map((option, optIdx) => (
                        <button
                          key={optIdx}
                          onClick={() => handleSelect(optIdx)}
                          className={`w-full text-left px-5 py-4 rounded-xl border transition-all ${
                            selectedAnswer === optIdx
                              ? 'text-white'
                              : 'border-[#E2E8F0] hover:border-[#CBD5E1] hover:bg-[#F8FAFC] text-[#1E293B]'
                          }`}
                          style={
                            selectedAnswer === optIdx
                              ? { borderColor: currentLevel.color, backgroundColor: currentLevel.color }
                              : {}
                          }
                        >
                          <div className="flex items-center gap-3">
                            <span
                              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 ${
                                selectedAnswer === optIdx
                                  ? 'bg-white/20 text-white'
                                  : 'bg-[#F1F5F9] text-[#64748B]'
                              }`}
                            >
                              {String.fromCharCode(65 + optIdx)}
                            </span>
                            <span className="text-sm sm:text-base">{option}</span>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Exit button */}
                  <div className="flex justify-center mb-6">
                    <button
                      onClick={() => router.push('/challenges/intro')}
                      className="text-xs font-medium text-[#94A3B8] hover:text-[#64748B] transition-colors underline underline-offset-2"
                    >
                      Exit challenge (progress will not be saved)
                    </button>
                  </div>

                  {/* Navigation */}
                  <div className="flex items-center justify-between">
                    <button
                      onClick={handlePrevQuestion}
                      disabled={currentQuestionIndex === 0}
                      className="inline-flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium text-[#64748B] hover:text-[#1E293B] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                    >
                      Previous
                    </button>

                    <div className="flex items-center gap-2">
                      {/* Question dots */}
                      {questions.map((_, idx) => {
                        const key = `${currentLevel.id}-${idx}`;
                        const answered = selectedAnswers[key] !== undefined && selectedAnswers[key] !== null;
                        return (
                          <button
                            key={idx}
                            onClick={() => setCurrentQuestionIndex(idx)}
                            className={`w-7 h-7 rounded-lg text-[10px] font-bold transition-all ${
                              idx === currentQuestionIndex
                                ? 'text-white shadow-sm'
                                : answered
                                  ? 'text-white'
                                  : 'bg-[#F1F5F9] text-[#94A3B8] hover:bg-[#E2E8F0]'
                            }`}
                            style={
                              idx === currentQuestionIndex
                                ? { backgroundColor: currentLevel.color }
                                : answered
                                  ? { backgroundColor: currentLevel.color, opacity: 0.6 }
                                  : {}
                            }
                          >
                            {idx + 1}
                          </button>
                        );
                      })}
                    </div>

                    {currentQuestionIndex < questions.length - 1 ? (
                      <button
                        onClick={handleNextQuestion}
                        className="inline-flex items-center gap-1.5 px-5 py-2.5 text-sm font-semibold text-white rounded-xl hover:shadow-md transition-all"
                        style={{ backgroundColor: currentLevel.color }}
                      >
                        Next
                      </button>
                    ) : (
                      <button
                        onClick={handleSubmitLevel}
                        disabled={!allQuestionsAnswered}
                        className="inline-flex items-center gap-1.5 px-6 py-2.5 text-sm font-semibold text-white rounded-xl hover:shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        style={{ backgroundColor: currentLevel.color }}
                      >
                        Submit Level
                      </button>
                    )}
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

// ── Page Export ────────────────────────────────────────────────────────────

export default function ChallengePlayPage() {
  const router = useRouter();

  useEffect(() => {
    if (!getAccessToken()) {
      router.push('/login');
    }
  }, [router]);

  return <ChallengePlayContent />;
}
