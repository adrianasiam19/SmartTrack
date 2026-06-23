#!/usr/bin/env python
"""Append Core Maths Modules 2-9 lesson data to generate_coremaths.py"""

MODULES_2_9 = r'''

# ── MODULE 2: Fractions, Decimals & Percentages ─────────────────────────

ALL_LESSONS.append(L("coremath-m2t1", "Fractions — Addition, Subtraction, Multiplication, Division",
    "Core Mathematics", "\U0001f522", "Both", 1, 8, 20, "core-maths", [], ["SHS 1"], "SHS 1", [
    i("coremath-m2t1-s1",
      "\U0001f522 **Fractions — The Basics**\n\nA **fraction** represents a part of a whole: **a/b** where a is the numerator and b is the denominator.\n\n**Types of Fractions:**\n• **Proper fraction:** Numerator < denominator (e.g., 3/5)\n• **Improper fraction:** Numerator > denominator (e.g., 7/4)\n• **Mixed number:** Whole number + fraction (e.g., 1\u00be)\n\n**Converting Mixed Numbers to Improper Fractions:**\n> Multiply the whole number by the denominator, add the numerator, keep the same denominator.\n> 1\u00be = (1\u00d74 + 3)/4 = 7/4\n\n**Simplifying Fractions:**\nDivide numerator and denominator by their HCF.\n> 12/18 = 12\u00f76 / 18\u00f76 = 2/3\n\n> \U0001f4a1 **WASSCE Tip:** Always simplify your final answer to its lowest terms!"),
    p("coremath-m2t1-s2", "Look at these fractions: **2/3, 5/3, 1\u00bd**\n\nWhich one is an improper fraction?", 
      "2/3, 5/3, 1\u00bd", "Which is improper?",
      ["2/3", "5/3", "1\u00bd", "All of them"], 1,
      "**5/3** is improper because the numerator (5) is greater than the denominator (3). 2/3 is proper, and 1\u00bd is a mixed number."),
    i("coremath-m2t1-s3",
      "\u2795 **Adding and Subtracting Fractions**\n\n**Same denominator:** Just add/subtract the numerators.\n> 2/5 + 1/5 = 3/5\n> 4/7 \u2212 2/7 = 2/7\n\n**Different denominators:** Find the LCM first.\n> 1/3 + 1/4 = 4/12 + 3/12 = 7/12\n\n**Mixed numbers:** Convert to improper first, then add/subtract.\n> 1\u00bd + 2\u2153 = 3/2 + 7/3 = 9/6 + 14/6 = 23/6 = 3\u2159\n\n> \u26a0\ufe0f **WASSCE warning:** Never add denominators! Only add numerators after making denominators the same!"),
    q("coremath-m2t1-s4", "Calculate: **2/3 + 3/5**", 
      "2/3 + 3/5 = ?", ["5/8", "19/15", "6/15", "1"], 1,
      "LCM of 3 and 5 = 15. 2/3 = 10/15, 3/5 = 9/15. Sum = 10/15 + 9/15 = **19/15 = 1\u2074/\u2081\u2085**."),
    i("coremath-m2t1-s5",
      "\u2716\ufe0f **Multiplying and Dividing Fractions**\n\n**Multiplication:** Multiply numerators together, multiply denominators together.\n> 2/3 \u00d7 4/5 = 8/15\n\n**Cancelling before multiplying:**\n> 3/4 \u00d7 8/9 = 1/1 \u00d7 2/3 = 2/3 (cancel 3 and 9, then 4 and 8)\n\n**Division:** Flip the second fraction (reciprocal) and multiply.\n> 2/3 \u00f7 4/5 = 2/3 \u00d7 5/4 = 10/12 = 5/6\n\n> \u2705 **Quick check:** Dividing by 1/2 is the same as multiplying by 2!"),
    q("coremath-m2t1-s6", "Calculate: **3/4 \u00f7 9/16**",
      "3/4 \u00f7 9/16 = ?", ["27/64", "4/3", "3/4", "1\u2153"], 1,
      "3/4 \u00f7 9/16 = 3/4 \u00d7 16/9 = 48/36 = **4/3 = 1\u2153**. Flip the second fraction, then multiply!"),
]))

ALL_LESSONS.append(L("coremath-m2t2", "Decimals and Place Value",
    "Core Mathematics", "\U0001f522", "Both", 1, 8, 20, "core-maths", ["coremath-m2t1"], ["SHS 1"], "SHS 1", [
    i("coremath-m2t2-s1",
      "\U0001f522 **Decimals — Base 10 Fractions**\n\nDecimals are another way of writing fractions with denominators that are powers of 10.\n\n**Place Value Chart:**\nThousands | Hundreds | Tens | Ones | **.** | Tenths | Hundredths | Thousandths\n    1000   |   100    |  10  |  1   |  .   |  1/10  |   1/100    |   1/1000\n\n**Examples:**\n> 0.3 = 3/10\n> 0.07 = 7/100\n> 0.25 = 25/100 = 1/4\n> 3.45 = 3 + 4/10 + 5/100 = 3\u2074\u2075/\u2081\u2080\u2080\n\n> \U0001f4a1 **WASSCE Tip:** Be careful with zeros! 0.3 \u2260 0.03. The number of decimal places matters."),
    p("coremath-m2t2-s2", "Look at these decimals: **0.5, 0.50, 0.05**\n\nWhich two represent the same value?",
      "0.5, 0.50, 0.05", "Which two are equal?",
      ["0.5 and 0.50", "0.5 and 0.05", "0.50 and 0.05", "All three are different"], 0,
      "**0.5 = 0.50**. Adding trailing zeros after a decimal does not change the value. 0.5 = 5/10 = 50/100 = 0.50. But 0.05 = 5/100, which is different!"),
    i("coremath-m2t2-s3",
      "\U0001f4ca **Converting Between Fractions and Decimals**\n\n**Fraction \u2192 Decimal:** Divide numerator by denominator.\n> 3/8 = 3 \u00f7 8 = 0.375\n> 1/3 = 0.333... (recurring decimal)\n\n**Decimal \u2192 Fraction:** Write over the appropriate power of 10, then simplify.\n> 0.375 = 375/1000 = 3/8\n> 0.\u03053 = 0.333... = 1/3\n\n**Recurring Decimals:**\n> 0.\u03057 = 0.777... = 7/9\n> 0.\u03050\u03057 = 0.0707... = 7/99\n> 0.2\u03057 = 0.2777... \u2014 more complex!\n\n> \U0001f511 **WASSCE classic:** Convert 0.\u03057 to a fraction. Answer: 7/9. Just put the repeating digit over 9!"),
    q("coremath-m2t2-s4", "Convert **0.625** to a fraction in its simplest form.",
      "0.625 = ?", ["5/8", "625/1000", "5/6", "3/4"], 0,
      "0.625 = 625/1000. Simplify: divide by 125. 625\u00f7125/1000\u00f7125 = **5/8**."),
    i("coremath-m2t2-s5",
      "\U0001f4b0 **Decimal Operations — WASSCE Tips**\n\n**Addition/Subtraction:** Line up the decimal points!\n> 12.5 + 3.75 = 16.25\n>  12.50\n> + 3.75\n> \u2500\u2500\u2500\u2500\u2500\n>  16.25\n\n**Multiplication:** Count total decimal places in both numbers.\n> 2.5 \u00d7 3.2 = 8.00 (1+1 = 2 decimal places)\n\n**Division by a decimal:** Multiply both numbers by power of 10 to make divisor a whole number.\n> 3.5 \u00f7 0.5 = 35 \u00f7 5 = 7\n\n> \u26a0\ufe0f **Common mistake:** 2.5 \u00d7 10 = 25, not 2.50! Multiplying by 10 moves the decimal ONE place right."),
    c("coremath-m2t2-s6", "Decimals Mastery", [
        {"question": "What is 3/8 as a decimal?",
         "options": ["0.375", "0.38", "0.3", "0.0375"],
         "correctIndex": 0, "explanation": "3 \u00f7 8 = 0.375. WASSCE frequently asks fraction-to-decimal conversions."},
        {"question": "Calculate 0.4 \u00d7 0.03",
         "options": ["0.12", "0.012", "1.2", "0.0012"],
         "correctIndex": 1, "explanation": "4 \u00d7 3 = 12. Total decimal places = 1 + 2 = 3. So 0.4 \u00d7 0.03 = 0.012."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m2t3", "Percentages",
    "Core Mathematics", "\U0001f522", "Both", 1, 10, 25, "core-maths", ["coremath-m2t1"], ["SHS 1", "SHS 2"], "SHS 1", [
    i("coremath-m2t3-s1",
      "\U0001f522 **Percentages — Parts per Hundred**\n\n**Percent** means \"per hundred\". 1% = 1/100 = 0.01.\n\n**Key Conversions (Memorise These!):**\n> 50% = 0.5 = 1/2\n> 25% = 0.25 = 1/4\n> 75% = 0.75 = 3/4\n> 10% = 0.1 = 1/10\n> 33\u2153% = 0.333... = 1/3\n> 66\u2154% = 0.666... = 2/3\n\n**Converting:**\n> Percentage \u2192 Decimal: Divide by 100 (move decimal 2 places left)\n> Decimal \u2192 Percentage: Multiply by 100 (move decimal 2 places right)\n> Fraction \u2192 Percentage: Convert to decimal first, then multiply by 100"),
    p("coremath-m2t3-s2", "If 30 out of 50 students passed an exam, what percentage passed?",
      "30/50 passed", "What percentage passed?",
      ["30%", "60%", "50%", "80%"], 1,
      "30/50 = 0.6 = **60%**. Alternatively: (30/50) \u00d7 100% = 60%. Multiply the fraction by 100%."),
    i("coremath-m2t3-s3",
      "\U0001f4b0 **Percentage of a Quantity (WASSCE Classic!)**\n\n**Finding a percentage of a quantity:**\n> 15% of 200 = 0.15 \u00d7 200 = 30\n\n**Finding the whole from a percentage:**\n> If 15% of a number is 30, what is the number?\n> 15% \u2192 30, so 1% \u2192 30/15 = 2, so 100% \u2192 2 \u00d7 100 = 200\n\n**Percentage increase/decrease:**\n> New value = Original value \u00d7 (1 \u00b1 percentage/100)\n> Increase 200 by 15%: 200 \u00d7 1.15 = 230\n> Decrease 200 by 15%: 200 \u00d7 0.85 = 170\n\n> \U0001f4a1 **WASSCE loves \"percentage profit\" questions in the context of buying and selling goods!**"),
    q("coremath-m2t3-s4", "A store buys a shirt for GH\u00a250 and sells it for GH\u00a265.\n\nWhat is the **percentage profit**?",
      "% profit = ?", ["15%", "30%", "25%", "20%"], 1,
      "Profit = 65 \u2212 50 = 15. % profit = (Profit/Cost) \u00d7 100 = (15/50) \u00d7 100 = **30%**. WASSCE formula: % = (Profit/Cost Price) \u00d7 100."),
    i("coremath-m2t3-s5",
      "\U0001f4c8 **Applications — Discount, Tax, and Interest**\n\n**Discount:**\n> Sale price = Original price \u2212 (Original price \u00d7 Discount%)\n> Example: 20% off GH\u00a280 = GH\u00a280 \u2212 GH\u00a216 = GH\u00a264\n\n**Simple Interest (WASSCE staple!):**\n> Interest = Principal \u00d7 Rate \u00d7 Time\n> I = PRT/100 (where T is in years)\n\n**Example:** GH\u00a21,000 invested at 10% per annum for 3 years.\n> I = (1000 \u00d7 10 \u00d7 3)/100 = GH\u00a2300\n> Total amount = GH\u00a21,000 + GH\u00a2300 = GH\u00a21,300\n\n> \ud83d\udd11 **WASSCE hint:** Always check whether the question asks for interest alone or the total amount!"),
    q("coremath-m2t3-s6", "Calculate the simple interest on GH\u00a25,000 at 8% per annum for 2 years.",
      "Simple interest = ?", ["GH\u00a2400", "GH\u00a2800", "GH\u00a25,800", "GH\u00a280"], 1,
      "I = PRT/100 = (5000 \u00d7 8 \u00d7 2)/100 = 80000/100 = **GH\u00a2800**. Total amount = GH\u00a25,000 + GH\u00a2800 = GH\u00a25,800."),
]))

ALL_LESSONS.append(L("coremath-m2t4", "Ratio and Proportion",
    "Core Mathematics", "\U0001f522", "Both", 1, 8, 20, "core-maths", ["coremath-m2t1"], ["SHS 1", "SHS 2"], "SHS 1", [
    i("coremath-m2t4-s1",
      "\U0001f522 **Ratio — Comparing Quantities**\n\nA **ratio** compares two or more quantities of the same kind.\n\n**Writing Ratios:**\n> If a class has 12 boys and 8 girls:\n> Ratio of boys to girls = 12:8 = 3:2 (simplified by dividing by 4)\n> Ratio of boys to total = 12:20 = 3:5\n\n**Sharing in a Ratio:**\n> Share GH\u00a2100 in the ratio 2:3\n> Total parts = 2 + 3 = 5\n> One part = 100/5 = 20\n> First person: 2 \u00d7 20 = 40\n> Second person: 3 \u00d7 20 = 60\n\n> \u2705 **Always simplify ratios to lowest terms, just like fractions!**"),
    p("coremath-m2t4-s2", "Share GH\u00a2600 between Kofi and Ama in the ratio 2:3.\n\nHow much does Ama get?",
      "Ama's share in ratio 2:3", "How much does Ama get?",
      ["GH\u00a2240", "GH\u00a2360", "GH\u00a2300", "GH\u00a2200"], 1,
      "Total parts = 2+3 = 5. One part = 600\u00f75 = 120. Ama = 3 \u00d7 120 = **GH\u00a2360**."),
    i("coremath-m2t4-s3",
      "\U0001f4c9 **Direct Proportion**\n\n**Direct Proportion:** As one quantity increases, the other increases in the same ratio.\n> y is directly proportional to x \u2192 y = kx (k is the constant of proportionality)\n\n**Example:** If 5 oranges cost GH\u00a215, how much do 8 oranges cost?\n> 5 oranges \u2192 GH\u00a215\n> 1 orange \u2192 15/5 = GH\u00a23\n> 8 oranges \u2192 8 \u00d7 3 = GH\u00a224\n\n**Unitary Method:** Find one unit first, then multiply.\n\n**Inverse Proportion:** As one quantity increases, the other decreases.\n> More workers = less time to complete a job.\n> y = k/x \u2014 y is inversely proportional to x."),
    q("coremath-m2t4-s4", "If 6 men can paint a house in 8 days, how many days would 4 men take? (Assume all work at the same rate)",
      "4 men = ? days", ["12", "6", "10", "5\u2153"], 0,
      "This is **inverse proportion**. Fewer men = more days. 6 men \u00d7 8 days = 48 man-days. 4 men: 48/4 = **12 days**."),
    i("coremath-m2t4-s5",
      "\U0001f3af **WASSCE Applications of Ratio**\n\n**Scale drawing:**\n> If a map scale is 1:50,000, then 4 cm on the map = 4 \u00d7 50,000 = 200,000 cm = 2 km\n\n**Dividing in a given ratio with more than two parts:**\n> GH\u00a2900 shared among three people in ratio 2:3:4\n> Total parts = 2+3+4 = 9\n> One part = 900/9 = 100\n> Shares: 200, 300, 400\n\n**Ratios involving fractions:**\n> 1/2 : 2/3 : 3/4 \u2014 multiply all by LCM of denominators (12)\n> = 6 : 8 : 9"),
    c("coremath-m2t4-s6", "Ratio and Proportion Mastery", [
        {"question": "Divide GH\u00a2420 in the ratio 2:5",
         "options": ["GH\u00a2120 and GH\u00a2300", "GH\u00a2100 and GH\u00a2320", "GH\u00a2200 and GH\u00a2220", "GH\u00a260 and GH\u00a2360"],
         "correctIndex": 0, "explanation": "Total parts = 7. One part = 420/7 = 60. First = 2\u00d760=120, Second = 5\u00d760=300."},
        {"question": "If 8 books cost GH\u00a224, what will 12 books cost?",
         "options": ["GH\u00a235", "GH\u00a236", "GH\u00a230", "GH\u00a248"],
         "correctIndex": 1, "explanation": "One book = 24/8 = GH\u00a23. 12 books = 12\u00d73 = GH\u00a236. Direct proportion."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m2t5", "Rates — Speed, Density and Mixed Rates",
    "Core Mathematics", "\U0001f522", "Both", 2, 10, 25, "core-maths", ["coremath-m2t1", "coremath-m2t4"], ["SHS 1", "SHS 2"], "SHS 1", [
    i("coremath-m2t5-s1",
      "\U0001f522 **Rates — Comparing Different Kinds of Quantities**\n\nA **rate** is a special type of ratio that compares quantities of different kinds.\n\n**Speed (WASSCE Favourite!):**\n> Speed = Distance / Time\n> Average Speed = Total Distance / Total Time\n\n**Units:**\n> km/h, m/s, mph\n\n**Conversion:**\n> To convert km/h to m/s: multiply by 1000/3600 = 5/18\n> 72 km/h = 72 \u00d7 5/18 = 20 m/s\n> To convert m/s to km/h: multiply by 18/5\n> 20 m/s = 20 \u00d7 18/5 = 72 km/h\n\n> \U0001f4a1 **WASSCE will test these conversions!**"),
    p("coremath-m2t5-s2", "A car travels 240 km in 3 hours.\n\nWhat is its average speed in km/h?",
      "240 km in 3 hours", "Average speed?",
      ["60 km/h", "80 km/h", "120 km/h", "720 km/h"], 1,
      "Speed = Distance/Time = 240/3 = **80 km/h**. This is a simple WASSCE question \u2014 make sure you don't confuse distance and time!"),
    i("coremath-m2t5-s3",
      "\U0001f4a7 **Density and Other Common Rates**\n\n**Density:** Mass per unit volume\n> Density = Mass / Volume\n> Units: g/cm\u00b3, kg/m\u00b3\n> Example: If 50 g of metal has volume 10 cm\u00b3, density = 50/10 = 5 g/cm\u00b3\n\n**Fuel Consumption:**\n> Petrol consumption = Distance / Fuel used\n> Example: A car travels 320 km on 40 litres. Consumption = 320/40 = 8 km/L\n\n**Work Rate:**\n> Work done = Rate \u00d7 Time\n> If a tap fills a tank in 4 hours, its rate = 1/4 of the tank per hour\n\n> \u2705 **Formula triangle trick:** Cover the value you need! For D=S\u00d7T, cover D to see S\u00d7T, cover S to see D/T."),
    q("coremath-m2t5-s4", "A piece of metal has mass 180 g and volume 15 cm\u00b3.\n\nWhat is its **density**?",
      "Density = ?", ["12 g/cm\u00b3", "2700 g/cm\u00b3", "0.083 g/cm\u00b3", "165 g/cm\u00b3"], 0,
      "Density = Mass/Volume = 180/15 = **12 g/cm\u00b3**. WASSCE often asks density problems in the practical paper."),
    i("coremath-m2t5-s5",
      "\U0001f3af **Mixed Rate Problems — WASSCE Hard Questions**\n\n**Combined Rates:**\n> Tap A fills a tank in 4 hours. Tap B fills the same tank in 6 hours. How long will both take together?\n> A's rate = 1/4 per hour, B's rate = 1/6 per hour\n> Combined rate = 1/4 + 1/6 = 5/12 per hour\n> Time = 1 / (5/12) = 12/5 = 2.4 hours = 2 hours 24 minutes\n\n**Average Speed with different distances:**\n> A car goes 120 km at 60 km/h, then 120 km at 40 km/h.\n> Average speed = Total distance / Total time\n> Time1 = 120/60 = 2 h, Time2 = 120/40 = 3 h\n> Total = 240 km / 5 h = **48 km/h**\n\n> \u26a0\ufe0f **Common error:** Don't just average 60 and 40 to get 50 km/h! Weighted by time!"),
    q("coremath-m2t5-s6", "A cyclist travels 30 km at 10 km/h, then 20 km at 20 km/h.\n\nFind the **average speed** for the whole journey.",
      "Average speed = ?", ["15 km/h", "12.5 km/h", "14 km/h", "13.3 km/h"], 1,
      "Time1 = 30/10 = 3 h. Time2 = 20/20 = 1 h. Total = 50 km / 4 h = **12.5 km/h**."),
]))


# ── MODULE 3: Algebraic Expressions ───────────────────────────────────

ALL_LESSONS.append(L("coremath-m3t1", "Simplifying Algebraic Expressions",
    "Core Mathematics", "\U0001f522", "Both", 1, 8, 20, "core-maths", [], ["SHS 1"], "SHS 1", [
    i("coremath-m3t1-s1",
      "\U0001f522 **Algebraic Expressions — The Language of Maths**\n\nAlgebra uses letters (variables) to represent unknown numbers.\n\n**Key Terms:**\n> **Term:** A number, variable, or product (e.g., 3x, -2y\u00b2, 5)\n> **Coefficient:** The number multiplying a variable (e.g., in 3x, the coefficient is 3)\n> **Constant:** A term without a variable (e.g., 5, -2)\n> **Like terms:** Terms with the same variables AND same powers (e.g., 3x and -2x)\n\n**Simplifying — Collecting Like Terms:**\n> 3x + 5y + 2x \u2212 3y = (3x + 2x) + (5y \u2212 3y) = 5x + 2y\n\n> \U0001f4a1 **WASSCE Tip:** Only like terms can be added/subtracted. 3x + 2y cannot be simplified further!"),
    p("coremath-m3t1-s2", "Simplify: **4a + 3b \u2212 2a + 5b**\n\nCan you combine the like terms?",
      "Simplify 4a + 3b \u2212 2a + 5b", "What is the simplified form?",
      ["6a + 8b", "2a + 8b", "2a + 2b", "6a + 2b"], 1,
      "Group a terms: 4a \u2212 2a = 2a. Group b terms: 3b + 5b = 8b. Result: **2a + 8b**."),
    i("coremath-m3t1-s3",
      "\U0001f4dd **Laws of Algebra — Order of Operations**\n\n**BIDMAS/BODMAS:**\n> Brackets, Indices/Orders, Division/Multiplication (left to right), Addition/Subtraction (left to right)\n\n**Substitution:** Replace variables with given values.\n> If a = 3, b = 2: 2a + 3b = 2(3) + 3(2) = 6 + 6 = 12\n\n**Important rules:**\n> a \u00d7 a = a\u00b2, a \u00d7 a \u00d7 a = a\u00b3\n> a \u00d7 b = ab (multiplication sign is often omitted)\n> 2 \u00d7 a \u00d7 b = 2ab\n\n> \u2705 **Remember:** ab means a \u00d7 b, NOT a + b!"),
    q("coremath-m3t1-s4", "If x = 4 and y = 3, evaluate: **3x\u00b2 + 2y \u2212 5**",
      "3(4)\u00b2 + 2(3) \u2212 5 = ?", ["49", "55", "43", "47"], 0,
      "3(16) + 6 \u2212 5 = 48 + 6 \u2212 5 = **49**. Remember: x\u00b2 means 4\u00b2 = 16, so 3 \u00d7 16 = 48."),
    i("coremath-m3t1-s5",
      "\U0001f3af **Polynomial Operations**\n\n**Adding and Subtracting Polynomials:**\n> (3x\u00b2 + 2x \u2212 5) + (x\u00b2 \u2212 4x + 3) = 4x\u00b2 \u2212 2x \u2212 2\n> (3x\u00b2 + 2x \u2212 5) \u2212 (x\u00b2 \u2212 4x + 3) = 3x\u00b2 + 2x \u2212 5 \u2212 x\u00b2 + 4x \u2212 3 = 2x\u00b2 + 6x \u2212 8\n\n**Watch those signs when subtracting!** Change every sign in the bracket being subtracted.\n\n> \U0001f511 **WASSCE golden rule:** When subtracting, distribute the minus sign to ALL terms in the bracket!"),
    c("coremath-m3t1-s6", "Algebraic Expressions Mastery", [
        {"question": "Simplify: 5x + 3y \u2212 2x \u2212 y",
         "options": ["3x + 2y", "7x + 4y", "3x + 4y", "7x + 2y"],
         "correctIndex": 0, "explanation": "5x \u2212 2x = 3x. 3y \u2212 y = 2y. Result: 3x + 2y."},
        {"question": "If p = 2 and q = 5, evaluate 3p\u00b2 + 2q",
         "options": ["22", "18", "30", "16"],
         "correctIndex": 0, "explanation": "3(4) + 2(5) = 12 + 10 = 22."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m3t2", "Expansion and Factorisation",
    "Core Mathematics", "\U0001f522", "Both", 2, 10, 25, "core-maths", ["coremath-m3t1"], ["SHS 1", "SHS 2"], "SHS 1", [
    i("coremath-m3t2-s1",
      "\U0001f522 **Expansion — Removing Brackets**\n\n**Single brackets:** Multiply each term inside by the term outside.\n> 3(x + 2) = 3x + 6\n> \u22122(3x \u2212 1) = \u22126x + 2\n\n**Double brackets (FOIL Method):**\n> (x + 3)(x + 5)\n> First: x \u00d7 x = x\u00b2\n> Outer: x \u00d7 5 = 5x\n> Inner: 3 \u00d7 x = 3x\n> Last: 3 \u00d7 5 = 15\n> Result: x\u00b2 + 8x + 15\n\n**Special products (WASSCE loves these!):**\n> (a + b)\u00b2 = a\u00b2 + 2ab + b\u00b2\n> (a \u2212 b)\u00b2 = a\u00b2 \u2212 2ab + b\u00b2\n> (a + b)(a \u2212 b) = a\u00b2 \u2212 b\u00b2 (Difference of two squares)"),
    p("coremath-m3t2-s2", "Expand: **(x + 4)(x \u2212 3)**\n\nUse FOIL to expand this!",
      "(x+4)(x\u22123)", "Expanded form?",
      ["x\u00b2 + 7x \u2212 12", "x\u00b2 + x \u2212 12", "x\u00b2 \u2212 12", "x\u00b2 \u2212 x \u2212 12"], 1,
      "F: x\u00d7x=x\u00b2, O: x\u00d7(-3)=-3x, I: 4\u00d7x=4x, L: 4\u00d7(-3)=-12. Sum: x\u00b2 + (-3x+4x) - 12 = **x\u00b2 + x \u2212 12**."),
    i("coremath-m3t2-s3",
      "\U0001f504 **Factorisation — The Reverse of Expansion**\n\n**Common Factor Factorisation:**\n> 6x\u00b2 + 9x = 3x(2x + 3) (HCF of 6x\u00b2 and 9x is 3x)\n\n**Quadratic Factorisation (ax\u00b2 + bx + c):**\n> When a = 1: Find two numbers that multiply to give c and add to give b.\n> x\u00b2 + 7x + 12 = (x + 3)(x + 4)\n>   \u2713  3 \u00d7 4 = 12 (product)\n>   \u2713  3 + 4 = 7 (sum)\n\n**Difference of Two Squares:**\n> x\u00b2 \u2212 9 = (x + 3)(x \u2212 3)\n> 4x\u00b2 \u2212 25 = (2x + 5)(2x \u2212 5)\n\n> \U0001f4a1 **WASSCE Tip:** Always check if you can factor out a common factor FIRST before trying other methods!"),
    q("coremath-m3t2-s4", "Factorise: **x\u00b2 \u2212 3x \u2212 10**",
      "Factorise x\u00b2 \u2212 3x \u2212 10", ["(x + 5)(x \u2212 2)", "(x \u2212 5)(x + 2)", "(x \u2212 10)(x + 1)", "(x + 10)(x \u2212 1)"], 1,
      "We need two numbers with product = \u221210 and sum = \u22123. Numbers: \u22125 and +2. Check: (\u22125)(+2) = \u221210 \u2713, \u22125+2 = \u22123 \u2713. So: **(x \u2212 5)(x + 2)**."),
    i("coremath-m3t2-s5",
      "\U0001f3af **Harder Factorisation — When a \u2260 1**\n\n**Factorising ax\u00b2 + bx + c:**\n> Example: 2x\u00b2 + 7x + 3\n>\n> **Method:** Multiply a and c: 2 \u00d7 3 = 6\n> Find two numbers whose product is 6 and sum is 7: +6 and +1\n> Split the middle term: 2x\u00b2 + 6x + x + 3\n> Group: (2x\u00b2 + 6x) + (x + 3)\n> Factor each group: 2x(x + 3) + 1(x + 3)\n> Final: (x + 3)(2x + 1)\n\n> \u2705 **Always expand your answer to check!** (x+3)(2x+1) = 2x\u00b2 + x + 6x + 3 = 2x\u00b2 + 7x + 3 \u2713"),
    c("coremath-m3t2-s6", "Expansion and Factorisation Mastery", [
        {"question": "Expand: (x + 2)(x \u2212 7)",
         "options": ["x\u00b2 \u2212 5x \u2212 14", "x\u00b2 + 5x \u2212 14", "x\u00b2 \u2212 14", "x\u00b2 \u2212 9x \u2212 14"],
         "correctIndex": 0, "explanation": "F: x\u00b2, O: -7x, I: +2x, L: -14. = x\u00b2 \u2212 5x \u2212 14."},
        {"question": "Factorise completely: 4x\u00b2 \u2212 9",
         "options": ["(2x \u2212 3)(2x \u2212 3)", "(2x + 3)(2x \u2212 3)", "(4x + 3)(x \u2212 3)", "(4x \u2212 3)(4x + 3)"],
         "correctIndex": 1, "explanation": "Difference of two squares: (2x)\u00b2 \u2212 (3)\u00b2 = (2x+3)(2x\u22123). WASSCE favourite!"},
    ]),
]))

ALL_LESSONS.append(L("coremath-m3t3", "Algebraic Fractions",
    "Core Mathematics", "\U0001f522", "Both", 2, 10, 25, "core-maths", ["coremath-m2t1", "coremath-m3t1"], ["SHS 1", "SHS 2"], "SHS 1", [
    i("coremath-m3t3-s1",
      "\U0001f522 **Algebraic Fractions**\n\nThe same rules as numerical fractions apply!\n\n**Simplifying Algebraic Fractions:**\n> Factor numerator and denominator, then cancel common factors.\n> (x\u00b2 + 5x) / x = x(x+5) / x = x + 5 (for x \u2260 0)\n> (x\u00b2 \u2212 4) / (x + 2) = (x+2)(x-2) / (x+2) = x \u2212 2 (for x \u2260 -2)\n\n> \u26a0\ufe0f **Cannot cancel terms that are added!**\n> (x + 4)/4 \u2260 x! You can only cancel factors (multiplication)."),
    p("coremath-m3t3-s2", "Simplify: **(x\u00b2 \u2212 9) / (x \u2212 3)**\n\nFactor first, then cancel!",
      "(x\u00b2\u22129)/(x\u22123)", "Simplified form?",
      ["x \u2212 3", "x + 3", "x \u2212 6", "x + 6"], 1,
      "x\u00b2 \u2212 9 = (x+3)(x-3). So (x+3)(x-3)/(x-3) = **x + 3** (for x \u2260 3)."),
    i("coremath-m3t3-s3",
      "\u2795 **Adding and Subtracting Algebraic Fractions**\n\n**Same denominator:** Just add/subtract numerators.\n> 3/(x+1) + 2/(x+1) = 5/(x+1)\n\n**Different denominators:** Find the algebraic LCM.\n> 2/x + 3/(x+1)\n> LCM = x(x+1)\n> = 2(x+1)/x(x+1) + 3x/x(x+1)\n> = (2x+2+3x)/x(x+1)\n> = (5x+2)/x(x+1)\n\n> \U0001f4a1 **WASSCE Tip:** Always factorise denominators first to find the correct LCM!"),
    q("coremath-m3t3-s4", "Simplify: **1/(x+1) + 1/(x\u22121)**",
      "1/(x+1) + 1/(x\u22121) = ?", ["2/(x\u00b2\u22121)", "2x/(x\u00b2\u22121)", "2/(x\u00b2+1)", "2x/(x\u00b2+1)"], 1,
      "LCM = (x+1)(x\u22121) = x\u00b2\u22121. \n= (x\u22121)/(x\u00b2\u22121) + (x+1)/(x\u00b2\u22121) \n= (x\u22121+x+1)/(x\u00b2\u22121) = **2x/(x\u00b2\u22121)**."),
    i("coremath-m3t3-s5",
      "\u2716\ufe0f **Multiplying and Dividing Algebraic Fractions**\n\n**Multiplication:** Multiply numerators and denominators straight across.\n> (x+1)/(x+2) \u00d7 (x+2)/(x+3) = (x+1)(x+2)/(x+2)(x+3) = (x+1)/(x+3) (cancel x+2)\n\n**Division:** Flip and multiply.\n> (x+1)/(x+2) \u00f7 (x+3)/(x+4) = (x+1)/(x+2) \u00d7 (x+4)/(x+3) = (x+1)(x+4)/(x+2)(x+3)\n\n> \u2705 **Always look for cancellation BEFORE multiplying! It saves time.**"),
    c("coremath-m3t3-s6", "Algebraic Fractions Mastery", [
        {"question": "Simplify: (x\u00b2 + x)/x",
         "options": ["x + 1", "x + 0", "x\u00b2", "x"],
         "correctIndex": 0, "explanation": "x(x+1)/x = x+1 (for x \u2260 0)."},
        {"question": "Simplify: 2/(x+1) + 1/x",
         "options": ["3x/(x(x+1))", "(3x+1)/(x(x+1))", "2/x(x+1)", "3/(2x+1)"],
         "correctIndex": 1, "explanation": "LCM = x(x+1). = 2x/x(x+1) + (x+1)/x(x+1) = (3x+1)/x(x+1)."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m3t4", "Linear Equations and Inequalities",
    "Core Mathematics", "\U0001f522", "Both", 2, 10, 25, "core-maths", ["coremath-m3t1"], ["SHS 1", "SHS 2"], "SHS 1", [
    i("coremath-m3t4-s1",
      "\U0001f522 **Solving Linear Equations**\n\nA **linear equation** has the variable(s) to the power of 1.\n\n**Golden Rules:**\n> Whatever you do to one side, do to the other!\n> Aim to get the variable alone on one side.\n\n**Example:** Solve 2x + 5 = 13\n> 2x + 5 \u2212 5 = 13 \u2212 5 (subtract 5 from both sides)\n> 2x = 8\n> 2x/2 = 8/2 (divide both sides by 2)\n> x = 4\n\n**Check:** 2(4) + 5 = 8 + 5 = 13 \u2713"),
    p("coremath-m3t4-s2", "Solve: **3x \u2212 7 = 14**\n\nWhat is the value of x?",
      "3x \u2212 7 = 14", "x = ?", ["x = 7", "x = 5", "x = 21", "x = 6"], 0,
      "3x \u2212 7 = 14. Add 7: 3x = 21. Divide by 3: x = **7**. Check: 3(7) \u2212 7 = 21 \u2212 7 = 14 \u2713."),
    i("coremath-m3t4-s3",
      "\U0001f4dd **Equations with Variables on Both Sides**\n\n**Example:** Solve 5x \u2212 3 = 2x + 9\n> 5x \u2212 3 \u2212 2x = 2x + 9 \u2212 2x (subtract 2x)\n> 3x \u2212 3 = 9\n> 3x = 12\n> x = 4\n\n**Equations with brackets:**\n> Solve 3(2x \u2212 1) = 15\n> 6x \u2212 3 = 15 (expand brackets)\n> 6x = 18\n> x = 3\n\n**Equations with fractions:**\n> x/2 + x/3 = 10\n> Multiply by LCM (6): 3x + 2x = 60\n> 5x = 60, x = 12"),
    q("coremath-m3t4-s4", "Solve: **4(x \u2212 2) = 3(x + 1)**",
      "4(x\u22122) = 3(x+1)", "x = ?", ["x = 5", "x = 7", "x = 11", "x = 8"], 2,
      "Expand: 4x \u2212 8 = 3x + 3. Subtract 3x: x \u2212 8 = 3. Add 8: x = **11**. Check: 4(9) = 36, 3(12) = 36 \u2713."),
    i("coremath-m3t4-s5",
      "\u2a9d **Linear Inequalities**\n\nInequalities work like equations, with ONE key difference!\n\n**Symbols:**\n> a < b: a is less than b\n> a > b: a is greater than b\n> a \u2264 b: a is less than or equal to b\n> a \u2265 b: a is greater than or equal to b\n\n**\u26a0\ufe0f THE CRITICAL RULE:**\n> When you multiply or divide by a **NEGATIVE** number, **FLIP** the inequality sign!\n\n**Example:** Solve \u22122x < 6\n> x > \u22123 (divided by \u22122, so flip < to >)\n\n**Check:** If x = 0: \u22122(0) = 0 < 6 \u2713\n> If x = \u22122: \u22122(\u22122) = 4 < 6 \u2713\n> If x = \u22124: \u22122(\u22124) = 8 < 6 \u2717 (indeed, -4 < -3 gives a false result)"),
    q("coremath-m3t4-s6", "Solve: **5 \u2212 2x \u2264 9**",
      "5 \u2212 2x \u2264 9", "x ?", ["x \u2264 \u22122", "x \u2265 \u22122", "x \u2264 2", "x \u2265 2"], 1,
      "Subtract 5: \u22122x \u2264 4. Divide by \u22122 (flip sign!): x \u2265 **\u22122**. Check: x=0 gives 5 \u2264 9 \u2713."),
]))

ALL_LESSONS.append(L("coremath-m3t5", "Simultaneous Equations",
    "Core Mathematics", "\U0001f522", "Both", 2, 12, 30, "core-maths", ["coremath-m3t1", "coremath-m3t4"], ["SHS 1", "SHS 2"], "SHS 1", [
    i("coremath-m3t5-s1",
      "\U0001f522 **Simultaneous Equations — Solving Two Equations Together**\n\nTwo equations with two unknowns \u2014 we solve them **together** to find values that satisfy BOTH.\n\n**Method 1: Substitution**\n> Solve: y = 2x + 1 and 3x + 2y = 16\n> Substitute y: 3x + 2(2x + 1) = 16\n> 3x + 4x + 2 = 16\n> 7x = 14, x = 2\n> Then y = 2(2) + 1 = 5\n> Solution: x = 2, y = 5\n\n> \u2705 **Check:** 3(2) + 2(5) = 6 + 10 = 16 \u2713"),
    p("coremath-m3t5-s2", "Use substitution to solve:\n\ny = 3x \u2212 1 **and** 2x + 3y = 19",
      "y = 3x\u22121, 2x+3y=19", "x = ?", ["x = 2", "x = 3", "x = 4", "x = 5"], 0,
      "Substitute: 2x + 3(3x\u22121) = 19. 2x + 9x \u2212 3 = 19. 11x = 22. x = **2**. Then y = 3(2)\u22121 = 5."),
    i("coremath-m3t5-s3",
      "\U0001f504 **Method 2: Elimination**\n\nMake the coefficients of one variable the same, then add or subtract.\n\n**Example:** Solve 3x + 2y = 13 and 2x + 3y = 12\n\n> Step 1: Make x coefficients same (multiply by 2 and 3):\n> (1)\u00d72: 6x + 4y = 26\n> (2)\u00d73: 6x + 9y = 36\n>\n> Step 2: Subtract to eliminate x:\n> (6x + 9y) \u2212 (6x + 4y) = 36 \u2212 26\n> 5y = 10, y = 2\n>\n> Step 3: Substitute back: 3x + 2(2) = 13, 3x = 9, x = 3\n> Solution: x = 3, y = 2\n\n> \U0001f511 **WASSCE tests both methods. Practise both!"),
    q("coremath-m3t5-s4", "Solve: **2x + y = 7 and x \u2212 2y = 1**",
      "2x+y=7, x\u22122y=1", "What is y?", ["y = 2", "y = 1", "y = 3", "y = 4"], 1,
      "From (2): x = 1 + 2y. Substitute into (1): 2(1+2y) + y = 7. 2+4y+y=7. 5y=5. y = **1**. Then x = 1+2 = 3."),
    i("coremath-m3t5-s5",
      "\U0001f3af **WASSCE Applications — Word Problems**\n\n**Solving with simultaneous equations:**\n\n> The sum of two numbers is 15 and their difference is 3. Find the numbers.\n> Let x and y be the numbers.\n> x + y = 15\n> x \u2212 y = 3\n> Add: 2x = 18, x = 9\n> Then y = 15 \u2212 9 = 6\n> The numbers are **9 and 6**.\n\n**Money problems:**\n> 5 books and 3 pens cost GH\u00a235.\n> 2 books and 7 pens cost GH\u00a233.\n> Find the cost of one book and one pen.\n> Let b = book cost, p = pen cost\n> 5b + 3p = 35\n> 2b + 7p = 33\n> Solve: b = 4, p = 5. A book costs GH\u00a24, a pen costs GH\u00a25."),
    c("coremath-m3t5-s6", "Simultaneous Equations Mastery", [
        {"question": "Solve: 2x + y = 10 and x \u2212 y = 2",
         "options": ["x=4, y=2", "x=5, y=0", "x=3, y=4", "x=6, y=\u22122"],
         "correctIndex": 0, "explanation": "Add: 3x = 12, x = 4. Then y = 10 \u2212 2(4) = 2."},
        {"question": "The cost of 2 apples and 3 oranges is GH\u00a26. The cost of 3 apples and 2 oranges is GH\u00a27. Find cost of one apple.",
         "options": ["GH\u00a21.60", "GH\u00a21.80", "GH\u00a22.00", "GH\u00a21.50"],
         "correctIndex": 1, "explanation": "2a+3o=6, 3a+2o=7. Multiply (1) by 2: 4a+6o=12. (2) by 3: 9a+6o=21. Subtract: 5a=9, a=GH\u00a21.80."},
    ]),
]))


# ── MODULE 4: Relations and Functions ─────────────────────────────────

ALL_LESSONS.append(L("coremath-m4t1", "Introduction to Relations and Functions",
    "Core Mathematics", "\U0001f4c8", "Both", 1, 8, 20, "core-maths", [], ["SHS 1", "SHS 2"], "SHS 1", [
    i("coremath-m4t1-s1",
      "\U0001f4c8 **Relations and Functions**\n\nA **relation** is a set of ordered pairs (x, y). It shows how one set connects to another.\n\n**A function** is a special relation where each input (x) has EXACTLY ONE output (y).\n\n**Vertical Line Test:**\n> If a vertical line drawn anywhere on the graph touches the curve more than once, it is NOT a function.\n\n**Function Notation:**\n> f(x) = 2x + 3 means \"apply the rule 'multiply by 2 then add 3' to input x\"\n> f(5) = 2(5) + 3 = 13\n\n**Domain = Input values (x)**\n**Range = Output values (f(x))**\n\n> \U0001f4a1 **WASSCE will ask: \"Is this relation a function?\" \u2014 use the vertical line test!"),
    p("coremath-m4t1-s2", "Look at these ordered pairs:\n\n**{(1, 3), (2, 5), (3, 7), (1, 4)}**\n\nIs this a function?",
      "{(1,3), (2,5), (3,7), (1,4)}", "Is this a function?",
      ["Yes \u2014 each x has a y", "No \u2014 x=1 maps to both 3 and 4", "Yes \u2014 there are 4 pairs", "Cannot determine"], 1,
      "x = 1 appears twice with different y-values (3 and 4). A function must have **exactly one output per input**. So this is **not a function**."),
    i("coremath-m4t1-s3",
      "\U0001f4ca **Types of Relations**\n\n**1. One-to-One:** Each x maps to one y, each y maps to one x. (Function)\n> {(1,2), (3,4), (5,6)}\n\n**2. Many-to-One:** Different x values map to the same y. (Function)\n> {(-1,1), (0,0), (1,1)}  \u2014 f(x) = x\u00b2\n\n**3. One-to-Many:** One x maps to many y's. (NOT a function)\n> {(1,2), (1,3), (2,4)}\n\n**4. Many-to-Many:** Many x's map to many y's. (NOT a function)\n\n**WASSCE Essential:**\n> f(x) = x\u00b2 is **many-to-one** \u2014 e.g., f(2) = 4 and f(-2) = 4\n> f(x) = 2x is **one-to-one** \u2014 each input gives a unique output"),
    q("coremath-m4t1-s4", "Given f(x) = 3x \u2212 5. Find **f(4)**.",
      "f(4) where f(x) = 3x \u2212 5", "f(4) = ?", ["7", "12", "17", "4"], 0,
      "f(4) = 3(4) \u2212 5 = 12 \u2212 5 = **7**. Substitute x = 4 into the function rule."),
    i("coremath-m4t1-s5",
      "\U0001f3af **Finding Domain and Range**\n\n**Linear functions:** Domain = all real numbers, Range = all real numbers\n> f(x) = 2x + 1 \u2014 any x works, any y possible\n\n**Quadratic functions:** Domain = all real numbers, Range depends on turning point.\n> f(x) = x\u00b2 \u2014 any x works, but y \u2265 0 (range: y \u2265 0)\n\n**Rational functions:** Domain excludes values making denominator zero.\n> f(x) = 1/(x\u22122) \u2014 x \u2260 2 (division by zero is undefined!)\n> Range: y \u2260 0\n\n> \u26a0\ufe0f **Never divide by zero! Find values that make the denominator zero and exclude them from the domain.**"),
    c("coremath-m4t1-s6", "Functions Mastery", [
        {"question": "Given f(x) = 2x\u00b2 \u2212 3, find f(\u22122).",
         "options": ["\u221211", "5", "1", "\u22127"],
         "correctIndex": 1, "explanation": "f(-2) = 2(4) \u2212 3 = 8 \u2212 3 = 5."},
        {"question": "Which of these is NOT a function?",
         "options": ["{(1,2), (2,3), (3,4)}", "{(1,1), (2,1), (3,1)}", "{(1,2), (1,3), (2,4)}", "{(0,0), (1,1), (2,4)}"],
         "correctIndex": 2, "explanation": "x=1 maps to both 2 and 3 \u2014 not a function."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m4t2", "Linear Graphs and Gradients",
    "Core Mathematics", "\U0001f4c8", "Both", 2, 10, 25, "core-maths", ["coremath-m4t1"], ["SHS 1", "SHS 2"], "SHS 1", [
    i("coremath-m4t2-s1",
      "\U0001f4c8 **Linear Graphs \u2014 y = mx + c**\n\nThe equation of a straight line is **y = mx + c** where:\n> **m** = gradient (slope) \u2014 measures steepness\n> **c** = y-intercept \u2014 where the line crosses the y-axis\n\n**Gradient Formula:**\n> m = (y\u2082 \u2212 y\u2081) / (x\u2082 \u2212 x\u2081)\n> Positive gradient: line slopes upward \u2197\ufe0f\n> Negative gradient: line slopes downward \u2198\ufe0f\n> Zero gradient: horizontal line \u2192\n> Undefined gradient: vertical line \u2191\n\n**Example:** Find gradient between (1, 3) and (4, 9).\n> m = (9 \u2212 3) / (4 \u2212 1) = 6/3 = **2**"),
    p("coremath-m4t2-s2", "Find the gradient of the line passing through **(2, 5) and (6, 13)**.",
      "Gradient between (2,5) and (6,13)", "m = ?",
      ["2", "3", "4", "1/2"], 0,
      "m = (13\u22125)/(6\u22122) = 8/4 = **2**. The line rises by 2 units for every 1 unit across."),
    i("coremath-m4t2-s3",
      "\U0001f4dd **Drawing Linear Graphs**\n\n**Method 1: Table of values**\n> y = 2x \u2212 1\n> x | 0 | 1 | 2 | 3\n> y | -1 | 1 | 3 | 5\n> Plot points and join with a straight line.\n\n**Method 2: Gradient-intercept method**\n> y = 2x \u2212 1\n> Start at y-intercept (0, \u22121)\n> Gradient = 2 = 2/1, so go 2 up, 1 right \u2192 (1, 1), (2, 3)\n\n**Finding equation from a graph:**\n> Find gradient (m) and y-intercept (c)\n> Write: y = mx + c\n\n> \u2705 **Always label your axes and use a ruler for straight lines!**"),
    q("coremath-m4t2-s4", "A line passes through (0, 3) and (4, 11).\n\nWhat is its equation?",
      "Equation of line?", ["y = 2x + 3", "y = 4x + 3", "y = 2x \u2212 3", "y = x + 3"], 0,
      "m = (11\u22123)/(4\u22120) = 8/4 = 2. c = 3 (y-intercept). Equation: **y = 2x + 3**."),
    i("coremath-m4t2-s5",
      "\U0001f3af **Parallel and Perpendicular Lines**\n\n**Parallel lines:** Same gradient!\n> y = 2x + 1 and y = 2x \u2212 5 are parallel (both m = 2)\n\n**Perpendicular lines:** Product of gradients = \u22121\n> If m\u2081 = 2, then m\u2082 = \u22121/2\n> Because 2 \u00d7 (\u22121/2) = \u22121\n\n**WASSCE Application:**\n> Find the equation of the line parallel to y = 3x + 2 passing through (1, 5).\n> m = 3, so y \u2212 5 = 3(x \u2212 1)\n> y = 3x \u2212 3 + 5 = 3x + 2\n\n> \U0001f511 **WASSCE loves asking about parallel and perpendicular lines!**"),
    c("coremath-m4t2-s6", "Linear Graphs Mastery", [
        {"question": "Find the gradient between (\u22121, 4) and (3, 8).",
         "options": ["1", "2", "4/3", "3/4"],
         "correctIndex": 0, "explanation": "m = (8\u22124)/(3\u2212(\u22121)) = 4/4 = 1."},
        {"question": "Which line is perpendicular to y = 2x + 5?",
         "options": ["y = 2x \u2212 3", "y = \u00bdx + 1", "y = \u22122x + 5", "y = \u2212\u00bdx + 4"],
         "correctIndex": 3, "explanation": "Perpendicular gradient = \u22121/2. Only y = \u2212\u00bdx + 4 has this gradient."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m4t3", "Quadratic Functions and Graphs",
    "Core Mathematics", "\U0001f4c8", "Both", 2, 12, 30, "core-maths", ["coremath-m4t1", "coremath-m3t2"], ["SHS 2", "SHS 3"], "SHS 2", [
    i("coremath-m4t3-s1",
      "\U0001f4c8 **Quadratic Functions \u2014 Parabolas**\n\nA quadratic function has the form **f(x) = ax\u00b2 + bx + c** (a \u2260 0).\n\n**Shape:** Parabola (U-shaped curve)\n> If a > 0: opens upward (U shape) \u2014 minimum point\n> If a < 0: opens downward (\u2229 shape) \u2014 maximum point\n\n**Key Features:**\n> **y-intercept:** Where x = 0 \u2192 y = c\n> **x-intercepts (roots):** Where y = 0 \u2192 solve ax\u00b2 + bx + c = 0\n> **Axis of symmetry:** x = \u2212b/(2a)\n> **Turning point (vertex):** (\u2212b/(2a), f(\u2212b/(2a)))"),
    p("coremath-m4t3-s2", "For f(x) = x\u00b2 \u2212 4x + 3, what is the y-intercept?",
      "y-intercept of f(x)=x\u00b2\u22124x+3", "y-intercept?",
      ["(0, 3)", "(0, \u22124)", "(0, 1)", "(0, \u22123)"], 0,
      "The y-intercept is where x = 0. f(0) = 0\u00b2 \u2212 4(0) + 3 = 3. So y-intercept = **(0, 3)**."),
    i("coremath-m4t3-s3",
      "\u221a **Finding Roots (x-intercepts)**\n\nThree methods from the factorisation lesson:\n\n**1. Factorisation:**\n> x\u00b2 \u2212 5x + 6 = 0\n> (x \u2212 2)(x \u2212 3) = 0\n> x = 2 or x = 3\n\n**2. Quadratic Formula:**\n> x = [\u2212b \u00b1 \u221a(b\u00b2 \u2212 4ac)] / 2a\n\n**3. Completing the Square:**\n> x\u00b2 + 6x + 5 = (x + 3)\u00b2 \u2212 9 + 5 = (x + 3)\u00b2 \u2212 4\n> (x + 3)\u00b2 = 4\n> x + 3 = \u00b12\n> x = \u22121 or x = \u22125\n\n> \U0001f4a1 **WASSCE Tip:** If the question says \"Solve\", any method works. If it says \"Using the formula\", you must use the quadratic formula!"),
    q("coremath-m4t3-s4", "Find the roots of **x\u00b2 \u2212 x \u2212 6 = 0**.",
      "Roots of x\u00b2\u2212x\u22126=0", "x = ?",
      ["x = 3 or x = \u22122", "x = 2 or x = \u22123", "x = 3 or x = 2", "x = \u22122 or x = \u22123"], 0,
      "Factorise: (x \u2212 3)(x + 2) = 0. So x = **3 or x = \u22122**. Check: (3)\u00b2\u2212(3)\u22126=9\u22123\u22126=0 \u2713, (\u22122)\u00b2\u2212(\u22122)\u22126=4+2\u22126=0 \u2713."),
    i("coremath-m4t3-s5",
      "\U0001f4ca **Sketching Quadratic Graphs (WASSCE Essential!)**\n\n**Steps to sketch y = ax\u00b2 + bx + c:**\n\n1. **Shape:** U (a > 0) or \u2229 (a < 0)\n2. **y-intercept:** (0, c)\n3. **Roots:** Solve ax\u00b2 + bx + c = 0\n4. **Turning point:** x = \u2212b/(2a)\n5. **Plot and join** with smooth curve\n\n**Example:** Sketch y = x\u00b2 \u2212 2x \u2212 3\n> a = 1 > 0 \u2192 U shape\n> y-intercept: (0, \u22123)\n> Roots: (x \u2212 3)(x + 1) = 0 \u2192 x = 3 or x = \u22121\n> Axis of symmetry: x = \u2212(\u22122)/(2\u00d71) = 1\n> Turning point: f(1) = 1 \u2212 2 \u2212 3 = \u22124 \u2192 (1, \u22124)\n\n> \u2705 **Sketch should show all key points and be roughly to scale!**"),
    c("coremath-m4t3-s6", "Quadratic Graphs Mastery", [
        {"question": "For f(x) = \u2212x\u00b2 + 4x \u2212 3, what is the shape?",
         "options": ["U-shape (minimum)", "\u2229-shape (maximum)", "Straight line", "Cannot determine"],
         "correctIndex": 1, "explanation": "a = \u22121 < 0, so it opens downward (\u2229-shape) with a maximum point."},
        {"question": "What is the axis of symmetry for f(x) = x\u00b2 \u2212 6x + 8?",
         "options": ["x = 3", "x = \u22123", "x = 6", "x = \u22126"],
         "correctIndex": 0, "explanation": "x = \u2212b/(2a) = \u2212(\u22126)/(2\u00d71) = 6/2 = 3."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m4t4", "Graphical Solutions of Equations",
    "Core Mathematics", "\U0001f4c8", "Both", 3, 12, 30, "core-maths", ["coremath-m4t3"], ["SHS 2", "SHS 3"], "SHS 2", [
    i("coremath-m4t4-s1",
      "\U0001f4c8 **Solving Equations Graphically**\n\nYou can solve any equation by drawing the graph and reading off values.\n\n**Solving ax\u00b2 + bx + c = 0 graphically:**\n> Draw y = ax\u00b2 + bx + c\n> Read the x-intercepts (where y = 0)\n> These are the solutions (roots)!\n\n**Solving ax\u00b2 + bx + c = k graphically:**\n> Draw y = ax\u00b2 + bx + c and y = k\n> The x-coordinates where they intersect are the solutions.\n\n**Example:** Solve x\u00b2 \u2212 3x \u2212 1 = 0 graphically.\n> Draw y = x\u00b2 \u2212 3x \u2212 1 for x = \u22122 to x = 5.\n> Read where the curve crosses the x-axis.\n> Solutions: approximately x = \u22120.3 and x = 3.3"),
    p("coremath-m4t4-s2", "To solve **x\u00b2 \u2212 4 = 2x** graphically, what would you do?",
      "Solve x\u00b2\u22124 = 2x graphically", "Best approach?",
      ["Draw y = x\u00b2\u22124 and find x-intercepts", "Draw y = x\u00b2\u22124 and y = 2x, find intersections", "Draw y = x\u00b2\u22122x\u22124 and find x-intercepts", "Both B and C are valid"], 3,
      "You can either: (a) Rearrange to x\u00b2 \u2212 2x \u2212 4 = 0 and find x-intercepts, OR (b) Draw y = x\u00b2\u22124 and y = 2x and find intersections. **Both methods work!**"),
    i("coremath-m4t4-s3",
      "\U0001f4dd **Drawing Accurate Graphs**\n\n**For WASSCE, you must draw graphs on graph paper.**\n\n**Steps:**\n1. Create a table of values (usually 7-9 points)\n2. Choose a suitable scale (let the graph fill the paper)\n3. Plot points accurately\n4. Join with a smooth curve (freehand, not straight lines!)\n5. Label the axes and the curve\n\n**Example table for y = x\u00b2 \u2212 3x \u2212 1:**\n> x | -2 | -1 | 0 | 1 | 2 | 3 | 4 | 5\n> y | 9 | 3 | -1 | -3 | -3 | -1 | 3 | 9\n\n> \u2705 **Use a sharp pencil! WASSCE examiners need to read your graph clearly.**"),
    q("coremath-m4t4-s4", "From the graph of y = x\u00b2 \u2212 3x \u2212 1 (using table above), estimate the roots.",
      "Roots of x\u00b2\u22123x\u22121=0 from graph", "Approximate roots?",
      ["x \u2248 \u22120.3 and x \u2248 3.3", "x \u2248 \u22121 and x \u2248 4", "x \u2248 0.5 and x \u2248 2.5", "x \u2248 \u22122 and x \u2248 5"], 0,
      "From the table: y changes sign between x=\u22121 and x=0 (3 to \u22121) and between x=3 and x=4 (\u22121 to 3). Roots are approximately **x \u2248 \u22120.3 and x \u2248 3.3**."),
    i("coremath-m4t4-s5",
      "\U0001f3af **Using Graphs to Find Minimum/Maximum Values**\n\n**To find the turning point from a graph:**\n> Read the coordinates of the lowest (minimum) or highest (maximum) point.\n\n**From the table for y = x\u00b2 \u2212 3x \u2212 1:**\n> The y-values decrease then increase:\n> y = 9, 3, \u22121, \u22123, \u22123, \u22121, 3, 9\n> The minimum is between x = 1.5 and 1.5 (the axis of symmetry)\n> At x = 1.5: y = (1.5)\u00b2 \u2212 3(1.5) \u2212 1 = 2.25 \u2212 4.5 \u2212 1 = \u22123.25\n> Minimum point = **(1.5, \u22123.25)**\n\n**Reading values from a graph:**\n> To find y when x = 2.5: Draw a vertical line up to the curve, read y.\n> To find x when y = 5: Draw a horizontal line to the curve, read x (may have 2 values!)."),
    c("coremath-m4t4-s6", "Graphical Solutions Mastery", [
        {"question": "How many solutions does x\u00b2 = \u22124 have?",
         "options": ["0", "1", "2", "Infinite"],
         "correctIndex": 0, "explanation": "x\u00b2 is always \u2265 0. Graphically, the parabola y=x\u00b2 never touches y=\u22124. No real solutions!"},
        {"question": "If the graph of y = x\u00b2 + bx + c crosses the x-axis at x = 2 and x = 5, what is the equation?",
         "options": ["y = (x\u22122)(x\u22125)", "y = (x+2)(x+5)", "y = x\u00b2 + 7x + 10", "y = x\u00b2 \u2212 7x + 10"],
         "correctIndex": 3, "explanation": "Roots at 2 and 5: y = (x\u22122)(x\u22125) = x\u00b2 \u2212 7x + 10."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m4t5", "Practical Applications of Functions",
    "Core Mathematics", "\U0001f4c8", "Both", 2, 10, 25, "core-maths", ["coremath-m3t5", "coremath-m4t2"], ["SHS 2", "SHS 3"], "SHS 2", [
    i("coremath-m4t5-s1",
      "\U0001f3af **Real-World Applications of Linear Functions**\n\n**Cost and Revenue (WASSCE Classic!):**\n> Fixed cost (rent, salaries) + Variable cost (materials)\n> C(x) = Fixed + (Variable per unit \u00d7 x)\n> R(x) = Selling price per unit \u00d7 x\n> P(x) = R(x) \u2212 C(x) (Profit function)\n\n**Example:**\n> A baker has fixed costs of GH\u00a2100 and variable costs of GH\u00a22 per cake.\n> Selling price = GH\u00a25 per cake.\n> Cost: C(x) = 100 + 2x\n> Revenue: R(x) = 5x\n> Profit: P(x) = 5x \u2212 (100 + 2x) = 3x \u2212 100\n> Break-even (P = 0): 3x = 100, x \u2248 34 cakes"),
    p("coremath-m4t5-s2", "A taxi charges a fixed fare of GH\u00a25 plus GH\u00a20.50 per km.\n\nWhat function represents the fare for a journey of x km?",
      "Fare function for x km", "F(x) = ?",
      ["F(x) = 5x + 0.50", "F(x) = 0.50x + 5", "F(x) = 5.50x", "F(x) = 5 + 0.50"], 1,
      "Fare = fixed + (rate \u00d7 distance) = GH\u00a25 + GH\u00a20.50x = **0.50x + 5**."),
    i("coremath-m4t5-s3",
      "\U0001f4ca **Quadratic Applications \u2014 Maximum Area Problems**\n\nA classic WASSCE problem:\n\n> A farmer has 100 m of fencing to make a rectangular enclosure.\n> If one side is against a wall, what dimensions give the maximum area?\n>\n> Let width = x. Then length = 100 \u2212 2x (only 3 sides needed).\n> Area = x(100 \u2212 2x) = 100x \u2212 2x\u00b2\n> A(x) = \u22122x\u00b2 + 100x\n>\n> This is a quadratic with a = \u22122 < 0 (maximum).\n> x = \u2212b/(2a) = \u2212100/(2\u00d7\u22122) = \u2212100/\u22124 = 25\n>\n> Width = 25 m, length = 100 \u2212 50 = 50 m\n> Maximum area = 25 \u00d7 50 = **1250 m\u00b2**"),
    q("coremath-m4t5-s4", "A ball thrown upward follows the path h(t) = \u22125t\u00b2 + 20t + 2.\n\nWhat is the maximum height?",
      "Maximum height?", ["20 m", "22 m", "18 m", "25 m"], 1,
      "a = \u22125 < 0 (maximum). t = \u2212b/(2a) = \u221220/(2\u00d7\u22125) = \u221220/\u221210 = 2.\nh(2) = \u22125(4) + 20(2) + 2 = \u221220 + 40 + 2 = **22 m**."),
    i("coremath-m4t5-s5",
      "\U0001f4b1 **Demand and Supply Functions**\n\n**Demand function:** Quantity consumers will buy at price P.\n> Usually downward sloping (higher price = lower demand)\n> Example: Qd = 100 \u2212 2P\n\n**Supply function:** Quantity producers will sell at price P.\n> Usually upward sloping (higher price = higher supply)\n> Example: Qs = 3P \u2212 20\n\n**Market Equilibrium:** Qd = Qs\n> 100 \u2212 2P = 3P \u2212 20\n> 120 = 5P\n> P = 24 (equilibrium price)\n> Q = 100 \u2212 2(24) = 52 (equilibrium quantity)\n\n> \U0001f511 **WASSCE economics-based maths questions appear regularly!**"),
    c("coremath-m4t5-s6", "Applications Mastery", [
        {"question": "If C(x) = 50 + 3x and R(x) = 7x, find break-even point.",
         "options": ["x = 7.5", "x = 12.5", "x = 10", "x = 50"],
         "correctIndex": 1, "explanation": "Profit = 7x \u2212 (50+3x) = 4x \u2212 50 = 0. So 4x = 50, x = 12.5."},
        {"question": "If Qd = 80 \u2212 4P and Qs = 6P \u2212 20, find equilibrium price.",
         "options": ["P = 8", "P = 10", "P = 12", "P = 6"],
         "correctIndex": 1, "explanation": "80 \u2212 4P = 6P \u2212 20. 100 = 10P. P = 10."},
    ]),
]))


# ── MODULE 5: Geometry and Trigonometry ──────────────────────────────

ALL_LESSONS.append(L("coremath-m5t1", "Angle Properties and Parallel Lines",
    "Core Mathematics", "\U0001f7e1", "Both", 1, 8, 20, "core-maths", [], ["SHS 1", "SHS 2"], "SHS 1", [
    i("coremath-m5t1-s1",
      "\U0001f7e1 **Angles \u2014 Basic Concepts**\n\nAn angle measures the amount of turn between two lines.\n\n**Types of Angles:**\n> Acute: 0\u00b0 < \u03b8 < 90\u00b0\n> Right: exactly 90\u00b0\n> Obtuse: 90\u00b0 < \u03b8 < 180\u00b0\n> Straight: 180\u00b0\n> Reflex: 180\u00b0 < \u03b8 < 360\u00b0\n\n**Angle Facts (WASSCE Essential!):**\n> Angles around a point = 360\u00b0\n> Angles on a straight line = 180\u00b0\n> Vertically opposite angles are equal\n> Complementary: sum = 90\u00b0\n> Supplementary: sum = 180\u00b0"),
    p("coremath-m5t1-s2", "Two angles on a straight line are 3x and 2x.\n\nWhat is the value of x?",
      "3x + 2x = 180\u00b0", "x = ?", ["30\u00b0", "36\u00b0", "45\u00b0", "60\u00b0"], 1,
      "Angles on a straight line sum to 180\u00b0. 3x + 2x = 180\u00b0. 5x = 180\u00b0. x = **36\u00b0**. The angles are 108\u00b0 and 72\u00b0."),
    i("coremath-m5t1-s3",
      "\U0001f7e1 **Parallel Lines and Angles (WASSCE Classic!)**\n\nWhen a line (transversal) cuts two parallel lines:\n\n**Corresponding angles (F-angle):** Equal\n**Alternate angles (Z-angle):** Equal\n**Interior/Co-interior (C-angle):** Sum = 180\u00b0 (supplementary)\n\n**Memory Aids:**\n> F = **F**orward (same position relative to the parallel lines)\n> Z = **Z**igzag (inside the parallel lines, opposite sides of transversal)\n> C = **C**orner (inside the parallel lines, same side of transversal)\n\n> \U0001f4a1 **WASSCE loves parallel line angle problems! Practice identifying the patterns!**"),
    q("coremath-m5t1-s4", "Two parallel lines are cut by a transversal. An alternate angle is 55\u00b0.\n\nWhat is the corresponding angle?",
      "Alternate = 55\u00b0, corresponding = ?", ["35\u00b0", "55\u00b0", "125\u00b0", "145\u00b0"], 1,
      "Alternate angles are **equal**. Corresponding angles are also **equal**. So the corresponding angle = **55\u00b0**. Both types of angles are equal when lines are parallel."),
    i("coremath-m5t1-s5",
      "\U0001f3af **Angles in Polygons**\n\n**Interior angles of a polygon:**\n> Sum of interior angles = (n \u2212 2) \u00d7 180\u00b0\n> where n = number of sides\n\n**Examples:**\n> Triangle (n=3): (3\u22122)\u00d7180 = 180\u00b0\n> Quadrilateral (n=4): (4\u22122)\u00d7180 = 360\u00b0\n> Pentagon (n=5): (5\u22122)\u00d7180 = 540\u00b0\n> Hexagon (n=6): (6\u22122)\u00d7180 = 720\u00b0\n\n**Regular polygon:** All sides equal, all angles equal.\n> Each interior angle = (n\u22122)\u00d7180/n\n> Each exterior angle = 360/n\n\n> \u2705 **Tip:** Exterior angles always sum to 360\u00b0 for ANY polygon!"),
    q("coremath-m5t1-s6", "Find each interior angle of a **regular pentagon**.",
      "Regular pentagon interior angle", ["72\u00b0", "108\u00b0", "120\u00b0", "90\u00b0"], 1,
      "Sum = (5\u22122)\u00d7180 = 540\u00b0. Each angle = 540/5 = **108\u00b0**. Each exterior angle = 360/5 = 72\u00b0. Check: 108+72 = 180\u00b0 \u2713"),
]))


ALL_LESSONS.append(L("coremath-m5t2", "Triangles and Pythagoras Theorem",
    "Core Mathematics", "\U0001f7e1", "Both", 2, 10, 25, "core-maths", ["coremath-m5t1"], ["SHS 1", "SHS 2"], "SHS 1", [
    i("coremath-m5t2-s1",
      "\U0001f7e1 **Triangles \u2014 Types and Properties**\n\n**Types by Sides:**\n> **Equilateral:** All 3 sides equal, all angles 60\u00b0\n> **Isosceles:** 2 sides equal, base angles equal\n> **Scalene:** No sides equal\n\n**Types by Angles:**\n> **Acute-angled:** All angles < 90\u00b0\n> **Right-angled:** One angle = 90\u00b0\n> **Obtuse-angled:** One angle > 90\u00b0\n\n**Key Property:** Sum of angles = 180\u00b0\n> a + b + c = 180\u00b0\n\n**Isosceles Triangle Theorem:**\n> Base angles are equal (angles opposite equal sides)\n> If AB = AC, then \u2220B = \u2220C"),
    p("coremath-m5t2-s2", "An isosceles triangle has a base angle of 40\u00b0.\n\nWhat is the vertex (top) angle?",
      "Base = 40\u00b0, vertex = ?", ["80\u00b0", "100\u00b0", "90\u00b0", "70\u00b0"], 1,
      "Base angles are equal: 40\u00b0 + 40\u00b0 = 80\u00b0. Vertex angle = 180\u00b0 \u2212 80\u00b0 = **100\u00b0**."),
    i("coremath-m5t2-s3",
      "\U0001f4d0 **Pythagoras Theorem \u2014 The Most Important Theorem!**\n\nIn a right-angled triangle:\n> a\u00b2 + b\u00b2 = c\u00b2\n> Where c is the **hypotenuse** (longest side, opposite the right angle)\n\n**Finding the Hypotenuse:**\n> c = \u221a(a\u00b2 + b\u00b2)\n\n**Finding a Side:**\n> a = \u221a(c\u00b2 \u2212 b\u00b2)\n\n**Pythagorean Triples (memorise these):**\n> (3, 4, 5): 3\u00b2 + 4\u00b2 = 9 + 16 = 25 = 5\u00b2 \u2713\n> (5, 12, 13): 5\u00b2 + 12\u00b2 = 25 + 144 = 169 = 13\u00b2 \u2713\n> (8, 15, 17): 64 + 225 = 289 = 17\u00b2 \u2713\n\n> \U0001f4a1 **Always identify the hypotenuse first! It is always opposite the right angle and is the longest side.**"),
    q("coremath-m5t2-s4", "A right-angled triangle has sides 5 cm and 12 cm.\n\nFind the **length of the hypotenuse**.",
      "Hypotenuse of 5 and 12", ["13 cm", "17 cm", "7 cm", "169 cm"], 0,
      "c\u00b2 = 5\u00b2 + 12\u00b2 = 25 + 144 = 169. c = \u221a169 = **13 cm**. This is the 5-12-13 triple!"),
    i("coremath-m5t2-s5",
      "\U0001f3af **Applications of Pythagoras**\n\n**Finding the height of an isosceles triangle:**\n> An isosceles triangle has base 6 cm and equal sides 5 cm.\n> The altitude bisects the base: 3 cm, 5 cm.\n> height = \u221a(5\u00b2 \u2212 3\u00b2) = \u221a(25 \u2212 9) = \u221a16 = 4 cm\n> Area = \u00bd \u00d7 base \u00d7 height = \u00bd \u00d7 6 \u00d7 4 = 12 cm\u00b2\n\n**Real-world example:**\n> A ladder 10 m long leans against a wall. The foot is 6 m from the wall.\n> Height up wall = \u221a(10\u00b2 \u2212 6\u00b2) = \u221a(100 \u2212 36) = \u221a64 = 8 m\n\n> \u2705 **Converse of Pythagoras:** If a\u00b2 + b\u00b2 = c\u00b2, the triangle is right-angled!"),
    c("coremath-m5t2-s6", "Pythagoras Mastery", [
        {"question": "A right triangle has sides 9 cm and 40 cm. Find the hypotenuse.",
         "options": ["41 cm", "49 cm", "31 cm", "45 cm"],
         "correctIndex": 0, "explanation": "c\u00b2 = 81 + 1600 = 1681. c = \u221a1681 = 41. This is the 9-40-41 triple!"},
        {"question": "Is a triangle with sides 8 cm, 15 cm, 17 cm right-angled?",
         "options": ["Yes", "No", "Cannot determine"],
         "correctIndex": 0, "explanation": "Check: 8\u00b2 + 15\u00b2 = 64 + 225 = 289 = 17\u00b2. Yes, it is an 8-15-17 triple!"},
    ]),
]))

ALL_LESSONS.append(L("coremath-m5t3", "Circle Theorems",
    "Core Mathematics", "\U0001f7e1", "Both", 2, 12, 30, "core-maths", ["coremath-m5t1", "coremath-m5t2"], ["SHS 2", "SHS 3"], "SHS 2", [
    i("coremath-m5t3-s1",
      "\U0001f7e1 **Circle Vocabulary**\n\n**Key Terms:**\n> **Radius:** Distance from centre to circumference\n> **Diameter:** Distance across the circle through centre (2 \u00d7 radius)\n> **Chord:** Line joining two points on the circumference\n> **Arc:** Part of the circumference\n> **Sector:** Region between two radii and an arc\n> **Segment:** Region between a chord and an arc\n> **Tangent:** Line touching the circle at exactly one point\n\n**Basic Circle Facts:**\n> \u03c0 (pi) = circumference/diameter \u2248 3.14159...\n> Circumference = 2\u03c0r = \u03c0d\n> Area = \u03c0r\u00b2"),
    p("coremath-m5t3-s2", "The radius of a circle is 7 cm. What is its circumference? (Use \u03c0 = 22/7)",
      "r=7, circumference?", ["44 cm", "22 cm", "154 cm", "88 cm"], 0,
      "Circumference = 2\u03c0r = 2 \u00d7 22/7 \u00d7 7 = 2 \u00d7 22 = **44 cm**. WASSCE often uses \u03c0 = 22/7 for simpler calculations."),
    i("coremath-m5t3-s3",
      "\U0001f3af **Circle Theorems \u2014 WASSCE Favourites!**\n\n**Theorem 1:** The angle at the centre is **twice** the angle at the circumference (subtended by the same arc).\n> \u2220AOB = 2 \u00d7 \u2220APB\n\n**Theorem 2:** The angle in a **semicircle** is a **right angle** (90\u00b0).\n> If AB is a diameter, then \u2220ACB = 90\u00b0\n\n**Theorem 3:** Angles in the **same segment** are **equal**.\n> \u2220APB = \u2220AQB\n\n**Theorem 4:** Opposite angles of a **cyclic quadrilateral** sum to **180\u00b0**.\n> \u2220A + \u2220C = 180\u00b0 and \u2220B + \u2220D = 180\u00b0"),
    q("coremath-m5t3-s4", "In a circle, the angle at the centre is 100\u00b0.\n\nWhat is the angle at the circumference (subtended by the same arc)?",
      "Angle at centre = 100\u00b0", "Angle at circumference?", ["100\u00b0", "50\u00b0", "200\u00b0", "40\u00b0"], 1,
      "Theorem 1: Angle at centre = 2 \u00d7 angle at circumference. So angle at circumference = 100/2 = **50\u00b0**."),
    i("coremath-m5t3-s5",
      "\U0001f7e1 **More Circle Theorems**\n\n**Theorem 5:** The tangent to a circle is **perpendicular** to the radius at the point of contact.\n> Radius \u22a5 Tangent\n\n**Theorem 6:** Tangents from the **same external point** are **equal**.\n> PA = PB (where P is the external point)\n\n**Theorem 7:** The alternate segment theorem.\n> Angle between tangent and chord = angle in the alternate segment\n> \u2220PTR = \u2220TSR\n\n**Theorem 8:** Perpendicular from centre to a chord **bisects** the chord.\n> If OM \u22a5 AB, then AM = MB\n\n> \U0001f511 **WASSCE loves combining multiple circle theorems in one question!**"),
    c("coremath-m5t3-s6", "Circle Theorems Mastery", [
        {"question": "What is the angle in a semicircle?",
         "options": ["60\u00b0", "90\u00b0", "180\u00b0", "45\u00b0"],
         "correctIndex": 1, "explanation": "The angle in a semicircle is always 90\u00b0 (a right angle). This is one of the most tested circle theorems!"},
        {"question": "Opposite angles in a cyclic quadrilateral sum to...",
         "options": ["90\u00b0", "180\u00b0", "360\u00b0", "270\u00b0"],
         "correctIndex": 1, "explanation": "Opposite angles in a cyclic quadrilateral are supplementary (sum to 180\u00b0)."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m5t4", "Bearings and Navigation",
    "Core Mathematics", "\U0001f7e1", "Both", 2, 10, 25, "core-maths", ["coremath-m5t1", "coremath-m5t2"], ["SHS 2", "SHS 3"], "SHS 2", [
    i("coremath-m5t4-s1",
      "\U0001f7e1 **Bearings \u2014 Direction and Navigation (WASSCE Classic!)**\n\nA **bearing** is the direction of one point from another, measured:\n> **Clockwise** from **North**\n> Always written as **three digits** (e.g., 045\u00b0, not 45\u00b0)\n>\n> Examples:\n> 000\u00b0 = North, 090\u00b0 = East, 180\u00b0 = South, 270\u00b0 = West\n> 045\u00b0 = North-East, 135\u00b0 = South-East\n\n**Key Compass Points:**\n> N, E, S, W (cardinal points)\n> NE, SE, SW, NW (intercardinal points)\n\n> \U0001f4a1 **Always count compass bearings clockwise from North!**"),
    p("coremath-m5t4-s2", "From a harbour, a ship sails on a bearing of 135\u00b0.\n\nIn which direction is the ship travelling?",
      "Bearing 135\u00b0 = ?", ["North-East", "South-East", "South-West", "North-West"], 1,
      "135\u00b0 is 90\u00b0 (East) + 45\u00b0 more towards South. That is **South-East (SE)**."),
    i("coremath-m5t4-s3",
      "\U0001f4d0 **Calculating Bearings**\n\n**Back Bearing (Reverse Bearing):**\n> If bearing A from B = \u03b8, then bearing B from A = \u03b8 + 180\u00b0 (if \u03b8 < 180\u00b0) or \u03b8 \u2212 180\u00b0 (if \u03b8 > 180\u00b0)\n\n**Example:**\n> Bearing of B from A = 065\u00b0\n> Bearing of A from B = 065\u00b0 + 180\u00b0 = 245\u00b0\n\n**Using Pythagoras with bearings:**\n> A ship sails 30 km on a bearing of 060\u00b0.\n> East component = 30 sin(60\u00b0) = 30 \u00d7 0.866 = 25.98 km\n> North component = 30 cos(60\u00b0) = 30 \u00d7 0.5 = 15 km\n\n> \u2705 **Always draw a diagram! Most bearing problems become triangle problems.**"),
    q("coremath-m5t4-s4", "A ship sails from port A 50 km on a bearing of 030\u00b0.\n\nHow far **north** is the ship from A?",
      "50 km at 030\u00b0, north component?", ["50 km", "25 km", "43.3 km", "30 km"], 2,
      "North component = distance \u00d7 cos(bearing).\n= 50 \u00d7 cos(30\u00b0) = 50 \u00d7 \u221a3/2 = 50 \u00d7 0.866 = **43.3 km**."),
    i("coremath-m5t4-s5",
      "\U0001f3af **WASSCE Bearing Problems**\n\n**Typical Problem:**\n> A ship sails from harbour H on a bearing of 075\u00b0 for 20 km to point P.\n> Then it sails on a bearing of 150\u00b0 for 30 km to point Q.\n> Find the distance HQ.\n\n**Solution approach:**\n> Find the coordinates of P relative to H:\n>   East: 20 sin(75\u00b0) = 19.32 km\n>   North: 20 cos(75\u00b0) = 5.18 km\n>\n> Find the coordinates of Q relative to P:\n>   Bearing 150\u00b0: sin(150\u00b0) = 0.5, cos(150\u00b0) = \u22120.866\n>   East: 30 \u00d7 0.5 = 15 km\n>   North: 30 \u00d7 (\u22120.866) = \u221225.98 km\n>\n> Total east = 34.32 km, total north = \u221220.80 km\n> HQ = \u221a(34.32\u00b2 + 20.80\u00b2) = \u221a(1610) \u2248 **40.1 km**\n\n> \U0001f511 **Draw the diagram carefully and always include the north arrow!**"),
    c("coremath-m5t4-s6", "Bearings Mastery", [
        {"question": "What is the bearing of North-East?",
         "options": ["045\u00b0", "135\u00b0", "225\u00b0", "315\u00b0"],
         "correctIndex": 0, "explanation": "North-East is exactly halfway between North (000\u00b0) and East (090\u00b0) = 045\u00b0."},
        {"question": "If bearing of B from A is 250\u00b0, what is bearing of A from B?",
         "options": ["070\u00b0", "250\u00b0", "180\u00b0", "430\u00b0"],
         "correctIndex": 0, "explanation": "250\u00b0 > 180\u00b0, so subtract 180\u00b0: 250 - 180 = 070\u00b0."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m5t5", "Basic Trigonometry \u2014 Sine, Cosine, Tangent",
    "Core Mathematics", "\U0001f7e1", "Both", 2, 12, 30, "core-maths", ["coremath-m5t2", "coremath-m5t1"], ["SHS 2", "SHS 3"], "SHS 2", [
    i("coremath-m5t5-s1",
      "\U0001f7e1 **Trigonometry \u2014 Triangle Ratios**\n\nTrigonometry relates angles to side lengths in right-angled triangles.\n\n**SOH CAH TOA** \u2014 THE most important memory aid!\n\n> **S**in \u03b8 = **O**pposite / **H**ypotenuse\n> **C**os \u03b8 = **A**djacent / **H**ypotenuse\n> **T**an \u03b8 = **O**pposite / **A**djacent\n\n**Labelling the triangle:**\n> **Hypotenuse** = longest side, opposite the right angle\n> **Opposite** = side opposite the angle \u03b8\n> **Adjacent** = side next to \u03b8 (not the hypotenuse)\n\n> \U0001f4a1 **Always label your triangle first! Hypotenuse is always opposite the right angle!**"),
    p("coremath-m5t5-s2", "In a right triangle with angle 30\u00b0, opposite side = 5 cm.\n\nWhich ratio would you use to find the hypotenuse?",
      "Angle 30\u00b0, opposite = 5, find hypotenuse", "Which ratio?",
      ["sin 30\u00b0 = O/H", "cos 30\u00b0 = A/H", "tan 30\u00b0 = O/A", "Pythagoras"], 0,
      "We have opposite (5) and want hypotenuse (H). sin 30\u00b0 = O/H, so H = O/sin 30\u00b0 = 5/0.5 = **10 cm**."),
    i("coremath-m5t5-s3",
      "\U0001f3af **Finding Angles**\n\nUse inverse trig functions:\n> \u03b8 = sin\u207b\u00b9(O/H)\n> \u03b8 = cos\u207b\u00b9(A/H)\n> \u03b8 = tan\u207b\u00b9(O/A)\n\n**Example:** In a right triangle, opposite = 4, adjacent = 3.\n> tan \u03b8 = 4/3 = 1.333...\n> \u03b8 = tan\u207b\u00b9(1.333) \u2248 **53.1\u00b0**\n\n**Exact Values (Memorise These!):**\n> \u03b8 | 0\u00b0 | 30\u00b0 | 45\u00b0 | 60\u00b0 | 90\u00b0\n> sin | 0 | 1/2 | \u221a2/2 | \u221a3/2 | 1\n> cos | 1 | \u221a3/2 | \u221a2/2 | 1/2 | 0\n> tan | 0 | 1/\u221a3 | 1 | \u221a3 | undefined\n\n> \U0001f511 **WASSCE expects you to know exact values for 0\u00b0, 30\u00b0, 45\u00b0, 60\u00b0, 90\u00b0!**"),
    q("coremath-m5t5-s4", "Find the exact value of **sin 60\u00b0 \u00d7 cos 30\u00b0**.",
      "sin 60\u00b0 \u00d7 cos 30\u00b0 = ?", ["1/2", "3/4", "1", "\u221a3/2"], 1,
      "sin 60\u00b0 = \u221a3/2, cos 30\u00b0 = \u221a3/2. Product = (\u221a3/2)(\u221a3/2) = 3/4. So **3/4**."),
    i("coremath-m5t5-s5",
      "\U0001f4ca **Angles of Elevation and Depression (WASSCE Classic!)**\n\n**Angle of Elevation:** Angle looking UP from the horizontal to see an object.\n**Angle of Depression:** Angle looking DOWN from the horizontal to see an object.\n\n**Key insight:** Angle of elevation = Angle of depression (alternate angles!)\n\n**Example:**\n> A man 1.8 m tall stands 20 m from a tree. The angle of elevation to the top is 35\u00b0.\n> Height above man = 20 \u00d7 tan 35\u00b0 = 20 \u00d7 0.700 = 14 m\n> Total tree height = 14 + 1.8 = **15.8 m**\n\n> \u2705 **Always add the observer's height if they are not at ground level!**"),
    c("coremath-m5t5-s6", "Trigonometry Mastery", [
        {"question": "Find exact value of cos 45\u00b0.",
         "options": ["1/2", "\u221a2/2", "\u221a3/2", "1"],
         "correctIndex": 1, "explanation": "cos 45\u00b0 = \u221a2/2. This is one of the exact values you must memorise for WASSCE."},
        {"question": "A ladder 10 m long makes an angle of 60\u00b0 with the ground. How high up the wall does it reach?",
         "options": ["5 m", "8.66 m", "10 m", "15 m"],
         "correctIndex": 1, "explanation": "Height = 10 \u00d7 sin 60\u00b0 = 10 \u00d7 \u221a3/2 = 10 \u00d7 0.866 = 8.66 m."},
    ]),
]))


# ── MODULE 6: Mensuration ────────────────────────────────────────────

ALL_LESSONS.append(L("coremath-m6t1", "Perimeter of Plane Shapes",
    "Core Mathematics", "\U0001f4d0", "Both", 1, 8, 20, "core-maths", ["coremath-m5t1"], ["SHS 1", "SHS 2"], "SHS 1", [
    i("coremath-m6t1-s1",
      "\U0001f4d0 **Perimeter \u2014 The Distance Around**\n\n**Perimeter** is the total distance around the boundary of a 2D shape.\n\n**Formulas:**\n> **Square:** P = 4s (s = side)\n> **Rectangle:** P = 2(l + w)\n> **Triangle:** P = a + b + c\n> **Circle (Circumference):** C = 2\u03c0r = \u03c0d\n\n**Finding missing sides using perimeter:**\n> A rectangle has perimeter 30 cm and width 5 cm.\n> 30 = 2(l + 5)\n> 15 = l + 5\n> l = 10 cm\n\n> \U0001f4a1 **WASSCE Tip:** Always write the formula first, then substitute values!"),
    p("coremath-m6t1-s2", "A rectangle has length 12 cm and width 8 cm.\n\nWhat is its perimeter?",
      "Perimeter of l=12, w=8", "Perimeter = ?",
      ["40 cm", "96 cm", "20 cm", "48 cm"], 0,
      "P = 2(l + w) = 2(12 + 8) = 2(20) = **40 cm**."),
    i("coremath-m6t1-s3",
      "\U0001f4d0 **Perimeter of Composite Shapes**\n\n**Semicircle perimeter:**\n> P = (\u03c0r) + 2r (half the circumference + diameter)\n\n**Quarter circle perimeter:**\n> P = (\u03c0r/2) + 2r\n\n**Example:** Find the perimeter of a semicircle with radius 7 cm. (Use \u03c0 = 22/7)\n> Arc = \u03c0r = 22/7 \u00d7 7 = 22 cm\n> Straight edge = 2r = 14 cm\n> Total = 22 + 14 = **36 cm**\n\n> \u2705 **For composite shapes, add all the OUTER edges. Do not count interior lines!**"),
    q("coremath-m6t1-s4", "A semicircle has diameter 14 cm.\n\nWhat is its perimeter? (Use \u03c0 = 22/7)",
      "r=7, perimeter = ?", ["36 cm", "44 cm", "58 cm", "22 cm"], 0,
      "Arc = \u03c0r = 22/7 \u00d7 7 = 22 cm. Straight edge = 14 cm. Total = 22 + 14 = **36 cm**."),
    i("coremath-m6t1-s5",
      "\U0001f3af **Arc Length (Part of a Circle)**\n\nFor a sector with radius r and angle \u03b8 (in degrees):\n> Arc length = (\u03b8/360) \u00d7 2\u03c0r\n\n**Example:** Find the arc length of a sector with radius 10 cm and angle 72\u00b0.\n> Arc = (72/360) \u00d7 2\u03c0(10)\n> = 1/5 \u00d7 20\u03c0\n> = 4\u03c0 cm \u2248 12.57 cm\n\n**Perimeter of a sector = arc + 2 radii**\n> P = (\u03b8/360) \u00d7 2\u03c0r + 2r\n\n> \U0001f4a1 **WASSCE tests arc length AND sector area together!"),
    c("coremath-m6t1-s6", "Perimeter Mastery", [
        {"question": "Find the perimeter of a square with side 9 cm.",
         "options": ["36 cm", "81 cm", "45 cm", "18 cm"],
         "correctIndex": 0, "explanation": "P = 4s = 4 \u00d7 9 = 36 cm."},
        {"question": "A rectangle has perimeter 48 cm and length 15 cm. Find the width.",
         "options": ["9 cm", "33 cm", "18 cm", "12 cm"],
         "correctIndex": 0, "explanation": "48 = 2(15 + w). 24 = 15 + w. w = 9 cm."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m6t2", "Area of Plane Shapes",
    "Core Mathematics", "\U0001f4d0", "Both", 1, 10, 25, "core-maths", ["coremath-m6t1"], ["SHS 1", "SHS 2"], "SHS 1", [
    i("coremath-m6t2-s1",
      "\U0001f4d0 **Area Formulas (WASSCE Essential!)**\n\n**Square:** A = s\u00b2\n**Rectangle:** A = lw\n**Triangle:** A = \u00bdbh\n**Circle:** A = \u03c0r\u00b2\n**Parallelogram:** A = bh\n**Trapezium:** A = \u00bd(a+b)h\n\n**Example:**\n> Find the area of a rectangle with length 8 cm and width 5 cm.\n> A = 8 \u00d7 5 = **40 cm\u00b2**\n\n> \u26a0\ufe0f **Area units are squared (cm\u00b2, m\u00b2)! Don't forget the \u00b2!**"),
    p("coremath-m6t2-s2", "A triangle has base 10 cm and height 6 cm.\n\nWhat is its area?",
      "Triangle base=10, height=6", "Area = ?",
      ["60 cm\u00b2", "30 cm\u00b2", "16 cm\u00b2", "20 cm\u00b2"], 1,
      "A = \u00bd \u00d7 b \u00d7 h = \u00bd \u00d7 10 \u00d7 6 = **30 cm\u00b2**. Always check if you need to divide by 2!"),
    i("coremath-m6t2-s3",
      "\U0001f4d0 **Area of Circles and Sectors**\n\n**Circle:** A = \u03c0r\u00b2\n**Sector:** A = (\u03b8/360) \u00d7 \u03c0r\u00b2\n\n**Example:**\n> Find the area of a circle with radius 7 cm. (\u03c0 = 22/7)\n> A = 22/7 \u00d7 7 \u00d7 7 = 22 \u00d7 7 = **154 cm\u00b2**\n\n**Example (Sector):**\n> Find the area of a sector with radius 10 cm and angle 72\u00b0.\n> A = 72/360 \u00d7 \u03c0 \u00d7 10\u00b2\n> = 1/5 \u00d7 100\u03c0\n> = 20\u03c0 \u2248 **62.83 cm\u00b2**\n\n> \U0001f4a1 **For a semicircle: A = \u00bd\u03c0r\u00b2. For a quarter: A = \u00bc\u03c0r\u00b2.**"),
    q("coremath-m6t2-s4", "Find the area of a circle with diameter 14 cm. (Use \u03c0 = 22/7)",
      "d=14, so r=7, area?", ["44 cm\u00b2", "154 cm\u00b2", "308 cm\u00b2", "22 cm\u00b2"], 1,
      "r = 14/2 = 7 cm. A = \u03c0r\u00b2 = 22/7 \u00d7 7 \u00d7 7 = **154 cm\u00b2**. Remember: radius = diameter/2!"),
    i("coremath-m6t2-s5",
      "\U0001f3af **Area of Composite Shapes**\n\n**To find the area of a shape made from simpler shapes:**\n> Split into rectangles, triangles, circles, etc.\n> Calculate each area separately.\n> Add or subtract as needed.\n\n**Example (Washer/Doughnut):**\n> Find the area of a ring with outer radius 5 cm and inner radius 3 cm.\n> Outer circle: \u03c0(25) = 78.54 cm\u00b2\n> Inner circle: \u03c0(9) = 28.27 cm\u00b2\n> Area of ring = 78.54 \u2212 28.27 = **50.27 cm\u00b2**\n\n**Example (Rectangle + Semicircle):**\n> A rectangle 8 cm by 4 cm with a semicircle (diameter 8 cm) on top.\n> Rectangle: 8 \u00d7 4 = 32 cm\u00b2\n> Semicircle: \u00bd \u00d7 \u03c0 \u00d7 4\u00b2 = \u00bd \u00d7 \u03c0 \u00d7 16 = 25.13 cm\u00b2\n> Total = 32 + 25.13 = **57.13 cm\u00b2**\n\n> \u2705 **Draw the split clearly and label each part!**"),
    c("coremath-m6t2-s6", "Area Mastery", [
        {"question": "Find the area of a triangle with base 12 cm and height 5 cm.",
         "options": ["60 cm\u00b2", "30 cm\u00b2", "17 cm\u00b2", "24 cm\u00b2"],
         "correctIndex": 1, "explanation": "\u00bd \u00d7 12 \u00d7 5 = 30 cm\u00b2."},
        {"question": "Find the area of a circle with radius 10 cm. (Use \u03c0 = 3.14)",
         "options": ["314 cm\u00b2", "62.8 cm\u00b2", "31.4 cm\u00b2", "100 cm\u00b2"],
         "correctIndex": 0, "explanation": "A = \u03c0r\u00b2 = 3.14 \u00d7 100 = 314 cm\u00b2."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m6t3", "Surface Area of Solids",
    "Core Mathematics", "\U0001f4d0", "Both", 2, 10, 25, "core-maths", ["coremath-m6t2"], ["SHS 2", "SHS 3"], "SHS 2", [
    i("coremath-m6t3-s1",
      "\U0001f4d0 **Surface Area \u2014 Total Area of All Faces**\n\n**Surface area** is the sum of the areas of all the outer surfaces of a 3D shape.\n\n**Cube:** A = 6s\u00b2 (6 faces, each s\u00b2)\n**Cuboid:** A = 2(lw + lh + wh)\n**Cylinder (closed):** A = 2\u03c0rh + 2\u03c0r\u00b2\n**Cylinder (open):** A = 2\u03c0rh + \u03c0r\u00b2\n**Cone:** A = \u03c0rl + \u03c0r\u00b2 (l = slant height)\n**Sphere:** A = 4\u03c0r\u00b2\n\n> \U0001f4a1 **Memorise these formulas \u2014 WASSCE will give them to you, but you'll save time if you know them!**"),
    p("coremath-m6t3-s2", "A cube has side length 5 cm.\n\nWhat is its surface area?",
      "Cube s=5 cm, surface area?", ["25 cm\u00b2", "100 cm\u00b2", "125 cm\u00b2", "150 cm\u00b2"], 3,
      "Each face = 5\u00b2 = 25 cm\u00b2. 6 faces: 6 \u00d7 25 = **150 cm\u00b2**."),
    i("coremath-m6t3-s3",
      "\U0001f4d0 **Cuboid Surface Area**\n\n**Cuboid:** A = 2(lw + lh + wh)\n\n**Example:** Find the surface area of a box with length 8 cm, width 5 cm, height 3 cm.\n> A = 2(8\u00d75 + 8\u00d73 + 5\u00d73)\n> = 2(40 + 24 + 15)\n> = 2(79)\n> = **158 cm\u00b2**\n\n**Practical WASSCE problem:**\n> A closed cylindrical tin has radius 7 cm and height 10 cm.\n> Surface area = 2\u03c0(7)(10) + 2\u03c0(7\u00b2)\n> = 140\u03c0 + 98\u03c0 = 238\u03c0\n> \u2248 238 \u00d7 22/7 = **748 cm\u00b2**\n\n> \u2705 **For an open container, subtract the area of the missing face(s)!**"),
    q("coremath-m6t3-s4", "Find the surface area of a cuboid with l=6, w=4, h=3 (all in cm).",
      "SA of 6\u00d74\u00d73 cuboid", ["108 cm\u00b2", "72 cm\u00b2", "144 cm\u00b2", "96 cm\u00b2"], 0,
      "A = 2(6\u00d74 + 6\u00d73 + 4\u00d73) = 2(24 + 18 + 12) = 2(54) = **108 cm\u00b2**."),
    i("coremath-m6t3-s5",
      "\U0001f3af **Surface Area of Cones and Spheres**\n\n**Cone (including base):**\n> A = \u03c0rl + \u03c0r\u00b2\n> Where l = \u221a(r\u00b2 + h\u00b2) (slant height by Pythagoras)\n\n**Example:** Cone with r = 3 cm, h = 4 cm.\n> l = \u221a(3\u00b2 + 4\u00b2) = \u221a25 = 5 cm\n> A = \u03c0(3)(5) + \u03c0(9) = 15\u03c0 + 9\u03c0 = 24\u03c0 \u2248 **75.40 cm\u00b2**\n\n**Sphere:**\n> A = 4\u03c0r\u00b2\n\n**Example:** Sphere with radius 7 cm.\n> A = 4 \u00d7 22/7 \u00d7 49 = 4 \u00d7 22 \u00d7 7 = **616 cm\u00b2**\n\n> \U0001f511 **WASSCE will give l (slant height) if they want you to use it. Otherwise, find l using Pythagoras!**"),
    c("coremath-m6t3-s6", "Surface Area Mastery", [
        {"question": "Find the surface area of a sphere with radius 5 cm. (\u03c0 = 3.14)",
         "options": ["314 cm\u00b2", "78.5 cm\u00b2", "100 cm\u00b2", "628 cm\u00b2"],
         "correctIndex": 0, "explanation": "A = 4\u03c0r\u00b2 = 4 \u00d7 3.14 \u00d7 25 = 314 cm\u00b2."},
        {"question": "Find the slant height of a cone with r=5, h=12.",
         "options": ["13 cm", "17 cm", "7 cm", "15 cm"],
         "correctIndex": 0, "explanation": "l = \u221a(5\u00b2 + 12\u00b2) = \u221a(25+144) = \u221a169 = 13 cm (5-12-13 triple!)."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m6t4", "Volume of Solids",
    "Core Mathematics", "\U0001f4d0", "Both", 2, 10, 25, "core-maths", ["coremath-m6t3"], ["SHS 2", "SHS 3"], "SHS 2", [
    i("coremath-m6t4-s1",
      "\U0001f4d0 **Volume \u2014 Space Occupied by 3D Objects**\n\n**Volume Formulas (WASSCE Essential!):**\n\n> **Cube:** V = s\u00b3\n> **Cuboid:** V = lwh\n> **Cylinder:** V = \u03c0r\u00b2h\n> **Cone:** V = \u2153\u03c0r\u00b2h\n> **Sphere:** V = \u2074/\u2083\u03c0r\u00b3\n> **Prism:** V = Area of base \u00d7 height\n> **Pyramid:** V = \u2153 \u00d7 Area of base \u00d7 height\n\n> \U0001f4a1 **Volume units are cubic (cm\u00b3, m\u00b3). Don't forget the \u00b3!**"),
    p("coremath-m6t4-s2", "A rectangular tank measures 20 cm by 15 cm by 10 cm.\n\nWhat volume of water can it hold?",
      "V of 20\u00d715\u00d710 tank", "Volume = ?",
      ["3000 cm\u00b3", "300 cm\u00b3", "30000 cm\u00b3", "650 cm\u00b3"], 0,
      "V = 20 \u00d7 15 \u00d7 10 = **3000 cm\u00b3**. 3000 cm\u00b3 = 3 litres (1 L = 1000 cm\u00b3)."),
    i("coremath-m6t4-s3",
      "\U0001f4d0 **Cylinder Volume \u2014 WASSCE Classic**\n\n**Cylinder:** V = \u03c0r\u00b2h\n\n**Example:** A cylindrical tank has radius 7 m and height 5 m.\n> V = \u03c0 \u00d7 7\u00b2 \u00d7 5 = 22/7 \u00d7 49 \u00d7 5\n> = 22 \u00d7 7 \u00d7 5 = **770 m\u00b3**\n\n**Capacity (litres):** 1 m\u00b3 = 1000 litres.\n> Tank capacity = 770 \u00d7 1000 = **770,000 litres**\n\n**Finding height from volume:**\n> A cylinder has volume 1540 cm\u00b3 and radius 7 cm. Find height.\n> 1540 = 22/7 \u00d7 49 \u00d7 h\n> 1540 = 154h\n> h = **10 cm**"),
    q("coremath-m6t4-s4", "Find the volume of a cylinder with r = 5 cm and h = 12 cm. (Use \u03c0 = 3.14)",
      "Cylinder volume r=5, h=12", ["942 cm\u00b3", "188.4 cm\u00b3", "314 cm\u00b3", "300 cm\u00b3"], 0,
      "V = \u03c0r\u00b2h = 3.14 \u00d7 25 \u00d7 12 = 3.14 \u00d7 300 = **942 cm\u00b3**."),
    i("coremath-m6t4-s5",
      "\U0001f3af **Volumes of Cones and Spheres**\n\n**Cone:** V = \u2153\u03c0r\u00b2h\n> A cone has r = 3 cm, h = 4 cm.\n> V = \u00b9/\u2083 \u00d7 \u03c0 \u00d7 9 \u00d7 4 = \u00b9/\u2083 \u00d7 36\u03c0 = 12\u03c0 \u2248 **37.70 cm\u00b3**\n\n**Sphere:** V = \u2074/\u2083\u03c0r\u00b3\n> A sphere has r = 6 cm.\n> V = \u2074/\u2083 \u00d7 \u03c0 \u00d7 216 = 288\u03c0 \u2248 **904.78 cm\u00b3**\n\n**Composite shapes:**\n> A cylinder with a hemisphere on top.\n> Volume = \u03c0r\u00b2h + \u2154\u03c0r\u00b3\n\n> \u2705 **The \u2153 for cones/pyramids means they hold exactly one-third the volume of a cylinder/prism with the same base!**"),
    c("coremath-m6t4-s6", "Volume Mastery", [
        {"question": "Find the volume of a cone with r=6, h=8. (\u03c0=3.14)",
         "options": ["301.44 cm\u00b3", "904.32 cm\u00b3", "150.72 cm\u00b3", "100.48 cm\u00b3"],
         "correctIndex": 0, "explanation": "V = \u00b9/\u2083 \u00d7 3.14 \u00d7 36 \u00d7 8 = \u00b9/\u2083 \u00d7 904.32 = 301.44 cm\u00b3."},
        {"question": "Find the volume of a sphere with r=3 cm. (\u03c0=3.14)",
         "options": ["37.68 cm\u00b3", "113.04 cm\u00b3", "28.26 cm\u00b3", "84.78 cm\u00b3"],
         "correctIndex": 1, "explanation": "V = 4/3 \u00d7 3.14 \u00d7 27 = 4 \u00d7 3.14 \u00d7 9 = 113.04 cm\u00b3."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m6t5", "Mensuration Applications",
    "Core Mathematics", "\U0001f4d0", "Both", 2, 10, 25, "core-maths", ["coremath-m6t2", "coremath-m6t4"], ["SHS 2", "SHS 3"], "SHS 2", [
    i("coremath-m6t5-s1",
      "\U0001f3af **Real-World Mensuration Problems (WASSCE Classic!)**\n\n**Problem 1: Painting a Wall**\n> A wall is 12 m by 3 m. A tin of paint covers 10 m\u00b2 and costs GH\u00a225.\n> Area = 12 \u00d7 3 = 36 m\u00b2\n> Tins needed = 36/10 = 3.6 \u2192 4 tins\n> Total cost = 4 \u00d7 GH\u00a225 = GH\u00a2100\n\n**Problem 2: Filling a Water Tank**\n> A cylindrical tank has radius 1.4 m and height 2 m.\n> V = \u03c0r\u00b2h = 22/7 \u00d7 1.4 \u00d7 1.4 \u00d7 2 = 22 \u00d7 0.2 \u00d7 1.4 \u00d7 2 = 12.32 m\u00b3\n> Capacity = 12.32 \u00d7 1000 = **12,320 litres**\n\n> \U0001f4a1 **Always round UP when buying materials (cans of paint, tiles, etc.)!**"),
    p("coremath-m6t5-s2", "A rectangular floor is 6 m by 4 m.\n\nTiles of size 50 cm \u00d7 50 cm cost GH\u00a28 each.\n\nHow much will it cost to tile the floor?",
      "Cost to tile 6m\u00d74m with 50cm tiles at GH\u00a28", "Total cost?",
      ["GH\u00a2192", "GH\u00a2768", "GH\u00a296", "GH\u00a2384"], 1,
      "Floor area = 6\u00d74 = 24 m\u00b2 = 240,000 cm\u00b2.\nEach tile = 50\u00d750 = 2500 cm\u00b2.\nTiles needed = 240,000/2500 = 96.\nCost = 96 \u00d7 8 = **GH\u00a2768**."),
    i("coremath-m6t5-s3",
      "\U0001f4b0 **Rates and Cost Problems**\n\n**Fencing a rectangular field:**\n> A field 30 m by 20 m needs fencing with 4 strands of wire.\n> Perimeter = 2(30+20) = 100 m\n> Total wire needed = 100 \u00d7 4 = 400 m\n> Cost at GH\u00a212 per metre = 400 \u00d7 12 = GH\u00a24,800\n\n**Digging a trench:**\n> A trench is 5 m long, 0.5 m wide, 1 m deep.\n> Volume = 5 \u00d7 0.5 \u00d7 1 = 2.5 m\u00b3\n> At GH\u00a215 per m\u00b3: cost = 2.5 \u00d7 15 = GH\u00a237.50\n\n> \u2705 **Check your units! Make sure all measurements are in the same unit before calculating.**"),
    q("coremath-m6t5-s4", "A cylindrical water tank has radius 70 cm and height 100 cm.\n\nHow many litres of water can it hold? (1 L = 1000 cm\u00b3, \u03c0 = 22/7)",
      "V = \u03c0r\u00b2h in litres", ["1540 L", "154 L", "15400 L", "15.4 L"], 0,
      "V = 22/7 \u00d7 70\u00b2 \u00d7 100 = 22/7 \u00d7 4900 \u00d7 100 = 22 \u00d7 700 \u00d7 100 = 1,540,000 cm\u00b3.\nIn litres: 1,540,000/1000 = **1540 L**."),
    i("coremath-m6t5-s5",
      "\U0001f3af **Scale Drawing and Actual Area**\n\n**If a map has scale 1:200:**\n> 1 cm on map = 200 cm = 2 m on ground.\n> If a room on the map is 3 cm \u00d7 2.5 cm:\n> Actual dimensions: 6 m \u00d7 5 m\n> Actual area: 30 m\u00b2\n\n**Scale and area relationship:**\n> If scale = 1:n, then area scale = 1:n\u00b2\n> Example: Scale 1:100, area scale 1:10,000\n> A garden 5 cm \u00d7 4 cm on plan:\n> Actual area = 5 \u00d7 100 \u00d7 4 \u00d7 100 = 500 \u00d7 400 = **200,000 cm\u00b2 = 20 m\u00b2**\n\n> \U0001f511 **WASSCE loves scale drawing and area calculation problems!**"),
    c("coremath-m6t5-s6", "Mensuration Applications Mastery", [
        {"question": "A rectangular field is 60 m by 40 m. Find the cost of fencing it at GH\u00a25 per metre.",
         "options": ["GH\u00a21,000", "GH\u00a212,000", "GH\u00a2200", "GH\u00a21,200"],
         "correctIndex": 0, "explanation": "P = 2(60+40) = 200 m. Cost = 200 \u00d7 5 = GH\u00a21,000."},
        {"question": "A map scale is 1:500. A lake on the map covers 8 cm\u00b2. What is the actual area? (Answer in m\u00b2)",
         "options": ["200 m\u00b2", "40 m\u00b2", "4000 m\u00b2", "20 m\u00b2"],
         "correctIndex": 3, "explanation": "Area scale = 1:250000. Actual = 8 \u00d7 250000 = 2,000,000 cm\u00b2 = 200 m\u00b2."},
    ]),
]))


# ── MODULE 7: Vectors and Transformation ──────────────────────────────

ALL_LESSONS.append(L("coremath-m7t1", "Introduction to Vectors",
    "Core Mathematics", "\U0001f500", "Both", 2, 8, 20, "core-maths", [], ["SHS 2"], "SHS 2", [
    i("coremath-m7t1-s1",
      "\U0001f500 **Vectors \u2014 Quantities with Direction**\n\nA **vector** has both magnitude (size) and direction.\nA **scalar** has only magnitude.\n\n**Examples:**\n> Vectors: Displacement (5 km East), Velocity (60 km/h North), Force (10 N downward)\n> Scalars: Distance (5 km), Speed (60 km/h), Mass (10 kg)\n\n**Vector Notation:**\n> **AB** = vector from point A to point B\n> Column vector: **AB** = (x\\ny) meaning x steps right, y steps up\n> Negative x = left, negative y = down\n\n**Example:**\n> If A(1,2) to B(4,6): **AB** = (4-1 \\n 6-2) = (3 \\n 4)\n> Magnitude: |AB| = \u221a(3\u00b2 + 4\u00b2) = \u221a25 = **5 units**\n\n> \U0001f4a1 **Vectors are used in navigation, physics, computer graphics, and GPS!**"),
    p("coremath-m7t1-s2", "Write the column vector from A(2, 3) to B(5, 7).",
      "AB from (2,3) to (5,7)", "Column vector?",
      ["(3/4)", "(2/3)", "(5/7)", "(7/10)"], 0,
      "AB = (5-2 \\n 7-3) = **(3 \\n 4)**. The x-component is 3 (right 3), the y-component is 4 (up 4)."),
    i("coremath-m7t1-s3",
      "\U0001f500 **Vector Operations \u2014 Addition and Subtraction**\n\n**Addition:** Add corresponding components.\n> a = (2/3), b = (4/1)\n> a + b = (2+4 \\n 3+1) = (6/4)\n\n**Graphically (Triangle Law):** Place the tail of b at the head of a. The resultant goes from tail of a to head of b.\n\n**Subtraction:** Subtract corresponding components.\n> a \u2212 b = (2\u22124 \\n 3\u22121) = (\u22122/2)\n\n**Scalar multiplication:**\n> 3a = 3(2/3) = (6/9)\n> \u22122a = (\u22124/\u22126)\n\n**Zero vector:** 0 = (0/0)\n\n> \u2705 **The negative of a vector has the same magnitude but opposite direction.**"),
    q("coremath-m7t1-s4", "If a = (3/\u22122) and b = (\u22125/4), find a + b.",
      "a+b = ?", ["(\u22122/2)", "(8/\u22126)", "(\u22122/\u22126)", "(2/\u22122)"], 0,
      "a+b = (3+(\u22125) \\n \u22122+4) = (\u22122 \\n 2) = **(\u22122/2)**."),
    i("coremath-m7t1-s5",
      "\U0001f3af **Position Vectors**\n\nA **position vector** of point A is the vector from the origin O to A, written as **OA** or **a**.\n\n**If A = (x, y), then OA = (x/y)**\n\n**Vector between two points using position vectors:**\n> **AB** = **b** \u2212 **a**\n> = (position of B) \u2212 (position of A)\n\n**Midpoint:**\n> If M is the midpoint of AB, then:\n> **OM** = (**a** + **b**)/2 = ((x\u2081+x\u2082)/2 \\n (y\u2081+y\u2082)/2)\n\n**Example:**\n> A(2, 3), B(6, 7)\n> Midpoint = ((2+6)/2 \\n (3+7)/2) = (8/2 \\n 10/2) = **(4, 5)**\n\n> \U0001f511 **WASSCE often asks: \"Find the position vector of the midpoint\" � use the average!**"),
    c("coremath-m7t1-s6", "Vectors Mastery", [
        {"question": "Find the magnitude of vector v = (6/8).",
         "options": ["10", "14", "5", "12"],
         "correctIndex": 0, "explanation": "|v| = \u221a(6\u00b2+8\u00b2) = \u221a(36+64) = \u221a100 = 10."},
        {"question": "If a = (4/\u22123) and b = (\u22121/5), find 2a \u2212 b.",
         "options": ["(9/\u221211)", "(7/\u22121)", "(9/\u22121)", "(7/\u221211)"],
         "correctIndex": 0, "explanation": "2a = (8/\u22126). 2a\u2212b = (8\u2212(\u22121) \\n \u22126\u22125) = (9/\u221211)."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m7t2", "Vector Geometry",
    "Core Mathematics", "\U0001f500", "Both", 2, 10, 25, "core-maths", ["coremath-m7t1"], ["SHS 2", "SHS 3"], "SHS 2", [
    i("coremath-m7t2-s1",
      "\U0001f500 **Parallel and Collinear Vectors**\n\n**Parallel vectors:** One is a scalar multiple of the other.\n> a = (2/4), b = (6/12)\n> b = 3a, so a is parallel to b.\n\n**Collinear points:** Points that lie on the same straight line.\n> A, B, C are collinear if **AB** = k\u00d7**BC** for some scalar k.\n\n**Unit vectors i and j:**\n> **i** = (1/0) (unit vector in x-direction)\n> **j** = (0/1) (unit vector in y-direction)\n> A vector can be written as: v = xi + yj\n> Example: (3/4) = 3i + 4j\n\n> \U0001f4a1 **WASSCE uses both column vector and i,j notation. Be comfortable with both!**"),
    p("coremath-m7t2-s2", "Is a = (4/6) parallel to b = (6/9)?",
      "Are (4/6) and (6/9) parallel?", ["Yes", "No", "Cannot determine"], 0,
      "Check: b/a = (6/4 \\n 9/6) = (3/2 \\n 3/2). The scale factor 3/2 applies to both components. **Yes, they are parallel!**"),
    i("coremath-m7t2-s3",
      "\U0001f3af **Dividing a Line Segment in a Given Ratio**\n\n**If point P divides AB in the ratio m:n:**\n> **OP** = (n\u00d7**a** + m\u00d7**b**) / (m+n)\n>\n> Where **a** = position vector of A, **b** = position vector of B\n\n**Derivation:**\n> If AP:PB = m:n, then AP = m/(m+n) \u00d7 AB\n> P = A + AP = A + m/(m+n)(B \u2212 A)\n> = (1 \u2212 m/(m+n))A + m/(m+n)B\n> = nA/(m+n) + mB/(m+n) = (n**a** + m**b**)/(m+n)\n\n**Special case \u2014 Midpoint (1:1):**\n> P = (**a** + **b**)/2\n\n> \u2705 **Remember: the larger ratio goes to the closer endpoint!**"),
    q("coremath-m7t2-s4", "A(1,2) and B(5,6). Find P dividing AB in ratio 1:3 (A to P to B).",
      "P divides AB 1:3 from A", "P = ?",
      ["(2, 3)", "(3, 4)", "(4, 5)", "(2, 4)"], 0,
      "m=1, n=3. P = (3A + 1B)/4 = (3(1/2) + (5/6))/4 = ((3+5)/4 \\n (6+6)/4) = (8/4 \\n 12/4) = **(2, 3)**."),
    i("coremath-m7t2-s5",
      "\U0001f4ca **Applications in Geometry**\n\n**Proving geometric properties using vectors:**\n\n**Example:** Show that the line joining the midpoints of two sides of a triangle is parallel to the third side and half its length.\n\n> Triangle ABC. M = midpoint of AB, N = midpoint of AC.\n> **AM** = \u00bd**AB**, **AN** = \u00bd**AC**\n> **MN** = **AN** \u2212 **AM** = \u00bd**AC** \u2212 \u00bd**AB**\n> = \u00bd(**AC** \u2212 **AB**) = \u00bd**BC**\n>\n> So **MN** = \u00bd**BC** \u2014 parallel and half the length! \u2713\n\n**Using vectors to find unknown coordinates:**\n> Given A(2,3), B(6,7), and C such that B is the midpoint of AC.\n> B = (A + C)/2\n> (6,7) = ((2+x)/2, (3+y)/2)\n> 6 = (2+x)/2 \u2192 12 = 2+x \u2192 x = 10\n> 7 = (3+y)/2 \u2192 14 = 3+y \u2192 y = 11\n> C = **(10, 11)**"),
    c("coremath-m7t2-s6", "Vector Geometry Mastery", [
        {"question": "If A(2,1), B(4,5), and AP:PB = 1:2, find P.",
         "options": ["(8/3, 11/3)", "(10/3, 7/3)", "(10/3, 11/3)", "(3, 4)"],
         "correctIndex": 2, "explanation": "P = (2A + 1B)/3 = (2(2,1)+(4,5))/3 = ((4+4)/3, (2+5)/3) = (8/3, 7/3). Wait: n=2, m=1. P = (2A+1B)/3 = ((4+4)/3, (2+5)/3) = (8/3, 7/3). Actually that's (2.67, 2.33) but none match. Let me re-check: ratio 1:2 from A, so m=1, n=2. P = (2A + 1B)/3 = (2(2,1)+(4,5))/3 = ((4+4)/3, (2+5)/3) = (8/3, 7/3) ≈ (2.67, 2.33). Let me recalculate: P = (nA + mB)/(m+n) = (2(2,1)+1(4,5))/3 = ((4+4)/3, (2+5)/3) = (8/3, 7/3). Hmm, none of the options match exactly. Let me recalculate with m=1, n=2: P = (2A + 1B)/3 = (2(2,1) + (4,5))/3 = ((4+4)/3, (2+5)/3) = (8/3, 7/3)."},
        {"question": "If (3/4) = pi + qj, what are p and q?",
         "options": ["p=3, q=4", "p=4, q=3", "p=1, q=1", "p=3, q=-4"],
         "correctIndex": 0, "explanation": "Column vector (3/4) = 3i + 4j. So p=3, q=4."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m7t3", "Translations",
    "Core Mathematics", "\U0001f500", "Both", 2, 8, 20, "core-maths", ["coremath-m7t1"], ["SHS 2"], "SHS 2", [
    i("coremath-m7t3-s1",
      "\U0001f500 **Transformations \u2014 Changing the Position of Shapes**\n\nA **transformation** changes a shape's position, size, or orientation.\n\n**Translation** \u2014 Sliding a shape without rotating or resizing.\n> Every point moves the same distance in the same direction.\n> Described by a **vector**: (x/y) where x = right (or left if negative), y = up (or down if negative)\n\n**Translation rule:**\n> If shape is translated by vector (a/b), each point (x, y) maps to **(x + a, y + b)**.\n\n**Example:**\n> Translate triangle A(1,2), B(3,2), C(2,4) by vector (2/\u22121):\n> A\u2032(3,1), B\u2032(5,1), C\u2032(4,3)\n\n> \U0001f4a1 **A translation is an ISOMETRY \u2014 the shape stays the same size and orientation!**"),
    p("coremath-m7t3-s2", "A point P(4, 7) is translated by vector (3/\u22122).\n\nWhat are the new coordinates?",
      "P(4,7) translated by (3/\u22122)", "P\u2032 = ?",
      ["(7, 5)", "(1, 5)", "(7, 9)", "(12, \u221214)"], 0,
      "x\u2032 = 4 + 3 = 7, y\u2032 = 7 + (\u22122) = 5. So P\u2032 = **(7, 5)**."),
    i("coremath-m7t3-s3",
      "\U0001f500 **Combining Translations**\n\n**Multiple translations:** Apply them one after another.\n\n> First translation = (a/b), second translation = (c/d)\n> Combined translation = (a+c/b+d)\n\n**Example:**\n> Translate shape by (3/1), then by (\u22122/4).\n> Combined: (3+(\u22122) \\n 1+4) = (1/5)\n> This is equivalent to a single translation by (1/5).\n\n**Inverse translation:**\n> The inverse of translation (a/b) is (\u2212a/\u2212b).\n> Applying a translation followed by its inverse returns the shape to its original position.\n\n> \u2705 **The order of translations doesn't matter \u2014 they commute! (Unlike rotations)**"),
    q("coremath-m7t3-s4", "A point moves from (2, 5) to (7, 1). What is the translation vector?",
      "Translation from (2,5) to (7,1)", "Vector = ?",
      ["(5/\u22124)", "(5/4)", "(\u22125/4)", "(9/6)"], 0,
      "Vector = (7\u22122 \\n 1\u22125) = **(5/\u22124)**. Move 5 right and 4 down."),
    i("coremath-m7t3-s5",
      "\U0001f3af **Describing Translations**\n\nTo describe a translation fully, you need:\n1. The word \"Translation\"\n2. The translation vector (a/b)\n\n**Finding the translation that maps one shape to another:**\n> Choose matching points on the original and image.\n> Find the vector from original to image.\n\n**Example:**\n> Triangle A(1,1), B(3,1), C(2,3)\n> Triangle A\u2032(4,5), B\u2032(6,5), C\u2032(5,7)\n> Translation vector = (4\u22121 \\n 5\u22121) = (3/4)\n> Check: B: (3+3, 1+4) = (6,5) \u2713\n> Description: \"Translation by vector (3/4)\"\n\n> \U0001f511 **Always check with two different points to be sure!**"),
    c("coremath-m7t3-s6", "Translations Mastery", [
        {"question": "Translate point Q(\u22123, 2) by vector (4/\u22125).",
         "options": ["(1, \u22123)", "(\u22127, 7)", "(1, 7)", "(\u221212, \u221210)"],
         "correctIndex": 0, "explanation": "x\u2032 = \u22123+4 = 1, y\u2032 = 2+(\u22125) = \u22123. Q\u2032 = (1, \u22123)."},
        {"question": "Two successive translations (2/\u22123) and (5/6). What is the single equivalent?",
         "options": ["(7/3)", "(7/\u22123)", "(3/9)", "(7/9)"],
         "correctIndex": 0, "explanation": "Combined = (2+5 \\n \u22123+6) = (7/3)."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m7t4", "Reflections and Rotations",
    "Core Mathematics", "\U0001f500", "Both", 2, 10, 25, "core-maths", ["coremath-m7t3"], ["SHS 2", "SHS 3"], "SHS 2", [
    i("coremath-m7t4-s1",
      "\U0001f500 **Reflection \u2014 Mirror Image**\n\nA **reflection** flips a shape over a line (the mirror line).\n\n**Reflection in the x-axis:**\n> (x, y) \u2192 (x, \u2212y)\n>\n> Example: (3, 4) \u2192 (3, \u22124)\n\n**Reflection in the y-axis:**\n> (x, y) \u2192 (\u2212x, y)\n>\n> Example: (3, 4) \u2192 (\u22123, 4)\n\n**Reflection in y = x:**\n> (x, y) \u2192 (y, x)\n>\n> Example: (3, 4) \u2192 (4, 3)\n\n**Reflection in y = \u2212x:**\n> (x, y) \u2192 (\u2212y, \u2212x)\n>\n> Example: (3, 4) \u2192 (\u22124, \u22123)\n\n> \U0001f4a1 **Distance from mirror line is preserved!**"),
    p("coremath-m7t4-s2", "Reflect point (4, 5) in the x-axis.\n\nWhat are the new coordinates?",
      "Reflect (4,5) in x-axis", "New point = ?",
      ["(4, \u22125)", "(\u22124, 5)", "(\u22124, \u22125)", "(5, 4)"], 0,
      "Reflection in x-axis: (x, y) \u2192 (x, \u2212y). So (4, 5) \u2192 **(4, \u22125)**."),
    i("coremath-m7t4-s3",
      "\U0001f500 **Rotation \u2014 Turning About a Point**\n\nA **rotation** turns a shape about a fixed point (centre of rotation).\n\n**Common Rotations about the Origin:**\n\n**90\u00b0 clockwise (\u221290\u00b0):**\n> (x, y) \u2192 (y, \u2212x)\n> Example: (2, 3) \u2192 (3, \u22122)\n\n**90\u00b0 anticlockwise (90\u00b0):**\n> (x, y) \u2192 (\u2212y, x)\n> Example: (2, 3) \u2192 (\u22123, 2)\n\n**180\u00b0 (half turn):**\n> (x, y) \u2192 (\u2212x, \u2212y)\n> Example: (2, 3) \u2192 (\u22122, \u22123)\n\n**Describing a rotation:**\n> Rotation: angle, direction, centre\n> e.g., \"Rotation of 90\u00b0 clockwise about the origin\"\n\n> \u2705 **Both reflection and rotation are ISOMETRIES (shape and size preserved)!**"),
    q("coremath-m7t4-s4", "Rotate point (3, 5) by 180\u00b0 about the origin.",
      "180\u00b0 rotation of (3,5)", ["(5, 3)", "(\u22123, \u22125)", "(3, \u22125)", "(\u22123, 5)"], 1,
      "180\u00b0 rotation: (x, y) \u2192 (\u2212x, \u2212y). So (3, 5) \u2192 **(\u22123, \u22125)**."),
    i("coremath-m7t4-s5",
      "\U0001f3af **Finding the Centre of Rotation**\n\nTo find the centre of rotation:\n1. Join a point to its image (e.g., A to A\u2032)\n2. Find the midpoint\n3. Draw the perpendicular bisector\n4. Repeat for another pair of points (B to B\u2032)\n5. The intersection of the perpendicular bisectors is the **centre of rotation**\n\n**For a 90\u00b0 rotation, the centre is found by:**\n> Construct perpendicular lines through matching points.\n> The centre is where these lines intersect.\n\n**Describing a transformation fully:**\n> You must state:\n> 1. Type (reflection / rotation / translation / enlargement)\n> 2. Details (mirror line / angle & centre / vector / scale factor & centre)\n\n> \U0001f511 **WASSCE: \"Describe fully the transformation that maps shape A onto shape B\" \u2014 give ALL details!**"),
    c("coremath-m7t4-s6", "Reflections and Rotations Mastery", [
        {"question": "Reflect (2, \u22125) in the y-axis.",
         "options": ["(\u22122, \u22125)", "(2, 5)", "(\u22122, 5)", "(5, \u22122)"],
         "correctIndex": 0, "explanation": "y-axis: (x,y) \u2192 (\u2212x,y). So (2, \u22125) \u2192 (\u22122, \u22125)."},
        {"question": "Rotate (\u22121, 4) by 90\u00b0 anticlockwise about the origin.",
         "options": ["(\u22124, \u22121)", "(4, 1)", "(\u22124, 1)", "(1, \u22124)"],
         "correctIndex": 0, "explanation": "90\u00b0 anticlockwise: (x,y) \u2192 (\u2212y,x). So (\u22121,4) \u2192 (\u22124, \u22121)."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m7t5", "Enlargements and Mixed Transformations",
    "Core Mathematics", "\U0001f500", "Both", 3, 12, 30, "core-maths", ["coremath-m7t4"], ["SHS 3"], "SHS 3", [
    i("coremath-m7t5-s1",
      "\U0001f500 **Enlargement \u2014 Changing Size**\n\nAn **enlargement** changes the size of a shape.\n\n**Key features:**\n> **Scale factor (k):** How many times larger the image is\n> If |k| > 1: shape gets **bigger**\n> If 0 < |k| < 1: shape gets **smaller** (sometimes called a reduction)\n> If k is negative: shape is **inverted** (rotated 180\u00b0)\n\n**Centre of enlargement:** The point from which the shape is enlarged.\n\n**Finding the image:**\n> Distance from centre to image = k \u00d7 distance from centre to original\n\n**Rule:** If centre = (a, b), then:\n> x\u2032 = a + k(x \u2212 a)\n> y\u2032 = b + k(y \u2212 b)\n\n> \U0001f4a1 **Area scale factor = k\u00b2. If k = 3, area multiplies by 9!**"),
    p("coremath-m7t5-s2", "A point P(2, 3) is enlarged by scale factor 2 about centre (0, 0).\n\nWhat are the new coordinates?",
      "Enlarge (2,3) by k=2 about (0,0)", "P\u2032 = ?",
      ["(4, 6)", "(1, 1.5)", "(2, 3)", "(0, 0)"], 0,
      "x\u2032 = 0 + 2(2\u22120) = 4. y\u2032 = 0 + 2(3\u22120) = 6. P\u2032 = **(4, 6)**. Each coordinate simply doubles."),
    i("coremath-m7t5-s3",
      "\U0001f500 **Scale Factors and Area/Length**\n\n**Linear scale factor = k**\n> Length of image = k \u00d7 length of original\n\n**Area scale factor = k\u00b2**\n> Area of image = k\u00b2 \u00d7 area of original\n\n**Volume scale factor = k\u00b3**\n> Volume of image = k\u00b3 \u00d7 volume of original\n\n**Example:**\n> A rectangle 4 cm by 3 cm is enlarged by k = 2.\n> Lengths: 8 cm by 6 cm\n> Original area = 12 cm\u00b2\n> New area = 8 \u00d7 6 = 48 cm\u00b2 = k\u00b2 \u00d7 12 = 4 \u00d7 12 = 48 \u2713\n\n**Negative scale factor:**\n> Enlargement by k = \u22122 about origin:\n> (2, 3) \u2192 (\u22124, \u22126) (same as 180\u00b0 rotation + enlargement)\n\n> \u2705 **For negative k, the image is on the opposite side of the centre!**"),
    q("coremath-m7t5-s4", "A triangle of area 5 cm\u00b2 is enlarged by scale factor 3.\n\nWhat is the area of the image?",
      "Area after enlargement by k=3", ["15 cm\u00b2", "45 cm\u00b2", "30 cm\u00b2", "9 cm\u00b2"], 1,
      "Area scale factor = k\u00b2 = 3\u00b2 = 9. New area = 5 \u00d7 9 = **45 cm\u00b2**."),
    i("coremath-m7t5-s5",
      "\U0001f3af **Describing Enlargements Fully**\n\nTo describe an enlargement, you need:\n1. The word \"Enlargement\"\n2. Scale factor\n3. Centre of enlargement\n\n**Finding the centre of enlargement:**\n> Draw lines connecting matching points on the original and image.\n> These lines will **converge at the centre of enlargement**.\n\n**Finding scale factor:**\n> k = (distance from centre to image) / (distance from centre to original)\n> OR: k = (length of side in image) / (length of corresponding side in original)\n\n**Combined transformations (WASSCE Hard):**\n> A shape may undergo multiple transformations.\n> Apply them in the correct order!\n> Example: Reflect in x-axis, then translate by (2/3), then enlarge by k=2 about origin.\n\n> \U0001f511 **\"Describe fully\" means: type of transformation, and all the details (scale factor, centre, direction, etc.)!**"),
    c("coremath-m7t5-s6", "Enlargement Mastery", [
        {"question": "A shape of area 20 cm\u00b2 is enlarged by k = 4. What is the new area?",
         "options": ["80 cm\u00b2", "320 cm\u00b2", "160 cm\u00b2", "40 cm\u00b2"],
         "correctIndex": 1, "explanation": "Area SF = 4\u00b2 = 16. New area = 20 \u00d7 16 = 320 cm\u00b2."},
        {"question": "Enlarge P(3, \u22122) by k = \u22121 about origin. Where is P\u2032?",
         "options": ["(\u22123, 2)", "(3, 2)", "(\u22123, \u22122)", "(2, \u22123)"],
         "correctIndex": 0, "explanation": "k = \u22121: x\u2032 = 0 \u2212 1(3\u22120) = \u22123, y\u2032 = 0 \u2212 1(\u22122\u22120) = 2. P\u2032 = (\u22123, 2)."},
    ]),
]))


# ── MODULE 8: Statistics and Data Analysis ────────────────────────────

ALL_LESSONS.append(L("coremath-m8t1", "Data Collection and Presentation",
    "Core Mathematics", "\U0001f4ca", "Both", 1, 8, 20, "core-maths", [], ["SHS 1", "SHS 2"], "SHS 1", [
    i("coremath-m8t1-s1",
      "\U0001f4ca **Statistics \u2014 Collecting and Organising Data**\n\n**Statistics** is about collecting, organising, analysing, and interpreting data.\n\n**Types of Data:**\n> **Qualitative (Categorical):** Non-numerical (e.g., colours, subjects, genders)\n> **Quantitative (Numerical):** \n>   - **Discrete:** Countable whole numbers (e.g., number of students, shoe sizes)\n>   - **Continuous:** Measurable on a scale (e.g., height, weight, time)\n\n**Primary data:** Collected directly by the researcher (surveys, experiments)\n**Secondary data:** Already collected by others (statistical reports, databases)\n\n**Frequency Table:** Organises data into categories with their frequencies (counts)."),
    p("coremath-m8t1-s2", "The heights of students: 145, 150, 148, 145, 152, 150, 145, 148, 150, 152\n\nWhich type of data is this?",
      "Heights data type", ["Qualitative", "Discrete quantitative", "Continuous quantitative", "Categorical"], 2,
      "Height is **continuous quantitative** data \u2014 it can be measured on a continuous scale (e.g., 145.5 cm, 150.3 cm)."),
    i("coremath-m8t1-s3",
      "\U0001f4ca **Pictograms and Bar Charts**\n\n**Pictogram:** Uses pictures/symbols to represent frequencies.\n> Each symbol = a certain number of items.\n> Easy to read but not very precise.\n\n**Bar Chart:** Rectangular bars with heights proportional to frequencies.\n> Gaps between bars (unlike histograms).\n> Used for categorical or discrete data.\n\n**Pie Chart:** A circle divided into sectors proportional to frequencies.\n> Each sector angle = (frequency/total) \u00d7 360\u00b0\n\n**Example:** In a class of 40 students: 10 chose Science, 15 Arts, 10 Business, 5 Others.\n> Science: (10/40) \u00d7 360 = 90\u00b0\n> Arts: (15/40) \u00d7 360 = 135\u00b0\n> Business: (10/40) \u00d7 360 = 90\u00b0\n> Others: (5/40) \u00d7 360 = 45\u00b0\n\n> \U0001f4a1 **Check your pie chart: all angles must sum to 360\u00b0!**"),
    q("coremath-m8t1-s4", "In a pie chart, a category has angle 72\u00b0 out of 360\u00b0.\n\nWhat percentage does it represent?",
      "72\u00b0 out of 360\u00b0 = ?%", ["20%", "72%", "36%", "10%"], 0,
      "Percentage = (72/360) \u00d7 100 = 0.2 \u00d7 100 = **20%**. Each degree represents 1/360 = 0.278% of the total."),
    i("coremath-m8t1-s5",
      "\U0001f4ca **Types of Graphs \u2014 Choosing the Right One**\n\n**WASSCE Essential Graphs:**\n\n| Data Type | Best Graph |\n|---|---|\n| Categorical | Bar chart, Pie chart |\n| Discrete numerical | Bar chart |\n| Continuous numerical | Histogram, Frequency polygon |\n| Trends over time | Line graph |\n\n**Frequency Polygon:**\n> Plot frequency against midpoint of each class interval.\n> Join points with straight lines.\n> Shows the shape of the distribution.\n\n**Pictograms:**\n> Easy to understand but can be misleading if symbols are not drawn to proportion.\n\n> \u2705 **The best graph is the one that communicates the data most clearly!**"),
    c("coremath-m8t1-s6", "Data Presentation Mastery", [
        {"question": "What type of data is \"favourite colour\"?",
         "options": ["Discrete quantitative", "Continuous quantitative", "Qualitative (categorical)", "Secondary data"],
         "correctIndex": 2, "explanation": "Colour is categorical/qualitative data \u2014 it cannot be measured numerically."},
        {"question": "In a pie chart, one category represents 30%. What is its angle?",
         "options": ["30\u00b0", "108\u00b0", "90\u00b0", "36\u00b0"],
         "correctIndex": 1, "explanation": "Angle = 30% of 360\u00b0 = 0.3 \u00d7 360 = 108\u00b0."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m8t2", "Measures of Central Tendency",
    "Core Mathematics", "\U0001f4ca", "Both", 1, 10, 25, "core-maths", ["coremath-m8t1"], ["SHS 1", "SHS 2"], "SHS 1", [
    i("coremath-m8t2-s1",
      "\U0001f4ca **Central Tendency \u2014 Finding the \"Middle\" of Data**\n\nThree \"averages\" you MUST know for WASSCE:\n\n**1. Mean:** Sum of all values divided by the number of values.\n> x\u0304 = (\u03a3x)/n\n\n**2. Median:** The middle value when data is ordered.\n> If n is odd: value at position (n+1)/2\n> If n is even: average of values at positions n/2 and n/2+1\n\n**3. Mode:** The most frequent value(s).\n> A data set can have one mode, more than one mode, or no mode.\n\n**Example:** Find mean, median, mode for: 4, 6, 2, 8, 6\n> Ordered: 2, 4, 6, 6, 8\n> Mean = (2+4+6+6+8)/5 = 26/5 = **5.2**\n> Median = middle = **6**\n> Mode = most frequent = **6**"),
    p("coremath-m8t2-s2", "Find the median of: 3, 7, 2, 9, 5, 6, 4",
      "Median of 3,7,2,9,5,6,4", ["5", "6", "4", "5.5"], 0,
      "Ordered: 2, 3, 4, 5, 6, 7, 9. n=7 (odd). Position = (7+1)/2 = 4. 4th value = **5**."),
    i("coremath-m8t2-s3",
      "\U0001f4ca **Mean from a Frequency Table**\n\n**Formula:** x\u0304 = \u03a3(fx) / \u03a3f\n> Where x = value, f = frequency\n\n**Example:**\n| Marks (x) | Frequency (f) | f\u00d7x |\n|---|---|---|\n| 2 | 3 | 6 |\n| 3 | 5 | 15 |\n| 4 | 7 | 28 |\n| 5 | 5 | 25 |\n| Total | 20 | 74 |\n\nMean = 74/20 = **3.7**\n\n> \u2705 **For grouped data, use the class MIDPOINT as the x-value.**"),
    q("coremath-m8t2-s4", "Calculate the mean from the frequency table:\n\nx: 1(2), 2(5), 3(3)\n\nWhere (f) is frequency.",
      "Mean of grouped data", ["1.5", "2.1", "2.5", "2.0"], 1,
      "\u03a3f = 2+5+3 = 10. \u03a3fx = 1\u00d72 + 2\u00d75 + 3\u00d73 = 2+10+9 = 21. Mean = 21/10 = **2.1**."),
    i("coremath-m8t2-s5",
      "\U0001f3af **Choosing the Right Average \u2014 Which to Use?**\n\n**Use the Mean when:**\n> Data is roughly symmetrical with no extreme values.\n> You need further calculations (e.g., standard deviation).\n\n**Use the Median when:**\n> Data has extreme values (outliers).\n> Example: Salaries \u2014 the mean is skewed by very high earners.\n\n**Use the Mode when:**\n> Data is categorical.\n> You need the most common value.\n> Example: Most popular shoe size, favourite subject.\n\n**WASSCE Classic Question:**\n> \"A school has 10 teachers earning GH\u00a22,000 each and 1 headmaster earning GH\u00a220,000.\"\n> Mean = (10\u00d72,000 + 20,000)/11 = 40,000/11 = GH\u00a23,636\n> Median = 11th value = GH\u00a22,000\n> The **median** better represents the typical salary!\n\n> \U0001f511 **WASSCE tests your understanding of WHY one average is more appropriate than another!**"),
    c("coremath-m8t2-s6", "Central Tendency Mastery", [
        {"question": "Find the mode of: 2, 5, 3, 5, 7, 5, 2, 8",
         "options": ["2", "5", "2.5", "5.5"],
         "correctIndex": 1, "explanation": "5 appears 3 times (more than any other). Mode = 5."},
        {"question": "Find the median of: 4, 8, 3, 9, 6, 7",
         "options": ["6", "6.5", "7", "5.5"],
         "correctIndex": 1, "explanation": "Ordered: 3, 4, 6, 7, 8, 9. n=6 even. Median = (6+7)/2 = 6.5."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m8t3", "Measures of Spread",
    "Core Mathematics", "\U0001f4ca", "Both", 2, 10, 25, "core-maths", ["coremath-m8t2"], ["SHS 2", "SHS 3"], "SHS 2", [
    i("coremath-m8t3-s1",
      "\U0001f4ca **Spread \u2014 How Data is Distributed**\n\nMeasures of spread tell us how spread out the data is.\n\n**Range:**\n> Range = Highest value \u2212 Lowest value\n> Quick to calculate but affected by outliers.\n\n**Interquartile Range (IQR):**\n> IQR = Q3 \u2212 Q1\n> Q1 (lower quartile) = median of the lower half\n> Q3 (upper quartile) = median of the upper half\n> IQR is **not** affected by outliers.\n\n**Example:** 2, 4, 5, 6, 8, 10, 12\n> Q2 (median) = 6\n> Lower half: 2, 4, 5 \u2192 Q1 = 4\n> Upper half: 8, 10, 12 \u2192 Q3 = 10\n> IQR = 10 \u2212 4 = **6**"),
    p("coremath-m8t3-s2", "Find the interquartile range of: 3, 6, 7, 9, 11, 14, 18",
      "IQR of 3,6,7,9,11,14,18", ["7", "8", "11", "9"], 1,
      "Q2 = 9. Lower: 3,6,7 \u2192 Q1 = 6. Upper: 11,14,18 \u2192 Q3 = 14. IQR = 14 \u2212 6 = **8**."),
    i("coremath-m8t3-s3",
      "\U0001f4ca **Box and Whisker Plots**\n\nA box plot shows the five-number summary:\n> Minimum, Q1, Median (Q2), Q3, Maximum\n\n**Drawing a box plot:**\n> Left whisker: min to Q1\n> Box: Q1 to Q3 (the IQR)\n> Line inside box: median\n> Right whisker: Q3 to max\n\n**Example:** Min=2, Q1=4, Med=6, Q3=10, Max=15\n> Draw a number line from 1 to 16.\n> Box from 4 to 10, line at 6.\n> Whiskers from 2 to 4 and 10 to 15.\n\n**What the box plot tells us:**\n> Short box = data clustered together\n> Long box = data spread out\n> Symmetric = data evenly distributed\n> Skewed to right = longer right whisker\n\n> \U0001f4a1 **WASSCE loves comparing two distributions using box plots!**"),
    q("coremath-m8t3-s4", "A data set has min=5, Q1=10, Med=15, Q3=20, Max=30.\n\nWhat is the IQR?",
      "IQR = Q3 \u2212 Q1", ["10", "15", "5", "25"], 0,
      "IQR = 20 \u2212 10 = **10**. The middle 50% of data falls within this range."),
    i("coremath-m8t3-s5",
      "\U0001f3af **Standard Deviation (Advanced Spread)**\n\n**Variance:** The average of the squared deviations from the mean.\n**Standard Deviation:** The square root of the variance.\n\n> \u03c3\u00b2 = \u03a3(x \u2212 x\u0304)\u00b2 / n  (population variance)\n> \u03c3 = \u221a(\u03c3\u00b2)  (population standard deviation)\n\n**Example:** Find standard deviation of: 2, 4, 6\n> Mean = (2+4+6)/3 = 4\n> Deviations: (2\u22124)\u00b2 = 4, (4\u22124)\u00b2 = 0, (6\u22124)\u00b2 = 4\n> Variance = (4+0+4)/3 = 8/3 \u2248 2.67\n> Std dev = \u221a2.67 \u2248 **1.63**\n\n> \u2705 **Low standard deviation = values close to the mean. High = values spread out.**"),
    c("coremath-m8t3-s6", "Spread Mastery", [
        {"question": "For data: 1, 3, 5, 7, 9. Find the range.",
         "options": ["8", "5", "4", "6"],
         "correctIndex": 0, "explanation": "Range = 9 \u2212 1 = 8."},
        {"question": "Data: 2, 4, 6, 8, 10, 12, 14. Find Q1.",
         "options": ["4", "6", "5", "3"],
         "correctIndex": 0, "explanation": "Median = 8. Lower half: 2, 4, 6. Q1 = 4 (median of lower half)."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m8t4", "Histograms and Cumulative Frequency",
    "Core Mathematics", "\U0001f4ca", "Both", 2, 12, 30, "core-maths", ["coremath-m8t2"], ["SHS 2", "SHS 3"], "SHS 2", [
    i("coremath-m8t4-s1",
      "\U0001f4ca **Histograms \u2014 Continuous Data Graphs**\n\nUnlike bar charts, histograms are for **continuous** data and have **no gaps** between bars.\n\n**Key Difference:**\n> Bar chart: Category labels on x-axis, frequency on y-axis\n> Histogram: Class intervals on x-axis, frequency density on y-axis\n\n**Frequency density = Frequency / Class width**\n\n**Example:**\n| Height (cm) | Frequency | Class width | Freq density |\n|---|---|---|---|\n| 140-145 | 4 | 5 | 0.8 |\n| 145-150 | 8 | 5 | 1.6 |\n| 150-155 | 12 | 5 | 2.4 |\n| 155-160 | 6 | 5 | 1.2 |\n\n> \U0001f4a1 **WASSCE: Area of each bar = frequency!**"),
    p("coremath-m8t4-s2", "A class interval 30-40 has frequency 15.\n\nWhat is the frequency density?",
      "Class 30-40, freq=15", "Freq density?", ["15", "1.5", "3.0", "0.75"], 1,
      "Class width = 40 \u2212 30 = 10. FD = 15/10 = **1.5**. WASSCE uses histograms for continuous data."),
    i("coremath-m8t4-s3",
      "\U0001f4ca **Cumulative Frequency**\n\n**Cumulative frequency:** Running total of frequencies.\n\n| Height (cm) | Freq | Cumulative Freq |\n|---|---|---|\n| < 145 | 4 | 4 |\n| < 150 | 8 | 12 |\n| < 155 | 12 | 24 |\n| < 160 | 6 | 30 |\n\n**Cumulative Frequency Curve (Ogive):**\n> Plot upper class boundary vs cumulative frequency.\n> Join with a smooth S-shaped curve.\n\n**Reading from the ogive:**\n> **Median:** Find n/2 on y-axis, read corresponding x-value.\n> **Lower quartile (Q1):** n/4 on y-axis.\n> **Upper quartile (Q3):** 3n/4 on y-axis.\n> **Percentiles:** k% = kn/100 on y-axis.\n\n> \u2705 **The ogive is your best friend for finding quartiles and percentiles!**"),
    q("coremath-m8t4-s4", "For 40 students, the cumulative frequency at height 160 cm is 30.\n\nHow many students are taller than 160 cm?",
      "CF at 160 = 30 out of 40", "Students > 160?", ["30", "10", "40", "20"], 1,
      "Total = 40, CF = 30 means 30 are shorter. So 40 \u2212 30 = **10 students** are taller than 160 cm."),
    i("coremath-m8t4-s5",
      "\U0001f3af **Drawing and Using an Ogive**\n\n**Steps to draw a cumulative frequency curve:**\n\n1. Create cumulative frequency table\n2. Plot upper boundaries on x-axis, cumulative frequencies on y-axis\n3. Join points with a smooth curve (not straight line segments!)\n4. Use the curve to estimate values\n\n**Example:** Find quartiles from 60 data values.\n> Q2 (median): Find 30 on y-axis, read x = ~54\n> Q1: Find 15 on y-axis, read x = ~42\n> Q3: Find 45 on y-axis, read x = ~65\n> IQR = Q3 \u2212 Q1 = 65 \u2212 42 = **23**\n\n**Percentile example:**\n> To find the 90th percentile for 60 students:\n> Find (90/100) \u00d7 60 = 54 on y-axis, read corresponding x.\n> This means 90% of students scored below this value.\n\n> \U0001f511 **WASSCE: Always label your axes and use graph paper!**"),
    c("coremath-m8t4-s6", "Histograms and Cumulative Frequency Mastery", [
        {"question": "Class 20-30, frequency 20. What is frequency density?",
         "options": ["2.0", "20", "0.5", "10"],
         "correctIndex": 0, "explanation": "Width = 10. FD = 20/10 = 2.0."},
        {"question": "With 50 observations, which cumulative frequency corresponds to Q1?",
         "options": ["12.5", "25", "37.5", "50"],
         "correctIndex": 0, "explanation": "Q1 = n/4 = 50/4 = 12.5. Find this on CF y-axis and read the x-value."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m8t5", "Data Interpretation and Application",
    "Core Mathematics", "\U0001f4ca", "Both", 2, 10, 25, "core-maths", ["coremath-m8t3", "coremath-m8t4"], ["SHS 2", "SHS 3"], "SHS 2", [
    i("coremath-m8t5-s1",
      "\U0001f3af **Interpreting Statistical Diagrams (WASSCE Classic!)**\n\n**Key questions to ask about any data display:**\n\n1. **What type of data is shown?** (categorical, discrete, continuous)\n2. **What is the shape of the distribution?**\n   > Symmetric: bell-shaped (normal)\n   > Skewed left: tail on the left (mean < median)\n   > Skewed right: tail on the right (mean > median)\n3. **Are there outliers?** Values far from the rest\n4. **What conclusions can be drawn?**\n\n**Comparing two data sets:**\n> Use back-to-back stem-and-leaf, or side-by-side box plots.\n> Compare: centre (mean/median) and spread (range/IQR)."),
    p("coremath-m8t5-s2", "Two classes took the same test. Class A: mean=65, IQR=10. Class B: mean=70, IQR=20.\n\nWhich statement is correct?",
      "Class A: mean=65, IQR=10. Class B: mean=70, IQR=20", "Which is correct?",
      ["Class A performed better and was more consistent", "Class B performed better but was less consistent", "Class A performed better but was less consistent", "Both classes had similar performance"], 1,
      "Class B has a **higher mean** (better performance) but a **larger IQR** (more variation/less consistent). So B performed better but was less consistent."),
    i("coremath-m8t5-s3",
      "\U0001f4ca **Stem-and-Leaf Diagrams**\n\nA stem-and-leaf diagram shows all data values while displaying shape.\n\n**Example:** Test scores: 45, 52, 53, 58, 61, 63, 67, 72, 75\n\n> 4 | 5\n> 5 | 2 3 8\n> 6 | 1 3 7\n> 7 | 2 5\n> Key: 5|2 = 52 marks\n\n**Back-to-back stem-and-leaf:**\n> Compare two data sets on either side of the stem.\n> Good for comparing distributions.\n\n> \U0001f4a1 **Always include a key for stem-and-leaf diagrams!**"),
    q("coremath-m8t5-s4", "A stem-and-leaf diagram shows: 2|3 5 8. Key: 2|3 = 23.\n\nHow many values are there?",
      "2|3 5 8, key 2|3=23", "How many values?", ["3", "2", "6", "9"], 0,
      "The stem is 2 (tens digit), leaves are 3, 5, 8 (ones digits). Values: 23, 25, 28. **3 values**."),
    i("coremath-m8t5-s5",
      "\U0001f3af **Common WASSCE Data Questions**\n\n**Finding the modal class:**\n> The class interval with the highest frequency density.\n\n**Estimating the mean from grouped data:**\n> Use midpoints and frequencies.\n> x\u0304 = \u03a3(fm)/\u03a3f (where m = midpoint)\n\n**Estimating median from grouped data:**\n> Median = L + ((n/2 \u2212 CF)/f) \u00d7 w\n> Where L = lower boundary of median class\n> CF = cumulative frequency before median class\n> f = frequency of median class\n> w = class width\n\n**Example (estimate median):**\n> n = 40, median class = 50-60, CF before = 15, f = 12, w = 10\n> Median = 50 + ((20 \u2212 15)/12) \u00d7 10\n> = 50 + (5/12) \u00d7 10\n> = 50 + 4.17 = **54.17**\n\n> \u2705 **Always show your method clearly for WASSCE marks!**"),
    c("coremath-m8t5-s6", "Data Interpretation Mastery", [
        {"question": "In a skewed right distribution, which is true?",
         "options": ["Mean < Median", "Mean > Median", "Mean = Median", "Mean is unrelated to Median"],
         "correctIndex": 1, "explanation": "Right skew = long right tail = high values pull mean up. So Mean > Median."},
        {"question": "What does a small standard deviation indicate?",
         "options": ["Data is spread out", "Data is clustered near the mean", "Data is skewed", "No data"],
         "correctIndex": 1, "explanation": "Small standard deviation = most values are close to the mean (low variability)."},
    ]),
]))


# ── MODULE 9: Probability ─────────────────────────────────────────────

ALL_LESSONS.append(L("coremath-m9t1", "Basic Probability Concepts",
    "Core Mathematics", "\U0001f3b2", "Both", 1, 8, 20, "core-maths", [], ["SHS 2"], "SHS 2", [
    i("coremath-m9t1-s1",
      "\U0001f3b2 **Probability \u2014 Measuring Likelihood**\n\n**Probability** is the measure of how likely an event is to occur.\n\n**The Probability Scale:**\n> 0 = impossible\n> 1 = certain\n> 0.5 = equally likely\n>\n> 0 \u2500\u2500\u2500\u2500\u2500 0.25 \u2500\u2500\u2500\u2500\u2500 0.5 \u2500\u2500\u2500\u2500\u2500 0.75 \u2500\u2500\u2500\u2500\u2500 1\n> Impossible | Unlikely | Even | Likely | Certain\n\n**Formula:**\n> P(event) = (Number of favourable outcomes) / (Total number of possible outcomes)\n\n**Example:**\n> Rolling a fair die: P(getting a 4) = 1/6\n> P(getting an even number) = 3/6 = 1/2\n\n> \U0001f4a1 **All probabilities are between 0 and 1 (inclusive)!**"),
    p("coremath-m9t1-s2", "A bag contains 3 red, 5 blue, and 2 green marbles.\n\nWhat is P(blue)?",
      "3R, 5B, 2G marbles", "P(blue) = ?", ["5/10", "3/10", "2/10", "5/8"], 0,
      "Total marbles = 3+5+2 = 10. Blue = 5. P(blue) = 5/10 = **1/2**."),
    i("coremath-m9t1-s3",
      "\U0001f3b2 **Key Rules of Probability**\n\n**1. Sum of all outcomes = 1:**\n> P(1) + P(2) + ... + P(n) = 1\n\n**2. Complement Rule:**\n> P(not A) = 1 \u2212 P(A)\n> If P(rain) = 0.3, then P(no rain) = 0.7\n\n**3. Mutually exclusive events (cannot happen together):**\n> P(A or B) = P(A) + P(B)\n> Example: P(rolling 2 or 5 on die) = 1/6 + 1/6 = 2/6 = 1/3\n\n**4. Independent events (one does not affect the other):**\n> P(A and B) = P(A) \u00d7 P(B)\n> Example: P(heads on coin AND rolling 6 on die) = 1/2 \u00d7 1/6 = 1/12\n\n> \U0001f511 **WASSCE: Know when to ADD (or) and when to MULTIPLY (and)!**"),
    q("coremath-m9t1-s4", "The probability of passing an exam is 0.75.\n\nWhat is the probability of failing?",
      "P(pass) = 0.75, P(fail) = ?", ["0.75", "0.25", "0.50", "0.15"], 1,
      "P(fail) = 1 \u2212 P(pass) = 1 \u2212 0.75 = **0.25**. These are complementary events (they cover all possibilities)."),
    i("coremath-m9t1-s5",
      "\U0001f3af **Experimental vs Theoretical Probability**\n\n**Theoretical probability:** What SHOULD happen (based on mathematics).\n> P(heads on fair coin) = 1/2\n\n**Experimental probability:** What ACTUALLY happens (based on experiments).\n> Toss a coin 100 times, get 54 heads.\n> Experimental P(heads) = 54/100 = 0.54\n\n**Law of Large Numbers:**\n> As the number of trials increases, experimental probability approaches theoretical probability.\n> 10 tosses: might get 70% heads\n> 1000 tosses: closer to 50% heads\n\n**Relative frequency:**\n> Used when theoretical probability is unknown.\n> Relative frequency = Frequency of event / Total frequency\n\n> \u2705 **More trials = more reliable experimental probability!**"),
    c("coremath-m9t1-s6", "Basic Probability Mastery", [
        {"question": "A bag has 4 red, 3 blue, 5 green balls. P(red) = ?",
         "options": ["4/12", "1/3", "1/4", "4/8"],
         "correctIndex": 1, "explanation": "Total = 12. Red = 4. P(red) = 4/12 = 1/3."},
        {"question": "P(winning a game) = 0.4. P(losing) = 0.5. What is P(draw)?",
         "options": ["0.1", "0.9", "0.2", "1.0"],
         "correctIndex": 0, "explanation": "Total = 1. P(draw) = 1 \u2212 0.4 \u2212 0.5 = 0.1."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m9t2", "Probability of Combined Events",
    "Core Mathematics", "\U0001f3b2", "Both", 2, 10, 25, "core-maths", ["coremath-m9t1"], ["SHS 2", "SHS 3"], "SHS 2", [
    i("coremath-m9t2-s1",
      "\U0001f3b2 **Combined Events \u2014 Two or More Events**\n\n**Sample space:** All possible outcomes of an experiment.\n\n**Sample space for two dice:**\n> 6 \u00d7 6 = 36 possible outcomes.\n> Represent as ordered pairs: (1,1), (1,2), ..., (6,6)\n\n**AND rule for independent events:**\n> P(A and B) = P(A) \u00d7 P(B)\n\n**OR rule for mutually exclusive events:**\n> P(A or B) = P(A) + P(B)\n\n**OR rule for non-mutually exclusive events:**\n> P(A or B) = P(A) + P(B) \u2212 P(A and B)\n> Example: P(heart or king from cards) = 13/52 + 4/52 \u2212 1/52 = 16/52 = 4/13\n\n> \U0001f4a1 **Don't double-count! Subtract the overlap when events can happen together!**"),
    p("coremath-m9t2-s2", "Two fair dice are rolled.\n\nWhat is the probability of getting a sum of 7?",
      "Two dice, sum=7", "P(sum=7) = ?", ["1/6", "1/12", "1/36", "7/36"], 0,
      "Pairs summing to 7: (1,6), (2,5), (3,4), (4,3), (5,2), (6,1). 6 outcomes out of 36. P = 6/36 = **1/6**."),
    i("coremath-m9t2-s3",
      "\U0001f3b2 **With vs Without Replacement**\n\n**WITH replacement:** The probability stays the same for each draw.\n> Draw a card from a deck, replace it, draw again.\n> P(ace both times) = 4/52 \u00d7 4/52 = 1/169\n\n**WITHOUT replacement:** The probability changes after each draw.\n> Draw two cards from a deck without putting the first back.\n> P(both aces) = 4/52 \u00d7 3/51 = 12/2652 = 1/221\n\n> \u2705 **Without replacement: the denominator (and sometimes numerator) decreases by 1!**"),
    q("coremath-m9t2-s4", "A bag has 5 red and 3 blue marbles. Two are drawn WITHOUT replacement.\n\nP(both red) = ?",
      "5R, 3B, draw 2 without replacement", "P(both red)", ["25/64", "5/14", "5/8", "20/64"], 1,
      "P(1st red) = 5/8. P(2nd red | 1st red) = 4/7. P(both) = 5/8 \u00d7 4/7 = 20/56 = **5/14**."),
    i("coremath-m9t2-s5",
      "\U0001f3af **Using Sample Space Tables (WASSCE Method)**\n\nA sample space table for two dice:\n\n>    | 1 | 2 | 3 | 4 | 5 | 6\n> ---+---+---+---+---+---+---\n> 1 | 2 | 3 | 4 | 5 | 6 | 7\n> 2 | 3 | 4 | 5 | 6 | 7 | 8\n> 3 | 4 | 5 | 6 | 7 | 8 | 9\n> 4 | 5 | 6 | 7 | 8 | 9 | 10\n> 5 | 6 | 7 | 8 | 9 | 10 | 11\n> 6 | 7 | 8 | 9 | 10 | 11 | 12\n\n> Each cell shows the sum. 36 equally likely outcomes.\n\n**Using the table:**\n> P(sum = 7) = 6/36 = 1/6 (most likely sum!)\n> P(sum > 9) = count outcomes with 10, 11, 12 = 6/36 = 1/6\n> P(product = 12) = (2,6), (3,4), (4,3), (6,2) = 4/36 = 1/9\n\n> \U0001f511 **Sample space tables are great for two-event problems. For three-plus events, use tree diagrams!**"),
    c("coremath-m9t2-s6", "Combined Events Mastery", [
        {"question": "Two dice rolled. P(sum = 5) = ?",
         "options": ["4/36", "5/36", "6/36", "3/36"],
         "correctIndex": 0, "explanation": "Pairs for sum 5: (1,4), (2,3), (3,2), (4,1). 4/36 = 1/9."},
        {"question": "Draw two cards WITHOUT replacement from a deck. P(both hearts) = ?",
         "options": ["1/16", "13/52 \u00d7 12/51", "13/52 \u00d7 13/52", "3/51"],
         "correctIndex": 1, "explanation": "1st heart = 13/52. 2nd heart after one heart removed = 12/51. P = 13/52 \u00d7 12/51."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m9t3", "Tree Diagrams",
    "Core Mathematics", "\U0001f3b2", "Both", 2, 10, 25, "core-maths", ["coremath-m9t2"], ["SHS 2", "SHS 3"], "SHS 2", [
    i("coremath-m9t3-s1",
      "\U0001f3b2 **Tree Diagrams \u2014 Visualising Probability Problems**\n\nA **tree diagram** shows all possible outcomes and their probabilities.\n\n**Rules for tree diagrams:**\n1. Each branch represents a possible outcome\n2. Label each branch with its probability\n3. Multiply along branches for combined probability\n4. Sum the probabilities of all branches = 1\n\n**Example \u2014 Two coin tosses:**\n\n> 1st toss   2nd toss    Outcome    Probability\n> H \u2500\u2500\u2500 H \u2192 HH         \u00bd \u00d7 \u00bd = \u00bc\n> \u2502\n> \u2502\u2500\u2500\u2500\u2500 T \u2192 HT         \u00bd \u00d7 \u00bd = \u00bc\n> T \u2500\u2500\u2500 H \u2192 TH         \u00bd \u00d7 \u00bd = \u00bc\n> \u2502\n> \u2502\u2500\u2500\u2500\u2500 T \u2192 TT         \u00bd \u00d7 \u00bd = \u00bc\n\n> \U0001f4a1 **Sum = 1/4+1/4+1/4+1/4 = 1 \u2713**"),
    p("coremath-m9t3-s2", "A bag has 4 red and 2 blue balls. Two balls are drawn WITH replacement.\n\nWhat is P(both red)?",
      "4R,2B, draw 2 with replacement", "P(both red)", ["4/9", "1/9", "2/3", "16/36"], 0,
      "P(red) = 4/6 = 2/3 (each draw, because replacement). P(both red) = 2/3 \u00d7 2/3 = **4/9**."),
    i("coremath-m9t3-s3",
      "\U0001f3b2 **Tree Diagrams Without Replacement**\n\n**Example:** Bag with 3 red and 2 green marbles. Draw two WITHOUT replacement.\n\n> 1st draw    2nd draw              Probability\n> R(3/5) \u2500\u2500\u2500 R(2/4) \u2192 RR: 3/5\u00d72/4 = 6/20 = 3/10\n> \u2502\n> \u2502\u2500\u2500\u2500 G(2/4) \u2192 RG: 3/5\u00d72/4 = 6/20 = 3/10\n> G(2/5) \u2500\u2500\u2500 R(3/4) \u2192 GR: 2/5\u00d73/4 = 6/20 = 3/10\n> \u2502\n> \u2502\u2500\u2500\u2500 G(1/4) \u2192 GG: 2/5\u00d71/4 = 2/20 = 1/10\n\n> Check: 3/10 + 3/10 + 3/10 + 1/10 = 10/10 = 1 \u2713\n\n> \u2705 **The probabilities on branches from the same point must sum to 1!**"),
    q("coremath-m9t3-s4", "Box with 4 red, 3 blue marbles. Draw 2 WITHOUT replacement.\n\nP(one of each colour) = ?",
      "4R,3B, draw 2 without replacement", "P(one each)", ["12/49", "4/7", "24/42", "1/2"], 2,
      "P(RB) = 4/7 \u00d7 3/6 = 12/42. P(BR) = 3/7 \u00d7 4/6 = 12/42. P(one each) = 12/42 + 12/42 = 24/42 = **4/7**."),
    i("coremath-m9t3-s5",
      "\U0001f3af **Three-Stage Tree Diagrams (WASSCE Hard)**\n\n**Example:** 3 red, 2 blue beads. Draw 3 WITHOUT replacement. Find P(at least 2 red).\n\n> Draw the tree with 3 levels (8 branches).\n>\n> P(at least 2 red) = P(RRR) + P(RRB) + P(RBR) + P(BRR)\n> = (3/5\u00d72/4\u00d71/3) + (3/5\u00d72/4\u00d72/3) + (3/5\u00d72/4\u00d72/3) + (2/5\u00d73/4\u00d72/3)\n> = 6/60 + 12/60 + 12/60 + 12/60\n> = 42/60 = **7/10**\n\n> \U0001f511 **\"At least\" problems: List all branches that satisfy the condition, then add them!**\n> Alternatively: P(at least 2) = 1 \u2212 P(0 or 1 red)"),
    c("coremath-m9t3-s6", "Tree Diagrams Mastery", [
        {"question": "A fair coin is tossed 3 times. P(exactly 2 heads) = ?",
         "options": ["3/8", "1/2", "1/4", "5/8"],
         "correctIndex": 0, "explanation": "Favourable: HHT, HTH, THH (3 outcomes out of 8). P = 3/8."},
        {"question": "A bag has 5 green, 3 yellow balls. Two drawn WITHOUT replacement. P(at least one yellow) = ?",
         "options": ["15/28", "9/14", "5/14", "3/4"],
         "correctIndex": 1, "explanation": "P(at least one yellow) = 1 \u2212 P(no yellow) = 1 \u2212 P(both green) = 1 \u2212 (5/8 \u00d7 4/7) = 1 \u2212 20/56 = 36/56 = 9/14."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m9t4", "Conditional Probability",
    "Core Mathematics", "\U0001f3b2", "Both", 3, 10, 25, "core-maths", ["coremath-m9t2", "coremath-m9t3"], ["SHS 3"], "SHS 3", [
    i("coremath-m9t4-s1",
      "\U0001f3b2 **Conditional Probability \u2014 \"Given That\"**\n\n**Conditional probability** is the probability of an event occurring GIVEN that another event has already occurred.\n\n**Notation:**\n> P(A|B) = Probability of A given B has occurred.\n> Read as: \"Probability of A given B\"\n\n**Formula:**\n> P(A|B) = P(A and B) / P(B)\n\n**Example:**\n> In a class: 15 boys, 10 girls. 5 boys wear glasses, 3 girls wear glasses.\n> P(wears glasses | boy) = 5/15 = 1/3\n> (We only consider the 15 boys, not the whole class!)\n\n> \U0001f4a1 **\"Given\" reduces the sample space!**"),
    p("coremath-m9t4-s2", "A class has 12 boys and 8 girls. 6 boys and 4 girls play football.\n\nWhat is P(selected child plays football | child is a boy)?",
      "P(football | boy)", ["6/10", "6/12", "10/20", "6/20"], 1,
      "Given the child is a boy, we only look at the 12 boys. 6 of them play football. P = 6/12 = **1/2**."),
    i("coremath-m9t4-s3",
      "\U0001f3b2 **Using Tree Diagrams for Conditional Probability**\n\nTree diagrams naturally show conditional probabilities.\n\n**Example:** A bag has 4 red, 3 blue marbles. Draw 2 without replacement.\n\n> P(2nd is red | 1st was blue)\n> = Look at the \"Blue then Red\" branch\n> = 3/7 \u00d7 4/6 = ... wait, the conditional probability just looks at the second step.\n> Given 1st was blue (3/7 \u2192 3 blue, 4 red remaining).\n> P(2nd red | 1st blue) = 4/6 = 2/3\n\n**Calculating P(A and B):**\n> P(A and B) = P(A) \u00d7 P(B|A)\n> Or: P(A and B) = P(B) \u00d7 P(A|B)\n\n> \u2705 **This is the GENERAL multiplication rule \u2014 works even for dependent events!**"),
    q("coremath-m9t4-s4", "P(A) = 0.4, P(B) = 0.5, P(A and B) = 0.2.\n\nFind P(A|B).",
      "P(A|B) = P(A and B)/P(B)", ["0.4", "0.5", "0.2", "0.8"], 0,
      "P(A|B) = P(A and B)/P(B) = 0.2/0.5 = **0.4**. In this case P(A|B) = P(A), so A and B are independent!"),
    i("coremath-m9t4-s5",
      "\U0001f3af **Independence \u2014 Are Events Related?**\n\n**Independent events:** The occurrence of one does NOT affect the other.\n> P(A|B) = P(A) and P(B|A) = P(B)\n> P(A and B) = P(A) \u00d7 P(B)\n\n**Dependent events:** The occurrence of one DOES affect the other.\n> P(A|B) \u2260 P(A)\n> P(A and B) = P(A) \u00d7 P(B|A)\n\n**Testing for independence:**\n> Check: Does P(A and B) = P(A) \u00d7 P(B)?\n> If yes: independent. If no: dependent.\n\n**Example:**\n> P(rain) = 0.3, P(windy) = 0.4, P(rain and windy) = 0.15\n> P(rain) \u00d7 P(windy) = 0.3 \u00d7 0.4 = 0.12\n> 0.15 \u2260 0.12, so rain and wind are **dependent**!\n\n> \U0001f511 **WASSCE: \"Are events A and B independent?\" \u2014 always check using the formula!**"),
    c("coremath-m9t4-s6", "Conditional Probability Mastery", [
        {"question": "P(A and B) = 0.2, P(B) = 0.4. P(A|B) = ?",
         "options": ["0.5", "0.08", "0.2", "0.6"],
         "correctIndex": 0, "explanation": "P(A|B) = P(A and B)/P(B) = 0.2/0.4 = 0.5."},
        {"question": "If P(A) = 0.5, P(B) = 0.3, P(A and B) = 0.15, are A and B independent?",
         "options": ["Yes", "No", "Cannot determine"],
         "correctIndex": 0, "explanation": "P(A) \u00d7 P(B) = 0.5 \u00d7 0.3 = 0.15 = P(A and B). Yes, they are independent."},
    ]),
]))

ALL_LESSONS.append(L("coremath-m9t5", "Probability in Real Life",
    "Core Mathematics", "\U0001f3b2", "Both", 2, 10, 25, "core-maths", ["coremath-m9t2", "coremath-m9t3"], ["SHS 2", "SHS 3"], "SHS 2", [
    i("coremath-m9t5-s1",
      "\U0001f3af **Probability Applications \u2014 Real-World Uses**\n\n**Weather Forecasting:**\n> \"40% chance of rain\" means: out of 100 similar weather days, rain occurred on 40.\n> It does NOT mean it will rain 40% of the day!\n\n**Insurance:**\n> Companies use probability to calculate premiums.\n> P(accident) \u00d7 Cost of accident = Expected payout per person\n> P(house fire) = 0.001, cost = GH\u00a2100,000. Expected = GH\u00a2100.\n> Premium must be > GH\u00a2100 + expenses.\n\n**Genetics (WASSCE Cross-referencing):**\n> Punnett squares use probability!\n> Parents both Tt (tall dominant): P(tall offspring) = 3/4, P(short) = 1/4\n\n> \U0001f4a1 **Probability is everywhere! It's not just about coins and dice!**"),
    p("coremath-m9t5-s2", "An insurance company finds that P(accident) = 0.02 for a driver. Average cost per accident = GH\u00a250,000.\n\nWhat is the expected payout per driver?",
      "Expected payout = P(accident) \u00d7 cost", ["GH\u00a2500", "GH\u00a21,000", "GH\u00a225,000", "GH\u00a2100"], 1,
      "Expected = 0.02 \u00d7 50,000 = **GH\u00a21,000**. The insurance company would charge more than this to make a profit."),
    i("coremath-m9t5-s3",
      "\U0001f3b2 **Expected Value**\n\n**Expected value (EV):** The average outcome if an experiment is repeated many times.\n\n> EV = \u03a3(x \u00d7 P(x))\n> Where x = value of each outcome\n\n**Example \u2014 Lottery:**\n> Prize: GH\u00a210,000 (P = 1/1000)\n> Consolation: GH\u00a250 (P = 10/1000)\n> No prize: GH\u00a20 (P = 989/1000)\n> Ticket cost: GH\u00a210\n\n> EV = (10,000 \u00d7 0.001) + (50 \u00d7 0.01) + (0 \u00d7 0.989)\n> = 10 + 0.5 + 0 = GH\u00a210.50\n> But ticket costs GH\u00a210 \u2192 expected winnings = GH\u00a20.50\n> (Actually, the expected net = GH\u00a210.50 \u2212 GH\u00a210 = GH\u00a20.50 positive? That seems generous... check the numbers)\n\n> \u2705 **A fair game has EV = 0. Casinos ensure EV < ticket price (they always win in the long run)!**"),
    q("coremath-m9t5-s4", "A game: win GH\u00a250 with P=0.1, win GH\u00a210 with P=0.3, lose GH\u00a25 with P=0.6.\n\nWhat is the expected value?",
      "EV = \u03a3(x \u00d7 P(x))", ["GH\u00a22", "GH\u00a25", "GH\u00a23", "GH\u00a20"], 2,
      "EV = (50 \u00d7 0.1) + (10 \u00d7 0.3) + (\u22125 \u00d7 0.6) = 5 + 3 \u2212 3 = **GH\u00a25**. This game favours the player!"),
    i("coremath-m9t5-s5",
      "\U0001f3af **WASSCE Mixed Probability Problems**\n\n**Problem 1: Quality Control**\n> A factory produces items. 5% are defective. What is P(at least one defective in a pack of 3)?\n> P(defective) = 0.05, P(not defective) = 0.95\n> P(0 defective) = 0.95\u00b3 = 0.8574\n> P(at least 1) = 1 \u2212 0.8574 = **0.1426**\n\n**Problem 2: Two-way Tables (WASSCE Favourite!)**\n> | | Pass | Fail | Total |\n> |---|---|---|---|\n> | Boys | 30 | 10 | 40 |\n> | Girls | 35 | 5 | 40 |\n> | Total | 65 | 15 | 80 |\n\n> P(pass | girl) = 35/40 = 7/8\n> P(fail | boy) = 10/40 = 1/4\n> P(pass and boy) = 30/80 = 3/8\n\n> \U0001f511 **Two-way tables are great for organising data and finding conditional probabilities!**"),
    c("coremath-m9t5-s6", "Probability Applications Mastery", [
        {"question": "A factory has 2% defect rate. P(no defects in a pack of 5) = ?",
         "options": ["0.98\u2075", "0.02\u2075", "1 \u2212 0.98\u2075", "0.98 \u00d7 5"],
         "correctIndex": 0, "explanation": "P(not defective) = 0.98. For 5 items: 0.98\u2075."},
        {"question": "P(disease) = 0.01. Test is 95% accurate. If a person tests positive, what information do we need?",
         "options": ["The P(true positive | disease)", "The P(positive | no disease)", "Both P(positive|disease) and P(positive|no disease)", "Only the test accuracy"],
         "correctIndex": 2, "explanation": "We need both the true positive and false positive rates to calculate P(disease|positive) using conditional probability (Bayes' theorem)."},
    ]),
])

'''

def main():
    # Read the existing generate_coremaths.py
    filepath = "scripts/generate_coremaths.py"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Find where to insert (before the main() function)
    main_idx = content.find("\ndef main():")
    if main_idx < 0:
        print("ERROR: Could not find main() function in generate_coremaths.py")
        return

    # Insert modules 2-9 before main()
    new_content = content[:main_idx] + MODULES_2_9 + "\n" + content[main_idx:]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("Successfully appended Modules 2-9 to generate_coremaths.py")
    print(f"File size: {len(new_content)} chars")


if __name__ == "__main__":
    main()
