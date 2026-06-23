#!/usr/bin/env python
"""Generate ALL 9 Core Maths modules (45 topics) and write to learningContent.ts"""

import os, sys

# ── String helpers ──────────────────────────────────────────────────────
def js_str(s: str) -> str:
    """Escape for TypeScript (single quotes, newlines as \n)."""
    escaped = (s
        .replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("\n", "\\n")
    )
    return "'" + escaped + "'"

def format_steps(steps: list) -> str:
    parts = []
    for s in steps:
        t = s["type"]
        sid = s["id"]
        ind = "      "
        if t == "info":
            parts.append(
                f"{ind}{{\n"
                f"{ind}  id: {js_str(sid)},\n"
                f"{ind}  type: 'info',\n"
                f"{ind}  content:\n"
                f"{ind}    {js_str(s['content'])},\n"
                f"{ind}}},"
            )
        elif t == "predict":
            p = s["predict"]
            opts = ", ".join(js_str(o) for o in p["options"])
            parts.append(
                f"{ind}{{\n"
                f"{ind}  id: {js_str(sid)},\n"
                f"{ind}  type: 'predict',\n"
                f"{ind}  content:\n"
                f"{ind}    {js_str(s['content'])},\n"
                f"{ind}  predict: {{\n"
                f"{ind}    pattern: {js_str(p['pattern'])},\n"
                f"{ind}    question: {js_str(p['question'])},\n"
                f"{ind}    options: [{opts}],\n"
                f"{ind}    correctIndex: {p['correctIndex']},\n"
                f"{ind}    explanation: {js_str(p['explanation'])},\n"
                f"{ind}  }},\n"
                f"{ind}}},"
            )
        elif t == "question":
            e = s["exercise"]
            opts = ", ".join(js_str(o) for o in e["options"])
            parts.append(
                f"{ind}{{\n"
                f"{ind}  id: {js_str(sid)},\n"
                f"{ind}  type: 'question',\n"
                f"{ind}  content:\n"
                f"{ind}    {js_str(s['content'])},\n"
                f"{ind}  exercise: {{\n"
                f"{ind}    question: {js_str(e['question'])},\n"
                f"{ind}    options: [{opts}],\n"
                f"{ind}    correctIndex: {e['correctIndex']},\n"
                f"{ind}    explanation: {js_str(e['explanation'])},\n"
                f"{ind}  }},\n"
                f"{ind}}},"
            )
        elif t == "checkpoint":
            qs = []
            for q in s["checkpoint"]["questions"]:
                opts = ", ".join(js_str(o) for o in q["options"])
                qs.append(
                    f"          {{\n"
                    f"            question: {js_str(q['question'])},\n"
                    f"            options: [{opts}],\n"
                    f"            correctIndex: {q['correctIndex']},\n"
                    f"            explanation: {js_str(q['explanation'])},\n"
                    f"          }}"
                )
            qs_block = ",\n".join(qs)
            parts.append(
                f"{ind}{{\n"
                f"{ind}  id: {js_str(sid)},\n"
                f"{ind}  type: 'checkpoint',\n"
                f"{ind}  content:\n"
                f"{ind}    {js_str(s['content'])},\n"
                f"{ind}  checkpoint: {{\n"
                f"{ind}    title: {js_str(s['checkpoint']['title'])},\n"
                f"{ind}    questions: [\n"
                f"{qs_block}\n"
                f"{ind}    ],\n"
                f"{ind}    passThreshold: {s['checkpoint']['passThreshold']},\n"
                f"{ind}    bonusXp: {s['checkpoint']['bonusXp']},\n"
                f"{ind}  }},\n"
                f"{ind}}},"
            )
    return "\n".join(parts)

def make_lesson(l: dict) -> str:
    prereqs = ", ".join(js_str(p) for p in l["prerequisites"])
    levels = ", ".join(js_str(ls) for ls in l["shsLevels"])
    steps_str = format_steps(l["steps"])
    return (
        f"  {{\n"
        f"    id: {js_str(l['id'])},\n"
        f"    title: {js_str(l['title'])},\n"
        f"    subject: {js_str(l['subject'])},\n"
        f"    subjectIcon: {js_str(l['subjectIcon'])},\n"
        f"    programme: {js_str(l['programme'])},\n"
        f"    difficulty: {l['difficulty']},\n"
        f"    estimatedMinutes: {l['estimatedMinutes']},\n"
        f"    xpReward: {l['xpReward']},\n"
        f"    unitId: {js_str(l['unitId'])},\n"
        f"    prerequisites: [{prereqs}],\n"
        f"    shsLevels: [{levels}],\n"
        f"    suggestedLevel: {js_str(l['suggestedLevel'])},\n"
        f"    steps: [\n"
        f"{steps_str}\n"
        f"    ],\n"
        f"  }},"
    )

# ── Step helpers ──────────────────────────────────────────────────────
def i(sid, content):
    return {"id": sid, "type": "info", "content": content}

def p(sid, content, pattern, question, options, correct, explanation):
    return {"id": sid, "type": "predict", "content": content,
            "predict": {"pattern": pattern, "question": question,
                        "options": options, "correctIndex": correct,
                        "explanation": explanation}}

def q(sid, content, question, options, correct, explanation):
    return {"id": sid, "type": "question", "content": content,
            "exercise": {"question": question, "options": options,
                         "correctIndex": correct, "explanation": explanation}}

def c(sid, title, questions):
    return {"id": sid, "type": "checkpoint",
            "content": f"Mastery Check: {title}\n\nTime to test your understanding! Complete all questions to pass.",
            "checkpoint": {"title": title, "questions": questions,
                           "passThreshold": len(questions) - 1, "bonusXp": 15}}

def L(lesson_id, title, subject, icon, programme, difficulty, minutes, xp,
       unit_id, prerequisites, shs_levels, suggested_level, steps):
    return {"id": lesson_id, "title": title, "subject": subject,
            "subjectIcon": icon, "programme": programme,
            "difficulty": difficulty, "estimatedMinutes": minutes,
            "xpReward": xp, "unitId": unit_id,
            "prerequisites": prerequisites,
            "shsLevels": shs_levels, "suggestedLevel": suggested_level,
            "steps": steps}

# ═══════════════════════════════════════════════════════════════════════
#  MODULE 1: Number Sets (5 Topics)
# ═══════════════════════════════════════════════════════════════════════
MODULE1 = [
    L("coremath-m1t1", "Natural Numbers, Integers and Prime Numbers",
      "Core Mathematics", "1d522", "Both", 1, 8, 20, "core-maths", [], ["SHS 1"], "SHS 1", [
        i("coremath-m1t1-s1",
          "Natural Numbers and Integers\n\nNatural Numbers (N): The numbers we use for counting - 1, 2, 3, 4, ...\n\nIntegers (Z): All whole numbers, including negatives - ..., -3, -2, -1, 0, 1, 2, 3, ...\n\nKey Properties:\nClosure: The sum/product of two naturals is always a natural.\nCommutative: a + b = b + a\nAssociative: (a + b) + c = a + (b + c)\nDistributive: a x (b + c) = a x b + a x c\n\nWASSCE Tip: Know the difference between natural numbers, integers, and whole numbers - they are not the same!"),
        p("coremath-m1t1-s2", "Look at this sequence: 2, 4, 6, 8, 10, ... What type of numbers are these?",
          "2, 4, 6, 8, 10, ...", "What do we call this pattern?",
          ["Odd numbers", "Even natural numbers", "Prime numbers", "Square numbers"], 1,
          "These are even natural numbers - they are all natural numbers divisible by 2."),
        i("coremath-m1t1-s3",
          "Prime Numbers and Composite Numbers\n\nPrime Numbers: Natural numbers greater than 1 that have exactly two factors: 1 and itself.\n2, 3, 5, 7, 11, 13, 17, 19, 23, 29, ...\n2 is the only even prime number!\n\nComposite Numbers: Natural numbers greater than 1 that have more than two factors.\n4, 6, 8, 9, 10, 12, ...\n\nNote: 1 is neither prime nor composite.\n\nPrime Factorisation: Breaking a number into its prime factors.\n12 = 2 x 2 x 3 = 2-squared x 3\n\nWASSCE loves prime factorisation - it is the foundation for HCF and LCM!"),
        q("coremath-m1t1-s4", "What is the prime factorisation of 36?",
          "Write 36 as a product of primes",
          ["2-squared x 3-squared", "2-cubed x 3", "6-squared", "2-squared x 9"], 0,
          "36 = 6 x 6 = (2 x 3) x (2 x 3) = 2-squared x 3-squared. Always break down until all factors are prime!"),
        i("coremath-m1t1-s5",
          "HCF and LCM - WASSCE Favourites!\n\nHighest Common Factor (HCF): The largest number that divides two or more numbers exactly.\nFind by: List factors OR use prime factorisation (take common primes with smallest powers)\n\nLowest Common Multiple (LCM): The smallest number that is a multiple of two or more numbers.\nFind by: List multiples OR use prime factorisation (take all primes with largest powers)\n\nExample: Find HCF and LCM of 12 and 18.\n12 = 2-squared x 3, 18 = 2 x 3-squared\nHCF = 2 x 3 = 6 (common primes, smallest powers)\nLCM = 2-squared x 3-squared = 36 (all primes, largest powers)"),
        q("coremath-m1t1-s6", "Find the HCF of 24 and 36.",
          "HCF of 24 and 36", ["6", "12", "72", "8"], 1,
          "24 = 2-cubed x 3, 36 = 2-squared x 3-squared. HCF = 2-squared x 3 = 12. Indeed, 12 is the largest number dividing both 24 and 36!"),
    ]),
    L("coremath-m1t2", "Rational and Irrational Numbers",
      "Core Mathematics", "1d522", "Both", 1, 10, 25, "core-maths", ["coremath-m1t1"], ["SHS 1"], "SHS 1", [
        i("coremath-m1t2-s1",
          "Rational Numbers (Q): Any number that can be expressed as a fraction p/q where p and q are integers and q is not 0.\n\nExamples of rational numbers:\n3 = 3/1, 0.5 = 1/2, -2.75 = -11/4, 0.333... = 1/3, sqrt(4) = 2\n\nExamples of irrational numbers:\nsqrt(2), pi, sqrt(3), sqrt(5)\n\nWASSCE Tip: A number is rational if its decimal form terminates or repeats. If it never repeats and never ends, it is irrational!"),
        p("coremath-m1t2-s2", "Look at these numbers: sqrt(4), 0.75, 1/3, sqrt(3), pi\n\nWhich are rational and which are irrational?",
          "sqrt(4), 0.75, 1/3, sqrt(3), pi", "How many of these are rational numbers?",
          ["All 5 are rational", "3 are rational, 2 are irrational", "2 are rational, 3 are irrational", "4 are rational, 1 is irrational"], 1,
          "sqrt(4)=2 (rational), 0.75=3/4 (rational), 1/3 (rational), sqrt(3) (irrational), pi (irrational). So 3 rational, 2 irrational."),
        i("coremath-m1t2-s3",
          "Real Numbers and the Number Line\n\nReal Numbers (R): The set of ALL rational and irrational numbers. Every real number has a position on the number line.\n\nReal Numbers (R)\n  Rational (Q)\n    Integers (Z)\n      Natural (N)\n    Fractions & decimals\n  Irrational (sqrt(2), pi, e, ...)\n\nDid you know? Between any two real numbers, there are infinitely many other real numbers!"),
        q("coremath-m1t2-s4", "Which set does the number sqrt(9) belong to?",
          "sqrt(9) belongs to which sets?",
          ["Natural only", "Integer only", "Rational only", "N, Z, Q, and R"], 3,
          "sqrt(9) = 3, which is a natural number, integer, rational number, and real number. It belongs to all these sets!"),
        i("coremath-m1t2-s5",
          "Approximating Irrational Numbers\n\nEven though irrational numbers cannot be written exactly as fractions, we can approximate them.\n\nMethod: Trial and Improvement\nsqrt(5) is between 2-squared = 4 and 3-squared = 9, so sqrt(5) is between 2 and 3.\n2.2-squared = 4.84 (too low)\n2.3-squared = 5.29 (too high)\n2.24-squared = 5.0176 (slightly high)\n2.23-squared = 4.9729 (slightly low)\nSo sqrt(5) is approx 2.236 (to 3 decimal places)"),
        c("coremath-m1t2-s6", "Number Sets Mastery", [
            {"question": "Which of the following is an irrational number?", "options": ["0.75", "sqrt(16)", "sqrt(7)", "22/7"], "correctIndex": 2, "explanation": "sqrt(7) is non-repeating, non-terminating - it is irrational."},
            {"question": "sqrt(64) belongs to which sets?", "options": ["Natural only", "Integer only", "All real number sets", "Irrational"], "correctIndex": 2, "explanation": "sqrt(64) = 8, which belongs to N, Z, Q, and R."},
        ]),
    ]),
    L("coremath-m1t3", "Indices and Standard Form",
      "Core Mathematics", "1d522", "Both", 2, 12, 30, "core-maths", ["coremath-m1t1"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m1t3-s1",
          "Laws of Indices (Exponents) - WASSCE Essential!\n\n1. Product Rule: a-to-the-n x a-to-the-m = a-to-the-(n+m)\n   Example: 2-cubed x 2-to-the-4 = 2-to-the-7 = 128\n\n2. Quotient Rule: a-to-the-n / a-to-the-m = a-to-the-(n-m)\n   Example: 2-to-the-5 / 2-squared = 2-cubed = 8\n\n3. Power Rule: (a-to-the-n)-to-the-m = a-to-the-(nxm)\n   Example: (2-squared)-cubed = 2-to-the-6 = 64\n\n4. Zero Index: a-to-the-0 = 1 (for any a not 0)\n\n5. Negative Index: a-to-the-( -n) = 1/a-to-the-n\n   Example: 2-to-the-( -3) = 1/8"),
        p("coremath-m1t3-s2", "Simplify: 3-to-the-5 x 3-to-the-( -2)\n\nCan you predict the answer?",
          "3-to-the-5 x 3-to-the-( -2)", "What is the simplified result?",
          ["3-cubed = 27", "3-to-the-7", "3-to-the-( -10)", "9-cubed"], 0,
          "Using the product rule: 3-to-the-5 x 3-to-the-( -2) = 3-to-the-(5 + -2) = 3-cubed = 27."),
        i("coremath-m1t3-s3",
          "Fractional Indices\n\nFractional exponents represent roots!\n\na-to-the-(1/n) = nth root of a\na-to-the-(m/n) = (nth root of a)-to-the-m\n\nExamples:\n9-to-the-(1/2) = sqrt(9) = 3\n8-to-the-(1/3) = cube root of 8 = 2\n27-to-the-(2/3) = (cube root of 27)-squared = 3-squared = 9\n16-to-the-(3/4) = (4th root of 16)-cubed = 2-cubed = 8\n\nWASSCE loves fractional indices! Remember: Denominator = root, Numerator = power."),
        q("coremath-m1t3-s4", "Evaluate: 8-to-the-(2/3)",
          "8 to the power of 2/3 = ?", ["4", "16/3", "64/3", "16"], 0,
          "8-to-the-(2/3) = (cube root of 8)-squared = 2-squared = 4. First find the cube root, then square it!"),
        i("coremath-m1t3-s5",
          "Standard Form (Scientific Notation)\n\nStandard form is a way of writing very large or very small numbers.\n\nFormat: A x 10-to-the-n where 1 <= A < 10 and n is an integer.\n\nExamples:\n3,000,000 = 3 x 10-to-the-6\n45,000 = 4.5 x 10-to-the-4\n0.005 = 5 x 10-to-the-( -3)\n0.0000072 = 7.2 x 10-to-the-( -6)\n\nQuick Method: Count how many places the decimal point moves!\nLarge numbers -> positive power (move left)\nSmall numbers -> negative power (move right)"),
        q("coremath-m1t3-s6", "Write 0.0000456 in standard form.",
          "0.0000456 in standard form = ?",
          ["4.56 x 10-to-the-( -5)", "4.56 x 10-to-the-5", "456 x 10-to-the-( -7)", "4.56 x 10-to-the-( -4)"], 0,
          "Move the decimal 5 places to the right: 0.0000456 = 4.56 x 10-to-the-( -5). Negative power because it is a small number!"),
    ]),
    L("coremath-m1t4", "Number Bases",
      "Core Mathematics", "1d522", "Both", 2, 10, 25, "core-maths", ["coremath-m1t1"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m1t4-s1",
          "Introduction to Number Bases\n\nWe usually work in base 10 (denary/decimal) - using digits 0-9. But numbers can be written in other bases!\n\nBase 2 (Binary): Uses digits 0 and 1 only.\nPlace values: ..., 8, 4, 2, 1 (powers of 2)\n\nBase 5: Uses digits 0-4\nPlace values: ..., 125, 25, 5, 1 (powers of 5)\n\nConverting to Base 10: Multiply each digit by its place value and add.\n\nExample: Convert 1101 (base 2) to base 10.\n1101 (base 2) = 1x8 + 1x4 + 0x2 + 1x1 = 8 + 4 + 0 + 1 = 13 (base 10)"),
        p("coremath-m1t4-s2", "Look at this binary number: 1011 (base 2)\n\nCan you convert it to base 10?",
          "1011 (base 2) = ? (base 10)", "What is 1011 in base 10?",
          ["11", "13", "14", "10"], 0,
          "1011 (base 2) = 1x8 + 0x4 + 1x2 + 1x1 = 8 + 0 + 2 + 1 = 11 (base 10)."),
        i("coremath-m1t4-s3",
          "Converting from Base 10 to Other Bases\n\nMethod: Repeated Division\nDivide the number by the target base, recording remainders. Read remainders from bottom to top!\n\nExample: Convert 25 (base 10) to binary (base 2).\n2 into 25 remainder 1\n2 into 12 remainder 0\n2 into 6 remainder 0\n2 into 3 remainder 1\n2 into 1 remainder 1\n    0\n\nRead remainders upwards: 11001 (base 2)\nCheck: 16 + 8 + 0 + 0 + 1 = 25. Correct!"),
        q("coremath-m1t4-s4", "Convert 37 (base 10) to base 5.",
          "37 in base 5 = ?", ["122 (base 5)", "132 (base 5)", "112 (base 5)", "202 (base 5)"], 0,
          "5 into 37 r2, 5 into 7 r2, 5 into 1 r1, 0. Read up: 122 (base 5). Check: 1x25 + 2x5 + 2x1 = 25 + 10 + 2 = 37!"),
        i("coremath-m1t4-s5",
          "Addition in Other Bases\n\nAdding in other bases works just like base 10 - but you carry when you reach the base value!\n\nExample: Add 1011 (base 2) + 110 (base 2)\n  1011\n+  110\n------\n 10001\n\nCheck: 11 (base 10) + 6 (base 10) = 17 (base 10) = 10001 (base 2). Correct!"),
        c("coremath-m1t4-s6", "Number Bases Mastery", [
            {"question": "Convert 1010 (base 2) to base 10.", "options": ["8", "10", "12", "5"], "correctIndex": 1, "explanation": "1010 (base 2) = 1x8 + 0x4 + 1x2 + 0x1 = 10 (base 10)"},
            {"question": "Convert 42 (base 10) to base 2.", "options": ["101010", "110010", "101100", "110100"], "correctIndex": 0, "explanation": "42 = 32 + 8 + 2 = 101010 (base 2)"},
        ]),
    ]),
    L("coremath-m1t5", "Set Theory and Venn Diagrams",
      "Core Mathematics", "1d522", "Both", 2, 12, 30, "core-maths", ["coremath-m1t1"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m1t5-s1",
          "Sets: The Language of Mathematics\n\nA set is a collection of distinct objects (elements).\n\nSet Notation (WASSCE Essential!):\nA = {1, 2, 3, 4, 5} - listing elements\nx in A - x is an element of set A\nx not in A - x is NOT in set A\nn(A) = 5 - number of elements in A\nEmpty set: {} or the symbol for empty set\n\nTypes of Sets:\nUniversal Set: Everything we are considering\nFinite Set: Has a countable number of elements\nInfinite Set: Goes on forever"),
        p("coremath-m1t5-s2", "If A = {1, 2, 3, 4} and B = {3, 4, 5, 6},\n\nWhat do you think A intersect B means?",
          "A = {1,2,3,4}, B = {3,4,5,6}", "What is A intersect B?",
          ["{1, 2, 3, 4, 5, 6}", "{3, 4}", "{1, 2}", "{5, 6}"], 1,
          "A intersect B means A intersection B - elements in BOTH sets. The common elements are {3, 4}."),
        i("coremath-m1t5-s3",
          "Set Operations - Union, Intersection, Complement\n\nUnion (A union B): All elements in A OR B (or both).\nA union B = {1, 2, 3, 4, 5, 6}\n\nIntersection (A intersect B): Elements in BOTH A and B.\nA intersect B = {3, 4}\n\nComplement (A' or A-complement): Everything in the universal set that is NOT in A.\n\nDifference (A - B): Elements in A but NOT in B.\nA - B = {1, 2}"),
        q("coremath-m1t5-s4", "Universal set = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}\nA = {2, 4, 6, 8, 10}\nB = {1, 3, 5, 7, 9}\n\nWhat is A union B?",
          "Union of A and B",
          ["{2, 4, 6, 8, 10}", "{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}", "{1, 3, 5, 7, 9}", "{}"], 1,
          "A union B = all elements in A OR B = all numbers 1-10 = universal set."),
        i("coremath-m1t5-s5",
          "Venn Diagrams - Visualising Sets\n\nVenn diagrams use overlapping circles to show relationships between sets.\n\nExample Problem:\nIn a class of 40 students: 20 study Maths, 18 study Science, 8 study both.\n\nStep 1: Place 8 in the intersection (both).\nStep 2: Maths-only = 20 - 8 = 12\nStep 3: Science-only = 18 - 8 = 10\nStep 4: Neither = 40 - (12 + 8 + 10) = 10\n\nFormula: n(A union B) = n(A) + n(B) - n(A intersect B)"),
        q("coremath-m1t5-s6", "In a class of 30 students: 15 play football, 12 play basketball, 5 play both.\n\nHow many play neither sport?",
          "Neither = ?", ["8", "3", "10", "5"], 0,
          "Football only = 15-5=10. Basketball only = 12-5=7. Both = 5. Playing at least one = 10+7+5=22. Neither = 30-22 = 8."),
    ]),
]

