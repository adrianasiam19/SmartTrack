import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

import { ALL_LESSONS } from '../app/lib/learningContent';

const outputPath = resolve(
  process.cwd(),
  '..',
  'smarttrack-backend',
  'data',
  'curriculum_lessons.json',
);

const lessons = ALL_LESSONS
  .filter((lesson) => lesson.shsLevels.some((level) => level === 'SHS 1' || level === 'SHS 2'))
  .map((lesson) => ({
    curriculum_id: lesson.id,
    title: lesson.title,
    subject: lesson.subject,
    programme: lesson.programme,
    shs_levels: lesson.shsLevels.filter((level) => level === 'SHS 1' || level === 'SHS 2'),
    unit_id: lesson.unitId,
    difficulty: lesson.difficulty,
    estimated_minutes: lesson.estimatedMinutes,
    xp_reward: lesson.xpReward,
    source_content: lesson,
  }));

mkdirSync(dirname(outputPath), { recursive: true });
writeFileSync(outputPath, `${JSON.stringify(lessons, null, 2)}\n`, 'utf8');

console.log(`Exported ${lessons.length} SHS 1/2 curriculum lessons to ${outputPath}`);
