import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, act, fireEvent } from '@testing-library/react';
import PsychometricPrompt from './PsychometricPrompt';

vi.mock('framer-motion', () => {
  const ReactMock = require('react');
  return {
    motion: {
      div: ({ children, ...props }: any) => {
        const { initial, animate, exit, whileHover, whileTap, ...rest } = props;
        return ReactMock.createElement('div', rest, children);
      },
    },
    AnimatePresence: ({ children }: any) =>
      ReactMock.createElement(ReactMock.Fragment, null, children),
  };
});

const mockSubmitPsychometric = vi.fn();
vi.mock('../lib/challengesApi', () => ({
  submitPsychometric: (...args: any[]) => mockSubmitPsychometric(...args),
}));

const MOCK_CARD = {
  id: 'motiv_001',
  category: 'Motivation',
  question: 'What sounds most exciting to you?',
  display: 'choose',
  options: [
    { value: 'A', label: 'Building something' },
    { value: 'B', label: 'Discovering how things work' },
    { value: 'C', label: 'Helping others' },
    { value: 'D', label: 'Competing and winning' },
  ],
};

function renderPrompt(props: Partial<Parameters<typeof PsychometricPrompt>[0]> = {}) {
  return render(
    React.createElement(PsychometricPrompt, {
      onComplete: vi.fn(),
      onSkip: vi.fn(),
      ...props,
    })
  );
}

function clickButton(button: HTMLElement) {
  act(() => {
    fireEvent.click(button);
  });
}

