'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface PredictChallengeProps {
  pattern: string;
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
  onComplete: (correct: boolean) => void;
}

export default function PredictChallenge({
  pattern,
  question,
  options,
  correctIndex,
  explanation,
  onComplete,
}: PredictChallengeProps) {
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [revealed, setRevealed] = useState(false);

  const handleSelect = (idx: number) => {
    if (showFeedback) return;
    setSelectedOption(idx);
    const correct = idx === correctIndex;
    setIsCorrect(correct);
    setShowFeedback(true);
    setTimeout(() => { onComplete(correct); }, 2500);
  };

  const handleReveal = () => { setRevealed(true); };

  return (
    <div className="space-y-4">
      <div className="bg-[#EEF2FF] rounded-xl p-6 border border-[#C7D2FE] text-center">
        <div className="flex items-center justify-center gap-2 mb-3">
          <span className="text-xs font-bold text-[#4F46E5] uppercase tracking-wider">Can you spot the pattern?</span>
        </div>
        {!revealed ? (
          <button
            onClick={handleReveal}
            className="px-6 py-3 bg-white border border-gray-200 rounded-xl text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition-all text-sm"
          >
            Tap to reveal the pattern
          </button>
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="font-mono text-lg text-[#1E293B] whitespace-pre-wrap leading-relaxed"
          >
            {pattern}
          </motion.div>
        )}
      </div>

      {revealed && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-[#1E293B] font-semibold mb-3">{question}</p>
          <div className="space-y-2">
            {options.map((option, idx) => {
              let borderClass = 'border-gray-200 hover:border-gray-300 bg-white hover:bg-gray-50';
              if (showFeedback && selectedOption === idx) {
                borderClass = isCorrect
                  ? 'border-[#4F46E5] bg-[#EEF2FF]'
                  : 'border-red-300 bg-red-50';
              } else if (showFeedback && idx === correctIndex) {
                borderClass = 'border-[#4F46E5]/60 bg-[#EEF2FF]';
              }
              return (
                <button key={idx} onClick={() => handleSelect(idx)} disabled={showFeedback}
                  className={`w-full text-left px-4 py-3 rounded-lg border transition-all duration-200 ${borderClass} disabled:cursor-default`}>
                  <div className="flex items-center gap-3">
                    <span className="w-6 h-6 rounded-full border-2 border-gray-300 flex items-center justify-center text-xs text-gray-400 font-mono">
                      {String.fromCharCode(65 + idx)}
                    </span>
                    <span className="text-[#1E293B] text-sm">{option}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </motion.div>
      )}

      <AnimatePresence>
        {showFeedback && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            className={`p-4 rounded-lg border ${isCorrect ? 'bg-[#EEF2FF] border-[#C7D2FE]' : 'bg-red-50 border-red-200'}`}>
            <div>
              <p className={`font-bold text-sm mb-1 ${isCorrect ? 'text-[#4F46E5]' : 'text-red-600'}`}>
                {isCorrect ? 'You spotted it!' : 'Not quite — look at the pattern again'}
              </p>
              <p className="text-gray-600 text-sm leading-relaxed">{explanation}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
