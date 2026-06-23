'use client';

import { Suspense, useState, useEffect, useRef, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import Sidebar from '../../components/Sidebar';
import BottomNav from '../../components/BottomNav';
import AppLayout from '../../components/AppLayout';
import XPAnimation from '../../components/XPAnimation';
import FillBlankExercise from '../../components/FillBlankExercise';
import MatchExercise from '../../components/MatchExercise';
import PredictChallenge from '../../components/PredictChallenge';
import PsychometricPrompt from '../../components/PsychometricPrompt';
import {
  getAccessToken,
  getStoredUser,
  getCurrentUser,
  storeUser,
  type UserProfile,
} from '../../lib/authApi';
import {
  startCalibration,
  fetchNextQuestions,
  submitAnswer,
  submitBehaviourData,
  fetchPsychometricCard,
  type Question,
  type QuestionType,
} from '../../lib/challengesApi';
import { getRandomLogicQuestions } from '../../lib/logicArenaData';
import { getRandomQuantQuestions } from '../../lib/quantArenaData';
import { getRandomScientificQuestions } from '../../lib/scientificArenaData';
import {
  getRandomStarterQuestions,
  type StarterQuestion,
} from '../../lib/starterArenaData';

type ArenaPhase = 'intro' | 'gameplay' | 'feedback' | 'psychometric' | 'loading_more' | 'complete';

interface GameSession {
  xpEarned: number;
  streak: number;
  questionsAnswered: number;
  correctAnswers: number;
  totalTime: number;
  startTime: number;
}

function starterToQuestion(sq: StarterQuestion): Question {
  const idNum = parseInt(sq.id.replace('SA-', ''), 10);
  return {
    id: 1000 + idNum,
    domain: sq.domain,
    question: sq.question,
    question_type: sq.interaction,
    options: sq.options || {},
    answer_hash: btoa(`ST_SEC_2024:${sq.correctKey || 'A'}`),
    _category: sq.domain,
    _explanation: sq.explanation,
    _answers: sq.answers,
    _hints: sq.hints,
    _pattern: sq.pattern,
    _leftItems: sq.leftItems,
    _rightItems: sq.rightItems,
    _correctMatches: sq.correctMatches,
    _rankedOrder: sq.rankedOrder,
    _allowMultiple: sq.allowMultiple,
    _xp: 0,
  };
}

function shuffleArray<T>(arr: T[]): T[] {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function shuffledOptionKeys(options: Record<string, string>): string[] {
  const keys = Object.keys(options);
  return shuffleArray([...keys]);
}

export function ChallengeArena() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const domain = searchParams.get('domain');
  const category = searchParams.get('category');
  const mode = searchParams.get('mode');

  const isPlacement = mode === 'placement';

  const [phase, setPhase] = useState<ArenaPhase>('intro');
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [questionQueue, setQuestionQueue] = useState<Question[]>([]);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);

  const usedIdsRef = useRef<Set<number>>(new Set());

  const [shuffledKeys, setShuffledKeys] = useState<string[]>([]);

  const [session, setSession] = useState<GameSession>({
    xpEarned: 0,
    streak: 0,
    questionsAnswered: 0,
    correctAnswers: 0,
    totalTime: 0,
    startTime: Date.now(),
  });
  const [questionStartTime, setQuestionStartTime] = useState<number>(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [lastXP, setLastXP] = useState(0);
  const [lastStreak, setLastStreak] = useState(0);
  const [levelUp, setLevelUp] = useState(false);
  const [newRank, setNewRank] = useState<string | null>(null);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [shsLevel, setSHSLevel] = useState<string | null>(null);

  useEffect(() => {
    if (user?.shs_level) setSHSLevel(user.shs_level);
  }, [user]);

  const [timeLeft, setTimeLeft] = useState(30);

  const PSYCHOMETRIC_EVERY_N = 3;
  const [prefetchedPsychCard, setPrefetchedPsychCard] = useState<Awaited<ReturnType<typeof fetchPsychometricCard>>>(null);
  const psychometricInProgressRef = useRef(false);
  const psychometricCompletedRef = useRef(false);

  const retriesRef = useRef(0);
  const responseTimesRef = useRef<number[]>([]);
  const bgFetchRef = useRef(false);

  useEffect(() => {
    if (isPlacement && phase === 'complete') {
      const timer = setTimeout(() => {
        router.push('/onboarding?phase=analysis');
      }, 800);
      return () => clearTimeout(timer);
    }
  }, [isPlacement, phase, router]);

  const MAX_QUESTIONS = isPlacement ? 12 : 10;
  const QUESTION_TIMEOUT = isPlacement ? 45 : 30;

  const decryptAnswer = (hash: string): string => {
    try {
      const decoded = atob(hash);
      return decoded.split(':')[1];
    } catch {
      return '';
    }
  };

  useEffect(() => {
    const loadUser = async () => {
      try {
        const cached = getStoredUser();
        if (cached) setUser(cached);
        if (!getAccessToken()) { router.push('/login'); return; }
        const fresh = await getCurrentUser();
        setUser(fresh);
      } catch { router.push('/login'); }
    };
    loadUser();
  }, [router]);

  const isLogicArena = category === 'logic-arena';
  const isScientificArena = category === 'scientific-thinking';
  const isQuantArena = category === 'quantitative-sprint' || category === 'advanced-quantitative' || category === 'problem-solving';

  const fetchMoreQuestions = useCallback(async (): Promise<Question[] | null> => {
    if (isPlacement) return null;
    if (isLogicArena) {
      const nextBatch = getRandomLogicQuestions(10).filter(
        (q) => !usedIdsRef.current.has(q.id)
      );
      nextBatch.forEach((q) => usedIdsRef.current.add(q.id));
      return nextBatch.length > 0 ? nextBatch : null;
    }
    if (isQuantArena) {
      const nextBatch = getRandomQuantQuestions(10).filter(
        (q) => !usedIdsRef.current.has(q.id)
      );
      nextBatch.forEach((q) => usedIdsRef.current.add(q.id));
      return nextBatch.length > 0 ? nextBatch : null;
    }
    if (isScientificArena) {
      const nextBatch = getRandomScientificQuestions(10).filter(
        (q) => !usedIdsRef.current.has(q.id)
      );
      nextBatch.forEach((q) => usedIdsRef.current.add(q.id));
      return nextBatch.length > 0 ? nextBatch : null;
    }
    try {
      return await fetchNextQuestions(domain || undefined, shsLevel || undefined);
    } catch {
      return null;
    }
  }, [domain, shsLevel, isLogicArena, isScientificArena, isQuantArena, isPlacement]);

  const startChallenge = async () => {
    try {
      setLoading(true);
      setError(null);
      setTimeLeft(QUESTION_TIMEOUT);
      usedIdsRef.current = new Set();

      let initialQuestions: Question[] = [];

      if (isPlacement) {
        const raw = getRandomStarterQuestions(MAX_QUESTIONS);
        initialQuestions = raw.map(starterToQuestion);
      } else if (isLogicArena) {
        initialQuestions = getRandomLogicQuestions(MAX_QUESTIONS);
      } else if (isQuantArena) {
        initialQuestions = getRandomQuantQuestions(MAX_QUESTIONS);
      } else if (isScientificArena) {
        initialQuestions = getRandomScientificQuestions(MAX_QUESTIONS);
      } else {
        const data = await startCalibration(domain || undefined, shsLevel || undefined);
        initialQuestions = data.questions || [];
      }

      if (initialQuestions.length > 0) {
        initialQuestions.forEach((q: Question) => usedIdsRef.current.add(q.id));

        setCurrentQuestion(initialQuestions[0]);
        setQuestionQueue(initialQuestions.slice(1));
        setShuffledKeys(shuffledOptionKeys(initialQuestions[0].options));
        setPhase('gameplay');
        setQuestionStartTime(Date.now());
        setSession((prev) => ({ ...prev, startTime: Date.now() }));
        setTimeLeft(QUESTION_TIMEOUT);
      } else {
        throw new Error('No questions returned');
      }
    } catch (e: any) {
      setError(e?.message || 'Failed to start.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async (answerKey: string) => {
    if (!currentQuestion || loading) return;
    setSelectedAnswer(answerKey);
    setLoading(true);

    const timeTaken = Math.max(0, (Date.now() - questionStartTime) / 1000);
    responseTimesRef.current.push(timeTaken);

    const localCorrect = decryptAnswer(currentQuestion.answer_hash);
    const isPreference = currentQuestion.question_type === 'discover';
    const localIsCorrect = isPreference ? true : answerKey === localCorrect;

    setIsCorrect(localIsCorrect);
    setPhase('feedback');

    if (isPlacement) {
      setLastXP(0);
      setLastStreak(0);
      setLevelUp(false);
      setNewRank(null);

      const countsTowardAccuracy = !isPreference;

      setSession((prev) => ({
        ...prev,
        questionsAnswered: prev.questionsAnswered + 1,
        correctAnswers: prev.correctAnswers + (countsTowardAccuracy && localIsCorrect ? 1 : 0),
        totalTime: prev.totalTime + timeTaken,
      }));
    } else {
      let apiSuccess = false;
      try {
        const data = await submitAnswer({
          question_id: currentQuestion.id,
          selected_option: answerKey,
          time_taken_seconds: timeTaken,
          hints_used: 0,
          is_correct: localIsCorrect,
        });

        setLastXP(data.xp_gained || (localIsCorrect ? 15 : 5));
        setLastStreak(data.streak_updated || session.streak + (localIsCorrect ? 1 : 0));
        setLevelUp(data.level_up || false);
        setNewRank(data.new_rank || null);

        setSession((prev) => ({
          ...prev,
          xpEarned: prev.xpEarned + (data.xp_gained || (localIsCorrect ? 15 : 5)),
          streak: data.streak_updated || (localIsCorrect ? prev.streak + 1 : 0),
          questionsAnswered: prev.questionsAnswered + 1,
          correctAnswers: prev.correctAnswers + (localIsCorrect ? 1 : 0),
          totalTime: prev.totalTime + timeTaken,
        }));

        if (user) {
          const updated = {
            ...user,
            xp: user.xp + (data.xp_gained || (localIsCorrect ? 15 : 5)),
            streak: data.streak_updated || (localIsCorrect ? user.streak + 1 : 0),
            rank: data.new_rank || user.rank,
          };
          storeUser(updated);
          setUser(updated);
        }

        if (data.next_questions?.length > 0) {
          const fresh = data.next_questions.filter(
            (q: Question) => !usedIdsRef.current.has(q.id)
          );
          fresh.forEach((q: Question) => usedIdsRef.current.add(q.id));
          setQuestionQueue((prev) => [...prev, ...fresh]);
        }

        apiSuccess = true;
      } catch {
        console.warn('Backend submit failed, using local XP only');
      }

      if (!apiSuccess) {
        const baseXP = localIsCorrect ? 15 : 5;
        const streakBonus = localIsCorrect ? (session.streak + 1) * 2 : 0;
        const earnedXP = baseXP + streakBonus;

        setLastXP(earnedXP);
        setLastStreak(localIsCorrect ? session.streak + 1 : 0);

        setSession((prev) => ({
          ...prev,
          xpEarned: prev.xpEarned + earnedXP,
          streak: localIsCorrect ? prev.streak + 1 : 0,
          questionsAnswered: prev.questionsAnswered + 1,
          correctAnswers: prev.correctAnswers + (localIsCorrect ? 1 : 0),
          totalTime: prev.totalTime + timeTaken,
        }));

        if (user) {
          const updated = {
            ...user,
            xp: user.xp + earnedXP,
            streak: localIsCorrect ? user.streak + 1 : 0,
          };
          storeUser(updated);
          setUser(updated);
        }
      }
    }

    const interactiveTypes = ['fill-blank', 'predict', 'match'];
    const isInteractive = interactiveTypes.includes(currentQuestion.question_type || 'mcq');

    setLoading(false);
    const newCount = session.questionsAnswered + 1;
    const isLastQuestion = newCount >= MAX_QUESTIONS;

    const willShowPsychometric = !isLastQuestion && isPlacement && newCount % PSYCHOMETRIC_EVERY_N === 0 && !psychometricInProgressRef.current;
    if (willShowPsychometric) {
      psychometricInProgressRef.current = true;
      psychometricCompletedRef.current = false;
      fetchPsychometricCard()
        .then((data) => {
          if (data && !psychometricCompletedRef.current) {
            setPrefetchedPsychCard(data);
          }
        })
        .catch(() => {
          psychometricInProgressRef.current = false;
        });
    }

    const handleAdvance = () => {
      if (isLastQuestion) {
        const avgTime = responseTimesRef.current.length > 0
          ? responseTimesRef.current.reduce((a, b) => a + b, 0) / responseTimesRef.current.length
          : 0;
        const consistency = Math.round((session.correctAnswers / session.questionsAnswered) * 100);
        submitBehaviourData({
          retries: retriesRef.current,
          response_time_avg: Math.round(avgTime * 10) / 10,
          response_times: responseTimesRef.current,
          questions_answered: newCount,
          correct_answers: session.correctAnswers,
          consistency,
          domain: domain || undefined,
        });
        setPhase('complete');
      } else if (isPlacement && newCount % PSYCHOMETRIC_EVERY_N === 0) {
        setPhase('psychometric');
      } else {
        advanceToNextQuestion();
      }
    };

    if (isInteractive) {
      setTimeout(handleAdvance, 400);
    } else {
      setTimeout(handleAdvance, isPlacement ? 1800 : 2200);
    }
  };

  useEffect(() => {
    if (isPlacement || (!isLogicArena && !isScientificArena && !isQuantArena)) return;
    if (phase !== 'gameplay') return;
    const queueLen = questionQueue.length;
    if (queueLen < 3) {
      const refill = isLogicArena
        ? getRandomLogicQuestions(5).filter((q) => !usedIdsRef.current.has(q.id))
        : isScientificArena
        ? getRandomScientificQuestions(5).filter((q) => !usedIdsRef.current.has(q.id))
        : getRandomQuantQuestions(5).filter((q) => !usedIdsRef.current.has(q.id));
      refill.forEach((q) => usedIdsRef.current.add(q.id));
      if (refill.length > 0) {
        setQuestionQueue((prev) => [...prev, ...refill]);
      }
    }
  }, [phase, isLogicArena, isQuantArena, isPlacement, questionQueue.length]);

  const advanceToNextQuestion = () => {
    setQuestionQueue((prev) => {
      const next = [...prev];
      const nextQ = next.shift();
      if (nextQ) {
        setCurrentQuestion(nextQ);
        setSelectedAnswer(null);
        setIsCorrect(null);
        setTimeLeft(QUESTION_TIMEOUT);
        setQuestionStartTime(Date.now());
        setShuffledKeys(shuffledOptionKeys(nextQ.options));
        bgFetchRef.current = false;
        setPhase('gameplay');
      } else {
        setPhase('loading_more');
      }
      return next;
    });
  };

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (phase === 'gameplay' && timeLeft > 0) {
      timer = setInterval(() => setTimeLeft((p) => p - 1), 1000);
    } else if (timeLeft === 0 && phase === 'gameplay') {
      handleSubmitAnswer(selectedAnswer || 'timeout');
    }
    return () => clearInterval(timer);
  }, [phase, timeLeft]);

  useEffect(() => {
    if (isPlacement) return;
    if (isScientificArena) return;
    if (phase === 'gameplay' && currentQuestion && !bgFetchRef.current) {
      bgFetchRef.current = true;
      fetchMoreQuestions().then((qs: Question[] | null) => {
        bgFetchRef.current = false;
        if (qs?.length) {
          const fresh = qs.filter((q: Question) => !usedIdsRef.current.has(q.id));
          fresh.forEach((q: Question) => usedIdsRef.current.add(q.id));
          if (fresh.length) {
            setQuestionQueue((prev) => [...prev, ...fresh]);
          }
        }
      });
    }
  }, [phase, currentQuestion?.id, fetchMoreQuestions, isPlacement]);

  const handlePsychometricComplete = () => {
    psychometricCompletedRef.current = true;
    setPrefetchedPsychCard(null);
    setTimeout(() => advanceToNextQuestion(), 400);
  };

  const handlePsychometricSkip = () => {
    psychometricCompletedRef.current = true;
    setPrefetchedPsychCard(null);
    setTimeout(() => advanceToNextQuestion(), 200);
  };

  const handleRetry = () => {
    setError(null);
    setPhase('intro');
    setSession({
      xpEarned: 0,
      streak: 0,
      questionsAnswered: 0,
      correctAnswers: 0,
      totalTime: 0,
      startTime: Date.now(),
    });
    setQuestionQueue([]);
    setCurrentQuestion(null);
    setShuffledKeys([]);
    usedIdsRef.current = new Set();
    retriesRef.current = 0;
    responseTimesRef.current = [];
    psychometricInProgressRef.current = false;
    psychometricCompletedRef.current = false;
  };

  const timerPercent = (timeLeft / QUESTION_TIMEOUT) * 100;
  const timerColour = timeLeft <= 5 ? 'bg-red-500' : timeLeft <= 10 ? 'bg-[#D97706]' : 'bg-[#4F46E5]';

  const domainName = category
    ? category.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
    : domain || 'Discovery';

  const modeLabel = isPlacement ? 'Starter Arena' : domainName;

  const psychometricCount = Math.min(
    Math.floor(MAX_QUESTIONS / PSYCHOMETRIC_EVERY_N),
    MAX_QUESTIONS
  );

  const renderMcqOptions = (options: Record<string, string>, questionType?: QuestionType) => {
    if (questionType === 'discover') {
      return (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {shuffledKeys.map((key) => (
            <button
              key={key}
              onClick={() => handleSubmitAnswer(key)}
              disabled={loading || selectedAnswer !== null}
              className={`p-5 rounded-xl border transition-all duration-200 text-left ${
                selectedAnswer === key
                  ? 'border-[#4F46E5] bg-[#EEF2FF] shadow-sm'
                  : 'border-gray-200 hover:border-gray-300 bg-white hover:bg-gray-50'
              } disabled:opacity-70 disabled:cursor-not-allowed`}
            >
              <span className="text-[#1E293B] text-sm leading-relaxed">{options[key]}</span>
            </button>
          ))}
        </div>
      );
    }

    return (
      <div className="space-y-3">
        {shuffledKeys.map((key) => (
          <button
            key={key}
            onClick={() => handleSubmitAnswer(key)}
            disabled={loading || selectedAnswer !== null}
            className={`w-full text-left px-6 py-4 rounded-xl border transition-all duration-200 ${
              selectedAnswer === key
                ? 'border-[#4F46E5] bg-[#EEF2FF] shadow-sm'
                : 'border-gray-200 hover:border-gray-300 bg-white hover:bg-gray-50'
            } disabled:opacity-70 disabled:cursor-not-allowed`}
          >
            <div className="flex items-center gap-4">
              <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all ${
                selectedAnswer === key
                  ? 'border-[#4F46E5] bg-[#4F46E5]'
                  : 'border-gray-300'
              }`}>
                {selectedAnswer === key && (
                  <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </div>
              <div>
                <span className="text-sm font-medium text-gray-400 mr-3">{key}. </span>
                <span className="text-[#1E293B]">{options[key]}</span>
              </div>
            </div>
          </button>
        ))}
      </div>
    );
  };

  const renderFillBlank = () => {
    if (!currentQuestion?._answers) return null;
    return (
      <FillBlankExercise
        template={currentQuestion.question}
        answers={currentQuestion._answers}
        hints={currentQuestion._hints || []}
        explanation={currentQuestion._explanation || 'Great job!'}
        onComplete={(correct) => {
          const correctKey = correct ? 'A' : 'B';
          handleSubmitAnswer(correctKey);
        }}
        onRequestHint={() => {}}
      />
    );
  };

  const renderPredict = () => {
    if (!currentQuestion?.options) return null;
    const opts = shuffledKeys.map((k) => currentQuestion!.options![k]);
    return (
      <PredictChallenge
        pattern={currentQuestion._pattern || ''}
        question={currentQuestion.question}
        options={opts}
        correctIndex={shuffledKeys.indexOf(decryptAnswer(currentQuestion.answer_hash))}
        explanation={currentQuestion._explanation || ''}
        onComplete={(correct) => {
          const correctKey = correct ? 'A' : 'B';
          handleSubmitAnswer(correctKey);
        }}
      />
    );
  };

  const renderMatch = () => {
    if (!currentQuestion?._leftItems || !currentQuestion?._rightItems || !currentQuestion?._correctMatches) return null;
    return (
      <MatchExercise
        instruction={currentQuestion.question}
        leftItems={currentQuestion._leftItems}
        rightItems={currentQuestion._rightItems}
        correctMatches={currentQuestion._correctMatches}
        explanation={currentQuestion._explanation || ''}
        onComplete={(correct) => {
          const correctKey = correct ? 'A' : 'B';
          handleSubmitAnswer(correctKey);
        }}
      />
    );
  };

  const renderIntro = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white border border-gray-200 rounded-2xl p-12 text-center max-w-lg mx-auto shadow-sm"
    >
      <div className="mb-6 flex justify-center">
        <div className="w-20 h-20 bg-[#EEF2FF] rounded-full border-2 border-[#C7D2FE] flex items-center justify-center">
          <span className="text-3xl font-bold text-[#4F46E5]">{isPlacement ? '?' : 'A'}</span>
        </div>
      </div>

      {isPlacement ? (
        <>
          <h1 className="text-3xl font-bold text-[#1E293B] mb-3">Hey there!</h1>
          <p className="text-gray-500 mb-2 max-w-sm mx-auto leading-relaxed">
            I&apos;m Atlas — let&apos;s discover your strengths together!
          </p>
          <p className="text-gray-400 text-sm mb-8 max-w-xs mx-auto leading-relaxed">
            We&apos;ll explore some fun challenges and activities. There are no wrong answers — just discoveries!
          </p>
        </>
      ) : (
        <>
          <h1 className="text-3xl font-bold text-[#1E293B] mb-4">{modeLabel}</h1>
          <p className="text-gray-500 mb-8 max-w-sm mx-auto leading-relaxed">
            Test your {domainName.toLowerCase()} skills with adaptive questions.
          </p>
        </>
      )}

      {!isPlacement && session.questionsAnswered > 0 && (
        <div className="grid grid-cols-3 gap-3 mb-8">
          <div className="bg-gray-50 rounded-xl p-3">
            <p className="text-xs text-gray-500">XP Earned</p>
            <p className="text-lg font-bold text-[#4F46E5]">+{session.xpEarned}</p>
          </div>
          <div className="bg-gray-50 rounded-xl p-3">
            <p className="text-xs text-gray-500">Streak</p>
            <p className="text-lg font-bold text-[#D97706]">{session.streak}</p>
          </div>
          <div className="bg-gray-50 rounded-xl p-3">
            <p className="text-xs text-gray-500">Accuracy</p>
            <p className="text-lg font-bold text-[#1E293B]">
              {session.questionsAnswered > 0
                ? Math.round((session.correctAnswers / session.questionsAnswered) * 100)
                : 0}%
            </p>
          </div>
        </div>
      )}

      <button
        onClick={startChallenge}
        disabled={loading}
        className="px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed bg-[#4F46E5] text-white hover:bg-[#4338CA] shadow-sm"
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Loading...
          </span>
        ) : (
          <span>{session.questionsAnswered > 0 ? 'Continue' : isPlacement ? 'Start Discovery' : 'Begin Challenge'}</span>
        )}
      </button>
      <p className="text-xs text-gray-400 mt-4">
        {MAX_QUESTIONS} activities
        {!isPlacement && ` \u00B7 ${QUESTION_TIMEOUT}s each`}
        {isPlacement && psychometricCount > 0 && ` \u00B7 ${psychometricCount} insight moments`}
      </p>
    </motion.div>
  );

  const renderGameplay = () => {
    if (!currentQuestion) return null;
    const options = currentQuestion.options || {};
    const questionType = currentQuestion.question_type || 'mcq';
    const explanation = currentQuestion._explanation;

    return (
      <motion.div
        key={currentQuestion.id}
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -50 }}
        className="bg-white border border-gray-200 rounded-2xl p-8 max-w-2xl mx-auto shadow-sm"
      >
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            {isPlacement ? (
              <span className="text-sm text-gray-500">Discovery</span>
            ) : (
              <span className="text-sm font-semibold text-[#4F46E5]">+{session.xpEarned} XP</span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">
              {session.questionsAnswered + 1}/{MAX_QUESTIONS}
            </span>
          </div>
        </div>

        <div className="w-full bg-gray-100 rounded-full h-1.5 mb-5">
          <motion.div
            className="h-1.5 rounded-full bg-[#4F46E5]"
            initial={{ width: 0 }}
            animate={{ width: `${(session.questionsAnswered / MAX_QUESTIONS) * 100}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>

        {!isPlacement && (
          <div className="mb-5">
            <div className="flex items-center justify-between mb-1">
              <span className={`text-xs font-mono ${timeLeft <= 5 ? 'text-red-500' : 'text-gray-400'}`}>
                {timeLeft}s
              </span>
            </div>
            <div className={`w-full bg-gray-100 rounded-full h-1 transition-all ${timeLeft <= 5 ? 'animate-pulse' : ''}`}>
              <motion.div
                className={`h-1 rounded-full ${timerColour}`}
                animate={{ width: `${timerPercent}%` }}
                transition={{ duration: 1 }}
              />
            </div>
          </div>
        )}

        <span className={`inline-block px-3 py-1 text-xs font-medium rounded-full border mb-4 bg-[#EEF2FF] text-[#4F46E5] border-[#C7D2FE]`}>
          {currentQuestion.domain}
        </span>

        {isPlacement && questionType !== 'mcq' && (
          <span className="inline-block px-3 py-1 text-xs font-medium bg-[#FFFBEB] text-[#D97706] rounded-full border border-[#FDE68A] mb-4 ml-2">
            {questionType === 'fill-blank' && 'Fill in'}
            {questionType === 'predict' && 'Pattern'}
            {questionType === 'match' && 'Match'}
            {questionType === 'discover' && 'Discover'}
          </span>
        )}

        {questionType === 'fill-blank' ? (
          <>
            <p className="text-sm text-gray-500 mb-3">{currentQuestion.question}</p>
            {renderFillBlank()}
          </>
        ) : questionType === 'predict' ? (
          renderPredict()
        ) : questionType === 'match' ? (
          renderMatch()
        ) : questionType === 'discover' ? (
          <>
            <h2 className="text-xl font-semibold text-[#1E293B] mb-6 leading-relaxed">
              {currentQuestion.question}
            </h2>
            {renderMcqOptions(options, 'discover')}
          </>
        ) : (
          <>
            <h2 className="text-xl font-semibold text-[#1E293B] mb-8 leading-relaxed">
              {currentQuestion.question}
            </h2>
            {renderMcqOptions(options, 'mcq')}
          </>
        )}

        {selectedAnswer && isCorrect !== null && questionType === 'mcq' && explanation && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`mt-6 p-4 rounded-xl border ${
              isCorrect ? 'bg-[#EEF2FF] border-[#C7D2FE]' : 'bg-[#FFFBEB] border-[#FDE68A]'
            }`}
          >
            <p className={`text-sm font-medium mb-1 ${isCorrect ? 'text-[#4F46E5]' : 'text-[#D97706]'}`}>
              {isCorrect ? (isPlacement ? 'Nice!' : 'Correct!') : (isPlacement ? 'Interesting!' : 'Not quite!')}
            </p>
            <p className="text-gray-500 text-sm leading-relaxed">{explanation}</p>
          </motion.div>
        )}
      </motion.div>
    );
  };

  const renderFeedback = () => {
    if (isPlacement) {
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-lg mx-auto"
        >
          <div className="bg-white border border-gray-200 rounded-2xl p-8 text-center shadow-sm">
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className={`text-lg font-semibold ${isCorrect ? 'text-[#4F46E5]' : 'text-[#D97706]'}`}
            >
              {isCorrect ? 'Great thinking!' : 'Thanks for exploring!'}
            </motion.p>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="text-gray-400 text-sm mt-1"
            >
              {isCorrect
                ? 'Atlas is learning about your strengths!'
                : 'Every answer helps Atlas understand you better!'}
            </motion.p>
          </div>
        </motion.div>
      );
    }

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-lg mx-auto"
      >
        <div className="bg-white border border-gray-200 rounded-2xl p-8 shadow-sm">
          <XPAnimation
            xpGained={lastXP}
            streak={lastStreak}
            levelUp={levelUp}
            newRank={newRank}
            isCorrect={isCorrect || false}
          />
        </div>
      </motion.div>
    );
  };

  const renderPsychometric = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="max-w-lg mx-auto"
    >
      <PsychometricPrompt
        onComplete={handlePsychometricComplete}
        onSkip={handlePsychometricSkip}
        preloadedCard={prefetchedPsychCard}
      />
    </motion.div>
  );

  const renderLoadingMore = () => (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-white border border-gray-200 rounded-2xl p-12 text-center max-w-lg mx-auto shadow-sm"
    >
      <div className="flex flex-col items-center gap-5">
        <div className="w-16 h-16 border-4 border-[#C7D2FE] border-t-[#4F46E5] rounded-full animate-spin" />
        <div>
          <h3 className="text-xl font-semibold text-[#1E293B] mb-2">
            {isPlacement ? 'Preparing your next discovery...' : 'Generating Challenge'}
          </h3>
          <p className="text-gray-400 text-sm max-w-xs mx-auto">
            {isPlacement
              ? 'Atlas is picking something interesting for you!'
              : 'AI is crafting adaptive questions tailored to your skill level...'}
          </p>
        </div>
      </div>
    </motion.div>
  );

  const renderComplete = () => {
    const accuracy = session.questionsAnswered > 0
      ? Math.round((session.correctAnswers / session.questionsAnswered) * 100)
      : 0;

    if (isPlacement) {
      return (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-lg mx-auto"
        >
          <div className="bg-white border border-gray-200 rounded-2xl p-10 text-center shadow-sm">
            <div className="mb-6 flex justify-center">
              <div className="w-20 h-20 bg-[#EEF2FF] rounded-full border-2 border-[#C7D2FE] flex items-center justify-center">
                <span className="text-3xl font-bold text-[#4F46E5]">A</span>
              </div>
            </div>

            <h1 className="text-3xl font-bold text-[#1E293B] mb-2">Discovery Complete!</h1>
            <p className="text-gray-500 mb-4 max-w-sm mx-auto leading-relaxed">
              Atlas now understands your strengths and interests better.
            </p>

            <div className="flex items-center justify-center gap-3 text-gray-400 text-sm">
              <div className="w-5 h-5 border-2 border-[#C7D2FE] border-t-[#4F46E5] rounded-full animate-spin" />
              <span>Building your profile...</span>
            </div>
          </div>
        </motion.div>
      );
    }

    // COMPETITIVE ARENA COMPLETE
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-lg mx-auto"
      >
        <div className="bg-white border border-gray-200 rounded-2xl p-10 text-center shadow-sm">
          <div className="mb-6 flex justify-center">
            <div className="w-20 h-20 bg-[#EEF2FF] rounded-full border-2 border-[#C7D2FE] flex items-center justify-center">
              <span className="text-3xl font-bold text-[#4F46E5]">A</span>
            </div>
          </div>

          <h1 className="text-3xl font-bold text-[#1E293B] mb-2">Challenge Complete!</h1>
          <p className="text-gray-400 mb-8">Here&apos;s how you performed:</p>

          <div className="grid grid-cols-2 gap-4 mb-8">
            <div className="bg-[#EEF2FF] rounded-xl p-4 border border-[#C7D2FE]">
              <p className="text-2xl font-black text-[#4F46E5]">+{session.xpEarned}</p>
              <p className="text-xs text-gray-500">XP Earned</p>
            </div>
            <div className="bg-[#FFFBEB] rounded-xl p-4 border border-[#FDE68A]">
              <p className="text-2xl font-black text-[#D97706]">{session.streak}</p>
              <p className="text-xs text-gray-500">Day Streak</p>
            </div>
            <div className="bg-[#EEF2FF] rounded-xl p-4 border border-[#C7D2FE]">
              <p className="text-2xl font-black text-[#4F46E5]">{session.correctAnswers}/{session.questionsAnswered}</p>
              <p className="text-xs text-gray-500">Correct</p>
            </div>
            <div className="bg-[#FFF1F2] rounded-xl p-4 border border-[#FFE4E6]">
              <p className="text-2xl font-black text-[#F43F5E]">{accuracy}%</p>
              <p className="text-xs text-gray-500">Accuracy</p>
            </div>
          </div>

          {levelUp && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-[#FFFBEB] border border-[#FDE68A] rounded-xl p-4 mb-8"
            >
              <p className="text-[#D97706] font-bold text-lg">LEVEL UP!</p>
              {newRank && <p className="text-[#D97706] text-sm mt-1">New Rank: {newRank}</p>}
            </motion.div>
          )}

          <div className="flex flex-col gap-3">
            <button onClick={handleRetry}
              className="w-full py-3 bg-[#4F46E5] text-white rounded-xl font-semibold hover:bg-[#4338CA] transition-all">
              Play Again
            </button>
            <button onClick={() => router.push('/challenges')}
              className="w-full py-3 border border-gray-200 text-gray-500 rounded-xl hover:bg-gray-50 transition-all">
              Back to Challenge Hub
            </button>
            <button onClick={() => router.push('/challenges/leaderboard')}
              className="w-full py-3 border border-gray-200 text-gray-400 rounded-xl hover:bg-gray-50 transition-all text-sm">
              View Leaderboard
            </button>
          </div>
        </div>
      </motion.div>
    );
  };

  const renderError = () => (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-white border border-red-200 rounded-2xl p-8 text-center max-w-lg mx-auto shadow-sm"
    >
      <h3 className="text-xl font-semibold text-[#1E293B] mb-2">Something went wrong</h3>
      <p className="text-gray-500 mb-6">{error}</p>
      <div className="flex gap-3 justify-center">
        <button onClick={handleRetry}
          className="px-6 py-3 bg-[#4F46E5] text-white rounded-xl font-semibold hover:bg-[#4338CA] transition-all">
          Try Again
        </button>
        <button onClick={() => router.push('/challenges')}
          className="px-6 py-3 border border-gray-200 text-gray-500 rounded-xl hover:bg-gray-50 transition-all">
          Back to Hub
        </button>
      </div>
    </motion.div>
  );

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-20">
          <main className="flex-1 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-8 pb-8">
            <div className="flex items-center gap-4 mb-6">
              <button onClick={() => router.push('/challenges')}
                className="flex items-center gap-2 text-gray-400 hover:text-[#1E293B] transition-colors">
                <span className="text-sm font-medium hidden sm:inline">Back</span>
              </button>
              <div>
                <h1 className="text-xl font-bold text-[#1E293B]">{modeLabel}</h1>
                <p className="text-xs text-gray-500">
                  {session.questionsAnswered > 0
                    ? isPlacement
                      ? `${session.questionsAnswered} activities completed`
                      : `${session.questionsAnswered} completed \u00B7 ${session.xpEarned} XP earned`
                    : isPlacement
                    ? 'Let Atlas get to know you!'
                    : 'Get ready to challenge yourself!'}
                </p>
              </div>
            </div>
            <AnimatePresence mode="wait">
              {error ? (
                renderError()
              ) : phase === 'intro' ? (
                renderIntro()
              ) : phase === 'gameplay' ? (
                renderGameplay()
              ) : phase === 'feedback' ? (
                renderFeedback()
              ) : phase === 'psychometric' ? (
                renderPsychometric()
              ) : phase === 'loading_more' ? (
                renderLoadingMore()
              ) : phase === 'complete' ? (
                renderComplete()
              ) : null}
            </AnimatePresence>
          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}

// Wrap in Suspense to satisfy Next.js 15 requirement for useSearchParams()
export default function ChallengeArenaPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-[#4F46E5] border-t-transparent rounded-full animate-spin" />
      </div>
    }>
      <ChallengeArena />
    </Suspense>
  );
}