# ═══════════════════════════════════════════════════════════════════════
#  MODULE 2: Fractions, Decimals & Percentages (5 Topics)
# ═══════════════════════════════════════════════════════════════════════
MODULE2 = [
    L("coremath-m2t1", "Fractions - Operations and Comparison",
      "Core Mathematics", "1d522", "Both", 1, 8, 20, "core-maths", ["coremath-m1t1"], ["SHS 1"], "SHS 1", [
        i("coremath-m2t1-s1",
          "Fractions represent parts of a whole. A fraction has a numerator (top) and denominator (bottom).\n\nTypes of Fractions:\nProper: numerator < denominator (e.g. 3/5)\nImproper: numerator > denominator (e.g. 7/4)\nMixed: whole number + proper fraction (e.g. 1 and 3/4)\n\nEquivalent Fractions: Multiplying or dividing both numerator and denominator by the same number gives an equivalent fraction.\n\n1/2 = 2/4 = 3/6 = 4/8 = 5/10\n\nSimplifying: Divide numerator and denominator by their HCF.\n12/18 = 2/3 (divided by 6)"),
        p("coremath-m2t1-s2", "Look at these fractions: 1/2, 2/4, 4/8, 8/16\n\nWhat is the pattern?",
          "1/2, 2/4, 4/8, 8/16", "What do these fractions have in common?",
          ["They are all equal to 1/2", "They are increasing", "They are all improper", "They have no pattern"], 0,
          "They are all equivalent fractions equal to 1/2! Each is formed by multiplying numerator and denominator by the same number."),
        i("coremath-m2t1-s3",
          "Adding and Subtracting Fractions - WASSCE Essential!\n\nTo add or subtract fractions, they must have the SAME denominator.\n\nStep 1: Find the LCM of the denominators (Lowest Common Denominator)\nStep 2: Convert each fraction to an equivalent fraction with that denominator\nStep 3: Add/subtract the numerators only\nStep 4: Simplify if possible\n\nExample: 1/3 + 1/4\nLCM of 3 and 4 = 12\n1/3 = 4/12, 1/4 = 3/12\n1/3 + 1/4 = 4/12 + 3/12 = 7/12\n\nMultiplying Fractions:\nMultiply numerators together and denominators together.\n2/3 x 4/5 = 8/15\n\nDividing Fractions:\nFlip the second fraction (reciprocal) and multiply.\n2/3 / 4/5 = 2/3 x 5/4 = 10/12 = 5/6"),
        q("coremath-m2t1-s4", "Calculate: 2/5 + 1/3",
          "2/5 + 1/3 = ?", ["3/8", "11/15", "3/15", "11/8"], 1,
          "LCM of 5 and 3 = 15. 2/5 = 6/15, 1/3 = 5/15. 6/15 + 5/15 = 11/15."),
        c("coremath-m2t1-s5", "Fractions Mastery", [
            {"question": "What is 3/4 - 1/3?", "options": ["2/1", "5/12", "1/12", "5/7"], "correctIndex": 1, "explanation": "LCM of 4 and 3 = 12. 3/4=9/12, 1/3=4/12. 9/12-4/12=5/12"},
            {"question": "What is 2/3 x 3/5?", "options": ["6/8", "2/5", "5/6", "2/15"], "correctIndex": 1, "explanation": "2/3 x 3/5 = 6/15 = 2/5. Cancel the 3s first!"},
        ]),
    ]),
    L("coremath-m2t2", "Decimals - Operations and Conversions",
      "Core Mathematics", "1d522", "Both", 1, 8, 20, "core-maths", ["coremath-m2t1"], ["SHS 1"], "SHS 1", [
        i("coremath-m2t2-s1",
          "Decimals are fractions written in base 10.\n\nPlace Values:\n0.123 = 1/10 + 2/100 + 3/1000\n\nConverting Fractions to Decimals:\nDivide numerator by denominator.\n1/2 = 0.5, 3/4 = 0.75, 1/3 = 0.333... (recurring)\n\nConverting Decimals to Fractions:\nWrite as a fraction over 10, 100, or 1000, then simplify.\n0.75 = 75/100 = 3/4\n0.125 = 125/1000 = 1/8\n\nRecurring Decimals:\n0.333... = 1/3, 0.666... = 2/3, 0.1666... = 1/6\n\nWASSCE Tip: Know common decimal-fraction conversions!"),
        p("coremath-m2t2-s2", "What is 0.625 as a simplified fraction?",
          "0.625 = ?", "0.625 in fraction form = ?",
          ["5/8", "25/40", "625/1000", "3/5"], 0,
          "0.625 = 625/1000 = 125/200 = 25/40 = 5/8. Always simplify to lowest terms!"),
        i("coremath-m2t2-s3",
          "Operations with Decimals\n\nAdding/Subtracting: Line up the decimal points!\n12.34 + 5.6 = 17.94\n\nMultiplying:\n1. Multiply as if they were whole numbers\n2. Count total decimal places in both numbers\n3. Place the decimal point that many places from the right\n\nExample: 2.5 x 0.3\n25 x 3 = 75\nTotal decimal places: 1 + 1 = 2\n2.5 x 0.3 = 0.75\n\nDividing:\nMove the decimal in the divisor to make it a whole number, then move the decimal in the dividend the same number of places.\n\nExample: 4.8 / 0.2 = 48 / 2 = 24"),
        q("coremath-m2t2-s4", "Calculate: 3.6 x 0.4",
          "3.6 x 0.4 = ?", ["14.4", "1.44", "0.144", "144"], 1,
          "36 x 4 = 144. Total decimal places: 1 + 1 = 2. So 3.6 x 0.4 = 1.44."),
    ]),
    L("coremath-m2t3", "Percentages - Calculations and Applications",
      "Core Mathematics", "1d522", "Both", 2, 10, 25, "core-maths", ["coremath-m2t2"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m2t3-s1",
          "Percentage means 'out of 100'.\n\nConverting: Fraction/Decimal to Percentage: Multiply by 100%\n0.25 = 0.25 x 100% = 25%\n3/4 = 3/4 x 100% = 75%\n\nConverting: Percentage to Fraction: Divide by 100 and simplify\n25% = 25/100 = 1/4\n\nConverting: Percentage to Decimal: Divide by 100\n25% = 0.25\n\nPercentage of a Quantity:\nFind 15% of 200.\n15% = 15/100 = 0.15\n0.15 x 200 = 30\n\nWASSCE loves percentage problems in real-world contexts!"),
        p("coremath-m2t3-s2", "What is 20% of 250?", "20% of 250", "20% of 250 = ?",
          ["50", "25", "70", "100"], 0,
          "20% = 20/100 = 0.2. 0.2 x 250 = 50. Or: 10% of 250 = 25, so 20% = 2 x 25 = 50."),
        i("coremath-m2t3-s3",
          "Percentage Change - WASSCE Favourite!\n\nPercentage Increase/Decrease:\nPercentage Change = (Change / Original) x 100%\n\nExample: A price rises from 50 to 65.\nChange = 65 - 50 = 15\nPercentage increase = (15/50) x 100% = 30%\n\nFinding the Original Amount (Reverse Percentage):\nIf a price after a 20% increase is 120, what was the original?\nOriginal x 1.20 = 120\nOriginal = 120 / 1.20 = 100\n\nProfit and Loss:\nProfit % = (Profit / Cost Price) x 100%\nLoss % = (Loss / Cost Price) x 100%"),
        q("coremath-m2t3-s4", "A student scored 42 out of 60 in a test. What is the percentage score?",
          "42/60 as a percentage = ?", ["60%", "70%", "80%", "65%"], 1,
          "42/60 x 100% = 0.7 x 100% = 70%. Another way: 42/60 = 7/10 = 70%."),
    ]),
    L("coremath-m2t4", "Ratio and Proportion",
      "Core Mathematics", "1d522", "Both", 2, 10, 25, "core-maths", ["coremath-m2t2"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m2t4-s1",
          "Ratio compares quantities of the same kind.\n\nWriting Ratios:\nIf there are 3 boys and 5 girls, the ratio boys:girls = 3:5\n\nSimplifying Ratios:\nDivide both parts by their HCF.\n12:8 = 3:2 (divided by 4)\n\nSharing in a Ratio:\nTo share 60 in the ratio 2:3:\nTotal parts = 2 + 3 = 5\nEach part = 60 / 5 = 12\nFirst share = 2 x 12 = 24\nSecond share = 3 x 12 = 36\n\nWASSCE loves sharing in ratio problems!"),
        p("coremath-m2t4-s2", "Share 80gh between two people in the ratio 3:5.\n\nHow much does each person get?",
          "80gh in ratio 3:5", "First person gets? Second person gets?",
          ["30gh and 50gh", "40gh and 40gh", "24gh and 56gh", "48gh and 32gh"], 0,
          "Total parts = 3 + 5 = 8. Each part = 80/8 = 10. First = 3x10 = 30gh. Second = 5x10 = 50gh."),
        i("coremath-m2t4-s3",
          "Direct and Inverse Proportion\n\nDirect Proportion: As one quantity increases, the other increases at the same rate.\ny = kx where k is the constant of proportionality\n\nExample: Cost of apples. If 5 apples cost 10gh, then 8 apples cost 16gh.\n\nInverse Proportion: As one quantity increases, the other decreases at the same rate.\ny = k/x\n\nExample: Speed and time. If you travel at 60 km/h taking 2 hours, at 120 km/h it takes 1 hour.\n\nWASSCE question: If 8 workers can build a wall in 6 days, how long would 12 workers take?\nInverse proportion: 8 x 6 = 12 x days\nDays = (8 x 6)/12 = 4 days"),
        q("coremath-m2t4-s4", "If 3 books cost 45gh, how much do 7 books cost?",
          "3 books = 45gh, 7 books = ?", ["90gh", "105gh", "75gh", "120gh"], 1,
          "Direct proportion: 1 book = 45/3 = 15gh. 7 books = 7 x 15 = 105gh."),
    ]),
    L("coremath-m2t5", "Rates and Sharing",
      "Core Mathematics", "1d522", "Both", 2, 10, 25, "core-maths", ["coremath-m2t4"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m2t5-s1",
          "Rates compare quantities of different kinds.\n\nCommon Rates:\nSpeed = Distance / Time (km/h, m/s)\nDensity = Mass / Volume (kg/m-cubed)\nRate of work = Work done / Time\n\nExample: A car travels 240 km in 3 hours.\nSpeed = 240/3 = 80 km/h\n\nAverage Rate:\nWhen quantities change, we use average.\nAverage speed = Total distance / Total time"),
        p("coremath-m2t5-s2", "A tap fills a tank in 4 hours. What fraction of the tank does it fill in 1 hour?",
          "Tap fills tank in 4 hours", "Fraction filled in 1 hour = ?",
          ["1/2", "1/4", "1/8", "3/4"], 1,
          "In 4 hours = 1 whole tank. In 1 hour = 1/4 of the tank. Rate of work = 1/4 tank per hour."),
        i("coremath-m2t5-s3",
          "Combined Rates - WASSCE Favourite!\n\nProblem: If tap A fills a tank in 3 hours and tap B fills it in 6 hours, how long to fill together?\n\nTap A's rate = 1/3 tank per hour\nTap B's rate = 1/6 tank per hour\nCombined rate = 1/3 + 1/6 = 2/6 + 1/6 = 3/6 = 1/2 tank per hour\n\nTime to fill together = 1 / (1/2) = 2 hours\n\nSimple Interest:\nI = PRT/100\nWhere I = Interest, P = Principal, R = Rate, T = Time in years\n\nExample: 500gh at 10% for 2 years.\nI = (500 x 10 x 2)/100 = 100gh"),
        q("coremath-m2t5-s4", "Tap A fills a tank in 2 hours. Tap B fills the same tank in 3 hours.\n\nHow long to fill the tank if both taps are opened together?",
          "Combined time = ?", ["1 hour", "1.2 hours", "2.5 hours", "1.5 hours"], 1,
          "A: 1/2 per hour. B: 1/3 per hour. Combined: 1/2 + 1/3 = 3/6 + 2/6 = 5/6 per hour. Time = 1/(5/6) = 6/5 = 1.2 hours."),
    ]),
]

