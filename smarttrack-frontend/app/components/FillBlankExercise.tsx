'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface FillBlankExerciseProps {
  template: string;
  answers: string[];
  hints: string[];
  explanation: string;
  onComplete: (correct: boolean) => void;
  onRequestHint: () => void;
}

export default function FillBlankExercise({
  template,
  answers,
  hints,
  explanation,
  onComplete,
  onRequestHint,
}: FillBlankExerciseProps) {
  const [userInputs, setUserInputs] = useState<string[]>(answers.map(() => ''));
  const [showFeedback, setShowFeedback] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [hintIndex, setHintIndex] = useState(0);

  const parts = template.split('___');
  const blanks = answers.length;

  const handleInputChange = (index: number, value: string) => {
    if (showFeedback) return;
    const newInputs = [...userInputs];
    newInputs[index] = value;
    setUserInputs(newInputs);
  };

  const handleCheck = () => {
    const correct = userInputs.every(
      (input, i) => input.trim().toLowerCase() === answers[i].trim().toLowerCase()
    );
    setIsCorrect(correct);
    setShowFeedback(true);
    setTimeout(() => { onComplete(correct); }, 2000);
  };

  const handleHint = () => {
    if (hintIndex < hints.length) {
      setShowHint(true);
      setHintIndex((p) => p + 1);
      onRequestHint();
    }
  };

  const allFilled = userInputs.every((i) => i.trim().length > 0);

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl p-5 border border-gray-200">
        <p className="text-[#1E293B] leading-relaxed text-sm">
          {parts.map((part, idx) => (
            <span key={idx}>
              {part}
              {idx < blanks && (
                <input
                  type="text"
                  value={userInputs[idx]}
                  onChange={(e) => handleInputChange(idx, e.target.value)}
                  disabled={showFeedback}
                  className={`inline-block mx-1 px-2 py-0.5 w-28 border-b-2 bg-transparent text-center text-[#1E293B] font-mono outline-none transition-all
                    ${showFeedback
                      ? userInputs[idx].trim().toLowerCase() === answers[idx].trim().toLowerCase()
                        ? 'border-[#4F46E5] text-[#4F46E5]'
                        : 'border-red-400 text-red-500'
                      : 'border-[#4F46E5]/50 focus:border-[#4F46E5]'
                    }`}
                  placeholder="______"
                />
              )}
            </span>
          ))}
        </p>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={handleCheck}
          disabled={!allFilled || showFeedback}
          className="flex-1 py-2.5 bg-[#4F46E5] text-white rounded-lg font-medium text-sm hover:bg-[#4338CA] transition-all disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {showFeedback ? (isCorrect ? 'Correct!' : 'Not quite...') : 'Check Answer'}
        </button>
        {!showFeedback && (
          <button
            onClick={handleHint}
            disabled={hintIndex >= hints.length}
            className="px-3 py-2.5 bg-[#FFFBEB] border border-[#FDE68A] text-[#D97706] rounded-lg hover:bg-[#FEF3C7] transition-all disabled:opacity-40"
            title="Get a hint"
          >
            Hint
          </button>
        )}
      </div>

      <AnimatePresence>
        {showHint && hintIndex > 0 && (
          <motion.div initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className="p-3 bg-[#FFFBEB] border border-[#FDE68A] rounded-lg">
            <p className="text-[#92400E] text-sm">{hints[hintIndex - 1]}</p>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showFeedback && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            className={`p-4 rounded-lg border ${isCorrect ? 'bg-[#EEF2FF] border-[#C7D2FE]' : 'bg-red-50 border-red-200'}`}>
            <div>
              <p className={`font-bold text-sm mb-1 ${isCorrect ? 'text-[#4F46E5]' : 'text-red-600'}`}>
                {isCorrect ? 'Perfect!' : 'Keep trying!'}
              </p>
              <p className="text-gray-600 text-sm leading-relaxed">{explanation}</p>
              {!isCorrect && (
                <p className="text-gray-400 text-xs mt-2">Correct answers: {answers.join(', ')}</p>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
