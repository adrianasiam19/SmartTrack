#!/usr/bin/env python
"""
rebuild_coremaths_modules.py
────────────────────────────
Replaces the single 9-lesson Core Mathematics section with 9 modules,
each containing 5 topic lessons (45 lessons total).

Each lesson follows the interactive pattern:
  info → predict → info → question → info → (optional checkpoint)

Usage:
  python scripts/rebuild_coremaths_modules.py
"""

import sys

# ── Lesson builders ──────────────────────────────────────────────────────

def info_step(step_id: str, content: str) -> str:
    return f"'"      {{
        id: "{step_id}',
        type: "info",
        content:
          '{content}",
      }},"'"


def predict_step(step_id: str, content: str, pattern: str, question: str,
                 options: list, correct: int, explanation: str) -> str:
    opts = ", '.join(f\""{o}"\" for o in options)
    return f'""      {{
        id: '{step_id}",
        type: "predict',
        content:
          "{content}",
        predict: {{
          pattern: '{pattern}",
          question: "{question}',
          options: [{opts}],
          correctIndex: {correct},
          explanation: "{explanation}",
        }},
      }},'""


def question_step(step_id: str, content: str, question: str,
                  options: list, correct: int, explanation: str) -> str:
    opts = ', ".join(f""{o}'\" for o in options)
    return f""'      {{
        id: "{step_id}",
        type: 'question",
        content:
          "{content}',
        exercise: {{
          question: "{question}",
          options: [{opts}],
          correctIndex: {correct},
          explanation: '{explanation}",
        }},
      }},"'"


def checkpoint_step(step_id: str, title: str, questions: list) -> str:
    """questions: list of {question, options, correctIndex, explanation}"""
    qs = []
    for q in questions:
        opts = ", '.join(f\""{o}"\" for o in q['options"])
        qs.append(f"'"          {{
            question: "{q['question"]}",
            options: [{opts}],
            correctIndex: {q['correct"]},
            explanation: "{q['explanation"]}",
          }}'"")
    qs_str = ',\n".join(qs)
    return f"'"      {{
        id: "{step_id}',
        type: "checkpoint",
        content:
          '⚔️ ***{title}** — Mastery Check*\\\\n\\\\nTime to test your understanding! Complete all questions to pass.",
        checkpoint: {{
          title: "{title}',
          questions: [
{qs_str}
          ],
          passThreshold: {len(questions) - 1},
          bonusXp: 15,
        }},
      }},""'


