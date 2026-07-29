"""
Internal Ghana SHS curriculum topic anchors for challenge generation.

Phase mapping (never shown to learners as SHS labels):
  Phase 1 → SHS 1 topics only
  Phase 2 → SHS 2 topics only
  Phase 3 → SHS 3 emphasis, with SHS 1–2 reinforcement

Each topic includes a reliable educational image_query so diagrams can be
resolved BEFORE the question is written (image-first alignment).
"""
from __future__ import annotations

import random
from typing import Any

# topic, image_query (search), concept_focus (what questions may ask)
CURRICULUM_TOPICS: dict[int, dict[str, list[dict[str, str]]]] = {
    1: {
        "integrated_science": [
            {
                "topic": "Plant and animal cells",
                "image_query": "simple plant cell diagram organelles",
                "focus": "Identify the overall cell type or main visible parts as a whole (cell wall, chloroplast region) without lettered labels.",
            },
            {
                "topic": "Diffusion and osmosis",
                "image_query": "osmosis diagram semi permeable membrane",
                "focus": "Identify the process shown (osmosis/diffusion) and direction of water/particle movement.",
            },
            {
                "topic": "Photosynthesis overview",
                "image_query": "photosynthesis process diagram leaf",
                "focus": "Identify photosynthesis inputs/outputs or that the diagram shows photosynthesis.",
            },
            {
                "topic": "Human digestive system overview",
                "image_query": "human digestive system diagram",
                "focus": "Identify the organ system shown and its overall function.",
            },
            {
                "topic": "Simple electrical circuit",
                "image_query": "simple series circuit diagram battery bulb",
                "focus": "Identify circuit type or role of battery/bulb in the whole circuit.",
            },
            {
                "topic": "States of matter",
                "image_query": "states of matter particle diagram solid liquid gas",
                "focus": "Match particle arrangement to solid, liquid, or gas.",
            },
        ],
        "social_studies": [
            {
                "topic": "Map reading basics",
                "image_query": "",
                "focus": "Explain how to read directions, symbols, or scale on a map using a text scenario.",
            },
            {
                "topic": "Ghana's physical environment",
                "image_query": "",
                "focus": "Describe Ghana's location, neighbours, or key physical features from written facts.",
            },
            {
                "topic": "Environmental sanitation",
                "image_query": "",
                "focus": "Identify pollution/sanitation problems and good community responses from a written scenario.",
            },
        ],
        "core_maths": [
            {
                "topic": "Number line",
                "image_query": "number line integers educational diagram",
                "focus": "Read values or compare positions on a number line.",
            },
            {
                "topic": "Simple bar chart",
                "image_query": "simple bar chart educational graph",
                "focus": "Read the tallest bar or compare categories from the chart.",
            },
        ],
        "english": [
            {
                "topic": "Reading comprehension",
                "image_query": "",
                "focus": "Infer main idea, mood, or purpose from a short written passage.",
            },
        ],
    },
    2: {
        "integrated_science": [
            {
                "topic": "Respiratory system",
                "image_query": "human respiratory system lungs diagram",
                "focus": "Identify the system shown and overall gas exchange role.",
            },
            {
                "topic": "Circulatory system / heart",
                "image_query": "human heart external anatomy diagram",
                "focus": "Identify that the diagram shows the heart/circulatory organ and its pumping role.",
            },
            {
                "topic": "Food chains and ecosystems",
                "image_query": "food chain ecosystem diagram producers consumers",
                "focus": "Identify producers/consumers or energy flow direction in the whole web.",
            },
            {
                "topic": "Acids, bases and indicators",
                "image_query": "pH scale diagram acids bases",
                "focus": "Interpret acidic vs basic regions on a pH scale diagram.",
            },
            {
                "topic": "Reflection of light",
                "image_query": "plane mirror reflection ray diagram incident reflected normal",
                "focus": "Use the ray diagram: incident ray, normal, reflected ray, and equal angles.",
            },
            {
                "topic": "Reproduction in flowering plants",
                "image_query": "flower structure diagram petals stigma ovary",
                "focus": "Identify that the diagram shows a flower and relate to reproduction overall.",
            },
        ],
        "social_studies": [
            {
                "topic": "Climate and vegetation",
                "image_query": "",
                "focus": "Relate climate zones to vegetation patterns using written descriptions.",
            },
            {
                "topic": "Population and settlement",
                "image_query": "",
                "focus": "Compare urban and rural settlement features and related social issues from text.",
            },
            {
                "topic": "Natural resources of Ghana",
                "image_query": "",
                "focus": "Explain the economic importance of Ghana's natural resources from a written scenario.",
            },
        ],
        "core_maths": [
            {
                "topic": "Linear graphs",
                "image_query": "linear graph coordinate plane educational",
                "focus": "Read slope/intercept concepts from a straight-line graph.",
            },
            {
                "topic": "Pie charts",
                "image_query": "pie chart educational percentages",
                "focus": "Compare sectors or estimate proportions from the pie chart.",
            },
        ],
        "english": [
            {
                "topic": "Inferring meaning from text",
                "image_query": "",
                "focus": "Infer purpose, audience, or main idea from a short written description or passage.",
            },
        ],
    },
    3: {
        "integrated_science": [
            {
                "topic": "Genetics and inheritance overview",
                "image_query": "Punnett square diagram genetics",
                "focus": "Interpret a Punnett square outcome at a conceptual level.",
            },
            {
                "topic": "Nervous system / neuron",
                "image_query": "neuron structure diagram axon dendrite",
                "focus": "Identify that the diagram shows a neuron and its signalling role.",
            },
            {
                "topic": "Electromagnetic spectrum / waves",
                "image_query": "electromagnetic spectrum diagram",
                "focus": "Identify the spectrum shown and compare wave regions conceptually.",
            },
            {
                "topic": "Organic chemistry functional groups overview",
                "image_query": "hydrocarbon molecule structure diagram",
                "focus": "Identify that a molecular structure diagram is shown and relate to carbon compounds.",
            },
            {
                "topic": "Ecology and pollution (reinforcement)",
                "image_query": "water pollution industrial waste illustration",
                "focus": "Identify the environmental issue and a mitigation strategy.",
            },
            {
                "topic": "Cell division overview (reinforcement)",
                "image_query": "mitosis stages diagram educational",
                "focus": "Identify mitosis as the process shown at a high level.",
            },
        ],
        "social_studies": [
            {
                "topic": "Governance and constitution",
                "image_query": "",
                "focus": "Explain branches of government or democratic participation from written facts.",
            },
            {
                "topic": "Globalisation and development",
                "image_query": "",
                "focus": "Relate trade, interdependence, or development using a written scenario.",
            },
            {
                "topic": "Map skills advanced (reinforcement)",
                "image_query": "",
                "focus": "Interpret map types (e.g. relief/contour concepts) from written descriptions, not a figure.",
            },
        ],
        "core_maths": [
            {
                "topic": "Trigonometry right triangle",
                "image_query": "right triangle trigonometry diagram opposite adjacent",
                "focus": "Identify opposite/adjacent/hypotenuse relationships from the triangle figure.",
            },
            {
                "topic": "Statistics graphs",
                "image_query": "histogram frequency chart educational",
                "focus": "Read distribution shape or modal class conceptually from the chart.",
            },
        ],
        "english": [
            {
                "topic": "Critical reading of persuasive text",
                "image_query": "",
                "focus": "Identify purpose, tone, or intended audience of a short written campaign or notice.",
            },
        ],
    },
}