# ═══════════════════════════════════════════════════════════════════════
#  MODULE 3: Algebraic Expressions & Factorisation (5 Topics)
# ═══════════════════════════════════════════════════════════════════════
MODULE3 = [
    L("coremath-m3t1", "Simplifying Algebraic Expressions",
      "Core Mathematics", "1d522", "Both", 2, 8, 20, "core-maths", ["coremath-m1t1"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m3t1-s1",
          "Algebra uses letters to represent unknown numbers.\n\nLike Terms: Terms with the same variable and power.\n3x and 5x are like terms\n4x-squared and 7x-squared are like terms\n3x and 3x-squared are NOT like terms\n\nSimplify by combining like terms:\n3x + 5x = 8x\n4x + 2y + 3x + y = 7x + 3y\n\nConstants: numbers without variables\n2x + 5 + 3x - 2 = 5x + 3\n\nSubstitution: Replace letters with numbers.\nIf x = 3, then 2x + 5 = 2(3) + 5 = 11"),
        p("coremath-m3t1-s2", "Simplify: 3a + 2b + 5a - b\n\nWhat is the simplified expression?",
          "3a + 2b + 5a - b", "Simplified = ?",
          ["8a + 3b", "8a + b", "9ab", "7a + 2b"], 1,
          "Group like terms: 3a + 5a = 8a, 2b - b = b. So 3a + 2b + 5a - b = 8a + b."),
        i("coremath-m3t1-s3",
          "Algebraic Conventions - Know These!\n\nMultiplication: 2 x x = 2x (dot or nothing between variable)\nDivision: x / 3 or x/3\nIndices: a x a x a = a-cubed\n\nKey Substitution Skills (WASSCE Essential!):\nIf x = 2, y = 3:\n3x + 2y = 3(2) + 2(3) = 6 + 6 = 12\n4x-squared - y = 4(4) - 3 = 16 - 3 = 13\n\nAlways use brackets when substituting!"),
        q("coremath-m3t1-s4", "If x = 4 and y = 2, evaluate: 3x-squared - 2y",
          "3(4-squared) - 2(2) = ?", ["44", "48", "40", "52"], 0,
          "3(16) - 2(2) = 48 - 4 = 44. Remember: x-squared means x to the power 2, not x times 2!"),
    ]),
    L("coremath-m3t2", "Expansion of Brackets",
      "Core Mathematics", "1d522", "Both", 2, 10, 25, "core-maths", ["coremath-m3t1"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m3t2-s1",
          "Expanding brackets means multiplying what is outside the bracket by everything inside.\n\na(b + c) = ab + ac\n\nExample 1: 3(x + 4) = 3x + 12\nExample 2: -2(3x - 5) = -6x + 10\nExample 3: 2x(3x + 1) = 6x-squared + 2x\n\nQuick check: Expand 5(2x - 3) = 10x - 15\n\nWASSCE Tip: Pay attention to negative signs outside the bracket - they change all signs inside!"),
        p("coremath-m3t2-s2", "Expand: -3(2x - 4)\n\nWhat is the result?",
          "-3(2x - 4)", "Expanded form = ?",
          ["-6x - 12", "-6x + 12", "6x - 12", "-5x + 1"], 1,
          "-3 x 2x = -6x. -3 x -4 = +12. So -3(2x - 4) = -6x + 12. Two negatives make a positive!"),
        i("coremath-m3t2-s3",
          "Expanding Double Brackets - FOIL Method\n\n(a + b)(c + d) = ac + ad + bc + bd\n\nFOIL: First, Outer, Inner, Last\n\nExample: (x + 3)(x + 5)\nFirst: x x x = x-squared\nOuter: x x 5 = 5x\nInner: 3 x x = 3x\nLast: 3 x 5 = 15\n= x-squared + 5x + 3x + 15\n= x-squared + 8x + 15\n\nSpecial Products - Memorise These!\n(a + b)-squared = a-squared + 2ab + b-squared\n(a - b)-squared = a-squared - 2ab + b-squared\n(a + b)(a - b) = a-squared - b-squared (Difference of two squares)"),
        q("coremath-m3t2-s4", "Expand: (x + 2)(x + 7)",
          "(x + 2)(x + 7) = ?", ["x-squared + 9x + 14", "x-squared + 14", "2x + 9", "x-squared + 9x + 9"], 0,
          "FOIL: First = x-squared, Outer = 7x, Inner = 2x, Last = 14. = x-squared + 7x + 2x + 14 = x-squared + 9x + 14."),
    ]),
    L("coremath-m3t3", "Factorisation",
      "Core Mathematics", "1d522", "Both", 2, 10, 25, "core-maths", ["coremath-m3t2"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m3t3-s1",
          "Factorisation is the reverse of expansion - putting an expression back into brackets.\n\nFactorising by taking out common factors:\nFind the HCF of all terms and write it outside the bracket.\n\nExample: 6x + 9\nHCF of 6 and 9 = 3\n6x + 9 = 3(2x + 3)\n\nCheck: Expand 3(2x + 3) = 6x + 9. Correct!\n\nExample: 12x-squared + 8x\nHCF of 12 and 8 is 4. Common variables: x (smallest power is 1)\n12x-squared + 8x = 4x(3x + 2)"),
        p("coremath-m3t3-s2", "Factorise: 15y - 10\n\nWhat goes outside the brackets?",
          "15y - 10 = ?(3y - 2)", "What is the HCF?",
          ["2", "3", "5", "10"], 2,
          "HCF of 15 and 10 = 5. 15y - 10 = 5(3y - 2). Check: 5(3y - 2) = 15y - 10."),
        i("coremath-m3t3-s3",
          "Factorising Quadratics - WASSCE Favourite!\n\nTo factorise x-squared + bx + c, find two numbers that:\nMultiply to give c\nAdd to give b\n\nExample: x-squared + 7x + 12\nFind two numbers multiplying to 12 and adding to 7: 3 and 4\nx-squared + 7x + 12 = (x + 3)(x + 4)\n\nExample: x-squared - 5x + 6\nFind two numbers multiplying to 6 and adding to -5: -2 and -3\nx-squared - 5x + 6 = (x - 2)(x - 3)\n\nDifference of Two Squares:\na-squared - b-squared = (a + b)(a - b)\nx-squared - 25 = (x + 5)(x - 5)"),
        q("coremath-m3t3-s4", "Factorise: x-squared + 5x + 6",
          "x-squared + 5x + 6 = ?", ["(x + 2)(x + 4)", "(x + 2)(x + 3)", "(x + 1)(x + 6)", "(x - 2)(x - 3)"], 1,
          "Find two numbers multiplying to 6 and adding to 5: 2 and 3. x-squared + 5x + 6 = (x + 2)(x + 3)."),
    ]),
    L("coremath-m3t4", "Algebraic Fractions",
      "Core Mathematics", "1d522", "Both", 3, 10, 30, "core-maths", ["coremath-m3t1", "coremath-m2t1"], ["SHS 2", "SHS 3"], "SHS 2", [
        i("coremath-m3t4-s1",
          "Algebraic fractions work like numeric fractions, but with variables.\n\nSimplifying: Cancel common factors in numerator and denominator.\n(6x)/(9x-squared) = 2/(3x) (Cancel x and divide by 3)\n\nSimplifying more complex fractions:\n(x-squared - 1)/(x - 1)\nFactorise numerator: (x-1)(x+1)/(x-1) = x + 1\n\nWASSCE Tip: Always factorise first, then cancel common factors!"),
        p("coremath-m3t4-s2", "Simplify: (x-squared - 9)/(x - 3)",
          "(x-squared - 9)/(x - 3)", "Simplified = ?",
          ["x - 3", "x + 3", "x - 9", "x + 9"], 1,
          "x-squared - 9 = (x-3)(x+3) [difference of two squares]. (x-3)(x+3)/(x-3) = x + 3."),
        i("coremath-m3t4-s3",
          "Adding and Subtracting Algebraic Fractions\n\nSame method as numeric fractions - find the common denominator!\n\nExample: 2/x + 3/(2x)\nCommon denominator = 2x\n2/x = 4/(2x)\n2/x + 3/(2x) = 4/(2x) + 3/(2x) = 7/(2x)\n\nExample with binomials:\n1/(x+1) + 1/(x-1)\nCommon denominator = (x+1)(x-1)\n= (x-1)/((x+1)(x-1)) + (x+1)/((x+1)(x-1))\n= (x-1 + x+1)/((x+1)(x-1))\n= 2x/(x-squared - 1)\n\nMultiplying: Multiply numerators and denominators.\nDividing: Flip the second and multiply."),
        q("coremath-m3t4-s4", "Simplify: 1/x + 1/(2x)",
          "1/x + 1/(2x) = ?", ["2/(2x)", "3/(2x)", "2/x-squared", "3/x"], 1,
          "Common denominator = 2x. 1/x = 2/(2x). So 1/x + 1/(2x) = 2/(2x) + 1/(2x) = 3/(2x)."),
    ]),
    L("coremath-m3t5", "Linear Inequalities",
      "Core Mathematics", "1d522", "Both", 2, 10, 25, "core-maths", ["coremath-m3t1"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m3t5-s1",
          "Inequalities compare quantities that are not necessarily equal.\n\nSymbols:\n< means 'less than'\n> means 'greater than'\n<= means 'less than or equal to'\n>= means 'greater than or equal to'\n\nSolving Linear Inequalities:\nSame as solving equations, BUT:\nIf you multiply or divide by a NEGATIVE number, flip the inequality sign!\n\nExample: 2x + 3 < 11\n2x < 8\nx < 4\n\nExample with negative: -3x < 12\nDivide by -3: x > -4 (sign flips!)"),
        p("coremath-m3t5-s2", "Solve: 2x - 5 <= 7\n\nWhat is the solution?",
          "2x - 5 <= 7", "x <= ?",
          ["x <= 6", "x <= 1", "x <= 12", "x >= 6"], 0,
          "2x - 5 <= 7. Add 5: 2x <= 12. Divide by 2: x <= 6. No sign flip because we divided by a positive number."),
        i("coremath-m3t5-s3",
          "Representing Inequalities on a Number Line\n\nx < 3: Open circle at 3, arrow left\nx > -1: Open circle at -1, arrow right\nx <= 2: Closed circle at 2, arrow left\nx >= 0: Closed circle at 0, arrow right\n\nCompound Inequalities:\n2 < x <= 5 means 'x is greater than 2 AND x is less than or equal to 5'\nOn a number line: Open circle at 2, closed circle at 5, line between them.\n\nWASSCE often asks you to solve and represent on a number line!"),
        q("coremath-m3t5-s4", "Solve: 3x + 1 > 10",
          "Solve: 3x + 1 > 10, what is x > ?", ["x > 3", "x > 11/3", "x > 9", "x < 3"], 0,
          "3x + 1 > 10. Subtract 1: 3x > 9. Divide by 3: x > 3. All numbers greater than 3 satisfy this!"),
    ]),
]

