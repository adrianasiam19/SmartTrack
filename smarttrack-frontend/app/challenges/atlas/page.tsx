'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '../../components/Sidebar';
import BottomNav from '../../components/BottomNav';
import AppLayout from '../../components/AppLayout';
import { getAccessToken, getCurrentUser, getStoredUser, getAuthHeaders } from '../../lib/authApi';

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1');

export default function AtlasChallengePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);

  // Session state
  const [session, setSession] = useState<any | null>(null);
  const [questions, setQuestions] = useState<any[]>([]);
  const [subject, setSubject] = useState<string>('');
  const [subjectIndex, setSubjectIndex] = useState<number>(0);
  const [questionIndex, setQuestionIndex] = useState<number>(0);
  const [remaining, setRemaining] = useState<number>(0);
  const timerRef = useRef<number | null>(null);
  const startTimeRef = useRef<number>(0);

  const [totalXp, setTotalXp] = useState(0);
  const [feedback, setFeedback] = useState<any | null>(null);
  const [showSubjectSummary, setShowSubjectSummary] = useState(false);
  const [finalSummary, setFinalSummary] = useState<any | null>(null);
  const [sessionSummary, setSessionSummary] = useState<any | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        if (!getAccessToken()) { router.push('/login'); return; }
        const cached = getStoredUser(); if (cached) setUser(cached as any);
        const fresh = await getCurrentUser(); setUser(fresh as any);
      } catch {
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };
    load();
    return () => { if (timerRef.current) window.clearInterval(timerRef.current); };
  }, [router]);

  // Start a new challenge session
  const startChallenge = async (level = 1) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/challenge-hub/start`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ challenge_level: level }),
      });
      if (!res.ok) throw new Error('Failed to start');
      const data = await res.json();
      const s = data.session;
      setSession(s);
      setSubject(s.current_subject);
      setSubjectIndex(s.current_subject_index || 0);
      setQuestions(s.questions || []);
      setQuestionIndex(s.current_question_index || 0);
      setRemaining(s.timer_seconds || 120);
      startTimer(s.timer_seconds || 120);
      setTotalXp(0);
    } catch (e) {
      console.error(e);
      alert('Could not start challenge. Ensure backend is running.');
    } finally { setLoading(false); }
  };

  const startTimer = (seconds: number) => {
    if (timerRef.current) window.clearInterval(timerRef.current);
    setRemaining(seconds);
    startTimeRef.current = Date.now();
    timerRef.current = window.setInterval(() => {
      setRemaining((r) => {
        if (r <= 1) {
          if (timerRef.current) window.clearInterval(timerRef.current);
          // Auto-submit empty answer
          handleSubmitAnswer('');
          return 0;
        }
        return r - 1;
      });
    }, 1000) as unknown as number;
  };

  const handleSubmitAnswer = async (userAnswer: string) => {
    if (!session) return;
    const currentSubject = subject;
    const qi = questionIndex;
    const timeTaken = (Date.now() - startTimeRef.current) / 1000;
    // Stop timer
    if (timerRef.current) window.clearInterval(timerRef.current);

    try {
      const res = await fetch(`${API_BASE}/challenge-hub/submit`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          session_id: session.session_id,
          subject: currentSubject,
          question_index: qi,
          user_answer: (userAnswer || '').toString(),
          time_taken_seconds: timeTaken,
        }),
      });
      if (!res.ok) throw new Error('Submit failed');
      const data = await res.json();
      const r = data.result;
      setFeedback(r);
      setTotalXp(r.total_xp || 0);

      // Show explanation for 2s then move on
      setTimeout(async () => {
        if (r.session_complete) {
          // Finalise session
          await completeSessionAndFetchSummary();
          return;
        }

        if (r.subject_complete) {
          // Show subject summary then fetch next subject questions
          // Fetch latest session summary (includes subject performance)
          await fetchSessionSummary();
          setShowSubjectSummary(true);
          // Allow user to continue; server already advanced subject index
        } else {
          // Advance to next question locally
          setQuestionIndex((q) => q + 1);
          // restart timer
          startTimer(session.timer_seconds || 120);
        }
      }, 1500);

    } catch (e) {
      console.error(e);
      alert('Failed to submit answer');
    }
  };

  const fetchCurrentSubject = async () => {
    if (!session) return;
    try {
      const res = await fetch(`${API_BASE}/challenge-hub/questions`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ session_id: session.session_id }),
      });
      if (!res.ok) throw new Error('No subject');
      const data = await res.json();
      const d = data.data;
      setSubject(d.subject);
      setSubjectIndex(d.subject_index);
      setQuestions(d.questions || []);
      setQuestionIndex(0);
      setShowSubjectSummary(false);
      setFeedback(null);
      startTimer(d.timer_seconds || 120);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchSessionSummary = async () => {
    if (!session) return;
    try {
      const params = new URLSearchParams({ session_id: session.session_id });
      const res = await fetch(`${API_BASE}/challenge-hub/summary?${params.toString()}`, {
        method: 'GET',
        headers: getAuthHeaders(),
      });
      if (!res.ok) throw new Error('Summary fetch failed');
      const data = await res.json();
      setSessionSummary(data.summary || null);
    } catch (e) {
      console.error('Failed to fetch session summary', e);
    }
  };

  const completeSessionAndFetchSummary = async () => {
    if (!session) return;
    try {
      const res = await fetch(`${API_BASE}/challenge-hub/complete`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ session_id: session.session_id }),
      });
      if (!res.ok) throw new Error('Complete failed');
      const data = await res.json();
      setFinalSummary(data.summary || null);
    } catch (e) {
      console.error(e);
      alert('Failed to complete session');
    }
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="w-8 h-8 border-2 border-[#2563EB] border-t-transparent rounded-full animate-spin" />
        </div>
      </AppLayout>
    );
  }

  // If no session yet, show welcome/start page
  if (!session) {
    return (
      <AppLayout>
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex-1 lg:pb-0 pb-24">
            <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10">
              <div className="text-center py-12">
                <h1 className="text-3xl font-bold mb-2">Welcome to Today's Challenge</h1>
                <p className="text-gray-600 mb-6">Today's challenge consists of the four Core Subjects. Strong performance here builds a solid foundation for WASSCE.</p>
                <div className="flex items-center justify-center gap-3 mb-6">
                  <button onClick={() => startChallenge(1)} className="px-8 py-3 bg-blue-600 text-white rounded-xl">Start Level 1 (Easy)</button>
                  <button onClick={() => startChallenge(2)} className="px-8 py-3 bg-purple-600 text-white rounded-xl">Start Level 2 (Moderate)</button>
                  <button onClick={() => startChallenge(3)} className="px-8 py-3 bg-orange-600 text-white rounded-xl">Start Level 3 (Difficult)</button>
                </div>
                <p className="text-sm text-gray-500">You will answer 6 questions per subject (24 questions total). Each question has a countdown timer.</p>
              </div>
            </main>
          </div>
          <BottomNav />
        </div>
      </AppLayout>
    );
  }

  // If final summary exists, show final screen
  if (finalSummary) {
    return (
      <AppLayout>
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex-1 lg:pb-0 pb-24">
            <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10">
              <div className="text-center py-12">
                <h1 className="text-2xl font-bold mb-2">Challenge Summary</h1>
                <p className="text-gray-700 mb-4">Total XP: {finalSummary.total_xp}</p>
                <p className="text-gray-700 mb-4">Accuracy: {finalSummary.accuracy}%</p>
                <p className="text-gray-700 mb-4">Strongest: {finalSummary.strongest_subject}</p>
                <p className="text-gray-700 mb-4">Weakest: {finalSummary.weakest_subject}</p>
                <div className="mt-6">
                  <button onClick={() => router.push('/dashboard')} className="px-6 py-3 bg-blue-600 text-white rounded-xl mr-3">Go to Dashboard</button>
                  <button onClick={() => router.push('/challenges/leaderboard')} className="px-6 py-3 border border-gray-200 rounded-xl">Leaderboard</button>
                </div>
              </div>
            </main>
          </div>
          <BottomNav />
        </div>
      </AppLayout>
    );
  }

  // If showing subject summary
  if (showSubjectSummary) {
    const perf = sessionSummary?.subject_performance?.find((s: any) => s.subject === subject) || null;
    return (
      <AppLayout>
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex-1 lg:pb-0 pb-24">
            <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10">
              <div className="bg-white border rounded-xl p-6">
                <h2 className="text-xl font-bold mb-2">Subject Completed — {subject}</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-500">XP Earned</div>
                    <div className="text-2xl font-bold">{perf ? perf.xp : 0}</div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-500">Accuracy</div>
                    <div className="text-2xl font-bold">{perf ? `${perf.accuracy}%` : '0%'}</div>
                  </div>
                </div>

                <div className="mb-4">
                  <div className="text-sm text-gray-500">Correct Answers</div>
                  <div className="text-lg font-semibold">{perf ? perf.correct : 0} / {perf ? perf.total : 6}</div>
                </div>

                <div className="mb-4">
                  <div className="text-sm text-gray-500">Strong Topics</div>
                  <div className="text-sm text-gray-700">{sessionSummary?.strongest_subject || '—'}</div>
                </div>

                <div className="mb-4">
                  <div className="text-sm text-gray-500">Weak Topics</div>
                  <div className="text-sm text-gray-700">{(sessionSummary?.weak_topics && sessionSummary.weak_topics.join(', ')) || '—'}</div>
                </div>

                <div className="mt-6 text-center">
                  <button onClick={() => fetchCurrentSubject()} className="px-6 py-3 bg-blue-600 text-white rounded-xl">Continue →</button>
                </div>
              </div>
            </main>
          </div>
          <BottomNav />
        </div>
      </AppLayout>
    );
  }

  const currentQ = questions[questionIndex] || null;
  if (!currentQ) {
    return <div />;
  }

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 lg:pb-0 pb-24">
          <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 lg:pt-10">
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="text-sm text-gray-500">Subject</div>
                <div className="text-lg font-semibold">{subject}</div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-500">Time left</div>
                <div className="text-lg font-mono font-bold">{remaining}s</div>
              </div>
            </div>

            <div className="bg-white border rounded-2xl p-6 mb-4">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm text-gray-500">Question {questionIndex + 1} of {questions.length}</div>
                <div className="text-sm text-gray-500">XP: {totalXp}</div>
              </div>
              <h3 className="text-base text-gray-800 mb-4">{currentQ.question}</h3>

              {/* Options or input */}
              <div className="space-y-3">
                {currentQ.options && typeof currentQ.options === 'object' && (
                  Object.entries(currentQ.options).map(([k, v]: any) => (
                    <button
                      key={k}
                      onClick={() => handleSubmitAnswer(k)}
                      className="w-full text-left px-4 py-3 bg-gray-50 rounded-lg border border-gray-100 hover:shadow-sm"
                    >
                      <span className="font-semibold mr-3">{k}.</span> {v}
                    </button>
                  ))
                )}

                {!currentQ.options && (
                  <div>
                    <input type="text" placeholder="Type your answer" className="w-full border rounded-lg px-3 py-2" id="short_answer" />
                    <div className="mt-3 flex gap-2">
                      <button onClick={() => {
                        const el = document.getElementById('short_answer') as HTMLInputElement | null;
                        handleSubmitAnswer(el?.value || '');
                      }} className="px-4 py-2 bg-blue-600 text-white rounded-lg">Submit</button>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {feedback && (
              <div className={`p-4 rounded-lg ${feedback.is_correct ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'} border mb-4`}>
                <div className="font-bold">{feedback.is_correct ? '✅ Correct!' : '❌ Incorrect'}</div>
                <div className="text-sm">{feedback.xp_earned > 0 ? `+${feedback.xp_earned} XP` : `${feedback.xp_earned} XP`}</div>
                <div className="text-sm text-gray-700 mt-2">{feedback.explanation}</div>
              </div>
            )}

            <div className="flex gap-3">
              <button onClick={() => handleSubmitAnswer('')} className="px-4 py-2 border rounded-lg">Skip / Mark Incorrect</button>
            </div>
          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}
