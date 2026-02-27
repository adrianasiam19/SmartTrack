'use client';

import { useState } from 'react';
import Sidebar from '../components/Sidebar';
import GlassmorphicLayout from '../components/GlassmorphicLayout';

export default function Assessment() {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);

  const questions = [
    {
      question: 'What is the result of 15 × 8?',
      options: ['110', '120', '130', '140'],
      correct: 1,
    },
    {
      question: 'Which of the following is a prime number?',
      options: ['15', '21', '23', '27'],
      correct: 2,
    },
    {
      question: 'If x + 5 = 12, what is the value of x?',
      options: ['5', '6', '7', '8'],
      correct: 2,
    },
  ];

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedAnswer(null);
    }
  };

  const progress = ((currentQuestion + 1) / questions.length) * 100;

  return (
    <GlassmorphicLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        
        <main className="flex-1">
          <header className="bg-white/5 backdrop-blur-2xl border-b border-white/10 px-8 py-6">
            <h1 className="text-2xl font-semibold text-white">Assessment</h1>
          </header>

          <div className="p-8 max-w-3xl mx-auto">
            <div className="bg-white/5 backdrop-blur-2xl rounded-2xl border border-white/10 p-8">
            <div className="mb-8">
              <div className="flex justify-between text-sm text-gray-300 mb-2">
                <span>Question {currentQuestion + 1} of {questions.length}</span>
                <span>{Math.round(progress)}% Complete</span>
              </div>
              <div className="w-full bg-white/10 rounded-full h-2">
                <div
                  className="bg-lime-400 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            <div className="mb-8">
              <h2 className="text-2xl font-semibold text-white mb-6">
                {questions[currentQuestion].question}
              </h2>

              <div className="space-y-3">
                {questions[currentQuestion].options.map((option, index) => (
                  <button
                    key={index}
                    onClick={() => setSelectedAnswer(index)}
                    className={`w-full text-left px-6 py-4 rounded-xl border transition ${
                      selectedAnswer === index
                        ? 'border-lime-400 bg-lime-400/20'
                        : 'border-white/10 hover:border-white/20 bg-white/5'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                          selectedAnswer === index
                            ? 'border-lime-400 bg-lime-400'
                            : 'border-white/30'
                        }`}
                      >
                        {selectedAnswer === index && (
                          <svg className="w-4 h-4 text-gray-900" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>
                      <span className="text-white">{option}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <div className="flex justify-between">
              <button
                onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                disabled={currentQuestion === 0}
                className="px-6 py-3 border border-white/10 text-gray-300 rounded-xl hover:bg-white/5 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                Previous
              </button>
              <button
                onClick={handleNext}
                disabled={selectedAnswer === null}
                className="px-6 py-3 bg-lime-400 text-gray-900 rounded-xl hover:bg-lime-500 disabled:opacity-50 disabled:cursor-not-allowed transition font-semibold"
              >
                {currentQuestion === questions.length - 1 ? 'Submit' : 'Next'}
              </button>
            </div>
          </div>
        </div>
      </main>
      </div>
    </GlassmorphicLayout>
  );
}
