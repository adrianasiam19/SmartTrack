import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import AITutorLesson from './AITutorLesson';

const getAITaughtLesson = vi.fn();
const askCurriculumTutor = vi.fn();

vi.mock('../lib/learningApi', () => ({
  getAITaughtLesson: (...args: unknown[]) => getAITaughtLesson(...args),
  askCurriculumTutor: (...args: unknown[]) => askCurriculumTutor(...args),
}));

const TAUGHT_LESSON = {
  curriculum_id: 'coremath-number-systems',
  subject: 'Core Mathematics',
  shs_level: 'SHS 1',
  estimated_minutes: 10,
  xp_reward: 15,
  lesson: {
    topic_title: 'Number Systems',
    simple_introduction: 'Numbers help us describe quantities around us.',
    main_explanation: 'Natural numbers begin at **one**.',
    step_by_step_examples: [
      {
        title: 'Classify 5',
        steps: ['Check whether 5 is positive.', 'Notice that 5 is a whole number.'],
        answer: '5 is a natural number.',
      },
    ],
    real_life_applications: ['Counting books'],
    important_points: ['Zero is a whole number.'],
    common_mistakes: ['Not every integer is a natural number.'],
    short_summary: 'Number sets classify numbers by their properties.',
  },
};

describe('AITutorLesson', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getAITaughtLesson.mockResolvedValue(TAUGHT_LESSON);
    askCurriculumTutor.mockResolvedValue('Here is another curriculum-based example.');
  });

  it('renders the complete AI teaching structure without raw textbook filler', async () => {
    render(
      <AITutorLesson
        curriculumId="coremath-number-systems"
        onBack={vi.fn()}
        onComplete={vi.fn()}
      />,
    );

    expect(screen.getByText(/Atlas AI is preparing your lesson/i)).toBeInTheDocument();
    expect(await screen.findByRole('heading', { name: 'Number Systems' })).toBeInTheDocument();
    expect(screen.getByText('Main Explanation')).toBeInTheDocument();
    expect(screen.getByText('Step-by-Step Examples')).toBeInTheDocument();
    expect(screen.getByText('Real-Life Applications')).toBeInTheDocument();
    expect(screen.getByText('Important Points to Remember')).toBeInTheDocument();
    expect(screen.getByText('Common Mistakes Students Make')).toBeInTheDocument();
    expect(screen.getByText('Short Summary')).toBeInTheDocument();
    expect(screen.getByText('Ask Atlas AI')).toBeInTheDocument();
    expect(screen.queryByText(/learning objectives/i)).not.toBeInTheDocument();
  });

  it('sends follow-up questions through the curriculum-grounded tutor', async () => {
    render(
      <AITutorLesson
        curriculumId="coremath-number-systems"
        onBack={vi.fn()}
        onComplete={vi.fn()}
      />,
    );
    await screen.findByRole('heading', { name: 'Number Systems' });

    fireEvent.click(screen.getByRole('button', { name: 'Give me another example.' }));

    await waitFor(() => {
      expect(askCurriculumTutor).toHaveBeenCalledWith(
        'coremath-number-systems',
        'Give me another example.',
        [],
      );
    });
    expect(await screen.findByText('Here is another curriculum-based example.')).toBeInTheDocument();
  });

  it('awards the database lesson XP once on completion', async () => {
    const onComplete = vi.fn();
    render(
      <AITutorLesson
        curriculumId="coremath-number-systems"
        onBack={vi.fn()}
        onComplete={onComplete}
      />,
    );
    await screen.findByRole('heading', { name: 'Number Systems' });

    const complete = screen.getByRole('button', { name: 'Complete Lesson' });
    fireEvent.click(complete);
    fireEvent.click(complete);
    expect(onComplete).toHaveBeenCalledTimes(1);
    expect(onComplete).toHaveBeenCalledWith(15);
  });
});