# ═══════════════════════════════════════════════════════════════════════
#  MODULE 4: Linear Equations & Relations (5 Topics)
# ═══════════════════════════════════════════════════════════════════════
MODULE4 = [
    L("coremath-m4t1", "Solving Linear Equations",
      "Core Mathematics", "1d522", "Both", 2, 10, 25, "core-maths", ["coremath-m3t1"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m4t1-s1",
          "A linear equation has the variable raised to the power 1.\n\nGoal: Get the variable alone on one side.\n\nMethod:\n1. Remove brackets (expand if needed)\n2. Collect variable terms on one side, constants on the other\n3. Divide by the coefficient of the variable\n\nExample: 3x + 7 = 22\nSubtract 7: 3x = 15\nDivide by 3: x = 5\n\nCheck: 3(5) + 7 = 15 + 7 = 22. Correct!\n\nWASSCE Tip: Always check your answer by substituting back!"),
        p("coremath-m4t1-s2", "Solve: 5x - 8 = 22\n\nWhat is x?",
          "5x - 8 = 22", "x = ?", ["4", "6", "30", "14"], 1,
          "5x - 8 = 22. Add 8: 5x = 30. Divide by 5: x = 6. Check: 5(6) - 8 = 30 - 8 = 22."),
        i("coremath-m4t1-s3",
          "Equations with Variables on Both Sides\n\nExample: 4x + 3 = 2x + 11\nSubtract 2x from both sides: 2x + 3 = 11\nSubtract 3: 2x = 8\nDivide by 2: x = 4\n\nCheck: 4(4) + 3 = 19, 2(4) + 11 = 19. Correct!\n\nEquations with Brackets:\n2(3x - 1) = 16\nExpand: 6x - 2 = 16\nAdd 2: 6x = 18\nx = 3\n\nEquations with Fractions:\nMultiply both sides by the common denominator.\nx/2 + x/3 = 5\nMultiply by 6: 3x + 2x = 30\n5x = 30, x = 6"),
        q("coremath-m4t1-s4", "Solve: 3(x - 2) = 12",
          "3(x - 2) = 12, x = ?", ["2", "6", "4", "14"], 1,
          "3(x - 2) = 12. Divide by 3: x - 2 = 4. Add 2: x = 6. Or expand: 3x - 6 = 12, 3x = 18, x = 6."),
    ]),
    L("coremath-m4t2", "Simultaneous Equations",
      "Core Mathematics", "1d522", "Both", 3, 12, 30, "core-maths", ["coremath-m4t1"], ["SHS 2", "SHS 3"], "SHS 2", [
        i("coremath-m4t2-s1",
          "Simultaneous equations are two or more equations with the same variables. We find values that satisfy ALL equations.\n\nMethod 1: Elimination\nMake the coefficients of one variable the same, then add/subtract to eliminate it.\n\nExample:\nx + y = 10\nx - y = 4\n\nAdding: 2x = 14, x = 7\nSubstitute: 7 + y = 10, y = 3\n\nSolution: x = 7, y = 3\n\nCheck: 7 + 3 = 10, 7 - 3 = 4. Correct!"),
        p("coremath-m4t2-s2", "Solve: 2x + y = 7 and x - y = 2\n\nWhat is the solution?",
          "2x + y = 7, x - y = 2", "x = ?, y = ?",
          ["x=3, y=1", "x=2, y=3", "x=1, y=5", "x=4, y=-1"], 0,
          "Add equations: 3x = 9, x = 3. Substitute into x - y = 2: 3 - y = 2, y = 1. Solution: x=3, y=1."),
        i("coremath-m4t2-s3",
          "Method 2: Substitution\n\nMake one variable the subject, then substitute into the other equation.\n\nExample:\n2x + y = 10 ...(1)\n3x - 2y = 1 ...(2)\n\nFrom (1): y = 10 - 2x\nSub into (2): 3x - 2(10 - 2x) = 1\n3x - 20 + 4x = 1\n7x = 21\nx = 3\n\nThen y = 10 - 2(3) = 4\n\nSolution: x = 3, y = 4\n\nWASSCE Tip: Use elimination when coefficients match easily, substitution when one variable is already isolated!"),
        q("coremath-m4t2-s4", "Solve: 3x + y = 14 and 2x - y = 1",
          "3x + y = 14, 2x - y = 1, x = ?, y = ?",
          ["x=3, y=5", "x=2, y=8", "x=5, y=-1", "x=4, y=2"], 0,
          "Add equations: 5x = 15, x = 3. Then 3(3) + y = 14, 9 + y = 14, y = 5. Solution: x=3, y=5."),
    ]),
    L("coremath-m4t3", "Linear Graphs and Gradients",
      "Core Mathematics", "1d522", "Both", 2, 10, 25, "core-maths", ["coremath-m4t1"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m4t3-s1",
          "The Cartesian plane has x-axis (horizontal) and y-axis (vertical). Points are written as (x, y).\n\nLinear equations in the form y = mx + c produce straight-line graphs.\nm = gradient (steepness)\nc = y-intercept (where line crosses y-axis)\n\nFinding the Gradient:\nGradient = (Change in y)/(Change in x) = Rise/Run\n\nFormula: m = (y2 - y1)/(x2 - x1)\n\nExample: Find gradient between (1, 3) and (4, 9)\nm = (9 - 3)/(4 - 1) = 6/3 = 2\n\nPositive gradient: line slopes upward right\nNegative gradient: line slopes downward right"),
        p("coremath-m4t3-s2", "A line passes through (0, 2) and (3, 8).\n\nWhat is the gradient?",
          "Line through (0, 2) and (3, 8)", "Gradient = ?",
          ["2", "3", "6", "1/2"], 0,
          "m = (8-2)/(3-0) = 6/3 = 2. The line has gradient 2 and y-intercept 2, so equation is y = 2x + 2."),
        i("coremath-m4t3-s3",
          "Drawing Linear Graphs\n\nMethod: Find coordinates by substituting x values, then plot points and join.\n\nExample: y = 2x + 1\nx = 0: y = 1, point (0, 1)\nx = 1: y = 3, point (1, 3)\nx = 2: y = 5, point (2, 5)\nx = -1: y = -1, point (-1, -1)\n\nSpecial Lines:\ny = c: horizontal line through (0, c)\nx = a: vertical line through (a, 0)\ny = x: line through origin at 45 degrees\n\nFinding Equation from Graph:\nFind gradient (m) and y-intercept (c), then y = mx + c\n\nWASSCE will ask you to draw graphs, find gradients, and find equations!"),
        q("coremath-m4t3-s4", "What is the equation of a line with gradient 3 and y-intercept -2?",
          "m = 3, c = -2", 
          ["y = 3x - 2", "y = -2x + 3", "y = 3x + 2", "y = -3x - 2"], 0,
          "y = mx + c. m = 3, c = -2. So y = 3x - 2."),
    ]),
    L("coremath-m4t4", "Quadratic Equations",
      "Core Mathematics", "1d522", "Both", 3, 12, 30, "core-maths", ["coremath-m4t1"], ["SHS 2", "SHS 3"], "SHS 2", [
        i("coremath-m4t4-s1",
          "A quadratic equation has the form ax-squared + bx + c = 0, where a is not 0.\n\nGraph of y = ax-squared + bx + c is a parabola.\nIf a > 0: U-shaped (minimum)\nIf a < 0: upside-down U (maximum)\n\nSolving Quadratic Equations:\n\nMethod 1: Factorisation\nx-squared - 5x + 6 = 0\n(x - 2)(x - 3) = 0\nx - 2 = 0 or x - 3 = 0\nx = 2 or x = 3\n\nCheck: 4 - 10 + 6 = 0, 9 - 15 + 6 = 0. Correct!"),
        p("coremath-m4t4-s2", "Solve: x-squared + 7x + 12 = 0\n\nWhat are the solutions?",
          "x-squared + 7x + 12 = 0", "x = ? or x = ?",
          ["x = -3 or x = -4", "x = 3 or x = 4", "x = -2 or x = -6", "x = 2 or x = 6"], 0,
          "Find two numbers multiplying to 12 and adding to 7: 3 and 4. So (x+3)(x+4) = 0. x = -3 or x = -4."),
        i("coremath-m4t4-s3",
          "Method 2: Quadratic Formula\n\nWhen factorisation is difficult, use:\nx = [-b +/- sqrt(b-squared - 4ac)] / 2a\n\nThe discriminant (D) = b-squared - 4ac:\nIf D > 0: Two real roots\nIf D = 0: One real root (repeated)\nIf D < 0: No real roots\n\nExample: x-squared + 5x + 3 = 0\na = 1, b = 5, c = 3\nD = 25 - 12 = 13\nx = [-5 +/- sqrt(13)]/2\nx = (-5 + 3.606)/2 = -0.697\nx = (-5 - 3.606)/2 = -4.303\n\nComplete the Square:\nx-squared + 6x + 5 = 0\n(x + 3)-squared - 9 + 5 = 0\n(x + 3)-squared = 4\nx + 3 = +/-2\nx = -1 or x = -5"),
        q("coremath-m4t4-s4", "Solve: 2x-squared + 5x - 3 = 0 using the formula",
          "2x-squared + 5x - 3 = 0", 
          ["x = 1/2 or x = -3", "x = -1/2 or x = 3", "x = 1 or x = -1.5", "x = -1 or x = 3/2"], 0,
          "a=2, b=5, c=-3. D = 25 - 4(2)(-3) = 25 + 24 = 49. x = [-5 +/- 7]/4. x = 2/4 = 1/2 or x = -12/4 = -3."),
    ]),
    L("coremath-m4t5", "Relations and Functions",
      "Core Mathematics", "1d522", "Both", 3, 10, 25, "core-maths", ["coremath-m4t1"], ["SHS 2", "SHS 3"], "SHS 2", [
        i("coremath-m4t5-s1",
          "A relation links two sets of numbers (domain and range).\n\nA function is a special relation where each input has EXACTLY ONE output.\n\nVertical Line Test: If a vertical line crosses the graph more than once, it is NOT a function.\n\nFunction Notation:\nf(x) = 2x + 3 means 'the function f applied to x equals 2x + 3'\nf(4) = 2(4) + 3 = 11\n\nDomain: All possible input values (x)\nRange: All possible output values (f(x))"),
        p("coremath-m4t5-s2", "If f(x) = 3x - 5, what is f(4)?",
          "f(x) = 3x - 5", "f(4) = ?", ["12", "7", "17", "4"], 1,
          "f(4) = 3(4) - 5 = 12 - 5 = 7. Substitute 4 for x."),
        i("coremath-m4t5-s3",
          "Types of Functions (WASSCE Essential!)\n\nLinear: f(x) = mx + c (straight line)\nQuadratic: f(x) = ax-squared + bx + c (parabola)\nCubic: f(x) = ax-cubed + bx-squared + cx + d\n\nComposite Functions:\nf(g(x)) means 'apply g first, then apply f to the result'\n\nExample: f(x) = 2x, g(x) = x + 3\nf(g(4)) = f(7) = 14\ng(f(4)) = g(8) = 11\n\nNote: f(g(x)) is NOT the same as g(f(x))!\n\nInverse Functions:\nIf f(x) = 2x + 3, then f-inverse(x) = (x - 3)/2\nCheck: f(f-inverse(7)) = 2((7-3)/2) + 3 = 2(2) + 3 = 7"),
        q("coremath-m4t5-s4", "Given f(x) = 2x + 1 and g(x) = x-squared,\n\nWhat is f(g(3))?",
          "f(g(3)) = ?", ["19", "13", "7", "36"], 0,
          "g(3) = 3-squared = 9. f(g(3)) = f(9) = 2(9) + 1 = 18 + 1 = 19."),
    ]),
]

