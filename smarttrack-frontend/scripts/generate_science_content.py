#!/usr/bin/env python3
"""
generate_science_content.py
─────────────────────────────
Generates General Science Year 1 learning content from the Ministry of Education
LM-General-Science PDFs. Output is a TypeScript file that can be imported into
the Atlas learning system.

Usage:
    cd smarttrack-frontend && python scripts/generate_science_content.py
"""

import json
import os

# ── Session Structure ──────────────────────────────────────────────────────

SESSIONS = [
    {
        "id": "gen-sci-s1",
        "title": "Understanding Science — The Scientific Method",
        "difficulty": 1,
        "minutes": 12,
        "xp": 30,
        "icon": "🔬",
        "overview": "Science is a systematic way of understanding the natural world through observation, experimentation, and evidence-based reasoning. In this session, you will explore the core characteristics of science and learn how scientists approach problems.",
        "steps": [
            {
                "type": "info",
                "content": "What is Science?\n\nScience comes from the Latin word 'scientia', meaning knowledge. It is both:\n\n→ A body of knowledge about the natural world\n→ A process for discovering new knowledge\n\n**Core Characteristics of Science:**\n\n🔬 **Empirical** — Based on observation and data, not just opinion\n📊 **Systematic** — Follows an organised approach with clear steps\n🔄 **Reproducible** — Results can be repeated by other scientists\n📝 **Tentative** — Knowledge can change with new evidence\n🎯 **Predictable** — Can make accurate forecasts\n\nDid you know? The word 'science' wasn't always used. Before the 19th century, it was called 'natural philosophy'!",
            },
            {
                "type": "predict",
                "pattern": "Observation → Question → Hypothesis → Experiment → Analysis → Conclusion",
                "question": "What do you call this process that scientists follow?",
                "options": [
                    "The Scientific Method",
                    "The Laboratory Process",
                    "The Theory of Everything",
                    "The Natural Cycle",
                ],
                "correctIndex": 0,
                "explanation": "This is the **Scientific Method**! It's the systematic approach scientists use to investigate phenomena, acquire new knowledge, and solve problems.",
            },
            {
                "type": "info",
                "content": "**The Scientific Method — Step by Step**\n\n1️⃣ **Observation** — Notice something interesting (e.g., 'Plants grow towards sunlight')\n\n2️⃣ **Question** — Ask why or how it happens ('Why do plants grow towards light?')\n\n3️⃣ **Hypothesis** — Make an educated guess ('Plants grow towards light to maximise photosynthesis')\n\n4️⃣ **Experiment** — Design and conduct a test (Grow plants with light on one side only)\n\n5️⃣ **Analysis** — Examine your results (Measure and compare plant growth)\n\n6️⃣ **Conclusion** — Was your hypothesis supported? (Yes — plants do bend towards light!)\n\n> **SHS 1 Tip:** In WASSCE, you will often be asked to identify which step of the scientific method is being described in a scenario.",
            },
            {
                "type": "question",
                "question": "A student notices that salt dissolves faster in hot water than cold water. What is the FIRST step of the scientific method they should take?",
                "options": [
                    "Conduct an experiment",
                    "Make an observation",
                    "Draw a conclusion",
                    "Form a hypothesis",
                ],
                "correctIndex": 1,
                "explanation": "The first step is always **observation** — noticing that something is happening. In this case, the student has already observed that salt dissolves faster in hot water.",
            },
            {
                "type": "info",
                "content": "**Science in Everyday Life**\n\nScience is not just for laboratories — it's all around us!\n\n🏠 **At Home:** Cooking is chemistry! When you bake bread, yeast causes fermentation. When you fry an egg, proteins denature.\n\n🏥 **In Medicine:** Scientists developed COVID-19 vaccines using the scientific method — testing on thousands of volunteers to ensure safety.\n\n🌾 **In Agriculture:** Farmers test different fertilisers on crops to see which produces the best yield.\n\n🏭 **In Industry:** Engineers use scientific principles to design safer cars, cleaner energy, and faster computers.\n\n**Key Terms to Remember:**\n• **Hypothesis:** A testable prediction\n• **Variable:** Something that can change in an experiment\n• **Control:** A standard for comparison\n• **Theory:** A well-tested explanation for a wide range of observations",
            },
            {
                "type": "question",
                "question": "Which characteristic of science means that scientific knowledge can change when new evidence emerges?",
                "options": [
                    "Empirical",
                    "Tentative",
                    "Reproducible",
                    "Systematic",
                ],
                "correctIndex": 1,
                "explanation": "Science is **tentative** — meaning it is open to revision. That's why textbooks get updated! When new evidence challenges old ideas, science changes. This is a strength, not a weakness!",
            },
            {
                "type": "checkpoint",
                "title": "Scientific Method Mastery",
                "bonusXp": 15,
                "passThreshold": 2,
                "questions": [
                    {
                        "question": "What is a hypothesis?",
                        "options": [
                            "A proven fact",
                            "A testable prediction",
                            "The final conclusion",
                            "An observation",
                        ],
                        "correctIndex": 1,
                        "explanation": "A hypothesis is a testable prediction that can be supported or rejected through experimentation.",
                    },
                    {
                        "question": "Why is reproducibility important in science?",
                        "options": [
                            "It makes experiments faster",
                            "It confirms results are reliable",
                            "It saves money on equipment",
                            "It is only needed in chemistry",
                        ],
                        "correctIndex": 1,
                        "explanation": "Reproducibility ensures that results are reliable and not just a one-time accident. If other scientists can repeat the experiment and get the same results, the findings are trustworthy.",
                    },
                    {
                        "question": "Which step comes AFTER forming a hypothesis?",
                        "options": [
                            "Making observations",
                            "Drawing conclusions",
                            "Conducting an experiment",
                            "Asking a question",
                        ],
                        "correctIndex": 2,
                        "explanation": "After forming a hypothesis, the next step is to **conduct an experiment** to test whether the hypothesis is supported.",
                    },
                ],
            },
        ],
    },
    {
        "id": "gen-sci-s2",
        "title": "Exploring Materials — Metals, Non-metals and Bonding",
        "difficulty": 2,
        "minutes": 15,
        "xp": 35,
        "icon": "⚗️",
        "overview": "Everything around you is made of materials. In this session, you will discover how scientists classify solids into metals, non-metals, and semi-metals, explore the periodic table, and understand how atoms bond together to form compounds.",
        "steps": [
            {
                "type": "info",
                "content": "**Classifying Solids**\n\nAll solids can be classified into three main groups:\n\n**🥇 Metals** — Hard, shiny, good conductors of heat and electricity\n→ Examples: Iron (Fe), Copper (Cu), Gold (Au), Aluminium (Al)\n\n**💎 Non-metals** — Usually dull, brittle, poor conductors\n→ Examples: Oxygen (O), Carbon (C), Sulfur (S), Nitrogen (N)\n\n**🔶 Semi-metals (Metalloids)** — Have properties of both\n→ Examples: Silicon (Si), Germanium (Ge)\n\n**Properties of Metals:**\n• **Malleable** — Can be hammered into shape\n• **Ductile** — Can be drawn into wires\n• **Lustrous** — Shiny when polished\n• **Good conductors** — Heat and electricity flow easily\n\nDid you know? Mercury is the only metal that is liquid at room temperature!",
            },
            {
                "type": "predict",
                "pattern": "Gold → Shiny, Malleable, Conducts electricity\nSulfur → Dull, Brittle, Does not conduct\nSilicon → Somewhat shiny, Semi-conductor",
                "question": "Silicon is used in computer chips. What type of solid is it?",
                "options": [
                    "Metal",
                    "Non-metal",
                    "Semi-metal (Metalloid)",
                    "Alloy",
                ],
                "correctIndex": 2,
                "explanation": "Silicon is a **semi-metal (metalloid)**. It has some properties of metals (slight shine, can conduct electricity under certain conditions) and some of non-metals. This is why it's perfect for computer chips!",
            },
            {
                "type": "info",
                "content": "**The Periodic Table**\n\nThe periodic table organises all known elements.\n\n**Key features:**\n• **Groups** — Vertical columns (1-18). Elements in the same group have similar properties.\n• **Periods** — Horizontal rows (1-7). Elements in the same period have the same number of electron shells.\n\n**First 20 Elements — You Must Know These!**\n\nH (1) → Hydrogen    He (2) → Helium\nLi (3) → Lithium     Be (4) → Beryllium\nB (5) → Boron        C (6) → Carbon\nN (7) → Nitrogen     O (8) → Oxygen\nF (9) → Fluorine     Ne (10) → Neon\nNa (11) → Sodium     Mg (12) → Magnesium\nAl (13) → Aluminium  Si (14) → Silicon\nP (15) → Phosphorus  S (16) → Sulfur\nCl (17) → Chlorine   Ar (18) → Argon\nK (19) → Potassium   Ca (20) → Calcium\n\n> **Valence Electrons:** The electrons in the outermost shell. They determine how an element will react with others.",
            },
            {
                "type": "question",
                "question": "How many electrons does a neutral atom of Oxygen (O, atomic number 8) have?",
                "options": ["4", "6", "8", "16"],
                "correctIndex": 2,
                "explanation": "A neutral atom has the same number of electrons as protons. Oxygen has atomic number 8, so it has 8 protons and **8 electrons**. Its electron arrangement is 2,6.",
            },
            {
                "type": "info",
                "content": "**Chemical Bonding — How Atoms Combine**\n\n**🔗 Ionic Bonding** (Metal + Non-metal)\n• Electrons are **transferred** from metal to non-metal\n• Forms positive and negative ions that attract\n• Example: NaCl (Sodium Chloride — table salt!)\n→ Sodium gives 1 electron to Chlorine\n\n**🔗 Covalent Bonding** (Non-metal + Non-metal)\n• Electrons are **shared** between atoms\n• Forms molecules\n• Example: H₂O (Water)\n→ Oxygen shares electrons with 2 Hydrogen atoms\n\n**How to Name Binary Compounds:**\n• Metal + Non-metal → 'ide' ending\n• NaCl = Sodium Chloride\n• MgO = Magnesium Oxide\n• CaCl₂ = Calcium Chloride\n\n**WASSCE Tip:** The 'ide' ending tells you the compound has only TWO elements!",
            },
            {
                "type": "question",
                "question": "What type of bond forms between Sodium (a metal) and Chlorine (a non-metal)?",
                "options": [
                    "Covalent bond",
                    "Ionic bond",
                    "Metallic bond",
                    "Hydrogen bond",
                ],
                "correctIndex": 1,
                "explanation": "When a **metal** (Sodium) bonds with a **non-metal** (Chlorine), they form an **ionic bond**. Sodium transfers its valence electron to Chlorine, creating positive Na⁺ and negative Cl⁻ ions that attract each other.",
            },
            {
                "type": "checkpoint",
                "title": "Materials Mastery",
                "bonusXp": 15,
                "passThreshold": 2,
                "questions": [
                    {
                        "question": "Which of these is a property of metals?",
                        "options": ["Brittle", "Malleable", "Dull", "Poor conductor"],
                        "correctIndex": 1,
                        "explanation": "Metals are **malleable** (can be hammered into shape), ductile, lustrous, and good conductors of heat and electricity.",
                    },
                    {
                        "question": "How many valence electrons does Carbon (C, atomic number 6) have?",
                        "options": ["2", "4", "6", "8"],
                        "correctIndex": 1,
                        "explanation": "Carbon has electron arrangement 2,4. So it has **4 valence electrons** in its outermost shell. This is why carbon can form 4 bonds — it's the basis of organic chemistry!",
                    },
                    {
                        "question": "What is the correct name for the compound MgO?",
                        "options": [
                            "Magnesium Oxygen",
                            "Magnesium Oxide",
                            "Magnesium Dioxide",
                            "Magnesium(I) Oxide",
                        ],
                        "correctIndex": 1,
                        "explanation": "Mg is Magnesium, O is Oxygen. Since it has two elements, the name ends in 'ide' — **Magnesium Oxide**.",
                    },
                ],
            },
        ],
    },
    {
        "id": "gen-sci-s3",
        "title": "Diffusion and Osmosis — Movement of Particles",
        "difficulty": 2,
        "minutes": 12,
        "xp": 30,
        "icon": "💧",
        "overview": "Why does the smell of perfume spread across a room? How do plants drink water from the soil? The answers lie in two important processes: diffusion and osmosis. Let's explore how particles move!",
        "steps": [
            {
                "type": "info",
                "content": "**Diffusion — Particles on the Move**\n\nDiffusion is the movement of particles from an area of **high concentration** to an area of **low concentration**.\n\n→ Particles spread out until they are evenly distributed\n→ It happens in liquids and gases\n→ NO energy is needed (it's passive)\n\n**Real-life Examples:**\n• 🌸 Perfume spreading across a room\n• 🫖 Tea bag colouring water\n• 🍳 Smell of cooking food reaching your nose\n• 💨 Oxygen moving from lungs into blood\n\n**Factors that affect diffusion rate:**\n• Temperature ↑ → Diffusion faster\n• Concentration difference ↑ → Diffusion faster\n• Particle size ↓ → Diffusion faster\n• Medium — Gas diffuses faster than liquid\n\nDid you know? Diffusion in gases is about 10,000 times faster than in liquids!",
            },
            {
                "type": "predict",
                "pattern": "A drop of blue ink is placed in a glass of water.\nAfter 1 minute: Blue colour near the drop\nAfter 10 minutes: Blue colour spreading\nAfter 1 hour: Water is evenly light blue",
                "question": "What process is causing the ink to spread?",
                "options": [
                    "Osmosis",
                    "Active transport",
                    "Diffusion",
                    "Evaporation",
                ],
                "correctIndex": 2,
                "explanation": "This is **diffusion**! The ink particles move from an area of high concentration (near the drop) to areas of low concentration (the rest of the water) until they are evenly distributed.",
            },
            {
                "type": "info",
                "content": "**Osmosis — Water's Special Journey**\n\nOsmosis is a **special type of diffusion** — it's the movement of **water molecules** across a **selectively permeable membrane**.\n\n🔑 **Key points:**\n• Only WATER molecules move\n• Water moves from **dilute** (more water) to **concentrated** (less water)\n• The membrane lets water through but blocks larger solute particles\n\n**🌱 In Plants:**\n• Root hairs absorb water from soil by osmosis\n• Water moves up the plant through xylem vessels\n• This is how plants stay hydrated and transport nutrients!\n\n**🧂 In Food Preservation:**\n• Salt draws water out of bacteria (osmosis!) — killing them\n• This is why salted fish and pickled vegetables last longer\n\n**Important Terms:**\n• **Selectively permeable membrane** — Only lets some substances through\n• **Dilute solution** — Has more water, less solute\n• **Concentrated solution** — Has less water, more solute",
            },
            {
                "type": "question",
                "question": "A potato strip is placed in salt water. After 30 minutes, it becomes soft and shrinks. What happened?",
                "options": [
                    "Salt entered the potato by diffusion",
                    "Water left the potato by osmosis",
                    "The salt dissolved the potato",
                    "Air entered the potato cells",
                ],
                "correctIndex": 1,
                "explanation": "Water moved **out** of the potato cells by **osmosis**! The salt water outside is more concentrated (less water), so water from inside the potato moves out through the cell membrane, causing the potato to shrink and become soft.",
            },
            {
                "type": "info",
                "content": "**Active Transport — Moving Against the Flow**\n\nSometimes cells need to move substances from **low to high concentration** (the opposite of diffusion). This is called **active transport**.\n\n⚡ **Requires ENERGY** (ATP)\n⛰️ **Moves against the concentration gradient**\n\n**Examples in living things:**\n• 🌱 Plant roots absorbing mineral ions from soil (soil has few, roots need many!)\n• 🫁 Kidney cells reabsorbing useful substances from urine back into blood\n\n**Comparison Summary:**\n\n| Process | Direction | Needs Energy? | Membrane? |\n|---------|-----------|--------------|-----------|\n| Diffusion | High → Low | No | Not needed |\n| Osmosis | High water → Low water | No | Yes |\n| Active Transport | Low → High | Yes | Yes |\n\n> **SHS 1 Tip:** WASSCE often asks you to compare these three processes!",
            },
            {
                "type": "question",
                "question": "What is the MAIN difference between osmosis and active transport?",
                "options": [
                    "Osmosis needs energy, active transport does not",
                    "Osmosis is only in plants, active transport is only in animals",
                    "Osmosis is passive (no energy), active transport requires energy",
                    "There is no difference — they are the same process",
                ],
                "correctIndex": 2,
                "explanation": "**Osmosis** is a passive process (no energy needed) where water moves across a membrane. **Active transport** requires energy (ATP) to move substances against the concentration gradient — from low to high concentration.",
            },
            {
                "type": "checkpoint",
                "title": "Diffusion & Osmosis Mastery",
                "bonusXp": 15,
                "passThreshold": 2,
                "questions": [
                    {
                        "question": "Which factor INCREASES the rate of diffusion?",
                        "options": [
                            "Lower temperature",
                            "Larger particle size",
                            "Higher temperature",
                            "Solid medium",
                        ],
                        "correctIndex": 2,
                        "explanation": "Higher temperature gives particles more energy, making them move faster — this **increases** the rate of diffusion!",
                    },
                    {
                        "question": "A selectively permeable membrane allows:",
                        "options": [
                            "Only water to pass through",
                            "All substances to pass through",
                            "Only some substances to pass through",
                            "No substances to pass through",
                        ],
                        "correctIndex": 2,
                        "explanation": "A **selectively permeable** membrane allows **only some substances** to pass through while blocking others. For example, it lets water through but not large solute molecules.",
                    },
                    {
                        "question": "Plant roots absorb water from soil by which process?",
                        "options": [
                            "Active transport",
                            "Diffusion",
                            "Osmosis",
                            "Transpiration",
                        ],
                        "correctIndex": 2,
                        "explanation": "Plant roots absorb water from soil by **osmosis**. The soil water is more dilute (has more water) than the root cell sap, so water moves into the roots.",
                    },
                ],
            },
        ],
    },
    {
        "id": "gen-sci-s4",
        "title": "Reproduction in Plants and Humans",
        "difficulty": 2,
        "minutes": 15,
        "xp": 35,
        "icon": "🌱",
        "overview": "Life continues because living things reproduce. In this session, you will explore how plants reproduce through flowers and seeds, how humans reproduce, and the amazing ways life passes from one generation to the next.",
        "steps": [
            {
                "type": "info",
                "content": "**Reproduction in Plants**\n\nPlants can reproduce in TWO ways:\n\n**🌸 Sexual Reproduction** — Involves flowers\n→ Male part (stamen) produces pollen\n→ Female part (carpel/pistil) contains ovules\n→ Pollination + Fertilisation → Seed + Fruit\n\n**🌿 Asexual Reproduction (Vegetative Propagation)** — No flowers needed!\n• **Runners** — Strawberry plants send out horizontal stems\n• **Rhizomes** — Ginger grows underground stems\n• **Bulbs** — Onions and garlic store food in underground leaves\n• **Tubers** — Potatoes grow from underground stems\n\n**Artificial Propagation (Humans helping):**\n✂️ **Cuttings** — Cut a stem, plant it, it grows roots\n🌳 **Grafting** — Join one plant to another\n🧪 **Tissue culture** — Grow new plants from tiny tissue samples\n\nDid you know? A single potato tuber can produce dozens of new potato plants!",
            },
            {
                "type": "predict",
                "pattern": "Flower → Pollination → Fertilisation → Seed → Germination → New Plant",
                "question": "What is missing from this plant life cycle?",
                "options": [
                    "Photosynthesis",
                    "Fruit formation",
                    "Respiration",
                    "Transpiration",
                ],
                "correctIndex": 1,
                "explanation": "After fertilisation, the ovary develops into a **fruit** that protects the seeds and helps with dispersal. So the cycle is: Flower → Pollination → Fertilisation → **Fruit** → Seed → Germination → New Plant.",
            },
            {
                "type": "info",
                "content": "**Pollination — The Journey of Pollen**\n\nPollination is the transfer of pollen from the **stamen** (male) to the **stigma** (female).\n\n**🐝 Insect-pollinated flowers:**\n• Large, colourful petals\n• Sweet scent and nectar\n• Sticky pollen (attaches to insects)\n• Examples: Rose, Sunflower, Orchid\n\n**🌬️ Wind-pollinated flowers:**\n• Small, dull petals\n• No scent or nectar\n• Light, smooth pollen (blown by wind)\n• Examples: Grass, Maize, Wheat\n\n**After pollination:**\n• Pollen tube grows down the style\n• Male nucleus meets female nucleus → **Fertilisation**\n• Ovule becomes **seed**, ovary becomes **fruit**\n\n**Seed Dispersal:**\n🌬️ Wind — Dandelion, Maple\n🐦 Animals — Berries eaten and seeds passed out\n💥 Explosive — Touch-me-not plant shoots seeds\n🌊 Water — Coconut floats to new islands",
            },
            {
                "type": "question",
                "question": "A flower has large, brightly coloured petals and produces nectar. How is it most likely pollinated?",
                "options": [
                    "By wind",
                    "By insects",
                    "By water",
                    "By self-pollination",
                ],
                "correctIndex": 1,
                "explanation": "Large, brightly coloured petals and nectar are signs of an **insect-pollinated** flower. The bright colours attract insects like bees, and the nectar rewards them for visiting.",
            },
            {
                "type": "info",
                "content": "**Reproduction in Humans**\n\nHumans reproduce **sexually** — this means a male sex cell (sperm) must fuse with a female sex cell (egg/ovum).\n\n**👨 Male Reproductive System:**\n• **Testes** — Produce sperm and testosterone\n• **Sperm duct** — Carries sperm\n• **Penis** — Delivers sperm\n\n**👩 Female Reproductive System:**\n• **Ovaries** — Produce eggs (ova) and hormones\n• **Fallopian tubes** — Where fertilisation happens\n• **Uterus (womb)** — Where baby grows\n• **Vagina** — Birth canal\n\n**The Menstrual Cycle (~28 days):**\n📅 Day 1-5: Menstruation (period)\n📅 Day 6-13: Uterus lining rebuilds\n📅 Day 14: **Ovulation** — egg released\n📅 Day 15-28: Uterus ready for pregnancy\n\n**Fertilisation:**\n• Sperm meets egg in the fallopian tube\n• One sperm penetrates the egg\n• Fertilised egg travels to uterus\n• Embryo implants in uterus lining\n• Baby develops over 9 months (40 weeks)",
            },
            {
                "type": "question",
                "question": "Where does fertilisation typically occur in humans?",
                "options": [
                    "In the ovary",
                    "In the uterus",
                    "In the fallopian tube",
                    "In the vagina",
                ],
                "correctIndex": 2,
                "explanation": "Fertilisation typically occurs in the **fallopian tube**. The sperm swim up from the vagina, through the uterus, and meet the egg in the fallopian tube. The fertilised egg then travels to the uterus to implant and grow.",
            },
            {
                "type": "checkpoint",
                "title": "Reproduction Mastery",
                "bonusXp": 15,
                "passThreshold": 2,
                "questions": [
                    {
                        "question": "What is the male part of a flower called?",
                        "options": ["Carpel", "Stamen", "Ovary", "Petal"],
                        "correctIndex": 1,
                        "explanation": "The **stamen** is the male reproductive part of a flower. It consists of the anther (produces pollen) and filament (supports the anther).",
                    },
                    {
                        "question": "Which form of reproduction does NOT require seeds or flowers?",
                        "options": [
                            "Sexual reproduction",
                            "Pollination",
                            "Vegetative propagation",
                            "Fertilisation",
                        ],
                        "correctIndex": 2,
                        "explanation": "**Vegetative propagation** (asexual reproduction) does not require seeds or flowers. New plants grow from runners, bulbs, tubers, or cuttings.",
                    },
                    {
                        "question": "During the menstrual cycle, ovulation occurs around day:",
                        "options": ["5", "14", "21", "28"],
                        "correctIndex": 1,
                        "explanation": "**Ovulation** typically occurs around **day 14** of a 28-day menstrual cycle. This is when a mature egg is released from the ovary.",
                    },
                ],
            },
        ],
    },
    {
        "id": "gen-sci-s5",
        "title": "Solar Panels — Harnessing the Sun's Energy",
        "difficulty": 2,
        "minutes": 12,
        "xp": 30,
        "icon": "☀️",
        "overview": "The sun provides more energy in one hour than the entire world uses in a year! In this session, you will discover how solar panels capture this energy and convert it into electricity — and learn why Ghana is investing in solar power.",
        "steps": [
            {
                "type": "info",
                "content": "**What is Solar Energy?**\n\nSolar panels are devices that convert **sunlight directly into electricity** using a process called the **photovoltaic effect**.\n\n**How does a solar panel work?**\n\n☀️ Sunlight hits the panel (made of silicon semiconductors)\n⚡ Photons from sunlight knock electrons loose\n🔀 Electrons flow through the material -> ELECTRICITY!\n🔌 Wires carry this electricity to power your home\n\n**Key Components:**\n• **Solar cells** — The individual units that generate electricity\n• **Solar panel** — A collection of solar cells\n• **Solar array** — Multiple panels working together\n• **Inverter** — Converts DC to AC (what your home uses)\n• **Battery** — Stores excess energy for night-time use\n\nDid you know? The first solar cell was invented in 1954 at Bell Labs and could only power a small radio!",
            },
            {
                "type": "predict",
                "pattern": "Ghana has abundant sunshine (4.5-5.5 kWh/m²/day)\nMany rural areas lack grid electricity\nSolar panel prices have dropped 80% in 10 years",
                "question": "Why is solar energy a good choice for Ghana?",
                "options": [
                    "Ghana has limited sunshine",
                    "Solar panels are very cheap",
                    "Ghana has abundant sunshine and many areas need electricity",
                    "Solar panels work better in cloudy weather",
                ],
                "correctIndex": 2,
                "explanation": "Ghana has **abundant sunshine** and many rural areas do not have access to the national electricity grid. Solar panels can be installed anywhere the sun shines, making them perfect for bringing electricity to remote communities!",
            },
            {
                "type": "info",
                "content": "**Solar Energy in Ghana — Real Projects**\n\n**🏗️ Pokuase Community Solar Project**\n• Brings solar power to under-served communities\n• Provides reliable electricity for homes and small businesses\n• Reduces dependence on the national grid\n\n**🏗️ Bui Solar Energy Project**\n• One of the largest solar projects in West Africa\n• 250 MW capacity (enough for thousands of homes!)\n• Hybrid system — combines solar with Bui Hydroelectric Dam\n• Water from the dam can be used when the sun isn't shining\n\n**💡 Solar vs. Fossil Fuels:**\n\n| Solar Energy | Fossil Fuels |\n|-------------|-------------|\n| ☀️ Renewable (never runs out) | 🪨 Non-renewable (will run out) |\n| 🌱 Clean (no pollution) | 💨 Pollutes the air |\n| 🏠 Can be installed anywhere | 🏭 Needs big power plants |\n| 💰 Free after installation | 💸 Continuous fuel cost |\n\n> **Environmental Impact:** Switching to solar reduces greenhouse gas emissions and helps fight climate change!",
            },
            {
                "type": "question",
                "question": "What device converts the DC electricity from solar panels into AC electricity for home use?",
                "options": [
                    "Solar cell",
                    "Battery",
                    "Inverter",
                    "Transformer",
                ],
                "correctIndex": 2,
                "explanation": "An **inverter** converts the direct current (DC) electricity produced by solar panels into alternating current (AC) electricity that can be used by home appliances and the electrical grid.",
            },
            {
                "type": "info",
                "content": "**Factors Affecting Solar Panel Performance**\n\n**☀️ Sunlight intensity** — More sunlight = more electricity\n• Panels work best in direct sunlight\n• Cloudy days reduce output by 50-90%\n\n**🌡️ Temperature** — Surprisingly, cooler is better!\n• Solar panels lose efficiency when very hot\n• Optimal temperature is about 25°C\n\n**📐 Tilt and orientation** — Panels should face the sun\n• In Ghana, panels face south (we're in the northern hemisphere!)\n• Tilt angle should match your latitude\n\n**🧹 Cleanliness** — Dust reduces output\n• Dust can reduce efficiency by up to 25%\n• Regular cleaning is essential, especially in dry seasons\n\n**Economic Benefits for Ghana:**\n• 💼 Creates jobs in installation and maintenance\n• 💰 Reduces electricity bills for homes and businesses\n• 🌍 Reduces carbon emissions\n• 🔋 Energy independence — less reliance on imported fuels",
            },
            {
                "type": "question",
                "question": "What happens to solar panel efficiency when the temperature gets very high?",
                "options": [
                    "It increases",
                    "It decreases",
                    "It stays the same",
                    "It doubles",
                ],
                "correctIndex": 1,
                "explanation": "Solar panel efficiency **decreases** at high temperatures! Although sunlight is needed, panels work best at around 25°C. High temperatures cause the electrons to move more erratically, reducing the voltage output.",
            },
            {
                "type": "checkpoint",
                "title": "Solar Energy Mastery",
                "bonusXp": 15,
                "passThreshold": 2,
                "questions": [
                    {
                        "question": "What material is commonly used in solar cells to convert sunlight to electricity?",
                        "options": ["Copper", "Aluminium", "Silicon", "Iron"],
                        "correctIndex": 2,
                        "explanation": "**Silicon** is the most common semiconductor used in solar cells. It's abundant (found in sand!) and has the right properties for the photovoltaic effect.",
                    },
                    {
                        "question": "Why is solar energy considered a renewable resource?",
                        "options": [
                            "It is cheap",
                            "The sun will keep shining for billions of years",
                            "It does not pollute",
                            "It can be stored in batteries",
                        ],
                        "correctIndex": 1,
                        "explanation": "Solar energy is **renewable** because the sun will continue to produce energy for billions of years. Unlike fossil fuels, we will never 'run out' of sunlight.",
                    },
                    {
                        "question": "Which Ghanaian project combines solar power with a hydroelectric dam?",
                        "options": [
                            "Pokuase Solar Project",
                            "Akosombo Dam",
                            "Bui Solar Energy Project",
                            "Tema Solar Farm",
                        ],
                        "correctIndex": 2,
                        "explanation": "The **Bui Solar Energy Project** is a hybrid system that combines solar power with the Bui Hydroelectric Dam. This way, electricity can be generated both from the sun and from water.",
                    },
                ],
            },
        ],
    },
    {
        "id": "gen-sci-s6",
        "title": "Force — Pushes and Pulls in the Physical World",
        "difficulty": 2,
        "minutes": 12,
        "xp": 35,
        "icon": "💪",
        "overview": "Everything that moves — from a falling leaf to a rocket launching into space — is affected by forces. In this session, you will discover what forces are, how they affect motion, and why understanding forces is essential in science.",
        "steps": [
            {
                "type": "info",
                "content": "**What is a Force?**\n\nA force is a **push or pull** that can change an object's motion or shape.\n\n→ Forces are measured in **Newtons (N)**\n→ They are **vector quantities** (have magnitude AND direction)\n\n**Types of Forces:**\n\n💪 **Contact Forces** — Objects must touch\n• **Friction** — Resistance when surfaces rub together\n• **Tension** — Pulling force in a rope/string\n• **Air resistance** — Friction with air molecules\n• **Normal reaction** — Surface pushing up against an object\n\n🌌 **Non-contact Forces** — Objects don't need to touch\n• **Gravity** — Attraction between objects with mass\n• **Magnetism** — Attraction/repulsion between magnets\n• **Electrostatic** — Force between charged objects\n\nDid you know? You are currently experiencing a force of about 700 N pulling you towards the Earth (gravity)!",
            },
            {
                "type": "predict",
                "pattern": "A ball is kicked on grass → It slows down and stops\nA ball is kicked on ice → It slides much further\nA ball is kicked in space → It keeps going forever",
                "question": "What force causes the ball to slow down on grass?",
                "options": [
                    "Gravity",
                    "Friction",
                    "Magnetism",
                    "Air resistance",
                ],
                "correctIndex": 1,
                "explanation": "**Friction** between the ball and the grass causes it to slow down. On ice, there is less friction, so the ball travels further. In space, there is no friction at all — so the ball would keep moving forever!",
            },
            {
                "type": "info",
                "content": "**Friction — Helpful or Harmful?**\n\n**✅ Advantages of Friction:**\n• 🚶 Allows us to walk without slipping\n• ✍️ Lets us write on paper\n• 🚗 Car brakes use friction to stop\n• 🪵 Matches light due to friction\n\n**❌ Disadvantages of Friction:**\n• 🔥 Causes wear and tear on machines\n• 🌡️ Produces heat (engines can overheat)\n• ⚡ Wastes energy (need more fuel)\n\n**Reducing Friction:**\n• 🛢️ Lubricants (oil, grease)\n• 🛞 Ball bearings (rolling instead of sliding)\n• ✈️ Streamlining (reducing air resistance)\n\n**Gravity — The Universal Force**\n\n• Every object with mass attracts every other object\n• Earth's gravity pulls everything towards its centre\n• Gravity gives us **weight** (mass × gravity = weight)\n• On the Moon, gravity is 1/6 of Earth's\n\n> **Formula:** Weight (N) = Mass (kg) × Gravitational field strength (N/kg)\n> On Earth: g = 9.8 N/kg (or approximately 10 N/kg)",
            },
            {
                "type": "question",
                "question": "A student has a mass of 50 kg. What is their weight on Earth? (Use g = 10 N/kg)",
                "options": [
                    "5 N",
                    "50 N",
                    "500 N",
                    "5000 N",
                ],
                "correctIndex": 2,
                "explanation": "Weight = mass × gravity = 50 kg × 10 N/kg = **500 N**.\n\nNotice that weight and mass are DIFFERENT! Mass is how much matter you contain (always 50 kg), while weight is the force of gravity on you (changes with gravity).",
            },
            {
                "type": "info",
                "content": "**Speed, Velocity and Acceleration**\n\n**Speed** — How fast something is moving (scalar)\n→ Speed = Distance / Time\n→ Units: m/s or km/h\n\n**Velocity** — Speed in a given direction (vector)\n→ Same formula as speed, but includes direction\n→ Example: '20 m/s due North'\n\n**Acceleration** — How quickly velocity changes\n→ Acceleration = Change in velocity / Time taken\n→ Units: m/s²\n\n**Newton's Second Law:**\n\n> **Force = Mass × Acceleration (F = ma)**\n\nThis means:\n• Heavier objects need MORE force to accelerate\n• More force = faster acceleration\n• More mass = slower acceleration (with same force)\n\n**Example:** If you push a shopping cart with 10 N of force and it has a mass of 5 kg:\na = F/m = 10/5 = 2 m/s²",
            },
            {
                "type": "question",
                "question": "A car accelerates from rest to 20 m/s in 5 seconds. What is its acceleration?",
                "options": [
                    "4 m/s²",
                    "10 m/s²",
                    "100 m/s²",
                    "0.25 m/s²",
                ],
                "correctIndex": 0,
                "explanation": "Acceleration = Change in velocity / Time = (20 - 0) / 5 = **4 m/s²**.\n\nThis means the car's velocity increases by 4 m/s every second!",
            },
            {
                "type": "checkpoint",
                "title": "Force Mastery",
                "bonusXp": 15,
                "passThreshold": 2,
                "questions": [
                    {
                        "question": "What type of force is gravity?",
                        "options": [
                            "Contact force",
                            "Non-contact force",
                            "Frictional force",
                            "Elastic force",
                        ],
                        "correctIndex": 1,
                        "explanation": "Gravity is a **non-contact force** — objects don't need to be touching to experience it. The Earth's gravity reaches across space to keep the Moon in orbit!",
                    },
                    {
                        "question": "What unit is force measured in?",
                        "options": ["Kilograms", "Newtons", "Metres", "Joules"],
                        "correctIndex": 1,
                        "explanation": "Force is measured in **Newtons (N)**, named after Sir Isaac Newton who developed the laws of motion. 1 Newton is approximately the force needed to lift a 100g apple.",
                    },
                    {
                        "question": "Which of these is NOT a way to reduce friction?",
                        "options": [
                            "Using oil",
                            "Using ball bearings",
                            "Making surfaces rougher",
                            "Streamlining",
                        ],
                        "correctIndex": 2,
                        "explanation": "Making surfaces **rougher** would INCREASE friction, not reduce it! Smooth surfaces reduce friction. That's why ice skates glide easily on ice.",
                    },
                ],
            },
        ],
    },
    {
        "id": "gen-sci-s7",
        "title": "Basic Electronics — Components and Circuits",
        "difficulty": 2,
        "minutes": 15,
        "xp": 35,
        "icon": "⚡",
        "overview": "Electronics are everywhere — from your phone to traffic lights to medical equipment. In this session, you'll learn about the basic components that make up electronic circuits and how to build simple circuits of your own.",
        "steps": [
            {
                "type": "info",
                "content": "**What is Electronics?**\n\nElectronics is the branch of physics that deals with controlling the flow of electrons through components to perform useful functions.\n\n**Basic Circuit Components:**\n\n⚡ **Battery** — Provides the electrical energy (voltage source)\n🔌 **Wire** — Connects components, allows current to flow\n💡 **Bulb/LED** — Converts electricity into light\n📏 **Resistor** — Limits current flow (measured in Ohms Ω)\n🔘 **Switch** — Opens or closes the circuit\n\n**Key Concepts:**\n\n**Voltage (V)** — The 'push' that makes electrons move\n→ Measured in volts (V)\n→ Like water pressure in a pipe\n\n**Current (I)** — The flow of electrons\n→ Measured in amperes or amps (A)\n→ Like the flow rate of water\n\n**Resistance (R)** — Opposition to current flow\n→ Measured in ohms (Ω)\n→ Like a narrow section in a pipe\n\n> **Ohm's Law:** V = I × R\n> Voltage = Current × Resistance",
            },
            {
                "type": "predict",
                "pattern": "Battery (+) → Wire → LED → Wire → Battery (-)\nCurrent flows: + → LED → -\nThe LED lights up!",
                "question": "This is a diagram of a:",
                "options": [
                    "Parallel circuit",
                    "Complete circuit",
                    "Broken circuit",
                    "Short circuit",
                ],
                "correctIndex": 1,
                "explanation": "This is a **complete circuit** (also called a closed circuit)! The electrons can flow from the battery's positive terminal, through the LED, and back to the negative terminal. As long as the path is unbroken, the LED will light up.",
            },
            {
                "type": "info",
                "content": "**Electronic Components — The Building Blocks**\n\n**🔶 Resistors** — Control current flow\n• Colour bands tell you the resistance value\n• Used to protect other components from too much current\n\n**🔷 Capacitors** — Store electrical charge\n• Like a rechargeable battery\n• Used to smooth voltage fluctuations\n\n**🔶 Diodes** — One-way valves for electricity\n• Allow current to flow in only ONE direction\n• LEDs (Light Emitting Diodes) are special diodes that produce light\n\n**🔷 Transistors** — Amplify or switch signals\n• The 'brain' of modern electronics\n• Billions of transistors in a computer chip!\n\n**🟢 LEDs (Light Emitting Diodes):**\n• Convert electricity directly into light\n• Very efficient (use less energy than bulbs)\n• Available in many colours\n• Always need a resistor to limit current!\n\n> **Safety Tip:** Always check the polarity of LEDs! The longer leg (+) goes to the positive side.",
            },
            {
                "type": "question",
                "question": "Why does an LED always need a resistor connected in series with it?",
                "options": [
                    "To make it brighter",
                    "To limit the current and prevent damage",
                    "To change the colour of the light",
                    "To store electricity",
                ],
                "correctIndex": 1,
                "explanation": "An LED needs a **resistor** to **limit the current**. Without a resistor, too much current would flow through the LED and it would burn out immediately. The resistor protects the LED by ensuring only the right amount of current flows.",
            },
            {
                "type": "info",
                "content": "**Reading Circuit Diagrams**\n\nCircuit diagrams use symbols to represent components:\n\n```\n─── ||| ───  Battery (long = +, short = -)\n─── ⏤⏤ ───  Resistor\n─── ▶| ───  Diode/LED (arrow shows flow direction)\n─── ○  ───  Bulb/Lamp\n─── ⏤/ ⏤───  Switch (open/closed)\n```\n\n**Series Circuit:**\n• Components in a single loop\n• Current is the same everywhere\n• If one component fails, ALL stop working\n• Example: Old Christmas tree lights\n\n**Parallel Circuit:**\n• Components in separate branches\n• Voltage is the same across each branch\n• If one component fails, others keep working\n• Example: House wiring\n\n**Practical Project — Light-Activated Switch:**\nYou can build a circuit that turns on an LED when it gets dark using:\n• An LDR (Light Dependent Resistor)\n• A transistor (acts as a switch)\n• A resistor and LED\n\n> **Real-world application:** This is how street lights automatically turn on at night!",
            },
            {
                "type": "question",
                "question": "In which type of circuit do all components stop working if one component fails?",
                "options": [
                    "Series circuit",
                    "Parallel circuit",
                    "Both types",
                    "Neither type",
                ],
                "correctIndex": 0,
                "explanation": "In a **series circuit**, components are connected in a single loop. If one component fails (like a bulb blowing), the circuit is broken and ALL components stop working. This is why parallel circuits are used for home wiring!",
            },
            {
                "type": "checkpoint",
                "title": "Electronics Mastery",
                "bonusXp": 15,
                "passThreshold": 2,
                "questions": [
                    {
                        "question": "What is the function of a diode in a circuit?",
                        "options": [
                            "Store electrical charge",
                            "Allow current flow in one direction only",
                            "Increase voltage",
                            "Limit current flow",
                        ],
                        "correctIndex": 1,
                        "explanation": "A **diode** allows current to flow in only **one direction**. This is useful for converting AC to DC and for protecting circuits from reverse voltage.",
                    },
                    {
                        "question": "Which component stores electrical charge and can smooth voltage fluctuations?",
                        "options": [
                            "Resistor",
                            "Capacitor",
                            "Diode",
                            "Transistor",
                        ],
                        "correctIndex": 1,
                        "explanation": "A **capacitor** stores electrical charge and releases it when needed. This makes capacitors useful for smoothing out voltage fluctuations in power supplies.",
                    },
                    {
                        "question": "What does an LDR (Light Dependent Resistor) do?",
                        "options": [
                            "Produces light when current flows",
                            "Its resistance changes with light intensity",
                            "Stores light energy",
                            "Amplifies light signals",
                        ],
                        "correctIndex": 1,
                        "explanation": "An **LDR's resistance changes with light intensity**. In bright light, its resistance is low. In darkness, its resistance is high. This makes it perfect for light-sensing circuits like automatic night lights.",
                    },
                ],
            },
        ],
    },
    {
        "id": "gen-sci-s8",
        "title": "Promoting Health and Safety",
        "difficulty": 1,
        "minutes": 12,
        "xp": 30,
        "icon": "🛡️",
        "overview": "Staying healthy and safe is one of the most important life skills. In this session, you will learn about different types of hazards, lifestyle diseases and their causes, and the effects of drugs on the body.",
        "steps": [
            {
                "type": "info",
                "content": "**Understanding Hazards**\n\nA **hazard** is anything that has the potential to cause harm.\n\n**Types of Hazards:**\n\n🧪 **Biological** — Bacteria, viruses, fungi\n→ Examples: Malaria, COVID-19, food poisoning\n\n🧪 **Chemical** — Toxic substances\n→ Examples: Bleach, pesticides, battery acid\n\n⚡ **Physical** — Environmental dangers\n→ Examples: Wet floors, exposed wires, noise\n\n🔥 **Fire/Electrical** — Fire and electricity risks\n→ Examples: Faulty wiring, gas leaks\n\n**Managing Hazards — The Safety Approach:**\n\n1️⃣ **Identify** — Spot the hazard\n2️⃣ **Assess** — How risky is it?\n3️⃣ **Control** — What can we do?\n   • Remove it completely\n   • Use protective equipment\n   • Put safety signs/policies\n4️⃣ **Review** — Is the control working?\n\n🛡️ **PPE (Personal Protective Equipment):**\n• Safety goggles\n• Lab coat/apron\n• Gloves\n• Closed shoes",
            },
            {
                "type": "predict",
                "pattern": "Person A: Eats balanced meals, exercises daily, sleeps 8 hours\nPerson B: Eats junk food, never exercises, sleeps 4 hours, smokes\n\nAfter 20 years: Person A is healthy. Person B has health problems.",
                "question": "Person B's health problems are most likely caused by:",
                "options": [
                    "Bad luck",
                    "Genetics",
                    "Lifestyle choices",
                    "Infectious diseases",
                ],
                "correctIndex": 2,
                "explanation": "Person B's health problems are due to **lifestyle choices** — poor diet, lack of exercise, insufficient sleep, and smoking. These are called **lifestyle diseases** because they develop from how we live our lives.",
            },
            {
                "type": "info",
                "content": "**Lifestyle Diseases — Preventable!**\n\nLifestyle diseases are **non-communicable** (you can't catch them from someone else).\n\n**Common Lifestyle Diseases:**\n\n❤️ **Heart Disease** — From poor diet, lack of exercise, smoking\n• Leading cause of death worldwide\n• Can be prevented with healthy habits\n\n🫁 **Lung Cancer** — Mainly from smoking\n• 90% of lung cancer cases are from smoking\n• Also from air pollution\n\n🧠 **Stroke** — Blood supply to brain is blocked\n• Linked to high blood pressure, smoking, obesity\n\n🍔 **Obesity** — Excessive body fat\n• BMI over 30 is considered obese\n• Increases risk of diabetes, heart disease\n\n💉 **Type 2 Diabetes** — Body can't control blood sugar\n• Strongly linked to diet and exercise\n\n**Prevention Tips:**\n🥗 Eat more fruits, vegetables, and whole grains\n🏃 Exercise at least 30 minutes daily\n😴 Get 7-9 hours of sleep\n🚭 Avoid smoking and excessive alcohol\n💧 Drink plenty of water\n\n> **Did you know?** Regular exercise can reduce your risk of heart disease by 50%!",
            },
            {
                "type": "question",
                "question": "Which of these is NOT a lifestyle disease?",
                "options": [
                    "Type 2 diabetes",
                    "Malaria",
                    "Heart disease",
                    "Obesity",
                ],
                "correctIndex": 1,
                "explanation": "**Malaria** is an **infectious disease** caused by a parasite transmitted by mosquitoes. You can 'catch' malaria from a mosquito bite. Type 2 diabetes, heart disease, and obesity are lifestyle diseases (non-communicable).",
            },
            {
                "type": "info",
                "content": "**Drugs and Their Effects**\n\nA drug is any substance that changes how the body works. Some drugs are medicines (like paracetamol), while others are abused.\n\n**Categories of Abused Drugs:**\n\n🚬 **Stimulants** (Speed up body systems)\n• Cocaine, methamphetamine, nicotine\n• Effects: Increased heart rate, alertness, energy\n• Risks: Heart attack, seizures, addiction\n\n🍷 **Depressants** (Slow down body systems)\n• Alcohol, sleeping pills\n• Effects: Relaxation, drowsiness, slower breathing\n• Risks: Liver disease, memory loss, addiction\n\n🌀 **Hallucinogens** (Change perception of reality)\n• LSD, MDMA (Ecstasy)\n• Effects: Seeing/hearing things that aren't real\n• Risks: Panic attacks, long-term mental health issues\n\n🌿 **Cannabis (Marijuana)**\n• Affects memory and concentration\n• Long-term use linked to mental health problems\n\n💉 **Heroin** — Highly addictive opiate\n• Slows breathing — can cause death from overdose\n\n**Consequences of Drug Abuse:**\n• ❤️‍🩹 Health damage (heart, lungs, liver, brain)\n• 💔 Family problems\n• ⚖️ Legal trouble\n• 📉 Poor academic performance\n• 💰 Financial hardship\n\n> **Say NO to drugs!** The best choice is to never start. If you or someone you know needs help, talk to a trusted adult or counsellor.",
            },
            {
                "type": "question",
                "question": "Which category of drugs speeds up the body's systems and increases heart rate?",
                "options": [
                    "Depressants",
                    "Stimulants",
                    "Hallucinogens",
                    "Opiates",
                ],
                "correctIndex": 1,
                "explanation": "**Stimulants** speed up the body's systems. They increase heart rate, blood pressure, and alertness. Examples include cocaine, methamphetamine, and nicotine. Long-term use can lead to heart attacks and addiction.",
            },
            {
                "type": "checkpoint",
                "title": "Health & Safety Mastery",
                "bonusXp": 15,
                "passThreshold": 2,
                "questions": [
                    {
                        "question": "Which of these is an example of a biological hazard?",
                        "options": [
                            "Wet floor",
                            "Bleach",
                            "Malaria parasite",
                            "Exposed wire",
                        ],
                        "correctIndex": 2,
                        "explanation": "The **malaria parasite** is a biological hazard (a living organism that can cause disease). Wet floors are physical hazards, bleach is chemical, and exposed wires are electrical hazards.",
                    },
                    {
                        "question": "Which lifestyle choice is most effective for preventing heart disease?",
                        "options": [
                            "Taking vitamins",
                            "Regular exercise and healthy diet",
                            "Sleeping 4 hours per night",
                            "Drinking coffee",
                        ],
                        "correctIndex": 1,
                        "explanation": "**Regular exercise and a healthy diet** are the most effective ways to prevent heart disease. Exercise strengthens the heart, and a healthy diet keeps cholesterol and blood pressure in check.",
                    },
                    {
                        "question": "What does PPE stand for in safety?",
                        "options": [
                            "Personal Protection Equipment",
                            "Professional Protective Equipment",
                            "Personal Protective Equipment",
                            "Primary Protection Element",
                        ],
                        "correctIndex": 2,
                        "explanation": "PPE stands for **Personal Protective Equipment**. This includes safety goggles, lab coats, gloves, and closed shoes that protect you from hazards in the laboratory or workplace.",
                    },
                ],
            },
        ],
    },
    {
        "id": "gen-sci-s9",
        "title": "Local Industry and Food Production — Science in Action",
        "difficulty": 2,
        "minutes": 12,
        "xp": 30,
        "icon": "🏭",
        "overview": "Science isn't just in textbooks — it's in your kitchen, your local market, and the industries around you! Discover how science is behind everyday Ghanaian products like soap, gari, kenkey, and tubani.",
        "steps": [
            {
                "type": "info",
                "content": "**Science in Local Industry**\n\nMany traditional Ghanaian products involve fascinating scientific processes. Let's explore the science behind them!\n\n**🧼 Local Soap Production — Saponification**\n\nSoap making is a **chemical reaction** called **saponification**:\n\n> Fat/Oil + Alkali (caustic soda) → Soap + Glycerol\n\n**The Process:**\n1. Heat oil (palm oil, coconut oil)\n2. Add alkali solution carefully\n3. Stir continuously — chemical reaction happens!\n4. Pour into moulds to set\n5. Cut and cure for several days\n\n**Types of Local Soap:**\n• 🟤 **African Black Soap** — Made from plantain skins, cocoa pods, palm leaves\n• ⚪ **African White Soap** — Made from coconut oil and palm kernel oil\n\n⚗️ **Emulsification** — Soap works because one end of the soap molecule loves water (hydrophilic) and the other end loves oil (hydrophobic). This allows soap to lift grease and dirt off surfaces!\n\n> **Safety Alert:** Caustic soda is highly corrosive! Always wear gloves and goggles when making soap.",
            },
            {
                "type": "predict",
                "pattern": "Fat/Oil + NaOH (caustic soda) → Soap + Glycerol\nThis is called saponification.\nHeat is released during the reaction.",
                "question": "What type of reaction is saponification?",
                "options": [
                    "Physical change",
                    "Exothermic chemical reaction",
                    "Endothermic reaction",
                    "Nuclear reaction",
                ],
                "correctIndex": 1,
                "explanation": "Saponification is an **exothermic chemical reaction** — heat is released when the fat reacts with the alkali. The fat molecules (triglycerides) break apart and form soap molecules and glycerol.",
            },
            {
                "type": "info",
                "content": "**🥣 Gari Production — Cassava Processing**\n\nGari is made from cassava — a staple crop in Ghana. The process involves several scientific principles:\n\n**Step 1: Peeling & Washing**\n→ Remove the skin (physical preparation)\n\n**Step 2: Grating**\n→ Break down cell walls to release water and starch\n\n**Step 3: Fermentation (2-3 days)**\n🧪 **Biology:** Microorganisms break down cyanogenic glycosides\n🧪 **Chemistry:** This removes toxic hydrogen cyanide!\n\n**Step 4: Pressing & Drying**\n→ Remove excess water (dehydration)\n\n**Step 5: Roasting**\n🔥 **Physics:** Heat transfer through conduction\n🔥 **Chemistry:** Starch gelatinises — becomes partially cooked\n\n**The Science Behind Cassava Processing:**\n• Raw cassava contains **cyanide compounds** — TOXIC!\n• Soaking and fermentation breaks down these compounds\n• Heat during roasting further removes any remaining toxins\n• This makes cassava SAFE to eat!\n\n> **Did you know?** Without proper processing, eating raw cassava can make you very sick. The fermentation and heating steps are essential for food safety!",
            },
            {
                "type": "question",
                "question": "Why is cassava fermented for 2-3 days before making gari?",
                "options": [
                    "To improve the taste only",
                    "To remove toxic cyanide compounds",
                    "To change the colour",
                    "To make it last longer",
                ],
                "correctIndex": 1,
                "explanation": "Fermentation is essential to **remove toxic cyanide compounds** from cassava. Raw cassava contains cyanogenic glycosides that break down to release hydrogen cyanide. The fermentation process allows microorganisms to break down these toxic compounds, making the cassava safe to eat.",
            },
            {
                "type": "info",
                "content": "**🌽 Kenkey Production — Fermentation in Action**\n\nKenkey is a traditional Ghanaian food made from fermented maize dough. The science behind it is fascinating!\n\n**The Process:**\n1. 🌾 **Soaking** — Maize soaked in water for 1-2 days\n2. ⚙️ **Milling** — Wet maize ground into dough\n3. 🧪 **Fermentation** (2-3 days):\n   → **Lactobacillus bacteria** produce lactic acid\n   → **Yeast** produces carbon dioxide\n   → This gives kenkey its sour taste and fluffy texture!\n4. 🔥 **Aflata preparation:**\n   → Part of the dough is cooked with water\n   → Mixed back with raw dough\n   → This gelatinises the starch and creates the right consistency\n5. 🥟 **Steaming** — The dough is wrapped in maize husks or leaves and steamed for 2-3 hours\n\n**🧁 Tubani Production:**\n• Made from **black-eyed peas** (not maize!)\n• Soaked, blended with spices (pepper, salt, ginger)\n• Fermented for 8-12 hours\n• Steamed in small cakes\n\n> **Key Science Concepts Involved:**\n🔬 **Microbiology** — Microorganisms drive fermentation\n🧪 **Biochemistry** — Enzymes break down complex molecules\n🔥 **Heat transfer** — Steaming cooks the food evenly\n⚗️ **Starch gelatinisation** — Heat causes starch to absorb water and thicken",
            },
            {
                "type": "question",
                "question": "What microorganism is primarily responsible for the sour taste of kenkey?",
                "options": [
                    "Yeast",
                    "Lactobacillus bacteria",
                    "E. coli",
                    "Mould",
                ],
                "correctIndex": 1,
                "explanation": "**Lactobacillus bacteria** produce lactic acid during fermentation, which gives kenkey its characteristic sour taste. The same type of bacteria is used to make yoghurt! Yeast also plays a role by producing carbon dioxide that makes the kenkey fluffy.",
            },
            {
                "type": "checkpoint",
                "title": "Local Industry Mastery",
                "bonusXp": 15,
                "passThreshold": 2,
                "questions": [
                    {
                        "question": "What is the chemical reaction called when making soap?",
                        "options": [
                            "Polymerisation",
                            "Saponification",
                            "Fermentation",
                            "Oxidation",
                        ],
                        "correctIndex": 1,
                        "explanation": "**Saponification** is the chemical reaction between fat/oil and an alkali (like caustic soda) to produce soap and glycerol.",
                    },
                    {
                        "question": "Why is fermentation important in gari production?",
                        "options": [
                            "To improve the colour",
                            "To increase the weight",
                            "To remove toxic cyanide compounds",
                            "To add vitamins",
                        ],
                        "correctIndex": 2,
                        "explanation": "Fermentation breaks down **cyanogenic glycosides** in cassava that produce toxic hydrogen cyanide. This makes the cassava safe for consumption.",
                    },
                    {
                        "question": "What is the main ingredient in tubani?",
                        "options": [
                            "Maize",
                            "Cassava",
                            "Black-eyed peas",
                            "Plantain",
                        ],
                        "correctIndex": 2,
                        "explanation": "**Tubani** is made from **black-eyed peas** (not maize like kenkey). The peas are soaked, blended with spices, fermented, and steamed into small cakes.",
                    },
                ],
            },
        ],
    },
]


