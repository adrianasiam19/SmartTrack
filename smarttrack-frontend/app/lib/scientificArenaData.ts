/**
 * scientificArenaData.ts
 * -----------------------
 * SHS 3 Scientific Thinking Arena - 200 curriculum-aligned questions.
 * Used directly by the frontend arena without requiring backend connectivity.
 *
 * Covers 9 categories aligned to Ghana GES SHS 3 General Science:
 * Chemical Bonding & Reactions, Consumer Electronics & Digital Systems,
 * Energy & Environment, Forces, Pressure & Machines, Genetics & Heredity,
 * Human Body & Health, Industrial Chemistry & Biotechnology,
 * Science, Technology & Society, Waves, Light & Sound.
 */

import type { Question } from './challengesApi';

/** Obfuscation secret must match the backend */
const OB_SALT = 'ST_SEC_2024';

function hash(answerKey: string): string {
  if (typeof btoa === 'undefined') return '';
  return btoa(`${OB_SALT}:${answerKey}`);
}

// ── Raw Question Data ────────────────────────────────────────────
interface RawScientificQuestion {
  id: string;
  category: string;
  mission_title: string;
  question: string;
  options: [string, string, string, string];
  answer: string;
  explanation: string;
  xp: number;
}

const RAW: RawScientificQuestion[] = [
];

// ── Helper: find which option key matches the answer text ─────────────────
function findAnswerKey(raw: RawScientificQuestion): string {
  const keys = ['A', 'B', 'C', 'D'];
  for (let i = 0; i < raw.options.length; i++) {
    if (raw.options[i] === raw.answer) return keys[i];
  }
  return 'A'; // fallback (should never happen)
}

// ── Build the full typed question bank ─────────────────────────────────────
export const SCIENTIFIC_ARENA_QUESTIONS: Question[] = RAW.map((raw, idx) => {
  const correctKey = findAnswerKey(raw);
  return {
    id: idx + 1,
    domain: 'Science',
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
export function getRandomScientificQuestions(count: number): Question[] {
  const shuffled = [...SCIENTIFIC_ARENA_QUESTIONS].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, Math.min(count, shuffled.length));
}

// ── Get questions by category ──────────────────────────────────────────────
export function getScientificQuestionsByCategory(category: string): Question[] {
  return SCIENTIFIC_ARENA_QUESTIONS.filter((q: any) => q._category === category);
}

// ── Get question IDs already used (for dedup) ──────────────────────────────
export const SCIENTIFIC_QUESTION_IDS = new Set(SCIENTIFIC_ARENA_QUESTIONS.map((q) => q.id));