# ═══════════════════════════════════════════════════════════════════════
#  MODULE 5: Angles & Pythagorean Theorem (5 Topics)
# ═══════════════════════════════════════════════════════════════════════
MODULE5 = [
    L("coremath-m5t1", "Angle Properties and Geometry",
      "Core Mathematics", "1d522", "Both", 2, 8, 20, "core-maths", ["coremath-m1t1"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m5t1-s1",
          "Angles are measured in degrees (degrees).\n\nTypes of Angles:\nAcute: 0 to 90 degrees\nRight: 90 degrees\nObtuse: 90 to 180 degrees\nStraight line: 180 degrees\nReflex: 180 to 360 degrees\n\nAngle Properties on a Straight Line:\nAngles on a straight line add to 180 degrees.\n\nAngles at a Point:\nAngles around a point add to 360 degrees.\n\nVertically Opposite Angles:\nWhen two lines cross, opposite angles are equal.\n\nComplementary: Two angles that add to 90 degrees.\nSupplementary: Two angles that add to 180 degrees."),
        p("coremath-m5t1-s2", "Two angles on a straight line are x and 110 degrees.\n\nWhat is the value of x?",
          "x + 110 = 180", "x = ?", ["70", "60", "80", "90"], 0,
          "Angles on a straight line add to 180 degrees. x + 110 = 180, x = 70 degrees."),
        i("coremath-m5t1-s3",
          "Parallel Lines and Transversals - WASSCE Favourite!\n\nWhen a transversal crosses parallel lines:\n\nCorresponding Angles (F-pattern): Equal\nAlternate Angles (Z-pattern): Equal\nCo-interior Angles (C-pattern): Add to 180 degrees\n\nExample:\nIf two parallel lines are cut by a transversal, and one angle is 65 degrees:\n- Corresponding angle = 65 degrees\n- Alternate angle = 65 degrees\n- Co-interior with 65 = 180 - 65 = 115 degrees\n\nWASSCE often gives a diagram with parallel lines and asks to find all the missing angles!"),
        q("coremath-m5t1-s4", "Two parallel lines are cut by a transversal. One co-interior angle is 75 degrees.\n\nWhat is the other co-interior angle?",
          "Co-interior angles add to ?", 
          ["75", "105", "15", "90"], 1,
          "Co-interior angles add to 180 degrees. 180 - 75 = 105 degrees."),
    ]),
    L("coremath-m5t2", "Triangles and Polygons",
      "Core Mathematics", "1d522", "Both", 2, 10, 25, "core-maths", ["coremath-m5t1"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m5t2-s1",
          "Triangles - WASSCE Essential!\n\nSum of angles in a triangle = 180 degrees.\n\nTypes of Triangles:\nEquilateral: All sides equal, all angles 60 degrees\nIsosceles: Two sides equal, base angles equal\nScalene: No sides equal, no angles equal\nRight-angled: One angle = 90 degrees\n\nExterior Angle: The exterior angle of a triangle equals the sum of the two opposite interior angles.\n\nExample: If two interior angles are 50 and 70, the exterior angle at the third vertex = 50 + 70 = 120 degrees."),
        p("coremath-m5t2-s2", "A triangle has angles 2x, 3x, and x.\n\nWhat is the value of x?",
          "2x + 3x + x = 180", "x = ?", ["30", "36", "20", "45"], 0,
          "2x + 3x + x = 180. 6x = 180. x = 30. The angles are 60, 90, and 30 degrees."),
        i("coremath-m5t2-s3",
          "Polygons - WASSCE Favourite!\n\nA polygon is a closed shape with straight sides.\n\nSum of Interior Angles = (n - 2) x 180 degrees, where n = number of sides\n\nTriangle (3): (3-2) x 180 = 180 degrees\nQuadrilateral (4): (4-2) x 180 = 360 degrees\nPentagon (5): (5-2) x 180 = 540 degrees\nHexagon (6): (6-2) x 180 = 720 degrees\n\nRegular Polygon: All sides equal, all angles equal.\nEach interior angle = (n-2) x 180 / n\nEach exterior angle = 360 / n\n\nNote: Sum of exterior angles of ANY polygon = 360 degrees!"),
        q("coremath-m5t2-s4", "What is each interior angle of a regular pentagon?",
          "Pentagon: n = 5", 
          ["72", "108", "120", "90"], 1,
          "Interior angle = (n-2) x 180 / n = 3 x 180 / 5 = 540/5 = 108 degrees."),
    ]),
    L("coremath-m5t3", "Pythagorean Theorem",
      "Core Mathematics", "1d522", "Both", 2, 10, 25, "core-maths", ["coremath-m5t2"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m5t3-s1",
          "Pythagorean Theorem applies to right-angled triangles.\n\nIn a right-angled triangle with sides a, b and hypotenuse c (longest side):\na-squared + b-squared = c-squared\n\nThe hypotenuse is always opposite the right angle (90 degrees).\n\nExample: Find c if a = 3, b = 4.\n3-squared + 4-squared = c-squared\n9 + 16 = c-squared\n25 = c-squared\nc = 5\n\nThis is the famous 3-4-5 triangle!\n\nCommon Pythagorean triples: 3-4-5, 5-12-13, 8-15-17, 7-24-25"),
        p("coremath-m5t3-s2", "A right-angled triangle has sides 6 and 8.\n\nWhat is the hypotenuse?",
          "6-squared + 8-squared = ?", "Hypotenuse = ?",
          ["10", "14", "12", "9"], 0,
          "c-squared = 36 + 64 = 100. c = 10. This is a 3-4-5 triangle scaled by 2 (6-8-10)."),
        i("coremath-m5t3-s3",
          "Finding a Shorter Side\n\nIf you know the hypotenuse and one side, rearrange:\na-squared = c-squared - b-squared\n\nExample: Find a if c = 13 and b = 5.\na-squared = 169 - 25 = 144\na = 12\n\nApplications of Pythagoras (WASSCE Essential!):\n\n1. Finding the diagonal of a rectangle.\nDiagonal-squared = length-squared + width-squared\n\n2. Checking if a triangle is right-angled.\nIf a-squared + b-squared = c-squared, it is a right-angled triangle.\n\n3. Distance between two points:\nd = sqrt((x2-x1)-squared + (y2-y1)-squared)\n\n4. Finding the height of an isosceles triangle.\nThe altitude splits the base in half, creating two right triangles."),
        q("coremath-m5t3-s4", "A right-angled triangle has hypotenuse 17 and one side 15.\n\nWhat is the other side?",
          "17-squared - 15-squared = ?", 
          ["8", "9", "6", "10"], 0,
          "a-squared = 289 - 225 = 64. a = 8. This is the 8-15-17 Pythagorean triple."),
    ]),
    L("coremath-m5t4", "Similarity and Congruence",
      "Core Mathematics", "1d522", "Both", 2, 10, 25, "core-maths", ["coremath-m5t2"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m5t4-s1",
          "Congruent shapes are IDENTICAL in size and shape.\n\nConditions for Congruence (SSS, SAS, ASA, RHS):\nSSS: All three sides equal\nSAS: Two sides and included angle equal\nASA: Two angles and included side equal\nRHS: Right angle, hypotenuse, and one side equal\n\nCongruent triangles have:\n- Same side lengths\n- Same angles\n- Same area\n\nSimilar shapes have the SAME SHAPE but DIFFERENT SIZE.\n\nCorresponding angles are equal\nCorresponding sides are in the same ratio (scale factor)\n\nIf triangle ABC is similar to triangle DEF:\nAB/DE = BC/EF = AC/DF = scale factor"),
        p("coremath-m5t4-s2", "Two triangles have angles: 40, 60, 80 and 40, 60, 80.\n\nAre they congruent, similar, or both?",
          "Same angles but different side lengths?", "What is the relationship?",
          ["Congruent only", "Similar only", "Both congruent and similar", "Neither"], 1,
          "Same angles means the shapes are similar (same shape). But without knowing side lengths, we cannot say they are congruent (same size)."),
        i("coremath-m5t4-s3",
          "Working with Similar Triangles - WASSCE Classic!\n\nTo find unknown lengths in similar triangles:\n1. Identify corresponding sides\n2. Find the scale factor\n3. Multiply/divide to find missing lengths\n\nExample: Triangle ABC ~ Triangle DEF\nAB = 4, BC = 6, DE = 6. Find EF.\nScale factor = 6/4 = 1.5\nEF = BC x 1.5 = 6 x 1.5 = 9\n\nAreas of Similar Shapes:\nIf scale factor = k:\nArea ratio = k-squared\nVolume ratio = k-cubed\n\nExample: If a triangle has sides twice another, its area is 4 times larger (2-squared)."),
        q("coremath-m5t4-s4", "A triangle has sides 3, 4, 5. A similar triangle has shortest side 9.\n\nWhat is the scale factor?",
          "Scale factor = 9/3", 
          ["2", "3", "6", "1/3"], 1,
          "The shortest sides correspond. 9/3 = 3. The scale factor is 3. The larger triangle sides are 9, 12, 15."),
    ]),
    L("coremath-m5t5", "Circle Theorems",
      "Core Mathematics", "1d522", "Both", 3, 12, 30, "core-maths", ["coremath-m5t2"], ["SHS 2", "SHS 3"], "SHS 2", [
        i("coremath-m5t5-s1",
          "Circle Theorems - Key Rules for WASSCE!\n\nParts of a Circle:\nCentre, radius, diameter, chord, arc, sector, segment, tangent\n\nTheorem 1: The angle at the centre is twice the angle at the circumference (when both subtend the same arc).\n\nTheorem 2: Angles in the same segment are equal.\n\nTheorem 3: The angle in a semicircle is 90 degrees.\n\nTheorem 4: The angle between a tangent and a radius at the point of contact is 90 degrees.\n\nTheorem 5: The angle between a tangent and a chord equals the angle in the alternate segment.\n\nWASSCE Tip: These theorems are tested EVERY YEAR!"),
        p("coremath-m5t5-s2", "An angle at the centre of a circle is 120 degrees.\n\nWhat is the angle at the circumference subtended by the same arc?",
          "Centre angle = 2 x circumference angle", "Circumference angle = ?",
          ["60", "120", "240", "30"], 0,
          "The angle at the centre is twice the angle at the circumference. 120/2 = 60 degrees."),
        i("coremath-m5t5-s3",
          "More Circle Theorems - Memorise These!\n\nTheorem 6: Opposite angles of a cyclic quadrilateral add to 180 degrees.\n\nProof: If a + c = 180 and b + d = 180, the quadrilateral is cyclic.\n\nTheorem 7: Tangents from the same external point are equal in length.\n\nTheorem 8: The line from the centre to the midpoint of a chord is perpendicular to the chord.\n\nTypical WASSCE question:\nIn a circle with centre O, AB is a chord of length 10 cm. The distance from O to AB is 12 cm. Find the radius.\n\nSolution: The line from O to the midpoint M of AB is perpendicular.\nAM = 5 cm, OM = 12 cm.\nBy Pythagoras: OA-squared = 5-squared + 12-squared = 25 + 144 = 169\nOA = 13 cm (the radius)"),
        q("coremath-m5t5-s4", "In a cyclic quadrilateral, angle A = 75 degrees.\n\nWhat is angle C (the opposite angle)?",
          "Opposite angles in cyclic quadrilateral add to 180", 
          ["75", "105", "15", "95"], 1,
          "Opposite angles of a cyclic quadrilateral add to 180 degrees. 180 - 75 = 105 degrees."),
    ]),
]

# ═══════════════════════════════════════════════════════════════════════
#  MODULE 6: Vectors & Trigonometry (5 Topics)
# ═══════════════════════════════════════════════════════════════════════
MODULE6 = [
    L("coremath-m6t1", "Introduction to Vectors",
      "Core Mathematics", "1d522", "Both", 2, 8, 20, "core-maths", ["coremath-m4t1"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m6t1-s1",
          "Vectors have both magnitude (size) and direction.\n\nScalars have only magnitude (e.g. speed, mass, time).\nVectors have magnitude and direction (e.g. velocity, force, displacement).\n\nRepresenting Vectors:\nAB (arrow above) = vector from A to B\nOr as column vector: (x-component, y-component)\nOr as: xi + yj where i is unit in x-direction, j in y-direction\n\nMagnitude of a vector:\n|a| = sqrt(x-squared + y-squared)\n\nExample: |3i + 4j| = sqrt(9 + 16) = sqrt(25) = 5\n\nWASSCE Tip: The magnitude is always positive!"),
        p("coremath-m6t1-s2", "A vector v = 6i + 8j.\n\nWhat is its magnitude?",
          "|6i + 8j| = sqrt(36 + 64)", "Magnitude = ?",
          ["10", "14", "100", "48"], 0,
          "|v| = sqrt(6-squared + 8-squared) = sqrt(36 + 64) = sqrt(100) = 10. A 3-4-5 triangle scaled by 2!"),
        i("coremath-m6t1-s3",
          "Vector Operations\n\nAddition: Add corresponding components.\na = 2i + 3j, b = 4i - j\na + b = (2+4)i + (3-1)j = 6i + 2j\n\nSubtraction: Subtract corresponding components.\na - b = (2-4)i + (3-(-1))j = -2i + 4j\n\nScalar Multiplication: Multiply each component.\n3a = 3(2i + 3j) = 6i + 9j\n\nNegative Vector: Same magnitude, opposite direction.\n-a = -2i - 3j\n\nPosition Vectors:\nThe position of point A relative to origin O = OA = a\nAB = OB - OA = b - a (vector from A to B)"),
        q("coremath-m6t1-s4", "If a = 2i + 5j and b = 4i - j,\n\nwhat is a + b?",
          "a + b = ?", ["6i + 4j", "6i - 4j", "8i + 5j", "2i + 6j"], 0,
          "a + b = (2+4)i + (5-1)j = 6i + 4j."),
    ]),
    L("coremath-m6t2", "Vector Applications and Bearings",
      "Core Mathematics", "1d522", "Both", 2, 10, 25, "core-maths", ["coremath-m6t1"], ["SHS 2", "SHS 3"], "SHS 2", [
        i("coremath-m6t2-s1",
          "Bearings describe direction using angles measured clockwise from North.\n\nBearings are always:\n1. Measured from North (0 degrees)\n2. Clockwise\n3. Written as three digits (e.g. 045, 120, 270)\n\nExamples:\nEast = 090 degrees\nSouth = 180 degrees\nWest = 270 degrees\nNorth = 000 or 360 degrees\n\nConverting Bearing to Vector:\nBearing theta: components are:\nx = d x sin(theta) (East component)\ny = d x cos(theta) (North component)\n\nExample: 5 km on bearing 060\nEast = 5 x sin(60) = 5 x 0.866 = 4.33 km\nNorth = 5 x cos(60) = 5 x 0.5 = 2.5 km"),
        p("coremath-m6t2-s2", "A ship sails 10 km on a bearing of 030.\n\nWhat is the north component?",
          "North = 10 x cos(30)", "North component = ?",
          ["5", "8.66", "10", "15"], 1,
          "cos(30) = 0.866. North = 10 x 0.866 = 8.66 km. East = 10 x sin(30) = 10 x 0.5 = 5 km."),
        i("coremath-m6t2-s3",
          "Resultant Vectors and Displacement\n\nTo find the resultant of two or more vectors:\n1. Add all x-components\n2. Add all y-components\n3. Resultant = (sum x)i + (sum y)j\n\nExample: A plane flies 100 km east then 50 km north.\nTotal x = 100, total y = 50\nResultant = 100i + 50j\nMagnitude = sqrt(10000 + 2500) = sqrt(12500) = 111.8 km\n\nBearing of Resultant:\ntheta = arctan(x/y) or arctan(y/x) depending on quadrant\n\nFor the plane above:\ntheta = arctan(50/100) = arctan(0.5) = 26.6 degrees\nBearing = 026.6 (measured from North clockwise)\n\nWASSCE loves resultant vector problems with bearings!"),
        q("coremath-m6t2-s4", "A car travels 40 km east then 30 km north.\n\nWhat is the distance from the starting point?",
          "Resultant magnitude = ?", 
          ["70 km", "50 km", "35 km", "120 km"], 1,
          "x = 40, y = 30. Magnitude = sqrt(40-squared + 30-squared) = sqrt(1600 + 900) = sqrt(2500) = 50 km. A 3-4-5 triangle scaled by 10!"),
    ]),
    L("coremath-m6t3", "Trigonometric Ratios",
      "Core Mathematics", "1d522", "Both", 2, 10, 25, "core-maths", ["coremath-m5t3"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m6t3-s1",
          "Trigonometry deals with relationships between sides and angles of triangles.\n\nFor a right-angled triangle with angle theta:\n\nSOH CAH TOA - Memorise This!\n\nsin(theta) = Opposite / Hypotenuse\ncos(theta) = Adjacent / Hypotenuse\ntan(theta) = Opposite / Adjacent\n\nExample: Right triangle with opposite = 3, adjacent = 4, hypotenuse = 5.\nsin(theta) = 3/5 = 0.6\ncos(theta) = 4/5 = 0.8\ntan(theta) = 3/4 = 0.75\n\nWASSCE Essential: Know SOH CAH TOA by heart!"),
        p("coremath-m6t3-s2", "In a right triangle, the side opposite angle A is 8 and the hypotenuse is 10.\n\nWhat is sin(A)?",
          "sin = opposite/hypotenuse", "sin(A) = ?",
          ["0.8", "0.6", "1.25", "10/8"], 0,
          "sin(A) = opposite/hypotenuse = 8/10 = 0.8. The adjacent side is 6 (6-8-10 triangle)."),
        i("coremath-m6t3-s3",
          "Finding Unknown Sides and Angles\n\nTo find a side:\nIdentify which sides you know and which you need. Choose the appropriate trig ratio.\n\nExample: Find x (opposite) if angle = 30 and hypotenuse = 10.\nsin(30) = x/10\n0.5 = x/10\nx = 5\n\nTo find an angle:\nUse inverse trig functions: sin-inverse, cos-inverse, tan-inverse\n\nExample: Find angle A if tan(A) = 0.75.\nA = tan-inverse(0.75) = 36.9 degrees\n\nSpecial Angles - Memorise These!\n\nsin(0)=0, sin(30)=0.5, sin(45)=0.707, sin(60)=0.866, sin(90)=1\ncos(0)=1, cos(30)=0.866, cos(45)=0.707, cos(60)=0.5, cos(90)=0\ntan(0)=0, tan(30)=0.577, tan(45)=1, tan(60)=1.732, tan(90)=undefined"),
        q("coremath-m6t3-s4", "In a right triangle, the opposite side is 5 and adjacent is 12.\n\nWhat is the angle theta?",
          "tan(theta) = 5/12", 
          ["22.6", "67.4", "11.3", "45.0"], 0,
          "tan(theta) = 5/12 = 0.4167. theta = tan-inverse(0.4167) = 22.6 degrees. The hypotenuse = 13 (5-12-13 triangle)."),
    ]),
    L("coremath-m6t4", "Applications of Trigonometry",
      "Core Mathematics", "1d522", "Both", 3, 12, 30, "core-maths", ["coremath-m6t3"], ["SHS 2", "SHS 3"], "SHS 2", [
        i("coremath-m6t4-s1",
          "Angle of Elevation and Depression - WASSCE Classic!\n\nAngle of Elevation: The angle between the horizontal and the line of sight when looking UP at an object.\n\nAngle of Depression: The angle between the horizontal and the line of sight when looking DOWN at an object.\n\nThe angle of elevation from point A to object B equals the angle of depression from B to A.\n\nExample: A student standing 20 m from a tree looks up at an angle of 40 degrees to see the top.\nHeight of tree = 20 x tan(40) = 20 x 0.839 = 16.78 m"),
        p("coremath-m6t4-s2", "The angle of elevation to the top of a building is 30 degrees when standing 50 m away.\n\nWhat is the height of the building?",
          "tan(30) = height/50", "Height = ?",
          ["28.9 m", "43.3 m", "57.7 m", "25 m"], 0,
          "tan(30) = 0.577. height = 50 x 0.577 = 28.9 m."),
        i("coremath-m6t4-s3",
          "The Sine Rule and Cosine Rule - WASSCE Essential!\n\nFor any triangle (not just right-angled):\n\nSine Rule: a/sin(A) = b/sin(B) = c/sin(C) = 2R\n(Use when you know two angles and one side, or two sides and a non-included angle)\n\nExample: Triangle has angle A=40, angle B=60, side a=10. Find side b.\nb/sin(60) = 10/sin(40)\nb = 10 x sin(60)/sin(40) = 10 x 0.866/0.643 = 13.47\n\nCosine Rule: a-squared = b-squared + c-squared - 2bc x cos(A)\n(Use when you know two sides and the included angle, or three sides)\n\nExample: Triangle has sides b=5, c=8, angle A=60. Find side a.\na-squared = 25 + 64 - 2(5)(8) x cos(60)\n= 89 - 80 x 0.5 = 89 - 40 = 49\na = 7"),
        q("coremath-m6t4-s4", "In a triangle, angle A = 50, angle B = 70, and side a = 8.\n\nWhat is side b?",
          "b = a x sin(B)/sin(A)", 
          ["9.8", "6.5", "7.2", "10.3"], 0,
          "Angle C = 180 - 50 - 70 = 60. Using sine rule: b = 8 x sin(70)/sin(50) = 8 x 0.94/0.766 = 9.8."),
    ]),
    L("coremath-m6t5", "Area of Triangles and Bearings",
      "Core Mathematics", "1d522", "Both", 3, 10, 25, "core-maths", ["coremath-m6t4"], ["SHS 2", "SHS 3"], "SHS 2", [
        i("coremath-m6t5-s1",
          "Area of a Triangle using Trigonometry\n\nFormula: Area = 1/2 x a x b x sin(C)\nWhere C is the angle between sides a and b.\n\nExample: Triangle with sides 6 and 8 and included angle 30 degrees.\nArea = 1/2 x 6 x 8 x sin(30)\n= 24 x 0.5 = 12 square units\n\nThis formula works for ANY triangle where you know two sides and the included angle.\n\nWASSCE classic: Finding area using sine rule."),
        p("coremath-m6t5-s2", "A triangle has sides 10 and 14 with an included angle of 60 degrees.\n\nWhat is the area?",
          "Area = 1/2 x 10 x 14 x sin(60)", "Area = ?",
          ["70", "60.6", "35", "121.2"], 1,
          "sin(60) = 0.866. Area = 0.5 x 10 x 14 x 0.866 = 60.6 square units."),
        i("coremath-m6t5-s3",
          "Three-Figure Bearings and Navigation\n\nThree-figure bearings are always written with three digits.\n\nTo find the bearing from A to B:\n1. Draw a north line at A\n2. Measure the angle clockwise from north to AB\n3. Write as three digits\n\nBack Bearing (from B to A) = Bearing from A to B + 180 degrees (if < 180) or - 180 (if > 180)\n\nExample: Bearing from A to B = 050\nBack bearing = 050 + 180 = 230\n\nCombined Bearings Problem:\nShip A sails 30 km on bearing 040. Ship B sails 20 km on bearing 130. Find the distance between them.\n\nSolution: Draw both journeys from the same point, then use cosine rule.\nAngle between them = 130 - 40 = 90 degrees!\nDistance = sqrt(30-squared + 20-squared) = sqrt(1300) = 36.1 km"),
        q("coremath-m6t5-s4", "The bearing from P to Q is 040.\n\nWhat is the back bearing from Q to P?",
          "Back bearing = 040 + 180", 
          ["220", "040", "140", "320"], 0,
          "Back bearing = forward bearing + 180 = 040 + 180 = 220 degrees."),
    ]),
]

