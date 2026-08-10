'use client';

import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { submitPsychometric } from '../lib/challengesApi';

interface PsychometricOption {
  value: string;
  label: string;
}

interface PsychometricCardData {
  id: string;
  category: string;
  question: string;
  display: string;
  options: PsychometricOption[];
}

interface PsychometricPromptProps {
  onComplete: () => void;
  onSkip: () => void;
  preloadedCard?: PsychometricCardData | null;
}

export default function PsychometricPrompt({ onComplete, onSkip, preloadedCard }: PsychometricPromptProps) {
  const [card, setCard] = useState<PsychometricCardData | null>(preloadedCard || null);
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [, setError] = useState(false);
  const [loading, setLoading] = useState(!preloadedCard);
  const settledRef = useRef(false);

  useEffect(() => {
    if (preloadedCard && preloadedCard.id && !settledRef.current) {
      setCard(preloadedCard);
      setError(false);
      setLoading(false);
      settledRef.current = true;
    }
  }, [preloadedCard]);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (!settledRef.current) {
        settledRef.current = true;
        setCard({
          id: 'psych_q1',
          category: 'Insight',
          question: 'What sounds most exciting to you?',
          display: 'choose',
          options: [
            { value: 'A', label: 'Solving puzzles and brain teasers' },
            { value: 'B', label: 'Discovering how things work' },
            { value: 'C', label: 'Creating art or telling stories' },
            { value: 'D', label: 'Helping and working with others' },
          ],
        });
        setLoading(false);
      }
    }, 5000);
    return () => clearTimeout(timeoutId);
  }, []);

  const handleSelect = async (value: string) => {
    if (submitting || !card) return;
    setSelectedOption(value);
    setSubmitting(true);
    try { await submitPsychometric({ question_id: card.id, answer: value }); } catch {}
    setTimeout(() => {
      setSubmitting(false);
      setSelectedOption(null);
      setCard(null);
      onComplete();
    }, 800);
  };

  if (loading) {
    return (
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}
        className="bg-white border border-gray-200 rounded-xl p-8 max-w-lg mx-auto text-center">
        <p className="text-sm text-gray-500">Loading insight...</p>
      </motion.div>
    );
  }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}
      className="bg-white border border-gray-200 rounded-xl p-8 max-w-lg mx-auto">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-xs font-bold text-[#4F46E5] uppercase tracking-wider">Quick Insight</span>
      </div>

      <h3 className="text-lg font-semibold text-[#1E293B] mb-5 leading-relaxed">
        {card?.question || 'What sounds most exciting to you?'}
      </h3>

      <div className="space-y-2.5">
        {(card?.options || []).map((option) => (
          <button key={option.value} onClick={() => handleSelect(option.value)} disabled={submitting}
            className={`w-full text-left px-5 py-3.5 rounded-lg border transition-all duration-200 ${
              selectedOption === option.value
                ? 'border-[#4F46E5] bg-[#EEF2FF]'
                : 'border-gray-200 bg-white hover:bg-gray-50 hover:border-gray-300'
            } disabled:opacity-70`}>
            <div className="flex items-center gap-3">
              <span className={`w-7 h-7 rounded-full border-2 flex items-center justify-center text-xs font-bold flex-shrink-0 transition-all ${
                selectedOption === option.value
                  ? 'border-[#4F46E5] bg-[#4F46E5] text-white'
                  : 'border-gray-300 text-gray-400'
              }`}>{option.value}</span>
              <span className="text-[#1E293B] text-sm">{option.label}</span>
            </div>
          </button>
        ))}
      </div>

      <button onClick={onSkip} className="mt-4 w-full text-center text-xs text-gray-400 hover:text-gray-600 transition-colors py-2">
        Skip
      </button>
    </motion.div>
  );
}
