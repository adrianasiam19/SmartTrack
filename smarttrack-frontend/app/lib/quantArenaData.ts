/**
 * quantArenaData.ts
 * ───────────────────
 * SHS 1 Quantitative Sprint — 200 curriculum-aligned questions across 10 categories.
 * Used directly by the frontend arena without requiring backend connectivity.
 *
 * Covers: Fractions & Percentages, Profit/Loss/Interest, Algebra & Expressions,
 * Linear Equations, Geometry & Pythagoras, Perimeter/Area/Volume,
 * Statistics & Averages, Probability, Vectors & Trigonometry, Word Problems.
 * Aligned to Ghana GES SHS 1 Core Mathematics (Sections 2–9).
 */

import type { Question } from './challengesApi';

/** Obfuscation secret must match the backend's OBFUSCATION_SALT */
const OB_SALT = 'ST_SEC_2024';

function hash(answerKey: string): string {
  if (typeof btoa === 'undefined') return '';
  return btoa(`${OB_SALT}:${answerKey}`);
}

export interface RawQuantQuestion {
  id: string;
  category: string;
  mission_title: string;
  question: string;
  options: [string, string, string, string];
  answer: string;
  explanation: string;
  xp: number;
}

const RAW: RawQuantQuestion[] = [
];

// ── Helper: find which option key matches the answer text ─────────────────
function findAnswerKey(raw: RawQuantQuestion): string {
  const keys = ['A', 'B', 'C', 'D'];
  for (let i = 0; i < raw.options.length; i++) {
    if (raw.options[i] === raw.answer) return keys[i];
  }
  return 'A'; // fallback (should never happen)
}

// ── Build the full typed question bank ─────────────────────────────────────
export const QUANT_ARENA_QUESTIONS: Question[] = RAW.map((raw, idx) => {
  const correctKey = findAnswerKey(raw);
  return {
    id: idx + 1,
    domain: 'Math',
    question: raw.question,
    options: { A: raw.options[0], B: raw.options[1], C: raw.options[2], D: raw.options[3] },
    answer_hash: hash(correctKey),
    _category: raw.category,
    _mission: raw.mission_title,
    _explanation: raw.explanation,
    _xp: raw.xp,
  };
});

// ── Get a random subset of questions (shuffled) ────────────────────────────
export function getRandomQuantQuestions(count: number): Question[] {
  const shuffled = [...QUANT_ARENA_QUESTIONS].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, Math.min(count, shuffled.length));
}

// ── Get questions by category ──────────────────────────────────────────────
export function getQuantQuestionsByCategory(category: string): Question[] {
  return QUANT_ARENA_QUESTIONS.filter((q: any) => q._category === category);
}

// ── Get question IDs already used (for dedup) ──────────────────────────────
export const QUANT_QUESTION_IDS = new Set(QUANT_ARENA_QUESTIONS.map((q) => q.id));