# ═══════════════════════════════════════════════════════════════════════
#  MODULE 7: Perimeter, Area & Volume (5 Topics)
# ═══════════════════════════════════════════════════════════════════════
MODULE7 = [
    L("coremath-m7t1", "Perimeter of Plane Shapes",
      "Core Mathematics", "1d522", "Both", 1, 8, 20, "core-maths", ["coremath-m1t1"], ["SHS 1"], "SHS 1", [
        i("coremath-m7t1-s1",
          "Perimeter is the total distance around the outside of a shape.\n\nSquare: P = 4s (s = side length)\nRectangle: P = 2(l + w) (l = length, w = width)\nTriangle: P = a + b + c (sum of three sides)\nCircle: P = 2 x pi x r (circumference)\n\nExample: A rectangle has length 8 cm and width 5 cm.\nPerimeter = 2(8 + 5) = 2 x 13 = 26 cm\n\nArc Length (part of circle):\nArc length = (theta/360) x 2 x pi x r\nwhere theta is the angle at the centre.\n\nExample: Sector with radius 10 cm and angle 60 degrees.\nArc length = (60/360) x 2 x pi x 10 = (1/6) x 62.83 = 10.47 cm"),
        p("coremath-m7t1-s2", "A rectangle has perimeter 30 cm and length 9 cm.\n\nWhat is the width?",
          "2(9 + w) = 30", "Width = ?", ["6 cm", "21 cm", "3.33 cm", "7.5 cm"], 0,
          "2(9 + w) = 30. 9 + w = 15. w = 6 cm."),
        i("coremath-m7t1-s3",
          "Composite Shapes - WASSCE Favourite!\n\nTo find the perimeter of a composite shape:\n1. Add all the outside edges\n2. Do NOT count interior edges\n\nExample: A rectangle (6 x 4) with a semicircle on one end.\nThree sides of rectangle = 6 + 4 + 6 = 16\nSemicircle arc = pi x 2 = 6.28 (half the circumference of a circle with radius 2)\nTotal perimeter = 16 + 6.28 = 22.28\n\nSquare: P = 4s\nRectangle: P = 2(l + w)\nTriangle: P = a + b + c\nCircle: C = 2 x pi x r\nSector: P = 2r + arc length"),
        q("coremath-m7t1-s4", "The circumference of a circle is 44 cm. What is the radius? (Use pi = 22/7)",
          "2 x (22/7) x r = 44", 
          ["7 cm", "14 cm", "3.5 cm", "10 cm"], 0,
          "2 x 22/7 x r = 44. 44/7 x r = 44. r = 44 x 7/44 = 7 cm."),
    ]),
    L("coremath-m7t2", "Area of Plane Shapes",
      "Core Mathematics", "1d522", "Both", 1, 10, 25, "core-maths", ["coremath-m7t1"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m7t2-s1",
          "Area measures the space inside a 2D shape. Measured in square units.\n\nKey Formulas (WASSCE Essential!):\n\nSquare: A = s-squared\nRectangle: A = l x w\nTriangle: A = 1/2 x b x h\nParallelogram: A = b x h\nTrapezium: A = 1/2 x (a + b) x h\nCircle: A = pi x r-squared\n\nExample: Triangle with base 8 cm and height 6 cm.\nArea = 1/2 x 8 x 6 = 24 cm-squared\n\nExample: Circle with radius 7 cm.\nArea = pi x 49 = 153.94 cm-squared (using pi = 3.142)\nOr: 22/7 x 49 = 154 cm-squared"),
        p("coremath-m7t2-s2", "A trapezium has parallel sides 8 cm and 12 cm with height 5 cm.\n\nWhat is its area?",
          "Area = 1/2(8+12) x 5", "Area = ?",
          ["50 cm-squared", "100 cm-squared", "40 cm-squared", "25 cm-squared"], 0,
          "Area = 1/2 x 20 x 5 = 50 cm-squared."),
        i("coremath-m7t2-s3",
          "Area of Composite Shapes - WASSCE Classic!\n\nDivide the shape into simpler parts, find each area, then add.\n\nExample: An L-shape can be divided into two rectangles.\n\nSector of a Circle:\nArea = (theta/360) x pi x r-squared\n\nExample: Sector radius 6 cm, angle 60 degrees.\nArea = (60/360) x pi x 36 = (1/6) x 113.1 = 18.85 cm-squared\n\nAnnulus (ring):\nArea = pi x (R-squared - r-squared) where R = outer radius, r = inner radius\n\nExample: Outer radius 5 cm, inner radius 3 cm.\nArea = pi x (25 - 9) = pi x 16 = 50.27 cm-squared"),
        q("coremath-m7t2-s4", "Find the area of a circle with diameter 14 cm. (Use pi = 22/7)",
          "r = 7 cm, A = pi x 49", 
          ["44 cm-squared", "154 cm-squared", "616 cm-squared", "22 cm-squared"], 1,
          "Radius = 7 cm. Area = 22/7 x 49 = 22 x 7 = 154 cm-squared."),
    ]),
    L("coremath-m7t3", "Surface Area of Solids",
      "Core Mathematics", "1d522", "Both", 2, 10, 25, "core-maths", ["coremath-m7t2"], ["SHS 2", "SHS 3"], "SHS 2", [
        i("coremath-m7t3-s1",
          "Surface Area is the total area of all faces of a 3D solid.\n\nCube: SA = 6s-squared (6 faces, each s-squared)\nCuboid: SA = 2(lw + lh + wh)\n\nExample: Cuboid with l=5, w=3, h=4.\nSA = 2(5x3 + 5x4 + 3x4) = 2(15 + 20 + 12) = 2 x 47 = 94 units-squared\n\nCylinder (closed): SA = 2 x pi x r-squared + 2 x pi x r x h\n= 2 x pi x r x (r + h)\n\nExample: Cylinder radius 3, height 10.\nSA = 2 x pi x 3(3+10) = 6 x pi x 13 = 78 x pi = 245.04 units-squared\n\nWASSCE may ask for 'total surface area' (including ends) or 'curved surface area' (excluding ends)."),
        p("coremath-m7t3-s2", "A cube has side length 5 cm.\n\nWhat is its total surface area?",
          "SA = 6 x 5-squared", "Surface area = ?",
          ["150 cm-squared", "125 cm-squared", "25 cm-squared", "100 cm-squared"], 0,
          "SA = 6 x 25 = 150 cm-squared."),
        i("coremath-m7t3-s3",
          "Surface Area Formulas - WASSCE Essential!\n\nSphere: SA = 4 x pi x r-squared\nHemisphere: SA = 2 x pi x r-squared + pi x r-squared = 3 x pi x r-squared (including base)\n\nCone: SA = pi x r x l + pi x r-squared (where l = slant height)\nCurved surface area of cone = pi x r x l\n\nExample: Cone radius 3 cm, slant height 5 cm.\nCurved SA = pi x 3 x 5 = 15 x pi = 47.12 cm-squared\nBase SA = pi x 9 = 28.27 cm-squared\nTotal SA = 47.12 + 28.27 = 75.39 cm-squared\n\nSquare-based Pyramid:\nSA = area of base + 4 x area of triangular faces\nEach triangular face: A = 1/2 x base x slant height"),
        q("coremath-m7t3-s4", "A sphere has radius 7 cm. What is its surface area? (Use pi = 22/7)",
          "SA = 4 x (22/7) x 49", 
          ["154 cm-squared", "308 cm-squared", "616 cm-squared", "88 cm-squared"], 2,
          "SA = 4 x 22/7 x 49 = 4 x 22 x 7 = 616 cm-squared."),
    ]),
    L("coremath-m7t4", "Volume of Solids",
      "Core Mathematics", "1d522", "Both", 2, 10, 25, "core-maths", ["coremath-m7t2"], ["SHS 2", "SHS 3"], "SHS 2", [
        i("coremath-m7t4-s1",
          "Volume measures the space inside a 3D solid. Measured in cubic units.\n\nKey Formulas (WASSCE Essential!):\n\nCube: V = s-cubed\nCuboid: V = l x w x h\nPrism: V = Area of base x height\nCylinder: V = pi x r-squared x h\n\nExample: Cuboid 5 cm x 3 cm x 4 cm.\nV = 5 x 3 x 4 = 60 cm-cubed\n\nExample: Cylinder radius 3 cm, height 10 cm.\nV = pi x 9 x 10 = 90 x pi = 282.74 cm-cubed\n\nSphere: V = 4/3 x pi x r-cubed\nCone: V = 1/3 x pi x r-squared x h\nPyramid: V = 1/3 x Area of base x height"),
        p("coremath-m7t4-s2", "A cylinder has radius 7 cm and height 10 cm. (Use pi = 22/7)\n\nWhat is its volume?",
          "V = (22/7) x 49 x 10", "Volume = ?",
          ["1540 cm-cubed", "770 cm-cubed", "3080 cm-cubed", "440 cm-cubed"], 0,
          "V = 22/7 x 49 x 10 = 22 x 7 x 10 = 1540 cm-cubed."),
        i("coremath-m7t4-s3",
          "Volume of Cones and Spheres - WASSCE Favourite!\n\nCone: V = 1/3 x pi x r-squared x h\nExample: Cone radius 3 cm, height 4 cm.\nV = 1/3 x pi x 9 x 4 = 12 x pi = 37.7 cm-cubed\n\nSphere: V = 4/3 x pi x r-cubed\nExample: Sphere radius 6 cm.\nV = 4/3 x pi x 216 = 288 x pi = 904.78 cm-cubed\n\nHemisphere: V = 2/3 x pi x r-cubed\n\nSquare-Based Pyramid: V = 1/3 x base-area x height\nExample: Base 6 cm, height 10 cm.\nV = 1/3 x 36 x 10 = 120 cm-cubed\n\nCapacity and Volume Conversions:\n1 litre = 1000 cm-cubed = 1000 mL\n1 m-cubed = 1,000,000 cm-cubed = 1000 litres"),
        q("coremath-m7t4-s4", "A cone has radius 6 cm and height 10 cm.\n\nWhat is its volume? (Use pi = 3.142)",
          "V = 1/3 x pi x 36 x 10", 
          ["377.04 cm-cubed", "1131.12 cm-cubed", "753.6 cm-cubed", "1885.2 cm-cubed"], 0,
          "V = 1/3 x 3.142 x 360 = 3.142 x 120 = 377.04 cm-cubed."),
    ]),
    L("coremath-m7t5", "Composite Shapes and Practical Problems",
      "Core Mathematics", "1d522", "Both", 3, 12, 30, "core-maths", ["coremath-m7t4"], ["SHS 2", "SHS 3"], "SHS 2", [
        i("coremath-m7t5-s1",
          "Composite solids combine two or more basic shapes.\n\nTo find volume of composite solids:\n1. Identify the basic shapes that make up the solid\n2. Find the volume of each part\n3. Add or subtract as needed\n\nExample: A cylinder with a hemisphere on top.\nTotal volume = volume of cylinder + volume of hemisphere\n\nExample: Cylinder radius 3 cm, height 8 cm, hemisphere radius 3 cm on top.\nCylinder: V = pi x 9 x 8 = 72 x pi\nHemisphere: V = 2/3 x pi x 27 = 18 x pi\nTotal = 90 x pi = 282.74 cm-cubed\n\nDensity:\nDensity = Mass/Volume\nMass = Density x Volume"),
        p("coremath-m7t5-s2", "A cuboid tank measures 2 m x 1.5 m x 1 m.\n\nHow many litres of water can it hold? (1 m-cubed = 1000 litres)",
          "Volume = 2 x 1.5 x 1 = 3 m-cubed", "Capacity = ?",
          ["3000 litres", "300 litres", "30,000 litres", "300,000 litres"], 0,
          "Volume = 3 m-cubed. Capacity = 3 x 1000 = 3000 litres."),
        i("coremath-m7t5-s3",
          "Practical Problems - WASSCE Favourites!\n\nScale Drawing and Area:\nIf a scale drawing uses scale 1:100, then:\nLength scale factor = 100\nArea scale factor = 100-squared = 10,000\nVolume scale factor = 100-cubed = 1,000,000\n\nExample: A rectangular room is 5 cm x 3 cm on a 1:100 plan.\nActual length = 5 x 100 = 500 cm = 5 m\nActual area = 5 x 3 x 10000 = 150,000 cm-squared = 15 m-squared\n\nRate of Flow:\nIf water flows at r cm-cubed per second into a tank of volume V cm-cubed:\nTime to fill = V/r seconds\n\nExample: Tank 200 litres, tap flows at 5 litres per minute.\nTime = 200/5 = 40 minutes"),
        q("coremath-m7t5-s4", "A rectangular tank is 40 cm long, 30 cm wide, and 20 cm high. Water flows in at 2 litres per minute.\n\nHow long to fill the tank? (1000 cm-cubed = 1 litre)",
          "Volume = 40 x 30 x 20 = 24000 cm-cubed = 24 litres", 
          ["12 minutes", "20 minutes", "8 minutes", "24 minutes"], 0,
          "Volume = 24000 cm-cubed = 24 litres. Time = 24/2 = 12 minutes."),
    ]),
]

