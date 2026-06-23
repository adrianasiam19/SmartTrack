'use client';

import { useMemo } from 'react';
import { motion } from 'framer-motion';
import type { Unit, Lesson } from '../lib/learningContent';

interface LearningPathTreeProps {
  units: Unit[];
  lessons: Lesson[];
  completedLessons: Set<string>;
  activeLessonId: string | null;
  onSelectLesson: (lessonId: string) => void;
  programme: string | null;
}

export default function LearningPathTree({
  units,
  lessons,
  completedLessons,
  activeLessonId,
  onSelectLesson,
  programme,
}: LearningPathTreeProps) {
  const lessonMap = useMemo(() => {
    const map = new Map<string, Lesson>();
    lessons.forEach((l) => map.set(l.id, l));
    return map;
  }, [lessons]);

  const isLessonUnlocked = (lesson: Lesson): boolean => {
    if (lesson.prerequisites.length === 0) return true;
    return lesson.prerequisites.every((preId) => completedLessons.has(preId));
  };

  const totalXp = useMemo(
    () => lessons.reduce((sum, l) => sum + l.xpReward, 0),
    [lessons]
  );
  const earnedXp = useMemo(
    () =>
      lessons
        .filter((l) => completedLessons.has(l.id))
        .reduce((sum, l) => sum + l.xpReward, 0),
    [lessons, completedLessons]
  );

  if (units.length === 0) {
    return (
      <div className="text-center py-16">
        <p className="text-gray-400 text-lg">No learning content available yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-12">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h2 className="text-2xl font-bold text-[#1E293B] mb-2">
          {programme || 'Your'} Learning Path
        </h2>
        <p className="text-gray-400 text-sm">
          {earnedXp} / {totalXp} XP earned · {completedLessons.size} / {lessons.length} lessons
        </p>
        <div className="w-full max-w-md mx-auto mt-3 bg-gray-100 rounded-full h-2 overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-[#4F46E5] to-[#D97706] rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${lessons.length > 0 ? (completedLessons.size / lessons.length) * 100 : 0}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          />
        </div>
      </motion.div>

      {units.map((unit, unitIdx) => {
        const unitLessons = lessons.filter((l) => l.unitId === unit.id);
        const completedInUnit = unitLessons.filter((l) => completedLessons.has(l.id)).length;

        if (unitLessons.length === 0) return null;

        return (
          <motion.div
            key={unit.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: unitIdx * 0.1 }}
          >
            <div className="bg-white border border-gray-200 rounded-2xl p-5 mb-5">
              <div className="flex items-center gap-3">
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-bold text-[#1E293B]">{unit.title}</h3>
                  <p className="text-sm text-gray-500">{unit.subtitle}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold text-[#4F46E5]">
                    {completedInUnit}/{unitLessons.length}
                  </p>
                  <p className="text-xs text-gray-500">lessons</p>
                </div>
              </div>
              <div className="mt-3 w-full bg-gray-100 rounded-full h-1 overflow-hidden">
                <motion.div
                  className="h-full bg-[#4F46E5] rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${(completedInUnit / unitLessons.length) * 100}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            </div>

            <div className="relative pl-8">
              <div className="absolute left-[15px] top-0 bottom-0 w-0.5 bg-gray-200" />

              <div className="space-y-4">
                {unitLessons.map((lesson, lessonIdx) => {
                  const isCompleted = completedLessons.has(lesson.id);
                  const isActive = activeLessonId === lesson.id;
                  const unlocked = isLessonUnlocked(lesson);
                  const isLocked = !unlocked && !isCompleted;

                  return (
                    <motion.div
                      key={lesson.id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: (unitIdx * 0.1) + (lessonIdx * 0.05) }}
                      className="relative"
                    >
                      <div className="absolute -left-8 top-1/2 -translate-y-1/2 z-10">
                        {isCompleted ? (
                          <div className="w-[30px] h-[30px] bg-[#4F46E5] rounded-full flex items-center justify-center">
                            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" /></svg>
                          </div>
                        ) : isActive ? (
                          <div className="w-[30px] h-[30px] bg-[#EEF2FF] border-2 border-[#4F46E5] rounded-full flex items-center justify-center">
                            <div className="w-3 h-3 bg-[#4F46E5] rounded-full" />
                          </div>
                        ) : isLocked ? (
                          <div className="w-[30px] h-[30px] bg-gray-100 border border-gray-300 rounded-full flex items-center justify-center">
                            <span className="text-xs font-bold text-gray-400">!</span>
                          </div>
                        ) : (
                          <div className="w-[30px] h-[30px] bg-gray-100 border border-gray-300 rounded-full flex items-center justify-center hover:bg-gray-200 transition-colors cursor-pointer"
                            onClick={() => onSelectLesson(lesson.id)}
                          >
                            <div className="w-2.5 h-2.5 bg-gray-400 rounded-full" />
                          </div>
                        )}
                      </div>

                      <button
                        onClick={() => {
                          if (!isLocked) onSelectLesson(lesson.id);
                        }}
                        disabled={isLocked}
                        className={`w-full text-left p-4 rounded-xl border transition-all duration-200 ${
                          isCompleted
                            ? 'bg-[#EEF2FF] border-[#C7D2FE] opacity-80'
                            : isActive
                            ? 'bg-[#EEF2FF] border-[#4F46E5] shadow-sm'
                            : isLocked
                            ? 'bg-gray-50 border-gray-200 opacity-40 cursor-not-allowed'
                            : 'bg-white border-gray-200 hover:bg-gray-50 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-center justify-between gap-3">
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center gap-2 mb-0.5">
                              <span className={`text-xs font-bold uppercase tracking-wider ${
                                isCompleted || isActive ? 'text-[#4F46E5]' : 'text-gray-500'
                              }`}>
                                {lesson.subject}
                              </span>
                              {isCompleted && (
                                <span className="text-xs text-[#4F46E5]">Done</span>
                              )}
                            </div>
                            <p className={`font-semibold truncate ${
                              isActive || isCompleted ? 'text-[#1E293B]' : 'text-gray-500'
                            }`}>
                              {lesson.title}
                            </p>

                            <div className="flex items-center gap-1 mt-1">
                              {Array.from({ length: 5 }).map((_, d) => (
                                <div
                                  key={d}
                                  className={`w-1.5 h-1.5 rounded-full ${
                                    d < lesson.difficulty ? 'bg-[#4F46E5]/70' : 'bg-gray-300'
                                  }`}
                                />
                              ))}
                            </div>
                          </div>

                          <div className="text-right flex-shrink-0">
                            <div className="flex items-center gap-1 justify-end">
                              <span className={`text-sm font-bold ${
                                isCompleted ? 'text-[#4F46E5]' : 'text-gray-500'
                              }`}>
                                {lesson.xpReward} XP
                              </span>
                            </div>
                            <div className="text-xs text-gray-400 mt-0.5">
                              {lesson.estimatedMinutes} min
                            </div>
                          </div>
                        </div>
                      </button>
                    </motion.div>
                  );
                })}
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
