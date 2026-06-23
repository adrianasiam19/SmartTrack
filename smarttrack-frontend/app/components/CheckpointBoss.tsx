'use client';

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface BossQuestion {
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
}

interface CheckpointBossProps {
  title: string;
  questions: BossQuestion[];
  passThreshold: number;
  bonusXp: number;
  onComplete: (passed: boolean, xpEarned: number) => void;
}

export default function CheckpointBoss({
  title,
  questions,
  passThreshold,
  bonusXp,
  onComplete,
}: CheckpointBossProps) {
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [correctCount, setCorrectCount] = useState(0);
  const [results, setResults] = useState<boolean[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [showIntro, setShowIntro] = useState(true);

  const currentQuestion = questions[currentQuestionIdx];
  const totalQuestions = questions.length;
  const passed = correctCount >= passThreshold;

  const handleSelectOption = useCallback((idx: number) => {
    if (showFeedback) return;
    setSelectedOption(idx);
    const correct = idx === currentQuestion.correctIndex;
    setIsCorrect(correct);
    setShowFeedback(true);
    if (correct) {
      setCorrectCount((p) => p + 1);
      setResults((p) => [...p, true]);
    } else {
      setResults((p) => [...p, false]);
    }
  }, [showFeedback, currentQuestion]);

  const handleNext = useCallback(() => {
    setSelectedOption(null);
    setShowFeedback(false);
    if (currentQuestionIdx >= totalQuestions - 1) {
      setShowResults(true);
    } else {
      setCurrentQuestionIdx((prev) => prev + 1);
    }
  }, [currentQuestionIdx, totalQuestions]);

  const handleFinish = () => { onComplete(passed, passed ? bonusXp : 0); };

  if (showIntro) {
    return (
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
        className="bg-white border border-gray-200 rounded-xl p-8 text-center">
        <h2 className="text-2xl font-bold text-[#1E293B] mb-2">Checkpoint Challenge</h2>
        <p className="text-[#4F46E5] font-bold text-lg mb-1">{title}</p>
        <p className="text-gray-500 text-sm mb-6">Answer {passThreshold}+ of {totalQuestions} correctly to pass</p>
        <div className="bg-amber-50 border border-[#FDE68A] rounded-xl p-4 mb-6 inline-block">
          <span className="text-[#D97706] font-bold">{bonusXp} Bonus XP</span>
        </div>
        <div className="grid grid-cols-3 gap-3 mb-6">
          <div className="bg-gray-50 rounded-xl p-3">
            <p className="text-xs text-gray-500">Questions</p>
            <p className="text-lg font-bold text-[#1E293B]">{totalQuestions}</p>
          </div>
          <div className="bg-gray-50 rounded-xl p-3">
            <p className="text-xs text-gray-500">To Pass</p>
            <p className="text-lg font-bold text-[#4F46E5]">{passThreshold}</p>
          </div>
          <div className="bg-gray-50 rounded-xl p-3">
            <p className="text-xs text-gray-500">XP Reward</p>
            <p className="text-lg font-bold text-[#D97706]">+{bonusXp}</p>
          </div>
        </div>
        <button onClick={() => setShowIntro(false)}
          className="px-8 py-3 bg-[#4F46E5] text-white rounded-lg font-medium hover:bg-[#4338CA] transition-all">
          Start Challenge
        </button>
      </motion.div>
    );
  }

  if (showResults) {
    return (
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
        className="bg-white border border-gray-200 rounded-xl p-8 text-center">
        <div className={`w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 border-2 ${
          passed ? 'bg-[#EEF2FF] border-[#C7D2FE]' : 'bg-red-50 border-red-200'
        }`}>
          <span className={`text-3xl font-bold ${passed ? 'text-[#4F46E5]' : 'text-red-400'}`}>{passed ? 'P' : 'X'}</span>
        </div>
        <h2 className={`text-2xl font-bold mb-2 ${passed ? 'text-[#4F46E5]' : 'text-red-500'}`}>
          {passed ? 'Challenge Passed!' : 'Not this time'}
        </h2>
        <p className="text-gray-500 text-sm mb-6">{correctCount}/{totalQuestions} correct (need {passThreshold} to pass)</p>
        {passed && (
          <div className="inline-flex items-center gap-3 bg-[#EEF2FF] border border-[#C7D2FE] rounded-2xl px-8 py-4 mb-6">
            <span className="text-3xl font-black text-[#4F46E5]">+{bonusXp} XP</span>
          </div>
        )}
        <button onClick={handleFinish}
          className="w-full py-3 bg-[#4F46E5] text-white rounded-lg font-medium hover:bg-[#4338CA] transition-all">
          {passed ? 'Continue' : 'Try Again Later'}
        </button>
      </motion.div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs font-bold text-[#4F46E5] uppercase tracking-wider">{title}</span>
        <span className="text-xs text-gray-400">Question {currentQuestionIdx + 1} of {totalQuestions}</span>
      </div>

      <div className="flex items-center gap-1.5 mb-4">
        {questions.map((_, idx) => (
          <div key={idx} className={`h-1.5 flex-1 rounded-full transition-all ${
            idx < currentQuestionIdx
              ? results[idx] ? 'bg-[#4F46E5]' : 'bg-red-400'
              : idx === currentQuestionIdx ? 'bg-[#4F46E5]/60' : 'bg-gray-200'
          }`} />
        ))}
      </div>

      <p className="text-[#1E293B] font-bold text-lg mb-4">{currentQuestion.question}</p>
      <div className="space-y-2.5">
        {currentQuestion.options.map((option, idx) => {
          let borderClass = 'border-gray-200 bg-white hover:bg-gray-50 hover:border-gray-300';
          if (showFeedback && selectedOption === idx) {
            borderClass = isCorrect
              ? 'border-[#4F46E5] bg-[#EEF2FF]'
              : 'border-red-300 bg-red-50';
          } else if (showFeedback && idx === currentQuestion.correctIndex) {
            borderClass = 'border-[#4F46E5]/60 bg-[#EEF2FF]';
          }
          return (
            <button key={idx} onClick={() => handleSelectOption(idx)} disabled={showFeedback}
              className={`w-full text-left px-5 py-3.5 rounded-lg border transition-all duration-200 ${borderClass} disabled:cursor-default`}>
              <div className="flex items-center gap-3">
                <div className={`w-7 h-7 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all ${
                  showFeedback && idx === currentQuestion.correctIndex
                    ? 'border-[#4F46E5] bg-[#4F46E5]'
                    : showFeedback && selectedOption === idx && !isCorrect
                    ? 'border-red-400 bg-red-400'
                    : selectedOption === idx ? 'border-[#4F46E5] bg-[#4F46E5]' : 'border-gray-300'
                }`}>
                  {showFeedback && idx === currentQuestion.correctIndex && (
                    <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" /></svg>
                  )}
                  {showFeedback && selectedOption === idx && !isCorrect && (
                    <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M6 18L18 6M6 6l12 12" /></svg>
                  )}
                </div>
                <span className="text-sm font-medium text-gray-400 mr-2">{String.fromCharCode(65 + idx)}.</span>
                <span className="text-[#1E293B]">{option}</span>
              </div>
            </button>
          );
        })}
      </div>

      <AnimatePresence>
        {showFeedback && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            className={`p-4 rounded-lg border mt-4 ${isCorrect ? 'bg-[#EEF2FF] border-[#C7D2FE]' : 'bg-red-50 border-red-200'}`}>
            <div>
              <p className={`font-bold text-sm mb-1 ${isCorrect ? 'text-[#4F46E5]' : 'text-red-600'}`}>
                {isCorrect ? 'Correct!' : 'Not quite'}
              </p>
              <p className="text-gray-600 text-sm">{currentQuestion.explanation}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {showFeedback && (
        <button onClick={handleNext}
          className="w-full py-3 bg-[#4F46E5] text-white rounded-lg font-medium hover:bg-[#4338CA] transition-all mt-4">
          {currentQuestionIdx >= totalQuestions - 1 ? 'See Results' : 'Next Question'}
        </button>
      )}
    </div>
  );
}