# ═══════════════════════════════════════════════════════════════════════
#  MODULE 8: Data Organisation & Analysis (5 Topics)
# ═══════════════════════════════════════════════════════════════════════
MODULE8 = [
    L("coremath-m8t1", "Data Collection and Presentation",
      "Core Mathematics", "1d522", "Both", 1, 8, 20, "core-maths", [], ["SHS 1"], "SHS 1", [
        i("coremath-m8t1-s1",
          "Statistics is the science of collecting, organising, and interpreting data.\n\nTypes of Data:\n\nQualitative (Categorical): Describes qualities or categories\n- Gender, colour, subject studied, favourite food\n\nQuantitative (Numerical): Can be measured or counted\n- Discrete: Countable values (e.g. number of students, shoe size)\n- Continuous: Can take any value in a range (e.g. height, weight, time)\n\nData Collection Methods:\n1. Surveys and questionnaires\n2. Experiments\n3. Observations\n4. Existing records / secondary data\n5. Census (everyone) vs Sample (representative group)\n\nWASSCE Tip: Be ready to identify types of data and suggest collection methods!"),
        p("coremath-m8t1-s2", "A researcher asks students their favourite subject. What type of data is this?",
          "Favourite subject = ?", "What type of data?",
          ["Quantitative discrete", "Qualitative", "Quantitative continuous", "Ordinal"], 1,
          "Favourite subject is a category - it is qualitative (categorical) data."),
        i("coremath-m8t1-s3",
          "Organising Data - Frequency Tables\n\nA frequency table shows how many times each value occurs.\n\nExample: Scores of 20 students in a test:\n5, 6, 7, 5, 8, 6, 7, 7, 5, 6, 8, 9, 6, 7, 5, 6, 7, 8, 6, 7\n\nScore | Tally    | Frequency\n5     | IIII     | 4\n6     | IIIII I  | 6\n7     | IIIII I  | 6\n8     | III      | 3\n9     | I        | 1\nTotal |          | 20\n\nTally marks: Groups of 5 (III = 3, IIII = 4, IIII = 5)\n\nGrouped Frequency Table:\nFor continuous data, group into classes.\ne.g. Heights (cm): 140-149, 150-159, 160-169, 170-179"),
        q("coremath-m8t1-s4", "A frequency table shows the number of siblings students have:\n0 siblings: 5 students, 1 sibling: 12, 2 siblings: 8, 3+ siblings: 3\n\nHow many students were surveyed?",
          "Total = ?", ["25", "28", "20", "33"], 1,
          "Total = 5 + 12 + 8 + 3 = 28 students."),
    ]),
    L("coremath-m8t2", "Measures of Central Tendency",
      "Core Mathematics", "1d522", "Both", 2, 10, 25, "core-maths", ["coremath-m8t1"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m8t2-s1",
          "Measures of central tendency describe the 'typical' or 'average' value in a dataset.\n\nMean: The arithmetic average.\nMean = Sum of all values / Number of values\n\nExample: 4, 6, 7, 9, 14\nMean = (4+6+7+9+14)/5 = 40/5 = 8\n\nMedian: The middle value when data is ordered.\nOdd number: Middle value (e.g. 5th of 9 values)\nEven number: Mean of the two middle values\n\nExample: 3, 7, 8, 12, 15: Median = 8 (3rd of 5)\nExample: 3, 7, 8, 12: Median = (7+8)/2 = 7.5\n\nMode: The most frequent value.\nExample: 2, 3, 3, 5, 7, 7, 7, 9: Mode = 7 (occurs 3 times)"),
        p("coremath-m8t2-s2", "Find the mean of: 5, 8, 12, 15, 20",
          "Mean = (5+8+12+15+20)/5", "Mean = ?", ["12", "15", "11", "14"], 0,
          "Sum = 60. Mean = 60/5 = 12."),
        i("coremath-m8t2-s3",
          "Choosing the Right Average - WASSCE Favourite!\n\nMean: Best when data has no extreme outliers. Uses all values.\nMedian: Best when data has outliers. Not affected by extreme values.\nMode: Best for categorical data or to find the most common value.\n\nExample: Salaries in a small company (thousands):\n20, 22, 25, 28, 30, 35, 200 (CEO)\n\nMean = 360/7 = 51.4 (not representative due to CEO's high salary)\nMedian = 28 (more representative!)\nMode = none (all different)\n\nCalculating Mean from a Frequency Table:\nMean = (Sum of (Value x Frequency))/Total Frequency\n\nExample: Scores x Frequency:\n5 x 4 = 20\n6 x 6 = 36\n7 x 6 = 42\nTotal = 98, Total frequency = 16\nMean = 98/16 = 6.125"),
        q("coremath-m8t2-s4", "Scores: 2, 3, 5, 5, 7, 8, 9, 10\n\nWhat is the median?",
          "Even number of values", 
          ["5", "6", "5.5", "7"], 1,
          "Ordered: 2, 3, 5, 5, 7, 8, 9, 10 (8 values). Middle two: 5 and 7. Median = (5+7)/2 = 6."),
    ]),
    L("coremath-m8t3", "Measures of Dispersion",
      "Core Mathematics", "1d522", "Both", 2, 10, 25, "core-maths", ["coremath-m8t2"], ["SHS 2", "SHS 3"], "SHS 2", [
        i("coremath-m8t3-s1",
          "Measures of dispersion describe how spread out the data is.\n\nRange = Highest value - Lowest value\nSimple but affected by outliers.\n\nExample: 4, 7, 8, 12, 15\nRange = 15 - 4 = 11\n\nInterquartile Range (IQR) = Q3 - Q1\nQ1 (Lower Quartile): Median of lower half of data\nQ3 (Upper Quartile): Median of upper half of data\nIQR is NOT affected by outliers.\n\nExample: 2, 4, 6, 8, 10, 12, 14, 16, 18\nQ1 = 5 (middle of 2,4,6,8 = 5)\nQ3 = 15 (middle of 12,14,16,18 = 15)\nIQR = 15 - 5 = 10"),
        p("coremath-m8t3-s2", "Data: 3, 7, 8, 11, 15, 18, 22\n\nWhat is the range?",
          "Range = Highest - Lowest", "Range = ?",
          ["19", "15", "22", "11"], 0,
          "Highest = 22, Lowest = 3. Range = 22 - 3 = 19."),
        i("coremath-m8t3-s3",
          "Semi-Interquartile Range and Percentiles\n\nSemi-Interquartile Range = IQR/2\n\nExample: If Q3 = 15 and Q1 = 5\nIQR = 10\nSemi-IQR = 5\n\nPercentiles:\nThe k-th percentile is the value below which k% of the data falls.\nMedian = 50th percentile\nQ1 = 25th percentile\nQ3 = 75th percentile\n\nVariance and Standard Deviation (more advanced):\nVariance = average of squared deviations from mean\nStandard Deviation = square root of variance\n\nLarger standard deviation = more spread out data\n\nBox and Whisker Plot:\nShows: Min, Q1, Median, Q3, Max\nUseful for comparing two or more datasets.\n\nWASSCE often asks you to draw or interpret box plots!"),
        q("coremath-m8t3-s4", "Data: 4, 8, 10, 12, 16, 20, 24\n\nQ1 = 8, Q3 = 20. What is the IQR?",
          "IQR = Q3 - Q1", 
          ["12", "20", "16", "8"], 0,
          "IQR = 20 - 8 = 12."),
    ]),
    L("coremath-m8t4", "Bar Charts, Histograms and Frequency Polygons",
      "Core Mathematics", "1d522", "Both", 2, 10, 25, "core-maths", ["coremath-m8t1"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m8t4-s1",
          "Bar Charts - for categorical data.\n\nBars of equal width, height = frequency.\nGaps between bars.\n\nExample: Favourite colour survey\nRed: 10, Blue: 15, Green: 8, Yellow: 7\nBar chart shows each colour with its frequency as bar height.\n\nHistograms - for continuous data grouped into classes.\n\nBars touch each other (no gaps).\nArea of bar represents frequency.\nHeight of bar = Frequency Density = Frequency/Class Width\n\nExample: Heights (cm)\n140-150: 8 students (width 10, density 0.8)\n150-160: 15 students (width 10, density 1.5)\n160-170: 12 students (width 10, density 1.2)\n\nWASSCE Tip: Know the difference between a bar chart and a histogram!"),
        p("coremath-m8t4-s2", "A bar chart has gaps between bars. A histogram has no gaps.\n\nWhich is used for continuous data?",
          "No gaps = continuous data", "Histogram or bar chart?",
          ["Bar chart", "Histogram", "Both", "Neither"], 1,
          "Histograms are used for continuous data (bars touch because data is continuous). Bar charts are for discrete/categorical data (gaps between bars)."),
        i("coremath-m8t4-s3",
          "Frequency Polygons - WASSCE Classic!\n\nA frequency polygon is a line graph connecting the midpoints of histogram bars.\n\nTo draw a frequency polygon:\n1. Find the midpoint of each class interval\n2. Plot frequency against midpoint\n3. Join points with straight lines\n4. Start and end on the x-axis (add extra classes with zero frequency at each end)\n\nExample: Heights (cm)\n140-150: midpoint 145, freq 8\n150-160: midpoint 155, freq 15\n160-170: midpoint 165, freq 12\n170-180: midpoint 175, freq 5\n\nPlot (145,8), (155,15), (165,12), (175,5)\nJoin them and extend to (135,0) and (185,0)"),
        q("coremath-m8t4-s4", "A class interval is 20-30. What is the midpoint?",
          "Midpoint = (20+30)/2", 
          ["25", "20", "30", "10"], 0,
          "Midpoint = (lower limit + upper limit)/2 = (20+30)/2 = 25."),
    ]),
    L("coremath-m8t5", "Pie Charts and Data Interpretation",
      "Core Mathematics", "1d522", "Both", 1, 8, 20, "core-maths", ["coremath-m8t1"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m8t5-s1",
          "Pie Charts show data as sectors (slices) of a circle.\n\nThe whole circle (360 degrees) represents the total frequency.\n\nTo draw a pie chart:\n1. Calculate angle for each category:\n   Angle = (Category frequency/Total frequency) x 360\n2. Draw and label each sector\n\nExample: Budget for education: 50gh, health: 30gh, roads: 20gh\nTotal = 100gh\nEducation: 50/100 x 360 = 180 degrees\nHealth: 30/100 x 360 = 108 degrees\nRoads: 20/100 x 360 = 72 degrees\n\nWASSCE often asks you to interpret pie charts!"),
        p("coremath-m8t5-s2", "A pie chart has 4 categories with frequencies: A=10, B=20, C=15, D=5.\n\nWhat is the angle for B?",
          "B angle = 20/50 x 360", "Angle for B = ?",
          ["144", "72", "108", "36"], 0,
          "Total = 10+20+15+5 = 50. Angle for B = 20/50 x 360 = 144 degrees."),
        i("coremath-m8t5-s3",
          "Interpreting Data - WASSCE Essential Skills!\n\nWhen reading tables, charts, and graphs:\n\n1. Check the title - what is the data about?\n2. Check the labels - what do the axes/categories represent?\n3. Check the scale - are there any breaks in the axes?\n4. Look for patterns and trends\n5. Compare categories or groups\n\nCommon Questions:\n- Which category has the highest/lowest value?\n- What is the difference between two categories?\n- What percentage does a category represent?\n- What is the ratio between two categories?\n- Estimate values between data points (interpolation)\n\nWASSCE Tip: Always show your working and include units in your answers!"),
        q("coremath-m8t5-s4", "A pie chart shows transport to school: Walk: 90 degrees, Bus: 120 degrees, Car: 60 degrees, Bike: 90 degrees.\n\nWhat percentage of students walk to school?",
          "Percentage = (90/360) x 100%", 
          ["25%", "33%", "15%", "20%"], 0,
          "90/360 x 100% = 1/4 x 100% = 25% of students walk to school."),
    ]),
]

