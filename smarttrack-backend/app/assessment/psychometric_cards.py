"""
psychometric_cards.py
─────────────────────
Psychometric Insight Cards for the Atlas Challenge Arena.

These cards are injected after every 3–5 challenge questions. They feel
natural and engaging — students should NOT feel they are taking a
psychological assessment. Instead, they should feel like quick, fun
reflection moments between challenges.

Architecture:
  Each card has:
    - id: unique identifier
    - category: which trait/dimension it measures
    - question: friendly, natural wording
    - options: list of { value, label, trait_weights }
      trait_weights map to behavioural dimensions used by the
      recommendation engine.
    - display: "emoji" | "thumbs" | "scale" | "choose"
"""

from typing import List, Dict, Any

# ── Type ─────────────────────────────────────────────────────────────────────
PsychometricCard = Dict[str, Any]


# ── Master card library ──────────────────────────────────────────────────────

PSYCHOMETRIC_CARDS: List[PsychometricCard] = [
    # ── Motivation & Drive ────────────────────────────────────────────────────
    {
        "id": "motiv_001",
        "category": "Motivation",
        "question": "What sounds most exciting to you?",
        "display": "choose",
        "options": [
            {"value": "A", "label": "🏗️ Building something new from scratch",
             "trait_weights": {"Creativity": 0.3, "Independence": 0.2}},
            {"value": "B", "label": "🔬 Discovering how things work",
             "trait_weights": {"Curiosity": 0.3, "Analytical": 0.2}},
            {"value": "C", "label": "🤝 Helping others succeed",
             "trait_weights": {"Empathy": 0.3, "Collaboration": 0.2}},
            {"value": "D", "label": "🏆 Competing and winning",
             "trait_weights": {"Competitiveness": 0.3, "Ambition": 0.2}},
        ],
    },
    {
        "id": "motiv_002",
        "category": "Motivation",
        "question": "Which describes you best when starting a new project?",
        "display": "choose",
        "options": [
            {"value": "A", "label": "I plan everything carefully first",
             "trait_weights": {"Methodical": 0.3, "Persistence": 0.1}},
            {"value": "B", "label": "I dive in and figure things out as I go",
             "trait_weights": {"Boldness": 0.3, "Adaptability": 0.2}},
            {"value": "C", "label": "I ask others who have done it before",
             "trait_weights": {"Collaboration": 0.3, "Openness": 0.1}},
            {"value": "D", "label": "I visualise the end result and work backwards",
             "trait_weights": {"Creativity": 0.2, "Strategic": 0.3}},
        ],
    },
    {
        "id": "motiv_003",
        "category": "Motivation",
        "question": "What makes you feel most proud?",
        "display": "choose",
        "options": [
            {"value": "A", "label": "Solving a problem nobody else could",
             "trait_weights": {"Analytical": 0.3, "Persistence": 0.2}},
            {"value": "B", "label": "Creating something beautiful or useful",
             "trait_weights": {"Creativity": 0.4, "Artistic": 0.1}},
            {"value": "C", "label": "Being recognised by my teachers or peers",
             "trait_weights": {"Ambition": 0.2, "Social": 0.3}},
            {"value": "D", "label": "Learning something completely new",
             "trait_weights": {"Curiosity": 0.3, "Growth": 0.2}},
        ],
    },
    {
        "id": "motiv_004",
        "category": "Motivation",
        "question": "Which activity sounds most enjoyable?",
        "display": "choose",
        "options": [
            {"value": "A", "label": "🧩 A challenging puzzle or riddle",
             "trait_weights": {"Analytical": 0.3, "Persistence": 0.2}},
            {"value": "B", "label": "✍️ Writing a story or poem",
             "trait_weights": {"Creativity": 0.3, "Verbal": 0.2}},
            {"value": "C", "label": "🔧 Fixing or building something with my hands",
             "trait_weights": {"Practical": 0.3, "Spatial": 0.2}},
            {"value": "D", "label": "🎤 Debating or discussing ideas with friends",
             "trait_weights": {"Verbal": 0.3, "Social": 0.2}},
        ],
    },
    {
        "id": "motiv_005",
        "category": "Motivation",
        "question": "What would you rather do on a free Saturday?",
        "display": "choose",
        "options": [
            {"value": "A", "label": "Visit a science museum or exhibition",
             "trait_weights": {"Curiosity": 0.3, "Analytical": 0.2}},
            {"value": "B", "label": "Read a novel or watch a thought-provoking film",
             "trait_weights": {"Verbal": 0.2, "Reflective": 0.3}},
            {"value": "C", "label": "Play sports or do something active",
             "trait_weights": {"Active": 0.3, "Social": 0.2}},
            {"value": "D", "label": "Hang out with friends and talk about life",
             "trait_weights": {"Social": 0.3, "Empathy": 0.2}},
        ],
    },
    
    # ── Problem-Solving Style ─────────────────────────────────────────────────
    {
        "id": "prob_001",
        "category": "Problem-Solving",
        "question": "When faced with a difficult problem, what do you usually do?",
        "display": "choose",
        "options": [
            {"value": "A", "label": "Break it into smaller parts and tackle each one",
             "trait_weights": {"Analytical": 0.3, "Methodical": 0.2}},
            {"value": "B", "label": "Think of similar problems I've solved before",
             "trait_weights": {"Experiential": 0.3, "Pragmatic": 0.2}},
            {"value": "C", "label": "Brainstorm many possible solutions",
             "trait_weights": {"Creativity": 0.3, "Openness": 0.2}},
            {"value": "D", "label": "Ask someone for their perspective",
             "trait_weights": {"Collaboration": 0.3, "Social": 0.2}},
        ],
    },
    {
        "id": "prob_002",
        "category": "Problem-Solving",
        "question": "How do you prefer to learn something new?",
        "display": "choose",
        "options": [
            {"value": "A", "label": "Read instructions or watch a demonstration",
             "trait_weights": {"Visual": 0.3, "Methodical": 0.2}},
            {"value": "B", "label": "Try it myself and learn from mistakes",
             "trait_weights": {"Boldness": 0.3, "Experiential": 0.2}},
            {"value": "C", "label": "Discuss it with others to understand better",
             "trait_weights": {"Social": 0.3, "Verbal": 0.2}},
            {"value": "D", "label": "Draw diagrams or make notes to organise the information",
             "trait_weights": {"Visual": 0.2, "Methodical": 0.3}},
        ],
    },
    {
        "id": "prob_003",
        "category": "Problem-Solving",
        "question": "When your first attempt at solving a problem fails, you usually:",
        "display": "choose",
        "options": [
            {"value": "A", "label": "Try a completely different approach",
             "trait_weights": {"Adaptability": 0.3, "Creativity": 0.2}},
            {"value": "B", "label": "Keep trying, making small adjustments",
             "trait_weights": {"Persistence": 0.4, "Methodical": 0.1}},
            {"value": "C", "label": "Look up how others have solved it",
             "trait_weights": {"Resourcefulness": 0.3, "Collaboration": 0.2}},
            {"value": "D", "label": "Take a break and come back with fresh eyes",
             "trait_weights": {"Reflective": 0.3, "Patience": 0.2}},
        ],
    },
    {
        "id": "prob_004",
        "category": "Problem-Solving",
        "question": "Which thinking style sounds more like you?",
        "display": "choose",
        "options": [
            {"value": "A", "label": "🎯 Focused — I dive deep into one thing at a time",
             "trait_weights": {"Methodical": 0.3, "Persistence": 0.2}},
            {"value": "B", "label": "🌈 Curious — I explore many different ideas",
             "trait_weights": {"Curiosity": 0.3, "Creativity": 0.2}},
            {"value": "C", "label": "🔄 Flexible — I adapt my thinking to the situation",
             "trait_weights": {"Adaptability": 0.3, "Pragmatic": 0.2}},
            {"value": "D", "label": "📊 Systematic — I follow logical steps and patterns",
             "trait_weights": {"Analytical": 0.3, "Methodical": 0.2}},
        ],
    },
    
    # ── Collaboration & Communication ────────────────────────────────────────
    {
        "id": "collab_001",
        "category": "Collaboration",
        "question": "In a group project, which role suits you best?",
        "display": "choose",
        "options": [
            {"value": "A", "label": "The organiser who keeps everyone on track",
             "trait_weights": {"Leadership": 0.3, "Methodical": 0.2}},
            {"value": "B", "label": "The idea generator who thinks creatively",
             "trait_weights": {"Creativity": 0.3, "Openness": 0.2}},
            {"value": "C", "label": "The researcher who finds the facts",
             "trait_weights": {"Analytical": 0.3, "Curiosity": 0.2}},
            {"value": "D", "label": "The communicator who presents the work",
             "trait_weights": {"Verbal": 0.3, "Social": 0.2}},
        ],
    },
    {
        "id": "collab_002",
        "category": "Collaboration",
        "question": "When you disagree with someone, you usually:",
        "display": "choose",
        "options": [
            {"value": "A", "label": "Explain your reasoning calmly and listen to theirs",
             "trait_weights": {"Verbal": 0.2, "Empathy": 0.3}},
            {"value": "B", "label": "Stick firmly to your position if you know you're right",
             "trait_weights": {"Conviction": 0.3, "Independence": 0.2}},
            {"value": "C", "label": "Look for common ground and compromise",
             "trait_weights": {"Collaboration": 0.3, "Empathy": 0.2}},
            {"value": "D", "label": "Agree to disagree and move on",
             "trait_weights": {"Openness": 0.2, "Pragmatic": 0.3}},
        ],
    },
    {
        "id": "collab_003",
        "category": "Collaboration",
        "question": "What matters most to you in a team?",
        "display": "choose",
        "options": [
            {"value": "A", "label": "Everyone contributes their fair share",
             "trait_weights": {"Fairness": 0.3, "Reliability": 0.2}},
            {"value": "B", "label": "Ideas are heard and respected",
             "trait_weights": {"Openness": 0.3, "Empathy": 0.2}},
            {"value": "C", "label": "The team produces high-quality work",
             "trait_weights": {"Conscientiousness": 0.3, "Ambition": 0.2}},
            {"value": "D", "label": "The process is organised and efficient",
             "trait_weights": {"Methodical": 0.3, "Leadership": 0.2}},
        ],
    },
    
    # ── Learning Style ────────────────────────────────────────────────────────
    {
        "id": "learn_001",
        "category": "Learning",
        "question": "How do you remember things best?",
        "display": "choose",
        "options": [
            {"value": "A", "label": "Writing things down or drawing diagrams",
             "trait_weights": {"Visual": 0.3, "Methodical": 0.2}},
            {"value": "B", "label": "Discussing and explaining to others",
             "trait_weights": {"Verbal": 0.3, "Social": 0.2}},
            {"value": "C", "label": "Doing hands-on activities and experiments",
             "trait_weights": {"Kinesthetic": 0.3, "Pragmatic": 0.2}},
            {"value": "D", "label": "Reading and re-reading notes silently",
             "trait_weights": {"Reflective": 0.3, "Independent": 0.2}},
        ],
    },
    {
        "id": "learn_002",
        "category": "Learning",
        "question": "When studying for a test, what helps you most?",
        "display": "choose",
        "options": [
            {"value": "A", "label": "Practice questions and past papers",
             "trait_weights": {"Pragmatic": 0.3, "Persistence": 0.2}},
            {"value": "B", "label": "Making colourful notes and summaries",
             "trait_weights": {"Creativity": 0.2, "Visual": 0.3}},
            {"value": "C", "label": "Teaching the material to a friend",
             "trait_weights": {"Verbal": 0.3, "Collaboration": 0.2}},
            {"value": "D", "label": "Creating mnemonics and memory tricks",
             "trait_weights": {"Creativity": 0.3, "Strategic": 0.2}},
        ],
    },
    {
        "id": "learn_003",
        "category": "Learning",
        "question": "What type of class do you enjoy most?",
        "display": "choose",
        "options": [
            {"value": "A", "label": "📐 Mathematics — I love numbers and logic",
             "trait_weights": {"Analytical": 0.3, "Quantitative": 0.2}},
            {"value": "B", "label": "📝 English / Literature — I love words and stories",
             "trait_weights": {"Verbal": 0.3, "Creative": 0.2}},
            {"value": "C", "label": "🔬 Science — I love experiments and discovery",
             "trait_weights": {"Curiosity": 0.3, "Analytical": 0.2}},
            {"value": "D", "label": "🎨 Creative Arts — I love expressing myself",
             "trait_weights": {"Creativity": 0.3, "Artistic": 0.2}},
        ],
    },
    
    # ── Career Orientation ────────────────────────────────────────────────────
    {
        "id": "career_001",
        "category": "Career",
        "question": "What kind of work environment appeals to you?",
        "display": "choose",
        "options": [
            {"value": "A", "label": "A lab or workshop where I can experiment",
             "trait_weights": {"Practical": 0.3, "Curiosity": 0.2}},
            {"value": "B", "label": "An office where I can collaborate with a team",
             "trait_weights": {"Social": 0.3, "Collaboration": 0.2}},
            {"value": "C", "label": "Outdoors or in the field, exploring new places",
             "trait_weights": {"Adventurous": 0.3, "Independent": 0.2}},
            {"value": "D", "label": "A quiet space where I can focus independently",
             "trait_weights": {"Independent": 0.3, "Reflective": 0.2}},
        ],
    },
    {
        "id": "career_002",
        "category": "Career",
        "question": "Which would you find most fulfilling?",
        "display": "choose",
        "options": [
            {"value": "A", "label": "Inventing something that changes lives",
             "trait_weights": {"Creativity": 0.3, "Ambition": 0.2}},
            {"value": "B", "label": "Teaching and inspiring the next generation",
             "trait_weights": {"Empathy": 0.3, "Verbal": 0.2}},
            {"value": "C", "label": "Leading a team to achieve a big goal",
             "trait_weights": {"Leadership": 0.3, "Ambition": 0.2}},
            {"value": "D", "label": "Analysing data to solve complex problems",
             "trait_weights": {"Analytical": 0.3, "Quantitative": 0.2}},
        ],
    },
    {
        "id": "career_003",
        "category": "Career",
        "question": "What kind of impact would you like to have?",
        "display": "choose",
        "options": [
            {"value": "A", "label": "🌍 Solving big global challenges like climate change or disease",
             "trait_weights": {"Altruism": 0.3, "Ambition": 0.2}},
            {"value": "B", "label": "🏘️ Making life better in my local community",
             "trait_weights": {"Empathy": 0.3, "Community": 0.2}},
            {"value": "C", "label": "💡 Creating new technology or innovations",
             "trait_weights": {"Creativity": 0.3, "Technical": 0.2}},
            {"value": "D", "label": "📊 Helping organisations make better decisions",
             "trait_weights": {"Analytical": 0.3, "Strategic": 0.2}},
        ],
    },
    
    # ── Reflection / Growth Mindset ───────────────────────────────────────────
    {
        "id": "reflect_001",
        "category": "Reflection",
        "question": "What do you do when you get a poor grade on a test?",
        "display": "choose",
        "options": [
            {"value": "A", "label": "Analyse what went wrong and study those areas",
             "trait_weights": {"Growth": 0.3, "Analytical": 0.2}},
            {"value": "B", "label": "Feel discouraged but try harder next time",
             "trait_weights": {"Persistence": 0.3, "Resilience": 0.2}},
            {"value": "C", "label": "Ask the teacher or friends for help understanding",
             "trait_weights": {"Collaboration": 0.3, "Openness": 0.2}},
            {"value": "D", "label": "Tell myself it's just one test and move forward",
             "trait_weights": {"Resilience": 0.3, "Pragmatic": 0.2}},
        ],
    },
    {
        "id": "reflect_002",
        "category": "Reflection",
        "question": "Which statement resonates most with you?",
        "display": "choose",
        "options": [
            {"value": "A", "label": "Mistakes are opportunities to learn and grow",
             "trait_weights": {"Growth": 0.4, "Resilience": 0.1}},
            {"value": "B", "label": "Practice and effort matter more than natural talent",
             "trait_weights": {"Persistence": 0.3, "Growth": 0.2}},
            {"value": "C", "label": "I want to understand things deeply, not just memorise",
             "trait_weights": {"Curiosity": 0.3, "Analytical": 0.2}},
            {"value": "D", "label": "Challenges make me stronger and smarter",
             "trait_weights": {"Resilience": 0.3, "Boldness": 0.2}},
        ],
    },
    {
        "id": "reflect_003",
        "category": "Reflection",
        "question": "How do you feel about trying something you're not good at?",
        "display": "choose",
        "options": [
            {"value": "A", "label": "Excited — I love the challenge of improving",
             "trait_weights": {"Boldness": 0.3, "Growth": 0.2}},
            {"value": "B", "label": "Nervous but willing to give it a shot",
             "trait_weights": {"Courage": 0.3, "Openness": 0.2}},
            {"value": "C", "label": "I'd rather focus on what I'm already good at",
             "trait_weights": {"Pragmatic": 0.3, "Confidence": 0.2}},
            {"value": "D", "label": "I'd try it if a friend or teacher encouraged me",
             "trait_weights": {"Collaboration": 0.3, "Openness": 0.2}},
        ],
    },
]


