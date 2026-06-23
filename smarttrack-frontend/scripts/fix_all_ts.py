"""
Fix all TypeScript errors in one shot:
1. Add Unit interface + metadata to learningContent.ts
2. Add MathVizConfig type alias to learningContent.ts
3. Fix MatchExercise.correctMatches type (MatchPair[] -> number[])
4. Fix getLessonsByProgramme to return Unit[] instead of string[]
5. Fix implicit any types in MathVisualizer.tsx
"""
import re
import sys

def fix_learning_content():
    with open('app/lib/learningContent.ts', 'r', encoding='utf-8') as f:
        content = f.read()

    # --- Fix 1: MatchExercise.correctMatches type ---
    content = content.replace(
        '  correctMatches: MatchPair[];',
        '  correctMatches: number[];'
    )

    # --- Fix 2: Add Unit interface after Lesson interface ---
    # Find where the Lesson interface closes and add Unit before the comment
    lesson_end_marker = "  checkpoints?: CheckpointConfig[];\n}\n\n// ── Lesson data"
    unit_interface = """  checkpoints?: CheckpointConfig[];\n}\n\nexport interface Unit {\n  id: string;\n  title: string;\n  subtitle: string;\n  icon: string;\n  colour: string;\n}\n\nexport interface MathVizConfig {\n  type: string;\n  data?: unknown[];\n  range?: { min: number; max: number };\n  width?: number;\n  height?: number;\n  labels?: string[];\n}\n\n// ── Lesson data"""
    content = content.replace(lesson_end_marker, unit_interface)

    # --- Fix 3: Fix getLessonsByProgramme ---
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

    new_func = """const UNIT_METADATA: Record<string, Unit> = {
  'core-maths': {
    id: 'core-maths',
    title: 'Core Mathematics',
    subtitle: 'Foundation mathematics for all SHS students',
    icon: '\\u{1f9ee}',
    colour: 'from-lime-500/20 to-emerald-500/20',
  },
};

export function getLessonsByProgramme(
  programme: 'Science' | 'Arts' | null,
  shsLevel: string | null
): { units: Unit[]; lessons: Lesson[] } {
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
  const unitIds = Array.from(new Set(filteredLessons.map((lesson) => lesson.unitId)));
  const units: Unit[] = unitIds
    .map((uid) => UNIT_METADATA[uid])
    .filter((u): u is Unit => u !== undefined);

  return { units, lessons: filteredLessons };
}"""

    if old_func in content:
        content = content.replace(old_func, new_func)
        print("SUCCESS: Updated getLessonsByProgramme")
    else:
        print("WARNING: Could not find old getLessonsByProgramme signature")
        # Try to find it with a regex
        match = re.search(r'export function getLessonsByProgramme\([^)]+\): \{ units: string\[\]; lessons: Lesson\[\] \} \{', content)
        if match:
            print(f"Found at: {match.start()}:{match.end()}")

    with open('app/lib/learningContent.ts', 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: learningContent.ts updated")


def fix_math_visualizer():
    with open('app/components/MathVisualizer.tsx', 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix import to use new MathVizConfig type
    old_import = "import type { MathVizConfig } from '../lib/learningContent';"
    content = content.replace(old_import, old_import)  # No change needed if export exists

    # Fix implicit any in NumberLine: data.map((val, idx) =>
    content = content.replace(
        'data.map((val, idx) => (',
        'data.map((val: number, idx: number) => ('
    )

    content = content.replace(
        '{data.map((val, idx) => {',
        '{data.map((val: number, idx: number) => {'
    )

    # Fix implicit any in BarChart: data.map((val, idx) => {
    content = content.replace(
        'data.map((val, idx) => {',
        'data.map((val: number, idx: number) => {'
    )

    # Fix the CoordinatePlane case - this data.map is different (val is an index used to access data[idx] and data[idx+1])
    content = content.replace(
        'data.map((val, idx) => {',
        'data.map((val: number, idx: number) => {'
    )

    # Fix implicit any in PunnettSquare: outcomes.map((outcome, idx) => {
    content = content.replace(
        '{outcomes.map((outcome, idx) => {',
        '{outcomes.map((outcome: string, idx: number) => {'
    )

    # Fix the second data.flatMap if any
    content = content.replace(
        'data.flatMap(',
        '(data as number[]).flatMap('
    )

    with open('app/components/MathVisualizer.tsx', 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: MathVisualizer.tsx updated")


if __name__ == '__main__':
    fix_learning_content()
    fix_math_visualizer()