def phase_curriculum_label(phase_number: int) -> str:
    """Internal depth label for prompts — never shown in learner UI."""
    return {1: "SHS 1", 2: "SHS 2", 3: "SHS 3 (with SHS 1–2 reinforcement)"}.get(
        phase_number, "SHS 1"
    )


def pick_curriculum_topic(
    phase_number: int,
    subject: str,
    rng: random.Random | None = None,
) -> dict[str, str] | None:
    rng = rng or random.Random()
    phase = phase_number if phase_number in CURRICULUM_TOPICS else 1
    # Phase 3 may reinforce earlier phases
    pools: list[dict[str, str]] = list(CURRICULUM_TOPICS.get(phase, {}).get(subject) or [])
    if phase >= 3:
        for earlier in (1, 2):
            pools.extend(CURRICULUM_TOPICS.get(earlier, {}).get(subject) or [])
    if not pools:
        # fallback any subject topics in phase
        for topics in CURRICULUM_TOPICS.get(phase, {}).values():
            pools.extend(topics)
    if not pools:
        return None
    return dict(rng.choice(pools))


def topic_prompt_block(topic: dict[str, str] | None) -> str:
    if not topic:
        return ""
    lines = [
        f"Curriculum topic (internal): {topic.get('topic')}.",
        f"Concept focus: {topic.get('focus')}.",
    ]
    image_query = (topic.get("image_query") or "").strip()
    if image_query:
        lines.append(f"Preferred diagram search: {image_query}.")
    else:
        lines.append("Do NOT invent or refer to any diagram, map, image, or illustration.")
    return "\n".join(lines) + "\n"
