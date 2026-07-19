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
  {
    id: 'SA-1',
    domain: 'Logic',
    interaction: 'mcq',
    question: 'If you rearrange the letters \"CIFAIPC\", you get the name of a:',
    options: { A: 'City', B: 'Animal', C: 'Ocean', D: 'Continent' },
    correctKey: 'A',
    explanation: 'CIFAIPC rearranges to PACIFIC — an ocean!',
  },
  {
    id: 'SA-2',
    domain: 'Math',
    interaction: 'mcq',
    question: 'What is the next number in this pattern: 2, 6, 18, 54, ?',
    options: { A: '108', B: '162', C: '72', D: '216' },
    correctKey: 'B',
    explanation: 'Each number is multiplied by 3. 54 x 3 = 162.',
  },
  {
    id: 'SA-3',
    domain: 'Science',
    interaction: 'mcq',
    question: 'Which of these is a renewable source of energy?',
    options: { A: 'Oil', B: 'Natural gas', C: 'Solar power', D: 'Coal' },
    correctKey: 'C',
    explanation: 'Solar power comes from the sun and is renewable — it won\'t run out!',
  },
  {
    id: 'SA-4',
    domain: 'Verbal',
    interaction: 'mcq',
    question: 'What does the word \"benevolent\" mean?',
    options: { A: 'Angry', B: 'Kind', C: 'Quick', D: 'Brave' },
    correctKey: 'B',
    explanation: 'Benevolent means kind, generous, and well-meaning.',
  },
  {
    id: 'SA-5',
    domain: 'Logic',
    interaction: 'mcq',
    question: 'A bat and a ball cost GHS 11 in total. The bat costs GHS 10 more than the ball. How much does the ball cost?',
    options: { A: 'GHS 1', B: 'GHS 0.50', C: 'GHS 2', D: 'GHS 1.50' },
    correctKey: 'B',
    explanation: 'If the ball costs x, the bat costs x+10. Total: x + (x+10) = 11. So 2x = 1, x = 0.50.',
  },
  {
    id: 'SA-6',
    domain: 'Interest',
    interaction: 'discover',
    question: 'Which activity sounds most interesting to you?',
    options: { A: 'Solving a challenging puzzle', B: 'Writing a creative story', C: 'Building something with my hands', D: 'Discussing ideas with others' },
    correctKey: 'A',
    explanation: 'Great! This helps Atlas understand your interests better.',
  },
  {
    id: 'SA-7',
    domain: 'Math',
    interaction: 'mcq',
    question: 'If a triangle has angles of 90\u00b0 and 45\u00b0, what is the third angle?',
    options: { A: '35\u00b0', B: '45\u00b0', C: '55\u00b0', D: '60\u00b0' },
    correctKey: 'B',
    explanation: 'Angles in a triangle add up to 180\u00b0. 180 - 90 - 45 = 45\u00b0.',
  },
  {
    id: 'SA-8',
    domain: 'Science',
    interaction: 'mcq',
    question: 'What planet is known as the Red Planet?',
    options: { A: 'Venus', B: 'Jupiter', C: 'Mars', D: 'Saturn' },
    correctKey: 'C',
    explanation: 'Mars is called the Red Planet because of its reddish appearance due to iron oxide on its surface.',
  },
  {
    id: 'SA-9',
    domain: 'Verbal',
    interaction: 'predict',
    question: 'What comes next in the sequence: \"January, March, May, ?\"',
    pattern: 'Months with 31 days, skipping one each time',
    options: { A: 'June', B: 'July', C: 'August', D: 'September' },
    correctKey: 'B',
    explanation: 'These are months with 31 days, taking every second one: January, March, May, July.',
  },
  {
    id: 'SA-10',
    domain: 'Behaviour',
    interaction: 'discover',
    question: 'When studying for a test, you usually:',
    options: { A: 'Read my notes repeatedly', B: 'Practice with questions', C: 'Study with friends', D: 'Teach someone else' },
    correctKey: 'A',
    explanation: 'Everyone has a unique study style! Atlas remembers this to personalise your journey.',
  },
  {
    id: 'SA-11',
    domain: 'Math',
    interaction: 'fill-blank',
    question: 'Fill in the missing number: 4, 9, 16, 25, __, 49',
    answers: ['36'],
    hints: ['Think of square numbers: 2x2=4, 3x3=9, 4x4=16...'],
    explanation: 'These are perfect squares: 2\u00b2, 3\u00b2, 4\u00b2, 5\u00b2, 6\u00b2, 7\u00b2. The missing one is 6\u00b2 = 36.',
    correctKey: 'A',
  },
  {
    id: 'SA-12',
    domain: 'Logic',
    interaction: 'fill-blank',
    question: 'Complete this analogy: \"Doctor is to hospital as teacher is to ____\"',
    answers: ['school', 'classroom'],
    hints: ['Where does a teacher work?'],
    explanation: 'A doctor works in a hospital, and a teacher works in a school (or classroom).',
    correctKey: 'A',
  },
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
