'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { AnimatePresence, motion } from 'framer-motion';
import Sidebar from '../components/Sidebar';
import BottomNav from '../components/BottomNav';
import AppLayout from '../components/AppLayout';
import {
  getCurrentUser,
  getAccessToken,
  getStoredUser,
  resolvePostAuthDestination,
  UserProfile,
} from '../lib/authApi';
import {
  hasPriorDashboardVisit,
  markDashboardVisited,
} from '../lib/dashboardWelcome';
import {
  getProgression,
  type PhasePublic,
  type ProgressionMe,
} from '../lib/phasesApi';
import {
  getLibraryHome,
  type CurriculumTopic,
} from '../lib/learningApi';

const EDUCATIONAL_TIPS = [
  'The human brain has about 86 billion neurons — roughly as many as stars in the Milky Way’s neighbour galaxies.',
  'Photosynthesis in plants turns sunlight, water, and carbon dioxide into sugar and oxygen.',
  'Ghana’s Lake Volta is one of the world’s largest artificial lakes by surface area.',
  'Pi (π) is an irrational number: its decimal never ends and never repeats.',
  'Blood travels about 19,000 km a day circulating through the human body.',
  'The Sahara is the largest hot desert on Earth, covering parts of North Africa.',
  'Sound travels faster through water than through air — about four times as fast.',
  'DNA is shaped like a double helix and carries the genetic instructions for living organisms.',
  'The equator is about 40,075 km long — the imaginary line around Earth’s middle.',
  'A light-year is a distance, not a time: how far light travels in one year in space.',
  'Honey never truly spoils when stored properly — archaeologists have found edible ancient honey.',
  'The heart of an adult typically beats around 100,000 times in a single day.',
  'Mount Kilimanjaro in Tanzania is Africa’s highest mountain, at about 5,895 metres.',
  'Electricity and magnetism are linked: moving charges create magnetic fields.',
  'The United Nations was founded in 1945 to promote peace and cooperation among nations.',
  'Octopuses have three hearts and blue blood that uses copper to carry oxygen.',
  'Ghana was the first sub-Saharan African country to gain independence from colonial rule, in 1957.',
  'The word “algebra” comes from the Arabic “al-jabr,” meaning restoring or balancing.',
  'Zero as a number was developed in ancient India and transformed mathematics worldwide.',
  'Water expands when it freezes, which is why ice floats on liquid water.',
  'Your stomach produces a new lining about every few days to protect itself from acid.',
  'Lightning is hotter than the surface of the Sun — around 30,000°C in a bolt.',
  'The Nile is among the world’s longest rivers and has supported civilisations for millennia.',
  'Atoms are mostly empty space; if an atom were a stadium, the nucleus would be a marble.',
  'Reading aloud engages more brain areas than reading silently and can improve memory.',
  'Ghana’s cocoa industry has long made it one of the world’s top cocoa producers.',
  'A year on Venus lasts longer than a day on Venus — it spins very slowly.',
  'Bones are living tissue: they constantly rebuild and get stronger with healthy activity.',
  'The speed of light is about 300,000 km per second — nothing with mass can go faster.',
  'Accra became Ghana’s capital; Kumasi is historically linked to the Ashanti Kingdom.',
  'Fractions, decimals, and percentages are three ways of writing the same kind of amount.',
  'Plants “breathe” through tiny pores called stomata on their leaves.',
  'The Moon has no atmosphere, so footprints left by astronauts can last for ages.',
  'Sleep helps your brain consolidate learning — studying then resting improves recall.',
  'West Africa’s harmattan is a dry, dusty wind that blows from the Sahara in the dry season.',
  'An equilateral triangle has three equal sides and three equal angles of 60° each.',
  'Your lungs contain about 300 million tiny air sacs called alveoli for gas exchange.',
  'Earth’s magnetic field protects us from much of the solar wind from the Sun.',
  'The Twi, Ga, Ewe, and Dagbani languages are among many spoken across Ghana.',
  'Gravity on the Moon is about one-sixth of Earth’s, so you would weigh much less there.',
  'A prime number has exactly two distinct factors: 1 and itself.',
  'Bees pollinate crops that feed people; without pollinators, harvests would shrink.',
  'The Atlantic Ocean borders Ghana’s southern coast along the Gulf of Guinea.',
  'Photosynthesis produces the oxygen that most animals, including humans, need to live.',
  'Practice spaced over days beats cramming: your brain remembers better with gaps.',
  'Diamonds and graphite are both pure carbon, but arranged in different crystal structures.',
  'The Amazon rainforest produces a large share of the world’s oxygen and hosts huge biodiversity.',
  'Circumference of a circle equals 2πr, where r is the radius.',
  'Your body is about 60% water — staying hydrated supports concentration and health.',
  'Kwame Nkrumah was Ghana’s first Prime Minister and later its first President.',
  'Antibiotics fight bacteria, not viruses — colds and flu are usually viral.',
  'The Pythagorean theorem: in a right triangle, a² + b² = c² for the sides.',
  'Camels store fat in their humps, not water — but that fat can be metabolised for energy.',
  'Ghana sits near the equator, so day length stays fairly even all year.',
  'Metals are good conductors of heat and electricity because of free-moving electrons.',
  'A map’s scale shows how distances on paper relate to distances in the real world.',
  'The human eye can distinguish millions of colour shades under good light.',
  'Fortresses along Ghana’s coast tell stories of trade, colonialism, and the Atlantic slave trade.',
  'Evaporation cools you when sweat turns to vapour and takes heat from your skin.',
  'Negative numbers were once controversial, but they are essential for finance and science.',
  'Whales are mammals: they breathe air, give birth to live young, and produce milk.',
  'The Tropic of Cancer and Tropic of Capricorn mark the edges of the tropical zone.',
  'Writing notes by hand can help you understand and remember material better than typing alone.',
  'Iron is essential in haemoglobin, the protein that carries oxygen in red blood cells.',
  'A hectare is 10,000 square metres — a common unit for measuring land area.',
  'The Big Bang theory describes how the universe expanded from a hot, dense early state.',
  'Ghana’s black star on the flag symbolises African freedom and unity.',
  'Acids taste sour; bases often feel soapy — but never taste chemicals in a lab.',
  'An isosceles triangle has at least two equal sides.',
  'Coral reefs are built by tiny animals and support some of the richest ocean ecosystems.',
  'The Earth’s core is mostly iron and nickel and generates our magnetic field.',
  'Speaking a second language can improve attention and problem-solving skills.',
  'Cassava, yam, and plantain are staple foods across much of West Africa.',
  'Kinetic energy depends on mass and speed: faster objects carry much more energy.',
  'A century is 100 years; a millennium is 1,000 years.',
  'Vitamin C helps your immune system and is found in fruits like oranges and mangoes.',
  'The Sahara once had lakes and grasslands thousands of years ago — climates change over time.',
  'Parallel lines never meet and stay the same distance apart.',
  'Your fingerprint pattern is unique — even identical twins have different prints.',
  'Solar panels convert sunlight into electricity using the photovoltaic effect.',
  'The Volta River system is vital for power, fishing, and transport in Ghana.',
  'Probability is a number between 0 and 1 that measures how likely an event is.',
  'Trees take in carbon dioxide and help cool cities with shade and moisture.',
  'Newton’s third law: for every action there is an equal and opposite reaction.',
  'The African Union brings African countries together for cooperation and development.',
  'A litre of water has a mass of about one kilogram at standard conditions.',
  'Mitochondria are often called the “powerhouses” of the cell because they make ATP energy.',
  'Longitude lines run from pole to pole; latitude lines run east–west.',
  'Chewing gum while studying doesn’t replace understanding — focus and practice do.',
  'Gold has been mined in Ghana for centuries; the old name “Gold Coast” reflects that history.',
  'An acute angle is less than 90°; an obtuse angle is greater than 90° but less than 180°.',
  'Butterflies taste with their feet to check if a plant is good for laying eggs.',
  'Recycling aluminium saves far more energy than making new aluminium from ore.',
  'The mean is the average; the median is the middle value when data are ordered.',
  'Earth completes one orbit around the Sun in about 365.25 days — hence leap years.',
  'Pan-African colours — red, gold, and green — appear on many African flags, including Ghana’s.',
  'Friction opposes motion and also lets you walk without slipping.',
  'A hypothesis is a testable idea; experiments help support or reject it.',
  'Shea butter, from the shea tree, is widely used in West African cooking and skincare.',
  'Square numbers come from multiplying a whole number by itself: 1, 4, 9, 16, 25…',
  'The ozone layer high in the atmosphere absorbs harmful ultraviolet (UV) rays from the Sun.',
  'Asking “why?” and checking evidence is at the heart of scientific thinking.',
  'Ghana’s Independence Arch in Accra commemorates freedom won on 6 March 1957.',
  'Compound interest grows savings faster because you earn interest on interest.',
  'Birds are living dinosaurs — modern birds evolved from theropod dinosaurs.',
  'A protractor measures angles in degrees.',
  'Fresh water is scarce: most of Earth’s water is salty ocean water.',
  'Teamwork and clear communication help in science labs and in everyday problem-solving.',
  'The Ashanti Golden Stool is a sacred symbol of unity for the Asante people.',
  'Velocity includes direction; speed is how fast you go without saying which way.',
  'Chlorophyll makes leaves green and captures light energy for photosynthesis.',
  'A Venn diagram shows how sets overlap and what they have in common.',
  'Volcanoes and earthquakes often occur near the edges of tectonic plates.',
  'Eating a balanced meal before exams helps your brain work more steadily.',
  'Ghana shares borders with Côte d’Ivoire, Burkina Faso, and Togo.',
  'An algorithm is a step-by-step method for solving a problem — used in maths and coding.',
  'Sharks existed before trees: early sharks swam hundreds of millions of years ago.',
  'Area of a rectangle is length × width; volume of a cuboid is length × width × height.',
  'The greenhouse effect keeps Earth warm enough for life — but too much warming is harmful.',
  'Respectful debate helps you learn: listen, give reasons, and update your views with evidence.',
];
function useRotatingTip(intervalMs = 10000) {
  const [index, setIndex] = useState(() =>
    Math.floor(Math.random() * EDUCATIONAL_TIPS.length),
  );

  useEffect(() => {
    const id = window.setInterval(() => {
      setIndex((current) => {
        if (EDUCATIONAL_TIPS.length <= 1) return current;
        let next = current;
        while (next === current) {
          next = Math.floor(Math.random() * EDUCATIONAL_TIPS.length);
        }
        return next;
      });
    }, intervalMs);
    return () => window.clearInterval(id);
  }, [intervalMs]);

  return EDUCATIONAL_TIPS[index];
}

