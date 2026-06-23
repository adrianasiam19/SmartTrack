/**
 * adaptiveEngine.ts
 * ──────────────────
 * Core adaptation logic for the Atlas adaptive learning system.
 * Maps SHS programme + level to learning zones, stages, challenge filters,
 * and progression paths, ensuring every student gets a personalised journey.
 */

import type { UserProfile } from './authApi';
import type { ChallengeCategory } from './challengesApi';
import type { Lesson, Unit } from './learningContent';

// ── Supported SHS Levels ──────────────────────────────────────────────────
export type SHSLevel = 'SHS 1' | 'SHS 2' | 'SHS 3';

// ── Learning Stages ───────────────────────────────────────────────────────
export interface LearningStage {
  id: string;
  title: string;
  subtitle: string;
  icon: string;
  colour: string;
  description: string;
}

export const STAGES: Record<string, LearningStage> = {
  'General Science+SHS 1': {
    id: 'foundation-scientist',
    title: 'Foundation Scientist',
    subtitle: 'Building scientific fundamentals',
    icon: '🔬',
    colour: 'from-indigo-500/20 to-purple-500/20',
    description: 'Foundational scientific reasoning, beginner quantitative thinking, and introductory analytical logic.',
  },
  'General Science+SHS 2': {
    id: 'experimental-researcher',
    title: 'Experimental Researcher',
    subtitle: 'Broadening scientific reasoning',
    icon: '🧪',
    colour: 'from-cyan-500/20 to-blue-500/20',
    description: 'Intermediate scientific analysis, deeper experimental reasoning, and data interpretation.',
  },
  'General Science+SHS 3': {
    id: 'waec-scientist',
    title: 'WAEC Analyst',
    subtitle: 'Mastering exam-level science',
    icon: '📊',
    colour: 'from-violet-500/20 to-purple-500/20',
    description: 'Advanced scientific analysis, WAEC-standard problem solving, and complex quantitative reasoning.',
  },
  'General Arts+SHS 1': {
    id: 'discovery-learner',
    title: 'Discovery Learner',
    subtitle: 'Exploring the world of ideas',
    icon: '📖',
    colour: 'from-amber-500/20 to-orange-500/20',
    description: 'Introductory verbal reasoning, communication basics, and beginner critical thinking.',
  },
  'General Arts+SHS 2': {
    id: 'critical-interpreter',
    title: 'Critical Interpreter',
    subtitle: 'Deepening analytical skills',
    icon: '🎭',
    colour: 'from-rose-500/20 to-pink-500/20',
    description: 'Intermediate analysis and argumentation, real-world context interpretation, and literary exploration.',
  },
  'General Arts+SHS 3': {
    id: 'mastery-analyst',
    title: 'Mastery Analyst',
    subtitle: 'Achieving WAEC excellence',
    icon: '🏛️',
    colour: 'from-purple-500/20 to-violet-500/20',
    description: 'Advanced verbal analysis, argumentative reasoning, and deeper real-world interpretation.',
  },
};

// ── Learning Zones (Programme + SHS Level combinations) ───────────────────
export interface LearningZone {
  id: string;
  title: string;
  description: string;
  icon: string;
  colour: string;
  programme: 'General Science' | 'General Arts';
  shsLevel: SHSLevel;
  /** Domain slugs this zone covers */
  domains: string[];
  /** Challenge category IDs relevant to this zone */
  challengeCategoryIds: string[];
  /** Lesson unit IDs relevant to this zone */
  unitIds: string[];
  /** XP required to complete this zone */
  xpRequired: number;
  /** Recommended next zone (if any) */
  nextZoneId?: string;
}