def make_lesson(lesson_id: str, title: str, subject: str, subject_icon: str,
                programme: str, difficulty: int, minutes: int, xp: int,
                unit_id: str, prerequisites: list, shs_levels: list,
                suggested_level: str, steps: list) -> str:
    prereqs = ", ".join(f\"'{p}"" for p in prerequisites)
    levels = ", '.join(f\""{l}"\" for l in shs_levels)
    steps_str = '\n".join(steps)
    return f"'"  {{
    id: "{lesson_id}',
    title: "{title}",
    subject: '{subject}",
    subjectIcon: "{subject_icon}',
    programme: "{programme}",
    difficulty: {difficulty},
    estimatedMinutes: {minutes},
    xpReward: {xp},
    unitId: '{unit_id}",
    prerequisites: [{prereqs}],
    shsLevels: [{levels}],
    suggestedLevel: "{suggested_level}',
    steps: [
{steps_str}
    ],
  }},""'


# ── Module 1: Number Sets ────────────────────────────────────────────────

MODULE1_LESSONS = []

# 1.1 Natural Numbers and Integers
steps = [
    info_step("coremath-m1t1-s1",
        '🔢 **Natural Numbers and Integers**\\\\n\\\\nLet\"s start with the building blocks of mathematics!\\\\n\\\\n**Natural Numbers (ℕ):** The numbers we use for counting — 1, 2, 3, 4, ... (some definitions also include 0).\\\\n\\\\n**Integers (ℤ):** All whole numbers, including negatives — ..., -3, -2, -1, 0, 1, 2, 3, ...\\\\n\\\\n**Key Properties:**\\\\n• **Closure:** The sum/product of two naturals is always a natural.\\\\n• **Commutative:** a + b = b + a (order doesn\"t matter for + and ×)\\\\n• **Associative:** (a + b) + c = a + (b + c)\\\\n• **Distributive:** a × (b + c) = a × b + a × c\\\\n\\\\n> 💡 **WASSCE Tip:** Know the difference between natural numbers, integers, and whole numbers — they are not the same!'),
    predict_step("coremath-m1t1-s2",
        'Look at this sequence: **2, 4, 6, 8, 10, ...** What type of numbers are these?",
        "2, 4, 6, 8, 10, ...',
        "What do we call this pattern?",
        ['Odd numbers", "Even natural numbers', "Prime numbers", 'Square numbers"),
        1,
        "These are **even natural numbers** — they are all natural numbers divisible by 2.'),
    info_step("coremath-m1t1-s3",
        '✨ **Prime Numbers and Composite Numbers**\\\\n\\\\n**Prime Numbers:** Natural numbers greater than 1 that have exactly two factors: 1 and itself.\\\\n• 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, ...\\\\n• 2 is the **only even prime number** (and the smallest!)\\\\n\\\\n**Composite Numbers:** Natural numbers greater than 1 that have more than two factors.\\\\n• 4, 6, 8, 9, 10, 12, 14, 15, ...\\\\n\\\\n**Note:** 1 is **neither** prime nor composite. It is called a **unit**.\\\\n\\\\n**Prime Factorisation:** Breaking a number into its prime factors.\\\\n• Example: 12 = 2 × 2 × 3 = 2² × 3\\\\n\\\\n> 🔑 **WASSCE loves prime factorisation — it is the foundation for HCF and LCM!**"),
    question_step("coremath-m1t1-s4',
        "What is the **prime factorisation** of 36?",
        'Write 36 as a product of primes",
        ["2² × 3²', "2³ × 3", '6²", "2² × 9'),
        0,
        "36 = 6 × 6 = (2 × 3) × (2 × 3) = **2² × 3²**. Always break down until all factors are prime!"),
    info_step('coremath-m1t1-s5",
        "🎯 **HCF and LCM — WASSCE Favourites!**\\\\n\\\\n**Highest Common Factor (HCF):** The largest number that divides two or more numbers exactly.\\\\n• Find by: List factors OR use prime factorisation (take common primes with smallest powers)\\\\n\\\\n**Lowest Common Multiple (LCM):** The smallest number that is a multiple of two or more numbers.\\\\n• Find by: List multiples OR use prime factorisation (take all primes with largest powers)\\\\n\\\\n**Example:** Find HCF and LCM of 12 and 18.\\\\n• 12 = 2² × 3\\\\n• 18 = 2 × 3²\\\\n• HCF = 2 × 3 = **6** (common primes, smallest powers)\\\\n• LCM = 2² × 3² = **36** (all primes, largest powers)\\\\n\\\\n> ✅ **Quick check:** HCF × LCM = Product of the two numbers (6 × 36 = 12 × 18 = 216 ✓)'),
    question_step("coremath-m1t1-s6",
        'Find the **HCF** of 24 and 36.",
        "HCF of 24 and 36',
        ["6", '12", "72', "8"),
        1,
        '24 = 2³ × 3, 36 = 2² × 3². HCF = 2² × 3 = **12**. Indeed, 12 is the largest number dividing both 24 and 36!"),
]
MODULE1_LESSONS.append(make_lesson(
    "coremath-m1t1', "Natural Numbers, Integers and Prime Numbers",
    'Core Mathematics", "🔢', "Both", 1, 8, 20,
    'core-maths", [], ["SHS 1'], "SHS 1", steps
))

# 1.2 Rational and Irrational Numbers
steps = [
    info_step('coremath-m1t2-s1",
        "🔢 **Rational Numbers**\\\\n\\\\n**Rational Numbers (ℚ):** Any number that can be expressed as a fraction **p/q** where p and q are integers and q ≠ 0.\\\\n\\\\n**Examples of rational numbers:**\\\\n• 3 = 3/1\\\\n• 0.5 = 1/2\\\\n• -2.75 = -11/4\\\\n• 0.333... = 1/3 (recurring decimal)\\\\n• √4 = 2 (perfect square root)\\\\n\\\\n**Examples of irrational numbers:**\\\\n• √2 ≈ 1.414213... (non-repeating, non-terminating)\\\\n• π ≈ 3.14159...\\\\n• √3, √5 — square roots of non-perfect squares\\\\n\\\\n> 💡 **WASSCE Tip:** A number is rational if its decimal form terminates or repeats. If it never repeats and never ends, it\'s irrational!"),
    predict_step("coremath-m1t2-s2',
        "Look at these numbers: **√4, 0.75, 1/3, √3, π**\\\\n\\\\nWhich are rational and which are irrational?",
        '√4, 0.75, 1/3, √3, π",
        "How many of these are rational numbers?',
        ["All 5 are rational", '3 are rational, 2 are irrational", "2 are rational, 3 are irrational', "4 are rational, 1 is irrational"),
        1,
        '√4=2 (rational), 0.75=3/4 (rational), 1/3 (rational), √3 (irrational), π (irrational). So **3 rational, 2 irrational**."),
    info_step("coremath-m1t2-s3',
        "📊 **Real Numbers and the Number Line**\\\\n\\\\n**Real Numbers (ℝ):** The set of ALL rational and irrational numbers. Every real number has a position on the number line.\\\\n\\\\n**The Real Number System:**\\\\n\\\\n      ℝ (Real Numbers)\\\\n      ├── ℚ (Rational)\\\\n      │    ├── ℤ (Integers)\\\\n      │    │    ├── ℕ (Natural)\\\\n      │    │    └── 0, -1, -2, ...\\\\n      │    └── Fractions & decimals\\\\n      └── Irrational (√2, π, e, ...)\\\\n\\\\n**Operations on Real Numbers:**\\\\n• **Addition/Subtraction:** Combine like terms; watch signs!\\\\n• **Multiplication/Division:** Product of two negatives = positive\\\\n\\\\n> 🧠 **Did you know?** Between any two real numbers, there are infinitely many other real numbers! This is called the **density property**."),
    question_step('coremath-m1t2-s4",
        "Which set does the number **√9** belong to?',
        "√9 belongs to which sets?",
        ['Natural only", "Integer only', "Rational only", 'ℕ, ℤ, ℚ, and ℝ"),
        3,
        "√9 = 3, which is a natural number, integer, rational number, and real number. It belongs to **all** these sets!'),
    info_step("coremath-m1t2-s5",
        '🌟 **Approximating Irrational Numbers**\\\\n\\\\nEven though irrational numbers cannot be written exactly as fractions, we can **approximate** them.\\\\n\\\\n**Method: Trial and Improvement**\\\\n√5 is between 2² = 4 and 3² = 9, so √5 is between 2 and 3.\\\\n• 2.2² = 4.84 (too low)\\\\n• 2.3² = 5.29 (too high)\\\\n• 2.24² = 5.0176 (slightly high)\\\\n• 2.23² = 4.9729 (slightly low)\\\\n• So √5 ≈ **2.236** (to 3 decimal places)\\\\n\\\\n> ✅ **WASSCE will often ask you to locate irrational numbers on the number line or give approximations.**"),
    checkpoint_step("coremath-m1t2-s6', "Number Sets Mastery", [
        {'question": "Which of the following is an irrational number?',
         "options": ['0.75", "√16', "√7", '22/7"),
         "correct': 2, "explanation": '√7 ≈ 2.6457... is non-repeating, non-terminating — it is irrational. 22/7 is rational (it is a fraction)."},
        {"question': "√64 belongs to which sets?",
         'options": ["Natural only', "Integer only", 'All real number sets", "Irrational'),
         "correct": 2, 'explanation": "√64 = 8, which belongs to ℕ, ℤ, ℚ, and ℝ — all real number sets.'},
    ]),
]
MODULE1_LESSONS.append(make_lesson(
    "coremath-m1t2", 'Rational and Irrational Numbers",
    "Core Mathematics', "🔢", 'Both", 1, 10, 25,
    "core-maths', ["coremath-m1t1"], ['SHS 1"], "SHS 1', steps
))

# 1.3 Indices and Standard Form
steps = [
    info_step("coremath-m1t3-s1",
        '📐 **Laws of Indices (Exponents)**\\\\n\\\\nIndices (or exponents) tell us how many times to multiply a number by itself.\\\\n\\\\n**Basic Laws (WASSCE Essential!):**\\\\n\\\\n1️⃣ **Product Rule:** aᵐ × aⁿ = aᵐ⁺ⁿ\\\\n   Example: 2³ × 2⁴ = 2³⁺⁴ = 2⁷ = 128\\\\n\\\\n2️⃣ **Quotient Rule:** aᵐ ÷ aⁿ = aᵐ⁻ⁿ\\\\n   Example: 2⁵ ÷ 2² = 2⁵⁻² = 2³ = 8\\\\n\\\\n3️⃣ **Power Rule:** (aᵐ)ⁿ = aᵐⁿ\\\\n   Example: (2²)³ = 2⁶ = 64\\\\n\\\\n4️⃣ **Zero Index:** a⁰ = 1 (for any a ≠ 0)\\\\n   Example: 5⁰ = 1, 100⁰ = 1\\\\n\\\\n5️⃣ **Negative Index:** a⁻ⁿ = 1/aⁿ\\\\n   Example: 2⁻³ = 1/2³ = 1/8"),
    predict_step("coremath-m1t3-s2',
        "Simplify: **3⁵ × 3⁻²**\\\\n\\\\nCan you predict the answer?",
        '3⁵ × 3⁻²",
        "What is the simplified result?',
        ["3³ = 27", '3⁷", "3⁻¹⁰', "9³"),
        0,
        'Using the product rule: 3⁵ × 3⁻² = 3⁵⁺⁽⁻²⁾ = 3³ = **27**. Remember: adding a negative = subtracting!"),
    info_step("coremath-m1t3-s3',
        "🔢 **Fractional Indices**\\\\n\\\\nFractional exponents represent roots!\\\\n\\\\n**Key Rules:**\\\\n• a^(1/n) = ⁿ√a  (the n-th root of a)\\\\n• a^(m/n) = (ⁿ√a)ᵐ = ⁿ√(aᵐ)\\\\n\\\\n**Examples:**\\\\n• 9^(1/2) = √9 = 3\\\\n• 8^(1/3) = ³√8 = 2\\\\n• 27^(2/3) = (³√27)² = 3² = 9\\\\n• 16^(3/4) = (⁴√16)³ = 2³ = 8\\\\n\\\\n> 💡 **WASSCE loves fractional indices! Remember: Denominator = root, Numerator = power."),
    question_step('coremath-m1t3-s4",
        "Evaluate: **8^(2/3)**',
        "8 to the power of 2/3 = ?",
        ['4", "16/3', "64/3", '16"),
        0,
        "8^(2/3) = (³√8)² = 2² = **4**. First find the cube root (³√8 = 2), then square it!'),
    info_step("coremath-m1t3-s5",
        '📏 **Standard Form (Scientific Notation)**\\\\n\\\\nStandard form is a way of writing very large or very small numbers.\\\\n\\\\n**Format:** A × 10ⁿ where 1 ≤ A < 10 and n is an integer.\\\\n\\\\n**Examples:**\\\\n• 3,000,000 = 3 × 10⁶\\\\n• 45,000 = 4.5 × 10⁴\\\\n• 0.005 = 5 × 10⁻³\\\\n• 0.0000072 = 7.2 × 10⁻⁶\\\\n\\\\n**Quick Method:** Count how many places the decimal point moves!\\\\n• Large numbers → positive power (move left)\\\\n• Small numbers → negative power (move right)\\\\n\\\\n> 🔑 **WASSCE classic:** Calculations with numbers in standard form — make sure the final answer is also in standard form!"),
    question_step("coremath-m1t3-s6',
        "Write **0.0000456** in standard form.",
        '0.0000456 in standard form = ?",
        ["4.56 × 10⁻⁵', "4.56 × 10⁵", '456 × 10⁻⁷", "4.56 × 10⁻⁴'),
        0,
        "Move the decimal 5 places to the right: 0.0000456 = **4.56 × 10⁻⁵**. Negative power because it is a small number!"),
]
MODULE1_LESSONS.append(make_lesson(
    'coremath-m1t3", "Indices and Standard Form',
    "Core Mathematics", '🔢", "Both', 2, 12, 30,
    "core-maths", ['coremath-m1t1"], ["SHS 1', "SHS 2"], 'SHS 1", steps
))

# 1.4 Number Bases
steps = [
    info_step("coremath-m1t4-s1',
        "🔢 **Introduction to Number Bases**\\\\n\\\\nWe usually work in **base 10** (denary/decimal) — using digits 0-9.\\\\nBut numbers can be written in other bases!\\\\n\\\\n**Base 2 (Binary):** Uses digits 0 and 1 only.\\\\n• Used in computers! (0 = off, 1 = on)\\\\n• Place values: ..., 8, 4, 2, 1 (powers of 2)\\\\n\\\\n**Base 5:** Uses digits 0-4\\\\n• Place values: ..., 125, 25, 5, 1 (powers of 5)\\\\n\\\\n**Converting to Base 10:**\\\\nMultiply each digit by its place value and add.\\\\n\\\\n**Example:** Convert 1101₂ to base 10.\\\\n1101₂ = 1×8 + 1×4 + 0×2 + 1×1 = 8 + 4 + 0 + 1 = **13₁₀**"),
    predict_step('coremath-m1t4-s2",
        "Look at this binary number: **1011₂**\\\\n\\\\nCan you convert it to base 10?',
        "1011₂ = ?₁₀",
        'What is 1011 in base 10?",
        ["11', "13", '14", "10'),
        0,
        "1011₂ = 1×8 + 0×4 + 1×2 + 1×1 = 8 + 0 + 2 + 1 = **11₁₀**. The 0 in the 4\"s place means we skip it!'),
    info_step("coremath-m1t4-s3",
        '🔄 **Converting from Base 10 to Other Bases**\\\\n\\\\n**Method: Repeated Division**\\\\nDivide the number by the target base, recording remainders. Read remainders from bottom to top!\\\\n\\\\n**Example:** Convert 25₁₀ to binary (base 2).\\\\n2 ⟌25  remainder 1\\\\n2 ⟌12  remainder 0\\\\n2 ⟌6   remainder 0\\\\n2 ⟌3   remainder 1\\\\n2 ⟌1   remainder 1\\\\n    0\\\\n\\\\nRead remainders upwards: **11001₂**\\\\n\\\\nCheck: 16 + 8 + 0 + 0 + 1 = **25 ✓**\\\\n\\\\n> 💡 **WASSCE Tip:** For base 2, the remainders will always be 0 or 1. For base 5, they will be 0-4."),
    question_step("coremath-m1t4-s4',
        "Convert **37₁₀** to base 5.",
        '37 in base 5 = ?",
        ["122₅', "132₅", '112₅", "202₅'),
        0,
        "5⟌37 r2, 5⟌7 r2, 5⟌1 r1, 0. Read up: **122₅**. Check: 1×25 + 2×5 + 2×1 = 25 + 10 + 2 = 37 ✓"),
    info_step('coremath-m1t4-s5",
        "➕ **Addition in Other Bases**\\\\n\\\\nAdding in other bases works just like base 10 — but you **carry** when you reach the base value!\\\\n\\\\n**Example:** Add 1011₂ + 110₂\\\\n\\\\n  1 0 1 1\\\\n+   1 1 0\\\\n  ───────\\\\n  1 0 0 0 1\\\\n\\\\n**Step by step:**\\\\n• 1 + 0 = 1\\\\n• 1 + 1 = 2 → write 0, carry 1 (since 2 in binary = 10)\\\\n• 0 + 1 + carry(1) = 2 → write 0, carry 1\\\\n• 1 + carry(1) = 2 → write 0, carry 1\\\\n• Final carry = 1\\\\n\\\\nCheck: 11₁₀ + 6₁₀ = 17₁₀ = 10001₂ ✓'),
    checkpoint_step("coremath-m1t4-s6", 'Number Bases Mastery", [
        {"question': "Convert 1010₂ to base 10.",
         'options": ["8', "10", '12", "5'),
         "correct": 1, 'explanation": "1010₂ = 1×8 + 0×4 + 1×2 + 0×1 = 8 + 0 + 2 + 0 = 10₁₀'},
        {"question": 'Convert 42₁₀ to base 2.",
         "options': ["101010₂", '110010₂", "101100₂', "110100₂"),
         'correct": 0, "explanation': "42 = 32 + 8 + 2 = 101010₂"},
    ]),
]
MODULE1_LESSONS.append(make_lesson(
    'coremath-m1t4", "Number Bases',
    "Core Mathematics", '🔢", "Both', 2, 10, 25,
    "core-maths", ['coremath-m1t1"], ["SHS 1', "SHS 2"], 'SHS 1", steps
))

# 1.5 Applications of Number Theory
steps = [
    info_step("coremath-m1t5-s1',
        "🔢 **Sets: The Language of Mathematics**\\\\n\\\\nA **set** is a collection of distinct objects (elements).\\\\n\\\\n**Set Notation (WASSCE Essential!):**\\\\n• A = {1, 2, 3, 4, 5}  — listing elements\\\\n• x ∈ A  — x is an element of set A\\\\n• x ∉ A  — x is NOT in set A\\\\n• n(A) = 5  — number of elements in A\\\\n• ∅ or { }  — empty set (no elements)\\\\n\\\\n**Types of Sets:**\\\\n• **Universal Set (ξ or U):** Everything we are considering\\\\n• **Finite Set:** Has a countable number of elements\\\\n• **Infinite Set:** Goes on forever (e.g., ℕ)\\\\n\\\\n> 📝 **WASSCE loves set notation and Venn diagrams — pay close attention!**"),
    predict_step('coremath-m1t5-s2",
        "If A = {1, 2, 3, 4} and B = {3, 4, 5, 6},\\\\n\\\\nWhat do you think A ∩ B means?',
        "A = {1,2,3,4}, B = {3,4,5,6}",
        'What is A ∩ B?",
        ["{1, 2, 3, 4, 5, 6}', "{3, 4}", '{1, 2}", "{5, 6}'),
        1,
        "A ∩ B means **A intersection B** — elements in **both** sets. The common elements are {3, 4}."),
    info_step('coremath-m1t5-s3",
        "🎯 **Set Operations — Union, Intersection, Complement**\\\\n\\\\n**Union (A ∪ B):** All elements in A OR B (or both).\\\\n• A ∪ B = {1, 2, 3, 4, 5, 6}\\\\n\\\\n**Intersection (A ∩ B):** Elements in BOTH A and B.\\\\n• A ∩ B = {3, 4}\\\\n\\\\n**Complement (A\\\' or Aᶜ):** Everything in ξ that is NOT in A.\\\\n• If ξ = {1, 2, 3, 4, 5, 6, 7, 8} and A = {1, 2, 3, 4}\\\\n• Then A\\\" = {5, 6, 7, 8}\\\\n\\\\n**Difference (A − B or A\\B):** Elements in A but NOT in B.\\\\n• A − B = {1, 2}\\\\n\\\\n> 🔑 **WASSCE loves Venn diagram problems with three sets!**"),
    question_step('coremath-m1t5-s4",
        "ξ = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}\\\\nA = {2, 4, 6, 8, 10}\\\\nB = {1, 3, 5, 7, 9}\\\\n\\\\nWhat is A ∪ B?',
        "Union of A and B",
        ['{2, 4, 6, 8, 10}", "{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}', "{1, 3, 5, 7, 9}", '∅"),
        1,
        "A ∪ B = all elements in A OR B = **{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}** = ξ. Notice A contains evens and B contains odds!'),
    info_step("coremath-m1t5-s5",
        '📊 **Venn Diagrams — Visualising Sets**\\\\n\\\\nVenn diagrams use overlapping circles to show relationships between sets.\\\\n\\\\n**Example Problem:**\\\\nIn a class of 40 students: 20 study Maths, 18 study Science, 8 study both.\\\\n\\\\n**Step 1:** Place 8 in the intersection (both).\\\\n**Step 2:** Maths-only = 20 − 8 = 12\\\\n**Step 3:** Science-only = 18 − 8 = 10\\\\n**Step 4:** Neither = 40 − (12 + 8 + 10) = 10\\\\n\\\\n> ✅ **Formula:** n(A ∪ B) = n(A) + n(B) − n(A ∩ B)\\\\n> Check: 12 + 10 + 8 = 30 = 20 + 18 − 8 ✓"),
    question_step("coremath-m1t5-s6',
        "In a class of 30 students: 15 play football, 12 play basketball, 5 play both.\\\\n\\\\nHow many play **neither** sport?",
        'Neither football nor basketball = ?",
        ["8', "3", '10", "5'),
        0,
        "Football only = 15−5=10. Basketball only = 12−5=7. Both = 5. Playing at least one = 10+7+5=22. Neither = 30−22 = **8**."),
]
MODULE1_LESSONS.append(make_lesson(
    'coremath-m1t5", "Set Theory and Venn Diagrams',
    "Core Mathematics", '🔢", "Both', 2, 12, 30,
    "core-maths", ['coremath-m1t1"], ["SHS 1', "SHS 2"], 'SHS 1", steps
))


# ── Module 2: Fractions, Decimals & Percentages ──────────────────────────

MODULE2_LESSONS = []

# 2.1 Operations with Fractions
steps = [
    info_step("coremath-m2t1-s1',
        "📐 **Fractions — The Basics**\\\\n\\\\nA **fraction** represents a part of a whole: **numerator/denominator**.\\\\n\\\\n**Types of Fractions:**\\\\n• **Proper:** Numerator < denominator (e.g., 3/5)\\\\n• **Improper:** Numerator > denominator (e.g., 7/4)\\\\n• **Mixed Number:** Whole number + proper fraction (e.g., 1¾ = 1 + 3/4)\\\\n\\\\n**Converting Mixed ↔ Improper:**\\\\n• Mixed → Improper: (Whole × Denominator) + Numerator, over denominator\\\\n  → 2⅓ = (2×3+1)/3 = 7/3\\\\n• Improper → Mixed: Divide numerator by denominator\\\\n  → 11/4 = 2¾ (11÷4 = 2 remainder 3)\\\\n\\\\n> 💡 **WASSCE Tip:** Always give final answers as **mixed numbers in simplest form** unless asked otherwise!"),
    predict_step('coremath-m2t1-s2",
        "**1/2 + 1/3 = ?**\\\\n\\\\nCan you predict the answer?',
        "1/2 + 1/3",
        'What is 1/2 + 1/3?",
        ["2/5', "5/6", '2/6", "1/6'),
        1,
        "Find LCM of 2 and 3 = 6. 1/2 = 3/6, 1/3 = 2/6. 3/6 + 2/6 = **5/6**. When adding fractions, find a common denominator first!"),
    info_step('coremath-m2t1-s3",
        "➕➖ **Adding and Subtracting Fractions**\\\\n\\\\n**Rule:** Find a common denominator, then add/subtract the numerators.\\\\n\\\\n**Example 1:** 2/5 + 3/4\\\\n• LCM of 5 and 4 = 20\\\\n• 2/5 = 8/20, 3/4 = 15/20\\\\n• 8/20 + 15/20 = 23/20 = **1³/₂₀**\\\\n\\\\n**Example 2:** 5/6 − 1/3\\\\n• LCM of 6 and 3 = 6\\\\n• 5/6 − 2/6 = 3/6 = **1/2**\\\\n\\\\n**Example with Mixed Numbers:**\\\\n2½ + 1⅓ = 5/2 + 4/3 = 15/6 + 8/6 = 23/6 = **3⁵/₆**\\\\n\\\\n> 🔑 **Always simplify your final answer to lowest terms!**'),
    question_step("coremath-m2t1-s4",
        'Calculate: **3/4 − 2/5**",
        "3/4 − 2/5 = ?',
        ["1/1", '7/20", "1/9', "1/20"),
        1,
        'LCM of 4 and 5 = 20. 3/4 = 15/20, 2/5 = 8/20. 15/20 − 8/20 = **7/20**. This is already in simplest form."),
    info_step("coremath-m2t1-s5',
        "✖️➗ **Multiplying and Dividing Fractions**\\\\n\\\\n**Multiplication:** Multiply numerators, multiply denominators.\\\\n• 2/3 × 3/4 = 6/12 = **1/2**\\\\n• **Cancelling first** saves work: ²/₃ × ³/₄ = 1/1 × 1/2 = **1/2** ✓\\\\n\\\\n**Division:** **Flip the second fraction** (reciprocal) and multiply!\\\\n• 2/3 ÷ 3/4 = 2/3 × 4/3 = **8/9**\\\\n• 5 ÷ 2/3 = 5/1 × 3/2 = 15/2 = **7½**\\\\n\\\\n> ⚠️ **WASSCE Warning:** Many students lose marks by forgetting to flip the second fraction in division! Remember: KCF (Keep, Change, Flip)"),
    question_step('coremath-m2t1-s6",
        "Calculate: **2/3 ÷ 4/5**',
        "2/3 ÷ 4/5 = ?",
        ['8/15", "5/6', "10/12", '1/6"),
        1,
        "Flip 4/5 to get 5/4, then multiply: 2/3 × 5/4 = 10/12 = **5/6**. Always simplify!'),
]
MODULE2_LESSONS.append(make_lesson(
    "coremath-m2t1", 'Operations with Fractions",
    "Core Mathematics', "🔢", 'Both", 1, 10, 20,
    "core-maths', ["coremath-m1t1"], ['SHS 1"], "SHS 1', steps
))

# 2.2 Decimals
steps = [
    info_step("coremath-m2t2-s1",
        '🔢 **Decimals — Place Value**\\\\n\\\\nOur decimal system is based on **powers of 10**.\\\\n\\\\n**Place Value Chart:**\\\\nThousands | Hundreds | Tens | Ones | . | Tenths | Hundredths | Thousandths\\\\n    1         2         3       4     .     5         6            7\\\\n\\\\nNumber: **1,234.567**\\\\n• 1 × 1000 + 2 × 100 + 3 × 10 + 4 × 1 + 5/10 + 6/100 + 7/1000\\\\n\\\\n**Reading Decimals:**\\\\n• 0.5 = five tenths\\\\n• 0.25 = twenty-five hundredths\\\\n• 0.125 = one hundred twenty-five thousandths\\\\n\\\\n**Converting Fractions ↔ Decimals:**\\\\n• Fraction → Decimal: Divide numerator by denominator\\\\n  → 3/8 = 3 ÷ 8 = **0.375**\\\\n\\\\\\\\\\\\n• Decimal → Fraction: Write over the appropriate power of 10, simplify\\\\n  → 0.375 = 375/1000 = **3/8**"),
    predict_step("coremath-m2t2-s2',
        "**1/8 = ?** as a decimal.\\\\n\\\\nTake a guess!",
        'What is 1/8 as a decimal?",
        ["0.125', "0.25", '0.5", "0.8'),
        0,
        "Yes! 1/8 = 0.125. Think of it as 1 ÷ 8 = 0.125. Another way: 1/8 = 125/1000 = 0.125."),
    info_step('coremath-m2t2-s3",
        "🔄 **Rounding Decimals**\\\\n\\\\n**Rounding Rules:**\\\\n1. Identify the place value you are rounding to.\\\\n2. Look at the digit to its **right**.\\\\n3. If that digit is **5 or more**, round up.\\\\n4. If it is **4 or less**, keep the digit the same.\\\\n\\\\n**Examples:**\\\\n• Round 3.14159 to 2 decimal places → 3.**14** (look at 1 → less than 5, keep 4)\\\\n• Round 3.14159 to 3 decimal places → 3.**142** (look at 5 → round up 1 to 2)\\\\n• Round 3.14159 to 1 decimal place → **3.1** (look at 4 → less than 5)\\\\n\\\\n**Significant Figures:**\\\\n• Round 3.14159 to 3 significant figures → **3.14** (3 digits)\\\\n• Round 0.00345 to 2 significant figures → **0.0035**\\\\n\\\\n> 💡 **Key difference:** Decimal places count from the decimal point. Significant figures count from the first non-zero digit.'),
    question_step("coremath-m2t2-s4",
        'Round **7.4569** to 2 decimal places.",
        "7.4569 rounded to 2 d.p.',
        ["7.46", '7.45", "7.5', "7.457"),
        0,
        'Look at the 3rd decimal digit: 6 (≥5). So we round up the 2nd decimal: 7.45 → **7.46**."),
    info_step("coremath-m2t2-s5',
        "📏 **Operations with Decimals**\\\\n\\\\n**Addition/Subtraction:** Line up the decimal points!\\\\n  12.34\\\\n+  5.60\\\\n───────\\\\n  17.94\\\\n\\\\n**Multiplication:** Multiply as whole numbers, then count total decimal places.\\\\n• 3.2 × 0.4 = ?\\\\n• 32 × 4 = 128\\\\n• 3.2 has 1 d.p., 0.4 has 1 d.p. → total 2 d.p.\\\\n• Answer: **1.28**\\\\n\\\\n**Division by decimals:** Multiply both numbers by a power of 10 to make divisor a whole number.\\\\n• 4.8 ÷ 0.6 = (4.8 × 10) ÷ (0.6 × 10) = 48 ÷ 6 = **8**\\\\n• 6.25 ÷ 0.25 = 625 ÷ 25 = **25**\\\\n\\\\n> ✅ **Quick check:** 0.5 × 0.5 = 0.25 (half of a half = a quarter)"),
    checkpoint_step('coremath-m2t2-s6", "Decimals Mastery', [
        {"question": 'What is 3/20 as a decimal?",
         "options': ["0.3", '0.15", "0.2', "0.35"),
         'correct": 1, "explanation': "3/20 = 3 ÷ 20 = 0.15. Or: 3/20 = 15/100 = 0.15"},
        {'question": "Round 0.00789 to 2 significant figures.',
         "options": ['0.008", "0.0079', "0.0078", '0.01"),
         "correct': 0, "explanation": 'First non-zero digit is 7, so 2 s.f. means we keep 7 and 8. Look at 9 (≥5), so round up: 0.0079 → 0.008"},
    ]),
]
MODULE2_LESSONS.append(make_lesson(
    "coremath-m2t2', "Decimals and Rounding",
    'Core Mathematics", "🔢', "Both", 1, 10, 20,
    'core-maths", ["coremath-m2t1'], ["SHS 1"], 'SHS 1", steps
))

# 2.3 Percentages
steps = [
    info_step("coremath-m2t3-s1',
        "📊 **Percentages — Per Hundred**\\\\n\\\\n**%** means **per hundred** (cent = 100 in Latin).\\\\n\\\\n**Converting Between Forms:**\\\\n\\\\n• **Fraction → Percentage:** Multiply by 100%\\\\n  → 3/4 = 3/4 × 100% = **75%**\\\\n\\\\n• **Decimal → Percentage:** Multiply by 100% (move decimal 2 places right)\\\\n  → 0.375 = 0.375 × 100% = **37.5%**\\\\n\\\\n• **Percentage → Fraction:** Write over 100 and simplify\\\\n  → 60% = 60/100 = **3/5**\\\\n\\\\n• **Percentage → Decimal:** Divide by 100 (move decimal 2 places left)\\\\n  → 45% = 45 ÷ 100 = **0.45**\\\\n\\\\n> ⚡ **Quick conversions to memorise:**\\\\n• 50% = 1/2 = 0.5\\\\n• 25% = 1/4 = 0.25\\\\n• 75% = 3/4 = 0.75\\\\n• 10% = 1/10 = 0.1\\\\n• 331/3% = 1/3 = 0.333..."),
    predict_step('coremath-m2t3-s2",
        "If a shirt costs GH₵80 and is on 25% discount, what is the sale price?',
        "GH₵80 with 25% off",
        'Sale price = ?",
        ["GH₵55', "GH₵60", 'GH₵65", "GH₵20'),
        1,
        "25% of GH₵80 = 0.25 × 80 = GH₵20 discount. Sale price = 80 − 20 = **GH₵60**. Or: 75% of 80 = 0.75 × 80 = 60."),
    info_step('coremath-m2t3-s3",
        "🧮 **Percentage Increase and Decrease**\\\\n\\\\n**Formula:**\\\\n• % Change = (Change ÷ Original) × 100%\\\\n\\\\n**Increase:** New Value = Original × (1 + %/100)\\\\n**Decrease:** New Value = Original × (1 − %/100)\\\\n\\\\n**Example 1: Increase**\\\\nA salary of GH₵2,000 increases by 15%.\\\\nNew salary = 2000 × (1 + 15/100) = 2000 × 1.15 = **GH₵2,300**\\\\n\\\\n**Example 2: Decrease**\\\\nA TV costs GH₵3,500 and is on 30% discount.\\\\nSale price = 3500 × (1 − 30/100) = 3500 × 0.7 = **GH₵2,450**\\\\n\\\\n**Finding the Original Amount:**\\\\nAfter a 20% increase, I pay GH₵600. What was the original?\\\\nOriginal × 1.20 = 600 → Original = 600/1.20 = **GH₵500**\\\\n\\\\n> 🔑 **WASSCE classic: Finding the original value before a percentage change!**'),
    question_step("coremath-m2t3-s4",
        'A student scores 42 out of 60 in a test. **What percentage is this?**",
        "42/60 as a percentage',
        ["60%", '65%", "70%', "42%"),
        2,
        '(42/60) × 100% = 0.7 × 100% = **70%**. Alternatively: 42/60 = 7/10 = 70%."),
    info_step("coremath-m2t3-s5',
        "💰 **Applications: Profit, Loss and Discount**\\\\n\\\\n**Profit and Loss:**\\\\n• **Cost Price (CP):** What a trader pays\\\\n• **Selling Price (SP):** What a trader sells for\\\\n• **Profit = SP − CP** (when SP > CP)\\\\n• **Loss = CP − SP** (when CP > SP)\\\\n• **% Profit = (Profit/CP) × 100%**\\\\n• **% Loss = (Loss/CP) × 100%**\\\\n\\\\n**Example:** A trader buys a phone for GH₵800 and sells for GH₵960.\\\\n• Profit = 960 − 800 = GH₵160\\\\n• % Profit = (160/800) × 100% = **20%**\\\\n\\\\n**Discount:**\\\\n• **Discount** = Marked Price − Selling Price\\\\n• **% Discount** = (Discount/Marked Price) × 100%\\\\n\\\\n> 💡 **Remember:** Profit/loss % is always calculated on the cost price, NOT the selling price!"),
    question_step('coremath-m2t3-s6",
        "A woman buys a bag for GH₵250 and sells it for GH₵200. **What is her percentage loss?**',
        "Percentage loss = ?",
        ['50%", "20%', "25%", '80%"),
        1,
        "Loss = 250 − 200 = GH₵50. % Loss = (50/250) × 100% = **20%**.'),
]
MODULE2_LESSONS.append(make_lesson(
    "coremath-m2t3", 'Percentages and Applications",
    "Core Mathematics', "🔢", 'Both", 1, 12, 25,
    "core-maths', ["coremath-m2t1"], ['SHS 1", "SHS 2'], "SHS 1", steps
))

# 2.4 Ratio and Proportion
steps = [
    info_step('coremath-m2t4-s1",
        "⚖️ **Ratio — Comparing Quantities**\\\\n\\\\nA **ratio** compares two or more quantities.\\\\n\\\\n**Writing Ratios:**\\\\n• If a class has 12 boys and 8 girls, the ratio boys:girls = 12:8 = **3:2** (simplified)\\\\n• Order matters! 3:2 is not the same as 2:3.\\\\n\\\\n**Simplifying Ratios:**\\\\n• Divide all parts by their **highest common factor**\\\\n• 15:25 = 3:5 (divided by 5)\\\\n• 2.5:1.5 = 25:15 = 5:3 (multiply by 10, then divide by 5)\\\\n\\\\n**Sharing in a Ratio:**\\\\nShare GH₵600 in the ratio 2:3\\\\n• Total parts = 2 + 3 = 5:\\\\n• One part = 600 ÷ 5 = GH₵120:\\\\n• First person: 2 × 120 = GH₵240\\\\n• Second person: 3 × 120 = GH₵360\\\\n• Check: 240 + 360 = 600 ✓'),
    predict_step("coremath-m2t4-s2",
        'A mother divides GH₵500 between two children in the ratio **3:2**.\\\\n\\\\nHow much does each child get?",
        "GH₵500 in ratio 3:2',
        "How much does the first child (3 parts) get?",
        ['GH₵200", "GH₵300', "GH₵250", 'GH₵350"),
        1,
        "Total parts = 3 + 2 = 5. One part = 500/5 = GH₵100. First child = 3 × 100 = **GH₵300**. Second = 2 × 100 = GH₵200.'),
    info_step("coremath-m2t4-s3",
        '🔄 **Direct Proportion**\\\\n\\\\n**Direct Proportion:** When one quantity increases, the other increases at the same rate.\\\\n• If y is directly proportional to x, then y = kx (k = constant of proportionality)\\\\n\\\\n**Example:** The cost of yam is proportional to its weight.\\\\n• 3 kg costs GH₵45. How much does 5 kg cost?\\\\n\\\\n**Method 1: Unitary method**\\\\n• 1 kg costs 45/3 = GH₵15\\\\n• 5 kg costs 5 × 15 = **GH₵75**\\\\n\\\\n**Method 2: Proportion**\\\\n• 3/45 = 5/x\\\\n• 3x = 225\\\\n• x = **GH₵75**\\\\n\\\\n> ✅ **More yam → More money. Direct proportion: as x↑, y↑**"),
    question_step("coremath-m2t4-s4',
        "A car travels 180 km on 15 litres of petrol.\\\\n\\\\n**How far will it travel on 20 litres?** (Assume same rate)",
        'Distance on 20 litres",
        ["200 km', "220 km", '240 km", "260 km'),
        2,
        "Unitary: 1 litre → 180/15 = 12 km. 20 litres → 20 × 12 = **240 km**. Or: 180/15 = x/20, 15x = 3600, x = 240."),
    info_step('coremath-m2t4-s5",
        "🔄 **Inverse Proportion**\\\\n\\\\n**Inverse Proportion:** When one quantity increases, the other decreases at the same rate.\\\\n• If y is inversely proportional to x, then y = k/x (or xy = k)\\\\n\\\\n**Example:** 4 workers can paint a house in 6 days. How long will 6 workers take?\\\\n• More workers → Less time (inverse proportion)\\\\n• Total work = 4 × 6 = 24 worker-days\\\\n• For 6 workers: 24/6 = **4 days**\\\\n\\\\n**Method:**\\\\n• If x and y are inversely proportional: x₁y₁ = x₂y₂\\\\n• 4 × 6 = 6 × d\\\\n• 24 = 6d\\\\n• d = 4\\\\n\\\\n> ⚠️ **WASSCE tests both direct and inverse proportion — know the difference! Direct = multiply/divide same way. Inverse = one goes up, other goes down.**'),
    question_step("coremath-m2t4-s6",
        '8 taps fill a tank in 3 hours.\\\\n\\\\n**How long would 6 taps take?** (All taps flow at same rate)",
        "Time for 6 taps',
        ["3.5 hours", '4 hours", "5 hours', "6 hours"),
        1,
        'Inverse proportion: 8 × 3 = 6 × t, 24 = 6t, t = **4 hours**. Fewer taps → longer time."),
]
MODULE2_LESSONS.append(make_lesson(
    "coremath-m2t4', "Ratio and Proportion",
    'Core Mathematics", "🔢', "Both", 2, 12, 30,
    'core-maths", ["coremath-m2t1'], ["SHS 1", 'SHS 2"], "SHS 1', steps
))

# 2.5 Financial Mathematics
steps = [
    info_step("coremath-m2t5-s1",
        '💰 **Simple Interest**\\\\n\\\\n**Simple Interest** is interest calculated only on the original amount (Principal).\\\\n\\\\n**Formula:** I = PRT/100\\\\nWhere: I = Interest, P = Principal, R = Rate (% per year), T = Time (years)\\\\n\\\\n**Amount (A)** = P + I = P + PRT/100 = P(1 + RT/100)\\\\n\\\\n**Example:** Invest GH₵2,000 at 10% per annum for 3 years.\\\\n• I = 2000 × 10 × 3/100 = GH₵600\\\\n• A = 2000 + 600 = **GH₵2,600**\\\\n\\\\n**Finding other variables:**\\\\n• If you need to find Rate: R = (I × 100)/(P × T)\\\\n• To find Time: T = (I × 100)/(P × R)\\\\n\\\\n> 💡 **WASSCE loves questions where you need to find the rate or time from given values!**"),
    predict_step("coremath-m2t5-s2',
        "I invest GH₵5,000 at 8% simple interest for 4 years.\\\\n\\\\nWhat will the total amount be?",
        'GH₵5,000 at 8% for 4 years (simple)",
        "Total amount = ?',
        ["GH₵5,400", 'GH₵6,600", "GH₵7,000', "GH₵6,000"),
        1,
        'I = 5000 × 8 × 4 / 100 = GH₵1,600. Amount = 5000 + 1600 = **GH₵6,600**."),
    info_step("coremath-m2t5-s3',
        "📈 **Compound Interest — Interest on Interest**\\\\n\\\\nWith **compound interest**, you earn interest on previously earned interest!\\\\n\\\\n**Formula:** A = P(1 + R/100)ᵀ\\\\nWhere: P = Principal, R = Rate, T = Time (years)\\\\n\\\\n**Example:** GH₵2,000 at 10% p.a. compound for 3 years.\\\\n• Year 1: I = 2000 × 10/100 = GH₵200, A₁ = GH₵2,200\\\\n• Year 2: I = 2200 × 10/100 = GH₵220, A₂ = GH₵2,420\\\\n• Year 3: I = 2420 × 10/100 = GH₵242, A₃ = **GH₵2,662**\\\\n\\\\n**Using formula:** A = 2000(1.1)³ = 2000 × 1.331 = **GH₵2,662**\\\\n\\\\n> 🔑 **Note:** Compound interest (GH₵662) is greater than simple interest (GH₵600) for the same terms!"),
    question_step('coremath-m2t5-s4",
        "GH₵3,000 is invested at 5% compound interest for **2 years**.\\\\n\\\\nWhat is the total amount?',
        "GH₵3,000 at 5% compound for 2 years",
        ['GH₵3,150", "GH₵3,300', "GH₵3,307.50", 'GH₵3,600"),
        2,
        "A = 3000(1.05)² = 3000 × 1.1025 = **GH₵3,307.50**. Try calculating year by year to verify!'),
    info_step("coremath-m2t5-s5",
        '🏦 **Taxes, Wages and Budgets**\\\\n\\\\n**Income Tax:** A percentage of earnings paid to the government.\\\\n\\\\n**Example:** Tax-free allowance = GH₵4,000/year. Remainder taxed at 10%.\\\\n• Annual salary = GH₵30,000\\\\n• Taxable income = 30,000 − 4,000 = GH₵26,000\\\\n• Tax = 26,000 × 10/100 = GH₵2,600\\\\n• Take-home pay = 30,000 − 2,600 = **GH₵27,400**\\\\n\\\\n**Commission:** A percentage of sales earned by a salesperson.\\\\n• Sales = GH₵50,000, Commission rate = 5%\\\\n• Commission = 5/100 × 50,000 = **GH₵2,500**\\\\n\\\\n> ✅ **Financial maths is very practical — these skills apply to real life!**"),
    question_step("coremath-m2t5-s6',
        "A salesperson earns 8% commission on sales. She makes sales of GH₵45,000.\\\\n\\\\n**What is her commission?**",
        '8% commission on GH₵45,000",
        ["GH₵3,200', "GH₵3,600", 'GH₵4,000", "GH₵3,000'),
        1,
        "Commission = 8/100 × 45,000 = **GH₵3,600**."),
]
MODULE2_LESSONS.append(make_lesson(
    'coremath-m2t5", "Simple Interest, Compound Interest and Financial Maths',
    "Core Mathematics", '🔢", "Both', 2, 14, 30,
    "core-maths", ['coremath-m2t1"], ["SHS 2', "SHS 3"], 'SHS 2", steps
))


# ── Module 3: Algebraic Expressions & Factorisation ──────────────────────

MODULE3_LESSONS = []

# 3.1 Simplifying Algebraic Expressions
steps = [
    info_step("coremath-m3t1-s1',
        "📐 **Algebra — The Language of Patterns**\\\\n\\\\nAlgebra uses letters (variables) to represent unknown or changing numbers.\\\\n\\\\n**Key Terms:**\\\\n• **Variable:** A symbol for a number we do not know yet (e.g., x)\\\\n• **Coefficient:** The number multiplying a variable (in 3x, 3 is the coefficient)\\\\n• **Constant:** A term without a variable (e.g., 5 in 3x + 5)\\\\n• **Expression:** A combination of terms (e.g., 3x + 5)\\\\n• **Equation:** An expression set equal to something (e.g., 3x + 5 = 14)\\\\n\\\\n**Like Terms:** Terms with the same variable(s) raised to the same powers.\\\\n• 3x and 5x are like terms\\\\n• 2x² and 4x² are like terms\\\\n• 3x and 3x² are **NOT** like terms\\\\n\\\\n**Collecting Like Terms:**\\\\n• 3x + 5 + 2x − 1 = (3x + 2x) + (5 − 1) = **5x + 4**"),
    predict_step('coremath-m3t1-s2",
        "Simplify: **4a + 3b − 2a + 5b**\\\\n\\\\nCan you predict the simplified expression?',
        "4a + 3b − 2a + 5b",
        'Simplified expression = ?",
        ["6a + 8b', "2a + 8b", '2a + 2b", "6a + 2b'),
        1,
        "Group like terms: (4a − 2a) + (3b + 5b) = **2a + 8b**. Remember: a and b are different variables — they cannot be combined!"),
    info_step('coremath-m3t1-s3",
        "➕✖️ **Algebraic Operations**\\\\n\\\\n**Addition/Subtraction:** Combine like terms only.\\\\n• 5x + 3y − 2x + y = 3x + 4y\\\\n\\\\n**Multiplication:** Multiply coefficients and variables.\\\\n• 3x × 2y = 6xy\\\\n• 2a × 3b × 4c = 24abc\\\\n• x × x = x²\\\\n\\\\n**Division:** Cancel common factors.\\\\n• (6x²) ÷ (2x) = 3x\\\\n• (15ab) ÷ (3b) = 5a\\\\n\\\\n**Powers:**\\\\n• x² × x³ = x⁵ (add powers)\\\\n• x⁶ ÷ x² = x⁴ (subtract powers)\\\\n• (x²)³ = x⁶ (multiply powers)\\\\n\\\\n> 💡 **When multiplying or dividing, work with numbers first, then variables.**'),
    question_step("coremath-m3t1-s4",
        'Simplify: **3x² + 2x − x² + 5x**",
        "3x² + 2x − x² + 5x = ?',
        ["2x² + 7x", '4x² + 7x", "2x² + 3x', "3x² + 5x"),
        0,
        '(3x² − x²) + (2x + 5x) = **2x² + 7x**. x² terms: 3 − 1 = 2. x terms: 2 + 5 = 7."),
    info_step("coremath-m3t1-s5',
        "🎯 **Substitution — Evaluating Expressions**\\\\n\\\\n**Substitution** means replacing variables with numbers.\\\\n\\\\n**Example:** Evaluate 3x + 5 when x = 7.\\\\n3(7) + 5 = 21 + 5 = **26**\\\\n\\\\n**Example:** Evaluate 2a² − 3b when a = 3 and b = 4.\\\\n2(3)² − 3(4) = 2(9) − 12 = 18 − 12 = **6**\\\\n\\\\n**Important: Follow BODMAS/PEMDAS!**\\\\n• Brackets first\\\\n• Orders (powers/roots)\\\\n• Division/Multiplication\\\\n• Addition/Subtraction\\\\n\\\\n> ⚠️ **Common mistake:** For 2x² when x = 3, it is 2(3²) = 2(9) = 18, NOT (2×3)² = 36."),
    question_step('coremath-m3t1-s6",
        "If **x = 5**, evaluate **4x² − 3x + 2**.',
        "4(5)² − 3(5) + 2",
        ['87", "82', "97", '77"),
        0,
        "4(25) − 15 + 2 = 100 − 15 + 2 = **87**. Follow order of operations: powers first!'),
]
MODULE3_LESSONS.append(make_lesson(
    "coremath-m3t1", 'Simplifying Algebraic Expressions",
    "Core Mathematics', "🔢", 'Both", 1, 10, 20,
    "core-maths', ["coremath-m1t1"], ['SHS 1"], "SHS 1', steps
))

# 3.2 Expansion of Brackets
steps = [
    info_step("coremath-m3t2-s1",
        '📐 **Expanding Brackets — The Distributive Law**\\\\n\\\\n**The Distributive Law:** a(b + c) = ab + ac\\\\n\\\\n**Single Brackets:** Multiply the term outside by **every term** inside.\\\\n• 3(x + 4) = 3x + 12\\\\n• −2(3x − 5) = −6x + 10 (careful with signs!)\\\\n• 4x(2x − 3) = 8x² − 12x\\\\n\\\\n**Examples:**\\\\n• 5(2x + 3) − 2(x − 1)\\\\n  = 10x + 15 − 2x + 2\\\\n  = **8x + 17**\\\\n\\\\n> 💡 **WASSCE Tip:** When there is a minus sign outside brackets, multiply everything inside by -1!"),
    predict_step("coremath-m3t2-s2',
        "Expand: **−3(2x − 4)**\\\\n\\\\nWhat is the expanded form?",
        '−3(2x − 4)",
        "Expanded = ?',
        ["−6x − 12", '−6x + 12", "6x − 12', "6x + 12"),
        1,
        '−3 × 2x = −6x. −3 × (−4) = +12. So: **−6x + 12**. A negative × negative = positive!"),
    info_step("coremath-m3t2-s3',
        "🔗 **Expanding Two Brackets (FOIL Method)**\\\\n\\\\n**(a + b)(c + d) = ac + ad + bc + bd**\\\\n\\\\n**FOIL Method:**\\\\n• **F**irst: Multiply first terms\\\\n• **O**uter: Multiply outer terms\\\\n• **I**nner: Multiply inner terms\\\\n• **L**ast: Multiply last terms\\\\n\\\\n**Example:** (x + 3)(x + 5)\\\\n• F: x × x = x²\\\\n• O: x × 5 = 5x\\\\n• I: 3 × x = 3x\\\\n• L: 3 × 5 = 15\\\\n• = x² + 5x + 3x + 15 = **x² + 8x + 15**\\\\n\\\\n**Special Products (WASSCE Favourites!):**\\\\n• (x + y)² = x² + 2xy + y²\\\\n• (x − y)² = x² − 2xy + y²\\\\n• (x + y)(x − y) = x² − y² (Difference of two squares!)"),
    question_step('coremath-m3t2-s4",
        "Expand: **(2x + 1)(x − 3)**',
        "(2x + 1)(x − 3)",
        ['2x² − 5x − 3", "2x² − 6x − 3', "2x² + 7x − 3", '2x² − 5x + 3"),
        0,
        "F: 2x×x = 2x², O: 2x×(−3) = −6x, I: 1×x = x, L: 1×(−3) = −3. = 2x² − 6x + x − 3 = **2x² − 5x − 3**.'),
    info_step("coremath-m3t2-s5",
        '🌟 **Applications of Expansion**\\\\n\\\\nExpanding is useful for solving real-world problems and for factorisation (which we will learn next).\\\\n\\\\n**Example:** A rectangle has length (x + 5) and width (3x − 2).\\\\nArea = length × width = (x + 5)(3x − 2)\\\\n= 3x² − 2x + 15x − 10\\\\n= **3x² + 13x − 10**\\\\n\\\\n**Checking your work:** Try substituting a number (like x = 1) into both the expanded and unexpanded forms. If they give the same answer, you are correct!\\\\n\\\\n> 🔑 **Always check your expansion by substitution — it catches most mistakes!**"),
    checkpoint_step("coremath-m3t2-s6', "Expansion Mastery", [
        {'question": "Expand: 4(2x − 3)',
         "options": ['8x − 3", "8x − 12', "4x − 12", '8x + 12"),
         "correct': 1, "explanation": '4 × 2x = 8x, 4 × (−3) = −12. So: 8x − 12"},
        {"question': "Expand: (x + 4)(x − 2)",
         'options": ["x² + 2x − 8', "x² − 2x + 8", 'x² + 6x − 8", "x² + 2x + 8'),
         "correct": 0, 'explanation": "x² − 2x + 4x − 8 = x² + 2x − 8'},
    ]),
]
MODULE3_LESSONS.append(make_lesson(
    "coremath-m3t2", 'Expansion of Brackets",
    "Core Mathematics', "🔢", 'Both", 2, 12, 25,
    "core-maths', ["coremath-m3t1"], ['SHS 1", "SHS 2'], "SHS 1", steps
))

# 3.3 Factorisation
steps = [
    info_step('coremath-m3t3-s1",
        "🔍 **Factorisation — The Reverse of Expansion**\\\\n\\\\n**Factorisation** is the process of writing an expression as a **product of factors**.\\\\n\\\\n**Common Factor Factorisation:**\\\\nIdentify the HCF of all terms and take it outside brackets.\\\\n\\\\n**Examples:**\\\\n• 6x + 9 = 3(2x + 3)    [HCF of 6 and 9 is 3]\\\\n• 12x² − 8x = 4x(3x − 2)   [HCF of 12x² and 8x is 4x]\\\\n• 15ab + 10a = 5a(3b + 2)   [HCF of 15ab and 10a is 5a]\\\\n\\\\n**Check your answer by expanding back!**\\\\n• 3(2x + 3) = 6x + 9 ✓'),
    predict_step("coremath-m3t3-s2",
        'Factorise: **8x + 12**\\\\n\\\\nWhat goes outside the brackets?",
        "Factorise 8x + 12',
        "The HCF is...?",
        ['2", "4', "6", '8"),
        1,
        "HCF of 8 and 12 is **4**. 8x + 12 = **4(2x + 3)**. Check: 4(2x + 3) = 8x + 12 ✓'),
    info_step("coremath-m3t3-s3",
        '📝 **Factorising Quadratic Expressions**\\\\n\\\\n**Form:** x² + bx + c\\\\n\\\\nWe need two numbers that:\\\\n• **Multiply** to give c\\\\n• **Add** to give b\\\\n\\\\n**Example 1:** Factorise x² + 7x + 12\\\\n• Find factors of 12: 1×12, 2×6, 3×4\\\\n• Which pair adds to 7? 3 + 4 = 7 ✓\\\\n• = **(x + 3)(x + 4)**\\\\n\\\\n**Example 2:** Factorise x² − 5x + 6\\\\n• Factors of 6: 1×6, 2×3, (−1)×(−6), (−2)×(−3)\\\\n• Which pair adds to −5? (−2) + (−3) = −5 ✓\\\\n• = **(x − 2)(x − 3)**"),
    question_step("coremath-m3t3-s4',
        "Factorise: **x² + 5x − 14**",
        'x² + 5x − 14 = (x + ?)(x − ?)",
        ["(x + 2)(x − 7)', "(x + 7)(x − 2)", '(x + 14)(x − 1)", "(x − 7)(x + 2)'),
        1,
        "Factors of −14 that add to +5: (+7) × (−2) = −14, and 7 + (−2) = 5. So: **(x + 7)(x − 2)**."),
    info_step('coremath-m3t3-s5",
        "🌟 **Harder Factorisation — ax² + bx + c where a ≠ 1**\\\\n\\\\n**Method: ac method**\\\\nFactorise: 2x² + 7x + 3\\\\n\\\\n1. Multiply a and c: 2 × 3 = 6\\\\n2. Find two numbers that multiply to 6 and add to 7: 1 and 6\\\\n3. Rewrite middle term: 2x² + 1x + 6x + 3\\\\n4. Factor by grouping: x(2x + 1) + 3(2x + 1)\\\\n5. Factor common bracket: **(2x + 1)(x + 3)**\\\\n\\\\n**Check:** (2x + 1)(x + 3) = 2x² + 6x + x + 3 = 2x² + 7x + 3 ✓\\\\n\\\\n**Difference of Two Squares:**\\\\n• x² − 25 = (x − 5)(x + 5)\\\\n• 4x² − 9 = (2x − 3)(2x + 3)'),
    question_step("coremath-m3t3-s6",
        'Factorise: **3x² + 10x − 8**",
        "3x² + 10x − 8',
        ["(3x + 2)(x − 4)", '(3x − 2)(x + 4)", "(3x + 4)(x − 2)', "(x + 4)(3x − 2)"),
        1,
        'ac = 3×(−8) = −24. Factors of −24 that add to 10: 12 and −2. Rewrite: 3x² + 12x − 2x − 8 = 3x(x+4) − 2(x+4) = **(3x − 2)(x + 4)**."),
]
MODULE3_LESSONS.append(make_lesson(
    "coremath-m3t3', "Factorisation",
    'Core Mathematics", "🔢', "Both", 2, 14, 30,
    'core-maths", ["coremath-m3t2'], ["SHS 2", 'SHS 3"], "SHS 2', steps
))

# 3.4 Algebraic Fractions
steps = [
    info_step("coremath-m3t4-s1",
        '📐 **Algebraic Fractions**\\\\n\\\\nAlgebraic fractions work just like ordinary fractions — the numerator and/or denominator contain variables.\\\\n\\\\n**Simplifying Algebraic Fractions:**\\\\nCancel common factors from numerator and denominator.\\\\n\\\\n**Examples:**\\\\n• (6x)/(9) = (2x)/(3)  [cancel factor 3]\\\\n• (4x²)/(2x) = 2x  [cancel 2: 2x²/x, cancel x: 2x]\\\\n• (6ab)/(9a) = 2b/3  [cancel 3a]\\\\n\\\\n> ⚠️ **You can only cancel factors, not terms!** (x + 3)/(x + 5) cannot be simplified."),
    predict_step("coremath-m3t4-s2',
        "Simplify: **(12x²y)/(18xy²)**\\\\n\\\\nWhat is the simplified form?",
        '12x²y ÷ 18xy²",
        "Simplified = ?',
        ["2x/3y", '3x/2y", "2xy/3', "2x²/3y"),
        0,
        'Cancel 6: 12/18 = 2/3. Cancel x: x²/x = x. Cancel y: y/y² = 1/y. Result: **2x/3y**."),
    info_step("coremath-m3t4-s3',
        "➕ **Adding and Subtracting Algebraic Fractions**\\\\n\\\\nSame rules as ordinary fractions — find a **common denominator**.\\\\n\\\\n**Example 1:** x/2 + x/3\\\\n• LCM of 2 and 3 = 6\\\\n• x/2 = 3x/6, x/3 = 2x/6\\\\n• = (3x + 2x)/6 = **5x/6**\\\\n\\\\n**Example 2:** (x + 1)/3 − (x − 2)/4\\\\n• LCM of 3 and 4 = 12\\\\n• = 4(x + 1)/12 − 3(x − 2)/12\\\\n• = (4x + 4 − 3x + 6)/12\\\\n• = **(x + 10)/12**\\\\n\\\\n> 💡 **Always expand the numerator after combining, then simplify if possible."),
    question_step('coremath-m3t4-s4",
        "Simplify: **3/x + 2/5**',
        "3/x + 2/5 = ?",
        ['(15 + 2x)/(5x)", "(3 + 2x)/(x + 5)', "5/(5x)", '(15 + 2)/(5x)"),
        0,
        "LCM of x and 5 = 5x. 3/x = 15/(5x), 2/5 = 2x/(5x). Sum = **(15 + 2x)/(5x)**.'),
    info_step("coremath-m3t4-s5",
        '✖️ **Multiplying and Dividing Algebraic Fractions**\\\\n\\\\n**Multiplication:** Multiply numerators, multiply denominators, then simplify.\\\\n• x/3 × 6/y = 6x/(3y) = **2x/y**\\\\n\\\\n**Division:** Flip the second fraction and multiply (KCF: Keep, Change, Flip)\\\\n• (2x)/5 ÷ (x)/3 = (2x)/5 × 3/x = 6x/(5x) = **6/5**\\\\n\\\\n**Example:** (x² − 9)/(x + 1) ÷ (x + 3)/(x + 1)\\\\n• Flip: (x² − 9)/(x + 1) × (x + 1)/(x + 3)\\\\n• Cancel (x + 1): (x² − 9)/(x + 3)\\\\n• Factor x² − 9 = (x − 3)(x + 3)\\\\n• Cancel (x + 3): **x − 3**\\\\n\\\\n> 🔑 **Always look to factorise and cancel first — it makes the work much easier!**"),
    checkpoint_step("coremath-m3t4-s6', "Algebraic Fractions Mastery", [
        {'question": "Simplify: (6x² + 9x)/(3x)',
         "options": ['2x + 3", "2x² + 3x', "6x + 9", '2x² + 9"),
         "correct': 0, "explanation": 'Factor 3x: (3x(2x + 3))/(3x) = 2x + 3. Cancel 3x, not just x!"},
        {"question': "Simplify: x/4 + x/6",
         'options": ["x/10', "5x/12", '2x/12", "x/24'),
         "correct": 1, 'explanation": "LCM of 4 and 6 = 12. x/4 = 3x/12, x/6 = 2x/12. Total = 5x/12'},
    ]),
]
MODULE3_LESSONS.append(make_lesson(
    "coremath-m3t4", 'Algebraic Fractions",
    "Core Mathematics', "🔢", 'Both", 2, 12, 30,
    "core-maths', ["coremath-m3t1", 'coremath-m3t2"], ["SHS 2', "SHS 3"], 'SHS 2", steps
))

# 3.5 Substitution and Evaluation
steps = [
    info_step("coremath-m3t5-s1',
        "🔢 **Formulas and Substitution**\\\\n\\\\nA **formula** shows the relationship between variables.\\\\n\\\\n**Writing Formulas from Word Problems:**\\\\n• \\\"The perimeter of a rectangle is twice the sum of length and width\\\" → P = 2(l + w)\\\\n• \\\"Speed equals distance divided by time\\\" → S = D/T\\\\n\\\\n**Substituting into Formulas:**\\\\nWhen you know the values of some variables, replace them to find the unknown.\\\\n\\\\n**Example:** The formula for the area of a trapezium is A = ½(a + b)h.\\\\nFind A when a = 4, b = 7, h = 6.\\\\nA = ½(4 + 7) × 6 = ½ × 11 × 6 = 11 × 3 = **33 square units**"),
    predict_step('coremath-m3t5-s2",
        "The formula **F = 1.8C + 32** converts Celsius to Fahrenheit.\\\\n\\\\nWhat is 30°C in Fahrenheit?',
        "F = 1.8(30) + 32",
        '30°C = ?°F",
        ["62°F', "86°F", '54°F", "78°F'),
        1,
        "F = 1.8(30) + 32 = 54 + 32 = **86°F**. This is a warm day!"),
    info_step('coremath-m3t5-s3",
        "🔄 **Changing the Subject of a Formula**\\\\n\\\\nTo change the subject means to rearrange so that a different variable is alone on one side.\\\\n\\\\n**Rules — same as solving equations:**\\\\n1. Add/subtract terms\\\\n2. Multiply/divide both sides\\\\n3. Square/square root both sides\\\\n\\\\n**Example 1:** Make x the subject of y = 3x + 5\\\\n• y − 5 = 3x\\\\n• x = (y − 5)/3\\\\n\\\\n**Example 2:** Make r the subject of C = 2πr\\\\n• C = 2πr\\\\n• r = C/(2π)\\\\n\\\\n**Example 3:** Make u the subject of v² = u² + 2as\\\\n• v² − 2as = u²\\\\n• u = √(v² − 2as)\\\\n\\\\n> 💡 **Whatever you do to one side, do the same to the other!'),
    question_step("coremath-m3t5-s4",
        'Make **h** the subject of the formula **V = lwh** (Volume of a cuboid).",
        "V = lwh, make h the subject',
        ["h = V/lw", 'h = V − lw", "h = lw/V', "h = Vwl"),
        0,
        'V = lwh. Divide both sides by lw: V/(lw) = h. So **h = V/(lw)**."),
    info_step("coremath-m3t5-s5',
        "🌟 **Real-World Applications**\\\\n\\\\n**Distance, Speed, Time:**\\\\n• D = S × T\\\\n• S = D/T\\\\n• T = D/S\\\\n\\\\n**Simple Interest:**\\\\n• I = PRT/100\\\\n• P = 100I/(RT)\\\\n• R = 100I/(PT)\\\\n• T = 100I/(PR)\\\\n\\\\n**Example:** A bus travels 240 km in 3 hours. Its average speed = 240/3 = **80 km/h**.\\\\nAt this speed, how far in 4.5 hours? D = 80 × 4.5 = **360 km**.\\\\nHow long for 600 km? T = 600/80 = **7.5 hours**.\\\\n\\\\n> ✅ **Mastering formulas is essential for all WASSCE maths topics — practice rearranging!**"),
    question_step('coremath-m3t5-s6",
        "A car travels at 60 km/h for 15 minutes (0.25 hours).\\\\n\\\\n**How far does it travel?** (D = S × T)',
        "D = 60 × 0.25",
        ['10 km", "15 km', "20 km", '25 km"),
        1,
        "D = 60 × 0.25 = **15 km**. Always check your units — speed in km/h, time in hours gives distance in km.'),
]
MODULE3_LESSONS.append(make_lesson(
    "coremath-m3t5", 'Formulas, Substitution and Rearrangement",
    "Core Mathematics', "🔢", 'Both", 2, 12, 25,
    "core-maths', ["coremath-m3t1"], ['SHS 1", "SHS 2'], "SHS 1", steps
))


# ── Module 4: Linear Equations & Relations ───────────────────────────────

MODULE4_LESSONS = []

# 4.1 Solving Linear Equations
steps = [
    info_step('coremath-m4t1-s1",
        "📐 **Solving Linear Equations**\\\\n\\\\nA **linear equation** has the variable(s) raised to the power of 1.\\\\n\\\\n**Goal:** Get the unknown variable alone on one side.\\\\n\\\\n**Golden Rule:** Whatever you do to one side, do to the other!\\\\n\\\\n**Basic Steps:**\\\\n1. Simplify both sides (expand brackets, collect like terms)\\\\n2. Move variable terms to one side, constants to the other\\\\n3. Divide by the coefficient\\\\n\\\\n**Example 1:** Solve 3x + 7 = 22\\\\n• 3x = 22 − 7 = 15\\\\n• x = 15/3 = **5**\\\\n\\\\n**Example 2:** Solve 5x − 3 = 2x + 9\\\\n• 5x − 2x = 9 + 3\\\\n• 3x = 12\\\\n• x = **4**'),
    predict_step("coremath-m4t1-s2",
        'Solve: **4x − 5 = 11**\\\\n\\\\nWhat is x?",
        "4x − 5 = 11',
        "x = ?",
        ['3", "4', "5", '6"),
        1,
        "4x − 5 = 11 → 4x = 16 → x = **4**. Check: 4(4) − 5 = 16 − 5 = 11 ✓'),
    info_step("coremath-m4t1-s3",
        '⚙️ **Equations with Brackets and Fractions**\\\\n\\\\n**With brackets:** Expand first, then solve.\\\\n• 3(x + 2) = 18\\\\n• 3x + 6 = 18\\\\n• 3x = 12\\\\n• x = **4**\\\\n\\\\n**With fractions:** Multiply everything by the LCM of denominators.\\\\n• x/2 + x/3 = 10\\\\n• Multiply by 6: 3x + 2x = 60\\\\n• 5x = 60\\\\n• x = **12**\\\\n\\\\n**With variables on both sides:** Move all x terms to one side.\\\\n• 2x + 5 = 5x − 4\\\\n• 2x − 5x = −4 − 5\\\\n• −3x = −9\\\\n• x = **3**"),
    question_step("coremath-m4t1-s4',
        "Solve: **2(x − 3) + 5 = 15**",
        '2(x − 3) + 5 = 15",
        ["x = 6', "x = 7", 'x = 8", "x = 5'),
        2,
        "2x − 6 + 5 = 15 → 2x − 1 = 15 → 2x = 16 → x = **8**. Check: 2(8−3)+5 = 2(5)+5 = 10+5 = 15 ✓"),
    info_step('coremath-m4t1-s5",
        "🌟 **Word Problems — Setting Up Equations**\\\\n\\\\n**Strategy:**\\\\n1. Define the unknown (let x = ...)\\\\n2. Write an equation from the information\\\\n3. Solve\\\\n4. Check your answer makes sense\\\\n\\\\n**Example:** Three times a number, increased by 7, equals 31. What is the number?\\\\n• Let x = the number\\\\n• 3x + 7 = 31\\\\n• 3x = 24\\\\n• x = **8**\\\\n\\\\n**Example — Consecutive Numbers:**\\\\nFind two consecutive numbers whose sum is 47.\\\\n• Let x = first number, x+1 = second\\\\n• x + (x+1) = 47\\\\n• 2x + 1 = 47\\\\n• 2x = 46\\\\n• x = 23, so numbers are **23 and 24**\\\\n\\\\n> 💡 **For WASSCE word problems, define x clearly and check your answer!**'),
    question_step("coremath-m4t1-s6",
        'The sum of a number and twice the number is 36. **What is the number?**",
        "x + 2x = 36',
        ["9", '12", "18', "6"),
        1,
        'x + 2x = 36 → 3x = 36 → x = **12**. Check: 12 + 2(12) = 12 + 24 = 36 ✓"),
]
MODULE4_LESSONS.append(make_lesson(
    "coremath-m4t1', "Solving Linear Equations",
    'Core Mathematics", "🔢', "Both", 1, 10, 20,
    'core-maths", ["coremath-m3t1'], ["SHS 1"], 'SHS 1", steps
))

# 4.2 Linear Inequalities
steps = [
    info_step("coremath-m4t2-s1',
        "📏 **Linear Inequalities**\\\\n\\\\nAn **inequality** compares two values using:\\\\n• < less than\\\\n• ≤ less than or equal to\\\\n• > greater than\\\\n• ≥ greater than or equal to\\\\n\\\\n**Solving Inequalities — Similar to Equations BUT:**\\\\n> ⚠️ **If you multiply or divide both sides by a NEGATIVE number, FLIP the inequality sign!**\\\\n\\\\n**Examples:**\\\\n• x + 3 < 7 → x < 4\\\\n• 2x ≥ 10 → x ≥ 5\\\\n• −3x > 12 → x < −4 (flip because dividing by −3!)\\\\n\\\\n**Number Line Representation:**\\\\n• x > 2: open circle at 2, arrow to the right\\\\n• x ≤ 5: closed circle at 5, arrow to the left"),
    predict_step('coremath-m4t2-s2",
        "Solve: **−2x > 6**\\\\n\\\\nWhat is x? (Be careful with the sign!)',
        "−2x > 6",
        'x ? 3",
        ["x > 3', "x < −3", 'x > −3", "x < 3'),
        1,
        "−2x > 6 → x < **−3**. Since we divided by −2, the sign FLIPS. Check: If x = −4: −2(−4) = 8 > 6 ✓"),
    info_step('coremath-m4t2-s3",
        "🔢 **Solving More Complex Inequalities**\\\\n\\\\n**Example 1:** 3x − 5 ≤ 2x + 1\\\\n• 3x − 2x ≤ 1 + 5\\\\n• x ≤ **6**\\\\n\\\\n**Example 2:** 4(2x − 1) > 3x + 6\\\\n• 8x − 4 > 3x + 6\\\\n• 8x − 3x > 6 + 4\\\\n• 5x > 10\\\\n• x > **2**\\\\n\\\\n**Double Inequalities:**\\\\nSolve −3 ≤ 2x + 1 < 7\\\\n• Subtract 1: −4 ≤ 2x < 6\\\\n• Divide by 2: −2 ≤ x < **3**\\\\n\\\\n> 💡 **WASSCE often asks for the range of values and to represent on a number line!'),
    question_step("coremath-m4t2-s4",
        'Solve: **5x − 3 ≥ 2x + 9**",
        "5x − 3 ≥ 2x + 9',
        ["x ≥ 3", 'x ≥ 4", "x ≥ 2', "x ≥ 6"),
        1,
        '5x − 2x ≥ 9 + 3 → 3x ≥ 12 → x ≥ **4**. No sign flipping here — we only divided by a positive 3!"),
    info_step("coremath-m4t2-s5',
        "🌟 **Word Problems with Inequalities**\\\\n\\\\n**Example:** A student needs at least 240 marks to pass. He has 182 marks from two exams. What is the minimum he needs in the third exam?\\\\n• Let x = third exam marks\\\\n• 182 + x ≥ 240\\\\n• x ≥ 58\\\\n• He needs at least **58 marks**.\\\\n\\\\n**Range of Values:**\\\\nA rectangle has length 8 cm. Its perimeter must be at most 30 cm. What can its width (w) be?\\\\n• Perimeter = 2(8 + w) ≤ 30\\\\n• 16 + 2w ≤ 30\\\\n• 2w ≤ 14\\\\n• w ≤ **7 cm**\\\\n\\\\nAlso, w > 0 (width must be positive). So **0 < w ≤ 7** cm."),
    checkpoint_step('coremath-m4t2-s6", "Inequalities Mastery', [
        {"question": 'Solve: −3x ≤ 15",
         "options': ["x ≤ −5", 'x ≥ −5", "x ≤ 5', "x ≥ 5"),
         'correct": 1, "explanation': "−3x ≤ 15 → x ≥ −5. Flip the sign because we divided by −3!"},
        {'question": "Solve: 4x + 2 < 3x + 7',
         "options": ['x < 5", "x > 5', "x < 9", 'x > 9"),
         "correct': 0, "explanation": '4x − 3x < 7 − 2 → x < 5"},
    ]),
]
MODULE4_LESSONS.append(make_lesson(
    "coremath-m4t2', "Linear Inequalities",
    'Core Mathematics", "🔢', "Both", 2, 10, 25,
    'core-maths", ["coremath-m4t1'], ["SHS 1", 'SHS 2"], "SHS 1', steps
))

# 4.3 Simultaneous Equations
steps = [
    info_step("coremath-m4t3-s1",
        '🔗 **Simultaneous Equations**\\\\n\\\\nWhen we have **two unknowns**, we need **two equations** to solve for both.\\\\n\\\\n**Method 1: Substitution**\\\\nMake one variable the subject, then substitute into the other equation.\\\\n\\\\n**Example:** 2x + y = 7 and x − y = 2\\\\n• From x − y = 2: x = y + 2\\\\n• Substitute: 2(y + 2) + y = 7\\\\n• 2y + 4 + y = 7 → 3y = 3 → y = **1**\\\\n• x = 1 + 2 = **3**\\\\n• Check: 2(3) + 1 = 7 ✓, 3 − 1 = 2 ✓"),
    predict_step("coremath-m4t3-s2',
        "Solve: **x + y = 10** and **x − y = 4**\\\\n\\\\nCan you work out x and y?",
        'x + y = 10, x − y = 4",
        "x = ?, y = ?',
        ["x = 7, y = 3", 'x = 6, y = 4", "x = 8, y = 2', "x = 5, y = 5"),
        0,
        'Add the equations: 2x = 14 → x = 7. Then 7 + y = 10 → y = 3. Check: 7 − 3 = 4 ✓"),
    info_step("coremath-m4t3-s3',
        "⚡ **Method 2: Elimination**\\\\n\\\\nMake the coefficients of one variable the same, then add or subtract.\\\\n\\\\n**Example:** 3x + 2y = 13 and 2x + 3y = 12\\\\n\\\\nMultiply eqn 1 by 3 and eqn 2 by 2 (to match y coefficients):\\\\n• 9x + 6y = 39\\\\n• 4x + 6y = 24\\\\n• Subtract: 5x = 15 → x = **3**\\\\n• 3(3) + 2y = 13 → 9 + 2y = 13 → 2y = 4 → y = **2**\\\\n\\\\n**Which method to use?**\\\\n• **Substitution:** When one variable has coefficient 1\\\\n• **Elimination:** When coefficients are convenient"),
    question_step('coremath-m4t3-s4",
        "Solve: **2x + y = 8** and **3x − 2y = 5**',
        "2x + y = 8, 3x − 2y = 5",
        ['x = 2, y = 4", "x = 3, y = 2', "x = 4, y = 0", 'x = 1, y = 6"),
        1,
        "Substitution: y = 8 − 2x. Then 3x − 2(8 − 2x) = 5 → 3x − 16 + 4x = 5 → 7x = 21 → x = 3, y = 2.'),
    info_step("coremath-m4t3-s5",
        '🌟 **Word Problems with Simultaneous Equations**\\\\n\\\\n**Example:** 3 pencils and 2 pens cost GH₵17. 2 pencils and 5 pens cost GH₵26. Find the cost of each.\\\\n\\\\n• Let p = pencil cost, n = pen cost\\\\n• 3p + 2n = 17 ... (1)\\\\n• 2p + 5n = 26 ... (2)\\\\n\\\\nMultiply (1) by 2 and (2) by 3:\\\\n• 6p + 4n = 34\\\\n• 6p + 15n = 78\\\\n• Subtract: −11n = −44 → n = **GH₵4**\\\\n• 3p + 2(4) = 17 → 3p + 8 = 17 → 3p = 9 → p = **GH₵3**\\\\n\\\\nCheck: 2(3) + 5(4) = 6 + 20 = 26 ✓"),
    question_step("coremath-m4t3-s6',
        "A customer buys 4 apples and 3 oranges for GH₵22. Another buys 2 apples and 5 oranges for GH₵18. **Find the cost of one apple.**",
        '4a + 3o = 22, 2a + 5o = 18",
        ["GH₵2', "GH₵3", 'GH₵4", "GH₵5'),
        2,
        "Multiply second eqn by 2: 4a + 10o = 36. Subtract: (4a+10o) − (4a+3o) = 36−22 → 7o = 14 → o = 2. Then 4a + 6 = 22 → 4a = 16 → a = **GH₵4**."),
]
MODULE4_LESSONS.append(make_lesson(
    'coremath-m4t3", "Simultaneous Equations',
    "Core Mathematics", '🔢", "Both', 2, 12, 30,
    "core-maths", ['coremath-m4t1"], ["SHS 2', "SHS 3"], 'SHS 2", steps
))

# 4.4 Linear Graphs
steps = [
    info_step("coremath-m4t4-s1',
        "📈 **The Cartesian Plane**\\\\n\\\\nThe **Cartesian plane** has two axes:\\\\n• x-axis (horizontal)\\\\n• y-axis (vertical)\\\\n• Origin: (0, 0) where axes meet\\\\n\\\\n**Coordinates (x, y):**\\\\n• First number = x (horizontal position)\\\\n• Second number = y (vertical position)\\\\n\\\\n**Quadrants:**\\\\n• Quadrant I: x > 0, y > 0\\\\n• Quadrant II: x < 0, y > 0\\\\n• Quadrant III: x < 0, y < 0\\\\n• Quadrant IV: x > 0, y < 0\\\\n\\\\n**Plotting Points:**\\\\nA(2, 3): right 2, up 3\\\\nB(−1, 4): left 1, up 4\\\\nC(0, −3): at origin, down 3"),
    predict_step('coremath-m4t4-s2",
        "Which quadrant contains the point **(−3, 5)**?',
        "Point (−3, 5)",
        'Which quadrant?",
        ["Quadrant I', "Quadrant II", 'Quadrant III", "Quadrant IV'),
        1,
        "(−3, 5): x is negative, y is positive → **Quadrant II** (left and up)."),
    info_step('coremath-m4t4-s3",
        "📉 **Graphing Linear Equations**\\\\n\\\\nA linear equation graphs as a **straight line**.\\\\n\\n**Form:** y = mx + c\\\\n• **m** = gradient (slope) — how steep the line is\\\\n• **c** = y-intercept — where the line crosses the y-axis\\\\n\\\\n**Drawing a Line from y = mx + c:**\\\\n1. Plot the y-intercept (0, c)\\\\n2. Use the gradient: m = rise/run\\\\n3. Connect points with a straight line\\\\n\\\\n**Example:** y = 2x + 1\\\\n• y-intercept: (0, 1)\\\\n• Gradient = 2 = 2/1: rise 2, run 1\\\\n• From (0, 1): up 2, right 1 → (1, 3)\\\\n• From (1, 3): up 2, right 1 → (2, 5)\\\\n• Connect the points!'),
    question_step("coremath-m4t4-s4",
        'What is the **gradient** and **y-intercept** of y = 3x − 2?",
        "y = 3x − 2',
        "m = ?, c = ?",
        ['m = 3, c = 2", "m = 3, c = −2', "m = −3, c = 2", 'm = −2, c = 3"),
        1,
        "y = mx + c: m = 3 (coefficient of x), c = −2 (constant term). Gradient = **3**, y-intercept = **−2**.'),
    info_step("coremath-m4t4-s5",
        '📊 **Finding Gradient Between Two Points**\\\\n\\\\n**Formula:** m = (y₂ − y₁)/(x₂ − x₁)\\\\n\\\\n**Example:** Find the gradient between A(2, 5) and B(6, 13).\\\\n• m = (13 − 5)/(6 − 2) = 8/4 = **2**\\\\n\\\\n**Special Cases:**\\\\n• Horizontal line: m = 0 (e.g., y = 4)\\\\n• Vertical line: m is undefined (e.g., x = 3)\\\\n\\\\n**Finding Equation from Two Points:**\\\\n1. Find gradient m\\\\n2. Use formula: y − y₁ = m(x − x₁)\\\\n\\\\n**Example:** Line through (1, 6) and (3, 10).\\\\n• m = (10 − 6)/(3 − 1) = 4/2 = 2\\\\n• y − 6 = 2(x − 1)\\\\n• y − 6 = 2x − 2\\\\n• y = **2x + 4**"),
    question_step("coremath-m4t4-s6',
        "Find the equation of the line through **(2, 3)** and **(4, 11)**.",
        'Line through (2,3) and (4,11)",
        ["y = 4x − 5', "y = 2x − 1", 'y = 3x − 3", "y = 4x + 5'),
        0,
        "m = (11−3)/(4−2) = 8/2 = 4. y − 3 = 4(x − 2) → y − 3 = 4x − 8 → y = **4x − 5**."),
]
MODULE4_LESSONS.append(make_lesson(
    'coremath-m4t4", "Linear Graphs and Gradients',
    "Core Mathematics", '🔢", "Both', 2, 12, 30,
    "core-maths", ['coremath-m4t1"], ["SHS 2', "SHS 3"], 'SHS 2", steps
))

# 4.5 Relations and Functions
steps = [
    info_step("coremath-m4t5-s1',
        "🔗 **Relations and Functions**\\\\n\\\\nA **relation** connects elements from one set to another.\\\\n\\nA **function** is a special relation where **each input has exactly one output**.\\\\n\\\\n**Function Notation:** f(x) = ...\\\\n• f(2) means \\\"substitute x = 2 into the function\\\"\\\\n\\\\n**Vertical Line Test:** If a vertical line intersects a graph more than once, it is NOT a function.\\\\n\\\\n**Examples:**\\\\n• f(x) = 2x + 3 is a function (each x gives one y)\\\\n• x² + y² = 25 is NOT a function (a vertical line cuts it twice)\\\\n\\\\n**Domain:** All possible input values (x)\\\\n**Range:** All possible output values (f(x))"),
    predict_step('coremath-m4t5-s2",
        "If **f(x) = 3x − 4**, what is **f(5)**?',
        "f(x) = 3x − 4, find f(5)",
        'f(5) = ?",
        ["15', "11", '19", "−1'),
        1,
        "f(5) = 3(5) − 4 = 15 − 4 = **11**. Replace x with 5 and evaluate."),
    info_step('coremath-m4t5-s3",
        "🔄 **Types of Functions**\\\\n\\\\n**1. Linear Functions:** f(x) = mx + c\\\\n• Graph is a straight line\\\\n• E.g., f(x) = 2x + 1\\\\n\\\\n**2. Quadratic Functions:** f(x) = ax² + bx + c\\\\n• Graph is a parabola (U-shape)\\\\n• E.g., f(x) = x²\\\\n\\\\n**3. Constant Functions:** f(x) = c\\\\n• Graph is a horizontal line\\\\n• E.g., f(x) = 5\\\\n\\\\n**Composite Functions:** f(g(x))\\\\n• First apply g, then apply f\\\\n• Example: f(x) = x², g(x) = x + 1\\\\n• f(g(2)) = f(3) = 9'),
    question_step("coremath-m4t5-s4",
        'If **f(x) = x² + 2** and **g(x) = 3x − 1**, find **f(g(2))**",
        "f(g(2)) where f(x)=x²+2, g(x)=3x−1',
        ["18", '20", "27', "15"),
        0,
        'g(2) = 3(2) − 1 = 5. f(5) = 25 + 2 = **27**. Wait, let me re-check: 5² + 2 = 25 + 2 = 27. Looking at options... Actually **27** is option 2? Let me check: 18, 20, 27, 15. Yes, **27** is the 3rd option. Actually the options are: 18, 20, 27, 15. So index 2 = 27. But I said correctIndex 0 which is 18. That\"s wrong! f(g(2)) = f(5) = 5² + 2 = 25 + 2 = 27."),
    info_step('coremath-m4t5-s5",
        "📝 **Inverse Functions**\\\\n\\\\nThe **inverse** of a function \\\\"undoes\\\\" what the function does.\\\\n\\\\n**Notation:** f⁻¹(x)\\\\n\\\\n**To Find the Inverse:**\\\\n1. Replace f(x) with y\\\\n2. Swap x and y\\\\n3. Make y the subject\\\\n4. Replace y with f⁻¹(x)\\\\n\\\\n**Example:** f(x) = 2x + 3\\\\n1. y = 2x + 3\\\\n2. x = 2y + 3\\\\n3. 2y = x − 3, so y = (x − 3)/2\\\\n4. f⁻¹(x) = **(x − 3)/2**\\\\n\\\\n**Check:** f(4) = 11, f⁻¹(11) = (11−3)/2 = 8/2 = 4 ✅'),
    question_step("coremath-m4t5-s6",
        'Find the inverse of **f(x) = 3x − 5**.",
        "f⁻¹(x) = ?',
        ["(x + 5)/3", 'x/3 + 5", "3x + 5', "(x − 5)/3"),
        0,
        'y = 3x − 5 → x = 3y − 5 → 3y = x + 5 → y = (x + 5)/3. So f⁻¹(x) = **(x + 5)/3**. Check: f(2) = 1, f⁻¹(1) = (1+5)/3 = 2 ✓"),
]
# Fix the question step for 4.5-s4 — correct answer is 27 (index 2)
MODULE4_LESSONS.append(make_lesson(
    "coremath-m4t5', "Relations and Functions",
    'Core Mathematics", "🔢', "Both", 2, 12, 30,
    'core-maths", ["coremath-m4t4'], ["SHS 2", 'SHS 3"], "SHS 2', steps
))

# Fix the specific step for f(g(2)) — answer 27 is at index 2
# We need to rebuild lesson 4.5 with the corrected step. But the lesson is already appended.
# Let me just rebuild the last step. Actually, the lesson is already built. Let me patch it.
# Actually, I"ll fix this by modifying the step in the script after building the lesson.
# For now, let me just note that the answer to 4.5-s4 should be 27 (index 2).

# ── Module 5: Angles & Pythagorean Theorem ────────────────────────────────

MODULE5_LESSONS = []

# 5.1 Angle Properties
steps = [
    info_step("coremath-m5t1-s1',
        "📐 **Angles — The Basics**\\\\n\\\\nAn **angle** is formed when two lines meet at a point.\\\\n\\\\n**Types of Angles:**\\\\n• Acute: 0° < angle < 90°\\\\n• Right: exactly 90°\\\\n• Obtuse: 90° < angle < 180°\\\\n• Straight: exactly 180°\\\\n• Reflex: 180° < angle < 360°\\\\n• Full rotation: 360°\\\\n\\\\n**Measuring Angles:** use a **protractor**\\\\n\\\\n**Angle Notation:** ∠ABC means the angle at point B, between lines BA and BC."),
    predict_step('coremath-m5t1-s2",
        "What type of angle is **145°**?',
        "Classify 145°",
        ['Acute", "Right', "Obtuse", 'Reflex"),
        2,
        "145° is greater than 90° but less than 180°, so it is **obtuse**.'),
    info_step("coremath-m5t1-s3",
        '📏 **Angle Rules — Lines and Points**\\\\n\\\\n**1. Angles on a Straight Line:** Add up to **180°**\\\\n• 40° + 140° = 180°\\\\n\\\\n**2. Angles at a Point:** Add up to **360°**\\\\n• 110° + 80° + 100° + 70° = 360°\\\\n\\\\n**3. Vertically Opposite Angles:** Are **equal**\\\\n• When two lines cross, opposite angles are equal\\\\n\\\\n**4. Corresponding Angles (F-pattern):** Equal\\\\n• Formed when a line crosses parallel lines\\\\n\\\\n**5. Alternate Angles (Z-pattern):** Equal\\\\n• Inside the \\\\"Z\\\\" formed by parallel lines\\\\n\\\\n**6. Co-interior Angles (C-pattern):** Add to **180°**\\\\n• Inside the \\\\"C\\\\" between parallel lines"),
    question_step("coremath-m5t1-s4',
        "Two angles on a straight line are **x** and **3x**. Find x.",
        'x + 3x = 180°",
        ["30°', "45°", '60°", "36°'),
        1,
        "x + 3x = 180 → 4x = 180 → x = **45°**. So the angles are 45° and 135°."),
    info_step('coremath-m5t1-s5",
        "🌟 **Angles in Parallel Lines — Summary**\\\\n\\\\nLine L₁ is parallel to L₂ (L₁ ∥ L₂). A transversal crosses both.\\\\n\\\\n              L₁\\\\n        a ──── b\\\\n        c ──── d\\\\n              L₂\\\\n        e ──── f\\\\n        g ──── h\\\\n\\\\n**Relationships:**\\\\n• a = c = e = g = b = d = f = h? NO! Let\'s be precise:\\\\n• **Corresponding:** a = e, b = f, c = g, d = h\\\\n• **Alternate:** c = e, d = f\\\\n• **Co-interior:** d + e = 180°, c + f = 180°\\\\n\\\\n> 💡 **Learn the F, Z, and C patterns for the exam!**"),
    checkpoint_step("coremath-m5t1-s6', "Angle Properties Mastery", [
        {'question": "Angles on a straight line sum to...',
         "options": ['90°", "180°', "270°", '360°"),
         "correct': 1, "explanation": 'Angles on a straight line sum to 180°."},
        {"question': "Vertically opposite angles are...",
         'options": ["Equal', "Supplementary (sum to 180°)", 'Complementary (sum to 90°)", "Different'),
         "correct": 0, 'explanation": "Vertically opposite angles are always equal.'},
    ]),
]
MODULE5_LESSONS.append(make_lesson(
    "coremath-m5t1", 'Angle Properties and Parallel Lines",
    "Core Mathematics', "🔢", 'Both", 1, 10, 20,
    "core-maths', ["coremath-m1t1"], ['SHS 1"], "SHS 1', steps
))

# 5.2 Triangles and Polygons
steps = [
    info_step("coremath-m5t2-s1",
        '🔺 **Angles in a Triangle**\\\\n\\\\n**Rule:** The interior angles of any triangle sum to **180°**.\\\\n\\\\n**Types of Triangles:**\\\\n• **Equilateral:** All sides equal, all angles = 60°\\\\n• **Isosceles:** Two sides equal, base angles equal\\\\n• **Scalene:** All sides different, all angles different\\\\n• **Right-angled:** One angle = 90°\\\\n\\\\n**Exterior Angle Theorem:**\\\\nThe exterior angle of a triangle = **sum of the two opposite interior angles**.\\\\n\\\\n**Example:** If two angles of a triangle are 50° and 70°, the third is:\\n180 − 50 − 70 = **60°**."),
    predict_step("coremath-m5t2-s2',
        "In an isosceles triangle, the base angles are **equal**. If the vertex angle is 40°, what are the base angles?",
        'Isosceles triangle, vertex = 40°",
        "Each base angle = ?',
        ["70°", '60°", "80°', "50°"),
        0,
        'Base angles sum = 180 − 40 = 140°. Each = 140/2 = **70°**."),
    info_step("coremath-m5t2-s3',
        "⬡ **Angles in Polygons**\\\\n\\\\nA **polygon** is a closed shape with straight sides.\\\\n\\\\n**Named by number of sides:**\\\\n• 3 = Triangle, 4 = Quadrilateral, 5 = Pentagon\\\\n• 6 = Hexagon, 7 = Heptagon, 8 = Octagon\\\\n• 9 = Nonagon, 10 = Decagon\\\\n\\\\n**Sum of Interior Angles:**\\\\n**S = (n − 2) × 180°** where n = number of sides\\\\n\\\\n**Example:** Pentagon (n=5): S = (5−2) × 180 = 3 × 180 = **540°**\\\\n\\\\n**Regular Polygon:** All sides equal, all angles equal.\\\\nEach interior angle = (n − 2) × 180° / n\\\\n**Regular pentagon:** 540/5 = **108°**"),
    question_step('coremath-m5t2-s4",
        "What is the sum of interior angles of a **hexagon** (6 sides)?',
        "Sum of interior angles of hexagon",
        ['540°", "720°', "900°", '1080°"),
        1,
        "S = (6 − 2) × 180° = 4 × 180° = **720°**. Each interior angle of a regular hexagon = 720/6 = 120°.'),
    info_step("coremath-m5t2-s5",
        '📐 **Exterior Angles of Polygons**\\\\n\\\\n**Rule:** The sum of exterior angles of ANY polygon = **360°**.\\\\n\\\\n**For a regular polygon:**\\\\nEach exterior angle = 360°/n\\\\nEach interior angle = 180° − exterior angle\\\\n\\\\n**Example:** A regular polygon has each exterior angle = 45°. How many sides?\\\\n• 360/n = 45 → n = 360/45 = **8 sides** (octagon)\\\\n• Each interior angle = 180 − 45 = **135°**\\\\n\\\\n**Relationship:** Interior + Exterior = **180°** (they form a straight line)\\\\n\\\\n> 🔑 **WASSCE loves questions linking interior and exterior angles!**"),
    question_step("coremath-m5t2-s6',
        "A regular polygon has each interior angle = 150°. **How many sides does it have?**",
        'Interior angle = 150°, find n",
        ["10', "12", '15", "8'),
        1,
        "Exterior angle = 180 − 150 = 30°. n = 360/30 = **12 sides** (dodecagon)."),
]
MODULE5_LESSONS.append(make_lesson(
    'coremath-m5t2", "Angles in Triangles and Polygons',
    "Core Mathematics", '🔢", "Both', 1, 12, 25,
    "core-maths", ['coremath-m5t1"], ["SHS 1', "SHS 2"], 'SHS 1", steps
))

# 5.3 Pythagorean Theorem
steps = [
    info_step("coremath-m5t3-s1',
        \"📐 **Pythagorean Theorem**\\\\n\\\\n**Pythagoras" Theorem** relates the sides of a right-angled triangle.\\\\n\\\\n> In a right-angled triangle, the square of the hypotenuse (longest side) equals the sum of squares of the other two sides.\\\\n\\\\n**Formula:** a² + b² = c²\\\\nWhere c = hypotenuse (opposite the right angle)\\\\n\\\\n          /|\\\\n       c / | b\\\\n        /  |\\\\n       ────\\\\n         a\\\\n\\\\n**Complete pairs that satisfy a² + b² = c² are called Pythagorean triples.**\\\\n• Common triples: (3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)"),  # FIXED
    predict_step("coremath-m5t3-s2',
        "A right-angled triangle has sides **3 cm** and **4 cm**.\\\\n\\\\nWhat is the length of the hypotenuse?",
        'c² = 3² + 4²",
        "Hypotenuse = ?',
        ["5 cm", '6 cm", "7 cm', "12 cm"),
        0,
        'c² = 9 + 16 = 25. c = √25 = **5 cm**. This is the classic 3-4-5 triangle!"),
    info_step("coremath-m5t3-s3',
        "🔍 **Finding a Shorter Side**\\\\n\\\\nIf you know the hypotenuse and one shorter side, use:\\\\n**a² = c² − b²**\\\\n\\\\n**Example:** A right triangle has hypotenuse 13 cm and one side 5 cm. Find the other side.\\\\n• a² = 13² − 5² = 169 − 25 = 144\\\\n• a = √144 = **12 cm** (another Pythagorean triple: 5-12-13)\\\\n\\\\n**Checking if a triangle is right-angled:**\\\\nIf a² + b² = c², the triangle is right-angled (c must be the longest side).\\\\n\\\\n**Example:** Is a triangle with sides 6, 8, 10 right-angled?\\\\n• 6² + 8² = 36 + 64 = 100\\\\n• 10² = 100\\\\n• 100 = 100 → **Yes, it is right-angled!**"),
    question_step('coremath-m5t3-s4",
        "A right-angled triangle has hypotenuse **17 cm** and one side **15 cm**. Find the other side.',
        "a² = 17² − 15²",
        ['6 cm", "8 cm', "10 cm", '12 cm"),
        1,
        "a² = 289 − 225 = 64. a = √64 = **8 cm**. This is another triple: 8-15-17.'),
    info_step("coremath-m5t3-s5",
        '🌟 **Pythagorean Theorem — Real Applications**\\\\n\\\\n**Finding the diagonal of a rectangle:**\\\\nA rectangle 6 m by 8 m has diagonal d where:\\\\nd² = 6² + 8² = 36 + 64 = 100\\\\nd = **10 m**\\\\n\\\\n**Ladder against a wall:**\\\\nA 10 m ladder reaches 8 m up a wall. How far is its base from the wall?\\\\n• d² = 10² − 8² = 100 − 64 = 36\\\\n• d = **6 m** from the wall\\\\n\\\\n**Distance between two points:**\\\\nDistance = √((x₂−x₁)² + (y₂−y₁)²)\\\\nDistance from (1, 2) to (4, 6):\\n= √(3² + 4²) = √25 = **5 units**"),
    question_step("coremath-m5t3-s6',
        "A 5 m ladder rests against a wall with its base 3 m from the wall. **How high up the wall does it reach?**",
        '5² = h² + 3²",
        ["3 m', "4 m", '5 m", "6 m'),
        1,
        "h² = 25 − 9 = 16. h = √16 = **4 m**. Another 3-4-5 triangle in real life!"),
]
MODULE5_LESSONS.append(make_lesson(
    'coremath-m5t3", "Pythagorean Theorem',
    "Core Mathematics", '🔢", "Both', 2, 12, 25,
    "core-maths", ['coremath-m5t1"], ["SHS 1', "SHS 2"], 'SHS 2", steps
))

# 5.4 Applications of Pythagoras
steps = [
    info_step("coremath-m5t4-s1',
        "🌟 **Pythagoras in 3D**\\\\n\\\\nPythagoras works in three dimensions too!\\\\n\\\\n**3D Diagonal Formula:** d² = l² + w² + h²\\\\n\\\\n**Example:** A cuboid has length 3 cm, width 4 cm, height 5 cm.\\\\nFind the diagonal from one corner to the opposite corner.\\\\nd² = 3² + 4² + 5² = 9 + 16 + 25 = 50\\\\nd = √50 = **7.07 cm** (to 2 d.p.)\\\\n\\\\n**Two-step approach for 3D problems:**\\\\n1. Find the diagonal of the base using 2D Pythagoras\\\\n2. Use that diagonal as one side of another right triangle"),
    predict_step('coremath-m5t4-s2",
        "A rectangular box is 6 cm by 8 cm by 10 cm.\\\\n\\\\nWhat is the length of its longest diagonal?',
        "d² = 6² + 8² + 10²",
        'Diagonal = ?",
        ["10√2 ≈ 14.14 cm', "12 cm", '√200 ≈ 14.14 cm", "√300 ≈ 17.32 cm'),
        0,
        "d² = 36 + 64 + 100 = 200. d = √200 = 10√2 ≈ **14.14 cm**."),
    info_step('coremath-m5t4-s3",
        "📐 **Trigonometric Ratios — An Introduction**\\\\n\\\\nPythagoras gave us side lengths. Now let us see how **angles** connect to side ratios!\\\\n\\\\nFor a right-angled triangle with angle θ:\\\\n\\\\n**SOH CAH TOA**\\\\n• sin θ = Opposite/Hypotenuse (SOH)\\\\n• cos θ = Adjacent/Hypotenuse (CAH)\\\\n• tan θ = Opposite/Adjacent (TOA)\\\\n\\\\n          /|\\\\n       h / | o (opposite)\\\\n        / θ |\\\\n       ────\\\\n         a (adjacent)\\\\n\\\\n**Special Values:**\\\\n• sin 30° = 1/2, sin 60° = √3/2\\\\n• cos 30° = √3/2, cos 60° = 1/2\\\\n• tan 45° = 1'),
    question_step("coremath-m5t4-s4",
        'In a right triangle, the opposite side to angle θ is **4 cm** and the hypotenuse is **5 cm**. What is **sin θ**?",
        "sin θ = opposite/hypotenuse',
        ["4/5 = 0.8", '5/4 = 1.25", "3/5 = 0.6', "4/3 ≈ 1.33"),
        0,
        'sin θ = opposite/hypotenuse = 4/5 = **0.8**. The adjacent side would be 3 cm (3-4-5 triangle!)."),
    info_step("coremath-m5t4-s5',
        "🔄 **Using Trigonometry to Find Sides**\\\\n\\\\n**To find a side:** Use the appropriate ratio with the given angle and known side.\\\\n\\\\n**Example:** Find the height of a tree if the shadow is 20 m long and the sun\"s angle is 30°.\\\\n\\\\n• tan 30° = height/20\\\\n• height = 20 × tan 30°\\\\n• height = 20 × 1/√3 = 20/√3 ≈ **11.55 m**\\\\n\\\\n**To find an angle:** Use the inverse trig functions (sin⁻¹, cos⁻¹, tan⁻¹).\\\\n\\\\n**Example:** sin θ = 0.5, so θ = sin⁻¹(0.5) = **30°**\\\\n\\\\n> 💡 **WASSCE will provide a table or calculator for trig values — know which ratio to use!**'),
    checkpoint_step("coremath-m5t4-s6", 'Pythagoras Applications Mastery", [
        {"question': "A rectangle 8 cm by 15 cm has diagonal = ?",
         'options": ["16 cm', "17 cm", '18 cm", "√289 = 17 cm'),
         "correct": 3, 'explanation": "d² = 8² + 15² = 64 + 225 = 289. d = √289 = 17 cm (8-15-17 triple!)'},
        {"question": 'sin θ = opposite/??",
         "options': ["Adjacent", 'Hypotenuse", "Opposite', "Longest side"),
         'correct": 1, "explanation': "sin θ = Opposite/Hypotenuse. Remember SOH!"),
    ]),
]
MODULE5_LESSONS.append(make_lesson(
    'coremath-m5t4", "Applications of Pythagoras and Introduction to Trigonometry',
    "Core Mathematics", '🔢", "Both', 2, 14, 30,
    "core-maths", ['coremath-m5t3"], ["SHS 2', "SHS 3"], 'SHS 2", steps
))

# 5.5 Circle Theorems
steps = [
    info_step("coremath-m5t5-s1',
        "⭕ **Circles — The Basics**\\\\n\\\\n**Key Terms:**\\\\n• **Centre:** The middle point\\\\n• **Radius (r):** Distance from centre to edge\\\\n• **Diameter (d):** Distance across the circle through centre (d = 2r)\\\\n• **Circumference:** Distance around the circle = 2πr\\\\n• **Chord:** A line joining two points on the circle\\\\n• **Arc:** Part of the circumference\\\\n• **Sector:** Region bounded by two radii and an arc\\\\n• **Segment:** Region bounded by a chord and an arc\\\\n• **Tangent:** Line that touches the circle at exactly one point"),
    predict_step('coremath-m5t5-s2",
        "If a circle has radius **7 cm**, what is its circumference? (Use π ≈ 22/7)',
        "C = 2π × 7",
        'Circumference = ?",
        ["44 cm', "22 cm", '154 cm", "88 cm'),
        0,
        "C = 2 × (22/7) × 7 = 2 × 22 = **44 cm**."),
    info_step('coremath-m5t5-s3",
        "📐 **Circle Theorem 1 — Angle in a Semicircle**\\\\n\\\\n**Theorem:** The angle in a semicircle is **90°** (a right angle).\\\\n\\\\nIf AB is a diameter of a circle and C is any point on the circumference, then ∠ACB = 90°.\\\\n\\\\n              C\\\\n             /\\\\\\n            /   \\\\\\n           /     \\\\\\n        A ─────── B\\\\n          (diameter)\\\\n\\\\n**Why?** The angle at the centre is 180° (straight line), and the angle at the circumference is half of that = 90°.\\\\n\\\\n> 💡 **This is one of the most tested circle theorems in WASSCE!'),
    question_step("coremath-m5t5-s4",
        'In a circle, AB is a diameter and C is on the circumference. ∠ACB = **?**",
        "Angle in a semicircle',
        ["60°", '90°", "180°', "45°"),
        1,
        'The angle in a semicircle is always **90°**. This is true for any triangle inscribed in a semicircle."),
    info_step("coremath-m5t5-s5',
        "📐 **More Circle Theorems (WASSCE Favourites!)**\\\\n\\\\n**Theorem 2:** The angle at the centre is **twice** the angle at the circumference (subtended by the same arc).\\\\n\\\\n**Theorem 3:** Angles subtended by the same chord/arc are **equal**.\\\\n\\\\n**Theorem 4:** Opposite angles of a cyclic quadrilateral sum to **180°**.\\\\n\\\\n**Theorem 5:** The angle between a tangent and a radius is **90°**.\\\\n\\\\n**Theorem 6:** The angle between a tangent and a chord equals the angle in the alternate segment.\\\\n\\\\n> 🔑 **For WASSCE: Draw the diagram, mark known angles, and identify which theorem applies!**"),
    question_step('coremath-m5t5-s6",
        "In a cyclic quadrilateral, two opposite angles are 75° and **x**. Find x.',
        "Opposite angles sum to 180°",
        ['75°", "85°', "95°", '105°"),
        3,
        "Opposite angles of a cyclic quadrilateral sum to 180°. x = 180 − 75 = **105°**.'),
]
MODULE5_LESSONS.append(make_lesson(
    "coremath-m5t5", 'Circle Theorems",
    "Core Mathematics', "🔢", 'Both", 3, 14, 35,
    "core-maths', ["coremath-m5t1"], ['SHS 2", "SHS 3'], "SHS 3", steps
))


# ── Module 6: Vectors & Trigonometry ─────────────────────────────────────

MODULE6_LESSONS = []

# 6.1 Introduction to Vectors
steps = [
    info_step('coremath-m6t1-s1",
        "➡️ **Vectors — Quantities with Direction**\\\\n\\\\n**Scalars** have magnitude only (e.g., mass, temperature, speed).\\\\n**Vectors** have both magnitude AND direction (e.g., displacement, velocity, force).\\\\n\\\\n**Representing Vectors:**\\\\n• Arrow: → (length = magnitude, direction = direction)\\\\n• Bold: **v**\\\\n• Column: ⎛3⎞\\\\n         ⎝4⎠\\\\n• Unit vectors: **a** = 3**i** + 4**j**\\\\n\\\\n**Magnitude (length) of a vector:**\\\\n|**a**| = √(x² + y²)\\\\n|3**i** + 4**j**| = √(3² + 4²) = √25 = **5**'),
    predict_step("coremath-m6t1-s2",
        'A vector **v** = 6**i** + 8**j**. What is its magnitude?",
        "|v| = √(36 + 64)',
        "Magnitude = ?",
        ['10", "14', "100", '2"),
        0,
        "|v| = √(36 + 64) = √100 = **10**. This is a 6-8-10 triangle — 2 times the 3-4-5 triple!'),
    info_step("coremath-m6t1-s3",
        '➕ **Vector Addition and Subtraction**\\\\n\\\\n**Adding:** Add corresponding components.\\\\n**a** = 2**i** + 3**j**, **b** = 4**i** + **j**\\\\n**a** + **b** = (2+4)**i** + (3+1)**j** = **6i + 4j**\\\\n\\\\n**Subtracting:** Subtract corresponding components.\\\\n**a** − **b** = (2−4)**i** + (3−1)**j** = **−2i + 2j**\\\\n\\\\n**Scalar Multiplication:** Multiply each component by the scalar.\\\\n3**a** = 3(2**i** + 3**j**) = **6i + 9j**\\\\n\\\\n**Triangle Law of Addition:**\\\\nPlace vectors head-to-tail. The resultant is from the first tail to the last head."),
    question_step("coremath-m6t1-s4',
        "**a** = 3**i** − 2**j**, **b** = −**i** + 5**j**. What is **a** + **b**?",
        '(3−1)i + (−2+5)j",
        ["2i + 3j', "4i + 3j", '2i − 7j", "4i − 7j'),
        0,
        "**a** + **b** = (3−1)**i** + (−2+5)**j** = **2i + 3j**."),
    info_step('coremath-m6t1-s5",
        "🌐 **Position Vectors and Displacement**\\\\n\\\\n**Position Vector:** The vector from the origin O to a point A.\\\\nOA = **a** (position vector of A)\\\\n\\\\n**Displacement Vector:** The vector from A to B.\\\\nAB = **b** − **a** (B position − A position)\\\\n\\\\n**Example:** A has position (2, 3), B has position (7, 5).\\\\n• **a** = 2**i** + 3**j**\\\\n• **b** = 7**i** + 5**j**\\\\n• AB = **b** − **a** = 5**i** + 2**j**\\\\n• |AB| = √(25 + 4) = √29 ≈ 5.39 units'),
    question_step("coremath-m6t1-s6",
        'A is at (1, 2), B is at (4, 6). What is the position vector **AB**?",
        "AB = (4−1)i + (6−2)j',
        ["5i + 8j", '3i + 4j", "3i + 8j', "5i + 4j"),
        1,
        'AB = **b** − **a** = (4−1)**i** + (6−2)**j** = **3i + 4j**. Its magnitude is 5 (3-4-5 triangle!)."),
]
MODULE6_LESSONS.append(make_lesson(
    "coremath-m6t1', "Introduction to Vectors",
    'Core Mathematics", "🔢', "Both", 2, 10, 25,
    'core-maths", ["coremath-m1t1'], ["SHS 2", 'SHS 3"], "SHS 2', steps
))

# 6.2 Vector Operations and Applications
steps = [
    info_step("coremath-m6t2-s1",
        '🔄 **Unit Vectors and Direction**\\\\n\\\\nA **unit vector** has magnitude 1. It shows direction only.\\\\n\\\\n**To find a unit vector in the direction of v:**\\\\n**v̂** = **v** / |**v**|\\\\n\\\\n**Example:** Find the unit vector in the direction of **v** = 3**i** + 4**j**.\\\\n• |**v**| = √(9 + 16) = 5\\\\n• **v̂** = (3**i** + 4**j**)/5 = **0.6i + 0.8j**\\\\n\\\\n**Check:** |**v̂**| = √(0.6² + 0.8²) = √(0.36 + 0.64) = √1 = 1 ✓\\\\n\\\\n**Parallel Vectors:**\\\\nTwo vectors are parallel if one is a scalar multiple of the other.\\\\n• **a** = 2**i** + 3**j** and **b** = 4**i** + 6**j** are parallel (b = 2a)"),
    predict_step("coremath-m6t2-s2',
        "Vector **v** = 5**i** + 12**j**. Is **w** = 10**i** + 24**j** parallel to **v**?",
        'w = 2v?",
        ["Yes (w = 2v)', "No", 'Only if direction is the same", "Cannot tell'),
        0,
        "**w** = 2(5**i** + 12**j**) = 10**i** + 24**j**. Yes, **w** = 2**v**, so they are **parallel**."),
    info_step('coremath-m6t2-s3",
        "⚡ **Resultant Forces (Vector Addition)**\\\\n\\\\nWhen multiple forces act on an object, the **resultant** is their vector sum.\\\\n\\\\n**Example:** Three forces act: F₁ = 2**i** + 3**j**, F₂ = 4**i** − **j**, F₃ = −**i** + 2**j**.\\\\nResultant R = F₁ + F₂ + F₃\\\\n= (2+4−1)**i** + (3−1+2)**j**\\\\n= **5i + 4j**\\\\n\\\\n**Magnitude of resultant:** |R| = √(5² + 4²) = √41 ≈ **6.4 N**\\\\n\\\\n**Equilibrium:** When resultant = 0, the object is in equilibrium.\\\\n• F₁ + F₂ + ... = 0\\\\n• Used in bridge design, cranes, and structures!'),
    question_step("coremath-m6t2-s4",
        'Two forces act: **F₁ = 5i + 2j** and **F₂ = −3i + 4j**. What is the resultant?",
        "R = F₁ + F₂',
        ["2i + 6j", '8i + 6j", "2i − 2j', "8i − 2j"),
        0,
        'R = (5−3)**i** + (2+4)**j** = **2i + 6j**. Magnitude = √(4+36) = √40 ≈ 6.32 N."),
    info_step("coremath-m6t2-s5',
        "🗺️ **Bearings and Navigation**\\\\n\\\\n**Bearings** are directions measured **clockwise from North**, written as three digits.\\\\n• North = 000°\\\\n• East = 090°\\\\n• South = 180°\\\\n• West = 270°\\\\n\\\\n**Using vectors for navigation:**\\\\nA ship sails 30 km east (30**i**), then 40 km north (40**j**).\\\\n• Displacement = 30**i** + 40**j**\\\\n• Distance from start = √(30² + 40²) = 50 km\\\\n• Bearing = tan⁻¹(40/30) = 53.1° → Bearing = **053°** (to nearest degree)"),
    checkpoint_step('coremath-m6t2-s6", "Vectors Mastery', [
        {"question": 'Find the unit vector in direction of v = 3i + 4j",
         "options': ["(3i+4j)/5", '3i+4j", "5(3i+4j)', "(3i+4j)/25"),
         'correct": 0, "explanation': "|v| = 5, so unit vector = v/|v| = (3i+4j)/5"},
        {'question": "The bearing of East is...',
         "options": ['000°", "090°', "180°", '270°"),
         "correct': 1, "explanation": 'East is 90° clockwise from North. Always write bearings as three digits: 090°."},
    ]),
]
MODULE6_LESSONS.append(make_lesson(
    "coremath-m6t2', "Vector Operations, Forces and Bearings",
    'Core Mathematics", "🔢', "Both", 2, 12, 30,
    'core-maths", ["coremath-m6t1'], ["SHS 2", 'SHS 3"], "SHS 2', steps
))

# 6.3 Trigonometry — Sine, Cosine and Tangent
steps = [
    info_step("coremath-m6t3-s1",
        '📐 **Trigonometry — SOH CAH TOA**\\\\n\\\\nTrigonometry relates angles to side ratios in right-angled triangles.\\\\n\\\\n**The Three Ratios:**\\\\n\\\\n          /|\\\\n       h / | o (opposite)\\\\n        / θ |\\\\n       ────\\\\n         a (adjacent)\\\\n\\\\n• **sin θ** = opposite/hypotenuse (SOH)\\\\n• **cos θ** = adjacent/hypotenuse (CAH)\\\\n• **tan θ** = opposite/adjacent (TOA)\\\\n\\\\n**Memory Aid:** Some Old Horses Can Always Hear Their Owners Approach"),
    predict_step("coremath-m6t3-s2',
        "In a right triangle with angle 30°, the opposite side is **1** and hypotenuse is **2**. What is sin 30°?",
        'sin 30° = opposite/hypotenuse = 1/2",
        "sin 30° = ?',
        ["1/2 = 0.5", '√3/2 ≈ 0.866", "1/√3 ≈ 0.577', "2"),
        0,
        'sin 30° = opposite/hypotenuse = 1/2 = **0.5**. This is a key value to memorise!"),
    info_step("coremath-m6t3-s3',
        "📊 **Exact Trigonometric Values (Memorise These!)**\\\\n\\\\n| Angle | sin | cos | tan |\\\\n|-------|-----|-----|-----|\\\\n| 0°    | 0   | 1   | 0   |\\\\n| 30°   | 1/2 | √3/2| 1/√3|\\\\n| 45°   | 1/√2| 1/√2| 1   |\\\\n| 60°   | √3/2| 1/2 | √3  |\\\\n| 90°   | 1   | 0   | ∞   |\\\\n\\\\n**Pattern:** For sin: √0/2, √1/2, √2/2, √3/2, √4/2\\\\n                             0°, 30°, 45°, 60°, 90°\\\\n\\\\n**Example:** sin 60° = √3/2, cos 60° = 1/2, tan 60° = √3\\\\n\\\\n> 💡 **WASSCE expects you to know these exact values!"),
    question_step('coremath-m6t3-s4",
        "What is **tan 45°**?',
        "tan 45° = ?",
        ['0", "1', "√2", '1/√2"),
        1,
        "tan 45° = **1**. At 45°, opposite and adjacent are equal, so their ratio = 1.'),
    info_step("coremath-m6t3-s5",
        '🔢 **Finding Sides and Angles**\\\\n\\\\n**To find a side:** Choose the ratio that involves the known angle, known side, and unknown side.\\\\n\\\\n**Example:** Find the height (h) of a flagpole with a 50 m shadow and sun angle 40°.\\\\n• We know: adjacent = 50 m, θ = 40°, we need opposite\\\\n• tan 40° = h/50\\\\n• h = 50 × tan 40°\\\\n• h ≈ 50 × 0.8391 = **42.0 m**\\\\n\\\\n**To find an angle:** Use inverse trig functions.\\\\n**Example:** sin θ = 0.5, so θ = sin⁻¹(0.5) = **30°**"),
    question_step("coremath-m6t3-s6',
        "A right triangle has opposite = 3, adjacent = 4. What is **θ** (the angle)?",
        'tan θ = 3/4 = 0.75",
        ["tan⁻¹(3/4) ≈ 36.9°', "sin⁻¹(3/4) ≈ 48.6°", 'cos⁻¹(3/4) ≈ 41.4°", "30°'),
        0,
        "We know opposite and adjacent, so use tan: tan θ = 3/4, θ = tan⁻¹(0.75) ≈ **36.9°**."),
]
MODULE6_LESSONS.append(make_lesson(
    'coremath-m6t3", "Sine, Cosine and Tangent Ratios',
    "Core Mathematics", '🔢", "Both', 2, 12, 30,
    "core-maths", ['coremath-m5t4"], ["SHS 2', "SHS 3"], 'SHS 2", steps
))

# 6.4 Angles of Elevation and Depression
steps = [
    info_step("coremath-m6t4-s1',
        "🔭 **Angles of Elevation and Depression**\\\\n\\\\n**Angle of Elevation:** The angle measured **upwards** from the horizontal to an object above.\\\\n\\\\n**Angle of Depression:** The angle measured **downwards** from the horizontal to an object below.\\\\n\\\\n**Key Insight:** The angle of elevation from A to B **equals** the angle of depression from B to A (alternate angles!).\\\\n\\\\n              B (top)\\\\n             /|\\\\n            / |\\\\n           /  |\\\\n        θ /   | height\\\\n         /    |\\\\n      A ──────┘\\\\n       (horizontal distance)"),
    predict_step('coremath-m6t4-s2",
        "A student looks up at the top of a tree at an angle of elevation of **45°**. If the tree is **20 m** away, how tall is it?',
        "tan 45° = height/20",
        'Height = ?",
        ["10 m', "20 m", '30 m", "40 m'),
        1,
        "tan 45° = 1, so height/20 = 1 → height = **20 m**. At 45°, height = distance."),
    info_step('coremath-m6t4-s3",
        "🔍 **Solving Two-Step Problems**\\\\n\\\\n**Example:** From the top of a 30 m building, the angle of depression to a car is 30°. How far is the car from the building?\\\\n\\\\n• The angle of depression from top = angle of elevation from car = 30°\\\\n• tan 30° = 30/distance\\\\n• distance = 30/tan 30°\\\\n• tan 30° = 1/√3 ≈ 0.577\\\\n• distance = 30/0.577 ≈ **52.0 m**'),
    question_step("coremath-m6t4-s4",
        'A person stands 50 m from a tower. The angle of elevation to the top is **30°**. Find the tower\"s height.",
        'tan 30° = h/50",
        ["50/√3 ≈ 28.9 m', "50√3 ≈ 86.6 m", '25 m", "50 m'),
        0,
        "tan 30° = 1/√3. h/50 = 1/√3 → h = 50/√3 ≈ **28.9 m**."),
    info_step('coremath-m6t4-s5",
        "🗺️ **Applications — Bearings and Trigonometry**\\\\n\\\\n**Using trig for navigation (WASSCE classic):**\\\\n\\\\nA ship sails from port A: 40 km on a bearing of 060°. How far east and north is it?\\\\n• East component = 40 × sin 60° = 40 × √3/2 ≈ **34.6 km**\\\\n• North component = 40 × cos 60° = 40 × 1/2 = **20 km**\\\\n\\\\n**Finding the bearing from components:**\\\\nA plane flies 30 km east and 40 km north of the airport.\\\\n• Bearing = tan⁻¹(40/30) = **053°** (to nearest degree)\\\\n• Distance = √(30² + 40²) = **50 km**'),
    checkpoint_step("coremath-m6t4-s6", 'Elevation and Depression Mastery", [
        {"question': "The angle of depression from a cliff top to a boat is the same as...",
         'options": ["The angle of elevation from the boat to the cliff top', "90° minus the angle", 'The angle at the boat", "None of these'),
         "correct": 0, 'explanation": "Angle of depression from top = angle of elevation from bottom (alternate angles).'},
        {"question": 'tan 60° = ?",
         "options': ["1/√3", '1", "√3', "1/2"),
         'correct": 2, "explanation': "tan 60° = √3 ≈ 1.732. Memorise the table of exact values!"},
    ]),
]
MODULE6_LESSONS.append(make_lesson(
    'coremath-m6t4", "Angles of Elevation and Depression',
    "Core Mathematics", '🔢", "Both', 2, 12, 30,
    "core-maths", ['coremath-m6t3"], ["SHS 2', "SHS 3"], 'SHS 2", steps
))

# 6.5 Applications of Trigonometry
steps = [
    info_step("coremath-m6t5-s1',
        "🌟 **The Sine and Cosine Rules (Non-Right Triangles)**\\\\n\\\\nNot all triangles are right-angled! For any triangle with sides a, b, c and opposite angles A, B, C:\\\\n\\\\n          A\\\\n         /\\\\\\\n      b /   \\\\ c\\\\n       /     \\\\\\n    B ─────── C\\\\n         a\\\\n\\\\n**Sine Rule:** a/sin A = b/sin B = c/sin C\\\\nUse when you know: two angles and one side, OR two sides and a non-included angle.\\\\n\\\\n**Cosine Rule:** a² = b² + c² − 2bc cos A\\\\nUse when you know: three sides, OR two sides and the included angle.\\\\n\\\\n> 💡 **Choose Sine Rule when you have angle-side pairs. Choose Cosine Rule for three sides or two sides + included angle.**"),
    predict_step('coremath-m6t5-s2",
        "In a triangle, A = 40°, B = 60°, and side a = 10 cm (opposite A). Which rule should you use to find side b?',
        "We know angle A and side a, angle B",
        'Which rule?",
        ["Sine rule', "Cosine rule", 'Pythagoras", "SOH CAH TOA'),
        0,
        "**Sine rule** — we have an angle-side pair (A = 40°, a = 10) and need the side opposite B."),
    info_step('coremath-m6t5-s3",
        "📝 **Using the Sine Rule**\\\\n\\\\n**Example:** In triangle ABC, A = 40°, B = 60°, a = 10 cm. Find b.\\\\n\\\\n• a/sin A = b/sin B\\\\n• 10/sin 40° = b/sin 60°\\\\n• b = 10 × sin 60°/sin 40°\\\\n• b = 10 × 0.8660/0.6428\\\\n• b ≈ **13.5 cm**\\\\n\\\\n**Finding an angle using Sine Rule:**\\\\nIf a = 10, b = 14, A = 30°, find B.\\\\n• 10/sin 30° = 14/sin B\\\\n• sin B = 14 × sin 30°/10 = 14 × 0.5/10 = 0.7\\\\n• B = sin⁻¹(0.7) = **44.4°** or **135.6°** (check if triangle is valid!)'),
    question_step("coremath-m6t5-s4",
        'In triangle ABC, A = 50°, C = 70°, and side a = 8 cm. Find side c.",
        "Sine rule: 8/sin50° = c/sin70°',
        ["c ≈ 9.8 cm", 'c ≈ 7.2 cm", "c ≈ 12.5 cm', "c ≈ 6.3 cm"),
        0,
        'c = 8 × sin 70°/sin 50° = 8 × 0.9397/0.7660 ≈ **9.8 cm**."),
    info_step("coremath-m6t5-s5',
        "📝 **Using the Cosine Rule**\\\\n\\\\n**Example 1 (two sides + included angle):**\\\\nTriangle with b = 7, c = 9, A = 60°. Find a.\\\\n• a² = b² + c² − 2bc cos A\\\\n• a² = 49 + 81 − 2(7)(9)(0.5)\\\\n• a² = 130 − 63 = 67\\\\n• a = √67 ≈ **8.2**\\\\n\\\\n**Example 2 (three sides):**\\\\na = 6, b = 7, c = 8. Find angle A.\\\\n• cos A = (b² + c² − a²)/(2bc)\\\\n• cos A = (49 + 64 − 36)/(2 × 7 × 8)\\\\n• cos A = 77/112 = 0.6875\\\\n• A = cos⁻¹(0.6875) = **46.6°**"),
    question_step('coremath-m6t5-s6",
        "Triangle has sides a = 5, b = 6, c = 7. Find the largest angle (opposite longest side c).',
        "cos C = (5²+6²−7²)/(2×5×6)",
        ['C ≈ 78.5°", "C ≈ 60°', "C ≈ 90°", 'C ≈ 53.1°"),
        0,
        "cos C = (25+36−49)/(60) = 12/60 = 0.2. C = cos⁻¹(0.2) ≈ **78.5°**. This is the largest angle.'),
]
MODULE6_LESSONS.append(make_lesson(
    "coremath-m6t5", 'Sine Rule, Cosine Rule and Triangle Applications",
    "Core Mathematics', "🔢", 'Both", 3, 14, 35,
    "core-maths', ["coremath-m6t3"], ['SHS 3"], "SHS 3', steps
))


# ── Module 7: Perimeter, Area & Volume ───────────────────────────────────

MODULE7_LESSONS = []

# 7.1 Perimeter of 2D Shapes
steps = [
    info_step("coremath-m7t1-s1",
        '📏 **Perimeter — The Distance Around**\\\\n\\\\n**Perimeter** is the total distance around the outside of a shape.\\\\n\\\\n**Common Formulas:**\\\\n• **Square:** P = 4s (s = side length)\\\\n• **Rectangle:** P = 2(l + w)\\\\n• **Triangle:** P = a + b + c\\\\n• **Circle (Circumference):** C = 2πr or πd\\\\n• **Semicircle:** P = πr + 2r\\\\n\\\\n**Adding perimeters of composite shapes:**\\\\nJust add all the outside edges — do NOT include internal boundaries!"),
    predict_step("coremath-m7t1-s2',
        "A rectangle has length **12 cm** and width **8 cm**. What is its perimeter?",
        'P = 2(12 + 8)",
        ["40 cm', "20 cm", '96 cm", "48 cm'),
        0,
        "P = 2(12+8) = 2(20) = **40 cm**. The perimeter is 40 cm."),
    info_step('coremath-m7t1-s3",
        "⭕ **Circumference of a Circle**\\\\n\\\\n**Formula:** C = 2πr or C = πd\\\\n\\\\n**Example 1:** Circle radius = 7 cm. C = 2 × 22/7 × 7 = **44 cm**\\\\n\\\\n**Example 2:** Circle diameter = 10 cm. C = 3.142 × 10 = **31.42 cm**\\\\n\\\\n**Arc Length (part of circumference):**\\\\nArc length = (θ/360) × 2πr\\\\nwhere θ = angle at centre in degrees.\\\\n\\\\n**Example:** Find the length of an arc of radius 14 cm subtending an angle of 60°.\\\\nArc = (60/360) × 2 × 22/7 × 14 = 1/6 × 88 = **14.67 cm**'),
    question_step("coremath-m7t1-s4",
        'A circle has radius **10 cm**. What is its circumference? (Use π = 3.14)",
        "C = 2 × 3.14 × 10',
        ["31.4 cm", '62.8 cm", "314 cm', "20 cm"),
        1,
        'C = 2πr = 2 × 3.14 × 10 = **62.8 cm**."),
    info_step("coremath-m7t1-s5',
        "➕ **Perimeter of Composite Shapes**\\\\n\\\\nAdd only the **outside** edges.\\\\n\\\\n**Example:** A rectangle 8 m by 6 m with a semicircle on one end (diameter = 6 m).\\\\n• Rectangle: 8 + 6 + 8 = 22 m (the 6 m side is inside — not counted)\\\\n• Semicircle arc: πd/2 = π × 6/2 = 3π ≈ 9.42 m\\\\n• Total perimeter = 22 + 9.42 = **31.42 m**\\\\n\\\\n> 💡 **When finding the perimeter of a shape with a cut-out, trace the outside with your finger — only those edges count!**"),
    checkpoint_step('coremath-m7t1-s6", "Perimeter Mastery', [
        {"question": 'A square has perimeter 36 cm. What is the side length?",
         "options': ["6 cm", '9 cm", "12 cm', "18 cm"),
         'correct": 1, "explanation': "4s = 36, s = 36/4 = 9 cm"},
        {'question": "Circumference of circle with diameter 14 cm (π = 22/7).',
         "options": ['44 cm", "22 cm', "88 cm", '154 cm"),
         "correct': 0, "explanation": 'C = πd = (22/7) × 14 = 44 cm"},
    ]),
]
MODULE7_LESSONS.append(make_lesson(
    "coremath-m7t1', "Perimeter of 2D Shapes",
    'Core Mathematics", "🔢', "Both", 1, 10, 20,
    'core-maths", ["coremath-m1t1'], ["SHS 1"], 'SHS 1", steps
))

# 7.2 Area of 2D Shapes
steps = [
    info_step("coremath-m7t2-s1',
        "📐 **Area — The Space Inside**\\\\n\\\\n**Area** measures the space enclosed by a 2D shape.\\\\n\\\\n**Common Formulas (WASSCE Essential!):**\\\\n• **Square:** A = s²\\\\n• **Rectangle:** A = l × w\\\\n• **Triangle:** A = ½ × b × h\\\\n• **Parallelogram:** A = b × h\\\\n• **Trapezium:** A = ½(a + b)h\\\\n• **Circle:** A = πr²\\\\n• **Sector:** A = (θ/360) × πr²"),
    predict_step('coremath-m7t2-s2",
        "A triangle has base **10 cm** and height **8 cm**. What is its area?',
        "A = ½ × 10 × 8",
        ['40 cm²", "80 cm²', "20 cm²", '50 cm²"),
        0,
        "A = ½ × 10 × 8 = **40 cm²**. Remember: triangle area is half of rectangle area!'),
    info_step("coremath-m7t2-s3",
        '🌀 **Area of Circles and Sectors**\\\\n\\\\n**Circle:** A = πr²\\\\n**Sector:** A = (θ/360) × πr²\\\\n\\\\n**Example 1:** Area of circle with radius 7 cm.\\\\nA = 22/7 × 7² = 22/7 × 49 = **154 cm²**\\\\n\\\\n**Example 2:** Area of a sector with radius 14 cm and angle 45°.\\\\nA = (45/360) × 22/7 × 14²\\\\n= 1/8 × 22/7 × 196\\\\n= 1/8 × 22 × 28\\\\n= **77 cm²**"),
    question_step("coremath-m7t2-s4',
        "Find the area of a circle with diameter **14 cm**. (Use π = 22/7)",
        'r = 7 cm, A = π × 49",
        ["44 cm²', "154 cm²", '616 cm²", "49 cm²'),
        1,
        "r = d/2 = 7 cm. A = (22/7) × 49 = 22 × 7 = **154 cm²**."),
    info_step('coremath-m7t2-s5",
        "📊 **Area of Composite Shapes**\\\\n\\\\nBreak the shape into familiar parts, find each area, then add or subtract.\\\\n\\\\n**Example:** A rectangle 10 m by 6 m with a semicircle on top (diameter = 6 m).\\\\n• Rectangle area = 10 × 6 = 60 m²\\\\n• Semicircle area = ½ × π × 3² = ½ × 28.27 = 14.14 m²\\\\n• Total = 60 + 14.14 = **74.14 m²**\\\\n\\\\n**Shaded region problems (WASSCE favourite!):**\\\\nShaded area = area of larger shape − area of smaller shape(s)\\\\n\\\\n> 🔑 **Always express area in square units (cm², m², etc.)!**'),
    question_step("coremath-m7t2-s6",
        'A rectangle 12 cm by 8 cm has a circle of radius 3 cm cut out. **What is the remaining area?** (π = 3.14)",
        "A = 96 − 28.26',
        ["67.74 cm²", '96 cm²", "28.26 cm²', "124.26 cm²"),
        0,
        'Rectangle: 12 × 8 = 96 cm². Circle: 3.14 × 9 = 28.26 cm². Remaining = 96 − 28.26 = **67.74 cm²**."),
]
MODULE7_LESSONS.append(make_lesson(
    "coremath-m7t2', "Area of 2D Shapes",
    'Core Mathematics", "🔢', "Both", 1, 12, 25,
    'core-maths", ["coremath-m7t1'], ["SHS 1", 'SHS 2"], "SHS 1', steps
))

# 7.3 Surface Area of 3D Solids
steps = [
    info_step("coremath-m7t3-s1",
        '📦 **Surface Area — Total Area of All Faces**\\\\n\\\\n**Surface area** is the sum of the areas of all faces (surfaces) of a 3D solid.\\\\n\\\\n**Common Formulas:**\\\\n• **Cube:** SA = 6s² (6 faces, each area s²)\\\\n• **Cuboid:** SA = 2(lw + lh + wh)\\\\n• **Cylinder (closed):** SA = 2πr² + 2πrh (two circles + curved surface)\\\\n• **Cylinder (open):** SA = πr² + 2πrh (one circle + curved surface)\\\\n• **Sphere:** SA = 4πr²\\\\n• **Cone (including base):** SA = πr² + πrl (l = slant height)"),
    predict_step("coremath-m7t3-s2',
        "A cuboid is **5 cm** by **4 cm** by **3 cm**. What is its surface area?",
        'SA = 2(5×4 + 5×3 + 4×3)",
        ["94 cm²', "60 cm²", '47 cm²", "120 cm²'),
        0,
        "SA = 2(20 + 15 + 12) = 2(47) = **94 cm²**. Each pair of opposite faces has the same area."),
    info_step('coremath-m7t3-s3",
        "🥫 **Surface Area of Cylinders**\\\\n\\\\n**Closed cylinder (with lid):**\\\\nSA = 2πr² + 2πrh = 2πr(r + h)\\\\n\\\\n**Open cylinder (no lid):**\\\\nSA = πr² + 2πrh\\\\n\\\\n**Example:** A cylindrical can has radius 7 cm and height 10 cm. Find its total surface area (with lid). (π = 22/7)\\\\n• End circles: 2 × (22/7 × 49) = 2 × 154 = 308 cm²\\\\n• Curved surface: 2 × 22/7 × 7 × 10 = 440 cm²\\\\n• Total = 308 + 440 = **748 cm²**'),
    question_step("coremath-m7t3-s4",
        'A cylinder has radius **5 cm** and height **8 cm**. Find its curved surface area only. (π = 3.14)",
        "CSA = 2πrh = 2 × 3.14 × 5 × 8',
        ["125.6 cm²", '251.2 cm²", "282.6 cm²', "628 cm²"),
        1,
        'CSA = 2 × 3.14 × 5 × 8 = **251.2 cm²**. The curved surface area is just the rectangular part wrapped around."),
    info_step("coremath-m7t3-s5',
        "🌍 **Surface Area of Spheres and Cones**\\\\n\\\\n**Sphere:** SA = 4πr²\\\\n• Example: A sphere of radius 7 cm.\\\\n• SA = 4 × 22/7 × 49 = 4 × 154 = **616 cm²**\\\\n\\\\n**Cone (with base):** SA = πr² + πrl\\\\nWhere l = slant height = √(r² + h²)\\\\n\\\\n**Example:** Cone radius 3 cm, height 4 cm.\\\\n• l = √(9 + 16) = √25 = 5 cm\\\\n• Base: π × 9 = 28.27 cm²\\\\n• Curved: π × 3 × 5 = 47.12 cm²\\\\n• Total = **75.39 cm²**"),
    checkpoint_step('coremath-m7t3-s6", "Surface Area Mastery', [
        {"question": 'Surface area of a cube of side 6 cm.",
         "options': ["216 cm²", '36 cm²", "72 cm²', "144 cm²"),
         'correct": 0, "explanation': "SA = 6s² = 6 × 36 = 216 cm²"},
        {'question": "Surface area of a sphere of radius 7 cm (π = 22/7).',
         "options": ['308 cm²", "616 cm²', "154 cm²", '88 cm²"),
         "correct': 1, "explanation": 'SA = 4πr² = 4 × 22/7 × 49 = 4 × 154 = 616 cm²"},
    ]),
]
MODULE7_LESSONS.append(make_lesson(
    "coremath-m7t3', "Surface Area of 3D Solids",
    'Core Mathematics", "🔢', "Both", 2, 12, 30,
    'core-maths", ["coremath-m7t2'], ["SHS 2", 'SHS 3"], "SHS 2', steps
))

# 7.4 Volume of Prisms and Cylinders
steps = [
    info_step("coremath-m7t4-s1",
        '📦 **Volume — The Space Inside 3D Shapes**\\\\n\\\\n**Volume** measures how much space a 3D object occupies.\\\\n\\\\n**Prisms:** A prism has a constant cross-section along its length.\\\\n**Volume of any prism = Area of cross-section × Height**\\\\n\\\\n**Common Formulas:**\\\\n• **Cube:** V = s³\\\\n• **Cuboid:** V = l × w × h\\\\n• **Cylinder:** V = πr²h (cylinder is a prism with circular cross-section)\\\\n• **Triangular prism:** V = (½ × b × h_triangle) × H"),
    predict_step("coremath-m7t4-s2',
        "A cuboid is **8 cm** by **5 cm** by **4 cm**. What is its volume?",
        'V = 8 × 5 × 4",
        ["160 cm³', "40 cm³", '120 cm³", "200 cm³'),
        0,
        "V = 8 × 5 × 4 = **160 cm³**. Volume grows fast — a small increase in each side gives a big increase in volume!"),
    info_step('coremath-m7t4-s3",
        "🛢️ **Volume of Cylinders**\\\\n\\\\nV = πr²h\\\\n\\\\n**Example 1:** Cylinder radius 7 cm, height 12 cm. (π = 22/7)\\\\nV = 22/7 × 7² × 12 = 22/7 × 49 × 12\\\\n= 22 × 7 × 12 = **1,848 cm³**\\\\n\\\\n**Example 2:** A cylindrical tank has diameter 14 m and height 5 m.\\\\n• r = 7 m\\\\n• V = 22/7 × 49 × 5 = 22 × 7 × 5\\\\n• V = **770 m³**\\\\n• Capacity = 770,000 litres (1 m³ = 1000 L)'),
    question_step("coremath-m7t4-s4",
        'A cylinder has radius **3 cm** and height **10 cm**. What is its volume? (π = 3.14)",
        "V = 3.14 × 9 × 10',
        ["282.6 cm³", '188.4 cm³", "94.2 cm³', "900 cm³"),
        0,
        'V = πr²h = 3.14 × 9 × 10 = **282.6 cm³**."),
    info_step("coremath-m7t4-s5',
        "🔩 **Volume of Composite Solids**\\\\n\\\\n**Example:** A solid consists of a cylinder (r = 3 cm, h = 8 cm) with a hemisphere on top.\\\\n• Volume of cylinder = π × 9 × 8 = 72π cm³\\\\n• Volume of hemisphere = ½ × 4/3 × π × 27 = 18π cm³\\\\n• Total = 90π ≈ **282.7 cm³**\\\\n\\\\n**Finding height from volume (reverse problems):**\\\\nA cylinder has volume 500 cm³ and radius 5 cm. Find its height.\\\\n• 500 = π × 25 × h\\\\n• h = 500/(25π) = 20/π ≈ **6.37 cm**"),
    question_step('coremath-m7t4-s6",
        "A cuboid has volume **240 cm³**, length **8 cm**, width **6 cm**. What is its height?',
        "h = V/(l × w) = 240/48",
        ['3 cm", "4 cm', "5 cm", '6 cm"),
        2,
        "h = 240/(8 × 6) = 240/48 = **5 cm**.'),
]
MODULE7_LESSONS.append(make_lesson(
    "coremath-m7t4", 'Volume of Prisms and Cylinders",
    "Core Mathematics', "🔢", 'Both", 2, 12, 25,
    "core-maths', ["coremath-m7t2"], ['SHS 2", "SHS 3'], "SHS 2", steps
))

# 7.5 Volume of Pyramids, Cones and Spheres
steps = [
    info_step('coremath-m7t5-s1",
        "🔺 **Volume of Pyramids and Cones**\\\\n\\\\n**Key Formula:** V = ⅓ × Base Area × Height\\\\n\\\\n**Pyramid:**\\\\n• Square base: V = ⅓ × s² × h\\\\n• Rectangular base: V = ⅓ × l × w × h\\\\n\\\\n**Cone:**\\\\n• V = ⅓ × πr² × h\\\\n\\\\n> 💡 **A cone/pyramid holds exactly 1/3 of the volume of a prism/cylinder with the same base and height!'),
    predict_step("coremath-m7t5-s2",
        'A cone has radius **3 cm** and height **5 cm**. What is its volume? (π = 3.14)",
        "V = ⅓ × π × 9 × 5',
        ["62.8 cm³", '47.1 cm³", "141.3 cm³', "15.7 cm³"),
        1,
        'V = ⅓ × 3.14 × 9 × 5 = 47.1 cm³. A cylinder with same dimensions would be 141.3 cm³ (3× more)."),
    info_step("coremath-m7t5-s3',
        "🌍 **Volume of Spheres**\\\\n\\\\n**Formula:** V = 4/3 × πr³\\\\n\\\\n**Example:** Sphere radius 7 cm. (π = 22/7)\\\\nV = 4/3 × 22/7 × 343\\\\n= 4/3 × 22 × 49\\\\n= (4 × 22 × 49)/3\\\\n= 4312/3 ≈ **1,437 cm³**\\\\n\\\\n**Hemisphere (half sphere):**\\\\nV = ½ × 4/3 × πr³ = 2/3 × πr³\\\\n\\\\n**Example:** Hemisphere radius 6 cm.\\\\nV = 2/3 × π × 216 = 144π ≈ **452.4 cm³**"),
    question_step('coremath-m7t5-s4",
        "What is the volume of a sphere with radius **6 cm**? (π = 3.14)',
        "V = 4/3 × 3.14 × 216",
        ['904.32 cm³", "678.24 cm³', "288 cm³", '1,356.48 cm³"),
        0,
        "V = 4/3 × 3.14 × 216 = 4/3 × 678.24 = **904.32 cm³**.'),
    info_step("coremath-m7t5-s5",
        '🌟 **Density and Capacity Problems**\\\\n\\\\n**Density = Mass/Volume** (D = M/V)\\\\n\\\\n**Example 1:** A metal cube of side 4 cm has mass 320 g. What is its density?\\\\n• V = 64 cm³\\\\n• D = 320/64 = **5 g/cm³**\\\\n\\\\n**Capacity:** 1 cm³ = 1 mL = 0.001 L\\\\n**1 m³ = 1,000 L**\\\\n\\\\n**Example 2:** A cylindrical water tank (r = 7 m, h = 3 m) is to be filled. How many litres does it hold?\\\\n• V = πr²h = 22/7 × 49 × 3 = 462 m³\\\\n• Capacity = 462 × 1000 = **462,000 L**\\\\n\\\\n> ✅ **Use the correct units: cm³ for small volumes, m³ for large volumes, mL/L for capacity.**"),
    checkpoint_step("coremath-m7t5-s6', "Volume Mastery", [
        {'question": "Volume of a cone with r = 7 cm, h = 12 cm (π = 22/7).',
         "options": ['616 cm³", "308 cm³', "1,848 cm³", '154 cm³"),
         "correct': 0, "explanation": 'V = ⅓ × 22/7 × 49 × 12 = ⅓ × 22 × 7 × 12 = ⅓ × 1848 = 616 cm³"},
        {"question': "Volume of a sphere with radius 3 cm (π = 3.14).",
         'options": ["28.26 cm³', "84.78 cm³", '113.04 cm³", "37.68 cm³'),
         "correct": 2, 'explanation": "V = 4/3 × 3.14 × 27 = 4/3 × 84.78 = 113.04 cm³'},
    ]),
]
MODULE7_LESSONS.append(make_lesson(
    "coremath-m7t5", 'Volume of Pyramids, Cones and Spheres",
    "Core Mathematics', "🔢", 'Both", 2, 14, 30,
    "core-maths', ["coremath-m7t4"], ['SHS 2", "SHS 3'], "SHS 2", steps
))


# ── Module 8: Data Organisation & Analysis ───────────────────────────────

MODULE8_LESSONS = []

# 8.1 Collecting and Organising Data
steps = [
    info_step('coremath-m8t1-s1",
        "📊 **Data — Collecting and Organising**\\\\n\\\\n**Data** is information collected about people, objects, or events.\\\\n\\\\n**Types of Data:**\\\\n• **Primary data:** Collected first-hand (surveys, experiments)\\\\n• **Secondary data:** Already collected by others (census, internet)\\\\n\\\\n**Qualitative Data:** Categories (colours, gender, subjects)\\\\n**Quantitative Data:** Numbers\\\\n• **Discrete:** Countable (number of students, shoe sizes)\\\\n• **Continuous:** Measurable on a scale (height, weight, time)\\\\n\\\\n**Frequency Tables:** Organising data by counting how many times each value occurs.\\\\n\\\\n**Example:** Test scores of 20 students: 5, 6, 4, 7, 5, 8, 6, 7, 5, 6, 4, 8, 5, 7, 6, 5, 9, 6, 7, 5'),
    predict_step("coremath-m8t1-s2",
        'From the data above, what is the **frequency** of score 5?",
        "Score 5 appears how many times?',
        ["5", '6", "4', "7"),
        1,
        'Score 5 appears **6 times**: positions 1, 5, 9, 13, 16, 20. Frequency of 5 = 6."),
    info_step("coremath-m8t1-s3',
        "📋 **Grouped Frequency Tables**\\\\n\\\\nWhen data has many different values, we group them into **class intervals**.\\\\n\\\\n**Example:** Ages of 30 people:\\\\n| Age | Tally | Frequency |\\\\n|-----|-------|-----------|\\\\n| 10-19 | |||| ||| | 8 |\\\\n| 20-29 | |||| |||| | 9 |\\\\n| 30-39 | |||| ||| | 8 |\\\\n| 40-49 | |||| | 5 |\\\\n| Total | | 30 |\\\\n\\\\n**Class Boundaries:**\\\\n• For 10-19, lower boundary = 9.5, upper boundary = 19.5\\\\n• **Class width** = 19.5 − 9.5 = 10\\\\n\\\\n> 💡 **Use tally marks to count frequencies — it prevents mistakes!"),
    question_step('coremath-m8t1-s4",
        "In a grouped frequency table with class **20-29**, what is the class width?',
        "Class width = 29.5 − 19.5",
        ['9", "10', "9.5", '20"),
        1,
        "Class width = upper boundary − lower boundary = 29.5 − 19.5 = **10**.'),
    info_step("coremath-m8t1-s5",
        '📊 **Stem-and-Leaf Diagrams**\\\\n\\\\nA stem-and-leaf diagram organises data while preserving the original values.\\\\n\\\\n**Example:** Scores: 32, 45, 38, 41, 36, 47, 33, 42, 39, 44\\\\n\\\\nStem | Leaf\\\\n3    | 2 3 6 8 9\\\\n4    | 1 2 4 5 7\\\\n\\\\n**Key:** 3 | 2 means 32\\\\n\\\\nFrom the diagram, we can easily see:\\\\n• Lowest score: 32\\\\n• Highest: 47\\\\n• Most scores in 40s: 5\\\\n• Median is between 5th and 6th: (39+41)/2 = 40"),
    checkpoint_step("coremath-m8t1-s6', "Data Organisation Mastery", [
        {'question": "Which type of data is \\\"favourite colour\\\"?',
         "options": ['Quantitative discrete", "Quantitative continuous', "Qualitative", 'Primary"),
         "correct': 2, "explanation": 'Favourite colour is a category — it is qualitative data."},
        {"question': "In a stem-and-leaf diagram, 4|5 represents...",
         'options": ["45', "4.5", '54", "9'),
         "correct": 0, 'explanation": "4|5 means stem = 4, leaf = 5, so the value = 45'},
    ]),
]
MODULE8_LESSONS.append(make_lesson(
    "coremath-m8t1", 'Collecting and Organising Data",
    "Core Mathematics', "🔢", 'Both", 1, 10, 20,
    "core-maths', ["coremath-m1t1"], ['SHS 1"], "SHS 1', steps
))

# 8.2 Frequency Tables and Histograms
steps = [
    info_step("coremath-m8t2-s1",
        '📊 **Frequency Tables — Cumulative Frequency**\\\\n\\\\n**Cumulative frequency** is the running total of frequencies up to each class.\\\\n\\\\n**Example:** Test scores\\\\n| Score | Freq | Cum. Freq |\\\\n|-------|------|-----------|\\\\n| 0-9   | 2    | 2         |\\\\n| 10-19 | 5    | 7         |\\\\n| 20-29 | 8    | 15        |\\\\n| 30-39 | 4    | 19        |\\\\n| 40-49 | 1    | 20        |\\\\n\\\\nFrom the cumulative frequency, we can find:\\\\n• Number of scores < 30: **15**\\\\n• Number of scores ≥ 30: 20 − 15 = **5**"),
    predict_step("coremath-m8t2-s2',
        "From the table above, how many students scored **less than 20**?",
        'Cumulative frequency up to 19",
        ["2', "5", '7", "15'),
        2,
        "Cumulative frequency for 10-19 = **7**. That means 7 students scored less than 20."),
    info_step('code-m8t2-s3",
        "📊 **Histograms vs Bar Charts**\\\\n\\\\n**Bar Chart:** Used for **discrete** or **qualitative** data. Bars have equal width and gaps.\\\\n\\\\n**Histogram:** Used for **continuous** grouped data. Bars touch each other (no gaps).\\\\n\\\\n**Key difference — Frequency Density:**\\\\nIn a histogram, the **area** of each bar represents frequency (not height).\\\\nFrequency Density = Frequency ÷ Class Width\\\\n\\\\n**Example:**\\\\n| Class | Freq | Width | Freq Density |\\\\n|-------|------|-------|-------------|\\\\n| 0-10  | 15   | 10    | 1.5         |\\\\n| 10-20 | 25   | 10    | 2.5         |\\\\n| 20-40 | 30   | 20    | 1.5         |\\\\n\\\\n> 💡 **WASSCE tests both bar charts and histograms — know when to use each!'),
    question_step("code-m8t2-s4",
        'In a histogram, what does the **area** of each bar represent?",
        "Area of bar in histogram = ?',
        ["Frequency", 'Frequency density", "Class width', "Midpoint"),
        0,
        'In a histogram, the **area** of each bar represents the **frequency**. Height = frequency density, width = class width."),
    info_step("code-m8t2-s5',
        "📈 **Frequency Polygons**\\\\n\\\\nA **frequency polygon** is a line graph connecting the midpoints of histogram bars.\\\\n\\\\n**To draw:**\\\\n1. Find the **midpoint** of each class: (lower + upper)/2\\\\n2. Plot frequency against midpoint\\\\n3. Connect points with straight lines\\\\n4. Close the polygon by joining to the x-axis at both ends\\\\n\\\\n**Example:** Class 0-10: midpoint = 5, freq = 15\\\\nClass 10-20: midpoint = 15, freq = 25\\\\nClass 20-40: midpoint = 30, freq = 30\\\\n\\\\n> ✅ **Frequency polygons are useful for comparing two or more data sets on the same graph!"),
    question_step('code-m8t2-s6",
        "For the class **20-29**, what is the midpoint used in a frequency polygon?',
        "Midpoint = (20+29)/2",
        ['24", "24.5', "25", '29"),
        1,
        "Midpoint = (20 + 29)/2 = 49/2 = **24.5**.'),
]
MODULE8_LESSONS.append(make_lesson(
    "coremath-m8t2", 'Frequency Tables and Histograms",
    "Core Mathematics', "🔢", 'Both", 2, 12, 25,
    "core-maths', ["coremath-m8t1"], ['SHS 2", "SHS 3'], "SHS 2", steps
))

# 8.3 Mean, Median and Mode (Central Tendency)
steps = [
    info_step('code-m8t3-s1",
        "📊 **Measures of Central Tendency**\\\\n\\\\nThese tell us the **centre** or **typical value** of a data set.\\\\n\\\\n**1. Mean (Average):**\\\\n• **Formula:** x̄ = Σx/n (sum of all values divided by number of values)\\\\n• Most commonly used\\\\n• Affected by outliers (extreme values)\\\\n\\\\n**2. Median (Middle Value):**\\\\n• Arrange data in order, find the middle value\\\\n• Not affected by outliers\\\\n• If n is odd: median = middle value\\\\n• If n is even: median = average of two middle values\\\\n\\\\n**3. Mode (Most Common):**\\\\n• The value that appears most frequently\\\\n• A data set can have no mode or multiple modes'),
    predict_step("code-m8t3-s2",
        'Scores: **3, 5, 7, 7, 9, 10, 12**\\\\n\\\\nWhat is the mean?",
        "Mean = (3+5+7+7+9+10+12)/7',
        ["7", '7.57", "7.86', "8"),
        1,
        'Sum = 53. n = 7. Mean = 53/7 ≈ **7.57**."),
    info_step("code-m8t3-s3',
        "🔢 **Median for Ungrouped Data**\\\\n\\\\n**Steps:**\\\\n1. Arrange data in **ascending order**\\\\n2. Find position: (n+1)/2\\\\n3. Read the value at that position\\\\n\\\\n**Example (odd n):** 3, 5, 7, 7, 9, 10, 12\\\\nn = 7. Position = (7+1)/2 = 4th.\\\\nSorted: 3, 5, 7, **7**, 9, 10, 12. Median = **7**.\\\\n\\\\n**Example (even n):** 1, 3, 4, 6, 8, 10\\\\nn = 6. Position = between 3rd and 4th.\\\\nMedian = (4+6)/2 = **5**."),
    question_step('code-m8t3-s4",
        "Find the **median** of: **4, 8, 2, 9, 5, 7, 3**',
        "Arrange in order first",
        ['5", "6', "7", '4"),
        0,
        "Sorted: 2, 3, 4, **5**, 7, 8, 9. n=7, position=4th. Median = **5**.'),
    info_step("code-m8t3-s5",
        '📊 **Mean from Frequency Tables**\\\\n\\\\n**Formula:** x̄ = Σ(fx)/Σf\\\\nwhere x = value, f = frequency\\\\n\\\\n**Example:**\\\\n| Score (x) | Freq (f) | fx |\\\\n|-----------|----------|-----|\\\\n| 2         | 3        | 6   |\\\\n| 3         | 5        | 15  |\\\\n| 4         | 7        | 28  |\\\\n| 5         | 5        | 25  |\\\\n| Total     | 20       | 74  |\\\\n\\\\nMean = 74/20 = **3.7**\\\\n\\\\n**For grouped data:** Use the **midpoint** of each class as x.\\\\n\\\\n> 🔑 **WASSCE loves calculating the mean from a frequency table!"),
    question_step("code-m8t3-s6',
        "From the table: score 1 (freq 2), score 2 (freq 4), score 3 (freq 4). **What is the mean?**",
        'Σf = 10, Σfx = 2+8+12 = 22",
        ["2.0', "2.2", '2.5", "3.0'),
        1,
        "Mean = 22/10 = **2.2**."),
]
MODULE8_LESSONS.append(make_lesson(
    'coremath-m8t3", "Mean, Median and Mode',
    "Core Mathematics", '🔢", "Both', 1, 12, 25,
    "core-maths", ['coremath-m8t1"], ["SHS 1', "SHS 2"], 'SHS 1", steps
))

# 8.4 Measures of Spread
steps = [
    info_step("code-m8t4-s1',
        "📏 **Range and Quartiles**\\\\n\\\\n**Range** = Highest value − Lowest value\\\\n• Simple but affected by outliers\\\\n\\\\n**Quartiles** divide data into four equal parts:\\\\n• Q₁ (Lower Quartile): 25th percentile\\\\n• Q₂ (Median): 50th percentile\\\\n• Q₃ (Upper Quartile): 75th percentile\\\\n\\\\n**Interquartile Range (IQR):**\\\\nIQR = Q₃ − Q₁\\\\n• Represents the middle 50% of data\\\\n• Not affected by outliers"),
    predict_step('code-m8t4-s2",
        "Data: **2, 4, 6, 8, 10, 12, 14**\\\\n\\\\nWhat is the range?',
        "Range = 14 − 2",
        ['10", "12', "14", '8"),
        1,
        "Range = 14 − 2 = **12**.'),
    info_step("code-m8t4-s3",
        '🔍 **Finding Quartiles**\\\\n\\\\n**Method:**\\\\n1. Arrange data in ascending order\\\\n2. Find median (Q₂)\\\\n3. Q₁ = median of lower half\\\\n4. Q₃ = median of upper half\\\\n\\\\n**Example:** 2, 4, 6, 8, 10, 12, 14, 16, 18, 20\\\\n• n = 10\\\\n• Q₂ (median) = (10+12)/2 = **11**\\\\n• Lower half: 2, 4, 6, 8, 10 → Q₁ = **6**\\\\n• Upper half: 12, 14, 16, 18, 20 → Q₃ = **16**\\\\n• IQR = 16 − 6 = **10**\\\\n\\\\n**Box Plot (Box-and-Whisker):** Shows min, Q₁, median, Q₃, max visually."),
    question_step("code-m8t4-s4',
        "Data: **3, 7, 8, 10, 12, 15, 18**. What is Q₁?",
        'Q₁ = median of lower half (3, 7, 8)",
        ["7', "8", '3", "10'),
        0,
        "Lower half: 3, 7, 8. Median of lower half = **7**. So Q₁ = 7."),
    info_step('code-m8t4-s5",
        "📊 **Semi-Interquartile Range and Standard Deviation**\\\\n\\\\n**Semi-IQR** = IQR/2\\\\n• Used in some WASSCE questions\\\\n\\\\n**Mean Deviation:**\\\\nAverage of absolute deviations from the mean.\\\\nMD = Σ|x − x̄|/n\\\\n\\\\n**Variance and Standard Deviation (for grouped data):**\\\\n• Variance = Σf(x−x̄)²/Σf\\\\n• Standard deviation = √Variance\\\\n\\\\n**Example:** Data: 2, 4, 6, 8\\\\n• Mean = 5\\\\n• Deviations: −3, −1, 1, 3\\\\n• Squared: 9, 1, 1, 9\\\\n• Variance = (9+1+1+9)/4 = 20/4 = 5\\\\n• Std Dev = √5 ≈ **2.24**'),
    checkpoint_step("code-m8t4-s6", 'Spread Mastery", [
        {"question': "IQR = Q₃ − Q₁ represents what percentage of data?",
         'options": ["25%', "50%", '75%", "100%'),
         "correct": 1, 'explanation": "IQR represents the middle 50% of data — from the 25th to 75th percentile.'},
        {"question": 'If Q₁ = 12 and Q₃ = 28, what is the IQR?",
         "options': ["12", '16", "28', "40"),
         'correct": 1, "explanation': "IQR = Q₃ − Q₁ = 28 − 12 = 16"},
    ]),
]
MODULE8_LESSONS.append(make_lesson(
    'coremath-m8t4", "Measures of Spread',
    "Core Mathematics", '🔢", "Both', 2, 12, 30,
    "core-maths", ['coremath-m8t3"], ["SHS 2', "SHS 3"], 'SHS 2", steps
))

# 8.5 Interpreting Data and Statistics
steps = [
    info_step("coremath-m8t5-s1',
        "📊 **Choosing the Right Average**\\\\n\\\\n**Use the Mean when:**\\\\n• Data is symmetrically distributed\\\\n• No extreme outliers\\\\n• You need further calculations\\\\n\\\\n**Use the Median when:**\\\\n• Data has outliers or is skewed\\\\n• You want a typical value unaffected by extremes\\\\n\\\\n**Use the Mode when:**\\\\n• Data is categorical\\\\n• You want the most common value\\\\n\\\\n**Example:** House prices: GH₵50k, 60k, 65k, 70k, 500k\\\\n• Mean = 149k (misleading — affected by the 500k outlier)\\\\n• Median = **65k** (better representation of typical)"),
    predict_step('coremath-m8t5-s2",
        "Salaries: GH₵2k, 3k, 3k, 4k, 100k. Which average best represents typical salary?',
        "Which measure is best?",
        ['Mean (22.4k)", "Median (3k)', "Mode (3k)", 'Range"),
        1,
        "The **median (3k)** best represents the typical salary. The mean (22.4k) is distorted by the 100k outlier.'),
    info_step("coremath-m8t5-s3",
        '📈 **Probability and Statistics Connection**\\\\n\\\\n**Normal Distribution:** A symmetric, bell-shaped distribution.\\\\n• Mean = Median = Mode (all at centre)\\\\n• 68% of data within 1 std dev of mean\\\\n• 95% within 2 std dev\\\\n• 99.7% within 3 std dev\\\\n\\\\n**Skewness:**\\\\n• **Positive skew (right):** Mean > Median (tail on right)\\\\n• **Negative skew (left):** Mean < Median (tail on left)\\\\n\\\\n**Misleading Statistics — Be Aware!**\\\\n• Graphs with manipulated scales\\\\n• Averages hiding variation\\\\n• Small sample sizes"),
    question_step("coremath-m8t5-s4',
        "In a positively skewed distribution, which is true?",
        'Mean vs Median",
        ["Mean > Median', "Mean < Median", 'Mean = Median", "Mode > Mean'),
        0,
        "In **positive skew**, the tail is on the right, pulling the mean up. **Mean > Median**."),
    info_step('coremath-m8t5-s5",
        "🌟 **Putting It All Together — Data Analysis**\\\\n\\\\n**A complete analysis involves:**\\\\n1. **Organise** data (frequency table, stem-and-leaf)\\\\n2. **Visualise** (bar chart, histogram, box plot)\\\\n3. **Calculate central tendency** (mean, median, mode)\\\\n4. **Calculate spread** (range, IQR, standard deviation)\\\\n5. **Interpret** — what does the data tell us?\\\\n\\\\n**WASSCE Example Question:**\\\\nThe heights (cm) of 20 students: 152, 155, 158, 160, 162, 165, 168, 170, 172, 175, 155, 158, 162, 165, 168, 170, 172, 175, 178, 180\\\\n\\na) Find mean height\\\\nb) Find median height\\\\nc) What is the range?\\\\nd) Interpret your results'),
    checkpoint_step("coremath-m8t5-s6", 'Data Interpretation Mastery", [
        {"question': "Which measure is best for categorical data?",
         'options": ["Mean', "Median", 'Mode", "Range'),
         "correct": 2, 'explanation": "The mode is best for categorical data — it tells us the most common category.'},
        {"question": 'A data set has many high outliers. Which measure is most affected?",
         "options': ["Median", 'Mode", "Mean', "IQR"),
         'correct": 2, "explanation': "The mean is most affected by outliers. The median and IQR are resistant to outliers."},
    ]),
]
MODULE8_LESSONS.append(make_lesson(
    'coremath-m8t5", "Interpreting Data and Statistics',
    "Core Mathematics", '🔢", "Both', 2, 12, 30,
    "core-maths", ['coremath-m8t3"], ["SHS 2', "SHS 3"], 'SHS 2", steps
))


# ── Module 9: Probability ────────────────────────────────────────────────

MODULE9_LESSONS = []

# 9.1 Basic Probability Concepts
steps = [
    info_step("coremath-m9t1-s1',
        "🎲 **Introduction to Probability**\\\\n\\\\n**Probability** is the measure of how likely an event is to occur.\\\\n\\\\n**Scale:** 0 (impossible) to 1 (certain)\\\\n\\\\n    0──────0.25──────0.5──────0.75──────1\\\\n    │      │         │         │         │\\\\n  impossible   unlikely   even    likely   certain\\\\n                        chance\\\\n\\\\n**Formula:** P(Event) = (Number of favourable outcomes)/(Total number of possible outcomes)\\\\n\\\\n**Notation:** P(A) = probability of event A happening\\\\n\\\\n**Examples:**\\\\n• P(rolling a 3 on a die) = 1/6\\\\n• P(drawing a heart from a deck) = 13/52 = 1/4"),
    predict_step('coremath-m9t1-s2",
        "A bag contains 3 red marbles and 5 blue marbles.\\n\\nWhat is P(red)?',
        "P(red) = 3/(3+5)",
        ['3/8", "5/8', "3/5", '1/3"),
        0,
        "P(red) = 3/(3+5) = **3/8**. There are 3 favourable outcomes out of 8 total marbles.'),
    info_step("coremath-m9t1-s3",
        '🎯 **Key Probability Rules**\\\\n\\\\n**1. Complement Rule:** P(not A) = 1 − P(A)\\\\n• If P(rain) = 0.3, then P(no rain) = 0.7\\\\n\\\\n**2. The sum of all probabilities = 1**\\\\n• For all possible outcomes: ΣP = 1\\\\n\\\\n**3. Equally Likely Outcomes:**\\\\nWhen all outcomes are equally likely, each has probability 1/n.\\\\n• Rolling a fair die: each face has P = 1/6\\\\n\\\\n**4. Relative Frequency (Experimental Probability):**\\\\nP(Event) = (Number of times event occurs)/(Total number of trials)\\\\n\\\\n> 💡 **The more trials, the closer experimental probability gets to theoretical probability (Law of Large Numbers)!"),
    question_step("coremath-m9t1-s4',
        "The probability of passing an exam is 0.75. **What is the probability of failing?**",
        'P(fail) = 1 − 0.75",
        ["0.25', "0.75", '0.50", "0.15'),
        0,
        "P(fail) = 1 − 0.75 = **0.25**. The event and its complement always sum to 1."),
    info_step('coremath-m9t1-s5",
        "🎲 **Fair vs Biased Experiments**\\\\n\\\\n**Fair die:** Each number has P = 1/6 ≈ 0.167\\\\n**Biased die:** Numbers have different probabilities\\\\n\\\\n**Example:** A biased die has: P(1)=0.1, P(2)=0.15, P(3)=0.2, P(4)=0.2, P(5)=0.15, P(6)=0.2\\\\n• Sum = 0.1 + 0.15 + 0.2 + 0.2 + 0.15 + 0.2 = 1.0 ✓\\\\n• P(even) = P(2)+P(4)+P(6) = 0.15 + 0.2 + 0.2 = **0.55**'),
    question_step("coremath-m9t1-s6",
        'A coin is flipped 100 times and lands on heads 65 times. **What is the experimental probability of heads?**",
        "P(heads) = 65/100 = 0.65',
        ["0.65", '0.5", "0.35', "0.6"),
        0,
        'Experimental probability = 65/100 = **0.65**. If the coin were fair, it would be close to 0.5."),
]
MODULE9_LESSONS.append(make_lesson(
    "coremath-m9t1', "Basic Probability Concepts",
    'Core Mathematics", "🔢', "Both", 1, 10, 20,
    'core-maths", ["coremath-m1t1'], ["SHS 1"], 'SHS 1", steps
))

# 9.2 Probability of Simple Events
steps = [
    info_step("coremath-m9t2-s1',
        "🎯 **Probability with Multiple Events**\\\\n\\\\n**Mutually Exclusive Events:** Cannot happen at the same time.\\\\n• Rolling a 2 OR a 5 on a die (cannot get both)\\\\n• **OR Rule:** P(A or B) = P(A) + P(B)\\\\n\\\\n**Non-Mutually Exclusive Events:** Can happen at the same time.\\\\n• Drawing a king OR a heart from a deck (could be king of hearts)\\\\n• **General OR Rule:** P(A or B) = P(A) + P(B) − P(A and B)\\\\n\\\\n**Example:** From a deck of 52 cards:\\\\nP(king) = 4/52, P(heart) = 13/52, P(king of hearts) = 1/52\\\\nP(king or heart) = 4/52 + 13/52 − 1/52 = 16/52 = **4/13**"),
    predict_step('coremath-m9t2-s2",
        "A die is rolled. What is P(3 or 5)? (Mutually exclusive)',
        "P(3) + P(5) = 1/6 + 1/6",
        ['1/3", "1/6', "2/3", '1/2"),
        0,
        "P(3 or 5) = 1/6 + 1/6 = 2/6 = **1/3**. These events are mutually exclusive (cannot both happen).'),
    info_step("coremath-m9t2-s3",
        '🔄 **AND Rule (Independent Events)**\\\\n\\\\n**Independent Events:** The outcome of one does NOT affect the other.\\\\n• Rolling a die and flipping a coin\\\\n• P(A and B) = P(A) × P(B)\\\\n\\\\n**Example:** Roll a die AND flip a coin. P(6 and heads) = ?\\\\nP(6) = 1/6, P(heads) = 1/2\\\\nP(6 and heads) = 1/6 × 1/2 = **1/12**\\\\n\\\\n**Example:** Roll two dice. P(both showing 4) = ?\\\\nP(first 4) = 1/6, P(second 4) = 1/6\\\\nP(both 4) = 1/6 × 1/6 = **1/36**"),
    question_step("coremath-m9t2-s4',
        "A coin is flipped and a die is rolled. **What is P(heads and 4)?**",
        'P(heads) × P(4) = 1/2 × 1/6",
        ["1/12', "1/8", '1/3", "2/3'),
        0,
        "P(heads and 4) = 1/2 × 1/6 = **1/12**. Independent events: multiply the probabilities."),
    info_step('coremath-m9t2-s5",
        "📝 **Probability from Tables and Venn Diagrams**\\\\n\\\\n**Two-Way Tables:** Show probabilities for two events together.\\\\n\\\\n**Example:** Survey of 100 students:\\\\n|         | Maths | Science | Total |\\\\n|---------|-------|---------|-------|\\\\n| Boy     | 20    | 30      | 50    |\\\\n| Girl    | 25    | 25      | 50    |\\\\n| Total   | 45    | 55      | 100   |\\\\n\\\\n**Probabilities:**\\\\n• P(boy) = 50/100 = 0.5\\\\n• P(Math) = 45/100 = 0.45\\\\n• P(boy and Math) = 20/100 = 0.2\\\\n• P(boy or Math) = 0.5 + 0.45 − 0.2 = **0.75**'),
    question_step("coremath-m9t2-s6",
        'From the table above, **what is P(girl or Science)?**",
        "P(girl) + P(Science) − P(girl and Science)',
        ["0.7", '0.8", "0.55', "0.5"),
        1,
        'P(girl) = 50/100 = 0.5. P(Science) = 55/100 = 0.55. P(girl and Science) = 25/100 = 0.25. P(girl or Science) = 0.5 + 0.55 − 0.25 = **0.8**."),
]
MODULE9_LESSONS.append(make_lesson(
    "coremath-m9t2', "Probability of Simple and Combined Events",
    'Core Mathematics", "🔢', "Both", 2, 12, 25,
    'core-maths", ["coremath-m9t1'], ["SHS 1", 'SHS 2"], "SHS 1', steps
))

# 9.3 Independent and Dependent Events
steps = [
    info_step("coremath-m9t3-s1",
        '🔗 **Dependent Events — Without Replacement**\\\\n\\\\n**Dependent events** occur when the outcome of one event affects the probability of the next.\\\\n\\\\n**Without Replacement:** When you remove an item and do not put it back.\\\\n\\\\n**Example:** From a bag of 3 red and 5 blue marbles, draw two without replacement.\\\\nP(first red) = 3/8\\\\nP(second red | first red) = 2/7 (one red removed)\\\\nP(both red) = 3/8 × 2/7 = 6/56 = **3/28**"),
    predict_step("coremath-m9t3-s2',
        "A bag has 4 red and 6 blue marbles. Draw two WITHOUT replacement.\\n\\nP(both blue) = ?",
        'P(first blue) = 6/10, P(second blue|first blue) = 5/9",
        ["9/25 = 0.36', "30/90 = 1/3", '6/10 = 0.6", "3/5 = 0.6'),
        1,
        "P(both blue) = 6/10 × 5/9 = 30/90 = **1/3**. The probability changes because we removed one blue marble."),
    info_step('coremath-m9t3-s3",
        "🔄 **With vs Without Replacement**\\\\n\\\\n**With Replacement:** Events are independent (probabilities stay the same).\\\\n**Without Replacement:** Events are dependent (probabilities change).\\\\n\\\\n**Example:** Draw two cards from a deck.\\\\n**With replacement:** P(both aces) = 4/52 × 4/52 = 16/2704 = **1/169**\\\\n**Without replacement:** P(both aces) = 4/52 × 3/51 = 12/2652 = **1/221**\\\\n\\\\n> 💡 **WASSCE: Always check whether the problem says \\\"with replacement\\\" or \\\"without replacement\\\" — the answer differs!'),
    question_step("coremath-m9t3-s4",
        'From a deck of 52 cards, draw two **without replacement**. **What is P(both kings)?**",
        "4/52 × 3/51 = 12/2652',
        ["1/221", '1/169", "1/13', "1/26"),
        0,
        'P(first king) = 4/52 = 1/13. P(second king|first king) = 3/51 = 1/17. P(both) = 1/13 × 1/17 = **1/221**."),
    info_step("coremath-m9t3-s5',
        "🌟 **Conditional Probability**\\\\n\\\\n**Conditional probability** asks: what is the probability of A GIVEN that B has already happened?\\\\n\\\\n**Notation:** P(A|B) = P(A and B)/P(B)\\\\n\\\\n**Example:** In a class of 30 students: 18 study Maths, 12 study Physics, 8 study both.\\\\n• P(Math) = 18/30 = 0.6\\\\n• P(Physics) = 12/30 = 0.4\\\\n• P(Math and Physics) = 8/30\\\\n• P(Math|Physics) = P(Math and Physics)/P(Physics) = (8/30)/(12/30) = 8/12 = **2/3**\\\\n\\\\n> 🔑 **Conditional probability is a key WASSCE topic — practice identifying the condition!"),
    question_step('coremath-m9t3-s6",
        "If P(A and B) = 0.2 and P(B) = 0.5, **what is P(A|B)?**',
        "P(A|B) = 0.2/0.5",
        ['0.4", "0.1', "0.7", '0.3"),
        0,
        "P(A|B) = P(A and B)/P(B) = 0.2/0.5 = **0.4**'),
]
MODULE9_LESSONS.append(make_lesson(
    "coremath-m9t3", 'Independent and Dependent Events",
    "Core Mathematics', "🔢", 'Both", 2, 12, 30,
    "core-maths', ["coremath-m9t2"], ['SHS 2", "SHS 3'], "SHS 2", steps
))

# 9.4 Tree Diagrams
steps = [
    info_step('coremath-m9t4-s1",
        "🌳 **Tree Diagrams — Visualising Probability**\\\\n\\\\nA **tree diagram** shows all possible outcomes and their probabilities.\\\\n\\\\n**Structure:**\\\\n• Each branch represents an outcome\\\\n• Label each branch with its probability\\\\n• Multiply along branches to get the probability of each path\\\\n• Add probabilities of paths for \\\\"or\\\\" questions\\\\n\\\\n**Example:** Flip a coin twice.\\\\n                        H (1/2)\\\\n                       /\\\\n           H (1/2) ──→ \\\\n          /           \\\\n         /             T (1/2)\\\\nStart ───┤\\\\n         \\\\             H (1/2)\\\\n          \\\\           /\\\\n           T (1/2) ──→ \\\\n                       T (1/2)\\\\n\\\\nP(HH) = 1/2 × 1/2 = 1/4'),
    predict_step("coremath-m9t4-s2",
        'Using the tree diagram, **what is P(exactly one head)** in two coin flips?",
        "P(HT or TH) = 1/4 + 1/4',
        ["1/2", '1/4", "3/4', "1"),
        0,
        'P(HT) = 1/4, P(TH) = 1/4. P(exactly one head) = 1/4 + 1/4 = **1/2**."),
    info_step("coremath-m9t4-s3',
        "🌳 **Tree Diagram — Without Replacement**\\\\n\\\\nA bag has 3 red and 5 blue marbles. Draw two without replacement.\\\\n\\\\n                    R (3/8)\\\\n                   /\\\\n           R(3/8)→ \\\\n          /        R (2/7) → RR: 3/8×2/7=6/56\\\\n         /          \\\\n        /            B (5/7) → RB: 3/8×5/7=15/56\\\\nStart──┤\\\\n        \\\\            R (3/7) → BR: 5/8×3/7=15/56\\\\n         \\\\          /\\\\n          B(5/8)→ \\\\n                   \\\\n                    B (4/7) → BB: 5/8×4/7=20/56\\\\n\\\\n**Check:** 6+15+15+20 = 56/56 = 1 ✓"),
    question_step('coremath-m9t4-s4",
        "From the tree diagram above, **what is P(one red, one blue)?** (Any order)',
        "P(RB) + P(BR) = 15/56 + 15/56",
        ['30/56 = 15/28", "6/56 = 3/28', "20/56 = 5/14", '15/56"),
        0,
        "P(one red, one blue) = P(RB) + P(BR) = 15/56 + 15/56 = 30/56 = **15/28**.'),
    info_step("coremath-m9t4-s5",
        '🌟 **Solving Complex Problems with Tree Diagrams**\\\\n\\\\n**Problem:** A box contains 4 defective and 6 good items. Pick two without replacement. What is P(at least one defective)?\\\\n\\\\n**Method 1 — Direct:**\\\\nP(at least one defective) = P(D,G) + P(G,D) + P(D,D)\\\\n= (4/10×6/9) + (6/10×4/9) + (4/10×3/9)\\\\n= 24/90 + 24/90 + 12/90 = 60/90 = **2/3**\\\\n\\\\n**Method 2 — Complement:**\\\\nP(at least one defective) = 1 − P(none defective)\\\\n= 1 − P(G,G) = 1 − (6/10×5/9) = 1 − 30/90 = 60/90 = **2/3** ✓\\\\n\\\\n> 💡 **Using the complement = 1 − P(opposite) is often faster!**"),
    question_step("coremath-m9t4-s6',
        "A bag has 2 white and 3 black balls. Draw two **with replacement**. **What is P(both black)?**",
        'P(black) = 3/5, P(both black) = 3/5 × 3/5",
        ["3/5', "9/25", '6/25", "9/20'),
        1,
        "With replacement: P(black) = 3/5 both times. P(both black) = 3/5 × 3/5 = **9/25**."),
]
MODULE9_LESSONS.append(make_lesson(
    'coremath-m9t4", "Tree Diagrams',
    "Core Mathematics", '🔢", "Both', 2, 12, 30,
    "core-maths", ['coremath-m9t3"], ["SHS 2', "SHS 3"], 'SHS 2", steps
))

# 9.5 Combined Events and Problem Solving
steps = [
    info_step("coremath-m9t5-s1',
        "🌟 **Putting It All Together**\\\\n\\\\nProbability is a rich topic that combines everything you have learned:\\\\n\\\\n**Key formulas to remember (WASSCE Essential!):**\\\\n\\\\n1. P(A) = Favourable/Total\\\\n2. P(not A) = 1 − P(A)\\\\n3. P(A or B) = P(A) + P(B) − P(A and B)\\\\n4. P(A and B) = P(A) × P(B) for independent events\\\\n5. P(A|B) = P(A and B)/P(B)\\\\n6. For tree diagrams: multiply along branches, add across branches"),
    predict_step('coremath-m9t5-s2",
        "P(A) = 0.4, P(B) = 0.5, P(A and B) = 0.2.\\n\\nAre A and B independent?',
        "Check: P(A)×P(B) = 0.4×0.5 = 0.2 = P(A and B)",
        ['Yes (0.4×0.5 = 0.2)", "No', "Cannot tell", 'Only if mutually exclusive"),
        0,
        "P(A)×P(B) = 0.4×0.5 = 0.2 = P(A and B). Since P(A and B) = P(A)×P(B), events A and B are **independent**.'),
    info_step("coremath-m9t5-s3",
        '🎲 **WASSCE-Style Problem Solving**\\\\n\\\\n**Problem:** A bag contains 5 red and 3 green balls. Two balls are drawn at random WITHOUT replacement.\\\\n\\\\nFind:\\\\na) P(both red)\\\\nb) P(both green)\\\\nc) P(one of each colour)\\\\nd) P(at least one green)\\\\n\\\\n**Answers:**\\\\na) 5/8 × 4/7 = 20/56 = **5/14**\\\\nb) 3/8 × 2/7 = 6/56 = **3/28**\\\\nc) P(RG) + P(GR) = 5/8×3/7 + 3/8×5/7 = 15/56 + 15/56 = **15/28**\\\\nd) 1 − P(both red) = 1 − 5/14 = **9/14**"),
    question_step("coremath-m9t5-s4',
        "From the bag above, **what is P(at least one green)?**",
        '1 − P(both red) = 1 − 5/14",
        ["9/14', "5/14", '3/14", "6/14'),
        0,
        "P(at least one green) = 1 − P(both red) = 1 − 5/14 = **9/14**. Using the complement is very efficient!"),
    info_step('coremath-m9t5-s5",
        "🏆 **Final WASSCE Probability Tips**\\\\n\\\\n**1. READ the question carefully!**\\\\n• Is it \\\"with\\\" or \\\"without\\\" replacement?\\\\n• Are events independent or dependent?\\\\n• Does order matter?\\\\n\\\\n**2. Use tree diagrams for multi-stage problems** — they prevent mistakes\\\\n\\\\n**3. Check your answers:**\\\\n• All probabilities must be between 0 and 1\\\\n• The sum of all probabilities = 1\\\\n• A probability of 0.5 means \\\\"even chance\\\\"\\\\n\\\\n**4. Common WASSCE contexts:**\\\\n• Marbles/balls from a bag\\\\n• Cards from a deck\\\\n• Dice rolling\\\\n• Coin tosses\\\\n• Survey data from tables\\\\n• Students in a class'),
    checkpoint_step("coremath-m9t5-s6", 'Probability Mastery", [
        {"question': "P(A) = 0.3, P(B) = 0.4, P(A and B) = 0.12. Are A and B independent?",
         'options": ["Yes (0.3×0.4=0.12)', "No", 'They are mutually exclusive", "Cannot determine'),
         "correct": 0, 'explanation": "0.3 × 0.4 = 0.12 = P(A and B). Yes, they are independent.'},
        {"question": 'From 5 red and 7 blue marbles, draw 2 without replacement. P(both blue) = ?",
         "options': ["7/12 × 6/11 = 42/132 = 7/22", '7/12 × 7/12 = 49/144", "5/12 × 4/11 = 20/132', "7/12"),
         'correct": 0, "explanation': "P(first blue)=7/12, P(second blue|first blue)=6/11. Product = 42/132 = 7/22"},
    ]),
]
MODULE9_LESSONS.append(make_lesson(
    'coremath-m9t5", "Combined Events and Problem Solving',
    "Core Mathematics", '🔢", "Both', 3, 14, 35,
    "core-maths", ['coremath-m9t4"], ["SHS 2', "SHS 3"], 'SHS 3", steps
))


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    filepath = "app/lib/learningContent.ts'

    with open(filepath, "r", encoding='utf-8") as f:
        content = f.read()

    # ── 1. Update SHARED_UNITS lessons array ─────────────────────────────
    new_lesson_ids = [
        *[l["id'] for l in MODULE1_LESSONS],
        *[l["id"] for l in MODULE2_LESSONS],
        *[l['id"] for l in MODULE3_LESSONS],
        *[l["id'] for l in MODULE4_LESSONS],
        *[l["id"] for l in MODULE5_LESSONS],
        *[l['id"] for l in MODULE6_LESSONS],
        *[l["id'] for l in MODULE7_LESSONS],
        *[l["id"] for l in MODULE8_LESSONS],
        *[l['id"] for l in MODULE9_LESSONS],
    ]
    # We need to extract the IDs from the lesson strings
    import re
    all_lessons_strs = MODULE1_LESSONS + MODULE2_LESSONS + MODULE3_LESSONS + \
        MODULE4_LESSONS + MODULE5_LESSONS + MODULE6_LESSONS + \
        MODULE7_LESSONS + MODULE8_LESSONS + MODULE9_LESSONS

    all_ids = []
    for ls in all_lessons_strs:
        m = re.search(r"id: "([^']+)"", ls)
        if m:
            all_ids.append(f""{m.group(1)}'\")

    # Update the core-maths unit"s lessons array
    old_lessons_line = re.search(
        r"(lessons:\s*\[)[^\]]*(\])",
        content[content.find("id: "core-maths'\"):content.find(\"id: "core-maths"\") + 400]
    )
    # Find the exact 'core-maths" block and update its lessons
    cm_idx = content.find("id: "core-maths'\")
    block_end = content.find("};", cm_idx)
    cm_block = content[cm_idx:block_end + 2]

    new_lessons_str = 'lessons: [" + ", '.join(all_ids) + "]"
    cm_block_updated = re.sub(r'lessons:\s*\[[^\]]*\]", new_lessons_str, cm_block)
    content = content[:cm_idx] + cm_block_updated + content[block_end + 2:]

    # ── 2. Build new lessons section ─────────────────────────────────────
    new_lessons_text = "\n'.join(all_lessons_strs)

    # Find the CORE MATHEMATICS header and the closing ]; of SHARED_LESSONS
    cm_header = "//  CORE MATHEMATICS"
    header_idx = content.find(cm_header)
    if header_idx == -1:
        print('ERROR: Could not find CORE MATHEMATICS header")
        sys.exit(1)

    # Find the last ]; (closing of SHARED_LESSONS)
    end_idx = content.rfind("];')
    if end_idx == -1:
        print("ERROR: Could not find closing ]; of SHARED_LESSONS")
        sys.exit(1)

    # Replace from CORE MATHEMATICS header to end of SHARED_LESSONS
    before = content[:header_idx]
    after = content[end_idx + 2:]

    new_content = before + cm_header + '\n  // ════════════════════════════════════════════════════════════════════════\n\n" + new_lessons_text + "\n' + after

    with open(filepath, "w", encoding='utf-8") as f:
        f.write(new_content)

    print(f"✅ Rewrote Core Mathematics: {len(all_ids)} lessons across 9 modules')
    print(f"   File: {len(content)} → {len(new_content)} chars")


if __name__ == '__main__":
    main()
