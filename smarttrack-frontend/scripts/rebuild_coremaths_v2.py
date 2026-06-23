#!/usr/bin/env python
"""
rebuild_coremaths_v2.py
────────────────────────
Replaces the single 9-lesson Core Mathematics section with 9 modules,
each containing 5 topic lessons (45 lessons total).

Each lesson follows the interactive pattern:
  info -> predict -> info -> question -> info -> (optional checkpoint)

This version uses triple-quoted Python strings ("\"\"\"...\"\"\") for all
content to properly handle apostrophes and special characters.
"""

# ── Helpers ──────────────────────────────────────────────────────────────────

def info_step(step_id, content):
    return f'''      {{
        id: '{step_id}',
        type: 'info',
        content:
          ''' + escape_js(content) + ''',
      }},'''

def predict_step(step_id, content, pattern, question, options, correct, explanation):
    opts = ', '.join(f"'{o}'" for o in options)
    return f'''      {{
        id: '{step_id}',
        type: 'predict',
        content:
          ''' + escape_js(content) + ''',
        predict: {{
          pattern: ''' + escape_js(pattern) + ''',
          question: ''' + escape_js(question) + ''',
          options: [{opts}],
          correctIndex: {correct},
          explanation: ''' + escape_js(explanation) + ''',
        }},
      }},'''

def question_step(step_id, content, question, options, correct, explanation):
    opts = ', '.join(f"'{o}'" for o in options)
    return f'''      {{
        id: '{step_id}',
        type: 'question',
        content:
          ''' + escape_js(content) + ''',
        exercise: {{
          question: ''' + escape_js(question) + ''',
          options: [{opts}],
          correctIndex: {correct},
          explanation: ''' + escape_js(explanation) + ''',
        }},
      }},'''

def escape_js(s):
    """Escape a string for use in JavaScript single-quoted string."""
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n") + "'"

def checkpoint_step(step_id, title, questions):
    qs_list = []
    for q in questions:
        opts = ', '.join(f"'{o}'" for o in q['options'])
        qs_list.append(f'''          {{
            question: ''' + escape_js(q['question']) + ''',
            options: [{opts}],
            correctIndex: {q['correct']},
            explanation: ''' + escape_js(q['explanation']) + ''',
          }}''')
    qs_str = ',\n'.join(qs_list)
    return f'''      {{
        id: '{step_id}',
        type: 'checkpoint',
        content:
          '⚔️ **{title}** — Mastery Check\\n\\nTime to test your understanding! Complete all questions to pass.',
        checkpoint: {{
          title: '{title}',
          questions: [
{qs_str}
          ],
          passThreshold: {len(questions) - 1},
          bonusXp: 15,
        }},
      }},'''


def make_lesson(lesson_id, title, subject, subject_icon, programme,
                difficulty, minutes, xp, unit_id, prerequisites, shs_levels,
                suggested_level, steps):
    prereqs = ', '.join(f"'{p}'" for p in prerequisites)
    levels = ', '.join(f"'{l}'" for l in shs_levels)
    steps_str = '\n'.join(steps)
    return f'''  {{
    id: '{lesson_id}',
    title: '{title}',
    subject: '{subject}',
    subjectIcon: '{subject_icon}',
    programme: '{programme}',
    difficulty: {difficulty},
    estimatedMinutes: {minutes},
    xpReward: {xp},
    unitId: '{unit_id}',
    prerequisites: [{prereqs}],
    shsLevels: [{levels}],
    suggestedLevel: '{suggested_level}',
    steps: [
{steps_str}
    ],
  }},'''


# ── Module 1: Number Sets ────────────────────────────────────────────────────
M1 = []

