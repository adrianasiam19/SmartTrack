"""
Fix TypeScript errors in learningContent.ts and MathVisualizer.tsx.

Issues to fix:
1. Add missing `Unit` interface
2. Add missing `MathVizConfig` type
3. Fix `MatchExercise` interface (correctMatches: number[] instead of MatchPair[])
4. Fix `getLessonsByProgramme` to return Unit[] instead of string[]
5. Fix implicit any types in MathVisualizer.tsx
"""

import re

# ── Fix learningContent.ts ─────────────────────────────────────────────────

with open('app/lib/learningContent.ts', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Unit interface after VisualizeConfig (before LessonStep)
old = '''export interface VisualizeConfig {
  type: 'number-line' | 'venn' | 'bar-chart' | 'coordinate' | 'tree' | 'table';
  data: Record<string, unknown>;
}

export interface LessonStep {'''

new = '''export interface MathVizConfig {
  type: string;
  data: number[];
  range?: { min: number; max: number };
  width?: number;
  height?: number;
  labels?: string[];
  colour?: string;
}

export interface Unit {
  id: string;
  title: string;
  subtitle: string;
  icon: string;
  colour: string;
}

export interface VisualizeConfig {
  type: 'number-line' | 'venn' | 'bar-chart' | 'coordinate' | 'tree' | 'table';
  data: Record<string, unknown>;
}

export interface LessonStep {'''

if old in content:
    content = content.replace(old, new, 1)
    print('[OK] Added Unit and MathVizConfig interfaces')
else:
    print('[WARN] Could not find insertion point for Unit/MathVizConfig')

# 2. Fix MatchExercise interface: correctMatches: MatchPair[] -> number[]
old_match = '''export interface MatchExercise {
  instruction: string;
  leftItems: string[];
  rightItems: string[];
  correctMatches: MatchPair[];
  explanation: string;
}'''

new_match = '''export interface MatchExercise {
  instruction: string;
  leftItems: string[];
  rightItems: string[];
  correctMatches: number[];
  explanation: string;
}'''

if old_match in content:
    content = content.replace(old_match, new_match, 1)
    print('[OK] Fixed MatchExercise interface')
else:
    print('[WARN] Could not find MatchExercise interface')

# 3. Fix getLessonsByProgramme to return Unit[] instead of string[]
old_fn = '''export function getLessonsByProgramme(programme: string | 'Science' | 'Arts' | null, shsLevel: string | null): { units: string[]; lessons: Lesson[] } {
  if (!programme || !shsLevel) {
    return { units: [], lessons: [] };
  }

  // Filter lessons by programme and shs level
  const filteredLessons = ALL_LESSONS.filter(
    (lesson) =>
      (lesson.programme === programme || lesson.programme === 'Both') &&
      lesson.shsLevels.includes(shsLevel)
  );

  // Get unique units from filtered lessons
  const units = Array.from(new Set(filteredLessons.map((lesson) => lesson.unitId)));

  return { units, lessons: filteredLessons };
}'''

new_fn = '''export function getLessonsByProgramme(programme: string | 'Science' | 'Arts' | null, shsLevel: string | null): { units: Unit[]; lessons: Lesson[] } {
  if (!programme || !shsLevel) {
    return { units: [], lessons: [] };
  }

  // Filter lessons by programme and shs level
  const filteredLessons = ALL_LESSONS.filter(
    (lesson) =>
      (lesson.programme === programme || lesson.programme === 'Both') &&
      lesson.shsLevels.includes(shsLevel)
  );

  // Get unique unit IDs from filtered lessons
  const unitIds = Array.from(new Set(filteredLessons.map((lesson) => lesson.unitId)));

  // Map unit IDs to Unit objects
  const units: Unit[] = unitIds
    .map((id) => UNIT_MAP[id])
    .filter(Boolean) as Unit[];

  return { units, lessons: filteredLessons };
}

const UNIT_MAP: Record<string, Unit> = {
  'core-maths': { id: 'core-maths', title: 'Core Mathematics', subtitle: 'Essential math foundations', icon: '📐', colour: 'from-lime-500/20 to-emerald-500/20' },
  'english-language': { id: 'english-language', title: 'English Language', subtitle: 'Communication & comprehension', icon: '📝', colour: 'from-blue-500/20 to-indigo-500/20' },
  'physics': { id: 'physics', title: 'Physics', subtitle: 'Matter, energy & forces', icon: '⚛️', colour: 'from-cyan-500/20 to-sky-500/20' },
  'chemistry': { id: 'chemistry', title: 'Chemistry', subtitle: 'Elements, compounds & reactions', icon: '🧪', colour: 'from-purple-500/20 to-violet-500/20' },
  'biology': { id: 'biology', title: 'Biology', subtitle: 'Living organisms & life processes', icon: '🧬', colour: 'from-green-500/20 to-emerald-500/20' },
  'elective-math': { id: 'elective-math', title: 'Elective Mathematics', subtitle: 'Advanced mathematical concepts', icon: '📊', colour: 'from-amber-500/20 to-orange-500/20' },
  'economics': { id: 'economics', title: 'Economics', subtitle: 'Scarcity, choice & markets', icon: '📈', colour: 'from-rose-500/20 to-pink-500/20' },
  'government': { id: 'government', title: 'Government', subtitle: 'Politics & constitutional systems', icon: '🏛️', colour: 'from-red-500/20 to-rose-500/20' },
  'geography': { id: 'geography', title: 'Geography', subtitle: 'Earth, environment & mapping', icon: '🌍', colour: 'from-teal-500/20 to-cyan-500/20' },
  'literature': { id: 'literature', title: 'Literature', subtitle: 'Prose, drama & poetry', icon: '📚', colour: 'from-fuchsia-500/20 to-purple-500/20' },
  'history': { id: 'history', title: 'History', subtitle: 'Past events & civilisations', icon: '⏳', colour: 'from-amber-500/20 to-yellow-500/20' },
  'crs': { id: 'crs', title: 'Christian Religious Studies', subtitle: 'Biblical knowledge & ethics', icon: '✝️', colour: 'from-orange-500/20 to-amber-500/20' },
};'''

if old_fn in content:
    content = content.replace(old_fn, new_fn, 1)
    print('[OK] Updated getLessonsByProgramme with Unit[] return type')
else:
    print('[WARN] Could not find getLessonsByProgramme function')

with open('app/lib/learningContent.ts', 'w', encoding='utf-8') as f:
    f.write(content)

print('[OK] learningContent.ts updated')

# ── Fix MathVisualizer.tsx ─────────────────────────────────────────────────

with open('app/components/MathVisualizer.tsx', 'r', encoding='utf-8') as f:
    viz_content = f.read()

# Fix implicit any types in map callbacks
# Line 114: val and idx in data.map((val, idx) => ...)
viz_content = viz_content.replace(
    'data.map((val, idx) =>',
    'data.map((val: number, idx: number) =>'
)
viz_content = viz_content.replace(
    'labels.map((label, idx) =>',
    'labels.map((label: string, idx: number) =>'
)

# Fix outcome and idx in outcomes.map
viz_content = viz_content.replace(
    'outcomes.map((outcome, idx) =>',
    'outcomes.map((outcome: string, idx: number) =>'
)

with open('app/components/MathVisualizer.tsx', 'w', encoding='utf-8') as f:
    f.write(viz_content)

print('[OK] MathVisualizer.tsx fixed')
print()
print('Done!')