type NextAction = {
  phase: PhasePublic;
  levelNumber: number;
  levelId: number;
  label: string;
  progressPct: number;
  completedLevels: number;
  totalLevels: number;
};

function findNextAction(data: ProgressionMe): NextAction | null {
  const ordered = [...data.phases].sort((a, b) => a.number - b.number);
  for (const phase of ordered) {
    if (phase.status === 'locked') continue;
    const levels = [...phase.levels].sort((a, b) => a.number - b.number);
    const completedLevels = levels.filter((l) => l.status === 'completed').length;
    const totalLevels = levels.length || 10;
    const progressPct = Math.round((completedLevels / totalLevels) * 100);
    const hasStarted =
      completedLevels > 0 ||
      levels.some((l) => l.status === 'in_progress');

    const playable = levels.find(
      (l) =>
        l.status === 'available' ||
        l.status === 'in_progress' ||
        l.status === 'completed',
    );
    // Prefer first incomplete playable level
    const next =
      levels.find(
        (l) => l.status === 'available' || l.status === 'in_progress',
      ) || playable;

    if (next && next.status !== 'locked') {
      const allDone = levels.every((l) => l.status === 'completed');
      return {
        phase,
        levelNumber: next.number,
        levelId: next.id,
        label: allDone
          ? `${phase.name} complete — open checkpoint or replay`
          : hasStarted
            ? `Continue ${phase.name} · Level ${next.number}`
            : `Start ${phase.name} · Level ${next.number}`,
        progressPct,
        completedLevels,
        totalLevels,
      };
    }
  }
  return null;
}

