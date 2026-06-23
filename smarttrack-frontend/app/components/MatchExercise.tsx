'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface MatchExerciseProps {
  instruction: string;
  leftItems: string[];
  rightItems: string[];
  correctMatches: number[];
  explanation: string;
  onComplete: (correct: boolean) => void;
}

export default function MatchExercise({
  instruction,
  leftItems,
  rightItems,
  correctMatches,
  explanation,
  onComplete,
}: MatchExerciseProps) {
  const [selections, setSelections] = useState<number[]>(leftItems.map(() => -1));
  const [selectedLeft, setSelectedLeft] = useState<number | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);

  const handleLeftClick = (leftIdx: number) => {
    if (showFeedback) return;
    setSelectedLeft(leftIdx);
  };

  const handleRightClick = (rightIdx: number) => {
    if (showFeedback || selectedLeft === null) return;
    const newSelections = [...selections];
    const prevLeft = newSelections.indexOf(rightIdx);
    if (prevLeft !== -1) { newSelections[prevLeft] = -1; }
    newSelections[selectedLeft] = rightIdx;
    setSelections(newSelections);
    setSelectedLeft(null);
  };

  const handleReset = () => {
    setSelections(leftItems.map(() => -1));
    setSelectedLeft(null);
    setShowFeedback(false);
  };

  const handleCheck = () => {
    if (selections.some((s) => s === -1)) return;
    const allCorrect = selections.every((rightIdx, leftIdx) => rightIdx === correctMatches[leftIdx]);
    setIsCorrect(allCorrect);
    setShowFeedback(true);
    setTimeout(() => { onComplete(allCorrect); }, 2000);
  };

  const allMatched = selections.every((s) => s !== -1);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm text-[#1E293B]">{instruction}</p>
        <button onClick={handleReset} className="text-xs text-gray-400 hover:text-gray-600 transition-colors">
          Reset
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          {leftItems.map((item, idx) => {
            const isSelected = selectedLeft === idx;
            const matchedRight = selections[idx];
            return (
              <button key={`l-${idx}`} onClick={() => handleLeftClick(idx)}
                className={`w-full text-left px-3 py-2.5 rounded-lg border text-sm transition-all ${
                  showFeedback
                    ? selections[idx] === correctMatches[idx]
                      ? 'border-[#4F46E5]/60 bg-[#EEF2FF]'
                      : selections[idx] !== -1 ? 'border-red-300 bg-red-50' : 'border-gray-200 bg-white'
                    : isSelected
                    ? 'border-[#4F46E5] bg-[#EEF2FF]'
                    : matchedRight !== -1 ? 'border-[#4F46E5]/40 bg-[#EEF2FF]' : 'border-gray-200 bg-white hover:border-gray-300'
                }`}>
                <span className="text-[#1E293B]">{item}</span>
              </button>
            );
          })}
        </div>

        <div className="space-y-2">
          {rightItems.map((item, idx) => {
            const isMatched = selections.includes(idx);
            const matchOwner = selections.indexOf(idx);
            const isCorrectMatch = matchOwner !== -1 && correctMatches[matchOwner] === idx;
            return (
              <button key={`r-${idx}`} onClick={() => handleRightClick(idx)} disabled={showFeedback}
                className={`w-full text-left px-3 py-2.5 rounded-lg border text-sm transition-all ${
                  showFeedback
                    ? isCorrectMatch ? 'border-[#4F46E5]/60 bg-[#EEF2FF]' : isMatched ? 'border-red-300 bg-red-50' : 'border-gray-200 bg-white'
                    : isMatched
                    ? 'border-[#4F46E5]/40 bg-[#EEF2FF]'
                    : selectedLeft !== null
                    ? 'border-gray-300 bg-gray-50 cursor-pointer hover:border-[#4F46E5] hover:bg-[#EEF2FF]'
                    : 'border-gray-200 bg-white'
                }`}>
                <span className="text-[#1E293B]">{item}</span>
              </button>
            );
          })}
        </div>
      </div>

      {allMatched && !showFeedback && (
        <button onClick={handleCheck}
          className="w-full py-2.5 bg-[#4F46E5] text-white rounded-lg font-medium text-sm hover:bg-[#4338CA] transition-all">
          Check Matches
        </button>
      )}

      <AnimatePresence>
        {showFeedback && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            className={`p-4 rounded-lg border ${isCorrect ? 'bg-[#EEF2FF] border-[#C7D2FE]' : 'bg-red-50 border-red-200'}`}>
            <div>
              <p className={`font-bold text-sm mb-1 ${isCorrect ? 'text-[#4F46E5]' : 'text-red-600'}`}>
                {isCorrect ? 'All matched correctly!' : 'Some matches are wrong'}
              </p>
              <p className="text-gray-600 text-sm leading-relaxed">{explanation}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {selectedLeft !== null && (
        <p className="text-xs text-[#4F46E5] text-center animate-pulse">
          Now click the matching item on the right
        </p>
      )}
    </div>
  );
}