describe('PsychometricPrompt', () => {
  beforeEach(() => {
    vi.useRealTimers();
    mockSubmitPsychometric.mockResolvedValue(undefined);
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  it('shows loading state when no preloadedCard is provided', () => {
    renderPrompt();
    expect(screen.getByText(/loading insight/i)).toBeInTheDocument();
  });

  it('shows loading state when preloadedCard is null', () => {
    renderPrompt({ preloadedCard: null });
    expect(screen.getByText(/loading insight/i)).toBeInTheDocument();
  });

  it('renders the preloaded card immediately when provided', () => {
    renderPrompt({ preloadedCard: MOCK_CARD });
    expect(screen.getByText(MOCK_CARD.question)).toBeInTheDocument();
    expect(screen.getByText('Building something')).toBeInTheDocument();
    expect(screen.getByText('Discovering how things work')).toBeInTheDocument();
    expect(screen.queryByText(/loading insight/i)).not.toBeInTheDocument();
  });

  it('displays the card header', () => {
    renderPrompt({ preloadedCard: MOCK_CARD });
    expect(screen.getByText(/quick insight/i)).toBeInTheDocument();
  });

  it('switches from loading to card when preloadedCard arrives', async () => {
    const { rerender } = render(
      React.createElement(PsychometricPrompt, { onComplete: vi.fn(), onSkip: vi.fn() })
    );
    expect(screen.getByText(/loading insight/i)).toBeInTheDocument();

    rerender(
      React.createElement(PsychometricPrompt, {
        onComplete: vi.fn(),
        onSkip: vi.fn(),
        preloadedCard: MOCK_CARD,
      })
    );

    await waitFor(() => {
      expect(screen.getByText(MOCK_CARD.question)).toBeInTheDocument();
    });
    expect(screen.queryByText(/loading insight/i)).not.toBeInTheDocument();
  });

  it('does not switch card when preloadedCard changes after settling', () => {
    const { rerender } = render(
      React.createElement(PsychometricPrompt, {
        onComplete: vi.fn(),
        onSkip: vi.fn(),
        preloadedCard: MOCK_CARD,
      })
    );
    expect(screen.getByText('What sounds most exciting to you?')).toBeInTheDocument();

    const NEW_CARD = {
      ...MOCK_CARD,
      id: 'prob_001',
      question: 'When faced with a difficult problem?',
    };

    rerender(
      React.createElement(PsychometricPrompt, {
        onComplete: vi.fn(),
        onSkip: vi.fn(),
        preloadedCard: NEW_CARD,
      })
    );

    expect(screen.getByText('What sounds most exciting to you?')).toBeInTheDocument();
    expect(screen.queryByText('When faced with a difficult problem?')).not.toBeInTheDocument();
  });

  it('shows fallback card after 5 seconds if no preloadedCard arrives', () => {
    vi.useFakeTimers();
    renderPrompt();
    expect(screen.getByText(/loading insight/i)).toBeInTheDocument();

    act(() => {
      vi.advanceTimersByTime(5000);
    });

    expect(screen.getByText(/what sounds most exciting to you/i)).toBeInTheDocument();
    vi.useRealTimers();
  });

  it('does not show fallback if preloadedCard arrives before timeout', () => {
    vi.useFakeTimers();
    const { rerender } = render(
      React.createElement(PsychometricPrompt, { onComplete: vi.fn(), onSkip: vi.fn() })
    );
    expect(screen.getByText(/loading insight/i)).toBeInTheDocument();

    act(() => {
      vi.advanceTimersByTime(3000);
    });

    rerender(
      React.createElement(PsychometricPrompt, {
        onComplete: vi.fn(),
        onSkip: vi.fn(),
        preloadedCard: MOCK_CARD,
      })
    );

    expect(screen.getByText(MOCK_CARD.question)).toBeInTheDocument();

    act(() => {
      vi.advanceTimersByTime(3000);
    });

    expect(screen.getByText(MOCK_CARD.question)).toBeInTheDocument();
    expect(screen.queryByText(/Solving puzzles/i)).not.toBeInTheDocument();
    vi.useRealTimers();
  });

  it('highlights the selected option', () => {
    renderPrompt({ preloadedCard: MOCK_CARD });
    const option = screen.getByText('Discovering how things work');
    clickButton(option);
    expect(option.closest('button')?.className).toContain('border-[#4F46E5]');
  });

  it('calls submitPsychometric with the correct data on selection', () => {
    renderPrompt({ preloadedCard: MOCK_CARD });
    clickButton(screen.getByText('Building something'));
    expect(mockSubmitPsychometric).toHaveBeenCalledWith({
      question_id: 'motiv_001',
      answer: 'A',
    });
  });

  it('calls onComplete after selecting an option', async () => {
    vi.useFakeTimers();
    const onComplete = vi.fn();
    renderPrompt({ preloadedCard: MOCK_CARD, onComplete });
    clickButton(screen.getByText('Building something'));

    await act(async () => {});

    act(() => {
      vi.advanceTimersByTime(800);
    });

    expect(onComplete).toHaveBeenCalled();
    vi.useRealTimers();
  });

  it('calls onSkip when skip button is clicked', () => {
    const onSkip = vi.fn();
    renderPrompt({ preloadedCard: MOCK_CARD, onSkip });
    clickButton(screen.getByText('Skip'));
    expect(onSkip).toHaveBeenCalled();
  });

  it('prevents double-submission when clicking multiple options', () => {
    renderPrompt({ preloadedCard: MOCK_CARD });
    clickButton(screen.getByText('Building something'));
    clickButton(screen.getByText('Discovering how things work'));
    expect(mockSubmitPsychometric).toHaveBeenCalledTimes(1);
    expect(mockSubmitPsychometric).toHaveBeenCalledWith({
      question_id: 'motiv_001',
      answer: 'A',
    });
  });

  it('prevents skip after option selection', () => {
    const onSkip = vi.fn();
    const onComplete = vi.fn();
    renderPrompt({ preloadedCard: MOCK_CARD, onComplete, onSkip });
    clickButton(screen.getByText('Building something'));
    clickButton(screen.getByText('Skip'));
    expect(onSkip).not.toHaveBeenCalled();
  });

  it('renders fallback card with static options after timeout', () => {
    vi.useFakeTimers();
    renderPrompt();
    act(() => { vi.advanceTimersByTime(5000); });
    expect(screen.getByText(/what sounds most exciting to you/i)).toBeInTheDocument();
    expect(screen.getByText('Solving puzzles and brain teasers')).toBeInTheDocument();
    expect(screen.getByText('Discovering how things work')).toBeInTheDocument();
    expect(screen.getByText('Creating art or telling stories')).toBeInTheDocument();
    expect(screen.getByText('Helping and working with others')).toBeInTheDocument();
    vi.useRealTimers();
  });

  it('calls submitPsychometric on fallback card selection', () => {
    vi.useFakeTimers();
    renderPrompt();
    act(() => { vi.advanceTimersByTime(5000); });
    clickButton(screen.getByText('Solving puzzles and brain teasers'));
    expect(mockSubmitPsychometric).toHaveBeenCalledWith({
      question_id: 'psych_q1',
      answer: 'A',
    });
    vi.useRealTimers();
  });

  it('allows skip on fallback card', () => {
    vi.useFakeTimers();
    const onSkip = vi.fn();
    renderPrompt({ onSkip });
    act(() => { vi.advanceTimersByTime(5000); });
    expect(screen.getByText(/what sounds most exciting to you/i)).toBeInTheDocument();
    clickButton(screen.getByText('Skip'));
    expect(onSkip).toHaveBeenCalled();
    vi.useRealTimers();
  });

  it('calls onComplete on fallback card selection after delay', async () => {
    vi.useFakeTimers();
    const onComplete = vi.fn();
    renderPrompt({ onComplete });
    act(() => { vi.advanceTimersByTime(5000); });
    clickButton(screen.getByText('Solving puzzles and brain teasers'));

    await act(async () => {});

    act(() => { vi.advanceTimersByTime(800); });
    expect(onComplete).toHaveBeenCalled();
    vi.useRealTimers();
  });

  it('does not crash when preloadedCard arrives after settledRef', () => {
    vi.useFakeTimers();
    const { rerender } = render(
      React.createElement(PsychometricPrompt, { onComplete: vi.fn(), onSkip: vi.fn() })
    );
    act(() => { vi.advanceTimersByTime(5000); });
    expect(screen.getByText(/what sounds most exciting to you/i)).toBeInTheDocument();

    rerender(
      React.createElement(PsychometricPrompt, {
        onComplete: vi.fn(),
        onSkip: vi.fn(),
        preloadedCard: MOCK_CARD,
      })
    );

    expect(screen.getByText('Solving puzzles and brain teasers')).toBeInTheDocument();
    expect(screen.queryByText('Building something')).not.toBeInTheDocument();
    vi.useRealTimers();
  });
});
