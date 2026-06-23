import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('app/lib/learningContent.ts', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# ── 1. Update literature unit to include new lessons ──
# Line 1005 (0-indexed: 1004): lessons: ['lit-1', 'lit-2', 'lit-3'],
old_unit_line = "    lessons: ['lit-1', 'lit-2', 'lit-3'],"
new_unit_line = "    lessons: ['lit-1', 'lit-2', 'lit-3', 'lit-4', 'lit-5', 'lit-6'],"

# Make the replacement
if old_unit_line in lines[1004]:
    lines[1004] = new_unit_line
    print(f"✓ Updated literature unit lessons list (line 1005)")
else:
    print(f"✗ Could not find literature unit line at line 1005")
    print(f"  Found: {lines[1004]}")

# ── 2. Expand lit-3 (Drama) — add 2 more steps after the existing 4th step ──
# Find lit-3-s4 step (last step of lit-3)
lit3_s4_idx = None
for i, line in enumerate(lines):
    if "id: 'lit-3-s4'" in line.strip():
        lit3_s4_idx = i
        break

if lit3_s4_idx:
    print(f"Found lit-3-s4 at line {lit3_s4_idx + 1}")
    
    # Find the closing of this step (look for the next }, after lit-3-s4)
    step_end_idx = None
    for j in range(lit3_s4_idx, min(lit3_s4_idx + 50, len(lines))):
        if lines[j].strip() == '},':
            step_end_idx = j
            break
    
    if step_end_idx:
        print(f"lit-3-s4 step ends at line {step_end_idx + 1}")
        
        # The next line after the step should be the last }] closing of the steps array
        # Before the closing of the lesson
        
        # New steps to add
        lit3_s5 = """    {
        id: 'lit-3-s5',
        type: 'info',
        content:
          \"🎭 **Dramatic Techniques — How Meaning is Created on Stage**\\n\\n**Key techniques used by playwrights (WASSCE Essential!):**\\n\\n**1. Soliloquy:**\\n• A character speaks their thoughts aloud while alone on stage\\n• Reveals inner thoughts and feelings to the audience\\n• Example: Hamlet's \\\"To be or not to be\\\" speech\\n\\n**2. Aside:**\\n• A character speaks directly to the audience, unheard by other characters\\n• Creates intimacy and dramatic irony\\n\\n**3. Dramatic Irony:**\\n• The audience knows something the characters don't\\n• Creates tension and suspense\\n\\n**4. Flashback:**\\n• Scene that takes the action back in time\\n• Reveals background information\\n\\n**5. Symbolism:**\\n• Objects, colours, or actions that represent deeper meanings\\n• Example: A storm representing chaos or inner turmoil\\n\\n**6. Foreshadowing:**\\n• Hints or clues about what will happen later\\n\\n> 💡 **WASSCE Tip:** When analysing a play extract, always comment on the dramatic effect of the techniques used — not just identify them!\",
    },
    {
        id: 'lit-3-s6',
        type: 'question',
        content:
          'In a play, a character speaks to the audience while other characters on stage cannot hear them.\\n\\n**What dramatic technique is this?**',
        exercise: {
          question: 'Speaking to audience, unheard by others = ?',
          options: [
            'Soliloquy',
            'Aside',
            'Dramatic irony',
            'Flashback',
          ],
          correctIndex: 1,
          explanation:
            'An **aside** is when a character speaks directly to the audience while other characters are unaware. A **soliloquy** is similar but the character is alone on stage. **Dramatic irony** is when the audience knows something characters don\'t. WASSCE frequently tests the difference between these three!',
        },
      }"""
        
        # Insert after the step end
        next_line = step_end_idx + 1
        # We need to insert before the closing ] of the steps array
        # Let's find the ] that closes the steps array
        closing_bracket_idx = None
        for j in range(step_end_idx, min(step_end_idx + 20, len(lines))):
            if lines[j].strip() == '],':
                closing_bracket_idx = j
                break
        
        if closing_bracket_idx:
            print(f"Steps array closes at line {closing_bracket_idx + 1}")
            # Insert new steps before the closing ]
            # The new steps will be inserted at the position of closing_bracket_idx
            new_lines = [lit3_s5]
            lines[closing_bracket_idx:closing_bracket_idx] = new_lines
            print(f"✓ Added 2 new steps to lit-3 (Drama) - dramatic techniques + scene analysis")
        else:
            print("✗ Could not find closing bracket of steps array")
    else:
        print("✗ Could not find end of lit-3-s4 step")
else:
    print("✗ Could not find lit-3-s4")

# Recalculate line numbers since we've modified the list
# Now find the end of ARTS_LESSONS
arts_end_idx = None
for i, line in enumerate(lines):
    if "export const SHARED_LESSONS" in line:
        arts_end_idx = i - 3  # The ]; closing ARTS_LESSONS should be a few lines above
        break

if arts_end_idx:
    # Verify we found the right spot
    print(f"ARTS_LESSONS closing at line {arts_end_idx + 1}: {lines[arts_end_idx]}")
    
    # ── 3. Add lit-4 — African Prose & WASSCE Set Texts ──
    lit4 = """  {
    id: 'lit-4',
    title: 'African Prose and WASSCE Set Texts',
    subject: 'Literature in English',
    subjectIcon: '📚',
    programme: 'Arts',
    difficulty: 2,
    estimatedMinutes: 6,
    xpReward: 30,
    unitId: 'literature',
    prerequisites: ['lit-1'],
    steps: [
      {
        id: 'lit-4-s1',
        type: 'info',
        content:
          \"🌍 **African Prose** is a major component of the WASSCE Literature paper. The exam board prescribes specific novels each year for study.\\n\\n**Why African Literature Matters:**\\n• Reflects African experiences and perspectives\\n• Explores themes of identity, colonialism, independence, and modern challenges\\n• Written by African authors for African audiences\\n\\n**Common WASSCE Set Authors (examples):**\\n• **Chinua Achebe** (Nigeria) — *Things Fall Apart*, *No Longer at Ease*\\n• **Ayí Kwei Armah** (Ghana) — *The Beautyful Ones Are Not Yet Born*\\n• **Mariama Bâ** (Senegal) — *So Long a Letter*\\n• **Ferdinand Oyono** (Cameroon) — *Houseboy*, *The Old Man and the Medal*\\n• **Ama Ata Aidoo** (Ghana) — *Changes: A Love Story*\\n\\n> ⚠️ **Important:** Always check the current WASSCE prescribed text list — it changes periodically!\",
      },
      {
        id: 'lit-4-s2',
        type: 'question',
        content:
          '**WASSCE-style question:** Which of the following is a novel by **Chinua Achebe**, one of Africa\\'s most celebrated writers?',
        exercise: {
          question: 'Novel by Chinua Achebe = ?',
          options: [
            'The Beautyful Ones Are Not Yet Born',
            'Things Fall Apart',
            'So Long a Letter',
            'Changes: A Love Story',
          ],
          correctIndex: 1,
          explanation:
            '**Things Fall Apart** (1958) is Chinua Achebe\\'s most famous novel. It tells the story of Okonkwo, an Igbo leader, and the impact of British colonialism on traditional Igbo society. The title comes from W.B. Yeats\\' poem \\"The Second Coming.\\"',
        },
      },
      {
        id: 'lit-4-s3',
        type: 'info',
        content:
          \"📖 **How to Approach a WASSCE Set Text — Step-by-Step**\\n\\n**Step 1: Read the Whole Work**\\n• Read the novel/play once for enjoyment and the story\\n• Then read it again analytically\\n\\n**Step 2: Take Notes by Chapter**\\n• Summarise what happens in each chapter\\n• Note key characters introduced, conflicts, and developments\\n\\n**Step 3: Track Characters**\\n• Create a character profile for each major character:\\n  - Who are they?\\n  - What motivates them?\\n  - How do they change?\\n  - What role do they play in the story?\\n\\n**Step 4: Identify Themes**\\n• What are the big ideas?\\n  - Tradition vs change\\n  - Power and corruption\\n  - Identity and belonging\\n  - Gender roles\\n  - Colonialism and its aftermath\\n\\n**Step 5: Note Key Passages**\\n• Mark important quotes and passages for revision\\n\\n> 📝 **WASSCE Tip:** Practice writing timed essay responses (40 minutes each) using past questions on your set texts!\",
      },
      {
        id: 'lit-4-s4',
        type: 'question',
        content:
          '**WASSCE-style question:** When studying a set text for WASSCE, why is it important to track how a character **changes** over the course of the story?',
        exercise: {
          question: 'Why track character change?',
          options: [
            'The WASSCE requires you to memorise character lists',
            'Character development often reveals the novel\\'s central themes and the author\\'s message',
            'The exam asks only about the main character',
            'Characters never change in African novels',
          ],
          correctIndex: 1,
          explanation:
            'Character **development** is directly linked to **theme**. When a character changes — like Okonkwo\\'s tragic fall in *Things Fall Apart* — it reveals the author\\'s message about society, culture, or human nature. This is exactly what WASSCE examiners want you to analyse!',
        },
      },
      {
        id: 'lit-4-s5',
        type: 'info',
        content:
          \"✍️ **WASSCE Prose Essay Structure (Sample Outline):**\\n\\n**Title:** Discuss the theme of tradition versus change in your prescribed novel.\\n\\n**Introduction (2-3 sentences):**\\n• Identify the novel, author, and the theme\\n• Briefly state your argument\\n\\n**Body Paragraphs (3-4 paragraphs):**\\n• Each paragraph = ONE point with evidence\\n\\n**P.E.E.L Structure (WASSCE Recommended!):**\\n• **P**oint — Make your claim\\n• **E**vidence — Quote or reference the text\\n• **E**xplanation — Explain how the evidence supports your point\\n• **L**ink — Link back to the question and the theme\\n\\n**Conclusion (2-3 sentences):**\\n• Summarise your main argument\\n• Offer a final insight about the author\\'s message\\n\\n> 🔑 **Remember:** Quality over quantity! A well-structured essay with 3 strong points is better than a disorganised one with 5 weak points.\",
      },
      {
        id: 'lit-4-s6',
        type: 'question',
        content:
          '**WASSCE-style question:** What does the **P.E.E.L.** structure help you achieve in a Literature essay?',
        exercise: {
          question: 'P.E.E.L. helps you...',
          options: [
            'Write faster without planning',
            'Develop each point clearly with textual evidence and analysis',
            'Memorise the entire plot',
            'Avoid quoting from the text',
          ],
          correctIndex: 1,
          explanation:
            '**P.E.E.L.** (Point, Evidence, Explanation, Link) ensures every paragraph is focused and well-supported. The **Evidence** step requires direct quotes or references from the text, and the **Explanation** step shows you can analyse — exactly what WASSCE examiners reward!',
        },
      },
    ],
  },""" 

    # ── 4. Add lit-5 — Essay Writing for Literature (WASSCE) ──
    lit5 = """  {
    id: 'lit-5',
    title: 'Essay Writing for Literature — WASSCE Mastery',
    subject: 'Literature in English',
    subjectIcon: '📚',
    programme: 'Arts',
    difficulty: 3,
    estimatedMinutes: 6,
    xpReward: 35,
    unitId: 'literature',
    prerequisites: ['lit-1', 'lit-4'],
    steps: [
      {
        id: 'lit-5-s1',
        type: 'info',
        content:
          \"✍️ **WASSCE Literature Paper 2 and 3 — What to Expect**\\n\\nThe WASSCE Literature in English exam has three papers:\\n\\n**Paper 1:** Objective questions (multiple choice) on general literary knowledge\\n**Paper 2:** Prose — Essay questions on prescribed texts\\n**Paper 3:** Drama and Poetry — Essay or commentary questions\\n\\n**Essay Types You Must Master:**\\n\\n1. **Character analysis:** Discuss a character's role, development, and significance\\n2. **Theme-based:** Explore a central theme with evidence from the text\\n3. **Compare and contrast:** Compare two characters, situations, or texts\\n4. **Context/background:** Discuss the social, historical, or cultural context\\n5. **Critical appreciation:** Analyse a given extract (language, style, meaning)\\n\\n> 📝 **Time management:** Allocate 35-40 minutes per essay. Spend the first 5 minutes planning!\",
      },
      {
        id: 'lit-5-s2',
        type: 'question',
        content:
          '**WASSCE-style question:** You have 40 minutes to write a Literature essay. How should you budget your time?',
        exercise: {
          question: 'Best time allocation for a 40-minute essay:',
          options: [
            'Write continuously for 40 minutes without stopping',
            '5 minutes planning, 30 minutes writing, 5 minutes reviewing',
            '10 minutes planning, 30 minutes writing',
            'Write for 35 minutes, then summarise in 5 minutes',
          ],
          correctIndex: 1,
          explanation:
            'The **5-30-5** rule: Spend the first 5 minutes **planning** your essay structure and key points. Use 30 minutes **writing** with the P.E.E.L. structure. Save the last 5 minutes to **review** and correct errors. This approach consistently produces better WASSCE essays!',
        },
      },
      {
        id: 'lit-5-s3',
        type: 'info',
        content:
          \"🎯 **Sample WASSCE Essay Question + Model Answer**\\n\\n**Question:** *Discuss the role of the traditional ruler in ensuring peace and stability in the society depicted in your prescribed novel.*\\n\\n**Model Introduction:**\\n*»In Chinua Achebe\\'s \\"Things Fall Apart,\\" traditional rulers and institutions play a crucial role in maintaining peace and stability in pre-colonial Igbo society. Through the actions of the egwugwu (the masked spirits representing ancestral authority) and the clan\\'s judicial system, Achebe demonstrates how traditional governance structures preserved order before colonial disruption.«*\\n\\n**Model Body Paragraph (P.E.E.L.):**\\n\\n**P:** The egwugwu serve as both spiritual and judicial authority in Umuofia.\\n\\n**E:** When a domestic dispute arises between Uzowulu and his wife\\'s family, the egwugwu hear the case and deliver judgment, declaring, *\\"We have heard both sides of the case... Uzowulu\\'s family should prepare a feast for Oduche\\'s family.\\"*\\n\\n**E:** This scene shows that the Igbo had a sophisticated legal system where disputes were resolved through public hearing and restitution rather than violence.\\n\\n**L:** Thus, Achebe challenges the colonial narrative that Africa lacked civilised systems of justice.\",
      },
      {
        id: 'lit-5-s4',
        type: 'question',
        content:
          '**WASSCE-style question:** What is the purpose of the **Link** step in the P.E.E.L. paragraph structure?',
        exercise: {
          question: 'The Link step = ?',
          options: [
            'To add more quotes to the paragraph',
            'To connect your point back to the essay question and overall argument',
            'To summarise the entire essay within the paragraph',
            'To introduce a new character',
          ],
          correctIndex: 1,
          explanation:
            'The **Link** step connects your paragraph\\'s argument back to the main essay question. It shows the examiner that you understand how this specific point supports your overall thesis. Without a strong link, your paragraph feels disconnected from the question!',
        },
      },
      {
        id: 'lit-5-s5',
        type: 'info',
        content:
          \"📋 **WASSCE Literature — Common Weaknesses (And How to Avoid Them)**\\n\\n**Weakness 1: Summary instead of analysis**\\n❌ *\\\"Okonkwo was a strong man who had three wives and many children. He was famous for wrestling.\\\"*\\n✅ *\\\"Achebe uses Okonkwo\\'s physical strength and wrestling prowess as symbols of his uncompromising masculinity and fear of appearing weak — traits that ultimately lead to his tragic downfall.\\\"*\\n\\n**Weakness 2: No textual evidence**\\n❌ *\\\"The character is very stubborn and this causes problems.\\\"*\\n✅ *\\\"Okonkwo\\'s stubbornness is evident when he \\\"did not eat for two days\\\" after being told his son Nwoye had converted to Christianity, revealing how his inflexibility destroys his family.\\\"*\\n\\n**Weakness 3: Forgetting the author\\'s purpose**\\n❌ *\\\"Things Fall Apart is about a man who kills himself.\\\"*\\n✅ *\\\"Through Okonkwo\\'s tragic end, Achebe critiques both the rigidity of Igbo tradition and the destructive force of colonialism, ultimately arguing for a balanced approach to change.\\\"*\\n\\n> 🔑 **The golden rule: SHOW you understand the writer\\'s craft, don\\'t just retell the story!**\",
      },
      {
        id: 'lit-5-s6',
        type: 'question',
        content:
          '**WASSCE-style question:** Which of the following is an **analytical** statement suitable for a high-scoring WASSCE Literature essay?',
        exercise: {
          question: 'Which is analytical writing?',
          options: [
            'Okonkwo killed Ikemefuna because the oracle said so',
            'Through the killing of Ikemefuna, Achebe explores the tragic conflict between personal affection and social duty — a conflict that defines Okonkwo\\'s character',
            'Ikemefuna was a boy who lived with Okonkwo\\'s family for three years',
            'Ezeudu was an important elder in the village',
          ],
          correctIndex: 1,
          explanation:
            'The second option is **analytical** — it interprets the event\\'s significance and connects it to character and theme. The others are merely **descriptive** or **narrative** statements. WASSCE examiners explicitly say analysis scores higher than narration!',
        },
      },
    ],
  },"""

    # ── 5. Add lit-6 — Character & Theme Analysis Across Genres ──
    lit6 = """  {
    id: 'lit-6',
    title: 'Character and Theme Analysis Across Genres',
    subject: 'Literature in English',
    subjectIcon: '📚',
    programme: 'Arts',
    difficulty: 3,
    estimatedMinutes: 6,
    xpReward: 35,
    unitId: 'literature',
    prerequisites: ['lit-1', 'lit-2', 'lit-3'],
    steps: [
      {
        id: 'lit-6-s1',
        type: 'info',
        content:
          \"🧩 **Analysing Characters — A Universal Approach**\\n\\nWhether you\\'re analysing a novel, poem, or play, you can use this framework:\\n\\n**1. Characterisation Methods:**\\nHow does the author reveal the character?\\n• **Direct:** The narrator tells us (\\\"He was a kind man\\\")\\n• **Indirect:** We infer from actions, speech, thoughts, appearance, and others\\' reactions\\n\\n**2. Character Types:**\\n• **Protagonist:** Main character (hero)\\n• **Antagonist:** Opposes the protagonist (villain/conflict)\\n• **Foil:** A character who contrasts with another to highlight qualities\\n• **Round character:** Complex, multi-dimensional, changes\\n• **Flat character:** Simple, one-dimensional, does not change\\n\\n**3. Character Functions in Plot:**\\n• **Catalyst:** Triggers events\\n• **Confidant:** Receives secrets, reveals character\\n• **Symbol:** Represents an idea or theme\\n\\n> 💡 **WASSCE loves questions that ask you to compare two characters — be ready!**\",
      },
      {
        id: 'lit-6-s2',
        type: 'question',
        content:
          'A **foil** is a character who...',
        exercise: {
          question: 'Definition of a foil character:',
          options: [
            'Always opposes the protagonist as the villain',
            'Contrasts with another character to highlight specific traits',
            'Tells the story from their point of view',
            'Never appears on stage',
          ],
          correctIndex: 1,
          explanation:
            'A **foil** contrasts with another character to highlight their qualities. For example, in *Things Fall Apart*, Obierika serves as a foil to Okonkwo — where Okonkwo is impulsive and rigid, Obierika is thoughtful and reflective. This contrast makes Okonkwo\\'s traits more visible to the reader.',
        },
      },
      {
        id: 'lit-6-s3',
        type: 'info',
        content:
          \"🎯 **Thematic Analysis — Uncovering the Big Ideas**\\n\\n**What is a theme?**\\nA theme is a central idea or message explored in a literary work. It is **not** the same as the subject or topic.\\n\\n**Topic vs Theme:**\\n• Topic: Love\\n• Theme: *\\\"Love can blind us to the truth about those we trust.\\\"*\\n\\n**Common Themes in African Literature (WASSCE Focus):**\\n\\n1. **Identity and Culture:**\\n   - The clash between tradition and modernity\\n   - Preserving cultural heritage\\n   - The search for self in a changing world\\n\\n2. **Power and Corruption:**\\n   - Abuse of political power\\n   - The corrupting influence of wealth\\n   - Resistance and revolution\\n\\n3. **Colonialism and Its Aftermath:**\\n   - Dispossession and alienation\\n   - Cultural hybridity\\n   - The struggle for independence\\n\\n4. **Gender and Society:**\\n   - Women\\'s roles and rights\\n   - Patriarchy and resistance\\n   - Marriage and family\\n\\n5. **Justice and Morality:**\\n   - Traditional vs Western justice systems\\n   - Moral choices and consequences\\n\\n> 📌 **Tip:** When asked about theme, think about what the AUTHOR is saying about the topic!\",
      },
      {
        id: 'lit-6-s4',
        type: 'question',
        content:
          '**WASSCE-style question:** What is the difference between a **topic** and a **theme** in literature?',
        exercise: {
          question: 'Topic vs Theme?',
          options: [
            'They mean the same thing',
            'A topic is a subject (e.g., love); a theme is the author\\'s message about that subject',
            'A topic is found only in prose; a theme is found only in poetry',
            'A theme is the title of the work',
          ],
          correctIndex: 1,
          explanation:
            'The **topic** is the general subject — like \\"war.\\" The **theme** is the author\\'s insight about that topic — like \\"War destroys not only bodies but also the humanity of those who fight.\\" WASSCE examiners expect you to articulate themes, not just topics!',
        },
      },
      {
        id: 'lit-6-s5',
        type: 'info',
        content:
          \"📝 **WASSCE Cross-Genre Analysis — Drama vs Prose**\\n\\nThe same themes appear across different genres, but they are explored differently.\\n\\n**Theme: Power and Corruption**\\n\\n**In Prose (e.g., *The Beautyful Ones Are Not Yet Born*):**\\n• The narrator describes the main character\\'s inner thoughts\\n• We see corruption through daily life details\\n• Extended description of decay and moral compromise\\n\\n**In Drama (e.g., *The Trials of Brother Jero*):**\\n• Corruption is shown through dialogue and action\\n• Characters reveal their motives through speech\\n• Dramatic irony creates humour and critique\\n\\n**In Poetry:**\\n• Condensed language to express emotional response\\n• Imagery and metaphor to convey critique\\n• Often more personal and subjective\\n\\n> 🔑 **Key insight for WASSCE:** When comparing how two texts from different genres explore the same theme, focus on the **techniques** each genre offers the writer!\",
      },
      {
        id: 'lit-6-s6',
        type: 'question',
        content:
          '**WASSCE-style question:** How does **drama** typically explore themes differently from **prose**?',
        exercise: {
          question: 'Drama explores themes through...',
          options: [
            'Primarily through extended narration and description',
            'Through dialogue, action, and stage directions — characters reveal themes by what they say and do',
            'Only through the chorus commenting on events',
            'The same way as prose in every respect',
          ],
          correctIndex: 1,
          explanation:
            'In **drama**, themes are revealed through **dialogue**, **action**, and **stage directions** because there is no narrator to explain. The playwright must \\\"show\\\" rather than \\\"tell.\\" This is why studying dramatic techniques (subtext, irony, symbolism) is crucial for WASSCE Drama questions!',
        },
      },
    ],
  },"""

    # Insert the 3 new lessons before ARTS_LESSONS closing
    new_lessons = '\n' + lit4 + '\n' + lit5 + '\n' + lit6
    
    # Insert at the position of the last element before ];
    # The line arts_end_idx is ]; (closing ARTS_LESSONS)
    # Line arts_end_idx - 1 is the last element (crs-2), ending with },
    lines[arts_end_idx] = new_lessons + '\n];'
    
    print(f"✓ Added lit-4, lit-5, lit-6 before ARTS_LESSONS closing at line {arts_end_idx + 1}")
else:
    print("✗ Could not find ARTS_LESSONS closing")

# Write the modified content back
with open('app/lib/learningContent.ts', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("\n✅ All changes applied!")
