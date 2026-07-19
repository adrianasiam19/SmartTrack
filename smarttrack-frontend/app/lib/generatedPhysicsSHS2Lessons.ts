/**
 * generatedPhysicsSHS2Lessons.ts
 * Auto-generated Physics SHS 2 lessons from Ministry of Education curriculum materials.
 * Source: Physics Year2.pdf (Ministry of Education, Ghana, 2025)
 * Contains 8 sections with 16 lessons total.
 */

import type { Lesson } from './learningContent';

export const PHYSICS_SHS2_LESSONS: Lesson[] = [

  // ═══ MODULE 1: DIMENSION, VECTORS, FLOTATION AND DEFORMATION ═══
  {
    id: "phys-2-s1t1",
    title: "Dimensional Analysis and Vectors",
    subject: "Physics",
    subjectIcon: "⚛️",
    programme: "Both",
    unitId: "physics",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: [],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "phys-2-s1t1-intro",
        type: "info",
        content: "**Dimensional Analysis and Vectors**\n\nDimensional analysis is a powerful tool in physics for checking the consistency of equations and deriving relationships between physical quantities. Vectors represent quantities with both magnitude and direction, essential for describing forces, velocities, and accelerations.",
      },
      {
        id: "phys-2-s1t1-content-1",
        type: "info",
        content: "**Dimensional Analysis**\n\nDimensions describe the fundamental nature of a physical quantity, independent of the units used.\n\n**Base Dimensions:**\n| Quantity | Dimension | SI Unit |\n|----------|-----------|---------|\n| Length | L | m |\n| Mass | M | kg |\n| Time | T | s |\n| Electric Current | I | A |\n| Temperature | θ | K |\n\n**Derived Dimensions:**\n- Velocity: [v] = LT⁻¹\n- Acceleration: [a] = LT⁻²\n- Force: [F] = MLT⁻²\n- Energy: [E] = ML²T⁻²\n- Pressure: [P] = ML⁻¹T⁻²\n\n**Applications of Dimensional Analysis:**\n1. **Checking equation consistency:** Both sides must have the same dimensions.\n2. **Deriving relationships:** Determine how one quantity depends on others.\n3. **Converting units.**",
      },
      {
        id: "phys-2-s1t1-content-2",
        type: "info",
        content: "**Dimensional Analysis — Worked Examples**\n\n**Example 1:** Check if v = u + at is dimensionally consistent.\n\n[v] = LT⁻¹, [u] = LT⁻¹, [a] = LT⁻², [t] = T\n[at] = LT⁻² × T = LT⁻¹\nLHS: LT⁻¹, RHS: LT⁻¹ + LT⁻¹ = LT⁻¹ (constants are dimensionless)\nConclusion: Dimensionally consistent ✓\n\n**Example 2:** Derive the relationship for the time period T of a simple pendulum, assuming it depends on length l and acceleration due to gravity g.\n\nAssume T = k·lᵃ·gᵇ (k is a dimensionless constant)\n[T] = T, [l] = L, [g] = LT⁻²\n\nT = Lᵃ·(LT⁻²)ᵇ = Lᵃ⁺ᵇ·T⁻²ᵇ\n\nComparing exponents:\nFor T: −2b = 1 → b = −½\nFor L: a + b = 0 → a = ½\n\nTherefore: T = k·l¹ᐟ²·g⁻¹ᐟ² = k·√(l/g)\n\n(Experimental: k = 2π, so T = 2π√(l/g))",
      },
      {
        id: "phys-2-s1t1-content-3",
        type: "info",
        content: "**Vector Operations**\n\n**Vector Components:**\nAny vector F can be resolved into perpendicular components:\nFₓ = F·cos θ\nFᵧ = F·sin θ\n\n**Resultant of Perpendicular Vectors:**\nMagnitude: F = √(Fₓ² + Fᵧ²)\nDirection: θ = tan⁻¹(Fᵧ/Fₓ)\n\n**Addition of Vectors (Component Method):**\n1. Resolve all vectors into x- and y-components.\n2. Sum all x-components: ΣFₓ = F₁ₓ + F₂ₓ + ...\n3. Sum all y-components: ΣFᵧ = F₁ᵧ + F₂ᵧ + ...\n4. Resultant: R = √[(ΣFₓ)² + (ΣFᵧ)²]\n5. Direction: θ = tan⁻¹(ΣFᵧ/ΣFₓ)\n\n**Triangle and Parallelogram Laws:**\n- Triangle law: The resultant of two vectors is the third side of a triangle formed by the two vectors head-to-tail.\n- Parallelogram law: The resultant is the diagonal of a parallelogram formed by two vectors from a common origin.\n\n**Applications:**\n- Resolving forces on an inclined plane.\n- Adding velocities in navigation.\n- Calculating net force on an object.",
      },
      {
        id: "phys-2-s1t1-practice",
        type: "question",
        content: "Test your understanding of dimensional analysis.",
        exercise: {
          question: "If force F has dimensions MLT⁻² and area A has dimensions L², what are the dimensions of pressure P = F/A?",
          options: [
            "ML²T⁻²",
            "ML⁻¹T⁻²",
            "MLT⁻²",
            "MLT"
          ],
          correctIndex: 1,
          explanation: "P = F/A, so [P] = [F]/[A] = MLT⁻²/L² = ML⁻¹T⁻²."
        }
      },
    ],
  },
  {
    id: "phys-2-s1t2",
    title: "Flotation, Archimedes' Principle and Elastic Deformation",
    subject: "Physics",
    subjectIcon: "⚛️",
    programme: "Both",
    unitId: "physics",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["phys-2-s1t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "phys-2-s1t2-intro",
        type: "info",
        content: "**Flotation, Archimedes' Principle and Elastic Deformation**\n\nArchimedes' Principle explains why objects float or sink in fluids. Hooke's Law describes the elastic behaviour of materials, and Young's Modulus quantifies a material's stiffness. These principles have wide-ranging applications in engineering and design.",
      },
      {
        id: "phys-2-s1t2-content-1",
        type: "info",
        content: "**Density and Relative Density**\n\n**Density (ρ):** Mass per unit volume.\nρ = m/V\nSI unit: kg/m³\n\n**Relative Density (Specific Gravity):**\nRatio of the density of a substance to the density of water (1000 kg/m³).\nRelative density = ρ_substance/ρ_water\n\n**Archimedes' Principle:**\nWhen a body is completely or partially immersed in a fluid, it experiences an upward force (upthrust) equal to the weight of the fluid displaced.\n\nUpthrust = Weight of fluid displaced = Vρg\n\nWhere:\n- V = volume of fluid displaced (m³)\n- ρ = density of fluid (kg/m³)\n- g = acceleration due to gravity (m/s²)\n\n**Law of Flotation:**\nA floating body displaces its own weight of the fluid in which it floats.\nWeight of floating body = Weight of fluid displaced",
      },
      {
        id: "phys-2-s1t2-content-2",
        type: "info",
        content: "**Hooke's Law and Elastic Deformation**\n\n**Hooke's Law:**\nProvided the elastic limit is not exceeded, the extension of a spring is directly proportional to the applied force.\n\nF = ke\n\nWhere:\n- F = applied force (N)\n- k = spring constant (N/m)\n- e = extension (m)\n\n**Elastic and Plastic Deformation:**\n- **Elastic deformation:** The material returns to its original shape when the force is removed.\n- **Plastic deformation:** The material remains permanently deformed after the force is removed.\n- **Elastic limit:** The maximum stress a material can withstand without permanent deformation.\n\n**Elastic Potential Energy (Strain Energy):**\nThe energy stored in a stretched spring or elastic material.\n\nE = ½Fe = ½ke²\n\n**Applications:**\n- Springs in suspension systems.\n- Elastic bands and bungee cords.\n- Spring balances for measuring force.",
      },
      {
        id: "phys-2-s1t2-content-3",
        type: "info",
        content: "**Young's Modulus**\n\nYoung's Modulus (E) measures the stiffness of a material.\n\n**Tensile Stress (σ):** Force per unit cross-sectional area.\nσ = F/A (Unit: N/m² or Pa)\n\n**Tensile Strain (ε):** Extension per unit original length.\nε = e/L (dimensionless)\n\n**Young's Modulus:**\nE = Stress/Strain = (F/A)/(e/L) = FL/Ae\n\n**Worked Example:**\nA wire of length 2.0 m and cross-sectional area 1.0 × 10⁻⁶ m² is stretched by a force of 100 N, extending by 1.0 mm. Calculate Young's Modulus.\n\nE = FL/Ae\n= (100 N × 2.0 m)/(1.0 × 10⁻⁶ m² × 0.001 m)\n= 200/1.0 × 10⁻⁹\n= 2.0 × 10¹¹ N/m²\n\n**Typical Values of Young's Modulus:**\n| Material | E (N/m²) |\n|----------|----------|\n| Steel | 2.0 × 10¹¹ |\n| Aluminium | 7.0 × 10¹⁰ |\n| Copper | 1.1 × 10¹¹ |\n| Wood | 1.0 × 10¹⁰ |\n\n**Applications:**\n- Selecting materials for bridges, buildings, and aircraft.\n- Designing springs and shock absorbers.\n- Understanding material behaviour under load.",
      },
      {
        id: "phys-2-s1t2-practice",
        type: "question",
        content: "Test your understanding of flotation and deformation.",
        exercise: {
          question: "According to Hooke's Law, the force needed to stretch a spring is:",
          options: [
            "Inversely proportional to the extension",
            "Directly proportional to the extension within the elastic limit",
            "Independent of the extension",
            "Equal to the spring constant divided by the extension"
          ],
          correctIndex: 1,
          explanation: "Hooke's Law states: F = ke, where F is force, k is spring constant, and e is extension. Force is directly proportional to extension, provided the elastic limit is not exceeded."
        }
      },
    ],
  },

  // ═══ MODULE 2: MEASUREMENT OF HEAT ═══
  {
    id: "phys-2-s2t1",
    title: "Specific Heat Capacity and Calorimetry",
    subject: "Physics",
    subjectIcon: "⚛️",
    programme: "Both",
    unitId: "physics",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["phys-2-s1t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "phys-2-s2t1-intro",
        type: "info",
        content: "**Specific Heat Capacity and Calorimetry**\n\nHeat is a form of energy transfer between systems at different temperatures. The measurement of heat energy is called calorimetry. Understanding specific heat capacity allows us to calculate how much energy is needed to change the temperature of a substance.",
      },
      {
        id: "phys-2-s2t1-content-1",
        type: "info",
        content: "**Heat Capacity and Specific Heat Capacity**\n\n**Heat Capacity (C):** The amount of heat energy required to raise the temperature of an object by 1°C (or 1 K).\nC = Q/ΔT\nUnit: J/K or J/°C\n\n**Specific Heat Capacity (c):** The amount of heat energy required to raise the temperature of 1 kg of a substance by 1°C (or 1 K).\nc = Q/mΔT\nUnit: J/(kg·K) or J/(kg·°C)\n\n**Key Formula:**\nQ = mcΔT\n\nWhere:\n- Q = heat energy (J)\n- m = mass (kg)\n- c = specific heat capacity (J/kg·K)\n- ΔT = change in temperature (K)\n\n**Typical Specific Heat Capacities:**\n| Substance | c (J/kg·K) |\n|-----------|-----------|\n| Water | 4200 |\n| Aluminium | 900 |\n| Copper | 390 |\n| Iron | 450 |\n| Ice | 2100 |\n| Air | 1000 |\n\nWater has a high specific heat capacity, which is why it is used as a coolant and why coastal areas have milder climates.",
      },
      {
        id: "phys-2-s2t1-content-2",
        type: "info",
        content: "**Calorimetry — Measuring Specific Heat Capacity**\n\n**Method of Mixtures:**\nA hot object is placed in a known mass of cool water in a calorimeter. The final equilibrium temperature is measured.\n\nHeat lost by hot object = Heat gained by water + calorimeter\n\n**Electrical Method (for liquids):**\nAn electrical heater supplies energy to the substance. The temperature rise is measured.\n\nElectrical energy supplied = VIt (V = voltage, I = current, t = time)\n\nQ = VIt = mcΔT\n\nTherefore: c = VIt/mΔT\n\n**Worked Example:**\nA 0.5 kg metal block at 100°C is placed in 0.2 kg of water at 20°C in a calorimeter (heat capacity 50 J/K). The final temperature is 30°C. Find the specific heat capacity of the metal. (c_water = 4200 J/kg·K)\n\nHeat lost by metal = m_metal × c_metal × ΔT_metal\n= 0.5 × c_metal × (100 − 30) = 35c_metal\n\nHeat gained by water = 0.2 × 4200 × (30 − 20) = 840 J\nHeat gained by calorimeter = 50 × (30 − 20) = 500 J\nTotal heat gained = 840 + 500 = 1340 J\n\nHeat lost = Heat gained\n35c_metal = 1340\nc_metal = 38.3 J/kg·K",
      },
      {
        id: "phys-2-s2t1-content-3",
        type: "info",
        content: "**Specific Latent Heat**\n\n**Latent heat** is the energy absorbed or released when a substance changes state (phase) without a change in temperature.\n\n**Specific Latent Heat of Fusion (L_f):**\nEnergy required to change 1 kg of a solid to liquid at its melting point.\nQ = mL_f\n\n**Specific Latent Heat of Vaporisation (L_v):**\nEnergy required to change 1 kg of a liquid to gas at its boiling point.\nQ = mL_v\n\n**Typical Values:**\n| Substance | L_f (J/kg) | L_v (J/kg) |\n|-----------|-----------|-----------|\n| Water | 3.36 × 10⁵ | 2.26 × 10⁶ |\n| Ice | 3.36 × 10⁵ | — |\n\n**Worked Example:**\nCalculate the heat required to convert 0.5 kg of ice at 0°C to steam at 100°C.\n\nStep 1: Melt ice at 0°C: Q₁ = mL_f = 0.5 × 3.36 × 10⁵ = 1.68 × 10⁵ J\nStep 2: Heat water to 100°C: Q₂ = mcΔT = 0.5 × 4200 × 100 = 2.10 × 10⁵ J\nStep 3: Vaporise water at 100°C: Q₃ = mL_v = 0.5 × 2.26 × 10⁶ = 1.13 × 10⁶ J\n\nTotal heat: Q = Q₁ + Q₂ + Q₃ = 1.68 × 10⁵ + 2.10 × 10⁵ + 1.13 × 10⁶ = 1.508 × 10⁶ J",
      },
      {
        id: "phys-2-s2t1-practice",
        type: "question",
        content: "Test your understanding of specific heat capacity.",
        exercise: {
          question: "The specific heat capacity of water is 4200 J/kg·K. How much energy is needed to raise the temperature of 2 kg of water from 20°C to 30°C?",
          options: [
            "42,000 J",
            "84,000 J",
            "8400 J",
            "4200 J"
          ],
          correctIndex: 1,
          explanation: "Q = mcΔT = 2 × 4200 × 10 = 84,000 J. It takes 84 kJ of energy to heat 2 kg of water by 10°C."
        }
      },
    ],
  },

  // ═══ MODULE 3: ELECTROSTATICS ═══
  {
    id: "phys-2-s3t1",
    title: "Coulomb's Law and Electric Fields",
    subject: "Physics",
    subjectIcon: "⚛️",
    programme: "Both",
    unitId: "physics",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["phys-2-s2t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "phys-2-s3t1-intro",
        type: "info",
        content: "**Coulomb's Law and Electric Fields**\n\nElectrostatics is the study of stationary electric charges. Coulomb's Law describes the force between charged particles, and the concept of an electric field helps us understand how charges interact over distance.",
      },
      {
        id: "phys-2-s3t1-content-1",
        type: "info",
        content: "**Coulomb's Law**\n\nCoulomb's Law states that the electrostatic force between two point charges is:\n- Directly proportional to the product of the charges.\n- Inversely proportional to the square of the distance between them.\n\nF = k|q₁q₂|/r²\n\nWhere:\n- F = electrostatic force (N)\n- q₁, q₂ = magnitudes of the charges (C)\n- r = distance between charges (m)\n- k = Coulomb's constant = 8.99 × 10⁹ N·m²/C²\n\nAlternatively: F = |q₁q₂|/(4πε₀r²)\n\nWhere ε₀ = 8.85 × 10⁻¹² C²/N·m² (permittivity of free space).\n\n**Key Points:**\n- Like charges (+ and +, or − and −) REPEL each other.\n- Opposite charges (+ and −) ATTRACT each other.\n- The force is along the line joining the centres of the two charges.",
      },
      {
        id: "phys-2-s3t1-content-2",
        type: "info",
        content: "**Electric Field**\n\nAn electric field is a region in which a charged particle experiences an electrostatic force.\n\n**Electric Field Strength (E):**\nThe electric field strength at a point is the force per unit positive charge experienced by a test charge placed at that point.\n\nE = F/q\n\nUnit: N/C or V/m\n\n**For a point charge:**\nE = kQ/r²\n\n**For a uniform field (between parallel plates):**\nE = V/d\n\nWhere:\n- V = potential difference between plates (V)\n- d = distance between plates (m)\n\n**Electric Field Lines:**\n- Start on positive charges and end on negative charges.\n- The direction of the field at any point is the direction of the force on a positive test charge.\n- Lines are closer together where the field is stronger.\n- Field lines never cross.",
      },
      {
        id: "phys-2-s3t1-content-3",
        type: "info",
        content: "**Electric Potential and Work**\n\n**Electric Potential (V):**\nThe electric potential at a point is the work done per unit charge in bringing a small positive test charge from infinity to that point.\n\nV = W/q\n\nUnit: Volt (V) = J/C\n\n**For a point charge:**\nV = kQ/r\n\n**Potential Difference:**\nThe work done in moving a charge between two points in an electric field.\n\nW = qΔV\n\n**Worked Example:**\nTwo charges, q₁ = +2 µC and q₂ = −3 µC, are separated by 0.5 m. Calculate the force between them.\n\nF = k|q₁q₂|/r²\n= (8.99 × 10⁹)(2 × 10⁻⁶)(3 × 10⁻⁶)/(0.5)²\n= (8.99 × 10⁹ × 6 × 10⁻¹²)/0.25\n= 0.05394/0.25\n= 0.216 N (attractive, since charges are opposite)\n\n**Electric Potential Energy:**\nU = kq₁q₂/r\n\nThe potential energy of a system of two point charges is the work required to bring them from infinity to their separation distance.",
      },
      {
        id: "phys-2-s3t1-practice",
        type: "question",
        content: "Test your understanding of electrostatics.",
        exercise: {
          question: "If the distance between two charges is doubled, the electrostatic force between them:",
          options: [
            "Doubles",
            "Halves",
            "Becomes one-quarter",
            "Becomes four times"
          ],
          correctIndex: 2,
          explanation: "Coulomb's Law: F ∝ 1/r². If r doubles (×2), then F becomes 1/2² = 1/4 of its original value."
        }
      },
    ],
  },
  {
    id: "phys-2-s3t2",
    title: "Capacitors and Dielectrics",
    subject: "Physics",
    subjectIcon: "⚛️",
    programme: "Both",
    unitId: "physics",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["phys-2-s3t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "phys-2-s3t2-intro",
        type: "info",
        content: "**Capacitors and Dielectrics**\n\nCapacitors are devices that store electrical energy in an electric field. They are essential components in electronic circuits for energy storage, filtering, timing, and coupling applications.",
      },
      {
        id: "phys-2-s3t2-content-1",
        type: "info",
        content: "**Capacitance**\n\n**Capacitance (C)** is the ability of a capacitor to store charge. It is defined as the ratio of the charge stored (Q) to the potential difference (V) across it.\n\nC = Q/V\n\nUnit: Farad (F) = C/V\n\n**Parallel Plate Capacitor:**\nFor a parallel plate capacitor:\nC = ε₀εᵣA/d\n\nWhere:\n- ε₀ = permittivity of free space (8.85 × 10⁻¹² F/m)\n- εᵣ = relative permittivity (dielectric constant) of the material between plates\n- A = area of each plate (m²)\n- d = distance between plates (m)\n\n**Factors Affecting Capacitance:**\n- Larger plate area → larger capacitance.\n- Smaller plate separation → larger capacitance.\n- Higher dielectric constant → larger capacitance.\n\n**Energy Stored in a Capacitor:**\nE = ½QV = ½CV² = ½Q²/C",
      },
      {
        id: "phys-2-s3t2-content-2",
        type: "info",
        content: "**Capacitors in Series and Parallel**\n\n**Capacitors in Series:**\n1/C_eq = 1/C₁ + 1/C₂ + 1/C₃ + ...\n\nThe equivalent capacitance is LESS than the smallest individual capacitance.\nCharge on each capacitor is the same.\nVoltage divides across capacitors.\n\n**Capacitors in Parallel:**\nC_eq = C₁ + C₂ + C₃ + ...\n\nThe equivalent capacitance is GREATER than the largest individual capacitance.\nVoltage across each capacitor is the same.\nCharge distributes proportionally to capacitance.\n\n**Worked Example:**\nA 2 µF and a 3 µF capacitor are connected in parallel. The combination is then connected in series with a 5 µF capacitor. Find the total capacitance.\n\nParallel combination: C_p = 2 + 3 = 5 µF\nSeries: 1/C_total = 1/5 + 1/5 = 2/5\nC_total = 2.5 µF",
      },
      {
        id: "phys-2-s3t2-content-3",
        type: "info",
        content: "**Dielectrics**\n\nA dielectric is an insulating material placed between the plates of a capacitor. It increases the capacitance by reducing the electric field strength for the same charge.\n\n**Dielectric Constant (εᵣ):**\nThe ratio of the capacitance with the dielectric to the capacitance without it.\nεᵣ = C/C₀\n\n| Material | Dielectric Constant (εᵣ) |\n|----------|------------------------|\n| Vacuum | 1.0000 |\n| Air | 1.0006 |\n| Paper | 3.7 |\n| Glass | 5–10 |\n| Water | 80 |\n| Ceramic | 100–1000 |\n\n**Why Dielectrics Increase Capacitance:**\n- Dielectric molecules polarise in the electric field.\n- The polarisation creates an internal field opposing the external field.\n- The net electric field between the plates is reduced.\n- For the same charge, a smaller field means a smaller voltage.\n- Since C = Q/V, a smaller V means larger C.\n\n**Applications of Capacitors:**\n- Smoothing power supply ripples.\n- Timing circuits (RC circuits).\n- Coupling and decoupling in audio circuits.\n- Energy storage in flash cameras and defibrillators.\n- Touch-sensitive screens.",
      },
      {
        id: "phys-2-s3t2-practice",
        type: "question",
        content: "Test your understanding of capacitors.",
        exercise: {
          question: "Two capacitors of 4 µF and 6 µF are connected in series. What is their equivalent capacitance?",
          options: [
            "10 µF",
            "2.4 µF",
            "24 µF",
            "0.42 µF"
          ],
          correctIndex: 1,
          explanation: "For series: 1/C_eq = 1/4 + 1/6 = 3/12 + 2/12 = 5/12, so C_eq = 12/5 = 2.4 µF."
        }
      },
    ],
  },

  // ═══ MODULE 4: PHOTOELECTRIC EFFECT AND RADIOACTIVITY ═══
  {
    id: "phys-2-s4t1",
    title: "The Photoelectric Effect",
    subject: "Physics",
    subjectIcon: "⚛️",
    programme: "Both",
    unitId: "physics",
    difficulty: 4,
    estimatedMinutes: 30,
    xpReward: 60,
    prerequisites: ["phys-2-s3t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "phys-2-s4t1-intro",
        type: "info",
        content: "**The Photoelectric Effect**\n\nThe photoelectric effect is the emission of electrons from a metal surface when electromagnetic radiation (light) of a sufficient frequency shines on it. This phenomenon provided crucial evidence for the quantum nature of light and won Albert Einstein the Nobel Prize in 1921.",
      },
      {
        id: "phys-2-s4t1-content-1",
        type: "info",
        content: "**Experimental Observations**\n\n**Key Experimental Facts:**\n1. For each metal, there is a minimum frequency (threshold frequency, f₀) below which no electrons are emitted, regardless of the light intensity.\n\n2. If the frequency is above the threshold, the maximum kinetic energy of the emitted electrons depends on the frequency of the light, NOT on its intensity.\n\n3. The number of emitted electrons (photocurrent) is proportional to the intensity of the light (for a given frequency above threshold).\n\n4. Electron emission is instantaneous — there is no time lag between illumination and emission.\n\n**Why Classical Physics Failed:**\nClassical wave theory predicted:\n- Electron emission at any frequency if intensity is high enough (wrong).\n- Higher intensity → more energy per electron (wrong).\n- Time delay before emission (wrong).\n\nThese contradictions led to Einstein's revolutionary explanation.",
      },
      {
        id: "phys-2-s4t1-content-2",
        type: "info",
        content: "**Einstein's Photon Model**\n\nEinstein proposed that light consists of discrete packets of energy called **photons**. Each photon has energy:\n\nE = hf\n\nWhere:\n- h = Planck's constant = 6.63 × 10⁻³⁴ J·s\n- f = frequency of light (Hz)\n\n**Einstein's Photoelectric Equation:**\n\nA photon gives all its energy to a single electron. The electron uses this energy to:\n1. Overcome the work function (escape the metal).\n2. The remaining energy becomes kinetic energy.\n\nhf = Φ + ½mv²_max\n\nWhere:\n- Φ (work function) = hf₀ = minimum energy needed to release an electron\n- f₀ = threshold frequency\n- ½mv²_max = maximum kinetic energy of the emitted electron\n\nRearranged:\n½mv²_max = hf − Φ = h(f − f₀)",
      },
      {
        id: "phys-2-s4t1-content-3",
        type: "info",
        content: "**Worked Examples and Applications**\n\n**Worked Example 1:**\nSodium has a work function of 2.3 eV. Calculate:\na) The threshold frequency for sodium.\nb) The maximum kinetic energy of electrons emitted by light of frequency 7.0 × 10¹⁴ Hz.\n\n(Planck's constant h = 6.63 × 10⁻³⁴ J·s, 1 eV = 1.6 × 10⁻¹⁹ J)\n\na) Φ = hf₀ → f₀ = Φ/h = (2.3 × 1.6 × 10⁻¹⁹)/(6.63 × 10⁻³⁴)\n= (3.68 × 10⁻¹⁹)/(6.63 × 10⁻³⁴) = 5.55 × 10¹⁴ Hz\n\nb) ½mv²_max = hf − Φ\n= (6.63 × 10⁻³⁴ × 7.0 × 10¹⁴) − 3.68 × 10⁻¹⁹\n= 4.64 × 10⁻¹⁹ − 3.68 × 10⁻¹⁹\n= 0.96 × 10⁻¹⁹ J = 0.6 eV\n\n**Applications of the Photoelectric Effect:**\n- **Solar panels (photovoltaic cells):** Convert light energy to electrical energy.\n- **Light sensors:** Automatic lighting controls, exposure meters in cameras.\n- **Photomultiplier tubes:** Detect very low light levels.\n- **Night vision devices.**\n\n**Wave-Particle Duality:**\n- Light exhibits wave-like properties (interference, diffraction).\n- Light exhibits particle-like properties (photoelectric effect).\n- This duality is a fundamental principle of quantum mechanics.",
      },
      {
        id: "phys-2-s4t1-practice",
        type: "question",
        content: "Test your understanding of the photoelectric effect.",
        exercise: {
          question: "The energy of a photon is proportional to:",
          options: [
            "The amplitude of the light wave",
            "The intensity of the light",
            "The frequency of the light",
            "The speed of the light"
          ],
          correctIndex: 2,
          explanation: "E = hf, so the energy of a photon is directly proportional to its frequency. Planck's constant (h) is the proportionality constant."
        }
      },
    ],
  },
  {
    id: "phys-2-s4t2",
    title: "Radioactivity and Half-Life",
    subject: "Physics",
    subjectIcon: "⚛️",
    programme: "Both",
    unitId: "physics",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["phys-2-s4t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "phys-2-s4t2-intro",
        type: "info",
        content: "**Radioactivity and Half-Life**\n\nRadioactivity is the spontaneous disintegration of unstable atomic nuclei, accompanied by the emission of radiation. Understanding radioactive decay is essential in medicine (radiotherapy, imaging), archaeology (carbon dating), and energy production (nuclear power).",
      },
      {
        id: "phys-2-s4t2-content-1",
        type: "info",
        content: "**Types of Radioactive Emissions**\n\n| Property | α (Alpha) | β (Beta) | γ (Gamma) |\n|----------|-----------|----------|-----------|\n| Nature | Helium nucleus (2p⁺, 2n⁰) | Fast-moving electron | High-energy photon |\n| Symbol | ⁴₂He | ⁰₋₁e | γ |\n| Charge | +2e | −e | 0 |\n| Mass | 6.64 × 10⁻²⁷ kg | 9.11 × 10⁻³¹ kg | 0 |\n| Speed | ~0.05c | ~0.9c | c |\n| Ionising power | Strong | Moderate | Weak |\n| Penetrating power | Low (paper) | Moderate (aluminium) | High (lead) |\n| Deflection in E/B fields | Slight | Large opposite direction | None |\n\n**Background Radiation:**\n- Natural sources: cosmic rays, rocks (radon gas), food, soil.\n- Artificial sources: medical X-rays, nuclear power, nuclear weapons testing.\n- Background radiation is always present at low levels.",
      },
      {
        id: "phys-2-s4t2-content-2",
        type: "info",
        content: "**Radioactive Decay Law**\n\nThe rate of radioactive decay is proportional to the number of undecayed nuclei present.\n\ndN/dt = −λN\n\nWhere:\n- N = number of undecayed nuclei\n- λ = decay constant (probability of decay per unit time)\n- t = time\n\n**Exponential Decay Equation:**\nN = N₀e⁻λᵗ\n\nWhere N₀ is the initial number of nuclei.\n\n**Half-Life (T₁/₂):**\nThe time taken for half of the radioactive nuclei to decay.\n\nT₁/₂ = ln(2)/λ = 0.693/λ\n\n**Worked Example:**\nA radioactive sample has an initial activity of 800 Bq and a half-life of 10 days. What is the activity after 30 days?\n\n30 days = 3 half-lives\nAfter 1 half-life: 400 Bq\nAfter 2 half-lives: 200 Bq\nAfter 3 half-lives: 100 Bq\n\nUsing formula: N = N₀(½)ᵗ/ᵀ = 800 × (½)³ = 800 × ⅛ = 100 Bq",
      },
      {
        id: "phys-2-s4t2-content-3",
        type: "info",
        content: "**Applications of Radioactivity**\n\n**Carbon-14 Dating:**\n- Carbon-14 has a half-life of 5730 years.\n- Living organisms absorb C-14 from the atmosphere at a constant rate.\n- When an organism dies, C-14 decays without replacement.\n- By measuring the remaining C-14, the age of organic materials can be determined.\n\n**Medical Applications:**\n- **Radiotherapy:** Gamma radiation destroys cancer cells.\n- **Medical imaging:** Radioactive tracers (technetium-99m) are used in PET scans.\n- **Sterilisation:** Gamma rays sterilise medical equipment.\n\n**Industrial Applications:**\n- **Thickness gauges:** Beta radiation measures the thickness of materials.\n- **Smoke detectors:** Americium-241 emits alpha particles that ionise air.\n- **Tracer studies:** Tracking fluid flow in pipes and underground water.\n\n**Nuclear Reactions:**\n\n**Nuclear Fission:** The splitting of a heavy nucleus into two lighter nuclei.\n₂₃₅U + ¹n → ¹⁴⁴Ba + ⁸⁹Kr + 3¹n + Energy\nUsed in nuclear power plants.\n\n**Nuclear Fusion:** The combining of light nuclei to form a heavier nucleus.\n²H + ³H → ⁴He + ¹n + Energy\nPowers the Sun and stars; being developed for clean energy on Earth.\n\n**Safety Precautions:**\n- Minimise exposure time.\n- Maximise distance from source.\n- Use shielding (lead, concrete).\n- Wear protective clothing and dosimeters.",
      },
      {
        id: "phys-2-s4t2-practice",
        type: "question",
        content: "Test your understanding of radioactivity.",
        exercise: {
          question: "If a radioactive sample has a half-life of 6 hours, what fraction of the original sample remains after 24 hours?",
          options: [
            "1/4",
            "1/8",
            "1/16",
            "1/2"
          ],
          correctIndex: 2,
          explanation: "24 hours = 4 half-lives. Fraction remaining = (½)⁴ = 1/16."
        }
      },
    ],
  },

  // ═══ MODULE 5: PROJECTILES, FRICTION, CIRCULAR MOTION ═══
  {
    id: "phys-2-s5t1",
    title: "Projectile Motion and Friction",
    subject: "Physics",
    subjectIcon: "⚛️",
    programme: "Both",
    unitId: "physics",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["phys-2-s4t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "phys-2-s5t1-intro",
        type: "info",
        content: "**Projectile Motion and Friction**\n\nProjectile motion describes the trajectory of an object launched into the air under the influence of gravity. Friction is a force that opposes relative motion between surfaces in contact. Both concepts are essential in engineering, sports, and transportation.",
      },
      {
        id: "phys-2-s5t1-content-1",
        type: "info",
        content: "**Projectile Motion**\n\nA projectile is an object moving through the air under the influence of gravity alone (ignoring air resistance).\n\n**Key Principles:**\n- Horizontal motion: constant velocity (no horizontal force).\n- Vertical motion: constant acceleration (g = 9.8 m/s² downward).\n- The two motions are independent.\n\n**Initial Velocity Components:**\nuₓ = u cos θ (horizontal)\nuᵧ = u sin θ (vertical)\n\nWhere u = initial speed, θ = launch angle.\n\n**Key Equations:**\n\n**Time of Flight (T):**\nT = 2u sin θ/g\n\n**Maximum Height (H):**\nH = u² sin²θ/2g\n\n**Horizontal Range (R):**\nR = u² sin 2θ/g\n\nMaximum range occurs at θ = 45° (sin 90° = 1).\nFor complementary angles (e.g., 30° and 60°), the range is the same.",
      },
      {
        id: "phys-2-s5t1-content-2",
        type: "info",
        content: "**Friction**\n\nFriction is a force that opposes relative motion or the tendency of such motion between surfaces in contact.\n\n**Types of Friction:**\n1. **Static friction (F_s):** Acts between surfaces at rest relative to each other. It prevents motion from starting.\n   - Maximum static friction: F_s_max = μ_sR\n\n2. **Kinetic (Dynamic) friction (F_k):** Acts between surfaces in relative motion.\n   - Kinetic friction: F_k = μ_kR\n   - μ_k < μ_s generally\n\nWhere μ = coefficient of friction, R = normal reaction force.\n\n**Coefficient of Friction (μ):**\nμ = F/R (dimensionless)\n\n| Surfaces | μ_s | μ_k |\n|----------|-----|-----|\n| Steel on steel | 0.74 | 0.57 |\n| Rubber on concrete | 1.0 | 0.8 |\n| Wood on wood | 0.6 | 0.4 |\n| Ice on ice | 0.1 | 0.03 |\n\n**Applications:**\n- Brakes and tyres need friction.\n- Lubricants reduce friction in engines.\n- Sand on icy roads increases friction.\n- Aerodynamic design reduces air friction (drag).",
      },
      {
        id: "phys-2-s5t1-content-3",
        type: "info",
        content: "**Worked Examples — Projectiles**\n\n**Example 1:** A ball is thrown with an initial velocity of 20 m/s at 30° to the horizontal. Find:\na) Maximum height.\nb) Time of flight.\nc) Range. (g = 10 m/s²)\n\nuₓ = 20 cos 30° = 20 × 0.866 = 17.32 m/s\nuᵧ = 20 sin 30° = 20 × 0.5 = 10 m/s\n\na) H = uᵧ²/2g = 10²/20 = 5 m\n\nb) T = 2uᵧ/g = 20/10 = 2 s\n\nc) R = uₓ × T = 17.32 × 2 = 34.64 m\n\n**Example 2:** A car of mass 1000 kg is on a horizontal road. The coefficient of static friction between tyres and road is 0.7. Calculate the maximum braking force.\n\nNormal reaction R = mg = 1000 × 9.8 = 9800 N\nMaximum braking force = F_s_max = μ_sR = 0.7 × 9800 = 6860 N\n\n**Factors Affecting Friction:**\n- Nature of surfaces (roughness, material).\n- Normal reaction force (not contact area).\n- Presence of lubricants.\n- Temperature (affects surface properties).",
      },
      {
        id: "phys-2-s5t1-practice",
        type: "question",
        content: "Test your understanding of projectiles.",
        exercise: {
          question: "At what launch angle does a projectile achieve maximum horizontal range (ignoring air resistance)?",
          options: [
            "30°",
            "45°",
            "60°",
            "90°"
          ],
          correctIndex: 1,
          explanation: "R = u² sin 2θ/g. Maximum range occurs when sin 2θ = 1, so 2θ = 90°, θ = 45°."
        }
      },
    ],
  },
  {
    id: "phys-2-s5t2",
    title: "Circular Motion and Centripetal Force",
    subject: "Physics",
    subjectIcon: "⚛️",
    programme: "Both",
    unitId: "physics",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["phys-2-s5t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "phys-2-s5t2-intro",
        type: "info",
        content: "**Circular Motion and Centripetal Force**\n\nCircular motion describes the movement of an object along a circular path. Even when the speed is constant, the velocity changes because the direction changes. This requires a force directed towards the centre — the centripetal force.",
      },
      {
        id: "phys-2-s5t2-content-1",
        type: "info",
        content: "**Angular Quantities**\n\n**Angular Displacement (θ):**\nThe angle swept by a radius vector as an object moves along a circular path.\nθ = s/r\nWhere s = arc length, r = radius.\nUnit: radian (rad). Full circle = 2π rad.\n\n**Angular Velocity (ω):**\nRate of change of angular displacement.\nω = θ/t = 2π/T = 2πf\n\nWhere:\n- T = period (time for one revolution)\n- f = frequency (number of revolutions per second)\n- ω is in rad/s\n\n**Relationship between Linear and Angular Velocity:**\nv = ωr\n\n**Angular Acceleration (α):**\nRate of change of angular velocity.\nα = ω/t = a/r\n\n**Centripetal Acceleration (a_c):**\nThe acceleration directed toward the centre of the circle.\na_c = v²/r = ω²r",
      },
      {
        id: "phys-2-s5t2-content-2",
        type: "info",
        content: "**Centripetal Force**\n\n**Newton's Second Law for Circular Motion:**\nFor an object moving in a circle, there must be a net force directed toward the centre.\n\nF_c = ma_c = mv²/r = mω²r\n\n**Examples of Centripetal Forces:**\n| Situation | Centripetal Force Provided By |\n|-----------|------------------------------|\n| Car turning on a flat road | Friction between tyres and road |\n| Car on a banked curve | Horizontal component of normal reaction |\n| Satellite in orbit | Gravitational force |\n| Object on a string | Tension in the string |\n| Electron orbiting nucleus | Electrostatic attraction |\n| Clothes in a spin dryer | Normal reaction from drum wall |\n\n**Worked Example:**\nA car of mass 1000 kg travels around a circular track of radius 50 m at 15 m/s. Calculate the centripetal force required.\n\nF_c = mv²/r = (1000 × 225)/50 = 225000/50 = 4500 N\n\nThis force must be provided by friction between the tyres and the road.",
      },
      {
        id: "phys-2-s5t2-content-3",
        type: "info",
        content: "**Applications of Circular Motion**\n\n**Banked Curves:**\nRoads and railway tracks are banked (tilted) on curves to reduce the reliance on friction.\n\nFor optimal banking (no friction required):\ntan θ = v²/rg\n\nWhere θ is the banking angle.\n\n**Vertical Circular Motion:**\nIn a vertical circle (e.g., a roller coaster loop), the speed varies. The apparent weight changes:\n- At top: mg + N = mv²/r\n- At bottom: N − mg = mv²/r\n\n**Centrifuges:**\n- Separate substances by density (e.g., separating blood components).\n- Operate based on \"centrifugal force\" (apparent outward force in a rotating frame).\n\n**Non-Uniform Circular Motion:**\nWhen the speed changes (e.g., a car speeding up around a curve), there are both centripetal and tangential acceleration components.\n\na_total = √(a_c² + a_t²)\n\n**Spin Dryers:**\nWater droplets leave the drum when the required centripetal force exceeds the adhesion force.\n\n**Artificial Satellites:**\nSatellites stay in orbit because gravity provides the exact centripetal force needed for circular (or elliptical) motion at that speed and altitude.",
      },
      {
        id: "phys-2-s5t2-practice",
        type: "question",
        content: "Test your understanding of circular motion.",
        exercise: {
          question: "What provides the centripetal force for a car turning on a flat road?",
          options: [
            "The car's engine",
            "Air resistance",
            "The normal reaction of the road",
            "Friction between the tyres and the road"
          ],
          correctIndex: 3,
          explanation: "On a flat road, friction between the tyres and the road provides the centripetal force needed for the car to turn. Without friction, the car would continue in a straight line."
        }
      },
    ],
  },

  // ═══ MODULE 6: ELECTROMAGNETISM ═══
  {
    id: "phys-2-s6t1",
    title: "Electromagnetic Devices and Force on Charged Particles",
    subject: "Physics",
    subjectIcon: "⚛️",
    programme: "Both",
    unitId: "physics",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["phys-2-s5t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "phys-2-s6t1-intro",
        type: "info",
        content: "**Electromagnetic Devices and Force on Charged Particles**\n\nElectromagnetism describes the interaction between electric currents and magnetic fields. This principle is used in countless devices — from electric motors and generators to mass spectrometers and particle accelerators.",
      },
      {
        id: "phys-2-s6t1-content-1",
        type: "info",
        content: "**Magnetic Fields and Current-Carrying Conductors**\n\nA current-carrying conductor produces a magnetic field around it. Conversely, a magnetic field exerts a force on a current-carrying conductor.\n\n**Force on a Current-Carrying Wire in a Magnetic Field:**\nF = BIL sin θ\n\nWhere:\n- F = force (N)\n- B = magnetic flux density (Tesla, T)\n- I = current (A)\n- L = length of conductor (m)\n- θ = angle between conductor and magnetic field\n\n**Fleming's Left-Hand Rule (Motor Rule):**\nThumb = Force (Motion)\nFirst finger = Field (North to South)\nSecond finger = Current (positive to negative)\n\nAll three are mutually perpendicular.\n\n**Electromagnetic Devices:**\n- **Relay:** A switch operated by an electromagnet. A small current activates the electromagnet, which closes a larger circuit.\n- **Solenoid:** A coil of wire that acts as a magnet when current flows.\n- **Electromagnet:** A solenoid with an iron core, producing a strong magnetic field.\n\n**Factors Affecting Electromagnet Strength:**\n- Number of turns in the coil (more turns = stronger).\n- Current (higher current = stronger).\n- Type of core material (iron core is best).",
      },
      {
        id: "phys-2-s6t1-content-2",
        type: "info",
        content: "**Force on a Moving Charged Particle in a Magnetic Field**\n\nWhen a charged particle moves through a magnetic field, it experiences a force (Lorentz force).\n\nF = qvB sin θ\n\nWhere:\n- q = charge of the particle (C)\n- v = velocity of the particle (m/s)\n- B = magnetic flux density (T)\n- θ = angle between velocity and field\n\n**Direction of Force:**\nUsing Fleming's Left-Hand Rule:\n- For a positive charge, the direction is perpendicular to both v and B.\n- For a negative charge, the force is in the opposite direction.\n\nThe force is always perpendicular to the velocity, so it does zero work — only the direction changes, not the speed.\n\n**Circular Path in a Uniform Field:**\nIf v ⟂ B, the particle moves in a circle.\n\nThe centripetal force is provided by the magnetic force:\nqvB = mv²/r\n\nRearranging: r = mv/qB\n\nThis shows:\n- Higher mass → larger radius.\n- Higher charge → smaller radius.\n- Higher speed → larger radius.\n- Stronger field → smaller radius.",
      },
      {
        id: "phys-2-s6t1-content-3",
        type: "info",
        content: "**Applications of Electromagnetic Forces**\n\n**The Cyclotron:**\nA particle accelerator that uses alternating electric fields and a constant magnetic field.\n- The magnetic field bends the particles into a spiral path.\n- The electric field accelerates them each half-turn.\n- Used to produce high-energy particles for medical treatments and research.\n\n**The Mass Spectrometer:**\n- Ions are accelerated by an electric field.\n- They enter a magnetic field where their paths are bent.\n- The radius of curvature depends on the mass-to-charge ratio (m/q).\n- Used to identify isotopes and chemical compounds.\n\n**Cathode Ray Tube (CRT):**\n- Electrons are emitted from a heated cathode.\n- Accelerated and focused by electric fields.\n- Deflected by magnetic fields to scan the screen.\n- Used in older televisions and oscilloscopes.\n\n**Applications of Electromagnetic Devices:**\n- **Electric motors:** Convert electrical energy to mechanical energy.\n- **Generators:** Convert mechanical energy to electrical energy.\n- **Transformers:** Change voltage levels in AC circuits.\n- **MRI scanners:** Use strong magnetic fields for medical imaging.\n- **Maglev trains:** Use electromagnets for levitation and propulsion.",
      },
      {
        id: "phys-2-s6t1-practice",
        type: "question",
        content: "Test your understanding of electromagnetism.",
        exercise: {
          question: "Fleming's Left-Hand Rule gives the direction of:",
          options: [
            "The induced current",
            "The magnetic field around a wire",
            "The force on a current-carrying conductor in a magnetic field",
            "The electric field"
          ],
          correctIndex: 2,
          explanation: "Fleming's Left-Hand Rule (thumb = force, first finger = field, second finger = current) gives the direction of the force (motion) on a current-carrying conductor in a magnetic field."
        }
      },
    ],
  },

  // ═══ MODULE 7: WAVES ═══
  {
    id: "phys-2-s7t1",
    title: "Wave Properties and Types",
    subject: "Physics",
    subjectIcon: "⚛️",
    programme: "Both",
    unitId: "physics",
    difficulty: 2,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["phys-2-s6t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "phys-2-s7t1-intro",
        type: "info",
        content: "**Wave Properties and Types**\n\nWaves are disturbances that transfer energy from one point to another without transferring matter. They are fundamental to our understanding of sound, light, and many other physical phenomena.",
      },
      {
        id: "phys-2-s7t1-content-1",
        type: "info",
        content: "**Types of Waves**\n\n**Mechanical Waves:**\n- Require a medium to travel through.\n- Examples: sound waves, water waves, seismic waves.\n- Cannot travel through a vacuum.\n\n**Electromagnetic Waves:**\n- Do not require a medium — can travel through a vacuum.\n- Examples: light, radio waves, X-rays.\n- All travel at 3.0 × 10⁸ m/s in a vacuum.\n\n**Transverse Waves:**\n- Particles vibrate perpendicular to the direction of wave propagation.\n- Examples: light, water waves, waves on a string.\n- Have crests and troughs.\n\n**Longitudinal Waves:**\n- Particles vibrate parallel to the direction of wave propagation.\n- Examples: sound waves, slinky spring compressions.\n- Have compressions (high pressure) and rarefactions (low pressure).",
      },
      {
        id: "phys-2-s7t1-content-2",
        type: "info",
        content: "**Wave Parameters**\n\n**Wavelength (λ):**\nThe distance between two consecutive points in phase (e.g., crest to crest).\nUnit: metres (m)\n\n**Frequency (f):**\nThe number of complete waves passing a point per second.\nUnit: hertz (Hz) = s⁻¹\n\n**Period (T):**\nThe time for one complete wave to pass.\nT = 1/f\n\n**Wave Speed (v):**\nv = fλ\n\n**Amplitude (A):**\nThe maximum displacement of a particle from its equilibrium position.\nRelated to the energy carried by the wave (E ∝ A²).\n\n**Wave Number (k):**\nk = 2π/λ\n\n**Angular Frequency (ω):**\nω = 2πf\n\n**Wave Equation:**\ny = A sin(kx − ωt) or y = A sin(2π(x/λ − ft))\n\n**Worked Example:**\nA wave has frequency 50 Hz and wavelength 0.2 m. Calculate its speed.\nv = fλ = 50 × 0.2 = 10 m/s",
      },
      {
        id: "phys-2-s7t1-content-3",
        type: "info",
        content: "**Wave Phenomena**\n\n**Reflection:**\n- Waves bounce off a surface.\n- Angle of incidence = Angle of reflection.\n- Echoes are reflected sound waves.\n\n**Refraction:**\n- Waves change direction when they change speed (entering a different medium).\n- Occurs because wave speed changes: v = fλ (f constant, so λ changes).\n- Light bends towards the normal when slowing down.\n\n**Diffraction:**\n- Waves spread out when passing through a gap or around an obstacle.\n- More noticeable when gap size ≈ wavelength.\n- Sound diffracts more than light (longer wavelength).\n\n**Interference:**\n- When two waves meet, they superpose (add together).\n- **Constructive interference:** Crest meets crest → larger amplitude.\n- **Destructive interference:** Crest meets trough → cancellation.\n\n**Standing Waves:**\n- Formed by interference of two waves travelling in opposite directions.\n- Fixed points (nodes) and points of maximum displacement (antinodes).\n- Important in musical instruments and resonant cavities.",
      },
      {
        id: "phys-2-s7t1-practice",
        type: "question",
        content: "Test your understanding of wave properties.",
        exercise: {
          question: "What is the speed of a wave with frequency 200 Hz and wavelength 1.5 m?",
          options: [
            "300 m/s",
            "133 m/s",
            "3000 m/s",
            "30 m/s"
          ],
          correctIndex: 0,
          explanation: "v = fλ = 200 × 1.5 = 300 m/s."
        }
      },
    ],
  },
  {
    id: "phys-2-s7t2",
    title: "Sound Waves and Resonance",
    subject: "Physics",
    subjectIcon: "⚛️",
    programme: "Both",
    unitId: "physics",
    difficulty: 2,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["phys-2-s7t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "phys-2-s7t2-intro",
        type: "info",
        content: "**Sound Waves and Resonance**\n\nSound is a longitudinal mechanical wave that requires a medium to travel. Resonance occurs when a system is driven at its natural frequency, causing large-amplitude oscillations. Understanding sound and resonance has practical applications in music, medicine, and engineering.",
      },
      {
        id: "phys-2-s7t2-content-1",
        type: "info",
        content: "**Nature of Sound Waves**\n\nSound waves are **longitudinal** — particles vibrate parallel to the direction of wave travel, creating compressions (high pressure) and rarefactions (low pressure).\n\n**Transmission of Sound:**\n- Sound requires a medium (solid, liquid, or gas).\n- Cannot travel through a vacuum.\n- Speed depends on the medium:\n  - Air (20°C): 343 m/s\n  - Water: ~1500 m/s\n  - Steel: ~5000 m/s\n- Sound travels fastest in solids (particles are closest together).\n\n**Frequency Ranges:**\n| Type | Frequency Range |\n|------|----------------|\n| Infrasonic | Below 20 Hz |\n| Audible (Audio) | 20 Hz – 20,000 Hz |\n| Ultrasonic | Above 20,000 Hz |\n\n**Loudness (Amplitude):**\n- Related to the amplitude of the sound wave.\n- Measured in decibels (dB).\n- A whisper: ~30 dB, Normal conversation: ~60 dB, Jet engine: ~120 dB.\n\n**Pitch (Frequency):**\n- Higher frequency = higher pitch.\n- A above middle C: 440 Hz.",
      },
      {
        id: "phys-2-s7t2-content-2",
        type: "info",
        content: "**Echoes and Applications of Sound**\n\n**Echo:**\nA reflected sound wave. The time delay between the original sound and the echo depends on the distance to the reflecting surface.\n\nd = vt/2\n\nWhere:\n- d = distance to the surface\n- v = speed of sound\n- t = time between sound and echo\n\n**Applications:**\n1. **Echo sounding / Sonar:** Ships use sound pulses to measure water depth and detect objects underwater.\n\n2. **Ultrasound scanning:** Medical imaging using high-frequency sound waves (2–18 MHz).\n\n3. **Ultrasonic cleaning:** High-frequency vibrations remove dirt from objects.\n\n4. **Animal communication:**\n   - Bats use echolocation (ultrasonic) to navigate and find prey.\n   - Dolphins and whales use sound for communication and navigation.\n\n5. **Non-destructive testing:** Detecting flaws in materials.\n\n**The Speed of Sound — Experimental Determination:**\nUsing a resonance tube and a tuning fork of known frequency:\nFirst resonance: L₁ = λ/4\nSecond resonance: L₂ = 3λ/4\nλ = 2(L₂ − L₁)\nv = fλ",
      },
      {
        id: "phys-2-s7t2-content-3",
        type: "info",
        content: "**Resonance**\n\nResonance occurs when a system is forced to vibrate at its **natural frequency**, resulting in a large-amplitude oscillation.\n\n**Key Features:**\n- Every object has one or more natural frequencies.\n- When driven at a natural frequency, energy transfer is maximised.\n- Amplitude grows until limited by damping or destruction.\n\n**Examples:**\n- **Pushing a swing:** Small pushes at the right time produce large swings.\n- **Musical instruments:** Soundboards resonate at the frequency of the strings.\n- **Glass breaking:** An opera singer shattering a glass by singing at its natural frequency.\n- **Tacoma Narrows Bridge (1940):** Wind caused resonant oscillations, destroying the bridge.\n\n**Resonance in Musical Instruments:**\n- **String instruments:** The body resonates at the string frequencies, amplifying the sound.\n- **Wind instruments:** The air column resonates at specific frequencies (harmonics).\n- **Percussion:** The instrument's body resonates when struck.\n\n**Harmonics:**\nA standing wave in a tube or string produces several modes of vibration:\n- **Fundamental (1st harmonic):** The lowest natural frequency.\n- **2nd harmonic:** Twice the fundamental frequency.\n- **Overtones:** All harmonics above the fundamental.\n\n**Damping:**\nReduction in amplitude over time due to energy dissipation (friction, air resistance).\n- Light damping: Gradual decrease in amplitude.\n- Heavy damping: Rapid decrease; system returns to equilibrium without oscillating.\n- Critical damping: Quickest return to equilibrium without oscillation.",
      },
      {
        id: "phys-2-s7t2-practice",
        type: "question",
        content: "Test your understanding of sound waves.",
        exercise: {
          question: "A ship sends a sonar pulse and receives the echo 2 seconds later. If the speed of sound in water is 1500 m/s, how deep is the water?",
          options: [
            "3000 m",
            "1500 m",
            "750 m",
            "375 m"
          ],
          correctIndex: 1,
          explanation: "d = vt/2 = (1500 × 2)/2 = 1500 m. The factor of 1/2 accounts for the pulse travelling to the bottom and back."
        }
      },
    ],
  },

  // ═══ MODULE 8: ELECTRIC FIELDS, MAGNETIC FIELDS AND ELECTRONICS ═══
  {
    id: "phys-2-s8t1",
    title: "Analogue and Digital Signals, Binary Numbers",
    subject: "Physics",
    subjectIcon: "⚛️",
    programme: "Both",
    unitId: "physics",
    difficulty: 2,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["phys-2-s7t2"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "phys-2-s8t1-intro",
        type: "info",
        content: "**Analogue and Digital Signals, Binary Numbers**\n\nElectronics deals with the control of electric current in circuits. Modern electronics uses both analogue and digital signals. Understanding binary numbers is essential for digital electronics, computing, and communication systems.",
      },
      {
        id: "phys-2-s8t1-content-1",
        type: "info",
        content: "**Analogue and Digital Signals**\n\n**Analogue Signals:**\n- Continuous signals that vary smoothly over time.\n- Can take any value within a range.\n- Examples: sound waves, temperature readings, voltage from a microphone.\n- Susceptible to noise and signal degradation.\n\n**Digital Signals:**\n- Discrete signals represented by binary digits (0 and 1).\n- Only two voltage levels: LOW (0 V) and HIGH (e.g., 5 V).\n- More resistant to noise.\n- Easier to store, process, and transmit.\n- Used in computers, smartphones, digital cameras.\n\n**Analogue-to-Digital Conversion (ADC):**\n1. **Sampling:** Measuring the analogue signal at regular intervals.\n2. **Quantisation:** Assigning each sample to the nearest discrete level.\n3. **Encoding:** Converting the quantised values to binary numbers.\n\n**Digital-to-Analogue Conversion (DAC):**\n1. Converting digital binary values back to voltage levels.\n2. **Reconstruction:** Creating a continuous signal from the discrete samples.\n3. **Filtering:** Smoothing the reconstructed signal.",
      },
      {
        id: "phys-2-s8t1-content-2",
        type: "info",
        content: "**Binary Number System**\n\n**Base-2 System:**\nBinary uses only two digits: 0 and 1.\nEach position represents a power of 2.\n\n**Place Values:**\n2ⁿ ... 2⁵ 2⁴ 2³ 2² 2¹ 2⁰\n... 32  16  8   4   2   1\n\n**Binary to Decimal Conversion:**\nMultiply each digit by its place value and sum.\n\nExample: 1101₂ = 1×8 + 1×4 + 0×2 + 1×1 = 8 + 4 + 0 + 1 = 13₁₀\n\n**Decimal to Binary Conversion:**\nRepeatedly divide by 2 and read remainders from bottom to top.\n\nExample: Convert 25₁₀ to binary.\n25 ÷ 2 = 12 remainder 1\n12 ÷ 2 = 6 remainder 0\n6 ÷ 2 = 3 remainder 0\n3 ÷ 2 = 1 remainder 1\n1 ÷ 2 = 0 remainder 1\nRead bottom to top: 11001₂\n\nCheck: 16 + 8 + 0 + 0 + 1 = 25 ✓\n\n**Binary Addition:**\n0 + 0 = 0\n0 + 1 = 1\n1 + 1 = 0 (carry 1)\n1 + 1 + 1 = 1 (carry 1)",
      },
      {
        id: "phys-2-s8t1-content-3",
        type: "info",
        content: "**7-Segment Displays**\n\nA 7-segment display consists of 7 LEDs arranged to form digits 0–9 and some letters.\n\n**Segments are labelled a–g:**\n```\n a\nf b\n g\ne c\n d\n```\n\nSo digit \"1\" lights segments b and c.\nDigit \"8\" lights all segments a–g.\n\n**Common Anode (CA):**\n- All anodes are connected to +V.\n- A segment lights when its cathode is connected to LOW (0 V).\n\n**Common Cathode (CC):**\n- All cathodes are connected to GND (0 V).\n- A segment lights when its anode is connected to HIGH (+V).\n\n**Applications:**\n- Digital clocks and watches.\n- Calculators and counters.\n- Instrument panels.\n- Electronic meters.\n\nThe display is controlled by a decoder IC (e.g., 74LS47) that converts a 4-bit binary input to the correct 7-segment pattern.",
      },
      {
        id: "phys-2-s8t1-practice",
        type: "question",
        content: "Test your understanding of binary numbers.",
        exercise: {
          question: "What is the decimal value of the binary number 10101?",
          options: [
            "17",
            "21",
            "25",
            "20"
          ],
          correctIndex: 1,
          explanation: "10101₂ = 1×16 + 0×8 + 1×4 + 0×2 + 1×1 = 16 + 4 + 1 = 21₁₀."
        }
      },
    ],
  },
  {
    id: "phys-2-s8t2",
    title: "Logic Gates and Boolean Algebra",
    subject: "Physics",
    subjectIcon: "⚛️",
    programme: "Both",
    unitId: "physics",
    difficulty: 3,
    estimatedMinutes: 25,
    xpReward: 50,
    prerequisites: ["phys-2-s8t1"],
    shsLevels: ["SHS 2"],
    suggestedLevel: "SHS 2",
    steps: [
      {
        id: "phys-2-s8t2-intro",
        type: "info",
        content: "**Logic Gates and Boolean Algebra**\n\nLogic gates are the fundamental building blocks of digital circuits. They perform Boolean operations on binary inputs to produce binary outputs. Boolean algebra provides the mathematical framework for designing and simplifying digital circuits.",
      },
      {
        id: "phys-2-s8t2-content-1",
        type: "info",
        content: "**Basic Logic Gates**\n\n**1. NOT Gate (Inverter):**\nInverts the input.\n| Input A | Output |\n|---------|--------|\n| 0 | 1 |\n| 1 | 0 |\n\nOutput = Ā or A'\n\n**2. AND Gate:**\nOutput is 1 only when ALL inputs are 1.\n| A | B | Output |\n|---|---|--------|\n| 0 | 0 | 0 |\n| 0 | 1 | 0 |\n| 1 | 0 | 0 |\n| 1 | 1 | 1 |\n\nOutput = A·B\n\n**3. OR Gate:**\nOutput is 1 when ANY input is 1.\n| A | B | Output |\n|---|---|--------|\n| 0 | 0 | 0 |\n| 0 | 1 | 1 |\n| 1 | 0 | 1 |\n| 1 | 1 | 1 |\n\nOutput = A + B\n\n**4. NAND Gate:**\nAND followed by NOT.\nOutput = (A·B)'\nEquivalent to: Output is 0 only when both inputs are 1.\n\n**5. NOR Gate:**\nOR followed by NOT.\nOutput = (A + B)'\nEquivalent to: Output is 1 only when both inputs are 0.\n\n**6. XOR Gate (Exclusive OR):**\nOutput is 1 when inputs are DIFFERENT.\nOutput = A ⊕ B\n\n| A | B | Output |\n|---|---|--------|\n| 0 | 0 | 0 |\n| 0 | 1 | 1 |\n| 1 | 0 | 1 |\n| 1 | 1 | 0 |",
      },
      {
        id: "phys-2-s8t2-content-2",
        type: "info",
        content: "**Boolean Algebra**\n\nBoolean algebra uses variables that can only be 0 or 1 (True/False), with operators AND (·), OR (+), and NOT (').\n\n**Basic Laws:**\n\n**Identities:**\n- A + 0 = A\n- A·1 = A\n- A + 1 = 1\n- A·0 = 0\n\n**Complement Laws:**\n- A + A' = 1\n- A·A' = 0\n- (A')' = A\n\n**Idempotent Laws:**\n- A + A = A\n- A·A = A\n\n**Commutative Laws:**\n- A + B = B + A\n- A·B = B·A\n\n**Associative Laws:**\n- A + (B + C) = (A + B) + C\n- A·(B·C) = (A·B)·C\n\n**Distributive Laws:**\n- A·(B + C) = A·B + A·C\n- A + (B·C) = (A + B)·(A + C)\n\n**De Morgan's Laws:**\n- (A·B)' = A' + B'\n- (A + B)' = A'·B'\n\nDe Morgan's Laws allow conversion between AND/OR operations with inverters, which is useful when certain gate types are preferred in circuit design.",
      },
      {
        id: "phys-2-s8t2-content-3",
        type: "info",
        content: "**Designing Logic Circuits**\n\n**From Truth Table to Boolean Expression:**\nIdentify rows where the output is 1. For each such row, write a product term (AND of inputs), then sum all product terms.\n\n**Example:** Design a circuit that outputs 1 when exactly one of two inputs is 1 (XOR gate).\n\n| A | B | Output |\n|---|---|--------|\n| 0 | 0 | 0 |\n| 0 | 1 | 1 |\n| 1 | 0 | 1 |\n| 1 | 1 | 0 |\n\nOutput = A'·B + A·B' (Sum of Products)\n\nThis is the XOR function: A ⊕ B.\n\n**Simplifying Boolean Expressions:**\nUse Boolean laws to minimise the expression, reducing the number of gates needed.\n\n**Example:** Simplify: A·B + A·B'\n= A·(B + B') (Distributive law)\n= A·1 (Complement law)\n= A (Identity law)\n\nSo A·B + A·B' = A — much simpler!\n\n**Applications of Logic Gates:**\n- **Adders:** Circuits that add binary numbers.\n- **Multiplexers:** Select one of several inputs.\n- **Flip-flops:** Memory elements that store one bit.\n- **Counters:** Sequential circuits that count pulses.\n- **Decoders:** Convert binary codes to output signals.\n\nLogic gates are the foundation of all digital electronics, from simple calculators to modern computers.",
      },
      {
        id: "phys-2-s8t2-practice",
        type: "question",
        content: "Test your understanding of logic gates.",
        exercise: {
          question: "The output of a NAND gate is 1 when:",
          options: [
            "Both inputs are 1",
            "Both inputs are 0",
            "At least one input is 0",
            "Both inputs are equal"
          ],
          correctIndex: 2,
          explanation: "NAND = NOT AND. An AND gate outputs 1 only when both inputs are 1. NAND inverts this, so NAND outputs 0 only when both inputs are 1, and outputs 1 when at least one input is 0."
        }
      },
    ],
  },
];

// ── Module count for reference ──────────────────────────────────────────────
export const PHYSICS_SHS2_COUNT = 8;
