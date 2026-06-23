/**
 * subjects.ts
 * ─────────────
 * Data definitions for the Daily Streak Challenge subjects.
 * To add real question content later, simply extend the `levels` array
 * with actual question objects (or import from a question bank).
 */

export type SubjectId = 'core-mathematics' | 'integrated-science' | 'english-language' | 'social-studies';

export interface Level {
  id: number;
  name: string;
  label: string; // e.g. "Foundation", "Intermediate", "Advanced"
  progress: number; // 0–100
  locked: boolean;
  xpReward: number;
}

export interface Subject {
  id: SubjectId;
  name: string;
  shortName: string;
  icon: string;
  gradient: string;
  bgGradient: string;
  borderColor: string;
  textColor: string;
  description: string;
  levels: Level[];
  /** Placeholder for future question content — extend this array when ready */
  questionPlaceholders: string[];
}

export const SUBJECTS: Subject[] = [
  {
    id: 'core-mathematics',
    name: 'Core Mathematics',
    shortName: 'Mathematics',
    icon: '∑',
    gradient: 'from-[#2563EB] to-[#3B82F6]',
    bgGradient: 'from-[#2563EB]/5 to-[#3B82F6]/5',
    borderColor: 'border-[#2563EB]/20',
    textColor: 'text-[#2563EB]',
    description: 'Build numerical reasoning, algebra, geometry, and problem-solving skills.',
    levels: [
      { id: 1, name: 'Level 1', label: 'Foundation', progress: 0, locked: false, xpReward: 100 },
      { id: 2, name: 'Level 2', label: 'Intermediate', progress: 0, locked: true, xpReward: 150 },
      { id: 3, name: 'Level 3', label: 'Advanced', progress: 0, locked: true, xpReward: 200 },
    ],
    questionPlaceholders: ['Core Mathematics → Level 1 → Questions Placeholder'],
  },
  {
    id: 'integrated-science',
    name: 'Integrated Science',
    shortName: 'Science',
    icon: '⚛',
    gradient: 'from-[#059669] to-[#34D399]',
    bgGradient: 'from-[#059669]/5 to-[#34D399]/5',
    borderColor: 'border-[#059669]/20',
    textColor: 'text-[#059669]',
    description: 'Explore biology, chemistry, physics, and scientific reasoning concepts.',
    levels: [
      { id: 1, name: 'Level 1', label: 'Foundation', progress: 0, locked: false, xpReward: 100 },
      { id: 2, name: 'Level 2', label: 'Intermediate', progress: 0, locked: true, xpReward: 150 },
      { id: 3, name: 'Level 3', label: 'Advanced', progress: 0, locked: true, xpReward: 200 },
    ],
    questionPlaceholders: ['Integrated Science → Level 1 → Questions Placeholder'],
  },
  {
    id: 'english-language',
    name: 'English Language',
    shortName: 'English',
    icon: '✎',
    gradient: 'from-[#7C3AED] to-[#8B5CF6]',
    bgGradient: 'from-[#7C3AED]/5 to-[#8B5CF6]/5',
    borderColor: 'border-[#7C3AED]/20',
    textColor: 'text-[#7C3AED]',
    description: 'Strengthen reading comprehension, grammar, writing, and verbal expression.',
    levels: [
      { id: 1, name: 'Level 1', label: 'Foundation', progress: 0, locked: false, xpReward: 100 },
      { id: 2, name: 'Level 2', label: 'Intermediate', progress: 0, locked: true, xpReward: 150 },
      { id: 3, name: 'Level 3', label: 'Advanced', progress: 0, locked: true, xpReward: 200 },
    ],
    questionPlaceholders: ['English Language → Level 1 → Questions Placeholder'],
  },
  {
    id: 'social-studies',
    name: 'Social Studies',
    shortName: 'Social Studies',
    icon: '◉',
    gradient: 'from-[#D97706] to-[#F59E0B]',
    bgGradient: 'from-[#D97706]/5 to-[#F59E0B]/5',
    borderColor: 'border-[#D97706]/20',
    textColor: 'text-[#D97706]',
    description: 'Develop understanding of history, geography, governance, and civic responsibility.',
    levels: [
      { id: 1, name: 'Level 1', label: 'Foundation', progress: 0, locked: false, xpReward: 100 },
      { id: 2, name: 'Level 2', label: 'Intermediate', progress: 0, locked: true, xpReward: 150 },
      { id: 3, name: 'Level 3', label: 'Advanced', progress: 0, locked: true, xpReward: 200 },
    ],
    questionPlaceholders: ['Social Studies → Level 1 → Questions Placeholder'],
  },
];

/** Look up a subject by its id */
export function getSubjectById(id: SubjectId): Subject | undefined {
  return SUBJECTS.find((s) => s.id === id);
}