# ── Generate TypeScript ───────────────────────────────────────────────────

def generate_ts():
    lines = []
    lines.append("""/**
 * generalScienceContent.ts
 * ──────────────────────────
 * General Science Year 1 — 9 interactive sessions generated from
 * the Ministry of Education SHS curriculum.
 *
 * Auto-generated by scripts/generate_science_content.py
 * Do not edit directly — re-run the generator instead.
 */

import type { Lesson } from './learningContent';

export const GENERAL_SCIENCE_UNIT = {
  id: 'general-science',
  title: 'General Science Year 1',
  subtitle: '🔬 Foundation scientists — explore the world around you',
  colour: 'from-cyan-500/20 to-blue-500/20',
  icon: '🔬',
};

""")

    lines.append("export const GENERAL_SCIENCE_LESSONS: Lesson[] = [\n")

    for s in SESSIONS:
        lines.append("  {\n")
        lines.append(f'    id: "{s["id"]}",\n')
        lines.append(f'    title: "{s["title"]}",\n')
        lines.append(f'    subject: "General Science",\n')
        lines.append(f'    subjectIcon: "{s["icon"]}",\n')
        lines.append(f'    programme: "Science" as const,\n')
        lines.append(f'    difficulty: {s["difficulty"]},\n')
        lines.append(f'    estimatedMinutes: {s["minutes"]},\n')
        lines.append(f'    xpReward: {s["xp"]},\n')
        lines.append(f'    unitId: "general-science",\n')
        lines.append(f'    prerequisites: [],\n')
        lines.append(f'    shsLevels: ["SHS 1"],\n')
        lines.append(f'    suggestedLevel: "SHS 1",\n')
        lines.append("    steps: [\n")

        for step in s["steps"]:
            stype = step["type"]
            lines.append("      {\n")
            lines.append(f'        id: "{s["id"]}-{s["steps"].index(step)}",\n')
            lines.append(f'        type: "{stype}" as const,\n')

            # content is required for all step types
            if "content" in step:
                content = json.dumps(step['content'])
            else:
                # Provide a default content for non-info steps
                content = json.dumps(step.get('question', step.get('title', '')))
            lines.append(f'        content:\n')
            lines.append(f'          {content},\n')

            if stype == "predict":
                p = step
                lines.append(f'        predict: {{\n')
                # Use backtick template literal if pattern contains newlines
                if '\n' in p["pattern"]:
                    lines.append(f'          pattern: `{p["pattern"]}`,\n')
                else:
                    lines.append(f'          pattern: {json.dumps(p["pattern"])},\n')
                lines.append(f'          question: {json.dumps(p["question"])},\n')
                lines.append(f'          options: {json.dumps(p["options"])},\n')
                lines.append(f'          correctIndex: {p["correctIndex"]},\n')
                lines.append(f'          explanation: {json.dumps(p["explanation"])},\n')
                lines.append(f'        }},\n')

            if stype == "question":
                lines.append(f'        exercise: {{\n')
                lines.append(f'          question: {json.dumps(step["question"])},\n')
                lines.append(f'          options: {json.dumps(step["options"])},\n')
                lines.append(f'          correctIndex: {step["correctIndex"]},\n')
                lines.append(f'          explanation: {json.dumps(step["explanation"])},\n')
                lines.append(f'        }},\n')

            if stype == "checkpoint":
                cp = step
                lines.append(f'        checkpoint: {{\n')
                lines.append(f'          title: {json.dumps(cp["title"])},\n')
                lines.append(f'          passThreshold: {cp["passThreshold"]},\n')
                lines.append(f'          bonusXp: {cp["bonusXp"]},\n')
                lines.append(f'          questions: [\n')
                for q in cp["questions"]:
                    lines.append(f'            {{\n')
                    lines.append(f'              question: {json.dumps(q["question"])},\n')
                    lines.append(f'              options: {json.dumps(q["options"])},\n')
                    lines.append(f'              correctIndex: {q["correctIndex"]},\n')
                    lines.append(f'              explanation: {json.dumps(q["explanation"])},\n')
                    lines.append(f'            }},\n')
                lines.append(f'          ],\n')
                lines.append(f'        }},\n')

            lines.append("      },\n")

        lines.append("    ],\n")
        lines.append("  },\n")

    lines.append("];\n")

    return "".join(lines)


if __name__ == "__main__":
    ts = generate_ts()
    # Write from project root so it works regardless of cwd
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "lib", "generalScienceContent.ts")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ts)
    # Use ASCII-safe output for Windows compatibility
    print("[OK] Generated generalScienceContent.ts successfully!")
    print(f"[OK] Created {len(SESSIONS)} lessons")
    print(f"[OK] File ready at app/lib/generalScienceContent.ts")
