/**
 * logicArenaData.ts
 * ──────────────────
 * SHS 3 Logic Arena — 200 NaCCA-aligned questions across 10 categories.
 * Replaces the previous SHS 1 bank. Includes interactive question types
 * (predict for pattern/sequence questions) and competitive XP/scoring.
 */

import type { Question } from './challengesApi';

const OB_SALT = 'ST_SEC_2024';

function hash(answerKey: string): string {
  if (typeof btoa === 'undefined') return '';
  return btoa(`${OB_SALT}:${answerKey}`);
}

export interface RawLogicQuestion {
  id: string;
  category: string;
  mission_title: string;
  question: string;
  options: [string, string, string, string];
  answer: string;
  explanation: string;
  xp: number;
  question_type?: 'mcq' | 'predict' | 'fill-blank' | 'match';
  pattern?: string;
  answers?: string[];
  hints?: string[];
  leftItems?: string[];
  rightItems?: string[];
  correctMatches?: number[];
}

const RAW: RawLogicQuestion[] = [
];

function findAnswerKey(raw: RawLogicQuestion): string {
  const keys = ['A', 'B', 'C', 'D'];
  for (let i = 0; i < raw.options.length; i++) {
    if (raw.options[i] === raw.answer) return keys[i];
  }
  return 'A';
}

export const LOGIC_ARENA_QUESTIONS: Question[] = RAW.map((raw, idx) => {
  const correctKey = findAnswerKey(raw);
  return {
    id: 2000 + idx + 1,
    domain: 'Logic',
    question: raw.question,
    question_type: raw.question_type || 'mcq',
    options: { A: raw.options[0], B: raw.options[1], C: raw.options[2], D: raw.options[3] },
    answer_hash: hash(correctKey),
    _category: raw.category,
    _mission: raw.mission_title,
    _explanation: raw.explanation,
    _xp: raw.xp,
    _pattern: raw.pattern,
    _answers: raw.answers,
    _hints: raw.hints,
    _leftItems: raw.leftItems,
    _rightItems: raw.rightItems,
    _correctMatches: raw.correctMatches,
  };
});

export function getRandomLogicQuestions(count: number): Question[] {
  const shuffled = [...LOGIC_ARENA_QUESTIONS].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, Math.min(count, shuffled.length));
}

export function getLogicQuestionsByCategory(category: string): Question[] {
  return LOGIC_ARENA_QUESTIONS.filter((q: any) => q._category === category);
}

export const LOGIC_QUESTION_IDS = new Set(LOGIC_ARENA_QUESTIONS.map((q) => q.id));