export const LEARNING_ZONES: LearningZone[] = [
  // ── General Science Zones ──
  {
    id: 'science-foundation-lab',
    title: 'Foundation Lab',
    description: 'Build your scientific foundations with core concepts in physics, chemistry, and biology.',
    icon: '🔬',
    colour: 'from-lime-500/20 to-emerald-500/20',
    programme: 'General Science',
    shsLevel: 'SHS 1',
    domains: ['Logic', 'Science', 'Math'],
    challengeCategoryIds: ['logic-arena', 'scientific-thinking', 'quantitative-sprint'],
    unitIds: ['physics', 'chemistry', 'biology', 'elective-math', 'core-maths', 'english-language', 'general-science'],
    xpRequired: 200,
    nextZoneId: 'science-intermediate-lab',
  },
  {
    id: 'science-intermediate-lab',
    title: 'Intermediate Lab',
    description: 'Deepen your understanding with experimental reasoning and broader scientific challenges.',
    icon: '🧪',
    colour: 'from-cyan-500/20 to-blue-500/20',
    programme: 'General Science',
    shsLevel: 'SHS 2',
    domains: ['Science', 'Analytical', 'Logic'],
    challengeCategoryIds: ['scientific-thinking', 'analytical-challenges', 'logic-arena'],
    unitIds: ['physics', 'chemistry', 'biology', 'elective-math', 'core-maths', 'english-language', 'general-science'],
    xpRequired: 500,
    nextZoneId: 'science-advanced-lab',
  },
  {
    id: 'science-advanced-lab',
    title: 'Advanced Lab',
    description: 'Master WAEC-standard problems with complex scientific analysis and quantitative reasoning.',
    icon: '📊',
    colour: 'from-violet-500/20 to-purple-500/20',
    programme: 'General Science',
    shsLevel: 'SHS 3',
    domains: ['Analytical', 'Science', 'Math'],
    challengeCategoryIds: ['analytical-challenges', 'scientific-thinking', 'logic-arena'],
    unitIds: ['physics', 'chemistry', 'biology', 'elective-math', 'core-maths', 'english-language', 'general-science'],
    xpRequired: 1000,
  },
  // ── General Arts Zones ──
  {
    id: 'arts-discovery-studio',
    title: 'Discovery Studio',
    description: 'Explore the foundations of critical thinking, communication, and verbal reasoning.',
    icon: '📖',
    colour: 'from-amber-500/20 to-orange-500/20',
    programme: 'General Arts',
    shsLevel: 'SHS 1',
    domains: ['Verbal', 'Logic', 'General'],
    challengeCategoryIds: ['communication-arena', 'critical-thinking', 'verbal-challenges'],
    unitIds: ['economics', 'government', 'geography', 'literature', 'history', 'crs', 'core-maths', 'english-language'],
    xpRequired: 200,
    nextZoneId: 'arts-interpretation-studio',
  },
  {
    id: 'arts-interpretation-studio',
    title: 'Interpretation Studio',
    description: 'Develop deeper analytical skills with argumentation, real-world context, and literary exploration.',
    icon: '🎭',
    colour: 'from-rose-500/20 to-pink-500/20',
    programme: 'General Arts',
    shsLevel: 'SHS 2',
    domains: ['Logic', 'Verbal', 'General'],
    challengeCategoryIds: ['critical-thinking', 'real-world-analysis', 'verbal-challenges'],
    unitIds: ['economics', 'government', 'geography', 'literature', 'history', 'crs', 'core-maths', 'english-language'],
    xpRequired: 500,
    nextZoneId: 'arts-mastery-studio',
  },
  {
    id: 'arts-mastery-studio',
    title: 'Mastery Studio',
    description: 'Achieve WAEC excellence with advanced verbal analysis, argumentative reasoning, and real-world interpretation.',
    icon: '🏛️',
    colour: 'from-purple-500/20 to-violet-500/20',
    programme: 'General Arts',
    shsLevel: 'SHS 3',
    domains: ['Analytical', 'Verbal', 'General'],
    challengeCategoryIds: ['real-world-analysis', 'critical-thinking', 'verbal-challenges'],
    unitIds: ['economics', 'government', 'geography', 'literature', 'history', 'crs', 'core-maths', 'english-language'],
    xpRequired: 1000,
  },
];

// ── Progression Track ─────────────────────────────────────────────────────

export interface ProgressionTrack {
  currentStage: LearningStage;
  currentZone: LearningZone;
  nextZone?: LearningZone;
  /** Overall progress in current zone (0-100) */
  zoneProgress: number;
  /** Whether the student is ready to advance to the next SHS level */
  readyForNextLevel: boolean;
  /** Recommended challenge categories for this student */
  recommendedCategories: ChallengeCategory[];
}

// ── Helpers ───────────────────────────────────────────────────────────────

/**
 * Get the learning stage for a programme + SHS level combination.
 */
export function getLearningStage(programme: string | null, shsLevel: string | null): LearningStage | null {
  if (!programme || !shsLevel) return null;
  const key = `${programme}+${shsLevel}`;
  return STAGES[key] || null;
}

/**
 * Get the current learning zone for a user based on their programme + SHS level.
 */
export function getCurrentZone(programme: string | null, shsLevel: string | null): LearningZone | null {
  if (!programme || !shsLevel) return null;
  return LEARNING_ZONES.find(
    (z) => z.programme === programme && z.shsLevel === shsLevel
  ) || null;
}