def get_psychometric_card(card_id: str) -> PsychometricCard | None:
    """Look up a specific psychometric card by ID."""
    for card in PSYCHOMETRIC_CARDS:
        if card["id"] == card_id:
            return card
    return None


def get_cards_by_category(category: str) -> List[PsychometricCard]:
    """Get all cards for a specific trait category."""
    return [c for c in PSYCHOMETRIC_CARDS if c["category"] == category]


def pick_cards_for_session(count: int = 3,
                            exclude_ids: List[str] | None = None,
                            preferred_categories: List[str] | None = None) -> List[PsychometricCard]:
    """
    Pick a balanced set of psychometric cards for a challenge session.
    
    Args:
      count: Number of cards to pick.
      exclude_ids: Card IDs to exclude (already shown).
      preferred_categories: If set, prioritise these categories.
    
    Returns:
      A list of PsychometricCard objects.
    """
    import random
    pool = [c for c in PSYCHOMETRIC_CARDS if not exclude_ids or c["id"] not in exclude_ids]
    
    if preferred_categories and pool:
        preferred = [c for c in pool if c["category"] in preferred_categories]
        if preferred:
            # Pick at least 1 from preferred, rest from whole pool
            chosen = [random.choice(preferred)]
            pool = [c for c in pool if c["id"] != chosen[0]["id"]]
            count -= 1
            if count > 0:
                chosen.extend(random.sample(pool, min(count, len(pool))))
            return chosen
    
    selected = random.sample(pool, min(count, len(pool)))
    return selected


def get_categories() -> List[str]:
    """Get all available psychometric card categories."""
    return list(set(c["category"] for c in PSYCHOMETRIC_CARDS))


# ── Flatten for API responses ────────────────────────────────────────────────
def flatten_card_for_api(card: PsychometricCard) -> Dict:
    """Remove trait_weights from options for frontend consumption."""
    return {
        "id": card["id"],
        "category": card["category"],
        "question": card["question"],
        "display": card["display"],
        "options": [
            {"value": o["value"], "label": o["label"]}
            for o in card["options"]
        ],
    }
