/**
 * starterArenaData.ts
 * ────────────────────
 * Starter Arena — a discovery journey, NOT a test.
 *
 * Question types (question_type):
 *   mcq         Standard multiple-choice (4 options)
 *   fill-blank  Fill in missing word / number
 *   predict     Pattern prediction with "tap to reveal"
 *   match       Drag-and-drop matching pairs
 *   rank        Order items by a criterion
 *   scenario    Scenario-based decision (can select multiple)
 *   discover    Click-to-reveal discovery card
 *
 * Each question has a friendly "discovery feel" — conversational
 * wording, curiosity-driven, no exam tone.
 */

export type StarterQuestionType =
  | 'mcq'
  | 'fill-blank'
  | 'predict'
  | 'match'
  | 'rank'
  | 'scenario'
  | 'discover';

export interface StarterQuestion {
  id: string;
  /** Which ability this tests */
  domain: 'Logic' | 'Math' | 'Science' | 'Verbal' | 'Interest' | 'Behaviour';
  interaction: StarterQuestionType;
  /** Friendly, conversational question */
  question: string;
  /** Optional visual hint / pattern to show */
  pattern?: string;
  /** Options — meaning depends on interaction type */
  options?: Record<string, string>;
  /** For fill-blank: the expected answer(s) */
  answers?: string[];
  /** For match: left-side items */
  leftItems?: string[];
  /** For match: right-side items (shuffled) */
  rightItems?: string[];
  /** For match: leftIndex -> correct rightIndex */
  correctMatches?: number[];
  /** For rank: items in correct order */
  rankedOrder?: string[];
  /** Correct option key (for mcq, scenario, predict) */
  correctKey?: string;
  /** Friendly explanation shown after answering */
  explanation: string;
  /** Hints for fill-in-blank */
  hints?: string[];
  /** Support for multi-select (scenario) */
  allowMultiple?: boolean;
}

/**
 * 24 discovery questions for the Starter Arena.
 * Mix of: 8 MCQ, 4 fill-blank, 4 predict (pattern), 2 match, 2 rank, 2 scenario, 2 discover
 */
export const STARTER_ARENA_QUESTIONS: StarterQuestion[] = [
];

/** Get a random subset of Starter Arena questions (shuffled, no repeats) */
export function getRandomStarterQuestions(count: number): StarterQuestion[] {
  const shuffled = [...STARTER_ARENA_QUESTIONS].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, Math.min(count, shuffled.length));
}

/** Get questions by interaction type */
export function getStarterQuestionsByType(type: StarterQuestionType): StarterQuestion[] {
  return STARTER_ARENA_QUESTIONS.filter((q) => q.interaction === type);
}