# 1.1 Natural Numbers and Integers
M1.append(make_lesson(
    'coremath-m1t1', 'Natural Numbers, Integers and Prime Numbers',
    'Core Mathematics', '🔢', 'Both', 1, 8, 20,
    'core-maths', [], ['SHS 1'], 'SHS 1',
    [
        info_step('coremath-m1t1-s1',
            '🔢 **Natural Numbers and Integers**\n\nLet\'s start with the building blocks of mathematics!\n\n**Natural Numbers (ℕ):** The numbers we use for counting \u2014 1, 2, 3, 4, ... (some definitions also include 0).\n\n**Integers (ℤ):** All whole numbers, including negatives \u2014 ..., -3, -2, -1, 0, 1, 2, 3, ...\n\n**Key Properties:**\n\u2022 **Closure:** The sum/product of two naturals is always a natural.\n\u2022 **Commutative:** a + b = b + a (order doesn\'t matter for + and \u00d7)\n\u2022 **Associative:** (a + b) + c = a + (b + c)\n\u2022 **Distributive:** a \u00d7 (b + c) = a \u00d7 b + a \u00d7 c\n\n> \U0001f4a1 **WASSCE Tip:** Know the difference between natural numbers, integers, and whole numbers \u2014 they are not the same!'),
        predict_step('coremath-m1t1-s2',
            'Look at this sequence: **2, 4, 6, 8, 10, ...** What type of numbers are these?',
            '2, 4, 6, 8, 10, ...',
            'What do we call this pattern?',
            ['Odd numbers', 'Even natural numbers', 'Prime numbers', 'Square numbers'],
            1,
            'These are **even natural numbers** \u2014 they are all natural numbers divisible by 2.'),
        info_step('coremath-m1t1-s3',
            '✨ **Prime Numbers and Composite Numbers**\n\n**Prime Numbers:** Natural numbers greater than 1 that have exactly two factors: 1 and itself.\n\u2022 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, ...\n\u2022 2 is the **only even prime number** (and the smallest!)\n\n**Composite Numbers:** Natural numbers greater than 1 that have more than two factors.\n\u2022 4, 6, 8, 9, 10, 12, 14, 15, ...\n\n**Note:** 1 is **neither** prime nor composite. It is called a **unit**.\n\n**Prime Factorisation:** Breaking a number into its prime factors.\n\u2022 Example: 12 = 2 \u00d7 2 \u00d7 3 = 2\u00b2 \u00d7 3\n\n> \U0001f511 **WASSCE loves prime factorisation \u2014 it is the foundation for HCF and LCM!**'),
        question_step('coremath-m1t1-s4',
            'What is the **prime factorisation** of 36?',
            'Write 36 as a product of primes',
            ['2\u00b2 \u00d7 3\u00b2', '2\u00b3 \u00d7 3', '6\u00b2', '2\u00b2 \u00d7 9'],
            0,
            '36 = 6 \u00d7 6 = (2 \u00d7 3) \u00d7 (2 \u00d7 3) = **2\u00b2 \u00d7 3\u00b2**. Always break down until all factors are prime!'),
        info_step('coremath-m1t1-s5',
            '🎯 **HCF and LCM \u2014 WASSCE Favourites!**\n\n**Highest Common Factor (HCF):** The largest number that divides two or more numbers exactly.\n\u2022 Find by: List factors OR use prime factorisation (take common primes with smallest powers)\n\n**Lowest Common Multiple (LCM):** The smallest number that is a multiple of two or more numbers.\n\u2022 Find by: List multiples OR use prime factorisation (take all primes with largest powers)\n\n**Example:** Find HCF and LCM of 12 and 18.\n\u2022 12 = 2\u00b2 \u00d7 3\n\u2022 18 = 2 \u00d7 3\u00b2\n\u2022 HCF = 2 \u00d7 3 = **6** (common primes, smallest powers)\n\u2022 LCM = 2\u00b2 \u00d7 3\u00b2 = **36** (all primes, largest powers)\n\n> ✅ **Quick check:** HCF \u00d7 LCM = Product of the two numbers (6 \u00d7 36 = 12 \u00d7 18 = 216 \u2713)'),
        question_step('coremath-m1t1-s6',
            'Find the **HCF** of 24 and 36.',
            'HCF of 24 and 36',
            ['6', '12', '72', '8'],
            1,
            '24 = 2\u00b3 \u00d7 3, 36 = 2\u00b2 \u00d7 3\u00b2. HCF = 2\u00b2 \u00d7 3 = **12**. Indeed, 12 is the largest number dividing both 24 and 36!'),
    ]
))

