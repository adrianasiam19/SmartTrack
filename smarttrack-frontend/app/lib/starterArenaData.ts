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
  // ── 1. PREDICT: Pattern recognition (visual) ──────────────────────
  {
    id: 'SA-001',
    domain: 'Logic',
    interaction: 'predict',
    question: 'What number completes this pattern?',
    pattern: '2  →  4  →  8  →  16  →  ___',
    options: { A: '18', B: '24', C: '32', D: '30' },
    correctKey: 'C',
    explanation: 'Each number doubles the previous one! 2×2=4, 4×2=8, 8×2=16, 16×2=32. You spotted the pattern! 🎯',
  },
  // ── 2. FILL-BLANK: Number sense ───────────────────────────────────
  {
    id: 'SA-002',
    domain: 'Math',
    interaction: 'fill-blank',
    question: 'Complete this sequence: 5, 10, 15, 20, ___',
    answers: ['25'],
    hints: ['What number comes after 20 if you keep adding 5?'],
    explanation: 'Each number increases by 5. 20 + 5 = 25. Simple and steady! ✨',
  },
  // ── 3. MCQ: Reasoning ─────────────────────────────────────────────
  {
    id: 'SA-003',
    domain: 'Logic',
    interaction: 'mcq',
    question: 'If all BLOOPs are RAZZies and all RAZZies are LAZZies, are all BLOOPs LAZZies?',
    options: { A: 'Yes, definitely', B: 'No, definitely not', C: 'We cannot know for sure', D: 'Only some of them' },
    correctKey: 'A',
    explanation: 'Yes! If BLOOPs are inside RAZZies, and RAZZies are inside LAZZies, then BLOOPs must be inside LAZZies. Like nesting dolls! 🪆',
  },
  // ── 4. PREDICT: Visual shape pattern ──────────────────────────────
  {
    id: 'SA-004',
    domain: 'Logic',
    interaction: 'predict',
    question: 'What comes next in this shape pattern?',
    pattern: '△  →  ○  →  □  →  △  →  ○  →  ___',
    options: { A: '△', B: '○', C: '□', D: '☆' },
    correctKey: 'C',
    explanation: 'The shapes cycle in a repeated order: triangle → circle → square → repeat! The square comes next. 🔄',
  },
  // ── 5. SCENARIO: Scientific thinking ──────────────────────────────
  {
    id: 'SA-005',
    domain: 'Science',
    interaction: 'scenario',
    question: 'A plant in a dark room grows tall and thin, while its twin in sunlight grows short and bushy. What do you think is happening?',
    options: {
      A: 'The dark room plant is sick',
      B: 'The plant is stretching to find light — it needs sunlight to grow strong',
      C: 'The soil must be different',
      D: 'The dark room is warmer',
    },
    correctKey: 'B',
    allowMultiple: false,
    explanation: 'Plants stretch toward light! Without enough light, they grow tall and thin trying to find it. This is called etiolation. Nature is clever! 🌱',
  },
  // ── 6. MATCH: Vocabulary/analogy ──────────────────────────────────
  {
    id: 'SA-006',
    domain: 'Verbal',
    interaction: 'match',
    question: 'Match each tool to what it measures:',
    leftItems: ['Thermometer', 'Clock', 'Ruler', 'Scale'],
    rightItems: ['Time', 'Temperature', 'Weight', 'Length'],
    correctMatches: [1, 0, 3, 2], // thermometer→temp(1), clock→time(0), ruler→length(3), scale→weight(2)
    explanation: 'Each tool has its own job: thermometer measures temperature, clock measures time, ruler measures length, scale measures weight. Nice matching! 🎯',
  },
  // ── 7. DISCOVER: Preference discovery ─────────────────────────────────
  {
    id: 'SA-007',
    domain: 'Interest',
    interaction: 'discover',
    question: 'Which of these sounds most interesting to you?',
    options: { A: 'Solving puzzles and cracking codes', B: 'Reading stories and writing', C: 'Building things and tinkering', D: 'Helping others and teaching' },
    correctKey: 'A',
    explanation: 'Thanks for sharing! Your interests help Atlas understand what you naturally enjoy. No wrong answers here — every path leads to discovery! 🌟',
  },
  // ── 8. MCQ: Quantitative reasoning ────────────────────────────────
  {
    id: 'SA-008',
    domain: 'Math',
    interaction: 'mcq',
    question: 'A pizza is cut into 8 equal slices. You eat 3 slices. What fraction of the pizza is left?',
    options: { A: '3/8', B: '5/8', C: '1/2', D: '3/5' },
    correctKey: 'B',
    explanation: '8 slices total − 3 eaten = 5 slices left. That is 5/8 of the pizza. Still plenty! 🍕',
  },
  // ── 9. FILL-BLANK: Word completion ────────────────────────────────
  {
    id: 'SA-009',
    domain: 'Verbal',
    interaction: 'fill-blank',
    question: 'Complete the word: "The opposite of happy is ___"',
    answers: ['sad', 'unhappy'],
    hints: ['Think about words that mean the opposite of feeling good'],
    explanation: '"Sad" or "unhappy" are opposites of happy. These are called antonyms! 📖',
  },
  // ── 10. PREDICT: Alphabet pattern ─────────────────────────────────
  {
    id: 'SA-010',
    domain: 'Logic',
    interaction: 'predict',
    question: 'Can you spot the pattern in these letters?',
    pattern: 'A  →  C  →  F  →  J  →  O  →  ___',
    options: { A: 'R', B: 'S', C: 'T', D: 'U' },
    correctKey: 'D',
    explanation: 'The gaps between letters grow: +2, +3, +4, +5, +6. A(1)→C(3)→F(6)→J(10)→O(15)→U(21). Brilliant! 🧩',
  },
  // ── 11. MCQ: Scientific observation ───────────────────────────────
  {
    id: 'SA-011',
    domain: 'Science',
    interaction: 'mcq',
    question: 'Why does an ice cube float in water instead of sinking?',
    options: {
      A: 'Ice is lighter because it has air in it',
      B: 'Water expands when it freezes, making ice less dense than liquid water',
      C: 'The cold water pushes the ice up',
      D: 'Ice is actually heavier — it just looks like it floats',
    },
    correctKey: 'B',
    explanation: 'Water is unusual! When it freezes, it expands and becomes less dense. That is why ice floats — and why fish can survive under frozen ponds! 🐟',
  },
  // ── 12. MATCH: Science concepts ───────────────────────────────────
  {
    id: 'SA-012',
    domain: 'Science',
    interaction: 'match',
    question: 'Match each process to what it needs:',
    leftItems: ['Photosynthesis', 'Burning', 'Digestion', 'Melting'],
    rightItems: ['Sunlight', 'Fire/combustion', 'Thermal energy', 'Enzymes'],
    correctMatches: [0, 1, 3, 2], // photo→sunlight(0), burn→fire/combustion(1), digest→enzymes(3), melt→thermal energy(2)
    explanation: 'Photosynthesis needs sunlight, burning needs fire, digestion needs enzymes, melting needs thermal energy. You are connecting the dots! 🔗',
  },
  // ── 13. DISCOVER: Click to reveal ─────────────────────────────────
  {
    id: 'SA-013',
    domain: 'Interest',
    interaction: 'discover',
    question: 'Tap to discover what your learning style says about you!',
    pattern: '✨ Click to reveal ✨',
    options: {
      A: 'I learn best by doing and experimenting',
      B: 'I learn best by reading and taking notes',
      C: 'I learn best by discussing with others',
      D: 'I learn best by watching demonstrations',
    },
    correctKey: 'A', // No right/wrong — just preference
    explanation: 'Knowing your learning style helps Atlas tailor explanations just for you. Every style is valid! 🌈',
  },
  // ── 14. MCQ: Critical thinking ────────────────────────────────────
  {
    id: 'SA-014',
    domain: 'Logic',
    interaction: 'mcq',
    question: 'A shopkeeper says: "Buy one, get one free!" You buy 3 items. How many do you get in total?',
    options: { A: '3', B: '4', C: '5', D: '6' },
    correctKey: 'D',
    explanation: 'Buy one → get one free (2 total). Buy another one → get another free (2 more). Total: 3 paid + 3 free = 6 items! Nice deal! 🛍️',
  },
  // ── 15. FILL-BLANK: Number pattern ────────────────────────────────
  {
    id: 'SA-015',
    domain: 'Math',
    interaction: 'fill-blank',
    question: 'Complete: 1, 1, 2, 3, 5, 8, ___',
    answers: ['13'],
    hints: ['Each number is the sum of the two numbers before it', '5 + 8 = ?'],
    explanation: 'This is the famous Fibonacci sequence! Each number adds the two before it. 5 + 8 = 13. Nature loves this pattern! 🌻',
  },
  // ── 16. SCENARIO: Decision-making ─────────────────────────────────
  {
    id: 'SA-016',
    domain: 'Behaviour',
    interaction: 'scenario',
    question: 'Your friend is stuck on a maths problem and asks for help — but you have your own homework due tomorrow. What do you do?',
    options: {
      A: 'Help them now, even if my homework is late',
      B: 'Explain that I have my own deadline, but offer to help right after',
      C: 'Tell them to figure it out themselves',
      D: 'Give them the answer quickly so I can get back to my work',
    },
    correctKey: 'B',
    allowMultiple: false,
    explanation: 'That is a thoughtful choice! Balancing kindness with responsibility is a key life skill. Atlas notices these strengths! 🌟',
  },
  // ── 17. PREDICT: Visual pattern ───────────────────────────────────
  {
    id: 'SA-017',
    domain: 'Logic',
    interaction: 'predict',
    question: 'What is the next in this colour pattern?',
    pattern: '🔴  →  🔵  →  🟢  →  🔴  →  🔵  →  ___',
    options: { A: '🔴', B: '🔵', C: '🟢', D: '🟡' },
    correctKey: 'C',
    explanation: 'The colours cycle: red → blue → green → repeat! Green comes next. Patterns are everywhere! 🎨',
  },
  // ── 18. MCQ: Verbal reasoning ─────────────────────────────────────
  {
    id: 'SA-018',
    domain: 'Verbal',
    interaction: 'mcq',
    question: '"Eloquent" means:',
    options: { A: 'Confusing and hard to follow', B: 'Fluent and persuasive in speech', C: 'Quiet and shy', D: 'Extremely loud' },
    correctKey: 'B',
    explanation: 'Eloquent means expressing yourself clearly, smoothly, and persuasively. A great skill to develop! 🎤',
  },
  // ── 19. DISCOVER: Study preference ────────────────────────────────────
  {
    id: 'SA-019',
    domain: 'Interest',
    interaction: 'discover',
    question: 'Which study method helps you learn best?',
    options: { A: 'Doing practice questions and exercises', B: 'Watching video demonstrations', C: 'Reading notes and textbooks', D: 'Studying in a group with friends' },
    correctKey: 'A',
    explanation: 'Your study preferences help Atlas suggest the best learning content style for you! 📚',
  },
  // ── 20. FILL-BLANK: Scientific term ───────────────────────────────
  {
    id: 'SA-020',
    domain: 'Science',
    interaction: 'fill-blank',
    question: 'The process by which plants make their own food using sunlight is called ________.',
    answers: ['photosynthesis'],
    hints: ['It starts with "photo" (meaning light)'],
    explanation: 'Photosynthesis! Plants use sunlight + water + carbon dioxide to make their food and release oxygen. They are nature\'s solar panels! 🌿',
  },
  // ── 21. MCQ: Quantitative ─────────────────────────────────────────
  {
    id: 'SA-021',
    domain: 'Math',
    interaction: 'mcq',
    question: 'A shirt costs GH₵80. It is on sale at 25% off. What is the sale price?',
    options: { A: 'GH₵55', B: 'GH₵60', C: 'GH₵65', D: 'GH₵70' },
    correctKey: 'B',
    explanation: '25% of 80 = GH₵20 off. 80 − 20 = GH₵60. You saved GH₵20! 🛒',
  },
  // ── 22. DISCOVER: Career interest ─────────────────────────────────
  {
    id: 'SA-022',
    domain: 'Interest',
    interaction: 'discover',
    question: 'Tap to discover which career fields might match your interests!',
    pattern: '🔍 Tap to see your match!',
    options: {
      A: '🧪 Science & Technology — I love discovering how things work',
      B: '🎨 Arts & Creativity — I enjoy expressing ideas and stories',
      C: '📊 Business & Leadership — I like organising and managing',
      D: '🤝 People & Service — I enjoy helping and teaching others',
    },
    correctKey: 'A',
    explanation: 'Each path leads to amazing opportunities! Atlas will use your interests to recommend programmes that fit you. 🚀',
  },
  // ── 23. MCQ: Scientific thinking ──────────────────────────────────
  {
    id: 'SA-023',
    domain: 'Science',
    interaction: 'mcq',
    question: 'A magnet attracts a paperclip through a piece of paper. What does this tell us about magnetic force?',
    options: {
      A: 'Magnetic force can pass through some materials',
      B: 'The paper is actually magnetic too',
      C: 'The paperclip is pretending to be attracted',
      D: 'The magnet only works on Tuesdays',
    },
    correctKey: 'A',
    explanation: 'Magnetic force can pass through non-magnetic materials like paper, plastic, and even your hand! Try it yourself! 🧲',
  },
  // ── 24. MCQ: Communication ────────────────────────────────────────
  {
    id: 'SA-024',
    domain: 'Verbal',
    interaction: 'mcq',
    question: 'Which of these is a FACT (not an opinion)?',
    options: {
      A: 'Chocolate ice cream is the best flavour',
      B: 'Water boils at 100°C at sea level',
      C: 'Mathematics is too difficult',
      D: 'Everyone should exercise daily',
    },
    correctKey: 'B',
    explanation: 'Water\'s boiling point is a scientific fact that can be measured and verified. The others are opinions — they depend on personal feelings. 🔬',
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
