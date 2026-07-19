/**
 * generatedAdditionalMathsSHS2Lessons.ts
 * Auto-generated Additional Mathematics SHS 2 lessons from Ministry of Education curriculum materials.
 * Source: Additional Maths Y2.pdf (Ministry of Education, 2025)
 * Contains 12 sections with 24 lessons total.
 */

import type { Lesson } from './learningContent';

export const ADD_MATHS_SHS2_LESSONS: Lesson[] = [

  // ═══ MODULE 1: SETS AND BINOMIAL EXPANSIONS ═══
  {
    id: "add-math-2-s1t1",
    title: "Set Theory and De Morgan's Laws",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 2,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: [],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s1t1-intro",
        type: "info",
        content: "**Set Theory and De Morgan's Laws**\n\nIn SHS 2, we deepen our understanding of set theory by exploring De Morgan's Laws and their applications. Sets provide a foundation for understanding relationships between collections of objects, which is essential in probability, logic, and advanced mathematics.",
      },
      {
        id: "add-math-2-s1t1-content-1",
        type: "info",
        content: "**Review of Basic Set Operations**\n\n- **Union (A ∪ B)**: The set of all elements in A or B (or both).\n- **Intersection (A ∩ B)**: The set of all elements in both A and B.\n- **Complement (A')**: The set of all elements in the universal set that are NOT in A.\n- **Difference (A − B)**: The set of elements in A but not in B.\n\n**Properties of Complements:**\n- A ∪ A' = ℰ (Universal set)\n- A ∩ A' = ∅ (Null set)\n- (A')' = A (Double complement)\n- ∅' = ℰ and ℰ' = ∅",
      },
      {
        id: "add-math-2-s1t1-content-2",
        type: "info",
        content: "**De Morgan's Laws**\n\nDe Morgan's Laws describe how complement interacts with union and intersection:\n\n**First Law:** (A ∪ B)' = A' ∩ B'\n*The complement of a union is the intersection of complements.*\n\n**Second Law:** (A ∩ B)' = A' ∪ B'\n*The complement of an intersection is the union of complements.*\n\n**Verification using Venn Diagrams:**\n\nFor (A ∪ B)':\n1. Shade A ∪ B (all elements in A or B).\n2. The complement is everything OUTSIDE A ∪ B.\n3. This is the same region as A' ∩ B' (outside A AND outside B).\n\nThese laws are useful for simplifying logical expressions and solving complex set problems.",
      },
      {
        id: "add-math-2-s1t1-content-3",
        type: "info",
        content: "**Worked Example — De Morgan's Laws**\n\n**Example:** Given universal set ℰ = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}, A = {2, 4, 6, 8, 10}, B = {3, 6, 9}.\n\nVerify (A ∪ B)' = A' ∩ B'.\n\n**Solution:**\n\nA ∪ B = {2, 3, 4, 6, 8, 9, 10}\n(A ∪ B)' = {1, 5, 7}\n\nA' = {1, 3, 5, 7, 9}\nB' = {1, 2, 4, 5, 7, 8, 10}\nA' ∩ B' = {1, 5, 7}\n\nSince (A ∪ B)' = {1, 5, 7} = A' ∩ B', the law is verified.\n\n**Check** (A ∩ B)' = A' ∪ B' using the same sets.\nA ∩ B = {6}\n(A ∩ B)' = {1, 2, 3, 4, 5, 7, 8, 9, 10}\nA' ∪ B' = {1, 3, 5, 7, 9} ∪ {1, 2, 4, 5, 7, 8, 10} = {1, 2, 3, 4, 5, 7, 8, 9, 10}\n\nBoth laws are verified!",
      },
      {
        id: "add-math-2-s1t1-practice",
        type: "question",
        content: "Test your understanding of De Morgan's Laws.",
        exercise: {
          question: "According to De Morgan's First Law, (A ∪ B)' is equivalent to:",
          options: [
            "A' ∪ B'",
            "A' ∩ B'",
            "(A ∩ B)'",
            "ℰ − (A ∩ B)"
          ],
          correctIndex: 1,
          explanation: "De Morgan's First Law states that (A ∪ B)' = A' ∩ B'. The complement of a union is the intersection of complements."
        }
      },
    ],
  },
  {
    id: "add-math-2-s1t2",
    title: "The Binomial Theorem for Rational and Negative Indices",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 4,
    estimatedMinutes: 30,
    xpReward: 60,
    prerequisites: ["add-math-2-s1t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s1t2-intro",
        type: "info",
        content: "**The Binomial Theorem for Rational and Negative Indices**\n\nIn SHS 1, we learned to expand (a + b)ⁿ for positive integer n using Pascal's triangle and the combination formula. In SHS 2, we extend the binomial theorem to rational (fractional) and negative indices, which allows us to approximate roots and complex expressions.",
      },
      {
        id: "add-math-2-s1t2-content-1",
        type: "info",
        content: "**General Binomial Theorem for Any Index**\n\nFor any rational number n (positive, negative, or fractional), the binomial expansion of (1 + x)ⁿ is given by:\n\n(1 + x)ⁿ = 1 + nx + n(n−1)x²/2! + n(n−1)(n−2)x³/3! + ...\n\n**Important Notes:**\n- When n is NOT a positive integer, the expansion is an **infinite series** (it never terminates).\n- The expansion is valid (converges) when |x| < 1.\n- We use the general term formula: Tᵣ₊₁ = ⁿCᵣ xʳ, where ⁿCᵣ = n(n−1)(n−2)...(n−r+1)/r!\n\n**Example:** Expand (1 + x)¹ᐟ² (the square root of 1 + x) up to the x³ term:\n(1 + x)¹ᐟ² = 1 + ½x + (½)(−½)x²/2! + (½)(−½)(−³⁄₂)x³/3! + ...\n= 1 + x/2 − x²/8 + x³/16 − ...",
      },
      {
        id: "add-math-2-s1t2-content-2",
        type: "info",
        content: "**Expanding Expressions Not in the Form (1 + x)ⁿ**\n\nWhen the expression is in the form (a + x)ⁿ, we first factor out 'a' to get:\n(a + x)ⁿ = aⁿ(1 + x/a)ⁿ\n\nThen expand (1 + x/a)ⁿ using the general binomial theorem.\n\n**Worked Example:** Expand (2 + 3x)⁻² up to the x³ term.\n\n**Solution:**\n(2 + 3x)⁻² = 2⁻²(1 + 3x/2)⁻²\n= ¼[1 + (−2)(3x/2) + (−2)(−3)(3x/2)²/2! + (−2)(−3)(−4)(3x/2)³/3! + ...]\n= ¼[1 − 3x + 27x²/4 − 27x³/2 + ...]\n= ¼ − 3x/4 + 27x²/16 − 27x³/8 + ...",
      },
      {
        id: "add-math-2-s1t2-content-3",
        type: "info",
        content: "**Approximations Using the Binomial Theorem**\n\nThe binomial theorem can be used to find approximate numerical values.\n\n**Worked Example:** Find the approximate value of √(1.12) correct to 5 decimal places.\n\n**Solution:**\n√(1.12) = (1 + 0.12)¹ᐟ²\n= 1 + ½(0.12) + (½)(−½)(0.12)²/2! + (½)(−½)(−³⁄₂)(0.12)³/3! + ...\n= 1 + 0.06 + (−0.0018) + 0.000108 + ...\n= 1.058308...\n≈ 1.05831 (correct to 5 decimal places)\n\n(Check: 1.05831² = 1.12002 ≈ 1.12 ✓)\n\n**Worked Example:** Find the value of √101 correct to 4 decimal places.\n\n√101 = √(100 + 1) = 10√(1 + 0.01) = 10(1 + 0.01)¹ᐟ²\n= 10[1 + ½(0.01) − ⅛(0.01)² + ...]\n= 10[1 + 0.005 − 0.0000125 + ...]\n= 10 × 1.0049875 = 10.0499 (correct to 4 d.p.)",
      },
      {
        id: "add-math-2-s1t2-practice",
        type: "question",
        content: "Test your understanding of the binomial theorem.",
        exercise: {
          question: "What is the first term of the binomial expansion of (1 + x)⁻²?",
          options: [
            "1",
            "−2x",
            "2",
            "1 − 2x"
          ],
          correctIndex: 0,
          explanation: "(1 + x)⁻² = 1 + (−2)x + (−2)(−3)x²/2! + ... = 1 − 2x + 3x² − ... The first term is always 1 when expanding (1 + x)ⁿ."
        }
      },
    ],
  },

  // ═══ MODULE 2: SEQUENCES AND INEQUALITIES ═══
  {
    id: "add-math-2-s2t1",
    title: "Arithmetic and Geometric Progressions",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 2,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["add-math-2-s1t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s2t1-intro",
        type: "info",
        content: "**Arithmetic and Geometric Progressions**\n\nSequences and series are fundamental concepts in mathematics. An arithmetic progression (AP) has a constant difference between consecutive terms, while a geometric progression (GP) has a constant ratio. Understanding these progressions enables us to model and solve many real-world problems.",
      },
      {
        id: "add-math-2-s2t1-content-1",
        type: "info",
        content: "**Arithmetic Progression (AP)**\n\nAn AP is a sequence where each term differs from the previous term by a constant called the **common difference (d)**.\n\n**General Form:** a, a + d, a + 2d, a + 3d, ...\n\n**n-th Term Formula:**\nUₙ = a + (n − 1)d\n\n**Sum of First n Terms:**\nSₙ = n/2 [2a + (n − 1)d]\nor Sₙ = n/2 [a + L] where L is the last term.\n\n**Example:** Find the 15th term and sum of the first 15 terms of the AP: 3, 7, 11, 15, ...\n\na = 3, d = 4\nU₁₅ = 3 + (15 − 1)(4) = 3 + 56 = 59\nS₁₅ = 15/2 [2(3) + (15 − 1)(4)] = 15/2 [6 + 56] = 15/2 × 62 = 465",
      },
      {
        id: "add-math-2-s2t1-content-2",
        type: "info",
        content: "**Geometric Progression (GP)**\n\nA GP is a sequence where each term is obtained by multiplying the previous term by a constant called the **common ratio (r)**.\n\n**General Form:** a, ar, ar², ar³, ...\n\n**n-th Term Formula:**\nUₙ = arⁿ⁻¹\n\n**Sum of First n Terms:**\nSₙ = a(rⁿ − 1)/(r − 1) for r ≠ 1\n\n**Sum to Infinity (when |r| < 1):**\nS∞ = a/(1 − r)\n\nA series converges (approaches a finite value) when |r| < 1, and diverges when |r| ≥ 1.\n\n**Example:** Find the sum to infinity of the GP: 16, 8, 4, 2, ...\n\na = 16, r = ½\nS∞ = 16/(1 − ½) = 16/(½) = 32",
      },
      {
        id: "add-math-2-s2t1-content-3",
        type: "info",
        content: "**Arithmetic and Geometric Means**\n\n**Arithmetic Mean (AM):**\nThe arithmetic mean of two numbers a and b is (a + b)/2.\nFor n numbers, the arithmetic mean is the sum divided by n.\n\n**Geometric Mean (GM):**\nThe geometric mean of two positive numbers a and b is √(ab).\nFor n positive numbers, the geometric mean is the n-th root of their product.\n\n**Relationship between AM and GM:**\nFor any two positive numbers, AM ≥ GM. Equality only occurs when a = b.\n\n**Applications:**\n- APs model linear growth (e.g., simple interest, uniform motion).\n- GPs model exponential growth/decay (e.g., compound interest, population growth, radioactive decay).\n- Sum to infinity is used in calculating the value of perpetuities in finance.",
      },
      {
        id: "add-math-2-s2t1-practice",
        type: "question",
        content: "Test your understanding of sequences and series.",
        exercise: {
          question: "A geometric progression has first term 4 and common ratio ½. What is its sum to infinity?",
          options: [
            "6",
            "8",
            "4",
            "16"
          ],
          correctIndex: 1,
          explanation: "S∞ = a/(1 − r) = 4/(1 − ½) = 4/(½) = 8."
        }
      },
    ],
  },
  {
    id: "add-math-2-s2t2",
    title: "Systems of Linear Inequalities and Linear Programming",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 3,
    estimatedMinutes: 30,
    xpReward: 60,
    prerequisites: ["add-math-2-s2t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s2t2-intro",
        type: "info",
        content: "**Systems of Linear Inequalities and Linear Programming**\n\nLinear programming is a method for finding optimal solutions (maximum or minimum values) subject to constraints expressed as linear inequalities. It has applications in business, economics, engineering, and resource allocation.",
      },
      {
        id: "add-math-2-s2t2-content-1",
        type: "info",
        content: "**Solving Linear Inequalities**\n\nLinear inequalities are solved similarly to linear equations, but with special rules for multiplying or dividing by negative numbers.\n\n**Rules:**\n- Adding/subtracting the same number: inequality sign stays the same.\n- Multiplying/dividing by a positive number: inequality sign stays the same.\n- Multiplying/dividing by a negative number: REVERSE the inequality sign.\n\n**Example:** Solve 3x − 7 ≤ 2x + 5\n3x − 2x ≤ 5 + 7\nx ≤ 12\n\n**Example:** Solve −2x + 3 > 7\n−2x > 4\nx < −2 (sign reversed when dividing by −2)",
      },
      {
        id: "add-math-2-s2t2-content-2",
        type: "info",
        content: "**Graphing Systems of Linear Inequalities**\n\nTo graph a system of linear inequalities:\n1. Graph each inequality as a straight line (boundary).\n2. Use a solid line for ≤ or ≥; a dashed line for < or >.\n3. Shade the region that satisfies each inequality.\n4. The feasible region is where ALL shaded regions overlap.\n\n**Example:** Graph the system:\nx + y ≤ 6\nx ≥ 0\ny ≥ 0\n2x + y ≤ 10\n\n1. Graph x + y = 6 (solid). Test (0,0): 0 ≤ 6, so shade below.\n2. x ≥ 0: shade to the right of the y-axis.\n3. y ≥ 0: shade above the x-axis.\n4. Graph 2x + y = 10 (solid). Test (0,0): 0 ≤ 10, so shade below.\n\nThe feasible region is a polygon with vertices at (0,0), (5,0), (4,2), and (0,6).",
      },
      {
        id: "add-math-2-s2t2-content-3",
        type: "info",
        content: "**Optimisation — Maximising and Minimising**\n\nTo find the maximum or minimum value of an objective function (e.g., P = 3x + 2y) subject to constraints:\n\n1. Graph all constraints and identify the feasible region.\n2. Find the coordinates of all vertices (corner points) of the feasible region.\n3. Evaluate the objective function at each vertex.\n4. The largest value is the maximum; the smallest is the minimum.\n\n**Worked Example:** Maximise P = 3x + 2y subject to:\nx + y ≤ 6, 2x + y ≤ 10, x ≥ 0, y ≥ 0\n\nVertices: (0,0) → P = 0\n(5,0) → P = 15\n(4,2) → P = 12 + 4 = 16\n(0,6) → P = 12\n\nMaximum: P = 16 at (4, 2).\n\n**Real-world Application:** A factory produces two products A and B. Each product requires certain machine hours and labour hours. The objective is to maximise profit given resource constraints — this is a classic linear programming problem.",
      },
      {
        id: "add-math-2-s2t2-practice",
        type: "question",
        content: "Test your understanding of linear programming.",
        exercise: {
          question: "In linear programming, the optimal solution occurs at:",
          options: [
            "Any point inside the feasible region",
            "A vertex (corner point) of the feasible region",
            "The center of the feasible region",
            "Any point on the boundary"
          ],
          correctIndex: 1,
          explanation: "The optimal solution in linear programming always occurs at one of the vertices (corner points) of the feasible region, according to the fundamental theorem of linear programming."
        }
      },
    ],
  },

  // ═══ MODULE 3: POLYNOMIAL FUNCTIONS ═══
  {
    id: "add-math-2-s3t1",
    title: "Factor and Remainder Theorems",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["add-math-2-s2t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s3t1-intro",
        type: "info",
        content: "**Factor and Remainder Theorems**\n\nPolynomial functions are expressions like P(x) = aₙxⁿ + aₙ₋₁xⁿ⁻¹ + ... + a₁x + a₀. The Factor and Remainder Theorems are powerful tools for analysing and factorising polynomials without performing long division.",
      },
      {
        id: "add-math-2-s3t1-content-1",
        type: "info",
        content: "**The Remainder Theorem**\n\nWhen a polynomial P(x) is divided by (x − a), the remainder is P(a).\n\n**Proof:** P(x) = (x − a)Q(x) + R\nSubstituting x = a: P(a) = (a − a)Q(a) + R = 0 + R = R\n\n**Example:** Find the remainder when P(x) = x³ − 2x² + 3x − 5 is divided by (x − 2).\n\nP(2) = 2³ − 2(2²) + 3(2) − 5\n= 8 − 8 + 6 − 5 = 1\n\nSo the remainder is 1.\n\nWe can also divide by (ax + b):\nP(x) ÷ (ax + b): remainder = P(−b/a)",
      },
      {
        id: "add-math-2-s3t1-content-2",
        type: "info",
        content: "**The Factor Theorem**\n\nThe Factor Theorem is a special case of the Remainder Theorem:\n\nIf P(a) = 0, then (x − a) is a factor of P(x).\nConversely, if (x − a) is a factor of P(x), then P(a) = 0.\n\n**Example:** Show that (x − 3) is a factor of P(x) = x³ − 6x² + 11x − 6.\n\nP(3) = 3³ − 6(3²) + 11(3) − 6\n= 27 − 54 + 33 − 6 = 0\n\nSince P(3) = 0, (x − 3) is a factor.\nTo find the other factors, divide P(x) by (x − 3):\n(x³ − 6x² + 11x − 6) ÷ (x − 3) = x² − 3x + 2\n= (x − 2)(x − 1)\n\nTherefore: P(x) = (x − 3)(x − 2)(x − 1)",
      },
      {
        id: "add-math-2-s3t1-content-3",
        type: "info",
        content: "**Rational Zero Theorem**\n\nThe Rational Zero Theorem helps identify possible rational roots (zeros) of a polynomial.\n\nIf P(x) = aₙxⁿ + ... + a₀ has integer coefficients, then any rational zero p/q must satisfy:\n- p is a factor of the constant term (a₀)\n- q is a factor of the leading coefficient (aₙ)\n\n**Example:** Find all zeros of P(x) = 2x³ − 3x² − 11x + 6.\n\nPossible rational zeros: factors of 6 ÷ factors of 2\np: ±1, ±2, ±3, ±6\nq: ±1, ±2\nPossible p/q: ±1, ±2, ±3, ±6, ±½, ±³⁄₂\n\nTest x = 2: P(2) = 16 − 12 − 22 + 6 = −12 ≠ 0\nTest x = 3: P(3) = 54 − 27 − 33 + 6 = 0 → (x − 3) is a factor\n\nDivide: (2x³ − 3x² − 11x + 6) ÷ (x − 3) = 2x² + 3x − 2\n= (2x − 1)(x + 2)\n\nSo zeros are x = 3, x = ½, x = −2.",
      },
      {
        id: "add-math-2-s3t1-practice",
        type: "question",
        content: "Test your understanding of the Factor and Remainder Theorems.",
        exercise: {
          question: "If P(2) = 0 for a polynomial P(x), what can we conclude?",
          options: [
            "The remainder when dividing by (x + 2) is 0",
            "The remainder when dividing by (x − 2) is 0, so (x − 2) is a factor",
            "x = −2 is a root of the polynomial",
            "The polynomial has no constant term"
          ],
          correctIndex: 1,
          explanation: "If P(2) = 0, then by the Factor Theorem, (x − 2) is a factor of the polynomial. This means the remainder when dividing P(x) by (x − 2) is 0."
        }
      },
    ],
  },
  {
    id: "add-math-2-s3t2",
    title: "Graphing and Solving Polynomial Equations",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 4,
    estimatedMinutes: 30,
    xpReward: 60,
    prerequisites: ["add-math-2-s3t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s3t2-intro",
        type: "info",
        content: "**Graphing and Solving Polynomial Equations**\n\nGraphing polynomial functions helps us understand their behaviour, identify roots, turning points, and end behaviour. The Fundamental Theorem of Algebra states that every polynomial of degree n > 0 has at least one complex zero.",
      },
      {
        id: "add-math-2-s3t2-content-1",
        type: "info",
        content: "**Key Features of Polynomial Graphs**\n\n**Degree and Shape:**\n- Linear (degree 1): Straight line\n- Quadratic (degree 2): Parabola\n- Cubic (degree 3): S-shaped curve\n- Quartic (degree 4): W-shaped (or inverted W)\n\n**End Behaviour:**\n- Leading coefficient a > 0 and even degree: both ends point up.\n- Leading coefficient a > 0 and odd degree: left end down, right end up.\n- Leading coefficient a < 0 and even degree: both ends point down.\n- Leading coefficient a < 0 and odd degree: left end up, right end down.\n\n**Multiplicity of Roots:**\n- If a factor (x − h)ᵏ appears with odd k: the graph CROSSES the x-axis at h.\n- If a factor (x − h)ᵏ appears with even k: the graph TOUCHES (but does not cross) the x-axis at h.",
      },
      {
        id: "add-math-2-s3t2-content-2",
        type: "info",
        content: "**Descartes' Rule of Signs**\n\nDescartes' Rule determines the possible number of positive and negative real zeros by counting sign changes.\n\n**For positive real zeros:**\nCount the number of sign changes in P(x). The number of positive real zeros is either this number or less by an even number.\n\n**For negative real zeros:**\nCount the number of sign changes in P(−x). The number of negative real zeros is either this number or less by an even number.\n\n**Example:** P(x) = 2x⁵ − 3x⁴ + x² − 5x + 1\nSign changes in P(x): + to − (1), − to + (2), + to − (3), − to + (4) → 4 changes\nPossible positive zeros: 4, 2, or 0\n\nP(−x) = −2x⁵ − 3x⁴ + x² + 5x + 1\nSign changes in P(−x): − to + (1) → 1 change\nPossible negative zeros: 1",
      },
      {
        id: "add-math-2-s3t2-content-3",
        type: "info",
        content: "**Complex Conjugates Theorem**\n\nIf a polynomial has real coefficients and a complex root a + bi, then its conjugate a − bi must also be a root.\n\n**Fundamental Theorem of Algebra:**\nEvery polynomial of degree n > 0 has exactly n roots (counting multiplicities), including real and complex roots.\n\n**Example:** Write a polynomial of degree 4 with zeros at x = 2, x = −1, and x = 1 ± i.\n\nFactors: (x − 2)(x + 1)[x − (1 + i)][x − (1 − i)]\n\nSimplify the complex factors:\n[x − (1 + i)][x − (1 − i)] = (x − 1 − i)(x − 1 + i)\n= (x − 1)² − (i)²\n= x² − 2x + 1 − (−1)\n= x² − 2x + 2\n\nP(x) = (x − 2)(x + 1)(x² − 2x + 2)\n= (x² − x − 2)(x² − 2x + 2)\n= x⁴ − 3x³ + 2x² + 2x − 4",
      },
      {
        id: "add-math-2-s3t2-practice",
        type: "question",
        content: "Test your understanding of polynomial functions.",
        exercise: {
          question: "If a cubic polynomial has leading coefficient positive, what is its end behaviour?",
          options: [
            "Both ends point up",
            "Left end down, right end up",
            "Left end up, right end down",
            "Both ends point down"
          ],
          correctIndex: 1,
          explanation: "For odd-degree polynomials with a positive leading coefficient, the end behaviour is: as x → −∞, y → −∞; as x → +∞, y → +∞. So left end points down, right end points up."
        }
      },
    ],
  },

  // ═══ MODULE 4: CIRCLES AND LOCI ═══
  {
    id: "add-math-2-s4t1",
    title: "Equations of Circles",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["add-math-2-s3t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s4t1-intro",
        type: "info",
        content: "**Equations of Circles**\n\nA circle is defined as the set of all points equidistant from a fixed point (the centre). The distance from the centre to any point on the circle is called the radius. Understanding the equation of a circle is essential for coordinate geometry and its applications.",
      },
      {
        id: "add-math-2-s4t1-content-1",
        type: "info",
        content: "**Standard Form of a Circle Equation**\n\nThe standard form is derived from the distance formula:\n\nFor a circle with centre (h, k) and radius r:\n(x − h)² + (y − k)² = r²\n\n**Example:** Write the equation of a circle with centre (3, −2) and radius 5.\n\n(x − 3)² + (y + 2)² = 25\n\n**Example:** Find the centre and radius of (x + 1)² + (y − 4)² = 9.\n\nCentre: (−1, 4)\nRadius: √9 = 3\n\n**Unit Circle:** x² + y² = 1 (centre at origin, radius 1)",
      },
      {
        id: "add-math-2-s4t1-content-2",
        type: "info",
        content: "**General Form of a Circle Equation**\n\nThe general form is:\nx² + y² + 2gx + 2fy + c = 0\n\nWhere:\n- Centre: (−g, −f)\n- Radius: √(g² + f² − c)\n\nThe circle exists (is real) only if g² + f² − c > 0.\n\n**Example:** Find the centre and radius of x² + y² − 6x + 8y − 11 = 0.\n\nComparing to general form:\n2g = −6 → g = −3\n2f = 8 → f = 4\nc = −11\n\nCentre = (−g, −f) = (3, −4)\nRadius = √(g² + f² − c) = √(9 + 16 + 11) = √36 = 6\n\n**Converting from General to Standard Form:**\nComplete the square for x and y terms:\nx² − 6x + y² + 8y − 11 = 0\n(x² − 6x + 9) + (y² + 8y + 16) = 11 + 9 + 16\n(x − 3)² + (y + 4)² = 36",
      },
      {
        id: "add-math-2-s4t1-content-3",
        type: "info",
        content: "**Tangents and Normals to Circles**\n\n**Tangent:** A line that touches the circle at exactly one point.\n- The radius drawn to the point of tangency is perpendicular to the tangent.\n- If a line is tangent, the discriminant b² − 4ac = 0 when solving the system of equations.\n\n**Normal:** A line perpendicular to the tangent at the point of contact.\n- The normal always passes through the centre of the circle.\n- If tangent gradient = mₜ, then normal gradient = −1/mₜ.\n\n**Length of a Tangent from an External Point:**\nIf point P is outside the circle, the length of the tangent from P to the circle is:\nL = √(d² − r²)\nwhere d is the distance from P to the centre.\n\n**Example:** Find the length of the tangent from (7, 1) to x² + y² = 25.\n\nCentre: (0, 0), r = 5\nd = √(7² + 1²) = √50\nL = √(50 − 25) = √25 = 5",
      },
      {
        id: "add-math-2-s4t1-practice",
        type: "question",
        content: "Test your understanding of circle equations.",
        exercise: {
          question: "What is the centre of the circle x² + y² + 4x − 6y − 12 = 0?",
          options: [
            "(2, −3)",
            "(−2, 3)",
            "(4, −6)",
            "(−4, 6)"
          ],
          correctIndex: 1,
          explanation: "Comparing to x² + y² + 2gx + 2fy + c = 0: 2g = 4 → g = 2, 2f = −6 → f = −3. Centre = (−g, −f) = (−2, 3)."
        }
      },
    ],
  },
  {
    id: "add-math-2-s4t2",
    title: "Introduction to Loci",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["add-math-2-s4t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s4t2-intro",
        type: "info",
        content: "**Introduction to Loci**\n\nA locus (plural: loci) is the set of all points that satisfy a given condition or set of conditions. Loci problems help us visualise geometric relationships and are fundamental to understanding curves and conic sections.",
      },
      {
        id: "add-math-2-s4t2-content-1",
        type: "info",
        content: "**Common Loci**\n\n**1. Points Equidistant from a Fixed Point:**\nThe locus of all points at a fixed distance r from a fixed point (h, k) is a circle.\nEquation: (x − h)² + (y − k)² = r²\n\n**2. Points Equidistant from Two Fixed Points:**\nThe locus of all points equidistant from two points A and B is the perpendicular bisector of line segment AB.\n\n**Example:** Find the locus of points equidistant from A(1, 2) and B(5, 6).\n\nLet P(x, y) be any point on the locus.\nPA = PB\n√[(x − 1)² + (y − 2)²] = √[(x − 5)² + (y − 6)²]\n(x − 1)² + (y − 2)² = (x − 5)² + (y − 6)²\nx² − 2x + 1 + y² − 4y + 4 = x² − 10x + 25 + y² − 12y + 36\n−2x − 4y + 5 = −10x − 12y + 61\n8x + 8y − 56 = 0\nx + y − 7 = 0 (a straight line)",
      },
      {
        id: "add-math-2-s4t2-content-2",
        type: "info",
        content: "**More Complex Loci**\n\n**3. Points at a Fixed Distance from a Line:**\nThe locus is a pair of lines parallel to the given line.\n\n**4. Points Equidistant from Two Parallel Lines:**\nThe locus is a line parallel to both and midway between them.\n\n**5. Points Equidistant from Two Intersecting Lines:**\nThe locus is the pair of angle bisectors of the two lines.\n\n**6. Points Where the Ratio of Distances to Two Fixed Points is Constant:**\nThe locus is a circle (called the Circle of Apollonius).\n\n**Example:** Find the locus of P(x, y) such that PA : PB = 2 : 1, where A(0, 0) and B(6, 0).\n\nPA² = 4PB²\nx² + y² = 4[(x − 6)² + y²]\nx² + y² = 4(x² − 12x + 36 + y²)\nx² + y² = 4x² − 48x + 144 + 4y²\n0 = 3x² + 3y² − 48x + 144\nx² + y² − 16x + 48 = 0\n(x − 8)² + y² = 16 (a circle with centre (8,0), radius 4)",
      },
      {
        id: "add-math-2-s4t2-content-3",
        type: "info",
        content: "**Applications of Loci**\n\n1. **Navigation:** A ship maintaining a constant distance from a lighthouse follows a circular locus.\n\n2. **Broadcasting:** The coverage area of a radio antenna is the locus of all points within a certain distance (circular locus).\n\n3. **Robotics:** The path traced by a robot arm endpoint under certain constraints is a locus.\n\n4. **Astronomy:** Planetary orbits are loci (ellipses) with the sun at one focus.\n\n5. **Engineering:** Cam and gear designs involve loci of points on rotating components.\n\n**Summary of Common Loci:**\n| Condition | Locus |\n|-----------|-------|\n| Fixed distance from a point | Circle |\n| Equal distances from two points | Perpendicular bisector |\n| Fixed distance from a line | Parallel lines |\n| Equal distances from two intersecting lines | Angle bisectors |\n| Fixed ratio of distances to two points | Circle of Apollonius |",
      },
      {
        id: "add-math-2-s4t2-practice",
        type: "question",
        content: "Test your understanding of loci.",
        exercise: {
          question: "The locus of points equidistant from two fixed points A and B is:",
          options: [
            "A circle",
            "The perpendicular bisector of AB",
            "A parabola",
            "The line segment AB"
          ],
          correctIndex: 1,
          explanation: "The perpendicular bisector of line segment AB passes through the midpoint of AB and is perpendicular to it. Every point on this line is equidistant from A and B."
        }
      },
    ],
  },

  // ═══ MODULE 5: VECTORS ═══
  {
    id: "add-math-2-s5t1",
    title: "Vectors in Two and Three Dimensions",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["add-math-2-s4t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s5t1-intro",
        type: "info",
        content: "**Vectors in Two and Three Dimensions**\n\nVectors are quantities that have both magnitude and direction. They are essential in physics (force, velocity, acceleration), engineering, and computer graphics. In SHS 2, we extend vector concepts to three dimensions.",
      },
      {
        id: "add-math-2-s5t1-content-1",
        type: "info",
        content: "**Vector Representation**\n\n**Column Vector Form:**\nIn 2D: a = (x, y)ᵀ or a = x i + y j\nIn 3D: a = (x, y, z)ᵀ or a = x i + y j + z k\n\nWhere i, j, k are unit vectors in the x, y, and z directions.\n\n**Position Vectors:**\nThe position vector of point A is a = OA, the displacement from the origin.\n\n**Vector between two points:**\nAB = b − a = (x₂ − x₁, y₂ − y₁, z₂ − z₁)ᵀ\n\n**Magnitude (Length) of a Vector:**\n|a| = √(x² + y²) in 2D\n|a| = √(x² + y² + z²) in 3D\n\n**Unit Vector:** A vector of length 1 in the direction of a:\nâ = a/|a|",
      },
      {
        id: "add-math-2-s5t1-content-2",
        type: "info",
        content: "**Vector Operations**\n\n**Addition:** a + b = (x₁ + x₂, y₁ + y₂, z₁ + z₂)ᵀ\n**Subtraction:** a − b = (x₁ − x₂, y₁ − y₂, z₁ − z₂)ᵀ\n**Scalar Multiplication:** ka = (kx, ky, kz)ᵀ\n\n**Properties:**\n- a + b = b + a (commutative)\n- a + (b + c) = (a + b) + c (associative)\n- k(a + b) = ka + kb (distributive)\n\n**Dot Product (Scalar Product):**\na · b = |a||b|cos θ = x₁x₂ + y₁y₂ + z₁z₂\n\n**Cross Product (Vector Product — 3D only):**\na × b = |a||b|sin θ · n̂\n= (y₁z₂ − z₁y₂, z₁x₂ − x₁z₂, x₁y₂ − y₁x₂)ᵀ\n\nThe cross product is perpendicular to both a and b.\n\n**Angle between two vectors:**\ncos θ = (a · b)/(|a||b|)",
      },
      {
        id: "add-math-2-s5t1-content-3",
        type: "info",
        content: "**Applications of Vectors**\n\n**Proving Collinearity:**\nThree points A, B, C are collinear if AB = k·BC for some scalar k.\n\n**Dividing a Line Segment in a Given Ratio:**\nPoint P dividing AB in ratio m:n:\nInternal division: p = (n·a + m·b)/(m + n)\nExternal division: p = (n·a − m·b)/(n − m)\n\n**Worked Example:** Find the point P that divides A(1, 2) and B(7, 8) in the ratio 2:1 internally.\n\np = (1·a + 2·b)/(2 + 1)\n= ((1)(1,2) + 2(7,8))/3\n= (1 + 14, 2 + 16)/3\n= (15, 18)/3\n= (5, 6)\n\n**Perpendicular Vectors:**\na · b = 0 if and only if a ⟂ b (vectors are perpendicular).",
      },
      {
        id: "add-math-2-s5t1-practice",
        type: "question",
        content: "Test your understanding of vectors.",
        exercise: {
          question: "If a = (3, −1) and b = (2, 5), what is a · b?",
          options: [
            "(5, 4)",
            "1",
            "11",
            "−1"
          ],
          correctIndex: 1,
          explanation: "a · b = (3)(2) + (−1)(5) = 6 − 5 = 1."
        }
      },
    ],
  },
  {
    id: "add-math-2-s5t2",
    title: "Applications of Vectors in Geometry",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 4,
    estimatedMinutes: 30,
    xpReward: 60,
    prerequisites: ["add-math-2-s5t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s5t2-intro",
        type: "info",
        content: "**Applications of Vectors in Geometry**\n\nVectors provide an elegant and powerful approach to proving geometric theorems and solving geometric problems. By representing points, lines, and planes as vectors, we can express geometric relationships algebraically.",
      },
      {
        id: "add-math-2-s5t2-content-1",
        type: "info",
        content: "**Parametric Equations of Lines**\n\nIn vector form, a line passing through point A (with position vector a) in direction v can be written as:\nr = a + tv, where t is a parameter.\n\nIn 2D: r = (x₀, y₀) + t(x₁, y₁) → x = x₀ + tx₁, y = y₀ + ty₁\n\n**Example:** Find the vector equation of the line through A(2, 3) in direction v = (4, −1).\n\nr = (2, 3) + t(4, −1)\nCartesian form: x = 2 + 4t, y = 3 − t\nEliminating t: t = (x − 2)/4 → y = 3 − (x − 2)/4 = (14 − x)/4\n\n**Equation of a Line through Two Points:**\nr = a + t(b − a)\nor r = (1 − t)a + tb (using section formula)",
      },
      {
        id: "add-math-2-s5t2-content-2",
        type: "info",
        content: "**Proving Geometric Results with Vectors**\n\n**Example 1 — Midpoint Theorem:**\nShow that the line joining the midpoints of two sides of a triangle is parallel to the third side and half its length.\n\nLet triangle have vertices A(a), B(b), C(c).\nMidpoint of AB: m₁ = (a + b)/2\nMidpoint of AC: m₂ = (a + c)/2\nVector m₁m₂ = m₂ − m₁ = (a + c)/2 − (a + b)/2 = (c − b)/2\nVector BC = c − b\n\nSince m₁m₂ = ½·BC, the segment joining midpoints is parallel to BC and half its length. ✓\n\n**Example 2 — Diagonals of a Parallelogram:**\nShow that diagonals of a parallelogram bisect each other.\n\nLet parallelogram OABC with O at origin, A(a), B(a + b), C(b).\nMidpoint of OB = (0 + a + b)/2 = (a + b)/2\nMidpoint of AC = (a + b)/2\nSame midpoint → diagonals bisect each other. ✓",
      },
      {
        id: "add-math-2-s5t2-content-3",
        type: "info",
        content: "**The Vector Equation of a Plane (3D)**\n\nA plane can be defined by a point A(a) and two non-parallel direction vectors u and v:\nr = a + su + tv, where s and t are parameters.\n\n**Normal Form of a Plane:**\nIf n is a vector normal (perpendicular) to the plane, then:\n(r − a) · n = 0\nor r · n = a · n = d (constant)\n\n**Equation of a Plane in Cartesian Form:**\nax + by + cz = d\nwhere (a, b, c) is a normal vector.\n\n**Example:** Find the equation of the plane through A(1, 0, 2) with normal n = (2, −1, 3).\n\n2(x − 1) + (−1)(y − 0) + 3(z − 2) = 0\n2x − 2 − y + 3z − 6 = 0\n2x − y + 3z = 8",
      },
      {
        id: "add-math-2-s5t2-practice",
        type: "question",
        content: "Test your understanding of vector applications.",
        exercise: {
          question: "The vector equation of a line passing through A(1, 2) in direction (3, 4) is:",
          options: [
            "r = (3, 4) + t(1, 2)",
            "r = (1, 2) + t(3, 4)",
            "r = t(3, 4)",
            "r = (1, 2) + (3, 4)"
          ],
          correctIndex: 1,
          explanation: "A line through point A with position vector a in direction v has equation r = a + tv. So r = (1, 2) + t(3, 4)."
        }
      },
    ],
  },

  // ═══ MODULE 6: MATRICES ═══
  {
    id: "add-math-2-s6t1",
    title: "Matrix Operations and Transformations",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["add-math-2-s5t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s6t1-intro",
        type: "info",
        content: "**Matrix Operations and Transformations**\n\nMatrices are rectangular arrays of numbers that represent linear transformations and systems of equations. They are fundamental in computer graphics, engineering, physics, and data science.",
      },
      {
        id: "add-math-2-s6t1-content-1",
        type: "info",
        content: "**Matrix Operations**\n\n**Addition/Subtraction:** Add/subtract corresponding elements. Only possible for matrices of the same dimensions.\n\n**Scalar Multiplication:** Multiply each element by the scalar.\n\n**Matrix Multiplication:**\nTo multiply A (m × n) by B (n × p):\n(AB)ᵢⱼ = Σₖ Aᵢₖ × Bₖⱼ\n\nThe number of columns in A must equal the number of rows in B.\n\n**Properties:**\n- AB ≠ BA generally (not commutative)\n- A(BC) = (AB)C (associative)\n- A(B + C) = AB + AC (distributive)\n\n**Identity Matrix:**\nI₂ = [[1, 0], [0, 1]], I₃ = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]\nAI = IA = A",
      },
      {
        id: "add-math-2-s6t1-content-2",
        type: "info",
        content: "**Determinants and Inverses**\n\n**Determinant of a 2 × 2 Matrix:**\nIf M = [[a, b], [c, d]], then det(M) = ad − bc.\n\n**Inverse of a 2 × 2 Matrix:**\nM⁻¹ = 1/(ad − bc) × [[d, −b], [−c, a]]\nExists only if det(M) ≠ 0.\n\n**Properties of Inverses:**\n- M × M⁻¹ = I\n- (M⁻¹)⁻¹ = M\n- (AB)⁻¹ = B⁻¹A⁻¹\n- det(M⁻¹) = 1/det(M)\n\n**Determinant of a 3 × 3 Matrix:**\nUsing expansion by minors or Sarrus' rule.\n\n**Singular vs. Non-Singular:**\n- If det(M) = 0, the matrix is singular (no inverse).\n- If det(M) ≠ 0, the matrix is non-singular (invertible).",
      },
      {
        id: "add-math-2-s6t1-content-3",
        type: "info",
        content: "**Linear Transformations Using Matrices**\n\nA 2 × 2 matrix represents a linear transformation of the plane.\n\n**Common Transformation Matrices:**\n| Transformation | Matrix | Effect |\n|----------------|--------|--------|\n| Identity | [[1,0],[0,1]] | No change |\n| Reflection in x-axis | [[1,0],[0,−1]] | Flips vertically |\n| Reflection in y-axis | [[−1,0],[0,1]] | Flips horizontally |\n| Reflection in y = x | [[0,1],[1,0]] | Swaps coordinates |\n| Rotation by 90° | [[0,−1],[1,0]] | Anti-clockwise |\n| Rotation by 180° | [[−1,0],[0,−1]] | Half-turn |\n| Enlargement (scale k) | [[k,0],[0,k]] | Scales by factor k |\n\n**Composition of Transformations:**\nIf T₁ has matrix A and T₂ has matrix B, then applying T₁ then T₂:\nResult = B(Av) = (BA)v\nSo the combined matrix is BA (order matters!)",
      },
      {
        id: "add-math-2-s6t1-practice",
        type: "question",
        content: "Test your understanding of matrices.",
        exercise: {
          question: "What is the inverse of the matrix [[2, 1], [5, 3]]?",
          options: [
            "[[3, −1], [−5, 2]]",
            "[[3, −1], [−5, 2]] / 1",
            "[[3, −1], [−5, 2]]",
            "No inverse exists"
          ],
          correctIndex: 2,
          explanation: "det = (2)(3) − (1)(5) = 6 − 5 = 1. M⁻¹ = 1/1 × [[3, −1], [−5, 2]] = [[3, −1], [−5, 2]]."
        }
      },
    ],
  },
  {
    id: "add-math-2-s6t2",
    title: "Solving Systems of Equations Using Matrices",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 4,
    estimatedMinutes: 30,
    xpReward: 60,
    prerequisites: ["add-math-2-s6t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s6t2-intro",
        type: "info",
        content: "**Solving Systems of Equations Using Matrices**\n\nMatrices provide an efficient method for solving systems of linear equations, especially when there are multiple equations with multiple unknowns. This approach is widely used in engineering, economics, and computer science.",
      },
      {
        id: "add-math-2-s6t2-content-1",
        type: "info",
        content: "**Matrix Representation of Linear Systems**\n\nA system of linear equations can be written in matrix form as:\nAX = B\n\nWhere A is the coefficient matrix, X is the column vector of variables, and B is the column vector of constants.\n\n**Example:**\n2x + 3y = 7\n4x − y = 1\n\nbecomes:\n[[2, 3], [4, −1]] × [x, y]ᵀ = [7, 1]ᵀ\n\n**Solving using the Inverse Matrix:**\nAX = B\nA⁻¹AX = A⁻¹B\nIX = A⁻¹B\nX = A⁻¹B\n\nThis gives the unique solution when A is non-singular (det ≠ 0).",
      },
      {
        id: "add-math-2-s6t2-content-2",
        type: "info",
        content: "**Worked Example — Solving 2 × 2 Systems**\n\nSolve:\n2x + 3y = 7\n4x − y = 1\n\nA = [[2, 3], [4, −1]]\ndet(A) = (2)(−1) − (3)(4) = −2 − 12 = −14 ≠ 0\n\nA⁻¹ = 1/(−14) × [[−1, −3], [−4, 2]]\n= [[1/14, 3/14], [4/14, −2/14]] / 1...\nActually: A⁻¹ = 1/(−14) × [[−1, −3], [−4, 2]] (wait that's wrong)\n\nA⁻¹ = 1/(ad − bc) × [[d, −b], [−c, a]]\n= 1/(−14) × [[−1, −3], [−4, 2]]\n= [[1/14, 3/14], [4/14, −2/14]] / 1...\n\nActually let me redo:\nA⁻¹ = 1/(−14) × [[−1, −3], [−4, 2]]\nHmm no. For [[a,b],[c,d]] the inverse is 1/(ad-bc) × [[d,-b],[-c,a]]\nSo A⁻¹ = 1/(−14) × [[−1, −3], [−4, 2]]\n= 1/(−14) × [[−1, −3], [−4, 2]]\n= [[1/14, 3/14], [4/14, −2/14]]\n= [[1/14, 3/14], [2/7, −1/7]]\n\nX = A⁻¹B = [[1/14, 3/14], [2/7, −1/7]] × [7, 1]ᵀ\n= [(1/14)(7) + (3/14)(1), (2/7)(7) + (−1/7)(1)]ᵀ\n= [1/2 + 3/14, 2 − 1/7]ᵀ\n= [7/14 + 3/14, 14/7 − 1/7]ᵀ\n= [10/14, 13/7]ᵀ\n= [5/7, 13/7]ᵀ\n\nCheck:\n2(5/7) + 3(13/7) = 10/7 + 39/7 = 49/7 = 7 ✓\n4(5/7) − 13/7 = 20/7 − 13/7 = 7/7 = 1 ✓",
      },
      {
        id: "add-math-2-s6t2-content-3",
        type: "info",
        content: "**Solving 3 × 3 Systems Using Gaussian Elimination**\n\nGaussian elimination (row reduction) is a systematic method for solving larger systems:\n\n**Steps:**\n1. Write the augmented matrix [A|B].\n2. Use elementary row operations to reduce to row-echelon form.\n   - Swap rows.\n   - Multiply a row by a non-zero constant.\n   - Add a multiple of one row to another.\n3. Back-substitute to find the solution.\n\n**Elementary Row Operations:**\n- Rᵢ ⟷ Rⱼ (swap)\n- kRᵢ → Rᵢ (multiply row by k)\n- Rᵢ + kRⱼ → Rᵢ (add multiple of another row)\n\n**Example:** Solve\nx + y + z = 6\n2x − y + z = 3\nx + 2y − z = 2\n\nAugmented matrix:\n[[1, 1, 1 | 6],\n [2, −1, 1 | 3],\n [1, 2, −1 | 2]]\n\nR₂ → R₂ − 2R₁:\n[[1, 1, 1 | 6],\n [0, −3, −1 | −9],\n [1, 2, −1 | 2]]\n\nR₃ → R₃ − R₁:\n[[1, 1, 1 | 6],\n [0, −3, −1 | −9],\n [0, 1, −2 | −4]]\n\nRow operations continue... The solution is x = 1, y = 2, z = 3.",
      },
      {
        id: "add-math-2-s6t2-practice",
        type: "question",
        content: "Test your understanding of solving systems with matrices.",
        exercise: {
          question: "To solve a system of equations AX = B using matrices, we compute:",
          options: [
            "X = A⁻¹B",
            "X = BA⁻¹",
            "X = B⁻¹A",
            "X = AB⁻¹"
          ],
          correctIndex: 0,
          explanation: "Given AX = B, multiply both sides by A⁻¹ on the left: A⁻¹AX = A⁻¹B → IX = X = A⁻¹B."
        }
      },
    ],
  },

  // ═══ MODULE 7: CORRELATION ═══
  {
    id: "add-math-2-s7t1",
    title: "Scatter Diagrams and Correlation",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 2,
    estimatedMinutes: 20,
    xpReward: 40,
    prerequisites: ["add-math-2-s6t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s7t1-intro",
        type: "info",
        content: "**Scatter Diagrams and Correlation**\n\nCorrelation measures the strength and direction of the linear relationship between two variables. Scatter diagrams (scatter plots) provide a visual representation of this relationship, helping us identify patterns, trends, and outliers.",
      },
      {
        id: "add-math-2-s7t1-content-1",
        type: "info",
        content: "**Scatter Diagrams**\n\nA scatter diagram plots paired data (x, y) as points on a coordinate plane.\n\n**Interpreting Scatter Diagrams:**\n- **Positive Correlation:** As x increases, y tends to increase. Points cluster around an upward-sloping line.\n- **Negative Correlation:** As x increases, y tends to decrease. Points cluster around a downward-sloping line.\n- **No Correlation:** No apparent pattern — points are randomly scattered.\n- **Non-linear Relationship:** Points follow a curve rather than a straight line.\n\n**Strength of Correlation:**\n- **Strong:** Points are tightly clustered around a line.\n- **Weak:** Points are widely scattered around a line.\n- **Perfect:** All points lie exactly on a straight line.",
      },
      {
        id: "add-math-2-s7t1-content-2",
        type: "info",
        content: "**Pearson's Product-Moment Correlation Coefficient (r)**\n\nThe correlation coefficient r quantifies the strength and direction of a linear relationship:\n\nr = Σ[(xᵢ − x̄)(yᵢ − ȳ)] / √[Σ(xᵢ − x̄)² × Σ(yᵢ − ȳ)²]\n\nAlternatively:\nr = [nΣxy − (Σx)(Σy)] / √[nΣx² − (Σx)²] × √[nΣy² − (Σy)²]\n\n**Properties of r:**\n- −1 ≤ r ≤ 1\n- r = 1: perfect positive correlation\n- r = −1: perfect negative correlation\n- r = 0: no linear correlation\n- r > 0: positive correlation\n- r < 0: negative correlation\n\n**Strength Guidelines:**\n| |r| | Strength |\n|-----|----------|\n| 0.0–0.3 | Weak |\n| 0.3–0.7 | Moderate |\n| 0.7–1.0 | Strong |",
      },
      {
        id: "add-math-2-s7t1-content-3",
        type: "info",
        content: "**Causation vs. Correlation**\n\n**Important:** Correlation does NOT imply causation!\n\nTwo variables may be strongly correlated without one causing the other:\n- There may be a **lurking (confounding) variable** affecting both.\n- The correlation may be **coincidental**.\n- The relationship may be **bidirectional**.\n\n**Example:** Ice cream sales and drowning incidents are positively correlated. But eating ice cream does not cause drowning — both are caused by hot weather (the lurking variable).\n\n**When Can Causation Be Inferred?**\n1. Controlled experiments (randomised trials).\n2. Strong theoretical basis.\n3. Consistent evidence across multiple studies.\n4. Temporal sequence (cause precedes effect).\n\n**The Spearman's Rank Correlation Coefficient (ρ):**\nUsed when data is ordinal (ranked) or when the relationship is monotonic but not necessarily linear.\nρ = 1 − [6Σd²]/[n(n² − 1)]\nwhere d is the difference between ranks.",
      },
      {
        id: "add-math-2-s7t1-practice",
        type: "question",
        content: "Test your understanding of correlation.",
        exercise: {
          question: "A correlation coefficient of r = −0.85 indicates:",
          options: [
            "A weak positive correlation",
            "A strong negative correlation",
            "No correlation",
            "A perfect negative correlation"
          ],
          correctIndex: 1,
          explanation: "r = −0.85 is close to −1, indicating a strong negative correlation. As one variable increases, the other tends to decrease strongly."
        }
      },
    ],
  },
  {
    id: "add-math-2-s7t2",
    title: "Linear Regression and Line of Best Fit",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["add-math-2-s7t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s7t2-intro",
        type: "info",
        content: "**Linear Regression and Line of Best Fit**\n\nLinear regression finds the straight line that best represents the relationship between two variables. This line can be used to predict values of one variable from values of the other.",
      },
      {
        id: "add-math-2-s7t2-content-1",
        type: "info",
        content: "**The Regression Line Equation**\n\nThe line of best fit (least squares regression line) has equation:\ny = a + bx or y = mx + c\n\nWhere:\nb = [nΣxy − (Σx)(Σy)] / [nΣx² − (Σx)²]\na = ȳ − bx̄\n\nb is the slope — the change in y for a unit change in x.\na is the y-intercept.\n\nThe regression line is the line that minimises the sum of squared vertical distances from data points to the line.\n\n**Two Regression Lines:**\n- Regression of y on x: y = a + bx (predicts y from x)\n- Regression of x on y: x = a' + b'y (predicts x from y)",
      },
      {
        id: "add-math-2-s7t2-content-2",
        type: "info",
        content: "**Worked Example — Fitting a Regression Line**\n\nFind the regression line of y on x for the data:\n| x | 1 | 2 | 3 | 4 | 5 |\n| y | 3 | 5 | 6 | 8 | 10 |\n\nn = 5\nΣx = 1 + 2 + 3 + 4 + 5 = 15\nΣy = 3 + 5 + 6 + 8 + 10 = 32\nΣxy = (1×3) + (2×5) + (3×6) + (4×8) + (5×10) = 3 + 10 + 18 + 32 + 50 = 113\nΣx² = 1 + 4 + 9 + 16 + 25 = 55\nx̄ = 15/5 = 3, ȳ = 32/5 = 6.4\n\nb = [5(113) − (15)(32)] / [5(55) − (15)²]\n= [565 − 480] / [275 − 225]\n= 85 / 50 = 1.7\n\na = 6.4 − 1.7(3) = 6.4 − 5.1 = 1.3\n\nRegression line: y = 1.3 + 1.7x\n\n**Prediction:** When x = 6, y = 1.3 + 1.7(6) = 1.3 + 10.2 = 11.5",
      },
      {
        id: "add-math-2-s7t2-content-3",
        type: "info",
        content: "**Interpreting and Using the Regression Line**\n\n**Interpolation vs. Extrapolation:**\n- **Interpolation:** Predicting within the range of observed x-values (reliable).\n- **Extrapolation:** Predicting outside the range of observed x-values (less reliable — the relationship may change).\n\n**Residuals:**\nA residual is the vertical distance from a data point to the regression line:\nResidual = observed y − predicted y\n\n**Properties of Residuals:**\n- Sum of residuals = 0 (always)\n- Positive residual: point is above the line\n- Negative residual: point is below the line\n- Residual plot: if residuals show no pattern, the linear model is appropriate.\n\n**Coefficient of Determination (r²):**\n- r² = (correlation coefficient)²\n- Represents the proportion of variation in y explained by x.\n- If r = 0.9, then r² = 0.81, meaning 81% of variation in y is explained by x.",
      },
      {
        id: "add-math-2-s7t2-practice",
        type: "question",
        content: "Test your understanding of linear regression.",
        exercise: {
          question: "If the regression line is y = 2 + 0.5x, what is the predicted y when x = 10?",
          options: [
            "5",
            "7",
            "12",
            "2.5"
          ],
          correctIndex: 1,
          explanation: "y = 2 + 0.5(10) = 2 + 5 = 7."
        }
      },
    ],
  },

  // ═══ MODULE 8: INDICES AND LOGARITHMS ═══
  {
    id: "add-math-2-s8t1",
    title: "Laws of Indices and Exponential Equations",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["add-math-2-s7t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s8t1-intro",
        type: "info",
        content: "**Laws of Indices and Exponential Equations**\n\nIndices (exponents) and logarithms are powerful tools for working with exponential relationships. In SHS 2, we extend our knowledge to solve complex exponential equations and apply them to real-world growth and decay problems.",
      },
      {
        id: "add-math-2-s8t1-content-1",
        type: "info",
        content: "**Review of the Laws of Indices**\n\nFor any positive numbers a, b and rational exponents m, n:\n\n1. aᵐ × aⁿ = aᵐ⁺ⁿ\n2. aᵐ ÷ aⁿ = aᵐ⁻ⁿ\n3. (aᵐ)ⁿ = aᵐⁿ\n4. (ab)ⁿ = aⁿbⁿ\n5. (a/b)ⁿ = aⁿ/bⁿ\n6. a⁰ = 1 (a ≠ 0)\n7. a⁻ⁿ = 1/aⁿ\n8. a¹ᐟⁿ = ⁿ√a\n9. aᵐᐟⁿ = (ⁿ√a)ᵐ = ⁿ√(aᵐ)\n\n**Worked Example — Simplifying Indices:**\nSimplify (2x²y⁻³)³ × (4x⁻¹y²)⁻²\n\n= (8x⁶y⁻⁹) × (4⁻²x²y⁻⁴)\n= (8x⁶y⁻⁹) × (x²y⁻⁴/16)\n= (8/16)x⁸y⁻¹³\n= x⁸/(2y¹³)",
      },
      {
        id: "add-math-2-s8t1-content-2",
        type: "info",
        content: "**Solving Exponential Equations**\n\nMethod 1: Equating Bases\nIf aᵐ = aⁿ, then m = n (for a > 0, a ≠ 1).\n\n**Example:** Solve 2ˣ⁺¹ = 16\n2ˣ⁺¹ = 2⁴\nx + 1 = 4\nx = 3\n\n**Example:** Solve 3²ˣ⁻¹ = 27ˣ⁺²\n3²ˣ⁻¹ = 3³⁽ˣ⁺²⁾\n2x − 1 = 3x + 6\n−x = 7\nx = −7\n\n**Example:** Solve 4ˣ = 8ˣ⁻¹\n(2²)ˣ = (2³)ˣ⁻¹\n2²ˣ = 2³ˣ⁻³\n2x = 3x − 3\n−x = −3\nx = 3",
      },
      {
        id: "add-math-2-s8t1-content-3",
        type: "info",
        content: "**Method 2: Using Logarithms**\n\nWhen bases cannot be made equal:\n\n**Example:** Solve 3ˣ = 20\nTake logarithms of both sides (any base):\nlog(3ˣ) = log(20)\nx·log(3) = log(20)\nx = log(20)/log(3)\nx ≈ 2.727\n\n**Example:** Solve 2²ˣ⁺¹ = 5ˣ⁻²\nlog(2²ˣ⁺¹) = log(5ˣ⁻²)\n(2x + 1)log(2) = (x − 2)log(5)\n2x·log(2) + log(2) = x·log(5) − 2·log(5)\n2x·log(2) − x·log(5) = −2·log(5) − log(2)\nx[2·log(2) − log(5)] = −[2·log(5) + log(2)]\nx = −[2·log(5) + log(2)] / [2·log(2) − log(5)]\nx = −[2(0.6990) + 0.3010] / [2(0.3010) − 0.6990]\nx = −[1.398 + 0.3010] / [0.602 − 0.699]\nx = −1.699 / (−0.097)\nx ≈ 17.52",
      },
      {
        id: "add-math-2-s8t1-practice",
        type: "question",
        content: "Test your understanding of indices and exponential equations.",
        exercise: {
          question: "Solve the equation: 2ˣ = 32",
          options: [
            "4",
            "5",
            "6",
            "16"
          ],
          correctIndex: 1,
          explanation: "32 = 2⁵, so 2ˣ = 2⁵ and x = 5."
        }
      },
    ],
  },
  {
    id: "add-math-2-s8t2",
    title: "Properties of Logarithms and Applications",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["add-math-2-s8t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s8t2-intro",
        type: "info",
        content: "**Properties of Logarithms and Applications**\n\nLogarithms are the inverse of exponentials. They are essential in many scientific and engineering fields, from measuring earthquake intensity (Richter scale) to sound intensity (decibels) and acid concentration (pH scale).",
      },
      {
        id: "add-math-2-s8t2-content-1",
        type: "info",
        content: "**Definition of Logarithms**\n\nIf bʸ = x, then log_b(x) = y\n\nWhere b > 0, b ≠ 1, and x > 0.\n\n**Common Logarithms:**\n- log₁₀(x) = log(x) (base 10, common log)\n- log_e(x) = ln(x) (natural log, base e ≈ 2.71828)\n\n**The Laws of Logarithms:**\n\n1. log_b(xy) = log_b(x) + log_b(y)\n   (Log of product = sum of logs)\n\n2. log_b(x/y) = log_b(x) − log_b(y)\n   (Log of quotient = difference of logs)\n\n3. log_b(xⁿ) = n·log_b(x)\n   (Log of power = power × log)\n\n4. log_b(1) = 0 (any base)\n\n5. log_b(b) = 1\n\n6. log_b(1/x) = −log_b(x) (from Law 2)",
      },
      {
        id: "add-math-2-s8t2-content-2",
        type: "info",
        content: "**Change of Base Formula**\n\nlog_b(x) = log_a(x) / log_a(b)\n\nThis allows us to convert between different bases, especially useful when using calculators with only log₁₀ and ln.\n\n**Example:** Evaluate log₂(5).\nlog₂(5) = log(5)/log(2) ≈ 0.6990/0.3010 ≈ 2.322\n\n**Example:** Solve log₂(x) + log₂(x + 2) = 3\n\nUsing Law 1:\nlog₂[x(x + 2)] = 3\nx(x + 2) = 2³\nx² + 2x − 8 = 0\n(x + 4)(x − 2) = 0\nx = −4 or x = 2\n\nCheck domains:\nx > 0 and x + 2 > 0 (log arguments must be positive)\nFor x = −4: log₂(−4) is undefined. Discard.\nFor x = 2: log₂(2) + log₂(4) = 1 + 2 = 3 ✓\n\nSolution: x = 2",
      },
      {
        id: "add-math-2-s8t2-content-3",
        type: "info",
        content: "**Real-World Applications of Logarithms**\n\n**1. Exponential Growth and Decay:**\nN = N₀eᵏᵗ or N = N₀aᵗ\n- Population growth\n- Radioactive decay (half-life)\n- Bacterial growth\n- Compound interest\n\n**Worked Example — Bacterial Growth:**\nA culture initially has 1000 bacteria and doubles every hour. How long until it reaches 8000?\n\nN = 1000 × 2ᵗ\n8000 = 1000 × 2ᵗ\n8 = 2ᵗ\nt = log₂(8) = 3 hours\n\n**Worked Example — Half-Life:**\nA radioactive substance has a half-life of 10 years. What fraction remains after 25 years?\n\nN = N₀(½)ᵗ/¹⁰\nN/N₀ = (½)²·⁵ = 2⁻²·⁵ ≈ 0.177\nAbout 17.7% remains.\n\n**2. pH Scale:**\npH = −log₁₀[H⁺]\n\n**3. Richter Scale:**\nM = log₁₀(I/I₀) where I is earthquake intensity.",
      },
      {
        id: "add-math-2-s8t2-practice",
        type: "question",
        content: "Test your understanding of logarithms.",
        exercise: {
          question: "Evaluate log₂(8) + log₂(4):",
          options: [
            "3",
            "5",
            "6",
            "2"
          ],
          correctIndex: 1,
          explanation: "log₂(8) = 3, log₂(4) = 2. So 3 + 2 = 5. Alternatively, log₂(8×4) = log₂(32) = 5."
        }
      },
    ],
  },

  // ═══ MODULE 9: TRIGONOMETRIC IDENTITIES ═══
  {
    id: "add-math-2-s9t1",
    title: "Trigonometric Ratios and Compound Angle Formulae",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["add-math-2-s8t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s9t1-intro",
        type: "info",
        content: "**Trigonometric Ratios and Compound Angle Formulae**\n\nTrigonometry deals with the relationships between angles and sides of triangles. In SHS 2, we extend trigonometric knowledge by exploring compound angle formulae, which allow us to find exact values for angles that are sums or differences of known angles.",
      },
      {
        id: "add-math-2-s9t1-content-1",
        type: "info",
        content: "**Review of Basic Trigonometric Ratios**\n\nsin θ = opposite/hypotenuse\ncos θ = adjacent/hypotenuse\ntan θ = opposite/adjacent = sin θ/cos θ\n\n**Exact Values for Special Angles:**\n| θ | sin θ | cos θ | tan θ |\n|---|---|---|---|\n| 0° | 0 | 1 | 0 |\n| 30° | ½ | √3/2 | 1/√3 |\n| 45° | √2/2 | √2/2 | 1 |\n| 60° | √3/2 | ½ | √3 |\n| 90° | 1 | 0 | ∞ |\n\n**Fundamental Identities:**\n- sin²θ + cos²θ = 1\n- 1 + tan²θ = sec²θ\n- 1 + cot²θ = csc²θ",
      },
      {
        id: "add-math-2-s9t1-content-2",
        type: "info",
        content: "**Compound Angle Formulae**\n\nThese formulae express trigonometric functions of A ± B in terms of functions of A and B.\n\n**Sine Addition/Subtraction:**\nsin(A + B) = sin A cos B + cos A sin B\nsin(A − B) = sin A cos B − cos A sin B\n\n**Cosine Addition/Subtraction:**\ncos(A + B) = cos A cos B − sin A sin B\ncos(A − B) = cos A cos B + sin A sin B\n\n**Tangent Addition/Subtraction:**\ntan(A + B) = (tan A + tan B)/(1 − tan A tan B)\ntan(A − B) = (tan A − tan B)/(1 + tan A tan B)\n\n**Worked Example — Exact Value:**\nFind the exact value of sin 75°.\n\n75° = 45° + 30°\nsin 75° = sin(45° + 30°)\n= sin 45° cos 30° + cos 45° sin 30°\n= (√2/2)(√3/2) + (√2/2)(1/2)\n= √6/4 + √2/4\n= (√6 + √2)/4",
      },
      {
        id: "add-math-2-s9t1-content-3",
        type: "info",
        content: "**Double Angle Formulae**\n\nDerived from compound angle formulae by setting A = B:\n\n**Sine:**\nsin(2A) = 2 sin A cos A\n\n**Cosine:**\ncos(2A) = cos²A − sin²A\n        = 2 cos²A − 1\n        = 1 − 2 sin²A\n\n**Tangent:**\ntan(2A) = 2 tan A/(1 − tan²A)\n\n**Worked Example:** Given sin A = 3/5 (A in first quadrant), find sin(2A).\n\ncos A = √(1 − sin²A) = √(1 − 9/25) = √(16/25) = 4/5\nsin(2A) = 2 sin A cos A = 2(3/5)(4/5) = 24/25\n\n**Applications of Compound Angle Formulae:**\n- Simplifying trigonometric expressions\n- Solving trigonometric equations\n- Deriving the sine, cosine, and tangent of multiples angles\n- Wave interference in physics (superposition of waves)",
      },
      {
        id: "add-math-2-s9t1-practice",
        type: "question",
        content: "Test your understanding of compound angle formulae.",
        exercise: {
          question: "Using the compound angle formula, cos(60° + 30°) equals:",
          options: [
            "cos 60° cos 30° + sin 60° sin 30°",
            "cos 60° cos 30° − sin 60° sin 30°",
            "sin 60° cos 30° + cos 60° sin 30°",
            "cos 60° − cos 30°"
          ],
          correctIndex: 1,
          explanation: "cos(A + B) = cos A cos B − sin A sin B. So cos(60° + 30°) = cos 60° cos 30° − sin 60° sin 30°."
        }
      },
    ],
  },
  {
    id: "add-math-2-s9t2",
    title: "Trigonometric Identities and Equations",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 4,
    estimatedMinutes: 30,
    xpReward: 60,
    prerequisites: ["add-math-2-s9t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s9t2-intro",
        type: "info",
        content: "**Trigonometric Identities and Equations**\n\nTrigonometric identities are equations that hold true for all values of the variables. They are used to simplify expressions, prove relationships, and solve trigonometric equations that arise in geometry, physics, and engineering.",
      },
      {
        id: "add-math-2-s9t2-content-1",
        type: "info",
        content: "**Proving Trigonometric Identities**\n\nTo prove a trigonometric identity, we manipulate one side (usually the more complex side) until it matches the other side.\n\n**Strategies:**\n1. Convert everything to sines and cosines.\n2. Use fundamental identities (sin²θ + cos²θ = 1).\n3. Factor expressions.\n4. Combine fractions.\n5. Use compound/double angle formulae.\n\n**Example 1:** Prove that tan θ + cot θ = sec θ csc θ\n\nLHS = tan θ + cot θ\n= sin θ/cos θ + cos θ/sin θ\n= (sin²θ + cos²θ)/(sin θ cos θ)\n= 1/(sin θ cos θ)\n= sec θ csc θ = RHS ✓",
      },
      {
        id: "add-math-2-s9t2-content-2",
        type: "info",
        content: "**Example 2:** Prove that sin²θ cos²θ = ⅛(1 − cos 4θ)\n\nRHS = ⅛(1 − cos 4θ)\ncos 4θ = cos(2·2θ) = 2 cos²(2θ) − 1\n= 2(2 cos²θ − 1)² − 1\n= 2(4 cos⁴θ − 4 cos²θ + 1) − 1\n= 8 cos⁴θ − 8 cos²θ + 2 − 1\n= 8 cos⁴θ − 8 cos²θ + 1\n\nSo 1 − cos 4θ = 1 − (8 cos⁴θ − 8 cos²θ + 1)\n= −8 cos⁴θ + 8 cos²θ\n= 8 cos²θ(1 − cos²θ)\n= 8 cos²θ sin²θ\n\nRHS = ⅛ × 8 cos²θ sin²θ = sin²θ cos²θ = LHS ✓\n\n**Alternative:** Use sin²θ cos²θ = (sin 2θ/2)² = sin²2θ/4\nThen sin²2θ = (1 − cos 4θ)/2\nSo sin²θ cos²θ = (1 − cos 4θ)/8",
      },
      {
        id: "add-math-2-s9t2-content-3",
        type: "info",
        content: "**Solving Trigonometric Equations**\n\n**General Approach:**\n1. Use trigonometric identities to simplify the equation.\n2. Solve for the trigonometric function.\n3. Find all solutions in the given interval.\n4. Express the general solution if required.\n\n**Example 1:** Solve 2 sin²x + sin x − 1 = 0 for 0° ≤ x ≤ 360°.\n\nLet u = sin x.\n2u² + u − 1 = 0\n(2u − 1)(u + 1) = 0\nu = ½ or u = −1\n\nsin x = ½ → x = 30°, 150°\nsin x = −1 → x = 270°\n\nSolutions: x = 30°, 150°, 270°\n\n**Example 2:** Solve cos 2x + sin x = 0 for 0 ≤ x ≤ 2π.\n\ncos 2x + sin x = 0\n(1 − 2 sin²x) + sin x = 0\n−2 sin²x + sin x + 1 = 0\n2 sin²x − sin x − 1 = 0\n(2 sin x + 1)(sin x − 1) = 0\nsin x = −½ or sin x = 1\n\nsin x = −½ → x = 7π/6, 11π/6\nsin x = 1 → x = π/2\n\nSolutions: x = π/2, 7π/6, 11π/6",
      },
      {
        id: "add-math-2-s9t2-practice",
        type: "question",
        content: "Test your understanding of trigonometric equations.",
        exercise: {
          question: "Solve sin θ = ½ for 0° ≤ θ ≤ 180°.",
          options: [
            "θ = 30° only",
            "θ = 30°, 150°",
            "θ = 60°, 120°",
            "θ = 30°, 330°"
          ],
          correctIndex: 1,
          explanation: "sin θ = ½ has solutions at θ = 30° (first quadrant) and θ = 150° (second quadrant) in the range 0° to 180°."
        }
      },
    ],
  },

  // ═══ MODULE 10: DIFFERENTIATION ═══
  {
    id: "add-math-2-s10t1",
    title: "Introduction to Differentiation and Derivatives",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 4,
    estimatedMinutes: 30,
    xpReward: 60,
    prerequisites: ["add-math-2-s9t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s10t1-intro",
        type: "info",
        content: "**Introduction to Differentiation and Derivatives**\n\nCalculus is the mathematics of change. Differentiation is the process of finding the derivative — the instantaneous rate of change of a function. It has applications in physics (velocity, acceleration), economics (marginal cost, marginal revenue), and optimisation.",
      },
      {
        id: "add-math-2-s10t1-content-1",
        type: "info",
        content: "**The Concept of a Derivative**\n\nThe derivative of a function f(x) at a point is the slope of the tangent line at that point.\n\n**Limit Definition (First Principles):**\nf'(x) = lim_{h→0} [f(x + h) − f(x)]/h\n\n**Example:** Find the derivative of f(x) = x² from first principles.\n\nf'(x) = lim_{h→0} [(x + h)² − x²]/h\n= lim_{h→0} [x² + 2xh + h² − x²]/h\n= lim_{h→0} [2xh + h²]/h\n= lim_{h→0} [2x + h]\n= 2x\n\nSo the derivative of x² is 2x.\n\n**Notation:**\n- f'(x) (Lagrange notation)\n- dy/dx (Leibniz notation)\n- y' (prime notation)",
      },
      {
        id: "add-math-2-s10t1-content-2",
        type: "info",
        content: "**Standard Derivatives**\n\n| Function f(x) | Derivative f'(x) |\n|--------------|----------------|\n| k (constant) | 0 |\n| xⁿ | nxⁿ⁻¹ |\n| eˣ | eˣ |\n| ln x | 1/x |\n| sin x | cos x |\n| cos x | −sin x |\n| tan x | sec²x |\n| k·f(x) | k·f'(x) |\n\n**Rules of Differentiation:**\n\n1. **Sum Rule:** (f + g)' = f' + g'\n2. **Difference Rule:** (f − g)' = f' − g'\n3. **Constant Multiple Rule:** (kf)' = kf'\n4. **Product Rule:** (fg)' = f'g + fg'\n5. **Quotient Rule:** (f/g)' = (f'g − fg')/g²\n6. **Chain Rule:** f(g(x))' = f'(g(x))·g'(x)",
      },
      {
        id: "add-math-2-s10t1-content-3",
        type: "info",
        content: "**Worked Examples**\n\n**Example 1:** Find dy/dx if y = 3x⁴ − 2x³ + 5x − 7\n\ndy/dx = 12x³ − 6x² + 5\n\n**Example 2 (Product Rule):** Differentiate y = x²sin x\n\nLet u = x², v = sin x\nu' = 2x, v' = cos x\n\ndy/dx = u'v + uv'\n= (2x)(sin x) + (x²)(cos x)\n= 2x sin x + x² cos x\n\n**Example 3 (Chain Rule):** Differentiate y = (2x³ + 1)⁵\n\nLet u = 2x³ + 1, then y = u⁵\ndy/du = 5u⁴, du/dx = 6x²\n\ndy/dx = dy/du × du/dx\n= 5u⁴ × 6x²\n= 30x²(2x³ + 1)⁴\n\n**Example 4 (Quotient Rule):** Differentiate y = (x² + 1)/(x − 2)\n\nLet u = x² + 1, v = x − 2\nu' = 2x, v' = 1\n\ndy/dx = (u'v − uv')/v²\n= [(2x)(x − 2) − (x² + 1)(1)]/(x − 2)²\n= [2x² − 4x − x² − 1]/(x − 2)²\n= (x² − 4x − 1)/(x − 2)²",
      },
      {
        id: "add-math-2-s10t1-practice",
        type: "question",
        content: "Test your understanding of differentiation.",
        exercise: {
          question: "What is the derivative of y = 5x³?",
          options: [
            "5x²",
            "15x²",
            "15x³",
            "5x⁴/4"
          ],
          correctIndex: 1,
          explanation: "Using the power rule: d/dx(5x³) = 5 × 3x² = 15x²."
        }
      },
    ],
  },
  {
    id: "add-math-2-s10t2",
    title: "Applications of Differentiation — Tangents, Normals and Stationary Points",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 4,
    estimatedMinutes: 30,
    xpReward: 60,
    prerequisites: ["add-math-2-s10t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s10t2-intro",
        type: "info",
        content: "**Applications of Differentiation**\n\nDifferentiation has many practical applications, from finding the slope of a curve at a point to solving optimisation problems. This lesson explores tangents, normals, stationary points, and their real-world applications.",
      },
      {
        id: "add-math-2-s10t2-content-1",
        type: "info",
        content: "**Tangents and Normals**\n\n**Tangent Line:**\nThe gradient of the tangent at point (x₁, y₁) is m_T = f'(x₁).\nEquation: y − y₁ = m_T(x − x₁)\n\n**Normal Line:**\nThe normal is perpendicular to the tangent.\nm_N × m_T = −1, so m_N = −1/m_T\nEquation: y − y₁ = m_N(x − x₁)\n\n**Worked Example:** Find the equations of the tangent and normal to y = x³ − 2x at the point where x = 1.\n\nf(x) = x³ − 2x, f'(x) = 3x² − 2\nAt x = 1: y = 1 − 2 = −1, f'(1) = 3 − 2 = 1\n\nTangent: y + 1 = 1(x − 1) → y = x − 2\nNormal: m_N = −1/1 = −1\ny + 1 = −1(x − 1) → y + 1 = −x + 1 → y = −x",
      },
      {
        id: "add-math-2-s10t2-content-2",
        type: "info",
        content: "**Stationary (Critical) Points**\n\nA stationary point occurs where f'(x) = 0.\n\n**Types of Stationary Points:**\n\n1. **Local Maximum:** The function changes from increasing to decreasing.\n   - f'(x) changes from + to −.\n   - f''(x) < 0.\n\n2. **Local Minimum:** The function changes from decreasing to increasing.\n   - f'(x) changes from − to +.\n   - f''(x) > 0.\n\n3. **Point of Inflection (with horizontal tangent):**\n   - f'(x) does not change sign.\n   - f''(x) = 0 and f'''(x) ≠ 0.\n\n**Worked Example:** Find and classify the stationary points of f(x) = x³ − 6x² + 9x + 1.\n\nf'(x) = 3x² − 12x + 9 = 0\n3(x² − 4x + 3) = 0\n3(x − 1)(x − 3) = 0\nx = 1 or x = 3\n\nf''(x) = 6x − 12\nAt x = 1: f''(1) = 6 − 12 = −6 < 0 → Local Maximum\nAt x = 3: f''(3) = 18 − 12 = 6 > 0 → Local Minimum\n\nf(1) = 1 − 6 + 9 + 1 = 5 → Max at (1, 5)\nf(3) = 27 − 54 + 27 + 1 = 1 → Min at (3, 1)",
      },
      {
        id: "add-math-2-s10t2-content-3",
        type: "info",
        content: "**Optimisation Problems**\n\nOptimisation uses derivatives to find maximum or minimum values in real-world contexts.\n\n**Worked Example — Maximising Area:**\nA farmer has 100 metres of fencing and wants to enclose a rectangular field against a river (no fencing needed on the river side). Find the maximum area.\n\nLet width = w, length = l.\nFencing: 2w + l = 100 → l = 100 − 2w\nArea: A = w × l = w(100 − 2w) = 100w − 2w²\n\ndA/dw = 100 − 4w = 0 → w = 25\nl = 100 − 50 = 50\nMaximum Area = 25 × 50 = 1250 m²\n\nd²A/dw² = −4 < 0 → confirms maximum.\n\n**Worked Example — Minimising Cost:**\nA closed cylindrical can must hold 1000 cm³ of liquid. Find the dimensions that minimise the surface area (and thus material cost).\n\nV = πr²h = 1000 → h = 1000/πr²\nSA = 2πr² + 2πrh = 2πr² + 2πr(1000/πr²) = 2πr² + 2000/r\n\nd(SA)/dr = 4πr − 2000/r² = 0\n4πr³ = 2000\nr = (500/π)¹ᐟ³ ≈ 5.42 cm\nh = 1000/π(5.42)² ≈ 10.84 cm\n\nMinimum SA ≈ 553.6 cm²",
      },
      {
        id: "add-math-2-s10t2-practice",
        type: "question",
        content: "Test your understanding of applications of differentiation.",
        exercise: {
          question: "At a stationary point of a function f(x), what must be true?",
          options: [
            "f(x) = 0",
            "f'(x) = 0",
            "f''(x) = 0",
            "f'(x) > 0"
          ],
          correctIndex: 1,
          explanation: "By definition, a stationary point occurs where the derivative equals zero: f'(x) = 0."
        }
      },
    ],
  },

  // ═══ MODULE 11: INTEGRATION ═══
  {
    id: "add-math-2-s11t1",
    title: "Integration as the Reverse of Differentiation",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 4,
    estimatedMinutes: 30,
    xpReward: 60,
    prerequisites: ["add-math-2-s10t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s11t1-intro",
        type: "info",
        content: "**Integration as the Reverse of Differentiation**\n\nIntegration (antidifferentiation) is the inverse process of differentiation. Just as differentiation finds the rate of change, integration finds the original function from its rate of change. Together, differentiation and integration form the two fundamental operations of calculus.",
      },
      {
        id: "add-math-2-s11t1-content-1",
        type: "info",
        content: "**Indefinite Integrals**\n\nThe indefinite integral of f(x) with respect to x is written:\n∫f(x) dx = F(x) + C\n\nWhere F'(x) = f(x) and C is the constant of integration.\n\n**Standard Integrals:**\n| Function f(x) | Integral ∫f(x) dx |\n|--------------|-------------------|\n| k (constant) | kx + C |\n| xⁿ (n ≠ −1) | xⁿ⁺¹/(n + 1) + C |\n| 1/x | ln|x| + C |\n| eˣ | eˣ + C |\n| sin x | −cos x + C |\n| cos x | sin x + C |\n| sec²x | tan x + C |\n\n**Properties:**\n1. ∫[f(x) ± g(x)] dx = ∫f(x) dx ± ∫g(x) dx\n2. ∫k·f(x) dx = k∫f(x) dx\n\n**Worked Examples:**\n∫(3x² + 2x) dx = x³ + x² + C\n∫(1/x²) dx = ∫x⁻² dx = x⁻¹/(−1) + C = −1/x + C",
      },
      {
        id: "add-math-2-s11t1-content-2",
        type: "info",
        content: "**Finding the Constant of Integration**\n\nGiven a derivative and a point on the original function, we can determine C.\n\n**Example:** If f'(x) = 2x + 3 and f(1) = 7, find f(x).\n\nf(x) = ∫(2x + 3) dx = x² + 3x + C\n\nf(1) = 1² + 3(1) + C = 4 + C = 7\nC = 3\n\nSo f(x) = x² + 3x + 3\n\n**Integration of (ax + b)ⁿ:**\n∫(ax + b)ⁿ dx = (ax + b)ⁿ⁺¹/[a(n + 1)] + C (n ≠ −1)\n\n**Example:** ∫(2x + 1)³ dx\n= (2x + 1)⁴/[2(4)] + C\n= (2x + 1)⁴/8 + C\n\n**Integration of 1/(ax + b):**\n∫1/(ax + b) dx = (1/a)ln|ax + b| + C",
      },
      {
        id: "add-math-2-s11t1-content-3",
        type: "info",
        content: "**Integration of Trigonometric Functions**\n\n∫sin(ax + b) dx = −(1/a)cos(ax + b) + C\n∫cos(ax + b) dx = (1/a)sin(ax + b) + C\n∫sec²(ax + b) dx = (1/a)tan(ax + b) + C\n\n**Applications of Integration in Kinematics:**\n\nIf acceleration a(t) is given:\n- Velocity v(t) = ∫a(t) dt\n- Displacement s(t) = ∫v(t) dt\n\n**Example:** A particle moves with acceleration a(t) = 6t − 4 (m/s²). Given v(0) = 2 m/s and s(0) = 1 m, find s(t).\n\nv(t) = ∫(6t − 4) dt = 3t² − 4t + C₁\nv(0) = C₁ = 2 → v(t) = 3t² − 4t + 2\n\ns(t) = ∫(3t² − 4t + 2) dt = t³ − 2t² + 2t + C₂\ns(0) = C₂ = 1 → s(t) = t³ − 2t² + 2t + 1",
      },
      {
        id: "add-math-2-s11t1-practice",
        type: "question",
        content: "Test your understanding of integration.",
        exercise: {
          question: "What is ∫3x² dx?",
          options: [
            "6x + C",
            "x³ + C",
            "3x³/3 + C",
            "x³/3 + C"
          ],
          correctIndex: 1,
          explanation: "∫3x² dx = 3 × x³/3 + C = x³ + C. Using the power rule: ∫xⁿ dx = xⁿ⁺¹/(n + 1) + C."
        }
      },
    ],
  },
  {
    id: "add-math-2-s11t2",
    title: "Definite Integrals and Area Under a Curve",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 4,
    estimatedMinutes: 30,
    xpReward: 60,
    prerequisites: ["add-math-2-s11t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s11t2-intro",
        type: "info",
        content: "**Definite Integrals and Area Under a Curve**\n\nA definite integral evaluates the integral between two limits and gives a numerical value. Geometrically, it represents the signed area under a curve between the limits of integration.",
      },
      {
        id: "add-math-2-s11t2-content-1",
        type: "info",
        content: "**The Definite Integral**\n\nThe definite integral from a to b is written:\n∫ₐᵇ f(x) dx = F(b) − F(a)\n\nWhere F is an antiderivative of f.\n\n**The Fundamental Theorem of Calculus (Part 2):**\nIf f is continuous on [a, b] and F'(x) = f(x), then:\n∫ₐᵇ f(x) dx = F(b) − F(a)\n\n**Properties of Definite Integrals:**\n1. ∫ₐᵃ f(x) dx = 0\n2. ∫ₐᵇ f(x) dx = −∫_bᵃ f(x) dx\n3. ∫ₐᵇ c·f(x) dx = c·∫ₐᵇ f(x) dx\n4. ∫ₐᵇ [f(x) ± g(x)] dx = ∫ₐᵇ f(x) dx ± ∫ₐᵇ g(x) dx\n5. ∫ₐᵇ f(x) dx = ∫ₐᶜ f(x) dx + ∫_cᵇ f(x) dx\n\n**Worked Example:**\n∫₁³ (3x² − 2x) dx = [x³ − x²]₁³\n= (27 − 9) − (1 − 1)\n= 18 − 0 = 18",
      },
      {
        id: "add-math-2-s11t2-content-2",
        type: "info",
        content: "**Area Under a Curve**\n\nThe area bounded by the curve y = f(x), the x-axis, and the lines x = a and x = b is:\nArea = ∫ₐᵇ f(x) dx (if f(x) ≥ 0 on [a, b])\n\nIf f(x) is negative on part of the interval, the definite integral gives the signed (net) area. For total area, split into sections where f(x) ≥ 0 and f(x) < 0.\n\n**Example 1:** Find the area under y = x² from x = 1 to x = 3.\n\nArea = ∫₁³ x² dx = [x³/3]₁³ = (27/3) − (1/3) = 9 − ⅓ = 8⅔ square units\n\n**Example 2:** Find the total area bounded by y = x² − 4x + 3 and the x-axis.\n\nFirst, find x-intercepts: x² − 4x + 3 = 0 → (x − 1)(x − 3) = 0 → x = 1, 3\n\nThe curve is below the x-axis between x = 1 and x = 3.\n\nArea = |∫₁³ (x² − 4x + 3) dx|\n= |[x³/3 − 2x² + 3x]₁³|\n= |[(9 − 18 + 9) − (⅓ − 2 + 3)]|\n= |[0 − (4/3)]|\n= 4/3 square units",
      },
      {
        id: "add-math-2-s11t2-content-3",
        type: "info",
        content: "**Area Between Two Curves**\n\nThe area between two curves y = f(x) and y = g(x) from x = a to x = b is:\nArea = ∫ₐᵇ [f(x) − g(x)] dx (where f(x) ≥ g(x))\n\n**Worked Example:** Find the area between y = x² and y = 2x from x = 0 to x = 2.\n\nIntersection points:\nx² = 2x → x² − 2x = 0 → x(x − 2) = 0 → x = 0, 2\n\nThe line y = 2x is above y = x² on [0, 2].\n\nArea = ∫₀² (2x − x²) dx\n= [x² − x³/3]₀²\n= [(4 − 8/3) − (0 − 0)]\n= (12/3 − 8/3)\n= 4/3 square units\n\n**Applications of Definite Integrals:**\n- Distance travelled from velocity: s = ∫v dt\n- Work done by a force: W = ∫F dx\n- Volume of revolution\n- Average value of a function",
      },
      {
        id: "add-math-2-s11t2-practice",
        type: "question",
        content: "Test your understanding of definite integrals.",
        exercise: {
          question: "What does ∫₂⁵ f(x) dx represent geometrically?",
          options: [
            "The slope of f(x) at x = 2",
            "The area under f(x) from x = 2 to x = 5",
            "The value of f(5) − f(2)",
            "The average of f(2) and f(5)"
          ],
          correctIndex: 1,
          explanation: "A definite integral ∫ₐᵇ f(x) dx represents the signed (net) area bounded by the curve y = f(x), the x-axis, and the vertical lines x = a and x = b."
        }
      },
    ],
  },

  // ═══ MODULE 12: APPLICATIONS OF DIFFERENTIATION ═══
  {
    id: "add-math-2-s12t1",
    title: "Kinematics — Motion Along a Straight Line",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 4,
    estimatedMinutes: 30,
    xpReward: 60,
    prerequisites: ["add-math-2-s11t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s12t1-intro",
        type: "info",
        content: "**Kinematics — Motion Along a Straight Line**\n\nKinematics is the study of motion without considering its causes. Differentiation allows us to find velocity and acceleration from displacement, while integration does the reverse. These tools are essential in physics and engineering.",
      },
      {
        id: "add-math-2-s12t1-content-1",
        type: "info",
        content: "**The Relationship Between Displacement, Velocity and Acceleration**\n\nFor a particle moving along a straight line:\n\n**Displacement s(t):** position of the particle from a fixed origin.\n\n**Velocity v(t) = ds/dt:**\n- Rate of change of displacement.\n- Positive v: moving forward/increasing s.\n- Negative v: moving backward/decreasing s.\n- v = 0: particle is momentarily at rest.\n\n**Acceleration a(t) = dv/dt = d²s/dt²:**\n- Rate of change of velocity.\n- Positive a: velocity is increasing (or becoming less negative).\n- Negative a (deceleration): velocity is decreasing.\n\n**Summary of Relationships:**\n| Quantity | Differentiation | Integration |\n|----------|---------------|-------------|\n| s → v | v = ds/dt | s = ∫v dt |\n| v → a | a = dv/dt | v = ∫a dt |\n| s → a | a = d²s/dt² | — |",
      },
      {
        id: "add-math-2-s12t1-content-2",
        type: "info",
        content: "**Worked Example 1 — From Displacement**\n\nA particle moves such that s(t) = t³ − 6t² + 9t + 2 (s in metres, t in seconds, t ≥ 0).\n\n**a) Find velocity and acceleration.**\nv(t) = ds/dt = 3t² − 12t + 9\na(t) = dv/dt = 6t − 12\n\n**b) Find when the particle is at rest.**\nv(t) = 0 → 3t² − 12t + 9 = 0\n3(t² − 4t + 3) = 0\n3(t − 1)(t − 3) = 0\nt = 1 s or t = 3 s\n\n**c) Find the displacement at these times.**\ns(1) = 1 − 6 + 9 + 2 = 6 m\ns(3) = 27 − 54 + 27 + 2 = 2 m\n\n**d) Find the distance travelled in the first 4 seconds.**\nTotal distance = |s(1) − s(0)| + |s(3) − s(1)| + |s(4) − s(3)|\ns(0) = 2 m, s(1) = 6 m, s(3) = 2 m, s(4) = 64 − 96 + 36 + 2 = 6 m\nDistance = |6 − 2| + |2 − 6| + |6 − 2| = 4 + 4 + 4 = 12 m",
      },
      {
        id: "add-math-2-s12t1-content-3",
        type: "info",
        content: "**Worked Example 2 — From Acceleration**\n\nA particle moves with acceleration a(t) = 4t − 6 (m/s²). Given v(0) = 2 m/s and s(0) = 3 m, find:\n\n**a) Velocity at time t.**\nv(t) = ∫(4t − 6) dt = 2t² − 6t + C₁\nv(0) = C₁ = 2 → v(t) = 2t² − 6t + 2\n\n**b) Displacement at time t.**\ns(t) = ∫(2t² − 6t + 2) dt = 2t³/3 − 3t² + 2t + C₂\ns(0) = C₂ = 3 → s(t) = 2t³/3 − 3t² + 2t + 3\n\n**c) Find when velocity is zero.**\n2t² − 6t + 2 = 0 → t² − 3t + 1 = 0\nt = [3 ± √(9 − 4)]/2 = (3 ± √5)/2\nt ≈ 0.382 s or t ≈ 2.618 s\n\n**d) Maximum/minimum displacement (stationary points).**\nWhen v(t) = 0 → at t ≈ 0.382 and t ≈ 2.618\ns(0.382) ≈ 0.037 − 0.438 + 0.764 + 3 ≈ 3.36 m (local maximum)\ns(2.618) ≈ 11.96 − 20.57 + 5.24 + 3 ≈ −0.37 m (local minimum)",
      },
      {
        id: "add-math-2-s12t1-practice",
        type: "question",
        content: "Test your understanding of kinematics.",
        exercise: {
          question: "If displacement s(t) = t² − 4t + 3, what is the velocity at t = 3?",
          options: [
            "2 m/s",
            "6 m/s",
            "−1 m/s",
            "−4 m/s"
          ],
          correctIndex: 0,
          explanation: "v(t) = ds/dt = 2t − 4. At t = 3, v(3) = 2(3) − 4 = 6 − 4 = 2 m/s."
        }
      },
    ],
  },
  {
    id: "add-math-2-s12t2",
    title: "Rates of Change and Connected Rates",
    subject: "Additional Mathematics",
    subjectIcon: "🔢",
    programme: "Both",
    unitId: "additional-mathematics",
    difficulty: 4,
    estimatedMinutes: 30,
    xpReward: 60,
    prerequisites: ["add-math-2-s12t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "add-math-2-s12t2-intro",
        type: "info",
        content: "**Rates of Change and Connected Rates**\n\nDifferentiation allows us to calculate the rate at which one quantity changes with respect to another. The chain rule enables us to find connected (related) rates — how the rates of change of different but related quantities are linked.",
      },
      {
        id: "add-math-2-s12t2-content-1",
        type: "info",
        content: "**Rate of Change Using the Chain Rule**\n\nIf y depends on u, and u depends on x, then:\ndy/dx = dy/du × du/dx\n\n**Example 1:** If y = u² + 3u and u = x² − 1, find dy/dx.\n\ndy/du = 2u + 3\ndu/dx = 2x\n\ndy/dx = (2u + 3)(2x) = 2x(2(x² − 1) + 3) = 2x(2x² − 2 + 3) = 2x(2x² + 1) = 4x³ + 2x\n\n**Example 2 — Connected Rates (Geometric):**\nA spherical balloon is being inflated at a rate of 100 cm³/s. Find the rate of increase of the radius when the radius is 5 cm.\n\nV = 4/3 πr³\ndV/dt = 4πr² × dr/dt\n\nGiven dV/dt = 100, r = 5:\n100 = 4π(25) × dr/dt\n100 = 100π × dr/dt\ndr/dt = 1/π ≈ 0.318 cm/s",
      },
      {
        id: "add-math-2-s12t2-content-2",
        type: "info",
        content: "**Connected Rates — Ladder and Shadow Problems**\n\n**Example 3 — Ladder Problem:**\nA 10 m ladder slides down a wall. If the bottom slides away at 2 m/s, find the rate at which the top slides down when the bottom is 6 m from the wall.\n\nLet x = distance of bottom from wall, y = height of top on wall.\nBy Pythagoras: x² + y² = 100\n\nDifferentiate implicitly with respect to t:\n2x·dx/dt + 2y·dy/dt = 0\nx·dx/dt + y·dy/dt = 0\n\nWhen x = 6: y = √(100 − 36) = √64 = 8 m\ndx/dt = 2 m/s\n\n6(2) + 8(dy/dt) = 0\n12 + 8(dy/dt) = 0\ndy/dt = −12/8 = −1.5 m/s\n\nThe top slides down at 1.5 m/s (negative = decreasing height).\n\n**Example 4 — Shadow Problem:**\nA 1.8 m tall person walks away from a 6 m lamppost at 1.2 m/s. Find the rate at which the shadow lengthens.\n\nUsing similar triangles:\ns/1.8 = (s + x)/6 → 6s = 1.8(s + x) → 6s = 1.8s + 1.8x → 4.2s = 1.8x → s = (3/7)x\n\nds/dt = (3/7)dx/dt = (3/7)(1.2) ≈ 0.514 m/s",
      },
      {
        id: "add-math-2-s12t2-content-3",
        type: "info",
        content: "**Approximations and Small Changes**\n\nFor small changes in x, the change in y can be approximated:\nΔy ≈ dy/dx × Δx\n\nThis is useful for estimating errors or small adjustments without recalculating the entire function.\n\n**Example:** Use differentiation to approximate the change in the volume of a sphere when the radius increases from 10 cm to 10.1 cm.\n\nV = 4/3 πr³\ndV/dr = 4πr² = 4π(100) = 400π\nΔr = 0.1 cm\nΔV ≈ 400π × 0.1 = 40π ≈ 125.66 cm³\n\n**Exact change:**\nΔV = 4/3 π(10.1³ − 10³) = 4/3 π(1030.301 − 1000) = 4/3 π(30.301) ≈ 126.91 cm³\n\nThe approximation is close (125.66 vs 126.91), differing by about 1%.\n\n**Summary of Differentiation Applications:**\n1. Tangents and normals to curves\n2. Stationary points and optimisation\n3. Kinematics (s → v → a)\n4. Connected rates of change\n5. Small changes and approximations\n6. Marginal analysis in economics (marginal cost, marginal revenue)",
      },
      {
        id: "add-math-2-s12t2-practice",
        type: "question",
        content: "Test your understanding of rates of change.",
        exercise: {
          question: "A cube's side increases at 2 cm/s. How fast is its volume increasing when the side is 5 cm?",
          options: [
            "150 cm³/s",
            "30 cm³/s",
            "6 cm³/s",
            "300 cm³/s"
          ],
          correctIndex: 0,
          explanation: "V = s³, dV/ds = 3s². Using chain rule: dV/dt = dV/ds × ds/dt = 3s² × 2 = 3(25)(2) = 150 cm³/s."
        }
      },
    ],
  },
];

// ── Module count for reference ──────────────────────────────────────────────
export const ADD_MATHS_SHS2_COUNT = 12;
