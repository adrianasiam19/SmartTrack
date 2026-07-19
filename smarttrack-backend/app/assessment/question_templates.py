"""
question_templates.py
─────────────────────
Template engine for the Atlas Challenge Arena question bank.

Each template defines a parameterized question schema. When rendered with
different parameter values it produces distinct question variants, ensuring
students rarely see the exact same question sequence (anti-cheating).

Two-layer parameter system:
  1. param_generators — produce independent random values (e.g. start, step, factor)
  2. computed_params  — derive values from already-generated params (e.g. next1, correct, wrong1)
"""

import hashlib
import random
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field


# ── Type aliases ────────────────────────────────────────────────────────────
Params = Dict[str, Any]
OptionMap = Dict[str, str]  # {"A": "...", "B": "...", ...}


@dataclass
class QuestionVariant:
    """A fully rendered question ready for the database or API response."""
    question: str
    options: OptionMap
    correct_answer: str  # "A", "B", "C", or "D"
    explanation: str


@dataclass
class QuestionTemplate:
    """
    A parameterized question template.

    Fields:
      template_id:  Unique identifier for this template family.
      arena:        "logic" | "quantitative" | "scientific" | "communication"
      domain:       "Logic" | "Math" | "Science" | "Verbal" | "General"
      difficulty_tier: "Bronze" | "Silver" | "Gold"
      shs_levels:   Which SHS levels this template is appropriate for.
      irt_base:     Base IRT parameters (a, b, c).
      question_template:  Python format string with {param} placeholders.
      options_template:   Dict of format strings for each option key.
      correct_answer:     Which option key is correct (e.g. "B").
      explanation_template: Template for the explanation text.
      param_generators:   Dict mapping param name → callable(rng) → value.
      computed_params:    Dict mapping param name → callable(params_dict) → value.
                          Derives values from already-generated params.
    """
    template_id: str
    arena: str
    domain: str
    difficulty_tier: str
    shs_levels: List[str]
    irt_base: Tuple[float, float, float]
    question_template: str
    options_template: Dict[str, str]
    correct_answer: str
    explanation_template: str
    param_generators: Dict[str, Callable] = field(default_factory=dict)
    computed_params: Dict[str, Callable[[Params], Any]] = field(default_factory=dict)

    def render(self, seed: Optional[int] = None, **overrides) -> QuestionVariant:
        rng = random.Random(seed) if seed is not None else random
        params: Params = {}
        for name, gen in self.param_generators.items():
            params[name] = overrides[name] if name in overrides else gen(rng)
        for k, v in overrides.items():
            if k not in params:
                params[k] = v
        for name, fn in self.computed_params.items():
            if name not in overrides:
                params[name] = fn(params)
        question = self.question_template.format(**params)
        explanation = self.explanation_template.format(**params)
        options: OptionMap = {}
        for key, tmpl in self.options_template.items():
            options[key] = tmpl.format(**params)
        return QuestionVariant(question=question, options=options,
                               correct_answer=self.correct_answer, explanation=explanation)

    def generate_variant_id(self, params: Params) -> str:
        raw = f"{self.template_id}:{sorted(params.items())}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]

    def difficulty_b_for_tier(self, rng: random.Random) -> float:
        ranges = {"Bronze": (-1.5, -0.5), "Silver": (-0.5, 0.5), "Gold": (0.5, 1.5)}
        lo, hi = ranges.get(self.difficulty_tier, (-0.5, 0.5))
        return round(rng.uniform(lo, hi), 2)

    def to_question_dict(self, variant: QuestionVariant, idx: int, rng: random.Random) -> Dict:
        b = self.difficulty_b_for_tier(rng)
        a, _, c = self.irt_base
        return {
            "id": idx, "arena": self.arena, "domain": self.domain,
            "difficulty_tier": self.difficulty_tier, "shs_levels": self.shs_levels,
            "difficulty_a": a, "difficulty_b": b, "difficulty_c": c,
            "question": variant.question, "options": variant.options,
            "correct_answer": variant.correct_answer, "explanation": variant.explanation,
            "template_id": self.template_id,
        }


# ── Helper generators ────────────────────────────────────────────────────────

def int_between(lo: int, hi: int) -> Callable:
    return lambda rng: rng.randint(lo, hi)

def pick_from(options: List[Any]) -> Callable:
    return lambda rng: rng.choice(options)

def always(value: Any) -> Callable:
    return lambda rng: value


def _make_scenario_template(tid, arena, domain, tier, levels, irt, scenarios,
                             qtemplate, o_template, correct_key="A", has_q=False):
    """Factory: scenario-based template where a single _pick returns a complete matched dict."""
    def _pick(rng):
        s = rng.choice(scenarios)
        return {k: v for k, v in zip(
            ["scenario","q","opt_a","opt_b","opt_c","opt_d","exp"
             ] if has_q else ["scenario","opt_a","opt_b","opt_c","opt_d","exp"],
            s)}
    keys = ["scenario","q","opt_a","opt_b","opt_c","opt_d","exp"] if has_q \
           else ["scenario","opt_a","opt_b","opt_c","opt_d","exp"]
    cp = {k: lambda p, k=k: p["_s"][k] for k in keys}
    return QuestionTemplate(
        template_id=tid, arena=arena, domain=domain,
        difficulty_tier=tier, shs_levels=levels, irt_base=irt,
        question_template=qtemplate, options_template=o_template,
        correct_answer=correct_key, explanation_template="{exp}",
        param_generators={"_s": _pick}, computed_params=cp,
    )


# ══════════════════════════════════════════════════════════════════════════════
# CONTENT TEMPLATES — Cleared. Add your own templates here.
# ══════════════════════════════════════════════════════════════════════════════

def _logic_templates() -> List[QuestionTemplate]:
    """Content cleared."""
    return []


def _quant_templates() -> List[QuestionTemplate]:
    """Content cleared."""
    return []


def _sci_templates() -> List[QuestionTemplate]:
    """Content cleared."""
    return []


def _comm_templates() -> List[QuestionTemplate]:
    """Content cleared."""
    return []


# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════════════════════════

def build_all_templates() -> List[QuestionTemplate]:
    templates: List[QuestionTemplate] = []
    templates.extend(_logic_templates())
    templates.extend(_quant_templates())
    templates.extend(_sci_templates())
    templates.extend(_comm_templates())
    return templates


def generate_bank(templates: List[QuestionTemplate],
                  questions_per_template: int = 5,
                  seed: int = 42) -> List[Dict]:
    """Generate a full question bank from templates with per-template deterministic seeds."""
    rng = random.Random(seed)
    bank = []
    idx = 1
    for tmpl in templates:
        tmpl_seed = int(hashlib.md5(tmpl.template_id.encode()).hexdigest()[:8], 16)
        for v in range(questions_per_template):
            variant = tmpl.render(seed=tmpl_seed + v * 7919)
            bank.append(tmpl.to_question_dict(variant, idx, rng))
            idx += 1
    return bank