# ═══════════════════════════════════════════════════════════════════════
#  MODULE 9: Probability (5 Topics)
# ═══════════════════════════════════════════════════════════════════════
MODULE9 = [
    L("coremath-m9t1", "Basic Probability Concepts",
      "Core Mathematics", "1d522", "Both", 2, 8, 20, "core-maths", ["coremath-m1t1"], ["SHS 1", "SHS 2"], "SHS 1", [
        i("coremath-m9t1-s1",
          "Probability measures how likely an event is to happen.\n\nScale: 0 (impossible) to 1 (certain)\n\nFormula:\nP(event) = Number of favourable outcomes / Total number of possible outcomes\n\nExamples:\nP(heads on a coin) = 1/2 = 0.5\nP(rolling a 3 on a die) = 1/6 = 0.167\nP(rolling an even number) = 3/6 = 1/2 = 0.5\n\nAll probabilities add to 1:\nP(heads) + P(tails) = 1/2 + 1/2 = 1\n\nComplement: P(not A) = 1 - P(A)\n\nWASSCE Tip: Always write probabilities as simplified fractions!"),
        p("coremath-m9t1-s2", "A fair die is rolled once. What is the probability of rolling a number greater than 4?",
          "Numbers > 4: 5, 6", "P(>4) = ?",
          ["1/3", "1/2", "1/6", "2/3"], 0,
          "Favourable: 5, 6 (2 outcomes). Total: 6 outcomes. P = 2/6 = 1/3."),
        i("coremath-m9t1-s3",
          "Sample Space and Outcomes\n\nThe sample space is all possible outcomes.\n\nSingle events:\nCoin: {H, T} - 2 outcomes\nDie: {1, 2, 3, 4, 5, 6} - 6 outcomes\n\nTwo events:\nTwo coins: {HH, HT, TH, TT} - 4 outcomes\nTwo dice: 6 x 6 = 36 outcomes\n\nListing systematic outcomes:\nWhen rolling two dice, list all 36 combinations.\nSum of 7: (1,6), (2,5), (3,4), (4,3), (5,2), (6,1) = 6 outcomes\nP(sum = 7) = 6/36 = 1/6\n\nMutually Exclusive Events: Cannot happen at the same time.\nP(A or B) = P(A) + P(B)\n\nExample: P(3 or 5 on a die) = 1/6 + 1/6 = 1/3"),
        q("coremath-m9t1-s4", "Two coins are tossed. What is the probability of getting exactly one head?",
          "Favourable: HT, TH", 
          ["1/4", "1/2", "3/4", "1/3"], 1,
          "Sample space: {HH, HT, TH, TT} (4 outcomes). Favourable: {HT, TH} (2 outcomes). P = 2/4 = 1/2."),
    ]),
    L("coremath-m9t2", "Probability of Combined Events",
      "Core Mathematics", "1d522", "Both", 2, 10, 25, "core-maths", ["coremath-m9t1"], ["SHS 2", "SHS 3"], "SHS 2", [
        i("coremath-m9t2-s1",
          "Independent Events: The outcome of one does NOT affect the other.\n\nP(A and B) = P(A) x P(B)\n\nExample: Rolling a die AND tossing a coin.\nP(heads AND 6) = P(heads) x P(6) = 1/2 x 1/6 = 1/12\n\nExample: Probability of rolling two sixes in a row.\nP(6 and 6) = 1/6 x 1/6 = 1/36\n\nDependent Events: The outcome of one AFFECTS the other.\nP(A and B) = P(A) x P(B given A)\n\nExample: Drawing two cards WITHOUT replacement.\nP(both aces) = 4/52 x 3/51 = 12/2652 = 1/221"),
        p("coremath-m9t2-s2", "A bag has 3 red and 4 blue marbles. You pick one, return it, then pick another.\n\nWhat is P(red AND red)?",
          "Independent (with replacement)", "P(red and red) = ?",
          ["3/7 x 3/7 = 9/49", "3/7 x 2/6 = 6/42", "3/4 x 3/4 = 9/16", "3/7 x 4/7 = 12/49"], 0,
          "With replacement: P(red) = 3/7 each time. P(red and red) = 3/7 x 3/7 = 9/49."),
        i("coremath-m9t2-s3",
          "Probability with and without Replacement - WASSCE Classic!\n\nWith Replacement:\n- The first item is returned before the second draw\n- Probabilities stay the same\n- Independent events\n\nWithout Replacement:\n- The first item is NOT returned\n- Probabilities change for the second draw\n- Dependent events\n\nExample: Bag with 5 red, 3 blue marbles (8 total). Pick TWO without replacement.\nP(both red) = 5/8 x 4/7 = 20/56 = 5/14\nP(one red, one blue) = P(red then blue) + P(blue then red)\n= (5/8 x 3/7) + (3/8 x 5/7)\n= 15/56 + 15/56 = 30/56 = 15/28\n\nAt least one: P(at least one red) = 1 - P(no reds) = 1 - P(blue, blue)\n= 1 - (3/8 x 2/7) = 1 - 6/56 = 50/56 = 25/28"),
        q("coremath-m9t2-s4", "A bag has 4 red and 6 blue marbles. Two are drawn WITHOUT replacement.\n\nWhat is P(both blue)?",
          "P(blue then blue) = 6/10 x 5/9", 
          ["30/90 = 1/3", "36/100 = 9/25", "6/10 x 5/9 = 30/90 = 1/3", "6/10 x 6/10 = 9/25"], 2,
          "First pick: 6/10. Second pick (without replacement): 5/9. P = 6/10 x 5/9 = 30/90 = 1/3."),
    ]),
    L("coremath-m9t3", "Tree Diagrams",
      "Core Mathematics", "1d522", "Both", 3, 12, 30, "core-maths", ["coremath-m9t2"], ["SHS 2", "SHS 3"], "SHS 2", [
        i("coremath-m9t3-s1",
          "Tree diagrams show all possible outcomes of combined events.\n\nEach branch represents a possible outcome.\nProbabilities multiply along branches.\n\nExample: Tossing a coin twice.\n\nFirst toss:      H (1/2)      T (1/2)\n                 /           /\nSecond:     H(1/2) T(1/2) H(1/2) T(1/2)\nOutcome:    HH    HT     TH    TT\nProb:       1/4   1/4    1/4   1/4\n\nTotal = 1 (1/4 + 1/4 + 1/4 + 1/4 = 1)\n\nThe sum of probabilities from each branching point = 1.\n\nWASSCE Essential: Tree diagrams are tested EVERY year!"),
        p("coremath-m9t3-s2", "A bag has 2 red and 3 green marbles. Two are picked WITH replacement.\n\nHow many branches does the tree diagram have?",
          "2 choices x 2 choices", "Number of outcomes = ?",
          ["4", "6", "9", "25"], 0,
          "First pick: 2 outcomes (R, G). Second pick: 2 outcomes. Total branches = 2 x 2 = 4."),
        i("coremath-m9t3-s3",
          "Solving Problems with Tree Diagrams\n\nStep 1: Draw the first set of branches with their probabilities\nStep 2: Draw the second set of branches from each outcome\nStep 3: Multiply along branches to find final probabilities\nStep 4: Add probabilities of relevant outcomes\n\nExample: Bag with 3 red, 5 blue marbles (8 total). Two picks WITHOUT replacement.\n\nFirst pick: R(3/8) or B(5/8)\n\nFrom R: second R(2/7) or B(5/7)\nFrom B: second R(3/7) or B(4/7)\n\nP(RR) = 3/8 x 2/7 = 6/56 = 3/28\nP(RB) = 3/8 x 5/7 = 15/56\nP(BR) = 5/8 x 3/7 = 15/56\nP(BB) = 5/8 x 4/7 = 20/56 = 5/14\n\nCheck sum: 6+15+15+20 = 56/56 = 1"),
        q("coremath-m9t3-s4", "A bag contains 2 red and 4 green balls. Two balls are picked WITH replacement.\n\nWhat is P(at least one red)?",
          "P(at least one R) = 1 - P(GG)", 
          ["20/36 = 5/9", "24/36 = 2/3", "12/36 = 1/3", "28/36 = 7/9"], 0,
          "P(GG) = 4/6 x 4/6 = 16/36 = 4/9. P(at least one R) = 1 - 4/9 = 5/9."),
    ]),
    L("coremath-m9t4", "Conditional Probability",
      "Core Mathematics", "1d522", "Both", 3, 10, 25, "core-maths", ["coremath-m9t2"], ["SHS 3"], "SHS 3", [
        i("coremath-m9t4-s1",
          "Conditional probability is the probability of an event given that another has already occurred.\n\nNotation: P(A | B) = Probability of A GIVEN that B has occurred.\n\nFormula: P(A | B) = P(A and B)/P(B)\n\nExample: In a class, 40% play football, 25% play both football and basketball. What is P(basketball | football)?\nP(B|F) = P(F and B)/P(F) = 25%/40% = 0.25/0.4 = 5/8 = 0.625\n\nTree Diagram Method:\nConditional probabilities are on the second set of branches (WITHOUT replacement problems)."),
        p("coremath-m9t4-s2", "From a standard deck of 52 cards, one card is drawn. It is a heart.\n\nWhat is the probability it is also an ace?",
          "P(ace | heart) = ?", "P(ace | heart) = ?",
          ["1/13", "4/52 = 1/13", "1/52", "1/4"], 0,
          "There are 13 hearts. One of them is an ace. P(ace | heart) = 1/13. This is a conditional probability (already known it is a heart)."),
        i("coremath-m9t4-s3",
          "Applications of Conditional Probability - WASSCE Classic!\n\nExample: A factory has two machines. Machine A produces 60% of items, Machine B produces 40%. 2% of Machine A's items are defective, 5% of Machine B's items are defective.\n\nWhat is the probability a randomly selected item is defective?\nP(D) = P(A and D) + P(B and D)\n= (0.6 x 0.02) + (0.4 x 0.05)\n= 0.012 + 0.02 = 0.032 = 3.2%\n\nGiven an item is defective, what is the probability it came from Machine A?\nP(A | D) = P(A and D)/P(D) = 0.012/0.032 = 0.375 = 37.5%\n\nThis is Bayes' Theorem in action!"),
        q("coremath-m9t4-s4", "In a school, 70% of students are boys. 10% of boys play netball. What percentage of ALL students are boys who play netball?",
          "P(boy and netball) = 0.7 x 0.1", 
          ["70%", "7%", "10%", "17%"], 1,
          "P(boy and netball) = P(boy) x P(netball | boy) = 0.7 x 0.1 = 0.07 = 7%."),
    ]),
    L("coremath-m9t5", "Probability Applications and Problem Solving",
      "Core Mathematics", "1d522", "Both", 3, 12, 30, "core-maths", ["coremath-m9t4"], ["SHS 3"], "SHS 3", [
        i("coremath-m9t5-s1",
          "Combined Probability Problems - WASSCE Style!\n\nProblem: Two dice are rolled. What is the probability that the sum is 7 or 11?\n\nPossible sums of 7: (1,6), (2,5), (3,4), (4,3), (5,2), (6,1) = 6 outcomes\nPossible sums of 11: (5,6), (6,5) = 2 outcomes\nTotal favourable = 8 outcomes\nP(7 or 11) = 8/36 = 2/9\n\nProblem: A coin is tossed 3 times. What is the probability of getting at least 2 heads?\n\nFavourable outcomes: HHH, HHT, HTH, THH (4 outcomes)\nTotal outcomes: 2-cubed = 8\nP(at least 2 heads) = 4/8 = 1/2"),
        p("coremath-m9t5-s2", "A fair die is rolled twice. What is the probability both rolls show a number less than 3?",
          "P(<3) = 2/6 = 1/3 each time", "P(both < 3) = ?",
          ["1/9", "1/3", "4/36 = 1/9", "2/3"], 0,
          "Numbers less than 3: 1, 2. P(one roll) = 2/6 = 1/3. Both: 1/3 x 1/3 = 1/9."),
        i("coremath-m9t5-s3",
          "Real-World Probability Applications\n\nExpected Value:\nExpected value = Sum of (value x probability)\n\nExample: A lottery has 100 tickets costing 5gh each. Prize is 200gh.\nWinning: P = 1/100, Value = 200-5 = 195gh profit\nLosing: P = 99/100, Value = -5gh loss\n\nExpected value = (0.01 x 195) + (0.99 x -5) = 1.95 - 4.95 = -3gh\nOn average, you lose 3gh per ticket!\n\nRisk Assessment:\nIf P(disease) = 0.01 and test is 95% accurate:\nP(positive | disease) = 0.95\nP(positive | no disease) = 0.05\nInterpretation is vital - see conditional probability.\n\nWASSCE often applies probability to real situations like:\n- Quality control in factories\n- Medical testing\n- Sports predictions\n- Weather forecasting"),
        q("coremath-m9t5-s4", "A bag contains 3 red, 4 blue, and 3 green marbles. One marble is picked at random.\n\nWhat is the probability it is red OR green?",
          "P(red or green) = (3+3)/10", 
          ["3/5", "2/5", "6/100", "3/10"], 0,
          "Total marbles = 10. Favourable = 3 red + 3 green = 6. P = 6/10 = 3/5."),
    ]),
]

# ═══════════════════════════════════════════════════════════════════════
#  COMBINE ALL MODULES
# ═══════════════════════════════════════════════════════════════════════
ALL_LESSONS = MODULE1 + MODULE2 + MODULE3 + MODULE4 + MODULE5 + MODULE6 + MODULE7 + MODULE8 + MODULE9


def main():
    filepath = "app/lib/learningContent.ts"

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lessons_str = "\n\n".join(make_lesson(l) for l in ALL_LESSONS)

    new_lessons_block = (
        "  //  CORE MATHEMATICS — 9 Modules × 5 Topics = 45 Lessons\n"
        "  //  Generated by scripts/generate_all_coremaths.py\n"
        f"{lessons_str}\n"
    )

    # Find CORE MATHEMATICS section
    cm_start = content.find("//  CORE MATHEMATICS")
    if cm_start < 0:
        # Fallback: look for coremath-1
        alt = content.find("id: 'coremath-")
        if alt >= 0:
            line_start = content.rfind("\n", 0, alt) + 1
            cm_start = line_start
            print(f"Found coremath lesson at position {alt}, using line start {line_start}")
        else:
            print("ERROR: Could not find CORE MATHEMATICS marker or coremath lessons")
            sys.exit(1)

    # Find end of the section
    search_from = cm_start + 50
    next_subject = content.find("\n  //  ", search_from)
    
    if next_subject < 0:
        cm_end = content.find("];", search_from)
        if cm_end < 0:
            print("ERROR: Could not find end of Core Maths section")
            sys.exit(1)
        cm_end_line = cm_end + 2
    else:
        cm_end_line = next_subject

    # Replace section
    new_content = content[:cm_start] + new_lessons_block + "\n" + content[cm_end_line:]

    # Update SHARED_UNITS entry for core-maths
    lesson_ids = [l["id"] for l in ALL_LESSONS]
    lesson_ids_str = ", ".join(f"'{lid}'" for lid in lesson_ids)
    new_arr = f"[{lesson_ids_str}]"

    idx_in_new = new_content.find("id: 'core-maths'")
    if idx_in_new >= 0:
        arr_s = new_content.find("[", new_content.find("lessons:", idx_in_new))
        arr_e = new_content.find("]", arr_s)
        if arr_s >= 0 and arr_e >= 0:
            new_content = new_content[:arr_s] + new_arr + new_content[arr_e+1:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"[OK] Generated {len(ALL_LESSONS)} lessons and updated {filepath}")
    print(f"   Module breakdown: {len(MODULE1)}+{len(MODULE2)}+{len(MODULE3)}+{len(MODULE4)}+{len(MODULE5)}+{len(MODULE6)}+{len(MODULE7)}+{len(MODULE8)}+{len(MODULE9)}")
    print(f"   File size: {len(new_content)} chars")


if __name__ == "__main__":
    main()