# 1.2 Rational and Irrational Numbers
M1.append(make_lesson(
    'coremath-m1t2', 'Rational and Irrational Numbers',
    'Core Mathematics', '🔢', 'Both', 1, 10, 25,
    'core-maths', ['coremath-m1t1'], ['SHS 1'], 'SHS 1',
    [
        info_step('coremath-m1t2-s1',
            '🔢 **Rational Numbers**\n\n**Rational Numbers (ℚ):** Any number that can be expressed as a fraction **p/q** where p and q are integers and q \u2260 0.\n\n**Examples of rational numbers:**\n\u2022 3 = 3/1\n\u2022 0.5 = 1/2\n\u2022 -2.75 = -11/4\n\u2022 0.333... = 1/3 (recurring decimal)\n\u2022 \u221a4 = 2 (perfect square root)\n\n**Examples of irrational numbers:**\n\u2022 \u221a2 \u2248 1.414213... (non-repeating, non-terminating)\n\u2022 \u03c0 \u2248 3.14159...\n\u2022 \u221a3, \u221a5 \u2014 square roots of non-perfect squares\n\n> \U0001f4a1 **WASSCE Tip:** A number is rational if its decimal form terminates or repeats. If it never repeats and never ends, it\'s irrational!'),
        predict_step('coremath-m1t2-s2',
            'Look at these numbers: **\u221a4, 0.75, 1/3, \u221a3, \u03c0**\n\nWhich are rational and which are irrational?',
            '\u221a4, 0.75, 1/3, \u221a3, \u03c0',
            'How many of these are rational numbers?',
            ['All 5 are rational', '3 are rational, 2 are irrational', '2 are rational, 3 are irrational', '4 are rational, 1 is irrational'],
            1,
            '\u221a4=2 (rational), 0.75=3/4 (rational), 1/3 (rational), \u221a3 (irrational), \u03c0 (irrational). So **3 rational, 2 irrational**.'),
        info_step('coremath-m1t2-s3',
            '📊 **Real Numbers and the Number Line**\n\n**Real Numbers (ℝ):** The set of ALL rational and irrational numbers. Every real number has a position on the number line.\n\n**The Real Number System:**\n\n      ℝ (Real Numbers)\n      \u251c\u2500\u2500 ℚ (Rational)\n      \u2502    \u251c\u2500\u2500 ℤ (Integers)\n      \u2502    \u2502    \u251c\u2500\u2500 ℕ (Natural)\n      \u2502    \u2502    \u2514\u2500\u2500 0, -1, -2, ...\n      \u2502    \u2514\u2500\u2500 Fractions & decimals\n      \u2514\u2500\u2500 Irrational (\u221a2, \u03c0, e, ...)\n\n**Operations on Real Numbers:**\n\u2022 **Addition/Subtraction:** Combine like terms; watch signs!\n\u2022 **Multiplication/Division:** Product of two negatives = positive\n\n> \U0001f9e0 **Did you know?** Between any two real numbers, there are infinitely many other real numbers! This is called the **density property**.'),
        question_step('coremath-m1t2-s4',
            'Which set does the number **\u221a9** belong to?',
            '\u221a9 belongs to which sets?',
            ['Natural only', 'Integer only', 'Rational only', '\u2115, \u2124, \u211a, and \u211d'],
            3,
            '\u221a9 = 3, which is a natural number, integer, rational number, and real number. It belongs to **all** these sets!'),
        info_step('coremath-m1t2-s5',
            '🌟 **Approximating Irrational Numbers**\n\nEven though irrational numbers cannot be written exactly as fractions, we can **approximate** them.\n\n**Method: Trial and Improvement**\n\u221a5 is between 2\u00b2 = 4 and 3\u00b2 = 9, so \u221a5 is between 2 and 3.\n\u2022 2.2\u00b2 = 4.84 (too low)\n\u2022 2.3\u00b2 = 5.29 (too high)\n\u2022 2.24\u00b2 = 5.0176 (slightly high)\n\u2022 2.23\u00b2 = 4.9729 (slightly low)\n\u2022 So \u221a5 \u2248 **2.236** (to 3 decimal places)\n\n> ✅ **WASSCE will often ask you to locate irrational numbers on the number line or give approximations.**'),
        checkpoint_step('coremath-m1t2-s6', 'Number Sets Mastery', [
            {'question': 'Which of the following is an irrational number?',
             'options': ['0.75', '\u221a16', '\u221a7', '22/7'],
             'correct': 2, 'explanation': '\u221a7 \u2248 2.6457... is non-repeating, non-terminating \u2014 it is irrational. 22/7 is rational (it is a fraction).'},
            {'question': '\u221a64 belongs to which sets?',
             'options': ['Natural only', 'Integer only', 'All real number sets', 'Irrational'],
             'correct': 2, 'explanation': '\u221a64 = 8, which belongs to \u2115, \u2124, \u211a, and \u211d \u2014 all real number sets.'},
        ]),
    ]
))

# For this initial test, let's just get Module 1 working.
# The rest of the modules will follow the same pattern.

all_modules = [M1]  # Just module 1 for now

if __name__ == '__main__':
    print("✅ Script loaded successfully! Ready to test.")
    print(f"Module 1 has {len(M1)} lessons")