/**
 * Get the next zone after the current one (progression path).
 */
export function getNextZone(zoneId: string | undefined): LearningZone | undefined {
  if (!zoneId) return undefined;
  const current = LEARNING_ZONES.find((z) => z.id === zoneId);
  if (!current?.nextZoneId) return undefined;
  return LEARNING_ZONES.find((z) => z.id === current.nextZoneId);
}

/**
 * Calculate zone progress based on XP earned relative to zone XP requirement.
 */
export function calculateZoneProgress(xp: number, zone: LearningZone): number {
  return Math.min(100, Math.round((xp / zone.xpRequired) * 100));
}

/**
 * Determine if a student is ready to advance to the next SHS level
 * based on their XP and the current zone's XP requirement.
 */
export function isReadyForNextLevel(
  xp: number,
  programme: string | null,
  shsLevel: string | null
): boolean {
  if (!programme || !shsLevel) return false;
  const zone = getCurrentZone(programme, shsLevel);
  if (!zone) return false;

  // Ready if XP is at least 150% of the zone requirement
  return xp >= zone.xpRequired * 1.5;
}

/**
 * Filter lessons by SHS level appropriateness.
 * Uses lesson difficulty mapping:
 *   SHS 1 → difficulty 1-2
 *   SHS 2 → difficulty 2-4
 *   SHS 3 → difficulty 3-5
 */
export function isLessonAppropriateForLevel(lesson: Lesson, shsLevel: string | null): boolean {
  if (!shsLevel) return true; // No level filter — show everything
  if (lesson.shsLevels && lesson.shsLevels.length > 0) {
    return lesson.shsLevels.includes(shsLevel as SHSLevel);
  }
  // Fallback: use difficulty mapping
  switch (shsLevel) {
    case 'SHS 1': return lesson.difficulty <= 2;
    case 'SHS 2': return lesson.difficulty >= 2 && lesson.difficulty <= 4;
    case 'SHS 3': return lesson.difficulty >= 3;
    default: return true;
  }
}

/**
 * Filter challenge categories by SHS level appropriateness.
 */
export function isCategoryAppropriateForLevel(
  category: ChallengeCategory,
  shsLevel: string | null
): boolean {
  if (!shsLevel) return true;
  if (category.shsLevels && category.shsLevels.length > 0) {
    return category.shsLevels.includes(shsLevel as 'SHS 1' | 'SHS 2' | 'SHS 3');
  }
  // Fallback: difficulty-based filtering
  switch (shsLevel) {
    case 'SHS 1': return category.difficulty !== 'Advanced';
    case 'SHS 2': return category.difficulty !== 'Beginner';
    case 'SHS 3': return category.difficulty !== 'Beginner';
    default: return true;
  }
}

/**
 * Get the recommended "next arena" label for the dashboard.
 */
export function getRecommendedArena(
  programme: string | null,
  shsLevel: string | null,
  xp: number,
  completedLessons: number,
  streak: number
): { label: string; icon: string; description: string } {
  if (!programme || !shsLevel) {
    return {
      label: 'Starter Arena',
      icon: '⚡',
      description: 'Set up your profile to get personalised recommendations.',
    };
  }

  const zone = getCurrentZone(programme, shsLevel);
  if (!zone) {
    return {
      label: 'Challenge Hub',
      icon: '🎯',
      description: 'Explore all available challenges.',
    };
  }

  const progress = calculateZoneProgress(xp, zone);
  const nextZone = getNextZone(zone.id);

  if (progress >= 100 && nextZone) {
    return {
      label: `${nextZone.title} ⚡`,
      icon: '🚀',
      description: `Ready for ${nextZone.title}! ${nextZone.description.slice(0, 80)}...`,
    };
  }

  if (streak >= 7 && completedLessons > 0) {
    return {
      label: `${zone.title} — Streak Booster`,
      icon: '🔥',
      description: `You're on fire with a ${streak}-day streak! Keep pushing in ${zone.title}.`,
    };
  }

  if (completedLessons === 0) {
    return {
      label: `${zone.title} 🎯`,
      icon: '🎯',
      description: `Start your ${zone.title} journey. ${zone.description.slice(0, 80)}...`,
    };
  }

  return {
    label: `${zone.title} ⚡`,
    icon: '⚡',
    description: `${progress}% through ${zone.title}. Keep learning!`,
  };
}
