"""Write the complete challenges frontend page."""
import os

path = r'C:\Users\Admin\Downloads\SmartTrack-Project\smarttrack-frontend\app\challenges\page.tsx'

content = """'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import Sidebar from '../components/Sidebar';
import GlassmorphicLayout from '../components/GlassmorphicLayout';
import { getAccessToken, getAuthHeaders } from '../lib/authApi';

type ChallengePhase = 'intro' | 'gameplay' | 'feedback' | 'loading_more' | 'complete';

interface Question {
  id: number;
  domain: string;
  question: string;
  options: { [key: string]: string };
  answer_hash: string;
}

export default function Challenges() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const domain = searchParams.get('domain');
  
  // State
  const [phase, setPhase] = useState<ChallengePhase>('intro');
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [questionQueue, setQuestionQueue] = useState<Question[]>([]);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  
  // Tracking & Telemetry
  const [questionsAnswered, setQuestionsAnswered] = useState(0);
  const [startTime, setStartTime] = useState<number>(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Feedback
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [correctAnswer, setCorrectAnswer] = useState<string | null>(null);
  const [timeLeft, setTimeLeft] = useState(30);

  // Polling ref
  const pollRef = useRef<NodeJS.Timeout | null>(null);
  
  const MAX_QUESTIONS = 10;
  const QUESTION_TIMEOUT = 30;
  const API_BASE = 'http://localhost:8000/api/v1';

  // Helpers
  const decryptAnswer = (hash: string): string => {
    try {
      const decoded = atob(hash);
      return decoded.split(':')[1];
    } catch (e) {
      return '';
    }
  };

  const handleError = (e: any, defaultMsg: string) => {
    console.error(defaultMsg, e);
    setError(defaultMsg);
    setLoading(false);
  };

  const fetchMoreQuestions = useCallback(async () => {
    try {
      const res = await fetch(
        `${API_BASE}/challenges/question/next${domain ? `?domain=${domain}` : ''}`,
        { headers: getAuthHeaders() }
      );
      if (!res.ok) return null;
      const data = await res.json();
      return data.questions || [];
    } catch {
      return null;
    }
  }, [domain]);

  const pollForQuestions = useCallback(async () => {
    const qs = await fetchMoreQuestions();
    if (qs && qs.length > 0) {
      setQuestionQueue(prev => {
        const existingIds = new Set(prev.map(q => q.id));
        const newQs = qs.filter((q: Question) => !existingIds.has(q.id));
        return [...prev, ...newQs];
      });
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    }
  }, [fetchMoreQuestions]);

  // Start polling when in loading_more phase
  useEffect(() => {
    if (phase === 'loading_more') {
      pollRef.current = setInterval(pollForQuestions, 2000);
    }
    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };
  }, [phase, pollForQuestions]);

  // Timer Logic
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (phase === 'gameplay' && timeLeft > 0) {
      timer = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    } else if (timeLeft === 0 && phase === 'gameplay') {
      if (selectedAnswer) {
        submitAnswer(selectedAnswer);
      } else {
        submitAnswer('timeout');
      }
    }
    return () => clearInterval(timer);
  }, [phase, timeLeft, selectedAnswer]);

  const startChallenge = async () => {
    try {
      setLoading(true);
      setError(null);
      setTimeLeft(QUESTION_TIMEOUT);
      const token = getAccessToken();
      if (!token) throw new Error('Not authenticated');

      const url = domain 
        ? `${API_BASE}/challenges/calibration/start?domain=${domain}`
        : `${API_BASE}/challenges/calibration/start`;

      const res = await fetch(url, {
        method: 'POST',
        headers: getAuthHeaders(),
      });

      if (!res.ok) throw new Error('Failed to start calibration');

      const data = await res.json();
      const initialQuestions = data.questions || [];
      if (initialQuestions.length > 0) {
        setCurrentQuestion(initialQuestions[0]);
        setQuestionQueue(initialQuestions.slice(1));
        setPhase('gameplay');
        setStartTime(Date.now());
        setTimeLeft(QUESTION_TIMEOUT);
      } else {
        throw new Error('No questions returned from server');
      }
    } catch (e) {
      handleError(e, 'Failed to start the placement match.');
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async (answerKey: string) => {
    if (!currentQuestion || loading) return;
    
    setSelectedAnswer(answerKey);
    setLoading(true);
    setError(null);
    
    const timeTaken = Math.max(0, (Date.now() - startTime) / 1000);
    
    const localCorrectAnswer = decryptAnswer(currentQuestion.answer_hash);
    const localIsCorrect = answerKey === localCorrectAnswer;
    
    setIsCorrect(localIsCorrect);
    setCorrectAnswer(localCorrectAnswer);
    setPhase('feedback');

    try {
      const submitRes = await fetch(`${API_BASE}/challenges/response/submit`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          question_id: currentQuestion.id,
          selected_option: answerKey,
          time_taken_seconds: timeTaken,
          hints_used: 0,
        }),
      });

      if (!submitRes.ok) throw new Error('Failed to submit answer');
      const submitData = await submitRes.json();
      
      setLoading(false);
      
      const newCount = questionsAnswered + 1;
      setQuestionsAnswered(newCount);

      // Update queue with piggybacked questions (includes AI-prefetched)
      if (submitData.next_questions && submitData.next_questions.length > 0) {
        setQuestionQueue(prev => {
          const existingIds = new Set(prev.map(q => q.id));
          const newQs = submitData.next_questions.filter(
            (q: Question) => !existingIds.has(q.id) && q.id !== currentQuestion.id
          );
          return [...prev, ...newQs];
        });
      }
      
      setTimeout(() => {
        if (newCount >= MAX_QUESTIONS) {
          setPhase('complete');
        } else {
          advanceToNextQuestion();
        }
      }, 1000);
      
    } catch (e) {
      handleError(e, 'Failed to submit answer.');
    }
  };

  const advanceToNextQuestion = () => {
    setQuestionQueue(prev => {
      const nextBatch = [...prev];
      const nextQ = nextBatch.shift();
      if (nextQ) {
        setCurrentQuestion(nextQ);
        setSelectedAnswer(null);
        setIsCorrect(null);
        setCorrectAnswer(null);
        setTimeLeft(QUESTION_TIMEOUT);
        setStartTime(Date.now());
        setPhase('gameplay');
      } else {
        setPhase('loading_more');
      }
      return nextBatch;
    });
  };

  // When questions arrive during loading_more phase
  useEffect(() => {
    if (phase === 'loading_more' && questionQueue.length > 0) {
      advanceToNextQuestion();
    }
  }, [questionQueue.length, phase]);

  // ── Renderers ─────────────────────────────────────────────────────

  const renderIntro = () => (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white/5 backdrop-blur-2xl rounded-2xl border border-white/10 p-12 text-center"
    >
      <div className="mb-8 flex justify-center">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-lime-400/20 border border-lime-400 shadow-[0_0_30px_rgba(163,230,53,0.3)]">
          <svg className="w-10 h-10 text-lime-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
      </div>
      <h1 className="text-3xl font-bold text-white mb-4">
        {domain ? `${domain} Challenge` : 'Placement Match'}
      </h1>
      <p className="text-gray-300 mb-8 max-w-lg mx-auto">
        Test your skills with adaptive questions. Each question has a 30-second timer.
        Your performance determines your skill profile and programme recommendations.
      </p>
      <div className="flex flex-col items-center gap-4">
        <button
          onClick={startChallenge}
          disabled={loading}
          className="px-8 py-4 bg-gradient-to-r from-lime-400 to-emerald-500 text-gray-900 
                     rounded-xl font-semibold text-lg hover:shadow-lg hover:shadow-lime-500/30 
                     transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
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
            'Start Challenge'
          )}
        </button>
        <p className="text-xs text-gray-500">{MAX_QUESTIONS} questions · {QUESTION_TIMEOUT}s each</p>
      </div>
    </motion.div>
  );

  const renderGameplay = () => {
    if (!currentQuestion) return null;
    const options = currentQuestion.options || {};
    const optionKeys = Object.keys(options);
    const timerPercent = (timeLeft / QUESTION_TIMEOUT) * 100;

    return (
      <motion.div
        key={currentQuestion.id}
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -50 }}
        className="bg-white/5 backdrop-blur-2xl rounded-2xl border border-white/10 p-8"
      >
        {/* Progress bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-400 mb-2">
            <span>Question {questionsAnswered + 1} of {MAX_QUESTIONS}</span>
            <span>{Math.round((questionsAnswered / MAX_QUESTIONS) * 100)}% Complete</span>
          </div>
          <div className="w-full bg-white/10 rounded-full h-2">
            <motion.div
              className="bg-gradient-to-r from-lime-400 to-emerald-500 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${(questionsAnswered / MAX_QUESTIONS) * 100}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>

        {/* Timer bar */}
        <div className="mb-6">
          <div className={`w-full bg-white/10 rounded-full h-1.5 transition-all ${
            timeLeft <= 5 ? 'animate-pulse' : ''
          }`}>
            <motion.div
              className={`h-1.5 rounded-full transition-colors ${
                timeLeft <= 5 ? 'bg-red-500' : timeLeft <= 10 ? 'bg-yellow-400' : 'bg-lime-400'
              }`}
              animate={{ width: `${timerPercent}%` }}
              transition={{ duration: 1 }}
            />
          </div>
          <div className="text-right mt-1">
            <span className={`text-sm font-mono ${
              timeLeft <= 5 ? 'text-red-400' : 'text-gray-400'
            }`}>
              {timeLeft}s
            </span>
          </div>
        </div>

        {/* Domain badge */}
        <span className="inline-block px-3 py-1 text-xs font-medium bg-lime-400/20 text-lime-300 
                        rounded-full border border-lime-400/30 mb-4">
          {currentQuestion.domain}
        </span>

        {/* Question */}
        <h2 className="text-xl font-semibold text-white mb-8 leading-relaxed">
          {currentQuestion.question}
        </h2>

        {/* Options */}
        <div className="space-y-3">
          {optionKeys.map((key) => (
            <button
              key={key}
              onClick={() => !loading && submitAnswer(key)}
              disabled={loading || selectedAnswer !== null}
              className={`w-full text-left px-6 py-4 rounded-xl border transition-all duration-200
                ${selectedAnswer === key
                  ? 'border-lime-400 bg-lime-400/20 shadow-lg shadow-lime-400/10'
                  : 'border-white/10 hover:border-white/30 bg-white/5 hover:bg-white/10'
                } disabled:opacity-70 disabled:cursor-not-allowed`}
            >
              <div className="flex items-center gap-4">
                <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all ${
                  selectedAnswer === key
                    ? 'border-lime-400 bg-lime-400'
                    : 'border-white/30'
                }`}>
                  {selectedAnswer === key && (
                    <svg className="w-4 h-4 text-gray-900" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-400 mr-3">{key}.</span>
                  <span className="text-white">{options[key]}</span>
                </div>
              </div>
            </button>
          ))}
        </div>
      </motion.div>
    );
  };

  const renderFeedback = () => (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-white/5 backdrop-blur-2xl rounded-2xl border border-white/10 p-8 text-center"
    >
      <div className="mb-6">
        <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full mb-4 ${
          isCorrect ? 'bg-green-500/20' : 'bg-red-500/20'
        }`}>
          {isCorrect ? (
            <svg className="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
            </svg>
          ) : (
            <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          )}
        </div>
        <h3 className={`text-2xl font-bold mb-2 ${isCorrect ? 'text-green-400' : 'text-red-400'}`}>
          {isCorrect ? 'Correct!' : 'Incorrect'}
        </h3>
        {!isCorrect && correctAnswer && (
          <p className="text-gray-300">
            The correct answer was: <span className="text-lime-400 font-semibold">{correctAnswer}</span>
          </p>
        )}
      </div>
      <div className="w-24 h-1 bg-white/10 rounded-full mx-auto">
        <motion.div
          className="h-full bg-lime-400 rounded-full"
          initial={{ width: 0 }}
          animate={{ width: '100%' }}
          transition={{ duration: 1 }}
        />
      </div>
      <p className="text-gray-500 text-sm mt-3">Next question loading...</p>
    </motion.div>
  );

  const renderLoadingMore = () => (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-white/5 backdrop-blur-2xl rounded-2xl border border-white/10 p-12 text-center"
    >
      <div className="flex flex-col items-center gap-6">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-lime-400/30 border-t-lime-400 rounded-full animate-spin" />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-8 h-8 border-4 border-emerald-400/30 border-b-emerald-400 rounded-full animate-spin animation-delay-150" />
          </div>
        </div>
        <div>
          <h3 className="text-xl font-semibold text-white mb-2">Generating Challenge</h3>
          <p className="text-gray-400 max-w-md">
            Our AI is crafting adaptive questions tailored to your skill level.
            This will just take a moment...
          </p>
        </div>
      </div>
    </motion.div>
  );

  const renderComplete = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white/5 backdrop-blur-2xl rounded-2xl border border-white/10 p-12 text-center"
    >
      <div className="mb-6 flex justify-center">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-lime-400/20 border border-lime-400 shadow-[0_0_30px_rgba(163,230,53,0.3)]">
          <svg className="w-10 h-10 text-lime-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      </div>
      <h1 className="text-3xl font-bold text-white mb-4">Challenge Complete!</h1>
      <p className="text-gray-300 mb-8">
        You answered {questionsAnswered} questions. Your results are being analyzed to
        generate personalized programme recommendations.
      </p>
      <div className="flex justify-center gap-4">
        <button
          onClick={() => router.push('/dashboard')}
          className="px-6 py-3 bg-lime-400 text-gray-900 rounded-xl font-semibold 
                     hover:bg-lime-500 transition-all"
        >
          View Dashboard
        </button>
        <button
          onClick={() => router.push('/recommendations')}
          className="px-6 py-3 border border-white/10 text-gray-300 rounded-xl 
                     hover:bg-white/5 transition-all"
        >
          View Recommendations
        </button>
      </div>
    </motion.div>
  );

  const renderError = () => (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-white/5 backdrop-blur-2xl rounded-2xl border border-red-500/30 p-8 text-center"
    >
      <div className="mb-4">
        <svg className="w-12 h-12 text-red-400 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      </div>
      <h3 className="text-xl font-semibold text-white mb-2">Something went wrong</h3>
      <p className="text-gray-400 mb-6">{error}</p>
      <button
        onClick={startChallenge}
        className="px-6 py-3 bg-lime-400 text-gray-900 rounded-xl font-semibold hover:bg-lime-500 transition-all"
      >
        Try Again
      </button>
    </motion.div>
  );

  // ── Main return ───────────────────────────────────────────────────
  return (
    <GlassmorphicLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1">
          <header className="bg-white/5 backdrop-blur-2xl border-b border-white/10 px-8 py-6">
            <h1 className="text-2xl font-semibold text-white">Challenges</h1>
          </header>
          <div className="p-8 max-w-3xl mx-auto">
            <AnimatePresence mode="wait">
              {error ? (
                renderError()
              ) : phase === 'intro' ? (
                renderIntro()
              ) : phase === 'gameplay' ? (
                renderGameplay()
              ) : phase === 'feedback' ? (
                renderFeedback()
              ) : phase === 'loading_more' ? (
                renderLoadingMore()
              ) : phase === 'complete' ? (
                renderComplete()
              ) : null}
            </AnimatePresence>
          </div>
        </main>
      </div>
    </GlassmorphicLayout>
  );
}
"""

os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Written {len(content)} bytes to {path}")
