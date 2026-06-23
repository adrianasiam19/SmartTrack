"""
Fix TypeScript errors in learningContent.ts:
1. Add Unit interface (after Lesson interface)
2. Add MathVizConfig type
3. Fix MatchExercise.correctMatches (MatchPair[] -> number[])
4. Fix getLessonsByProgramme to return Unit[] with proper metadata
"""
import sys

with open('app/lib/learningContent.ts', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Unit interface after the closing of Lesson interface (after the last })
# Find the end of the Lesson interface
lesson_end = content.find('}\n', content.find('  checkpoints?: CheckpointConfig[];'))
if lesson_end > 0:
    # Find the next blank line after Lesson interface
    unit_interface = """

export interface Unit {
  id: string;
  title: string;
  subtitle: string;
  colour: string;
  icon: string;
}

export type MathVizConfig = {
  type: 'number-line' | 'bar-chart' | 'coordinate-plane' | 'venn-diagram' | 'tree-diagram' | 'punnett-square' | 'fraction-pie';
  data?: number[];
  range?: { min: number; max: number };
  width?: number;
  height?: number;
  labels?: string[];
  [key: string]: unknown;
};

"""
    insert_pos = content.find('\n\n// ── Lesson data', lesson_end)
    if insert_pos == -1:
        # Fallback: find two blank lines after Lesson interface
        insert_pos = lesson_end + 1
        while insert_pos < len(content) and content[insert_pos] in ' \r\n':
            insert_pos += 1
    
    content = content[:insert_pos] + '\n' + unit_interface + content[insert_pos:]
    print('1. Added Unit interface and MathVizConfig type')
else:
    print('ERROR: Could not find Lesson interface end')

# 2. Fix MatchExercise.correctMatches type (MatchPair[] -> number[])
old_match = 'export interface MatchExercise {\n  instruction: string;\n  leftItems: string[];\n  rightItems: string[];\n  correctMatches: MatchPair[];'
new_match = 'export interface MatchExercise {\n  instruction: string;\n  leftItems: string[];\n  rightItems: string[];\n  correctMatches: number[];'
if old_match in content:
    content = content.replace(old_match, new_match)
    print('2. Fixed MatchExercise.correctMatches type')
else:
    print('ERROR: Could not find MatchExercise interface')

# 3. Fix getLessonsByProgramme to return Unit[] with proper objects
old_func = """export function getLessonsByProgramme(programme: string | 'Science' | 'Arts' | null, shsLevel: string | null): { units: string[]; lessons: Lesson[] } {
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
}"""

new_func = """const UNIT_MAP: Record<string, Unit> = {
  'core-maths': {
    id: 'core-maths',
    title: 'Core Mathematics',
    subtitle: 'Number & Algebra, Geometry, Statistics',
    colour: 'from-blue-500/20 via-purple-500/20 to-indigo-500/20',
    icon: '📐',
  },
  'core-english': {
    id: 'core-english',
    title: 'Core English',
    subtitle: 'Comprehension, Grammar & Literature',
    colour: 'from-emerald-500/20 via-teal-500/20 to-cyan-500/20',
    icon: '📖',
  },
  'integrated-science': {
    id: 'integrated-science',
    title: 'Integrated Science',
    subtitle: 'Biology, Chemistry & Physics',
    colour: 'from-green-500/20 via-lime-500/20 to-yellow-500/20',
    icon: '🔬',
  },
  'social-studies': {
    id: 'social-studies',
    title: 'Social Studies',
    subtitle: 'History, Geography & Governance',
    colour: 'from-orange-500/20 via-amber-500/20 to-yellow-500/20',
    icon: '🌍',
  },
};

export function getLessonsByProgramme(programme: string | 'Science' | 'Arts' | null, shsLevel: string | null): { units: Unit[]; lessons: Lesson[] } {
  if (!programme || !shsLevel) {
    return { units: [], lessons: [] };
  }

  // Filter lessons by programme and shs level
  const filteredLessons = ALL_LESSONS.filter(
    (lesson) =>
      (lesson.programme === programme || lesson.programme === 'Both') &&
      lesson.shsLevels.includes(shsLevel)
  );

  // Get unique units from filtered lessons and map to Unit objects
  const uniqueIds = Array.from(new Set(filteredLessons.map((lesson) => lesson.unitId)));
  const units: Unit[] = uniqueIds
    .map((id) => UNIT_MAP[id])
    .filter((u): u is Unit => u !== undefined);

  return { units, lessons: filteredLessons };
}"""

if old_func in content:
    content = content.replace(old_func, new_func)
    print('3. Fixed getLessonsByProgramme to return Unit[]')
else:
    print('ERROR: Could not find getLessonsByProgramme function - trying fuzzy match')
    # Try to find any version of the function
    import re
    match = re.search(r'export function getLessonsByProgramme.*?return \{ units.*?\}', content, re.DOTALL)
    if match:
        print(f'  Found function at position {match.start()}')
        content = content[:match.start()] + new_func + content[match.end():]
        print('  Replaced via regex')

with open('app/lib/learningContent.ts', 'w', encoding='utf-8') as f:
    f.write(content)

print('\\nDone! File updated.')
