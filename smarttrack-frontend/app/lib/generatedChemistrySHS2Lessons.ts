/**
 * generatedChemistrySHS2Lessons.ts
 * Auto-generated Chemistry SHS 2 lessons from Ministry of Education curriculum materials.
 * Source: LM-Chemistry Year 2.pdf (Ministry of Education, Ghana, 2025)
 * Contains 8 sections with 16 lessons total.
 */

import type { Lesson } from './learningContent';

export const CHEMISTRY_SHS2_LESSONS: Lesson[] = [

  // ═══ MODULE 1: ENERGY CHANGES ═══
  {
    id: "chem-2-s1t1",
    title: "Enthalpy Changes and Calorimetry",
    subject: "Chemistry",
    subjectIcon: "⚗️",
    programme: "Both",
    unitId: "chemistry",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: [],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "chem-2-s1t1-intro",
        type: "info",
        content: "**Enthalpy Changes and Calorimetry**\n\nEnergy changes accompany all chemical reactions. Thermochemistry is the study of heat energy changes in chemical reactions. Understanding enthalpy changes allows us to predict whether reactions will occur spontaneously and how much energy is involved.",
      },
      {
        id: "chem-2-s1t1-content-1",
        type: "info",
        content: "**Systems and Surroundings**\n\nA **system** is the part of the universe we are studying (e.g., the reactants and products in a chemical reaction). The **surroundings** are everything else.\n\n**Types of Systems:**\n- **Open system:** Both matter and energy can be exchanged with surroundings.\n- **Closed system:** Only energy can be exchanged.\n- **Isolated system:** Neither matter nor energy can be exchanged.\n\n**Enthalpy (H):** The heat content of a system at constant pressure.\n\n**Enthalpy Change (ΔH):** The heat energy absorbed or released during a reaction at constant pressure.\nΔH = H(products) − H(reactants)\n\n**Exothermic Reactions:**\n- Release heat to the surroundings.\n- ΔH is negative (ΔH < 0).\n- The surroundings feel warmer.\n- Examples: Combustion, neutralisation, respiration.\n\n**Endothermic Reactions:**\n- Absorb heat from the surroundings.\n- ΔH is positive (ΔH > 0).\n- The surroundings feel cooler.\n- Examples: Photosynthesis, dissolving ammonium nitrate, thermal decomposition.",
      },
      {
        id: "chem-2-s1t1-content-2",
        type: "info",
        content: "**Standard Enthalpy Changes**\n\n**Standard Conditions:**\n- Pressure: 1 atm (101.3 kPa)\n- Temperature: 298 K (25°C)\n- Concentration: 1.0 mol/dm³ for solutions\n- All substances in their standard states\n\n**Types of Standard Enthalpy Changes:**\n\n1. **Standard Enthalpy Change of Reaction (ΔH°ᵣ):**\n   The enthalpy change when molar quantities of reactants react completely under standard conditions.\n\n2. **Standard Enthalpy Change of Formation (ΔH°f):**\n   The enthalpy change when ONE mole of a compound is formed from its elements in their standard states.\n   - Elements in their standard states have ΔH°f = 0.\n   - Example: C(s) + O₂(g) → CO₂(g), ΔH°f = −393.5 kJ/mol\n\n3. **Standard Enthalpy Change of Combustion (ΔH°c):**\n   The enthalpy change when ONE mole of a substance is completely burned in excess oxygen.\n   - Example: CH₄(g) + 2O₂(g) → CO₂(g) + 2H₂O(l), ΔH°c = −890 kJ/mol\n\n4. **Standard Enthalpy Change of Neutralisation (ΔH°n):**\n   The enthalpy change when an acid and a base react to produce ONE mole of water.\n   - For strong acids and strong bases: ΔH°n ≈ −57 kJ/mol\n\n5. **Standard Enthalpy of Solution (ΔH°ₛₒₗₙ):**\n   The enthalpy change when one mole of a substance dissolves in excess solvent.",
      },
      {
        id: "chem-2-s1t1-content-3",
        type: "info",
        content: "**Calorimetry — Measuring Enthalpy Changes**\n\nCalorimetry is the experimental technique for measuring heat energy changes.\n\n**Key Formula:**\nQ = mcΔT\n\nWhere:\n- Q = heat energy transferred (J or kJ)\n- m = mass of substance being heated (g)\n- c = specific heat capacity (J/g°C or J/gK)\n  - Water: c = 4.18 J/g°C\n- ΔT = change in temperature (°C or K)\n\n**Experimental Determination of Enthalpy of Combustion:**\n1. Measure a known volume of water into a calorimeter (e.g., a copper can).\n2. Record the initial temperature of the water.\n3. Burn a known mass of fuel (e.g., an alcohol) beneath the calorimeter.\n4. Record the final temperature of the water.\n5. Calculate Q = mcΔT.\n6. Calculate the number of moles of fuel burned.\n7. ΔH = −Q/n (negative because heat is released).\n\n**Sources of Error:**\n- Heat loss to the surroundings (most significant).\n- Incomplete combustion.\n- Heat absorbed by the calorimeter itself.\n- Experimental ΔH values are often lower than theoretical values due to heat loss.",
      },
      {
        id: "chem-2-s1t1-practice",
        type: "question",
        content: "Test your understanding of enthalpy changes.",
        exercise: {
          question: "In an exothermic reaction, the enthalpy change ΔH is:",
          options: [
            "Positive (ΔH > 0)",
            "Negative (ΔH < 0)",
            "Zero (ΔH = 0)",
            "Cannot be determined"
          ],
          correctIndex: 1,
          explanation: "In exothermic reactions, heat is released to the surroundings, so the products have less enthalpy than the reactants. Therefore ΔH = H(products) − H(reactants) is negative."
        }
      },
    ],
  },
  {
    id: "chem-2-s1t2",
    title: "Hess's Law and Bond Energies",
    subject: "Chemistry",
    subjectIcon: "⚗️",
    programme: "Both",
    unitId: "chemistry",
    difficulty: 4,
    estimatedMinutes: 30,
    xpReward: 60,
    prerequisites: ["chem-2-s1t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "chem-2-s1t2-intro",
        type: "info",
        content: "**Hess's Law and Bond Energies**\n\nHess's Law is a powerful principle that allows us to calculate enthalpy changes for reactions that are difficult or impossible to measure directly. Bond energy calculations provide another method for estimating enthalpy changes.",
      },
      {
        id: "chem-2-s1t2-content-1",
        type: "info",
        content: "**Hess's Law**\n\n**Statement:** The total enthalpy change for a chemical reaction is the same, regardless of the route by which the reaction occurs, provided the initial and final conditions are the same.\n\nIn other words, enthalpy change depends only on the initial and final states, not on the reaction pathway.\n\n**Mathematical Expression:**\nIf a reaction A → B occurs via intermediate steps A → C → D → B, then:\nΔH(A→B) = ΔH(A→C) + ΔH(C→D) + ΔH(D→B)\n\n**Energy Cycle Diagrams:**\nHess's Law can be represented using energy cycles. Known enthalpy changes are used to find unknown ones by following the arrows.\n\n**Example — Calculating ΔH of Formation:**\nGiven:\nC(s) + O₂(g) → CO₂(g), ΔH = −393.5 kJ/mol\n2H₂(g) + O₂(g) → 2H₂O(l), ΔH = −571.6 kJ/mol\nCH₄(g) + 2O₂(g) → CO₂(g) + 2H₂O(l), ΔH = −890.3 kJ/mol\n\nFind ΔH°f for CH₄(g).\n\nUsing the formation reaction: C(s) + 2H₂(g) → CH₄(g)\n\nFrom the combustion data:\nΔH°f(CH₄) = ΔH°c(C) + 2ΔH°c(H₂) − ΔH°c(CH₄)\n= (−393.5) + (−571.6) − (−890.3)\n= −393.5 − 571.6 + 890.3\n= −74.8 kJ/mol",
      },
      {
        id: "chem-2-s1t2-content-2",
        type: "info",
        content: "**Born-Haber Cycles**\n\nA Born-Haber cycle is a specific application of Hess's Law used to calculate lattice energy for ionic compounds. Lattice energy is the enthalpy change when one mole of an ionic solid is formed from its gaseous ions.\n\n**The Born-Haber Cycle for NaCl:**\n1. **Atomisation of Na(s):** Na(s) → Na(g), ΔH = +108 kJ/mol\n2. **Atomisation of Cl₂(g):** ½Cl₂(g) → Cl(g), ΔH = +121 kJ/mol\n3. **Ionisation of Na(g):** Na(g) → Na⁺(g) + e⁻, ΔH = +496 kJ/mol\n4. **Electron affinity of Cl(g):** Cl(g) + e⁻ → Cl⁻(g), ΔH = −349 kJ/mol\n5. **Lattice energy:** Na⁺(g) + Cl⁻(g) → NaCl(s), ΔH = ?\n6. **Formation:** Na(s) + ½Cl₂(g) → NaCl(s), ΔH°f = −411 kJ/mol\n\nUsing Hess's Law:\nΔH°f = ΔH_atom(Na) + ΔH_atom(Cl) + IE(Na) + EA(Cl) + U\n\n−411 = 108 + 121 + 496 + (−349) + U\n−411 = 376 + U\nU = −787 kJ/mol\n\nThe large negative lattice energy explains the stability of ionic compounds.",
      },
      {
        id: "chem-2-s1t2-content-3",
        type: "info",
        content: "**Bond Enthalpies**\n\nBond enthalpy (bond energy) is the energy required to break one mole of a specific covalent bond in the gaseous state.\n\n**Key Points:**\n- **Breaking bonds** requires energy (endothermic, ΔH > 0).\n- **Forming bonds** releases energy (exothermic, ΔH < 0).\n- Average bond enthalpies are used because bond strengths vary slightly between compounds.\n\n**Calculating ΔH Using Bond Enthalpies:**\nΔH = Σ(Bond enthalpies of bonds broken) − Σ(Bond enthalpies of bonds formed)\n\n**Example:** Calculate the enthalpy of combustion of methane using bond enthalpies.\n\nCH₄(g) + 2O₂(g) → CO₂(g) + 2H₂O(g)\n\n**Bonds broken:**\n4 × C−H = 4 × 412 = 1648 kJ\n2 × O=O = 2 × 496 = 992 kJ\nTotal = 2640 kJ\n\n**Bonds formed:**\n2 × C=O = 2 × 743 = 1486 kJ\n4 × O−H = 4 × 463 = 1852 kJ\nTotal = 3338 kJ\n\nΔH = 2640 − 3338 = −698 kJ/mol\n\nThe actual value differs slightly from the experimental value because average bond enthalpies are approximations.",
      },
      {
        id: "chem-2-s1t2-practice",
        type: "question",
        content: "Test your understanding of Hess's Law.",
        exercise: {
          question: "According to Hess's Law, the enthalpy change for a reaction:",
          options: [
            "Depends on the number of intermediate steps",
            "Is the same regardless of the reaction pathway",
            "Depends on the temperature at which the reaction is carried out",
            "Is always negative"
          ],
          correctIndex: 1,
          explanation: "Hess's Law states that enthalpy change depends only on the initial and final states, not on the reaction pathway. This is because enthalpy is a state function."
        }
      },
    ],
  },

  // ═══ MODULE 2: CHEMICAL KINETICS ═══
  {
    id: "chem-2-s2t1",
    title: "Reaction Rates and Collision Theory",
    subject: "Chemistry",
    subjectIcon: "⚗️",
    programme: "Both",
    unitId: "chemistry",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["chem-2-s1t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "chem-2-s2t1-intro",
        type: "info",
        content: "**Reaction Rates and Collision Theory**\n\nChemical kinetics is the study of reaction rates — how fast chemical reactions occur. Understanding reaction rates is crucial in industry (optimising production), medicine (drug metabolism), and environmental science (pollutant degradation).",
      },
      {
        id: "chem-2-s2t1-content-1",
        type: "info",
        content: "**Measuring Reaction Rates**\n\n**Reaction rate** is the change in concentration of a reactant or product per unit time.\n\nRate = Δ[Reactant]/Δt or Rate = Δ[Product]/Δt\n\n**Units:** mol/dm³/s or mol dm⁻³ s⁻¹\n\n**Types of Rates:**\n1. **Initial Rate:** The rate at the very start of the reaction (t = 0). Determined from the slope of the tangent at t = 0 on a concentration-time graph.\n\n2. **Average Rate:** The rate over a specific time interval.\nAverage rate = (C₂ − C₁)/(t₂ − t₁)\n\n3. **Instantaneous Rate:** The rate at a particular moment. Determined from the slope of the tangent at that point on a concentration-time graph.\n\n**Methods for Measuring Rates:**\n- Monitoring gas volume (e.g., CO₂ production from acid-carbonate reactions).\n- Measuring mass loss (if a gas escapes).\n- Monitoring colour change (using colorimetry or spectrophotometry).\n- Measuring conductivity change (for reactions involving ions).\n- Measuring pH change (for acid-base reactions).",
      },
      {
        id: "chem-2-s2t1-content-2",
        type: "info",
        content: "**Collision Theory**\n\nFor a chemical reaction to occur, particles must:\n1. **Collide** with each other.\n2. Have the **correct orientation**.\n3. Possess **sufficient energy** (at least equal to the activation energy).\n\n**Activation Energy (Ea):** The minimum energy required for a collision to result in a reaction.\n\n**Effective Collision:** A collision that meets all three requirements and results in product formation.\n\n**The Maxwell-Boltzmann Distribution:**\n- Shows the distribution of kinetic energies among particles at a given temperature.\n- The area under the curve represents the total number of particles.\n- The area to the right of Ea represents the number of particles with energy ≥ Ea.\n- At higher temperatures, the curve shifts to the right (more particles have high energy), and a larger fraction of particles exceed Ea.\n\n**The Boltzmann Factor:**\nThe fraction of particles with energy ≥ Ea is given by:\nf = e⁻ᴱᵃ/ᴿᵀ\n\nWhere:\n- Ea = activation energy (J/mol)\n- R = gas constant (8.314 J/mol·K)\n- T = temperature (K)",
      },
      {
        id: "chem-2-s2t1-content-3",
        type: "info",
        content: "**Factors Affecting Reaction Rates**\n\n**1. Temperature:**\n- Increasing temperature increases the average kinetic energy of particles.\n- More collisions exceed the activation energy.\n- A 10°C rise typically doubles or triples the reaction rate.\n\n**2. Concentration:**\n- Higher concentration means more particles per unit volume.\n- Collision frequency increases, leading to a higher reaction rate.\n\n**3. Surface Area:**\n- Smaller particle size (powder vs. lumps) increases surface area.\n- More particles are exposed for collision.\n- Example: Zinc powder reacts with acid much faster than zinc granules.\n\n**4. Catalysts:**\n- Provide an alternative reaction pathway with a lower activation energy.\n- More particles have energy ≥ the lower Ea.\n- Catalysts are not consumed in the reaction.\n- Example: Enzymes in biological systems, platinum in catalytic converters.\n\n**5. Pressure (for gases):**\n- Increasing pressure brings gas particles closer together.\n- Collision frequency increases, increasing the reaction rate.",
      },
      {
        id: "chem-2-s2t1-practice",
        type: "question",
        content: "Test your understanding of collision theory.",
        exercise: {
          question: "What three requirements must be met for a collision to result in a chemical reaction?",
          options: [
            "High temperature, high pressure, and a catalyst",
            "Collision, correct orientation, and sufficient energy (≥ activation energy)",
            "Collision, low temperature, and high concentration",
            "Correct orientation, stirring, and high pressure"
          ],
          correctIndex: 1,
          explanation: "According to collision theory, particles must collide, have the correct orientation when they collide, and possess energy equal to or greater than the activation energy for a reaction to occur."
        }
      },
    ],
  },
  {
    id: "chem-2-s2t2",
    title: "Rate Equations and Reaction Order",
    subject: "Chemistry",
    subjectIcon: "⚗️",
    programme: "Both",
    unitId: "chemistry",
    difficulty: 4,
    estimatedMinutes: 30,
    xpReward: 60,
    prerequisites: ["chem-2-s2t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "chem-2-s2t2-intro",
        type: "info",
        content: "**Rate Equations and Reaction Order**\n\nRate equations express the relationship between reaction rate and the concentrations of reactants. Determining the rate equation for a reaction helps us understand its mechanism and predict how changing conditions affect the rate.",
      },
      {
        id: "chem-2-s2t2-content-1",
        type: "info",
        content: "**The Rate Equation**\n\nFor a general reaction: aA + bB → products\n\nThe rate equation is:\nRate = k[A]ᵐ[B]ⁿ\n\nWhere:\n- k = rate constant (varies with temperature)\n- [A], [B] = concentrations of reactants\n- m = order of reaction with respect to A\n- n = order of reaction with respect to B\n- (m + n) = overall order of reaction\n\n**Orders of Reaction:**\n\n**Zero Order (m = 0):**\n- Rate is independent of concentration.\n- Rate = k\n- [A] vs. time graph: straight line with slope = −k.\n\n**First Order (m = 1):**\n- Rate is directly proportional to concentration.\n- Rate = k[A]\n- ln[A] vs. time graph: straight line with slope = −k.\n- Half-life (t₁/₂) is constant: t₁/₂ = ln(2)/k\n\n**Second Order (m = 2):**\n- Rate is proportional to [A]².\n- Rate = k[A]²\n- 1/[A] vs. time graph: straight line with slope = k.",
      },
      {
        id: "chem-2-s2t2-content-2",
        type: "info",
        content: "**Determining Reaction Order Experimentally**\n\nThe order of reaction must be determined experimentally — it cannot be deduced from the balanced chemical equation.\n\n**Method 1: Initial Rates Method**\n1. Carry out several experiments, varying the concentration of one reactant at a time while keeping others constant.\n2. Measure the initial rate for each experiment.\n3. Compare how the rate changes as concentration changes.\n\n**Example:**\n| Experiment | [A] (mol/dm³) | Initial Rate (mol/dm³/s) |\n|------------|---------------|--------------------------|\n| 1 | 0.1 | 0.02 |\n| 2 | 0.2 | 0.08 |\n| 3 | 0.3 | 0.18 |\n\nComparing expt 1 and 2: [A] doubles, rate quadruples (×4) → second order with respect to A.\nComparing expt 2 and 3: [A] × 1.5, rate × 2.25 = 1.5² → confirms second order.\n\n**Method 2: Concentration-Time Graphs**\nPlot [A] vs. time. If the half-life is constant, the reaction is first order.\n\n**The Rate-Determining Step (RDS):**\nIn a multi-step reaction, the slowest step determines the overall reaction rate. The rate equation is determined by the rate-determining step.",
      },
      {
        id: "chem-2-s2t2-content-3",
        type: "info",
        content: "**The Rate Constant (k) and Temperature**\n\nThe rate constant k varies with temperature according to the **Arrhenius Equation**:\n\nk = Ae⁻ᴱᵃ/ᴿᵀ\n\nWhere:\n- k = rate constant\n- A = pre-exponential factor (frequency factor)\n- Ea = activation energy (J/mol)\n- R = gas constant (8.314 J/mol·K)\n- T = temperature (K)\n\n**In logarithmic form:**\nln(k) = ln(A) − Ea/(RT)\n\nA plot of ln(k) vs. 1/T gives a straight line:\n- Slope = −Ea/R\n- y-intercept = ln(A)\n\n**Catalysts and Activation Energy:**\n- Catalysts lower the activation energy, increasing the rate constant k.\n- A lower Ea means more particles have energy ≥ Ea.\n- The Arrhenius equation shows that a lower Ea results in a larger k.\n\n**Worked Example:**\nThe activation energy for a reaction is 50 kJ/mol at 298 K. Calculate the fraction of molecules with sufficient energy to react.\n\nf = e⁻ᴱᵃ/ᴿᵀ = e⁻⁵⁰⁰⁰⁰/⁸·³¹⁴×²⁹⁸ = e⁻²⁰·¹⁸ = 1.73 × 10⁻⁹\n\nOnly about 1.7 × 10⁻⁷% of collisions have sufficient energy!",
      },
      {
        id: "chem-2-s2t2-practice",
        type: "question",
        content: "Test your understanding of rate equations.",
        exercise: {
          question: "If doubling the concentration of a reactant quadruples the reaction rate, the reaction is:",
          options: [
            "Zero order with respect to that reactant",
            "First order with respect to that reactant",
            "Second order with respect to that reactant",
            "Third order with respect to that reactant"
          ],
          correctIndex: 2,
          explanation: "When rate ∝ [A]², doubling [A] gives 2² = 4 times the rate, so the reaction is second order with respect to A."
        }
      },
    ],
  },

  // ═══ MODULE 3: DYNAMIC EQUILIBRIUM ═══
  {
    id: "chem-2-s3t1",
    title: "Dynamic Equilibrium and Le Chatelier's Principle",
    subject: "Chemistry",
    subjectIcon: "⚗️",
    programme: "Both",
    unitId: "chemistry",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["chem-2-s2t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "chem-2-s3t1-intro",
        type: "info",
        content: "**Dynamic Equilibrium and Le Chatelier's Principle**\n\nMany chemical reactions are reversible — they can proceed in both forward and backward directions. When the rates of the forward and reverse reactions become equal, the system reaches dynamic equilibrium. Understanding equilibrium allows chemists to control reaction conditions to maximise product yield.",
      },
      {
        id: "chem-2-s3t1-content-1",
        type: "info",
        content: "**Reversible and Irreversible Reactions**\n\n**Irreversible Reactions:**\n- Proceed in only one direction.\n- Products do not revert to reactants.\n- Represented with a single arrow (→).\n- Examples: Combustion, precipitation reactions.\n\n**Reversible Reactions:**\n- Products can revert to reactants.\n- Both forward and backward reactions occur simultaneously.\n- Represented with a double arrow (⇌).\n- Examples: N₂(g) + 3H₂(g) ⇌ 2NH₃(g), H₂O(l) ⇌ H⁺(aq) + OH⁻(aq)\n\n**Dynamic Equilibrium:**\n- Occurs in a **closed system** (no exchange of matter with surroundings).\n- Rate of forward reaction = Rate of reverse reaction.\n- Concentrations of reactants and products remain constant (but not necessarily equal!).\n- The system is dynamic — reactions are still occurring at the molecular level.\n- Equilibrium can be approached from either direction.\n\n**Physical vs Chemical Equilibrium:**\n- Physical equilibrium: e.g., water and ice at 0°C.\n- Chemical equilibrium: e.g., N₂ + 3H₂ ⇌ 2NH₃.",
      },
      {
        id: "chem-2-s3t1-content-2",
        type: "info",
        content: "**Le Chatelier's Principle**\n\n**Statement:** If a system at equilibrium is subjected to a change in conditions (concentration, temperature, pressure), the system will shift its equilibrium position to partially counteract the change.\n\n**1. Effect of Concentration Changes:**\n- Increasing the concentration of a reactant shifts the equilibrium to the right (more products).\n- Decreasing the concentration of a reactant shifts the equilibrium to the left (more reactants).\n- Adding a product shifts equilibrium left; removing a product shifts it right.\n\n**2. Effect of Pressure Changes (for gaseous reactions):**\n- Increasing pressure shifts equilibrium towards the side with fewer gas molecules.\n- Decreasing pressure shifts equilibrium towards the side with more gas molecules.\n- If both sides have the same number of gas molecules, pressure has no effect.\n\n**3. Effect of Temperature Changes:**\n- Increasing temperature shifts equilibrium in the endothermic direction (absorbs heat).\n- Decreasing temperature shifts equilibrium in the exothermic direction (releases heat).\n\n**4. Effect of Catalysts:**\n- Catalysts speed up BOTH forward and reverse reactions equally.\n- They do NOT change the equilibrium position.\n- They help the system reach equilibrium faster.",
      },
      {
        id: "chem-2-s3t1-content-3",
        type: "info",
        content: "**Industrial Applications of Le Chatelier's Principle**\n\n**The Haber Process (Ammonia Production):**\nN₂(g) + 3H₂(g) ⇌ 2NH₃(g) ΔH = −92 kJ/mol (exothermic)\n\n| Condition | Effect on NH₃ Yield | Practical Compromise |\n|-----------|---------------------|---------------------|\n| High pressure | Shifts right (4 → 2 gas moles) → more NH₃ | 200–250 atm (cost of high pressure vessels) |\n| Low temperature | Shifts right (exothermic) → more NH₃ | 400–450°C (low temp = slow rate, compromise needed) |\n| Catalyst | No effect on yield; speeds up reaching equilibrium | Iron catalyst used |\n\n**The Contact Process (Sulphuric Acid):**\n2SO₂(g) + O₂(g) ⇌ 2SO₃(g) ΔH = −197 kJ/mol (exothermic)\n\n- High pressure favours product formation (3 → 2 gas moles).\n- Low temperature favours product (exothermic).\n- Vanadium(V) oxide (V₂O₅) catalyst is used to increase the rate.\n- Temperature compromise: ~450°C.\n\n**Catalytic Converters:**\n- Use platinum, palladium, and rhodium catalysts.\n- Convert toxic exhaust gases (CO, NOₓ, unburned hydrocarbons) into less harmful products (CO₂, N₂, H₂O).",
      },
      {
        id: "chem-2-s3t1-practice",
        type: "question",
        content: "Test your understanding of Le Chatelier's Principle.",
        exercise: {
          question: "For the exothermic reaction N₂(g) + 3H₂(g) ⇌ 2NH₃(g), which condition favours a higher yield of ammonia?",
          options: [
            "High temperature and low pressure",
            "Low temperature and high pressure",
            "High temperature and high pressure",
            "Low temperature and low pressure"
          ],
          correctIndex: 1,
          explanation: "Low temperature favours the exothermic forward reaction. High pressure favours the side with fewer gas molecules (products: 2 moles vs reactants: 4 moles). Both conditions increase ammonia yield."
        }
      },
    ],
  },
  {
    id: "chem-2-s3t2",
    title: "Equilibrium Constants — Kc and Kp",
    subject: "Chemistry",
    subjectIcon: "⚗️",
    programme: "Both",
    unitId: "chemistry",
    difficulty: 4,
    estimatedMinutes: 30,
    xpReward: 60,
    prerequisites: ["chem-2-s3t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "chem-2-s3t2-intro",
        type: "info",
        content: "**Equilibrium Constants — Kc and Kp**\n\nThe equilibrium constant quantifies the position of equilibrium for a reversible reaction. It expresses the ratio of product concentrations (or partial pressures) to reactant concentrations (or partial pressures) at equilibrium.",
      },
      {
        id: "chem-2-s3t2-content-1",
        type: "info",
        content: "**The Equilibrium Constant Kc**\n\nFor a general reaction: aA + bB ⇌ cC + dD\n\nThe equilibrium constant in terms of concentration is:\nKc = [C]ᶜ[D]ᵈ/[A]ᵃ[B]ᵇ\n\n**Key Points:**\n- Square brackets [ ] indicate concentration in mol/dm³.\n- Only aqueous and gaseous species are included; pure solids and pure liquids are omitted.\n- Kc has no units (in practice, the units cancel).\n- Kc is constant at a given temperature.\n\n**Interpreting Kc:**\n| Kc Value | Meaning |\n|----------|---------|\n| Kc >> 1 (large) | Equilibrium lies to the RIGHT — products favoured |\n| Kc << 1 (small) | Equilibrium lies to the LEFT — reactants favoured |\n| Kc ≈ 1 | Significant amounts of both reactants and products |\n\n**Worked Example:**\nFor the reaction: H₂(g) + I₂(g) ⇌ 2HI(g)\n\nAt equilibrium at 450°C: [H₂] = 0.05 M, [I₂] = 0.05 M, [HI] = 0.39 M.\n\nKc = [HI]²/([H₂][I₂]) = (0.39)²/(0.05 × 0.05) = 0.1521/0.0025 = 60.84\n\nSince Kc > 1, the equilibrium favours the product HI.",
      },
      {
        id: "chem-2-s3t2-content-2",
        type: "info",
        content: "**The Equilibrium Constant Kp**\n\nFor gaseous reactions, equilibrium can be expressed in terms of partial pressures.\n\nFor: aA(g) + bB(g) ⇌ cC(g) + dD(g)\n\nKp = (P_C)ᶜ(P_D)ᵈ/(P_A)ᵃ(P_B)ᵇ\n\nWhere P_A, P_B, etc. are the partial pressures of each gas at equilibrium.\n\n**Partial Pressure:**\nThe pressure that a gas would exert if it alone occupied the container.\nP_A = (moles of A/total moles) × total pressure = mole fraction × total pressure\n\n**Relationship between Kp and Kc:**\nKp = Kc(RT)^Δn\n\nWhere:\n- Δn = (moles of gaseous products) − (moles of gaseous reactants)\n- R = gas constant (0.0821 L·atm/mol·K)\n- T = temperature (K)\n\n**Worked Example:**\nFor N₂(g) + 3H₂(g) ⇌ 2NH₃(g):\nΔn = 2 − (1 + 3) = −2\nKp = Kc(RT)⁻² = Kc/(RT)²",
      },
      {
        id: "chem-2-s3t2-content-3",
        type: "info",
        content: "**The Solubility Product (Ksp)**\n\nThe solubility product is the equilibrium constant for the dissolution of a sparingly soluble ionic compound.\n\nFor: AₓBᵧ(s) ⇌ xAʸ⁺(aq) + yBˣ⁻(aq)\n\nKsp = [Aʸ⁺]ˣ[Bˣ⁻]ʸ\n\n**Worked Example:**\nCalculate the solubility of CaF₂ in water, given Ksp = 3.9 × 10⁻¹¹.\n\nCaF₂(s) ⇌ Ca²⁺(aq) + 2F⁻(aq)\n\nLet solubility = S mol/dm³.\nThen [Ca²⁺] = S, [F⁻] = 2S.\n\nKsp = [Ca²⁺][F⁻]² = S × (2S)² = 4S³\nS³ = Ksp/4 = 3.9 × 10⁻¹¹/4 = 9.75 × 10⁻¹²\nS = ∛(9.75 × 10⁻¹²) = 2.14 × 10⁻⁴ mol/dm³\n\n**Factors Affecting Kc:**\n- Only temperature changes affect the value of Kc.\n- Changing concentration, pressure, or adding a catalyst does NOT change Kc.\n- Kc increases with temperature for endothermic reactions.\n- Kc decreases with temperature for exothermic reactions.",
      },
      {
        id: "chem-2-s3t2-practice",
        type: "question",
        content: "Test your understanding of equilibrium constants.",
        exercise: {
          question: "If Kc for a reaction is 0.05, what does this indicate about the equilibrium position?",
          options: [
            "Products are strongly favoured",
            "Reactants are strongly favoured",
            "Reactants and products are present in equal amounts",
            "The reaction does not reach equilibrium"
          ],
          correctIndex: 1,
          explanation: "Kc = 0.05 is less than 1, which means the numerator (product concentrations) is much smaller than the denominator (reactant concentrations). The equilibrium lies to the left, favouring reactants."
        }
      },
    ],
  },

  // ═══ MODULE 4: ACIDS, BASES AND SALTS ═══
  {
    id: "chem-2-s4t1",
    title: "Acid-Base Theories and pH",
    subject: "Chemistry",
    subjectIcon: "⚗️",
    programme: "Both",
    unitId: "chemistry",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["chem-2-s3t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "chem-2-s4t1-intro",
        type: "info",
        content: "**Acid-Base Theories and pH**\n\nAcids and bases are fundamental concepts in chemistry. Three major theories have been developed to define them: Arrhenius, Brønsted-Lowry, and Lewis. The pH scale quantifies the acidity or basicity of a solution.",
      },
      {
        id: "chem-2-s4t1-content-1",
        type: "info",
        content: "**Three Theories of Acids and Bases**\n\n**1. Arrhenius Theory:**\n- Acids produce H⁺ ions in aqueous solution.\n- Bases produce OH⁻ ions in aqueous solution.\n- Limitation: Only applies to aqueous solutions.\n- Example: HCl(aq) → H⁺(aq) + Cl⁻(aq)\n  NaOH(aq) → Na⁺(aq) + OH⁻(aq)\n\n**2. Brønsted-Lowry Theory:**\n- Acids are proton (H⁺) donors.\n- Bases are proton (H⁺) acceptors.\n- Applies to any solvent (not just water).\n- Includes the concept of **conjugate acid-base pairs**.\n- Example: HCl + H₂O → Cl⁻ + H₃O⁺\n  HCl donates H⁺ (acid), H₂O accepts H⁺ (base).\n  Conjugate pair: HCl (acid)/Cl⁻ (conjugate base) and H₂O (base)/H₃O⁺ (conjugate acid).\n\n**Amphiprotic substances** can act as both acid and base (e.g., H₂O, HCO₃⁻).\n\n**3. Lewis Theory:**\n- Acids accept an electron pair.\n- Bases donate an electron pair.\n- The broadest theory — includes many reactions not involving H⁺.\n- Example: BF₃ + NH₃ → BF₃−NH₃\n  BF₃ accepts electron pair (Lewis acid), NH₃ donates (Lewis base).",
      },
      {
        id: "chem-2-s4t1-content-2",
        type: "info",
        content: "**Strong and Weak Acids/Bases**\n\n**Strong Acids:** Completely dissociate in water.\n- HCl, HNO₃, H₂SO₄\n- HCl → H⁺ + Cl⁻ (100% dissociation)\n\n**Weak Acids:** Partially dissociate in water.\n- CH₃COOH, H₂CO₃, H₃PO₄\n- CH₃COOH ⇌ CH₃COO⁻ + H⁺ (about 1% dissociation)\n\n**Strong Bases:** Completely dissociate in water.\n- NaOH, KOH, Ca(OH)₂\n\n**Weak Bases:** Partially dissociate in water.\n- NH₃, NH₄OH\n- NH₃ + H₂O ⇌ NH₄⁺ + OH⁻\n\n**The pH Scale:**\npH = −log₁₀[H⁺]\n\n| pH | [H⁺] (mol/dm³) | Type |\n|----|----------------|------|\n| 0–3 | 10⁰–10⁻³ | Strongly acidic |\n| 4–6 | 10⁻⁴–10⁻⁶ | Weakly acidic |\n| 7 | 10⁻⁷ | Neutral |\n| 8–10 | 10⁻⁸–10⁻¹⁰ | Weakly basic |\n| 11–14 | 10⁻¹¹–10⁻¹⁴ | Strongly basic |\n\n**pOH:** pOH = −log₁₀[OH⁻]\n**Relationship:** pH + pOH = 14 (at 25°C)",
      },
      {
        id: "chem-2-s4t1-content-3",
        type: "info",
        content: "**Properties and Tests for Acids and Bases**\n\n**Properties of Acids:**\n- Sour taste (e.g., citric acid in lemons).\n- Turn blue litmus red.\n- pH less than 7.\n- React with active metals (e.g., Zn, Mg) to produce H₂ gas.\n  Zn(s) + 2HCl(aq) → ZnCl₂(aq) + H₂(g)\n- React with carbonates and bicarbonates to produce CO₂.\n  CaCO₃(s) + 2HCl(aq) → CaCl₂(aq) + H₂O(l) + CO₂(g)\n- Neutralise bases to form salts and water.\n\n**Properties of Bases:**\n- Bitter taste, soapy feel.\n- Turn red litmus blue.\n- pH greater than 7.\n- Produce precipitates with heavy metal salts.\n  Fe³⁺(aq) + 3OH⁻(aq) → Fe(OH)₃(s) (rust-coloured precipitate)\n- React with ammonium salts to release NH₃ gas.\n  NH₄Cl(s) + NaOH(aq) → NaCl(aq) + H₂O(l) + NH₃(g)\n\n**Applications of Neutralisation:**\n- Antacids (Mg(OH)₂, Al(OH)₃) neutralise excess stomach acid.\n- Treating acidic soil with lime (CaO or CaCO₃).\n- Treating wasp stings (alkaline) with vinegar (acid).\n- Treating bee stings (acidic) with baking soda (base).",
      },
      {
        id: "chem-2-s4t1-practice",
        type: "question",
        content: "Test your understanding of acid-base theories.",
        exercise: {
          question: "According to the Brønsted-Lowry theory, a base is a:",
          options: [
            "Substance that produces OH⁻ in water",
            "Proton donor",
            "Proton acceptor",
            "Electron pair donor"
          ],
          correctIndex: 2,
          explanation: "The Brønsted-Lowry theory defines a base as a proton (H⁺) acceptor. An acid is a proton donor."
        }
      },
    ],
  },
  {
    id: "chem-2-s4t2",
    title: "Salts, Titrations and Indicators",
    subject: "Chemistry",
    subjectIcon: "⚗️",
    programme: "Both",
    unitId: "chemistry",
    difficulty: 3,
    estimatedMinutes: 30,
    xpReward: 60,
    prerequisites: ["chem-2-s4t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "chem-2-s4t2-intro",
        type: "info",
        content: "**Salts, Titrations and Indicators**\n\nSalts are ionic compounds formed from the neutralisation of an acid by a base. Titration is a precise analytical technique for determining the concentration of a solution. Indicators help us identify the endpoint of a titration.",
      },
      {
        id: "chem-2-s4t2-content-1",
        type: "info",
        content: "**Types of Salts**\n\n1. **Normal Salts:** Formed when all H⁺ ions of an acid are replaced by metal ions or NH₄⁺.\n   - NaCl, KNO₃, CaSO₄\n\n2. **Acidic Salts:** Contain replaceable H⁺ ions.\n   - NaHSO₄, NaHCO₃, KH₂PO₄\n\n3. **Basic Salts:** Contain OH⁻ groups.\n   - Mg(OH)Cl, Cu₂(OH)₂CO₃\n\n4. **Double Salts:** Contain two different cations or anions.\n   - KAl(SO₄)₂·12H₂O (alum)\n\n5. **Complex Salts:** Contain a complex ion.\n   - [Cu(NH₃)₄]SO₄\n\n6. **Hydrated Salts:** Contain water of crystallisation.\n   - CuSO₄·5H₂O, Na₂CO₃·10H₂O\n\n**Hygroscopic, Deliquescent and Efflorescent Salts:**\n- **Hygroscopic:** Absorb moisture from air (e.g., CaCl₂, NaOH).\n- **Deliquescent:** Absorb enough moisture to dissolve (e.g., CaCl₂, FeCl₃).\n- **Efflorescent:** Lose water of crystallisation to the air (e.g., Na₂CO₃·10H₂O, CuSO₄·5H₂O).\n\n**Preparation of Salts:**\n- **Soluble salts:** React acid with metal, base, or carbonate. Then crystallise.\n- **Insoluble salts:** Precipitation reaction, then filter and dry.",
      },
      {
        id: "chem-2-s4t2-content-2",
        type: "info",
        content: "**Acid-Base Titration**\n\nTitration is a volumetric analysis technique used to determine the concentration of an unknown solution.\n\n**Apparatus:**\n- Burette (for delivering the titrant)\n- Pipette (for measuring a fixed volume of analyte)\n- Conical flask (for the reaction)\n- Indicator (to signal the endpoint)\n\n**Procedure:**\n1. Pipette a known volume of the solution of unknown concentration into a conical flask.\n2. Add a few drops of indicator.\n3. Fill the burette with the standard solution (known concentration).\n4. Add the standard solution from the burette to the flask, swirling continuously.\n5. Stop when the indicator changes colour (endpoint).\n6. Record the volume (titre).\n7. Repeat for accuracy and calculate the average titre.\n\n**Calculations:**\nUsing the equation: C₁V₁ = C₂V₂ (for reactions with 1:1 mole ratio)\nOr: moles = concentration × volume (in dm³)\n\n**Example:**\n25.0 cm³ of NaOH solution requires 22.5 cm³ of 0.1 mol/dm³ HCl for neutralisation. Find the concentration of NaOH.\n\nHCl + NaOH → NaCl + H₂O (1:1 mole ratio)\n\nMoles of HCl = 0.1 × 22.5/1000 = 0.00225 mol\nMoles of NaOH = 0.00225 mol (1:1 ratio)\nConcentration of NaOH = 0.00225/(25/1000) = 0.09 mol/dm³",
      },
      {
        id: "chem-2-s4t2-content-3",
        type: "info",
        content: "**Indicators and Titration Types**\n\n**Common Indicators:**\n| Indicator | Colour in Acid | Colour in Base | pH Range |\n|-----------|---------------|----------------|----------|\n| Methyl orange | Red | Yellow | 3.1–4.4 |\n| Bromothymol blue | Yellow | Blue | 6.0–7.6 |\n| Phenolphthalein | Colourless | Pink | 8.3–10.0 |\n| Litmus | Red | Blue | 5.0–8.0 |\n\n**Choosing an Indicator:**\n- Strong acid + strong base: Any indicator (pH jump 3–11).\n- Strong acid + weak base: Methyl orange (pH jump 3–7).\n- Weak acid + strong base: Phenolphthalein (pH jump 7–11).\n- Weak acid + weak base: No suitable indicator (gradual pH change).\n\n**Double-Indicator Titration:**\nUsed for mixtures of Na₂CO₃ and NaHCO₃:\n- Phenolphthalein endpoint: Na₂CO₃ → NaHCO₃ (first half of reaction).\n- Methyl orange endpoint: Na₂CO₃ → H₂CO₃ and NaHCO₃ → H₂CO₃ (complete reaction).\n\n**Back Titration:**\nUsed when direct titration is unsuitable (e.g., insoluble substance, volatile analyte).\n1. Add excess standard reagent to the analyte.\n2. Titrate the unreacted excess with another standard solution.\n3. Calculate the amount that reacted with the analyte by difference.",
      },
      {
        id: "chem-2-s4t2-practice",
        type: "question",
        content: "Test your understanding of titrations.",
        exercise: {
          question: "Which indicator is most suitable for a titration between a strong acid and a weak base?",
          options: [
            "Phenolphthalein",
            "Methyl orange",
            "Bromothymol blue",
            "Litmus"
          ],
          correctIndex: 1,
          explanation: "Methyl orange (pH range 3.1–4.4) is suitable for strong acid-weak base titrations because the pH at equivalence point is acidic (below 7)."
        }
      },
    ],
  },

  // ═══ MODULE 5: PERIODIC TRENDS ═══
  {
    id: "chem-2-s5t1",
    title: "Periodicity and Period 3 Elements",
    subject: "Chemistry",
    subjectIcon: "⚗️",
    programme: "Both",
    unitId: "chemistry",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["chem-2-s4t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "chem-2-s5t1-intro",
        type: "info",
        content: "**Periodicity and Period 3 Elements**\n\nPeriodicity refers to the repeating patterns of physical and chemical properties across the periodic table. Period 3 elements (Na to Ar) provide an excellent illustration of how properties change across a period.",
      },
      {
        id: "chem-2-s5t1-content-1",
        type: "info",
        content: "**Trends Across Period 3**\n\n**Atomic Radius:**\n- Decreases across the period (Na → Ar).\n- Reason: Increasing nuclear charge pulls electrons closer to the nucleus.\n- Na (186 pm) → Ar (71 pm)\n\n**Ionisation Energy:**\n- Generally increases across the period.\n- Reason: Increasing nuclear charge makes it harder to remove electrons.\n- Small drops at Al (p-orbital starts) and S (electron pairing).\n\n**Electronegativity:**\n- Increases across the period.\n- Reason: Smaller atoms with higher nuclear charge attract bonding electrons more strongly.\n- Na (0.9) → Cl (3.0), Ar (no value — noble gas).\n\n**Melting and Boiling Points:**\n- Na, Mg, Al: High (metallic bonding, increasing charge on ions).\n- Si: Very high (giant covalent structure).\n- P, S, Cl: Low (simple molecular, weak van der Waals forces).\n- Ar: Very low (monatomic, very weak forces).",
      },
      {
        id: "chem-2-s5t1-content-2",
        type: "info",
        content: "**Chemical Properties of Period 3 Elements**\n\n**Reaction with Oxygen (Oxides):**\n| Element | Oxide | Type |\n|---------|-------|------|\n| Na | Na₂O | Ionic basic oxide |\n| Mg | MgO | Ionic basic oxide |\n| Al | Al₂O₃ | Ionic/amphoteric oxide |\n| Si | SiO₂ | Giant covalent, acidic |\n| P | P₄O₁₀ | Molecular, acidic |\n| S | SO₂, SO₃ | Molecular, acidic |\n| Cl | Cl₂O, Cl₂O₇ | Molecular, acidic |\n\n**Acid-Base Character of Period 3 Oxides:**\n- Na₂O + H₂O → 2NaOH (strongly basic)\n- MgO + H₂O → Mg(OH)₂ (weakly basic)\n- Al₂O₃ — amphoteric (reacts with both acids and bases)\n  Al₂O₃ + 6HCl → 2AlCl₃ + 3H₂O\n  Al₂O₃ + 2NaOH + 3H₂O → 2NaAl(OH)₄\n- SiO₂ — weakly acidic (reacts with strong bases)\n- P₄O₁₀, SO₂, Cl₂O₇ — acidic (react with water to form acids)\n  SO₃ + H₂O → H₂SO₄",
      },
      {
        id: "chem-2-s5t1-content-3",
        type: "info",
        content: "**Properties of Period 3 Chlorides and Hydrides**\n\n**Chlorides:**\n| Chloride | Formula | Bond Type | Nature with Water |\n|----------|---------|-----------|-------------------|\n| Sodium chloride | NaCl | Ionic | Dissolves, pH 7 |\n| Magnesium chloride | MgCl₂ | Ionic | Dissolves, pH 7 |\n| Aluminium chloride | Al₂Cl₆ | Covalent (dimer) | Hydrolyses, acidic fumes |\n| Silicon tetrachloride | SiCl₄ | Covalent | Hydrolyses vigorously |\n| Phosphorus trichloride | PCl₃ | Covalent | Hydrolyses, steamy fumes |\n| Sulfur dichloride | SCl₂ | Covalent | Hydrolyses |\n\n**Trend:** Ionic → Covalent across the period.\n\n**Hydrides:**\n| Hydride | Formula | Bonding | Boiling Point |\n|---------|---------|---------|---------------|\n| Sodium hydride | NaH | Ionic | High |\n| Magnesium hydride | MgH₂ | Ionic | High |\n| (AlH₃)ₙ | AlH₃ | Covalent polymer | Moderate |\n| Silane | SiH₄ | Covalent molecular | Low |\n| Phosphine | PH₃ | Covalent molecular | Low |\n| Hydrogen sulfide | H₂S | Covalent molecular | Low |\n| Hydrogen chloride | HCl | Covalent molecular | Low |\n\n**Thermal Stability of Carbonates and Nitrates:**\n- Thermal stability increases down a group (larger cation = more stable).\n- Period 3 carbonates: Na₂CO₃ (very stable) → MgCO₃ (decomposes on heating).\n- MgCO₃ → MgO + CO₂ (decomposes at moderate heat).",
      },
      {
        id: "chem-2-s5t1-practice",
        type: "question",
        content: "Test your understanding of periodic trends.",
        exercise: {
          question: "Which statement correctly describes the trend in atomic radius across Period 3?",
          options: [
            "Atomic radius increases from Na to Ar",
            "Atomic radius decreases from Na to Ar",
            "Atomic radius remains constant across the period",
            "Atomic radius increases then decreases"
          ],
          correctIndex: 1,
          explanation: "Atomic radius decreases across Period 3 because the increasing nuclear charge pulls the electrons more strongly towards the nucleus, reducing the atomic size."
        }
      },
    ],
  },
  {
    id: "chem-2-s5t2",
    title: "Properties of Period 3 Hydroxides and Oxides",
    subject: "Chemistry",
    subjectIcon: "⚗️",
    programme: "Both",
    unitId: "chemistry",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["chem-2-s5t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "chem-2-s5t2-intro",
        type: "info",
        content: "**Properties of Period 3 Hydroxides and Oxides**\n\nThe hydroxides and oxides of Period 3 elements show clear trends in their acid-base behaviour, solubility, and bonding. These trends illustrate the fundamental principles of periodicity.",
      },
      {
        id: "chem-2-s5t2-content-1",
        type: "info",
        content: "**Period 3 Hydroxides**\n\n**Sodium Hydroxide (NaOH):**\n- White, deliquescent solid.\n- Strongly basic — completely dissociates in water.\n- Very soluble in water (exothermic dissolution).\n- Used in soap making (saponification), drain cleaners, paper production.\n\n**Magnesium Hydroxide (Mg(OH)₂):**\n- White solid, sparingly soluble.\n- Weakly basic.\n- Used as an antacid (Milk of Magnesia).\n\n**Aluminium Hydroxide (Al(OH)₃):**\n- White gelatinous precipitate.\n- **Amphoteric** — reacts with both acids and bases.\n  Al(OH)₃ + 3HCl → AlCl₃ + 3H₂O (acts as a base)\n  Al(OH)₃ + NaOH → NaAl(OH)₄ (acts as an acid, forms aluminate)\n- Used in water purification (as a flocculant) and antacids.",
      },
      {
        id: "chem-2-s5t2-content-2",
        type: "info",
        content: "**Acid-Base Trends Across Period 3**\n\n**Summary of Period 3 Oxide and Hydroxide Behaviour:**\n\n| Element | Oxide | Hydroxide | Acid-Base Character |\n|---------|-------|-----------|-------------------|\n| Na | Na₂O | NaOH | Strongly basic |\n| Mg | MgO | Mg(OH)₂ | Weakly basic |\n| Al | Al₂O₃ | Al(OH)₃ | Amphoteric |\n| Si | SiO₂ | H₂SiO₃ | Weakly acidic |\n| P | P₄O₁₀ | H₃PO₄ | Acidic |\n| S | SO₃ | H₂SO₄ | Strongly acidic |\n| Cl | Cl₂O₇ | HClO₄ | Very strongly acidic |\n\n**Explanation:**\n- Left side (Na, Mg): Metals form ionic oxides that produce basic solutions.\n- Middle (Al): Amphoteric — can act as both acid and base.\n- Right side (Si, P, S, Cl): Non-metals form covalent oxides that produce acidic solutions.\n- The transition from basic → amphoteric → acidic is a key periodic trend.",
      },
      {
        id: "chem-2-s5t2-content-3",
        type: "info",
        content: "**Electrical Conductivity and Structure**\n\n**Conductivity Across Period 3:**\n- Na, Mg, Al: Good conductors (metallic bonding, delocalised electrons).\n- Si: Semiconductor (metalloid).\n- P, S, Cl, Ar: Non-conductors (insulators).\n\n**Structure and Bonding Summary:**\n\n| Element | State at RT | Structure | Bonding |\n|---------|-------------|-----------|---------|\n| Na | Solid | Metallic lattice | Metallic |\n| Mg | Solid | Metallic lattice | Metallic |\n| Al | Solid | Metallic lattice | Metallic |\n| Si | Solid | Giant covalent | Covalent |\n| P | Solid | Molecular (P₄) | Covalent |\n| S | Solid | Molecular (S₈ rings) | Covalent |\n| Cl | Gas | Diatomic (Cl₂) | Covalent |\n| Ar | Gas | Monatomic | None |\n\n**Reactions with Water — Period 3 Elements:**\n- Na: Vigorous reaction with water, producing H₂ and NaOH.\n  2Na(s) + 2H₂O(l) → 2NaOH(aq) + H₂(g)\n- Mg: Slow reaction with cold water; faster with steam.\n  Mg(s) + H₂O(g) → MgO(s) + H₂(g) (with steam)\n- Al: Protective oxide layer prevents reaction with water.\n- Si, P, S, Cl: Do not react directly with water (though their oxides do).",
      },
      {
        id: "chem-2-s5t2-practice",
        type: "question",
        content: "Test your understanding of Period 3 hydroxides.",
        exercise: {
          question: "Which Period 3 hydroxide is amphoteric?",
          options: [
            "NaOH",
            "Mg(OH)₂",
            "Al(OH)₃",
            "H₂SO₄"
          ],
          correctIndex: 2,
          explanation: "Aluminium hydroxide (Al(OH)₃) is amphoteric — it can react with both acids (acting as a base) and bases (acting as an acid)."
        }
      },
    ],
  },

  // ═══ MODULE 6: THE HALOGENS ═══
  {
    id: "chem-2-s6t1",
    title: "Physical and Chemical Properties of the Halogens",
    subject: "Chemistry",
    subjectIcon: "⚗️",
    programme: "Both",
    unitId: "chemistry",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["chem-2-s5t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "chem-2-s6t1-intro",
        type: "info",
        content: "**Physical and Chemical Properties of the Halogens**\n\nThe halogens are Group 17 elements: fluorine (F₂), chlorine (Cl₂), bromine (Br₂), iodine (I₂), and astatine (At). They are highly reactive non-metals with distinctive trends in properties down the group.",
      },
      {
        id: "chem-2-s6t1-content-1",
        type: "info",
        content: "**Physical Properties of the Halogens**\n\n| Property | F₂ | Cl₂ | Br₂ | I₂ |\n|----------|-----|-----|-----|-----|\n| Colour | Pale yellow | Greenish-yellow | Red-brown | Dark violet/grey |\n| State at RT | Gas | Gas | Liquid | Solid |\n| Melting point (°C) | −220 | −101 | −7 | 114 |\n| Boiling point (°C) | −188 | −34 | 59 | 184 |\n| Electronegativity | 4.0 | 3.0 | 2.8 | 2.5 |\n| Atomic radius (pm) | 71 | 99 | 114 | 133 |\n| First IE (kJ/mol) | 1681 | 1251 | 1140 | 1008 |\n\n**Trends Down the Group:**\n- Atomic radius increases (more electron shells).\n- Electronegativity decreases (larger atoms hold electrons less tightly).\n- Melting and boiling points increase (stronger van der Waals forces).\n- Colour deepens (more easily excited outer electrons absorb longer wavelengths).\n- Reactivity decreases (larger atoms attract electrons less readily).\n\n**Oxidising Power:**\nF₂ > Cl₂ > Br₂ > I₂\nFluorine is the strongest oxidising agent (most easily reduced).",
      },
      {
        id: "chem-2-s6t1-content-2",
        type: "info",
        content: "**Chemical Reactions of the Halogens**\n\n**Reaction with Metals:**\nHalogens react with metals to form halides (salts).\n2Na(s) + Cl₂(g) → 2NaCl(s)\nFe(s) + Br₂(l) → FeBr₃(s)\n\n**Reaction with Hydrogen:**\nH₂(g) + F₂(g) → 2HF(g) — explosive at room temperature\nH₂(g) + Cl₂(g) → 2HCl(g) — explosive in sunlight\nH₂(g) + Br₂(g) → 2HBr(g) — requires heating\nH₂(g) + I₂(g) ⇌ 2HI(g) — reversible, requires continuous heating\n\n**Displacement Reactions:**\nA more reactive halogen will displace a less reactive halogen from its compounds.\nCl₂(aq) + 2KBr(aq) → 2KCl(aq) + Br₂(aq) (colourless → orange)\nCl₂(aq) + 2KI(aq) → 2KCl(aq) + I₂(aq) (colourless → brown)\nBr₂(aq) + 2KI(aq) → 2KBr(aq) + I₂(aq) (orange → brown)\n\n**Reaction with Water:**\nCl₂ + H₂O ⇌ HCl + HOCl (hydrochloric and hypochlorous acids)\nHOCl is responsible for the bleaching and disinfecting properties of chlorine.\n\n**Uses of Halogens:**\n- **Chlorine:** Water disinfection, bleach production, PVC manufacture.\n- **Bromine:** Flame retardants, photography, pharmaceuticals.\n- **Iodine:** Antiseptic, thyroid hormone production.",
      },
      {
        id: "chem-2-s6t1-content-3",
        type: "info",
        content: "**Hydrogen Halides and Halide Ions**\n\n**Properties of Hydrogen Halides (HX):**\n\n| Property | HF | HCl | HBr | HI |\n|----------|-----|-----|-----|-----|\n| Bond strength (kJ/mol) | 565 | 431 | 364 | 297 |\n| Acid strength in water | Weak | Strong | Strong | Strong |\n| Thermal stability | Highest | ↓ | ↓ | Lowest |\n| Boiling point (°C) | 19.5 | −85 | −67 | −35 |\n\n- HF has unusually high boiling point due to hydrogen bonding.\n- Thermal stability decreases down the group (weaker H−X bonds).\n- Acid strength increases down the group (H−I bond breaks most easily).\n\n**Test for Halide Ions (X⁻):**\nAdd AgNO₃(aq) followed by dilute HNO₃:\n- Cl⁻: White precipitate (AgCl), soluble in dilute NH₃.\n- Br⁻: Cream precipitate (AgBr), soluble in concentrated NH₃.\n- I⁻: Yellow precipitate (AgI), insoluble in NH₃.\n\n**Reactions of Halides with Concentrated H₂SO₄:**\n- NaCl: Produces HCl gas (steamy fumes).\n- NaBr: Produces Br₂ (red-brown fumes) and SO₂.\n- NaI: Produces I₂ (violet fumes) and H₂S (smell of rotten eggs).\n\nThis demonstrates the increasing reducing power of halide ions: I⁻ > Br⁻ > Cl⁻ > F⁻.",
      },
      {
        id: "chem-2-s6t1-practice",
        type: "question",
        content: "Test your understanding of the halogens.",
        exercise: {
          question: "Which halogen is the strongest oxidising agent?",
          options: [
            "Iodine (I₂)",
            "Bromine (Br₂)",
            "Chlorine (Cl₂)",
            "Fluorine (F₂)"
          ],
          correctIndex: 3,
          explanation: "Fluorine is the strongest oxidising agent. It most readily gains electrons (is reduced) due to its small atomic size and high electronegativity."
        }
      },
    ],
  },

  // ═══ MODULE 7: STRUCTURE, CHEMICAL BONDING AND PROPERTIES ═══
  {
    id: "chem-2-s7t1",
    title: "Electronegativity and Bond Polarity",
    subject: "Chemistry",
    subjectIcon: "⚗️",
    programme: "Both",
    unitId: "chemistry",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["chem-2-s6t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "chem-2-s7t1-intro",
        type: "info",
        content: "**Electronegativity and Bond Polarity**\n\nElectronegativity is a measure of the tendency of an atom to attract bonding electrons. Differences in electronegativity between bonded atoms determine bond polarity and influence molecular properties.",
      },
      {
        id: "chem-2-s7t1-content-1",
        type: "info",
        content: "**The Pauling Scale of Electronegativity**\n\nLinus Pauling developed a numerical scale (0.7–4.0) for comparing electronegativities.\n\n**Key Values:**\n| Element | Electronegativity |\n|---------|------------------|\n| Fluorine | 4.0 (highest) |\n| Oxygen | 3.5 |\n| Chlorine | 3.0 |\n| Nitrogen | 3.0 |\n| Carbon | 2.5 |\n| Hydrogen | 2.1 |\n| Sodium | 0.9 |\n| Caesium | 0.7 (lowest) |\n\n**Electronegativity Trends:**\n- Increases from left to right across a period.\n- Decreases down a group.\n- The most electronegative elements are in the top right corner (excluding noble gases).",
      },
      {
        id: "chem-2-s7t1-content-2",
        type: "info",
        content: "**Bond Polarity**\n\nThe difference in electronegativity (ΔEN) between bonded atoms determines the type and polarity of the bond.\n\n| ΔEN | Bond Type | Example |\n|-----|-----------|---------|\n| 0.0–0.4 | Non-polar covalent | Cl₂ (0), CH₄ (0.4) |\n| 0.5–1.7 | Polar covalent | H₂O (1.4), HCl (0.9) |\n| > 1.7 | Ionic | NaCl (2.1), MgO (2.3) |\n\n**Non-polar Covalent Bond:**\n- Equal sharing of electrons.\n- No charge separation (dipole).\n- Examples: H₂, O₂, N₂, Cl₂.\n\n**Polar Covalent Bond:**\n- Unequal sharing of electrons.\n- Partial charges develop: δ⁺ (slightly positive) and δ⁻ (slightly negative).\n- The more electronegative atom has the δ⁻ charge.\n- Example: In HCl, Cl is δ⁻, H is δ⁺.\n\n**Ionic Bond:**\n- Complete transfer of electrons.\n- Full charges develop (+ and −).\n- Electrostatic attraction between oppositely charged ions.\n- Example: Na⁺Cl⁻",
      },
      {
        id: "chem-2-s7t1-content-3",
        type: "info",
        content: "**Dipole Moments and Molecular Polarity**\n\nA molecule is polar if:\n1. It contains polar bonds (ΔEN between bonded atoms > 0.4).\n2. The polar bonds do NOT cancel out due to symmetry.\n\n**Determining Molecular Polarity:**\nConsider both bond polarity and molecular shape (VSEPR theory).\n\n| Molecule | Shape | Bond Dipoles | Overall Polarity |\n|----------|-------|-------------|-----------------|\n| CO₂ | Linear | Cancel | Non-polar |\n| H₂O | Bent | Do not cancel | Polar |\n| CCl₄ | Tetrahedral | Cancel | Non-polar |\n| CH₃Cl | Tetrahedral | Do not cancel | Polar |\n| NH₃ | Trigonal pyramidal | Do not cancel | Polar |\n| BF₃ | Trigonal planar | Cancel | Non-polar |\n\n**Dipole Moment (μ):**\nμ = charge (Q) × distance of separation (d)\nMeasured in Debye units (D).\n\n**Applications of Polarity:**\n- \"Like dissolves like\" — polar solvents dissolve polar solutes.\n- Water is polar → dissolves ionic compounds and polar molecules.\n- Non-polar solvents (hexane, CCl₄) dissolve non-polar substances (oils, fats).",
      },
      {
        id: "chem-2-s7t1-practice",
        type: "question",
        content: "Test your understanding of bond polarity.",
        exercise: {
          question: "A bond between two atoms with electronegativity difference of 1.5 is best described as:",
          options: [
            "Non-polar covalent",
            "Polar covalent",
            "Ionic",
            "Metallic"
          ],
          correctIndex: 1,
          explanation: "A difference of 1.5 falls in the range 0.5–1.7, which is polar covalent. The electrons are shared unequally, creating partial charges."
        }
      },
    ],
  },
  {
    id: "chem-2-s7t2",
    title: "VSEPR Theory, Molecular Shapes and Sigma/Pi Bonds",
    subject: "Chemistry",
    subjectIcon: "⚗️",
    programme: "Both",
    unitId: "chemistry",
    difficulty: 4,
    estimatedMinutes: 30,
    xpReward: 60,
    prerequisites: ["chem-2-s7t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "chem-2-s7t2-intro",
        type: "info",
        content: "**VSEPR Theory, Molecular Shapes and Sigma/Pi Bonds**\n\nThe Valence Shell Electron Pair Repulsion (VSEPR) theory predicts the three-dimensional shapes of molecules based on electron pair repulsion. Understanding molecular shapes is essential for explaining chemical reactivity, polarity, and biological interactions.",
      },
      {
        id: "chem-2-s7t2-content-1",
        type: "info",
        content: "**VSEPR Theory — Predicting Molecular Shapes**\n\nVSEPR theory states that electron pairs (bonding and lone pairs) around a central atom repel each other and arrange themselves as far apart as possible.\n\n**Electron Pair Geometries:**\n| Electron Pairs | Geometry | Bond Angle | Example |\n|---------------|----------|------------|---------|\n| 2 | Linear | 180° | BeCl₂, CO₂ |\n| 3 | Trigonal planar | 120° | BF₃, SO₃ |\n| 4 | Tetrahedral | 109.5° | CH₄, NH₄⁺ |\n| 5 | Trigonal bipyramidal | 90°, 120° | PCl₅ |\n| 6 | Octahedral | 90° | SF₆ |\n\n**Effect of Lone Pairs:**\nLone pairs repel more strongly than bonding pairs, reducing bond angles.\n\n| Molecule | Electron Pairs | Lone Pairs | Shape | Bond Angle |\n|----------|---------------|------------|-------|------------|\n| CH₄ | 4 | 0 | Tetrahedral | 109.5° |\n| NH₃ | 4 | 1 | Trigonal pyramidal | 107° |\n| H₂O | 4 | 2 | Bent/V-shaped | 104.5° |\n\n**VSEPR Notation (AXE):**\nA = central atom, X = bonding pairs, E = lone pairs\n- CH₄: AX₄ (tetrahedral)\n- NH₃: AX₃E₁ (trigonal pyramidal)\n- H₂O: AX₂E₂ (bent)",
      },
      {
        id: "chem-2-s7t2-content-2",
        type: "info",
        content: "**Sigma (σ) and Pi (π) Bonds**\n\n**Sigma Bonds (σ):**\n- Formed by direct (head-on) overlap of atomic orbitals.\n- Can be s-s (H₂), s-p (HF), or p-p (F₂) overlap.\n- Stronger than pi bonds.\n- Allow free rotation of bonded atoms.\n- Every single bond is a sigma bond.\n\n**Pi Bonds (π):**\n- Formed by lateral (sideways) overlap of p-orbitals.\n- Weaker than sigma bonds.\n- Restrict rotation (locked configuration).\n- Occur in double and triple bonds.\n\n**Bond Composition:**\n| Bond Type | Components |\n|-----------|------------|\n| Single (C−C) | 1 σ bond |\n| Double (C=C) | 1 σ + 1 π bond |\n| Triple (C≡C) | 1 σ + 2 π bonds |\n\n**Bond Lengths and Strengths:**\n| Bond | Length (pm) | Strength (kJ/mol) |\n|------|-------------|-------------------|\n| C−C | 154 | 348 |\n| C=C | 134 | 612 |\n| C≡C | 120 | 837 |\n\n**Hybridisation:**\n- sp³: 4 sigma bonds (tetrahedral, 109.5°) — e.g., CH₄\n- sp²: 3 sigma + 1 pi bond (trigonal planar, 120°) — e.g., C₂H₄\n- sp: 2 sigma + 2 pi bonds (linear, 180°) — e.g., C₂H₂",
      },
      {
        id: "chem-2-s7t2-content-3",
        type: "info",
        content: "**Shapes of More Complex Molecules**\n\n**Molecules with Expanded Octets:**\n\n| Molecule | Central Atom | Electron Pairs | Shape |\n|----------|-------------|---------------|-------|\n| PCl₅ | P | 5 | Trigonal bipyramidal |\n| SF₆ | S | 6 | Octahedral |\n| ClF₃ | Cl | 5 (2 lone pairs) | T-shaped |\n| XeF₄ | Xe | 6 (2 lone pairs) | Square planar |\n\n**Predicting Bond Angles:**\nLone pair repulsion follows the order:\nLone pair−lone pair > Lone pair−bonding pair > Bonding pair−bonding pair\n\nThis explains why:\n- H₂O has a smaller bond angle (104.5°) than CH₄ (109.5°) — two lone pairs push the O−H bonds closer.\n- NH₃ has an intermediate angle (107°) — one lone pair.\n\n**Molecular Shape and Biological Function:**\n- The specific shape of molecules determines how they interact with biological receptors.\n- Enzymes have specific active sites that fit their substrates (lock-and-key model).\n- Drugs are designed with specific shapes to fit target receptors.\n- Molecular shape determines whether a substance has a particular smell, taste, or pharmacological effect.",
      },
      {
        id: "chem-2-s7t2-practice",
        type: "question",
        content: "Test your understanding of molecular shapes.",
        exercise: {
          question: "What is the shape of NH₃ according to VSEPR theory?",
          options: [
            "Tetrahedral",
            "Trigonal pyramidal",
            "Bent",
            "Trigonal planar"
          ],
          correctIndex: 1,
          explanation: "NH₃ has 4 electron pairs (3 bonding, 1 lone pair). The base geometry is tetrahedral, but the lone pair repels more strongly, giving a trigonal pyramidal shape with a 107° bond angle."
        }
      },
    ],
  },

  // ═══ MODULE 8: ORGANIC COMPOUNDS ═══
  {
    id: "chem-2-s8t1",
    title: "Alkanes, Alkenes and Alkynes",
    subject: "Chemistry",
    subjectIcon: "⚗️",
    programme: "Both",
    unitId: "chemistry",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["chem-2-s7t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "chem-2-s8t1-intro",
        type: "info",
        content: "**Alkanes, Alkenes and Alkynes**\n\nOrganic chemistry is the study of carbon-containing compounds. Hydrocarbons are compounds containing only carbon and hydrogen. They are classified as alkanes (saturated), alkenes (unsaturated with double bonds), and alkynes (unsaturated with triple bonds).",
      },
      {
        id: "chem-2-s8t1-content-1",
        type: "info",
        content: "**Alkanes (Saturated Hydrocarbons)**\n\n**General Formula:** CₙH₂ₙ₊₂\n\n**Examples:**\n- CH₄ (methane), C₂H₆ (ethane), C₃H₈ (propane), C₄H₁₀ (butane)\n\n**Structure:**\n- All carbon-carbon bonds are single bonds (σ bonds).\n- sp³ hybridised carbon atoms (tetrahedral, 109.5°).\n- Only sigma bonds — no pi bonds.\n\n**Properties:**\n- Relatively unreactive (saturated — no double bonds to attack).\n- Non-polar — insoluble in water, soluble in organic solvents.\n- Low boiling points (increase with chain length due to van der Waals forces).\n\n**Reactions of Alkanes:**\n\n1. **Combustion:** Complete: CH₄ + 2O₂ → CO₂ + 2H₂O\n   Incomplete: 2CH₄ + 3O₂ → 2CO + 4H₂O (produces toxic CO)\n\n2. **Halogenation (Substitution):**\n   CH₄ + Cl₂ → CH₃Cl + HCl (requires UV light or heat)\n   Free radical mechanism: initiation (Cl₂ → 2Cl•), propagation, termination.\n\n3. **Cracking:** Breaking long-chain alkanes into smaller, more valuable molecules.\n   C₁₆H₃₄ → C₈H₁₈ + C₈H₁₆ (octane and octene)\n   Thermal cracking: high temperature, high pressure.\n   Catalytic cracking: zeolite catalysts, lower temperature.",
      },
      {
        id: "chem-2-s8t1-content-2",
        type: "info",
        content: "**Alkenes (Unsaturated with C=C)**\n\n**General Formula:** CₙH₂ₙ\n\n**Examples:**\n- C₂H₄ (ethene), C₃H₆ (propene), C₄H₈ (butene)\n\n**Structure:**\n- Contains at least one carbon-carbon double bond (C=C).\n- sp² hybridised carbon atoms (trigonal planar, 120°).\n- Double bond = 1 σ bond + 1 π bond.\n- The π bond restricts rotation → cis-trans (geometric) isomerism.\n\n**Properties:**\n- More reactive than alkanes (the π bond is electron-rich and easily attacked).\n- The C=C bond is a site for electrophilic attack.\n\n**Reactions of Alkenes (Addition Reactions):**\n\n1. **Hydrogenation:** C₂H₄ + H₂ → C₂H₆ (Ni catalyst)\n2. **Halogenation:** C₂H₄ + Br₂ → C₂H₄Br₂ (orange bromine water decolourises)\n3. **Hydrohalogenation:** C₂H₄ + HCl → C₂H₅Cl\n4. **Hydration:** C₂H₄ + H₂O → C₂H₅OH (H₃PO₄ catalyst)\n5. **Polymerisation:** n(C₂H₄) → (CH₂−CH₂)ₙ (polyethene)\n\n**The test for unsaturation:**\n- Bromine water (orange) decolourised by alkenes and alkynes.\n- Purple KMnO₄ solution decolourised by alkenes (Baeyer's test).",
      },
      {
        id: "chem-2-s8t1-content-3",
        type: "info",
        content: "**Alkynes (Unsaturated with C≡C)**\n\n**General Formula:** CₙH₂ₙ₋₂\n\n**Examples:**\n- C₂H₂ (ethyne/acetylene), C₃H₄ (propyne)\n\n**Structure:**\n- Contains at least one carbon-carbon triple bond (C≡C).\n- sp hybridised carbon atoms (linear, 180°).\n- Triple bond = 1 σ bond + 2 π bonds.\n\n**Properties:**\n- Even more reactive than alkenes due to two π bonds.\n- Terminal alkynes (R−C≡C−H) are weakly acidic.\n\n**Reactions of Alkynes:**\n\n1. **Addition reactions:**\n   C₂H₂ + 2H₂ → C₂H₆ (complete hydrogenation)\n   C₂H₂ + 2Br₂ → C₂H₂Br₄ (bromine water decolourised)\n\n2. **Formation of metal acetylides:**\n   2C₂H₂ + 2Na → 2NaC≡CH + H₂\n   C₂H₂ + 2AgNO₃ + 2NH₃ → Ag₂C₂↓ (white precipitate) + 2NH₄NO₃ + 2H₂O\n   (This distinguishes terminal alkynes from alkenes.)\n\n**Benzene (C₆H₆) — Aromatic Hydrocarbon:**\n- Planar, cyclic structure with delocalised π-electrons.\n- sp² hybridised, 120° bond angles.\n- Especially stable due to resonance (aromaticity).\n- Undergoes **electrophilic substitution** rather than addition (to preserve the aromatic ring).\n- Reactions: halogenation, nitration, sulfonation, Friedel-Crafts alkylation.",
      },
      {
        id: "chem-2-s8t1-practice",
        type: "question",
        content: "Test your understanding of hydrocarbons.",
        exercise: {
          question: "Which test distinguishes an alkene from an alkane?",
          options: [
            "Burning in air",
            "Shaking with bromine water",
            "Adding water",
            "Measuring density"
          ],
          correctIndex: 1,
          explanation: "Bromine water (orange) is decolourised by alkenes (due to addition across the C=C double bond) but remains orange with alkanes. This is a simple test for unsaturation."
        }
      },
    ],
  },
  {
    id: "chem-2-s8t2",
    title: "Alkanols, Alkanoic Acids and Esters",
    subject: "Chemistry",
    subjectIcon: "⚗️",
    programme: "Both",
    unitId: "chemistry",
    difficulty: 3,
    estimatedMinutes: 30,
    xpReward: 60,
    prerequisites: ["chem-2-s8t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "chem-2-s8t2-intro",
        type: "info",
        content: "**Alkanols, Alkanoic Acids and Esters**\n\nFunctional groups are specific atoms or groups of atoms that give organic molecules their characteristic chemical properties. Alkanols (alcohols), alkanoic acids (carboxylic acids), and esters are three important families of organic compounds with the oxygen-containing functional groups −OH, −COOH, and −COO−.",
      },
      {
        id: "chem-2-s8t2-content-1",
        type: "info",
        content: "**Alkanols (Alcohols)**\n\n**General Formula:** CₙH₂ₙ₊₁OH or R−OH\n\n**Functional Group:** Hydroxyl group (−OH)\n\n**Naming:** Replace \"-e\" of the corresponding alkane with \"-ol\".\n- CH₃OH (methanol), C₂H₅OH (ethanol), C₃H₇OH (propanol)\n\n**Classification:**\n- **Primary (1°) Alkanol:** −OH on a carbon bonded to 1 other carbon.\n  - Example: CH₃CH₂OH (ethanol)\n- **Secondary (2°) Alkanol:** −OH on a carbon bonded to 2 other carbons.\n  - Example: CH₃CH(OH)CH₃ (propan-2-ol)\n- **Tertiary (3°) Alkanol:** −OH on a carbon bonded to 3 other carbons.\n  - Example: (CH₃)₃COH (2-methylpropan-2-ol)\n\n**Physical Properties:**\n- Polar −OH group allows hydrogen bonding.\n- Higher boiling points than corresponding alkanes.\n- Smaller alkanols (C₁−C₃) are soluble in water (hydrogen bonds with water).\n- Solubility decreases as carbon chain length increases.",
      },
      {
        id: "chem-2-s8t2-content-2",
        type: "info",
        content: "**Reactions of Alkanols**\n\n**1. Combustion:**\nC₂H₅OH + 3O₂ → 2CO₂ + 3H₂O (clean flame — used as fuel)\n\n**2. Oxidation:**\n- Primary alkanols → aldehydes → carboxylic acids\n  CH₃CH₂OH → CH₃CHO → CH₃COOH\n- Secondary alkanols → ketones\n  CH₃CH(OH)CH₃ → CH₃COCH₃\n- Tertiary alkanols: resistant to oxidation.\n\nOxidising agents: acidified K₂Cr₂O₇ (orange → green), KMnO₄.\n\nThe breathalyser test for alcohol uses the colour change of dichromate.\n\n**3. Dehydration (Elimination of Water):**\n- With concentrated H₂SO₄ at 170°C: alkene is formed.\n  C₂H₅OH → C₂H₄ + H₂O\n\n**4. Esterification:**\n- React with carboxylic acids to form esters (fruity smell).\n  CH₃COOH + C₂H₅OH ⇌ CH₃COOC₂H₅ + H₂O (conc. H₂SO₄ catalyst)\n\n**5. Reaction with Sodium:**\n2C₂H₅OH + 2Na → 2C₂H₅ONa + H₂(g)\n(Sodium ethoxide + hydrogen gas)\nThis shows that the O−H bond in alcohols is slightly acidic.",
      },
      {
        id: "chem-2-s8t2-content-3",
        type: "info",
        content: "**Alkanoic Acids (Carboxylic Acids) and Esters**\n\n**Alkanoic Acids — General Formula:** R−COOH\n**Functional Group:** Carboxyl group (−COOH)\n\n**Naming:** Replace \"-e\" with \"-oic acid\".\n- HCOOH (methanoic acid), CH₃COOH (ethanoic acid)\n\n**Properties:**\n- Weak acids (partially dissociate: RCOOH ⇌ RCOO⁻ + H⁺)\n- Form hydrogen-bonded dimers (high boiling points).\n- Soluble in water (short chain).\n- Sour taste, turn blue litmus red.\n\n**Reactions:**\n1. **Neutralisation:** CH₃COOH + NaOH → CH₃COONa + H₂O\n2. **Carbonates:** 2CH₃COOH + Na₂CO₃ → 2CH₃COONa + CO₂ + H₂O\n3. **Esterification:** RCOOH + R'OH ⇌ RCOOR' + H₂O\n\n**Identification Tests:**\n- Blue litmus → red (acidic).\n- NaHCO₃ test: effervescence (CO₂ bubbles).\n- Ester test: fruity smell after heating with ethanol and conc. H₂SO₄.\n\n**Esters — General Formula:** RCOOR'\n**Functional Group:** Ester linkage (−COO−)\n\n**Properties:**\n- Pleasant, fruity odours (used in flavourings and fragrances).\n- Volatile liquids with low boiling points.\n- Insoluble in water (longer chain esters).\n- Used in perfumes, food flavourings, plasticisers, and solvents.\n\n**Hydrolysis of Esters:**\n- Acid hydrolysis: RCOOR' + H₂O ⇌ RCOOH + R'OH (reversible)\n- Base hydrolysis (saponification): RCOOR' + NaOH → RCOONa + R'OH (irreversible) — used in soap making.",
      },
      {
        id: "chem-2-s8t2-practice",
        type: "question",
        content: "Test your understanding of organic functional groups.",
        exercise: {
          question: "Esterification is the reaction between:",
          options: [
            "An alkane and an alcohol",
            "An alkanol and an alkanoic acid",
            "An alkene and water",
            "An alkanol and a halogen"
          ],
          correctIndex: 1,
          explanation: "Esterification is the reaction between an alkanol (alcohol) and an alkanoic acid (carboxylic acid) to form an ester and water. It requires a strong acid catalyst (usually concentrated H₂SO₄)."
        }
      },
    ],
  },
];

// ── Module count for reference ──────────────────────────────────────────────
export const CHEMISTRY_SHS2_COUNT = 8;
