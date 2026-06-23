'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface ScreenQuickInsightsProps {
  onNext: () => void;
}

interface Question {
  id: number;
  text: string;
  options: { value: string; label: string; emoji?: string }[];
}

const questions: Question[] = [
  {
    id: 1,
    text: 'What excites you most about your future?',
    options: [
      { value: 'discover', label: 'Discovering how things work', emoji: '🔬' },
      { value: 'create', label: 'Creating & building things', emoji: '🎨' },
      { value: 'help', label: 'Helping & working with people', emoji: '🤝' },
      { value: 'lead', label: 'Leading & organizing', emoji: '🚀' },
    ],
  },
  {
    id: 2,
    text: 'How do you learn best?',
    options: [
      { value: 'reading', label: 'Reading & taking notes', emoji: '📖' },
      { value: 'practice', label: 'Hands-on practice', emoji: '👐' },
      { value: 'discussion', label: 'Discussing with others', emoji: '💬' },
      { value: 'watching', label: 'Watching demonstrations', emoji: '🎬' },
    ],
  },
  {
    id: 3,
    text: 'Which subject do you enjoy most?',
    options: [
      { value: 'math', label: 'Mathematics', emoji: '📐' },
      { value: 'science', label: 'Science', emoji: '🔬' },
      { value: 'english', label: 'English & Literature', emoji: '📝' },
      { value: 'social', label: 'Social Studies', emoji: '🌍' },
    ],
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08 } },
};

const cardVariants = {
  hidden: { opacity: 0, y: 15 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35 } },
};

export default function ScreenQuickInsights({ onNext }: ScreenQuickInsightsProps) {
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [selectedOption, setSelectedOption] = useState<string | null>(null);

  const currentQuestion = questions[currentIdx];
  const isLastQuestion = currentIdx === questions.length - 1;

  const handleSelect = (value: string) => {
    setSelectedOption(value);
  };

  const handleNext = () => {
    if (!selectedOption) return;

    // Save answer
    setAnswers((prev) => ({ ...prev, [currentQuestion.id]: selectedOption }));

    if (isLastQuestion) {
      // All done — proceed to profile-ready
      setTimeout(() => onNext(), 300);
    } else {
      setSelectedOption(null);
      setCurrentIdx((prev) => prev + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const progress = ((currentIdx + (selectedOption ? 1 : 0)) / questions.length) * 100;

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center relative overflow-hidden py-12 px-4 sm:px-6">
      {/* Subtle background */}
      <div className="absolute inset-0 pointer-events-none">
        <motion.div
          animate={{ scale: [1, 1.08, 1] }}
          transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut' }}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-r from-[#2563EB]/5 to-[#7C3AED]/5 rounded-full blur-3xl"
        />
      </div>

      <div className="relative z-10 w-full max-w-lg mx-auto">
        {/* Progress bar */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="h-1 bg-[#E2E8F0] rounded-full mb-10 overflow-hidden"
        >
          <motion.div
            className="h-full bg-gradient-to-r from-[#2563EB] to-[#7C3AED] rounded-full"
            initial={{ width: '0%' }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.4 }}
          />
        </motion.div>

        <AnimatePresence mode="wait">
          <motion.div
            key={currentQuestion.id}
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -30 }}
            transition={{ duration: 0.3 }}
          >
            {/* Question count */}
            <p className="text-sm font-medium text-[#94A3B8] mb-6">
              Question {currentIdx + 1} of {questions.length}
            </p>

            {/* Question text */}
            <h2 className="text-2xl sm:text-3xl font-bold text-[#1E293B] mb-8 leading-snug">
              {currentQuestion.text}
            </h2>

            {/* Options */}
            <motion.div
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              className="space-y-3 mb-10"
            >
              {currentQuestion.options.map((option) => (
                <motion.button
                  key={option.value}
                  variants={cardVariants}
                  whileHover={{ x: 4 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleSelect(option.value)}
                  className={`w-full text-left px-5 py-4 rounded-xl border-2 transition-all duration-200 flex items-center gap-4 ${
                    selectedOption === option.value
                      ? 'border-[#2563EB] bg-[#EFF6FF] shadow-md shadow-[#2563EB]/10'
                      : 'border-[#E2E8F0] bg-white hover:border-[#C7D2FE] hover:bg-[#F8FAFC]'
                  }`}
                >
                  {option.emoji && (
                    <span className="text-xl flex-shrink-0">{option.emoji}</span>
                  )}
                  <span
                    className={`text-base flex-1 ${
                      selectedOption === option.value
                        ? 'font-semibold text-[#2563EB]'
                        : 'font-medium text-[#1E293B]'
                    }`}
                  >
                    {option.label}
                  </span>
                  <div
                    className={`w-5 h-5 rounded-full border-2 flex-shrink-0 flex items-center justify-center transition-all ${
                      selectedOption === option.value
                        ? 'border-[#2563EB] bg-[#2563EB]'
                        : 'border-[#CBD5E1]'
                    }`}
                  >
                    {selectedOption === option.value && (
                      <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                      </svg>
                    )}
                  </div>
                </motion.button>
              ))}
            </motion.div>

            {/* Next / Continue button */}
            <div className="flex justify-end">
              <motion.button
                whileHover={selectedOption ? { scale: 1.02 } : {}}
                whileTap={selectedOption ? { scale: 0.98 } : {}}
                onClick={handleNext}
                disabled={!selectedOption}
                className={`px-8 py-3 rounded-xl font-semibold text-base transition-all duration-200 ${
                  selectedOption
                    ? 'bg-gradient-to-r from-[#2563EB] to-[#7C3AED] text-white shadow-lg shadow-[#2563EB]/20 hover:shadow-xl'
                    : 'bg-[#E2E8F0] text-[#94A3B8] cursor-not-allowed'
                }`}
              >
                {isLastQuestion ? 'Complete →' : 'Next →'}
              </motion.button>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
