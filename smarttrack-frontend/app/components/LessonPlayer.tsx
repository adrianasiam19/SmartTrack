'use client';

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowLeft,
  Zap,
  MessageSquare,
} from 'lucide-react';
import type { Lesson, LessonStep } from '../lib/learningContent';
import FillBlankExercise from './FillBlankExercise';
import MatchExercise from './MatchExercise';
import PredictChallenge from './PredictChallenge';
import CheckpointBoss from './CheckpointBoss';
import MathVisualizer from './MathVisualizer';
import LearningAssistant from './LearningAssistant';

interface LessonPlayerProps {
  lesson: Lesson;
  onComplete: (xpEarned: number) => void;
  onBack: () => void;
}

export default function LessonPlayer({ lesson, onComplete, onBack }: LessonPlayerProps) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(new Set());
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [totalXp, setTotalXp] = useState(lesson.xpReward);
  const [showAssistant, setShowAssistant] = useState(false);
  const [hintsUsed, setHintsUsed] = useState(0);

  const currentStep = lesson.steps[currentStepIndex];
  const isLastStep = currentStepIndex >= lesson.steps.length - 1;
  const progressPercent = (currentStepIndex / lesson.steps.length) * 100;

  const hasInteractiveContent =
    currentStep?.type === 'question' || currentStep?.type === 'fill-blank' ||
    currentStep?.type === 'match' || currentStep?.type === 'predict' || currentStep?.type === 'checkpoint';

  const handleSelectOption = useCallback((index: number) => {
    if (showFeedback || !currentStep?.exercise) return;
    setSelectedOption(index);
    const correct = index === currentStep.exercise.correctIndex;
    setIsCorrect(correct);
    setShowFeedback(true);
    setCompletedSteps((prev) => { const next = new Set(prev); next.add(currentStep.id); return next; });
  }, [showFeedback, currentStep]);

  const handleNext = useCallback(() => {
    setSelectedOption(null);
    setShowFeedback(false);
    setIsCorrect(false);
    if (isLastStep) {
      setIsComplete(true);
      setTimeout(() => { onComplete(Math.max(totalXp, lesson.xpReward)); }, 2500);
    } else {
      setCurrentStepIndex((prev) => prev + 1);
    }
  }, [isLastStep, lesson.xpReward, totalXp, onComplete]);

  const handleInfoContinue = useCallback(() => {
    setCompletedSteps((prev) => { const next = new Set(prev); next.add(currentStep.id); return next; });
    if (isLastStep) {
      setIsComplete(true);
      setTimeout(() => { onComplete(Math.max(totalXp, lesson.xpReward)); }, 2500);
    } else {
      setCurrentStepIndex((prev) => prev + 1);
    }
  }, [currentStep, isLastStep, lesson.xpReward, totalXp, onComplete]);

  const handleExerciseComplete = useCallback((correct: boolean) => {
    setCompletedSteps((prev) => { const next = new Set(prev); next.add(currentStep.id); return next; });
    if (correct) setTotalXp((prev) => prev + 5);
  }, [currentStep]);

  const handleCheckpointComplete = useCallback((passed: boolean, xp: number) => {
    setCompletedSteps((prev) => { const next = new Set(prev); next.add(currentStep.id); return next; });
    if (passed) setTotalXp((prev) => prev + xp);
  }, [currentStep]);

  if (isComplete) {
    return (
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
        className="max-w-lg mx-auto text-center">
        <div className="bg-white border border-gray-200 rounded-xl p-10">
          <h2 className="text-2xl font-bold text-[#1E293B] mb-2">Lesson Complete!</h2>
          <p className="text-gray-500 mb-6">{lesson.title}</p>
          <div className="inline-flex items-center gap-3 bg-[#EEF2FF] border border-[#C7D2FE] rounded-2xl px-8 py-4 mb-6">
            <span className="text-4xl font-black text-[#4F46E5]">+{totalXp} XP</span>
          </div>
          <div className="grid grid-cols-3 gap-2 mb-6">
            <div className="bg-gray-50 rounded-xl p-3">
              <p className="text-[10px] text-gray-500 uppercase tracking-wider">Steps</p>
              <p className="text-lg font-bold text-[#1E293B]">{completedSteps.size}/{lesson.steps.length}</p>
            </div>
            <div className="bg-gray-50 rounded-xl p-3">
              <p className="text-[10px] text-gray-500 uppercase tracking-wider">Subject</p>
              <p className="text-lg font-bold text-[#4F46E5] truncate">{lesson.subject}</p>
            </div>
            <div className="bg-gray-50 rounded-xl p-3">
              <p className="text-[10px] text-gray-500 uppercase tracking-wider">Difficulty</p>
              <p className="text-lg font-bold text-[#1E293B]">{'★'.repeat(lesson.difficulty)}</p>
            </div>
          </div>
          <button onClick={onBack}
            className="w-full py-3 bg-[#4F46E5] text-white rounded-lg font-medium hover:bg-[#4338CA] transition-all">
            Back to Learning Path
          </button>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-2xl mx-auto relative">
      <div className="flex items-center justify-between mb-4">
        <button onClick={onBack} className="flex items-center gap-2 text-gray-400 hover:text-[#1E293B] transition-colors">
          <ArrowLeft className="w-4 h-4" />
          <span className="text-sm">Back</span>
        </button>
        <div className="flex items-center gap-2">
          {totalXp > lesson.xpReward && (
            <div className="flex items-center gap-1 px-2.5 py-1 bg-amber-50 rounded-lg border border-[#FDE68A]">
              <span className="text-xs font-bold text-[#D97706]">+{totalXp - lesson.xpReward}</span>
            </div>
          )}
          <div className="flex items-center gap-1.5 px-3 py-1 bg-[#EEF2FF] rounded-lg border border-[#C7D2FE]">
            <span className="text-xs font-bold text-[#4F46E5]">{lesson.subject}</span>
          </div>
          <span className="text-sm text-gray-400 font-mono">{currentStepIndex + 1}/{lesson.steps.length}</span>
        </div>
      </div>

      <div className="w-full bg-gray-100 rounded-full h-1.5 mb-4 overflow-hidden">
        <div className="h-full bg-[#4F46E5] rounded-full transition-all duration-500" style={{ width: `${progressPercent}%` }} />
      </div>

      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-1.5">
          {lesson.steps.map((step, idx) => (
            <div key={step.id} className="flex items-center gap-1.5">
              {idx > 0 && <div className={`w-4 h-px ${idx <= currentStepIndex ? 'bg-[#4F46E5]/50' : 'bg-gray-200'}`} />}
              {completedSteps.has(step.id) || idx < currentStepIndex ? (
                <div className="w-4 h-4 rounded-full bg-[#4F46E5] flex items-center justify-center">
                  <svg className="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" /></svg>
                </div>
              ) : idx === currentStepIndex ? (
                <div className="w-4 h-4 rounded-full border-2 border-[#4F46E5] bg-[#EEF2FF]" />
              ) : (
                <div className="w-4 h-4 rounded-full border-2 border-gray-300" />
              )}
            </div>
          ))}
        </div>
        <button onClick={() => setShowAssistant(!showAssistant)}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium transition-all ${
            showAssistant ? 'bg-[#EEF2FF] border-[#C7D2FE] text-[#4F46E5]' : 'bg-white border-gray-200 text-gray-500 hover:text-gray-700 hover:bg-gray-50'
          }`}>
          <MessageSquare className="w-3.5 h-3.5" />
          <span>AI Tutor</span>
        </button>
      </div>

      <AnimatePresence mode="wait">
        <motion.div key={currentStep.id}
          initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }}
          transition={{ duration: 0.3 }}>
          <div className="bg-white border border-gray-200 rounded-xl p-8">
            <div className="flex items-center gap-2 mb-3">
              <div>
                <h3 className="text-lg font-bold text-[#1E293B]">{lesson.title}</h3>
                <p className="text-[10px] text-[#4F46E5]/80 font-medium uppercase tracking-wider">{lesson.subject}</p>
              </div>
            </div>

            <div className="space-y-3 mb-6 leading-relaxed">
              {renderLessonContent(currentStep.content)}
            </div>

            {currentStep.visualize && (
              <div className="mb-6 bg-gray-50 rounded-xl p-4 border border-gray-200">
                <MathVisualizer config={currentStep.visualize} animated={true} />
              </div>
            )}

            {currentStep.type === 'question' && currentStep.exercise && (
              <div className="border-t border-gray-100 pt-6 mt-6">
                <p className="text-[#1E293B] font-semibold mb-4">{currentStep.exercise.question}</p>
                <div className="space-y-2.5">
                  {currentStep.exercise.options.map((option, idx) => {
                    let borderClass = 'border-gray-200 bg-white hover:bg-gray-50 hover:border-gray-300';
                    if (showFeedback && selectedOption === idx) {
                      borderClass = isCorrect ? 'border-[#4F46E5] bg-[#EEF2FF]' : 'border-red-300 bg-red-50';
                    } else if (showFeedback && idx === currentStep.exercise!.correctIndex) {
                      borderClass = 'border-[#4F46E5]/60 bg-[#EEF2FF]';
                    }
                    return (
                      <button key={idx} onClick={() => handleSelectOption(idx)} disabled={showFeedback}
                        className={`w-full text-left px-5 py-3.5 rounded-lg border transition-all duration-200 ${borderClass} disabled:cursor-default`}>
                        <div className="flex items-center gap-3">
                          <div className={`w-7 h-7 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all ${
                            showFeedback && idx === currentStep.exercise!.correctIndex
                              ? 'border-[#4F46E5] bg-[#4F46E5]'
                              : showFeedback && selectedOption === idx && !isCorrect
                              ? 'border-red-400 bg-red-400'
                              : selectedOption === idx ? 'border-[#4F46E5] bg-[#4F46E5]' : 'border-gray-300'
                          }`}>
                            {showFeedback && idx === currentStep.exercise!.correctIndex && (
                              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" /></svg>
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
                      className={`mt-5 p-4 rounded-lg border ${isCorrect ? 'bg-[#EEF2FF] border-[#C7D2FE]' : 'bg-red-50 border-red-200'}`}>
                      <p className={`font-bold text-sm mb-1 ${isCorrect ? 'text-[#4F46E5]' : 'text-red-600'}`}>
                        {isCorrect ? 'Correct!' : 'Not quite.'}
                      </p>
                      <p className="text-gray-600 text-sm">{currentStep.exercise.explanation}</p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )}

            {currentStep.type === 'fill-blank' && currentStep.fillBlank && (
              <div className="border-t border-gray-100 pt-6 mt-6">
                <FillBlankExercise
                  template={currentStep.fillBlank.template}
                  answers={currentStep.fillBlank.answers}
                  hints={currentStep.fillBlank.hints}
                  explanation={currentStep.fillBlank.explanation}
                  onComplete={handleExerciseComplete}
                  onRequestHint={() => setHintsUsed((p) => p + 1)}
                />
              </div>
            )}

            {currentStep.type === 'match' && currentStep.match && (
              <div className="border-t border-gray-100 pt-6 mt-6">
                <MatchExercise
                  instruction={currentStep.match.instruction}
                  leftItems={currentStep.match.leftItems}
                  rightItems={currentStep.match.rightItems}
                  correctMatches={currentStep.match.correctMatches}
                  explanation={currentStep.match.explanation}
                  onComplete={handleExerciseComplete}
                />
              </div>
            )}

            {currentStep.type === 'predict' && currentStep.predict && (
              <div className="border-t border-gray-100 pt-6 mt-6">
                <PredictChallenge
                  pattern={currentStep.predict.pattern}
                  question={currentStep.predict.question}
                  options={currentStep.predict.options}
                  correctIndex={currentStep.predict.correctIndex}
                  explanation={currentStep.predict.explanation}
                  onComplete={handleExerciseComplete}
                />
              </div>
            )}

            {currentStep.type === 'checkpoint' && currentStep.checkpoint && (
              <div className="border-t border-gray-100 pt-6 mt-6">
                <CheckpointBoss
                  title={currentStep.checkpoint.title}
                  questions={currentStep.checkpoint.questions}
                  passThreshold={currentStep.checkpoint.passThreshold}
                  bonusXp={currentStep.checkpoint.bonusXp}
                  onComplete={handleCheckpointComplete}
                />
              </div>
            )}

            <div className="mt-6">
              {(!hasInteractiveContent) && (
                <button onClick={handleInfoContinue}
                  className="w-full py-3 bg-[#4F46E5] text-white rounded-lg font-medium hover:bg-[#4338CA] transition-all">
                  {isLastStep ? 'Complete Lesson' : 'Continue'}
                </button>
              )}

              {currentStep.type === 'question' && showFeedback && (
                <button onClick={handleNext}
                  className="w-full py-3 bg-[#4F46E5] text-white rounded-lg font-medium hover:bg-[#4338CA] transition-all">
                  {isLastStep ? 'Complete Lesson' : 'Continue'}
                </button>
              )}

              {(currentStep.type !== 'question' && currentStep.type !== 'info' && completedSteps.has(currentStep.id)) && (
                <button onClick={handleNext}
                  className="w-full py-3 bg-[#4F46E5] text-white rounded-lg font-medium hover:bg-[#4338CA] transition-all mt-3">
                  {isLastStep ? 'Complete Lesson' : 'Continue'}
                </button>
              )}

              {currentStep.type === 'checkpoint' && completedSteps.has(currentStep.id) && (
                <button onClick={handleNext}
                  className="w-full py-3 bg-[#4F46E5] text-white rounded-lg font-medium hover:bg-[#4338CA] transition-all mt-3">
                  {isLastStep ? 'Complete Lesson' : 'Continue'}
                </button>
              )}
            </div>
          </div>
        </motion.div>
      </AnimatePresence>

      <LearningAssistant lessonContext={buildLessonContext(lesson, currentStepIndex)} isOpen={showAssistant} onClose={() => setShowAssistant(false)} />
    </motion.div>
  );
}

function buildLessonContext(lesson: Lesson, currentStepIndex: number): string {
  const parts: string[] = [];
  parts.push(`Subject: ${lesson.subject}`);
  parts.push(`Topic: ${lesson.title}`);
  parts.push(`Current step: ${currentStepIndex + 1} — type: ${lesson.steps[currentStepIndex]?.type || 'info'}`);
  parts.push('');
  lesson.steps.forEach((step, idx) => {
    parts.push(`[Step ${idx + 1}/${lesson.steps.length} — ${step.type}]${idx === currentStepIndex ? ' ← CURRENT' : ''}`);
    if (step.content) parts.push(step.content);
    parts.push('');
  });
  return parts.join('\\n');
}

function renderLessonContent(content: string | undefined): React.ReactNode[] {
  if (!content) return [<p key="empty" className="text-gray-400 italic">No content available</p>];
  return content.split('\\n').map((line, idx) => {
    if (line.trim() === '') return <div key={idx} className="h-2" />;
    const numberedMatch = line.match(/^(\d+[️⃣.]?)\s*/);
    if (numberedMatch) {
      const num = numberedMatch[1];
      return <p key={idx} className="text-gray-600 pl-4 flex items-start gap-2">
        <span className="text-[#4F46E5] font-mono text-sm min-w-[24px]">{num}</span>
        <span>{line.slice(num.length).trim()}</span>
      </p>;
    }
    if (line.trimStart().startsWith('> ')) {
      return <div key={idx} className="border-l-2 border-[#4F46E5]/50 pl-4 py-2 my-2 bg-[#EEF2FF] rounded-r-lg">
        <p className="text-[#4F46E5] text-sm italic">{line.replace(/^>\s*/, '')}</p>
      </div>;
    }
    return <p key={idx} className="text-gray-600 leading-relaxed">{line}</p>;
  });
}