function hasChallengeProgress(data: ProgressionMe | null): boolean {
  if (!data?.phases?.length) return false;
  return data.phases.some((phase) =>
    phase.levels.some(
      (level) =>
        level.status === 'completed' || level.status === 'in_progress',
    ),
  );
}

function statusTone(status: string) {
  if (status === 'completed') {
    return 'bg-emerald-50 text-emerald-700 border-emerald-200';
  }
  if (status === 'in_progress' || status === 'available') {
    return 'bg-[#EFF6FF] text-[#1D4ED8] border-[#BFDBFE]';
  }
  return 'bg-slate-100 text-slate-500 border-slate-200';
}

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [progression, setProgression] = useState<ProgressionMe | null>(null);
  const [learningRecs, setLearningRecs] = useState<CurriculumTopic[]>([]);
  const [loading, setLoading] = useState(true);
  const [isReturningUser, setIsReturningUser] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        const token = getAccessToken();
        if (!token) {
          router.push('/login');
          return;
        }

        const cached = getStoredUser();
        if (cached) {
          const cachedDestination = resolvePostAuthDestination(cached);
          if (cachedDestination !== '/dashboard') {
            router.replace(cachedDestination);
            return;
          }
          setUser(cached);
          setLoading(false);
        }

        const [fresh, prog, library] = await Promise.all([
          getCurrentUser(),
          getProgression().catch(() => null),
          getLibraryHome().catch(() => null),
        ]);
        const destination = resolvePostAuthDestination(fresh);
        if (destination !== '/dashboard') {
          router.replace(destination);
          return;
        }
        setUser(fresh);
        setProgression(prog);
        setLearningRecs((library?.recommended || []).slice(0, 4));
      } catch {
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [router]);

  useEffect(() => {
    if (!user?.id) return;
    const returning = hasPriorDashboardVisit(user.id);
    setIsReturningUser(returning);
    if (!returning) {
      markDashboardVisited(user.id);
    }
  }, [user?.id]);

  const nextAction = useMemo(
    () => (progression ? findNextAction(progression) : null),
    [progression],
  );
  const hasStartedChallenges = useMemo(
    () => hasChallengeProgress(progression),
    [progression],
  );
  const tip = useRotatingTip(10000);

  if (loading && !user) {
    return (
      <AppLayout>
        <div className="flex min-h-screen items-center justify-center">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-[#2563EB] border-t-transparent" />
        </div>
      </AppLayout>
    );
  }

  if (!user) return null;

  const firstName = user.full_name?.split(' ')[0] || 'there';
  const userXp = typeof user.xp === 'number' ? user.xp : 0;
  const userRank = user.rank || 'Beginner';
  const userProgramme = user.programme || 'Student';

  return (
    <AppLayout>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 pb-28 lg:pb-0">
          <main className="mx-auto max-w-3xl px-4 pt-20 sm:px-6 lg:px-8 lg:pt-10 pb-10">
            {/* Hero welcome */}
            <motion.section
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8"
            >
              <p className="text-sm font-medium text-[#64748B]">Dashboard</p>
              <h1 className="mt-1 text-3xl font-bold tracking-tight text-[#0F172A] sm:text-4xl">
                {isReturningUser ? 'Welcome back,' : 'Welcome to ATLAS,'}{' '}
                <span className="text-[#2563EB]">{firstName}</span>
              </h1>
              <p className="mt-2 text-[#64748B]">{userProgramme}</p>
            </motion.section>

            {/* XP strip — no streak emphasis */}
            <motion.section
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.04 }}
              className="mb-6 flex items-center justify-between gap-4 rounded-2xl border border-[#E2E8F0] bg-white px-5 py-4"
            >
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">
                  Rank
                </p>
                <p className="mt-0.5 text-lg font-bold text-[#0F172A]">{userRank}</p>
              </div>
              <div className="text-right">
                <p className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">
                  XP
                </p>
                <p className="mt-0.5 text-lg font-bold text-[#2563EB]">
                  {userXp.toLocaleString()}
                </p>
              </div>
            </motion.section>

            {/* Primary: live phase progress */}
            <motion.section
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.08 }}
              className="mb-6 overflow-hidden rounded-3xl border border-[#BFDBFE] bg-gradient-to-b from-[#EFF6FF] to-white shadow-sm"
            >
              <div className="px-6 pt-6 sm:px-8 sm:pt-8">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wider text-[#2563EB]">
                      Your path
                    </p>
                    <h2 className="mt-1 text-2xl font-bold text-[#0F172A]">
                      {nextAction
                        ? nextAction.phase.name
                        : 'Phase Challenges'}
                    </h2>
                    <p className="mt-2 text-sm leading-relaxed text-[#64748B]">
                      {nextAction
                        ? nextAction.label
                        : 'Start Phase 1 to begin mixed-subject challenges.'}
                    </p>
                  </div>
                  {nextAction ? (
                    <span className="shrink-0 rounded-full border border-[#BFDBFE] bg-white px-3 py-1 text-[11px] font-semibold uppercase tracking-wide text-[#2563EB]">
                      Level {nextAction.levelNumber}
                    </span>
                  ) : null}
                </div>

                {nextAction ? (
                  <div className="mt-6 space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium text-[#475569]">
                        {nextAction.completedLevels} of {nextAction.totalLevels}{' '}
                        levels
                      </span>
                      <span className="font-semibold text-[#1E3A8A]">
                        {nextAction.progressPct}%
                      </span>
                    </div>
                    <div className="h-2.5 overflow-hidden rounded-full bg-[#DBEAFE]">
                      <div
                        className="h-full rounded-full bg-[#2563EB] transition-all"
                        style={{ width: `${nextAction.progressPct}%` }}
                      />
                    </div>
                  </div>
                ) : null}

                {/* Phase overview chips */}
                {progression?.phases?.length ? (
                  <div className="mt-6 grid grid-cols-3 gap-2 sm:gap-3">
                    {progression.phases
                      .slice()
                      .sort((a, b) => a.number - b.number)
                      .map((phase) => {
                        const done = phase.levels.filter(
                          (l) => l.status === 'completed',
                        ).length;
                        const total = phase.levels.length || 10;
                        return (
                          <div
                            key={phase.id}
                            className={`rounded-2xl border px-3 py-3 text-center ${statusTone(phase.status)}`}
                          >
                            <p className="text-[10px] font-semibold uppercase tracking-wider opacity-80">
                              Phase {phase.number}
                            </p>
                            <p className="mt-1 text-sm font-bold capitalize">
                              {phase.status.replace(/_/g, ' ')}
                            </p>
                            <p className="mt-1 text-[11px] opacity-80">
                              {done}/{total}
                            </p>
                          </div>
                        );
                      })}
                  </div>
                ) : null}
              </div>

              <div className="mt-6 border-t border-[#DBEAFE] p-4 sm:p-5">
                <button
                  type="button"
                  onClick={() => router.push('/challenges')}
                  className="w-full rounded-2xl bg-[#2563EB] py-3.5 text-center text-base font-bold text-white shadow-md shadow-[#2563EB]/25 transition hover:bg-[#1D4ED8] active:scale-[0.99]"
                >
                  {hasStartedChallenges ? 'Continue challenges' : 'Start challenges'}
                </button>
              </div>
            </motion.section>

            {/* Learning recommendations from challenges + history */}
            {learningRecs.length > 0 ? (
              <motion.section
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="mb-6"
              >
                <div className="mb-3 flex items-center justify-between gap-3">
                  <h2 className="text-sm font-semibold text-[#0F172A]">
                    Recommended for you
                  </h2>
                  <button
                    type="button"
                    onClick={() => router.push('/learning')}
                    className="text-xs font-semibold text-[#2563EB]"
                  >
                    Learning Center →
                  </button>
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  {learningRecs.map((topic) => (
                    <button
                      key={topic.curriculum_id}
                      type="button"
                      onClick={() =>
                        router.push(
                          `/learning?topic=${encodeURIComponent(topic.curriculum_id)}`,
                        )
                      }
                      className="rounded-2xl border border-[#E2E8F0] bg-white p-4 text-left transition hover:border-[#2563EB] hover:shadow-sm"
                    >
                      <p className="text-[10px] font-semibold uppercase tracking-wider text-[#94A3B8]">
                        {topic.subject}
                      </p>
                      <p className="mt-1 text-sm font-semibold text-[#0F172A] leading-snug">
                        {topic.title}
                      </p>
                      {topic.reason ? (
                        <p className="mt-1.5 text-xs text-[#2563EB]">{topic.reason}</p>
                      ) : null}
                    </button>
                  ))}
                </div>
              </motion.section>
            ) : null}

            {/* Secondary shortcuts */}
            <motion.section
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.12 }}
              className="mb-6 grid gap-4 grid-cols-1"
            >
              <button
                type="button"
                onClick={() => router.push('/learning')}
                className="rounded-3xl border border-[#E2E8F0] bg-white p-5 text-left transition hover:border-[#2563EB] hover:shadow-md"
              >
                <p className="text-xs font-semibold uppercase tracking-wider text-[#2563EB]">
                  Learning Center
                </p>
                <h3 className="mt-2 text-lg font-bold text-[#0F172A]">
                  Search lessons
                </h3>
                <p className="mt-1.5 text-sm leading-relaxed text-[#64748B]">
                  Practice topics with Atlas AI when you need extra support.
                </p>
                <span className="mt-4 inline-flex text-sm font-semibold text-[#2563EB]">
                  Open Learning →
                </span>
              </button>
            </motion.section>

            {/* Rotating educational tip */}
            <motion.section
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.16 }}
              className="rounded-2xl border border-[#E2E8F0] bg-[#F8FAFC] px-5 py-4"
            >
              <p className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">
                Did you know?
              </p>
              <div className="relative mt-1 min-h-[3.5rem]">
                <AnimatePresence mode="wait">
                  <motion.p
                    key={tip}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -6 }}
                    transition={{ duration: 0.25 }}
                    className="text-sm leading-relaxed text-[#64748B]"
                  >
                    {tip}
                  </motion.p>
                </AnimatePresence>
              </div>
            </motion.section>
          </main>
        </div>
        <BottomNav />
      </div>
    </AppLayout>
  );
}
