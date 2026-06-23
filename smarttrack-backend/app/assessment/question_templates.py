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
# LOGIC ARENA
# ══════════════════════════════════════════════════════════════════════════════

def _logic_templates() -> List[QuestionTemplate]:
    t: List[QuestionTemplate] = []

    # ── Sequences ────────────────────────────────────────────────────────
    t.append(QuestionTemplate(
        template_id="logic-seq-add-001", arena="logic", domain="Logic",
        difficulty_tier="Bronze", shs_levels=["SHS 1"], irt_base=(1.0, -1.0, 0.25),
        question_template="{a}, {b}, {c}, {d}, ?",
        options_template={"A": "{w1}", "B": "{correct}", "C": "{w2}", "D": "{w3}"},
        correct_answer="B",
        explanation_template="Each term increases by {step}: {a} → {step}+{a}={b} → ... → {d}+{step}={correct}.",
        param_generators={"start": int_between(1, 10), "step": pick_from([1, 2, 3, 5, 10])},
        computed_params={
            "a": lambda p: p["start"], "b": lambda p: p["start"]+p["step"],
            "c": lambda p: p["start"]+2*p["step"], "d": lambda p: p["start"]+3*p["step"],
            "correct": lambda p: p["start"]+4*p["step"],
            "w1": lambda p: p["start"]+4*p["step"]+1,
            "w2": lambda p: p["start"]+4*p["step"]-1,
            "w3": lambda p: p["start"]+4*p["step"]+p["step"],
        },
    ))
    t.append(QuestionTemplate(
        template_id="logic-seq-sub-001", arena="logic", domain="Logic",
        difficulty_tier="Bronze", shs_levels=["SHS 1"], irt_base=(1.0, -1.0, 0.25),
        question_template="{a}, {b}, {c}, {d}, ?",
        options_template={"A": "{correct}", "B": "{w1}", "C": "{w2}", "D": "{w3}"},
        correct_answer="A",
        explanation_template="Each term decreases by {diff}: {a} → {a}-{diff}={b} → ... → {d}-{diff}={correct}.",
        param_generators={"start": int_between(30, 100), "diff": pick_from([3,4,5,6,7,8,9,10])},
        computed_params={
            "a": lambda p: p["start"], "b": lambda p: p["start"]-p["diff"],
            "c": lambda p: p["start"]-2*p["diff"], "d": lambda p: p["start"]-3*p["diff"],
            "correct": lambda p: p["start"]-4*p["diff"],
            "w1": lambda p: p["start"]-4*p["diff"]+p["diff"],
            "w2": lambda p: p["start"]-4*p["diff"]-p["diff"],
            "w3": lambda p: abs(p["start"]-4*p["diff"]+1),
        },
    ))
    t.append(QuestionTemplate(
        template_id="logic-seq-mul-001", arena="logic", domain="Logic",
        difficulty_tier="Silver", shs_levels=["SHS 1","SHS 2"], irt_base=(1.2, 0.0, 0.25),
        question_template="{a}, {b}, {c}, {d}, ?",
        options_template={"A": "{w1}", "B": "{w2}", "C": "{correct}", "D": "{w3}"},
        correct_answer="C",
        explanation_template="Each term ×{factor}: {a}×{factor}={b} → ... → {d}×{factor}={correct}.",
        param_generators={"start": int_between(1,5), "factor": pick_from([2,3,4,5])},
        computed_params={
            "a": lambda p: p["start"], "b": lambda p: p["start"]*p["factor"],
            "c": lambda p: p["start"]*p["factor"]**2, "d": lambda p: p["start"]*p["factor"]**3,
            "correct": lambda p: p["start"]*p["factor"]**4,
            "w1": lambda p: p["start"]*p["factor"]**4+1,
            "w2": lambda p: p["start"]*p["factor"]**4-1,
            "w3": lambda p: p["start"]*p["factor"]**3,
        },
    ))
    t.append(QuestionTemplate(
        template_id="logic-seq-fib-001", arena="logic", domain="Logic",
        difficulty_tier="Gold", shs_levels=["SHS 2","SHS 3"], irt_base=(1.4, 1.0, 0.25),
        question_template="{a}, {b}, {c}, {d}, ?",
        options_template={"A": "{w1}", "B": "{w2}", "C": "{correct}", "D": "{w3}"},
        correct_answer="C",
        explanation_template="Each term is sum of previous two: {a}+{b}={c}, {b}+{c}={d}, so {c}+{d}={correct}.",
        param_generators={"sa": int_between(1,5), "sb": int_between(3,8)},
        computed_params={
            "a": lambda p: p["sa"], "b": lambda p: p["sb"],
            "c": lambda p: p["sa"]+p["sb"], "d": lambda p: p["sa"]+2*p["sb"],
            "correct": lambda p: 2*p["sa"]+3*p["sb"],
            "w1": lambda p: 2*p["sa"]+3*p["sb"]+1,
            "w2": lambda p: 2*p["sa"]+3*p["sb"]-1,
            "w3": lambda p: 3*p["sa"]+3*p["sb"],
        },
    ))
    # Pattern cycles
    t.append(QuestionTemplate(
        template_id="logic-pat-001", arena="logic", domain="Logic",
        difficulty_tier="Bronze", shs_levels=["SHS 1"], irt_base=(1.0, -1.0, 0.25),
        question_template="What is the next shape in the pattern: {pattern_desc}",
        options_template={"A": "{opt_a}", "B": "{opt_b}", "C": "{opt_c}", "D": "{opt_d}"},
        correct_answer="A", explanation_template="{exp}",
        param_generators={
            "_s": pick_from([
                {"pattern_desc":"circle, square, triangle, circle, square, ?",
                 "opt_a":"triangle","opt_b":"circle","opt_c":"square","opt_d":"diamond",
                 "exp":"The pattern cycles through three shapes: circle → square → triangle → repeat."},
                {"pattern_desc":"△, ○, □, △, ○, ?",
                 "opt_a":"□","opt_b":"△","opt_c":"○","opt_d":"☆",
                 "exp":"The pattern is △ → ○ → □ in a repeating cycle."},
                {"pattern_desc":"★, ◆, ●, ★, ◆, ?",
                 "opt_a":"●","opt_b":"★","opt_c":"◆","opt_d":"▲",
                 "exp":"The sequence cycles through star, diamond, circle repeatedly."},
                {"pattern_desc":"red, blue, green, red, blue, ?",
                 "opt_a":"green","opt_b":"blue","opt_c":"red","opt_d":"yellow",
                 "exp":"Colours cycle red → blue → green → repeat."},
            ]),
        },
        computed_params={
            "pattern_desc": lambda p: p["_s"]["pattern_desc"],
            "opt_a": lambda p: p["_s"]["opt_a"], "opt_b": lambda p: p["_s"]["opt_b"],
            "opt_c": lambda p: p["_s"]["opt_c"], "opt_d": lambda p: p["_s"]["opt_d"],
            "exp": lambda p: p["_s"]["exp"],
        },
    ))

    # ── Analogies (scenario-based) ───────────────────────────────────────
    _ana_bronze = [
        ("Hand","grasp","Eye","see","Touch","Smell","Taste","Hear",
         "A hand grasps; an eye sees. Organ → primary function."),
        ("Bird","flies","Fish","swims","walks","jumps","crawls","sleeps",
         "A bird flies; a fish swims. Animal → mode of movement."),
        ("Doctor","heals","Teacher","educates","sells","builds","drives","cooks",
         "A doctor heals; a teacher educates. Professional → action."),
        ("Sugar","sweet","Lemon","sour","bitter","salty","spicy","bland",
         "Sugar is sweet; lemon is sour. Item → taste."),
        ("Pencil","writes","Brush","paints","erases","draws","carves","prints",
         "A pencil writes; a brush paints. Tool → use."),
    ]
    _ana_silver = [
        ("Tree","wood","Book","paper","plastic","metal","glass","cloth",
         "A tree is made of wood; a book is made of paper. Object → material."),
        ("Key","opens","Password","unlocks","closes","locks","hides","reveals",
         "A key opens a lock; a password unlocks an account. Tool → what it secures."),
        ("Clock","time","Thermometer","temperature","pressure","speed","weight","distance",
         "A clock measures time; a thermometer measures temperature. Instrument → measurement."),
        ("Map","location","Recipe","instructions","history","weather","people","prices",
         "A map shows location; a recipe gives instructions. Guide → information."),
        ("Seed","plant","Egg","hatch","grow","cook","sell","eat",
         "A seed grows into a plant; an egg hatches into a bird. Origin → life."),
    ]
    _ana_gold = [
        ("Photosynthesis","light","Digestion","nutrients","heat","kinetic","sound","electrical",
         "Both convert external resources into usable energy. Light→chemical; Food→chemical."),
        ("Gravity","orbits","Magnetism","attracts","repels","levitates","friction","inertia",
         "Both are fundamental forces acting at a distance. Gravity: orbits; Magnetism: attraction."),
        ("Inflation","prices rise","Erosion","landscape lowers","grows","freezes","expands","heats",
         "Both are gradual change processes. Inflation ↑ prices; Erosion ↓ mountains."),
        ("Democracy","power shares","Market","resources flow","distributes","collects","produces","consumes",
         "Both are decentralised allocation systems. Democracy: power; Markets: resources."),
        ("Evolution","adapts","Learning","grows","fades","weakens","forms","stagnates",
         "Both are adaptive processes. Evolution: species; Learning: knowledge."),
    ]
    def _make_ana(tid, tier, levels, irt, scenarios):
        def _pick(rng):
            s = rng.choice(scenarios)
            return {"q": f"{s[0]} is to {s[1]} as {s[2]} is to ?",
                    "a": s[3].capitalize(), "b": s[4].capitalize(),
                    "c": s[5].capitalize(), "d": s[6].capitalize(), "e": s[7]}
        return QuestionTemplate(
            template_id=tid, arena="logic", domain="Logic",
            difficulty_tier=tier, shs_levels=levels, irt_base=irt,
            question_template="{q}", correct_answer="A",
            options_template={"A":"{a}","B":"{b}","C":"{c}","D":"{d}"},
            explanation_template="{e}",
            param_generators={"_s":_pick},
            computed_params={"q":lambda p:p["_s"]["q"],"a":lambda p:p["_s"]["a"],
                             "b":lambda p:p["_s"]["b"],"c":lambda p:p["_s"]["c"],
                             "d":lambda p:p["_s"]["d"],"e":lambda p:p["_s"]["e"]},
        )
    t.append(_make_ana("logic-ana-001","Bronze",["SHS 1"],(1.0,-1.0,0.25),_ana_bronze))
    t.append(_make_ana("logic-ana-002","Silver",["SHS 1","SHS 2"],(1.2,0.0,0.25),_ana_silver))
    t.append(_make_ana("logic-ana-003","Gold",["SHS 2","SHS 3"],(1.4,1.0,0.25),_ana_gold))

    # ── Syllogisms ───────────────────────────────────────────────────────
    t.append(QuestionTemplate(
        template_id="logic-ded-001", arena="logic", domain="Logic",
        difficulty_tier="Bronze", shs_levels=["SHS 1"], irt_base=(1.2, -1.0, 0.25),
        question_template="All {a} are {b}. Some {b} are {c}. Which must be true?",
        options_template={
            "A": "All {a} are {c}.", "B": "Some {c} are {a}.",
            "C": "It is possible that some {a} are {c}.", "D": "No {b} are {c}.",
        },
        correct_answer="C",
        explanation_template="We know all {a} are {b}, some {b} are {c}. The {a} could be among those {b} that are {c} — we cannot guarantee it. Only C could be true.",
        param_generators={
            "a": pick_from(["dogs","birds","students","trees","cars"]),
            "b": pick_from(["mammals","animals","people","plants","vehicles"]),
            "c": pick_from(["pets","flyers","athletes","evergreens","trucks"]),
        },
    ))
    t.append(QuestionTemplate(
        template_id="logic-ded-002", arena="logic", domain="Logic",
        difficulty_tier="Silver", shs_levels=["SHS 1","SHS 2"], irt_base=(1.3, 0.0, 0.25),
        question_template="All {a} are {b}. No {b} are {c}. What follows?",
        options_template={
            "A": "No {a} are {c}.", "B": "All {c} are {a}.",
            "C": "Some {b} are not {a}.", "D": "Both A and C.",
        },
        correct_answer="D",
        explanation_template="Since all {a} are {b}, and nothing in {b} is {c}, then no {a} is {c}. Also there may be {b} not {a}. Both A and C follow.",
        param_generators={
            "a": pick_from(["cats","robins","juniors","sedans","copper"]),
            "b": pick_from(["felines","birds","students","cars","metals"]),
            "c": pick_from(["canines","fish","seniors","trucks","plastics"]),
        },
    ))
    t.append(_make_scenario_template(
        "logic-ded-003","logic","Logic","Gold",["SHS 2","SHS 3"],(1.5,1.0,0.25),
        [("In a town, every person who reads the newspaper also reads books. Some people who watch television do not read books.",
          "Some people who read books may not watch television.","Everyone who reads the newspaper watches television.",
          "No one who reads books watches television.","Television watchers never read newspapers.",
          "Newspaper readers are a subset of book readers. Some TV watchers avoid books, but this tells us nothing about book readers & TV."),
         ("All successful athletes train daily. Some daily trainers do not eat healthy meals.",
          "Some successful athletes may not eat healthy meals.","All successful athletes eat healthy meals.",
          "No student who trains daily fails exams.","All students who train daily are athletes.",
          "Athletes ⊆ daily trainers. Some daily trainers don't eat healthy. So some athletes may not eat healthy."),
         ("Every member of the science club passed the maths test. Some who passed maths also passed physics. No one who failed physics can join the engineering club.",
          "Some who passed maths may not be in the science club.","All members of the science club passed physics.",
          "No one who failed maths can join engineering club.","Everyone who passed physics is in the science club.",
          "Science club ⊆ passed maths. There may be students who passed maths but aren't in the science club.")],
        "{scenario}\n\nIf true, which must also be true?",
        {"A":"{opt_a}","B":"{opt_b}","C":"{opt_c}","D":"{opt_d}"},
        correct_key="A", has_q=False))

    # ── Logic Puzzles (scenario-based) ───────────────────────────────────
    t.append(_make_scenario_template(
        "logic-puz-001","logic","Logic","Silver",["SHS 1","SHS 2"],(1.3,0.0,0.25),
        [("Ama, Yaw, and Esi each like a different subject: Maths, Science, English. Ama does not like Maths. Yaw does not like English. Esi likes Science.",
          "what is Ama's favourite subject","English","Mathematics","Science","Social Studies",
          "Esi takes Science. Ama doesn't like Maths, so Ama = English. Yaw gets Maths."),
         ("Kofi, Adwoa, and Kwame each own a different pet: dog, cat, bird. Kofi does not own the cat. Adwoa owns the bird.",
          "who owns the dog","Kofi","Adwoa","Kwame","None of them",
          "Adwoa owns the bird. Kofi doesn't own the cat, so Kofi = dog. Kwame = cat."),
         ("Three houses in a row: red, blue, green. Red is left of blue. Green is right of blue.",
          "which house is in the middle","Blue","Red","Green","Cannot be determined",
          "Red ← Blue ← Green. Blue is in the middle.")],
        "{scenario}\n\nWho {q}?", {"A":"{opt_a}","B":"{opt_b}","C":"{opt_c}","D":"{opt_d}"},
        correct_key="A", has_q=True))
    t.append(_make_scenario_template(
        "logic-puz-002","logic","Logic","Gold",["SHS 2","SHS 3"],(1.5,1.0,0.25),
        [("Akua, Mensah, Efia, Kwesi sit in 4 chairs. Akua sits left of Mensah but right of Efia. Kwesi at one end.",
          "Efia is at the far left.","Kwesi is at the right end.","Mensah sits next to Kwesi.","Akua sits in the middle.",
          "Order: Efia, Akua, Mensah, Kwesi (or reversed). Efia is far left."),
         ("A, B, C, D, E present. C before B but after A. E immediately after D. A presents first.",
          "D presents fourth.","E presents second.","B presents fifth.","C presents third.",
          "Order: A(1st), C, B, then D→E consecutive. A,C,B,D,E → D is 4th.")],
        "{scenario}\n\nWhich must be true?", {"A":"{opt_a}","B":"{opt_b}","C":"{opt_c}","D":"{opt_d}"},
        correct_key="A", has_q=False))
    t.append(_make_scenario_template(
        "logic-puz-003","logic","Logic","Bronze",["SHS 1"],(1.0,-1.0,0.25),
        [("Fill 5L jug, pour into 3L until full. What remains in the 5L?",
          "2 litres","1 litre","3 litres","4 litres",
          "5L full → pour 3L into 3L jug → 2L left in 5L jug."),
         ("Farmer with goat, wolf, cabbage. Can take one at a time. What should he take FIRST?",
          "The goat","The wolf","The cabbage","Himself only",
          "Take goat first. Wolf & cabbage are safe together. Return for wolf, bring goat back, take cabbage, return for goat."),
         ("A house has all four walls facing south. A bear walks by. What colour?",
          "White","Brown","Black","Grizzly",
          "If all walls face south, it's the North Pole. Polar bears are white.")],
        "{scenario}", {"A":"{opt_a}","B":"{opt_b}","C":"{opt_c}","D":"{opt_d}"},
        correct_key="A", has_q=False))

    return t


# ══════════════════════════════════════════════════════════════════════════════
# QUANTITATIVE SPRINT
# ══════════════════════════════════════════════════════════════════════════════

def _quant_templates() -> List[QuestionTemplate]:
    t: List[QuestionTemplate] = []

    # ── Percentages ──────────────────────────────────────────────────────
    t.append(QuestionTemplate(
        template_id="quant-pct-001", arena="quantitative", domain="Math",
        difficulty_tier="Bronze", shs_levels=["SHS 1"], irt_base=(1.0, -1.0, 0.25),
        question_template="What is {pct}% of {num}?",
        options_template={"A":"{w1}","B":"{correct}","C":"{w2}","D":"{w3}"},
        correct_answer="B",
        explanation_template="{pct}% of {num} = ({pct}/100)×{num} = {correct}",
        param_generators={
            "pct": pick_from([10,15,20,25,30,40,50,60,75]),
            "num": pick_from([40,60,80,100,120,150,200,250,300,400,500]),
        },
        computed_params={
            "correct": lambda p: int(p["num"]*p["pct"]/100),
            "w1": lambda p: int(p["num"]*p["pct"]/100)+5,
            "w2": lambda p: int(p["num"]*p["pct"]/100)-5,
            "w3": lambda p: int(p["num"]*(p["pct"]+5)/100),
        },
    ))
    t.append(QuestionTemplate(
        template_id="quant-pct-002", arena="quantitative", domain="Math",
        difficulty_tier="Silver", shs_levels=["SHS 1","SHS 2"], irt_base=(1.2, 0.0, 0.25),
        question_template="A student scored {score} out of {total}. What %?",
        options_template={"A":"{w1}%","B":"{w2}%","C":"{correct}%","D":"{w3}%"},
        correct_answer="C",
        explanation_template="Percentage = ({score}/{total})×100% = {correct}%",
        param_generators={
            "score": pick_from([12,15,18,20,24,28,30,35,40,42,45,48]),
            "total": pick_from([20,25,30,40,50,60]),
        },
        computed_params={
            "correct": lambda p: int(round(p["score"]/p["total"]*100)),
            "w1": lambda p: int(round(p["score"]/p["total"]*100))+5,
            "w2": lambda p: int(round(p["score"]/p["total"]*100))-5,
            "w3": lambda p: int(round((p["score"]+5)/p["total"]*100)),
        },
    ))
    t.append(QuestionTemplate(
        template_id="quant-pct-003", arena="quantitative", domain="Math",
        difficulty_tier="Gold", shs_levels=["SHS 2","SHS 3"], irt_base=(1.3, 1.0, 0.25),
        question_template="Price of {item}: GH₵{p1} → GH₵{p2}. % increase?",
        options_template={"A":"{w1}%","B":"{w2}%","C":"{correct}%","D":"{w3}%"},
        correct_answer="C",
        explanation_template="Increase={p2}-{p1}={diff}. %=({diff}/{p1})×100={correct}%",
        param_generators={
            "item": pick_from(["book","bag","shirt","shoe","calculator","textbook"]),
            "p1": int_between(20,100), "p2": int_between(25,150),
        },
        computed_params={
            "diff": lambda p: p["p2"]-p["p1"],
            "correct": lambda p: int(round((p["p2"]-p["p1"])/p["p1"]*100)),
            "w1": lambda p: int(round((p["p2"]-p["p1"])/p["p1"]*100))+5,
            "w2": lambda p: int(round((p["p2"]-p["p1"])/p["p1"]*100))-5,
            "w3": lambda p: int(round(p["p2"]/p["p1"]*100)),
        },
    ))

    # ── Ratios ───────────────────────────────────────────────────────────
    t.append(QuestionTemplate(
        template_id="quant-rat-001", arena="quantitative", domain="Math",
        difficulty_tier="Bronze", shs_levels=["SHS 1"], irt_base=(1.0, -1.0, 0.25),
        question_template="Share GH₵{a} in ratio {r1}:{r2}. Larger share?",
        options_template={"A":"GH₵{w1}","B":"GH₵{w2}","C":"GH₵{correct}","D":"GH₵{w3}"},
        correct_answer="C",
        explanation_template="Parts={r1}+{r2}={tp}. Per part={am}/{tp}={pp}. Larger={pp}×{mx}={correct}.",
        param_generators={
            "r1": int_between(1,5), "r2": int_between(1,5),
            "am": pick_from([100,120,150,180,200,240,300,360,400,500]),
        },
        computed_params={
            "tp": lambda p: p["r1"]+p["r2"], "mx": lambda p: max(p["r1"],p["r2"]),
            "pp": lambda p: p["am"]//(p["r1"]+p["r2"]),
            "correct": lambda p: p["am"]//(p["r1"]+p["r2"])*max(p["r1"],p["r2"]),
            "w1": lambda p: p["am"]//(p["r1"]+p["r2"])*max(p["r1"],p["r2"])+5,
            "w2": lambda p: p["am"]//(p["r1"]+p["r2"])*min(p["r1"],p["r2"]),
            "w3": lambda p: p["am"]//(p["r1"]+p["r2"])*max(p["r1"],p["r2"])-5,
            "a": lambda p: p["am"],
        },
    ))
    t.append(QuestionTemplate(
        template_id="quant-rat-002", arena="quantitative", domain="Math",
        difficulty_tier="Silver", shs_levels=["SHS 1","SHS 2"], irt_base=(1.2, 0.0, 0.25),
        question_template="Ratio boys:girls = {ra}:{rb}. {total} students. Boys?",
        options_template={"A":"{w1}","B":"{w2}","C":"{correct}","D":"{w3}"},
        correct_answer="C",
        explanation_template="Parts={ra}+{rb}={tp}. Per part={total}/{tp}={pp}. Boys={ra}×{pp}={correct}.",
        param_generators={
            "ra": pick_from([2,3,4,5,7]), "rb": pick_from([3,4,5,7,8]),
            "total": pick_from([30,35,40,45,48,55,60,72,80,90,100]),
        },
        computed_params={
            "tp": lambda p: p["ra"]+p["rb"],
            "pp": lambda p: p["total"]//(p["ra"]+p["rb"]),
            "correct": lambda p: p["total"]//(p["ra"]+p["rb"])*p["ra"],
            "w1": lambda p: p["total"]//(p["ra"]+p["rb"])*p["rb"],
            "w2": lambda p: p["total"]//(p["ra"]+p["rb"])*p["ra"]+1,
            "w3": lambda p: p["total"]//(p["ra"]+p["rb"])*p["ra"]-1,
        },
    ))
    t.append(QuestionTemplate(
        template_id="quant-rat-003", arena="quantitative", domain="Math",
        difficulty_tier="Gold", shs_levels=["SHS 2","SHS 3"], irt_base=(1.4, 1.0, 0.25),
        question_template="Map scale 1:{scale}. Towns {cm} cm apart. Actual km?",
        options_template={"A":"{w1} km","B":"{w2} km","C":"{correct} km","D":"{w3} km"},
        correct_answer="C",
        explanation_template="{cm} cm × {scale} = {ac} cm = {ak} km.",
        param_generators={
            "scale": pick_from([100000,200000,500000,1000000]),
            "cm": pick_from([5,8,10,12,15,20,25]),
        },
        computed_params={
            "ac": lambda p: p["cm"]*p["scale"],
            "ak": lambda p: p["cm"]*p["scale"]/100000,
            "correct": lambda p: p["cm"]*p["scale"]//100000,
            "w1": lambda p: p["cm"]*p["scale"]//100000+1,
            "w2": lambda p: max(1, p["cm"]*p["scale"]//100000-1),
            "w3": lambda p: p["cm"]*p["scale"]//50000,
        },
    ))

    # ── Algebra ──────────────────────────────────────────────────────────
    t.append(QuestionTemplate(
        template_id="quant-alg-001", arena="quantitative", domain="Math",
        difficulty_tier="Bronze", shs_levels=["SHS 1"], irt_base=(1.0, -1.0, 0.25),
        question_template="Solve {a}x + {b} = {c}",
        options_template={"A":"x={w1}","B":"x={w2}","C":"x={correct}","D":"x={w3}"},
        correct_answer="C",
        explanation_template="{a}x = {c}-{b} = {rhs}. x = {rhs}/{a} = {correct}.",
        param_generators={"a": pick_from([2,3,4,5,6]), "b": int_between(1,20), "c": int_between(10,50)},
        computed_params={
            "rhs": lambda p: p["c"]-p["b"],
            "correct": lambda p: (p["c"]-p["b"])//p["a"],
            "w1": lambda p: (p["c"]-p["b"])//p["a"]+1,
            "w2": lambda p: (p["c"]-p["b"])//p["a"]-1,
            "w3": lambda p: (p["c"]-p["b"])//p["a"]+p["a"],
        },
    ))
    t.append(QuestionTemplate(
        template_id="quant-alg-002", arena="quantitative", domain="Math",
        difficulty_tier="Silver", shs_levels=["SHS 1","SHS 2"], irt_base=(1.2, 0.0, 0.25),
        question_template="{a}x+{b} = {c}x-{d}. Find x.",
        options_template={"A":"x={w1}","B":"x={correct}","C":"x={w2}","D":"x={w3}"},
        correct_answer="B",
        explanation_template="({a}-{c})x = -{d}-{b} = {rhs}. x = {rhs}/{amc} = {correct}.",
        param_generators={
            "a": pick_from([4,5,7,8]), "b": int_between(2,15),
            "c": pick_from([1,2,3]), "d": int_between(1,10),
        },
        computed_params={
            "rhs": lambda p: -p["d"]-p["b"],
            "amc": lambda p: p["a"]-p["c"],
            "correct": lambda p: (-p["d"]-p["b"])//(p["a"]-p["c"]),
            "w1": lambda p: (-p["d"]-p["b"])//(p["a"]-p["c"])+1,
            "w2": lambda p: (-p["d"]-p["b"])//(p["a"]-p["c"])-1,
            "w3": lambda p: (-p["d"]-p["b"])//(p["a"]-p["c"])+2,
        },
    ))

    # ── Mental Math ──────────────────────────────────────────────────────
    t.append(QuestionTemplate(
        template_id="quant-ari-001", arena="quantitative", domain="Math",
        difficulty_tier="Bronze", shs_levels=["SHS 1"], irt_base=(1.0, -1.5, 0.25),
        question_template="{a} × {b} = ?",
        options_template={"A":"{w1}","B":"{correct}","C":"{w2}","D":"{w3}"},
        correct_answer="B", explanation_template="{a} × {b} = {correct}",
        param_generators={"a": int_between(6,15), "b": int_between(6,15)},
        computed_params={
            "correct": lambda p: p["a"]*p["b"],
            "w1": lambda p: p["a"]*p["b"]+1,
            "w2": lambda p: p["a"]*p["b"]-1,
            "w3": lambda p: p["a"]*(p["b"]+1),
        },
    ))
    t.append(QuestionTemplate(
        template_id="quant-ari-002", arena="quantitative", domain="Math",
        difficulty_tier="Silver", shs_levels=["SHS 1","SHS 2"], irt_base=(1.0, 0.0, 0.25),
        question_template="√{num} = ?",
        options_template={"A":"{w1}","B":"{correct}","C":"{w2}","D":"{w3}"},
        correct_answer="B", explanation_template="√{num} = {correct} ({correct}²={num})",
        param_generators={"num": pick_from([25,36,49,64,81,100,121,144,169,196,225,400])},
        computed_params={
            "correct": lambda p: int(p["num"]**0.5),
            "w1": lambda p: int(p["num"]**0.5)+1,
            "w2": lambda p: int(p["num"]**0.5)-1,
            "w3": lambda p: int(p["num"]**0.5)+2,
        },
    ))

    # ── Speed / Distance / Time ──────────────────────────────────────────
    t.append(QuestionTemplate(
        template_id="quant-sdt-001", arena="quantitative", domain="Math",
        difficulty_tier="Silver", shs_levels=["SHS 1","SHS 2"], irt_base=(1.2, 0.0, 0.25),
        question_template="{d} km in {t} hours. Speed?",
        options_template={"A":"{w1} km/h","B":"{w2} km/h","C":"{correct} km/h","D":"{w3} km/h"},
        correct_answer="C",
        explanation_template="Speed = {d}/{t} = {correct} km/h.",
        param_generators={"d": pick_from([60,80,100,120,150,180,200,240,300]), "t": pick_from([1,2,3,4,5])},
        computed_params={
            "correct": lambda p: p["d"]//p["t"],
            "w1": lambda p: p["d"]//p["t"]+5,
            "w2": lambda p: p["d"]//p["t"]-5,
            "w3": lambda p: p["d"]//p["t"]+10,
        },
    ))

    # ── Simple Interest ──────────────────────────────────────────────────
    t.append(QuestionTemplate(
        template_id="quant-int-001", arena="quantitative", domain="Math",
        difficulty_tier="Silver", shs_levels=["SHS 1","SHS 2"], irt_base=(1.3, 0.0, 0.25),
        question_template="GH₵{p} at {r}% simple for {y} years. Interest?",
        options_template={"A":"GH₵{w1}","B":"GH₵{correct}","C":"GH₵{w2}","D":"GH₵{w3}"},
        correct_answer="B",
        explanation_template="SI = P×R×T/100 = {p}×{r}×{y}/100 = {correct}.",
        param_generators={
            "p": pick_from([100,200,500,1000,2000,5000]),
            "r": pick_from([5,8,10,12,15,20]),
            "y": pick_from([1,2,3,4,5]),
        },
        computed_params={
            "correct": lambda p: p["p"]*p["r"]*p["y"]//100,
            "w1": lambda p: p["p"]*p["r"]*p["y"]//100+10,
            "w2": lambda p: p["p"]*p["r"]*p["y"]//100-10,
            "w3": lambda p: p["p"]*p["r"]*(p["y"]+1)//100,
        },
    ))

    # ── Geometry ─────────────────────────────────────────────────────────
    t.append(QuestionTemplate(
        template_id="quant-geo-001", arena="quantitative", domain="Math",
        difficulty_tier="Bronze", shs_levels=["SHS 1"], irt_base=(1.0, -1.0, 0.25),
        question_template="Rectangle {l}cm × {w}cm. Perimeter?",
        options_template={"A":"{w1} cm","B":"{correct} cm","C":"{w2} cm","D":"{w3} cm"},
        correct_answer="B",
        explanation_template="P=2(l+w)=2({l}+{w})={correct} cm.",
        param_generators={"l": int_between(5,20), "w": int_between(3,15)},
        computed_params={
            "correct": lambda p: 2*(p["l"]+p["w"]),
            "w1": lambda p: 2*(p["l"]+p["w"])+2,
            "w2": lambda p: 2*(p["l"]+p["w"])-2,
            "w3": lambda p: p["l"]*p["w"],
        },
    ))
    t.append(QuestionTemplate(
        template_id="quant-geo-002", arena="quantitative", domain="Math",
        difficulty_tier="Silver", shs_levels=["SHS 1","SHS 2"], irt_base=(1.2, 0.0, 0.25),
        question_template="Circle radius {r} cm. Area? (π≈{pi})",
        options_template={"A":"{w1} cm²","B":"{w2} cm²","C":"{correct} cm²","D":"{w3} cm²"},
        correct_answer="C",
        explanation_template="A=πr²={pi}×{r}²={pi}×{rsq}≈{correct} cm².",
        param_generators={"r": pick_from([3,4,5,6,7,8,9,10,14]), "pi": pick_from([3.14,22/7])},
        computed_params={
            "rsq": lambda p: p["r"]**2,
            "correct": lambda p: int(round(p["pi"]*p["r"]**2)),
            "w1": lambda p: int(round(p["pi"]*p["r"]**2))+10,
            "w2": lambda p: int(round(p["pi"]*p["r"]**2))-10,
            "w3": lambda p: int(round(p["pi"]*(p["r"]+1)**2)),
        },
    ))
    t.append(QuestionTemplate(
        template_id="quant-geo-003", arena="quantitative", domain="Math",
        difficulty_tier="Gold", shs_levels=["SHS 2","SHS 3"], irt_base=(1.3, 1.0, 0.25),
        question_template="Prism: base area {ba} cm², height {h} cm. Volume?",
        options_template={"A":"{w1} cm³","B":"{w2} cm³","C":"{correct} cm³","D":"{w3} cm³"},
        correct_answer="C",
        explanation_template="V = base area × height = {ba} × {h} = {correct} cm³.",
        param_generators={"ba": pick_from([15,20,24,30,36,40,48,50]), "h": pick_from([5,8,10,12,15,20])},
        computed_params={
            "correct": lambda p: p["ba"]*p["h"],
            "w1": lambda p: p["ba"]*p["h"]+10,
            "w2": lambda p: p["ba"]*p["h"]-10,
            "w3": lambda p: p["ba"]*(p["h"]+5),
        },
    ))

    # ── Probability ──────────────────────────────────────────────────────
    t.append(QuestionTemplate(
        template_id="quant-prob-001", arena="quantitative", domain="Math",
        difficulty_tier="Silver", shs_levels=["SHS 1","SHS 2"], irt_base=(1.3, 0.0, 0.25),
        question_template="Bag: {r} red, {b} blue, {g} green marbles. P(red)?",
        options_template={"A":"{w1}","B":"{correct}","C":"{w2}","D":"{w3}"},
        correct_answer="B",
        explanation_template="Total = {r}+{b}+{g} = {total}. P(red) = {r}/{total} = {correct}.",
        param_generators={"r": int_between(2,8), "b": int_between(2,8), "g": int_between(2,8)},
        computed_params={
            "total": lambda p: p["r"]+p["b"]+p["g"],
            "correct": lambda p: f"{p['r']}/{p['r']+p['b']+p['g']}",
            "w1": lambda p: f"{p['b']}/{p['r']+p['b']+p['g']}",
            "w2": lambda p: f"{p['g']}/{p['r']+p['b']+p['g']}",
            "w3": lambda p: f"{p['r']+1}/{p['r']+p['b']+p['g']}",
        },
    ))
    t.append(QuestionTemplate(
        template_id="quant-prob-002", arena="quantitative", domain="Math",
        difficulty_tier="Gold", shs_levels=["SHS 2","SHS 3"], irt_base=(1.4, 1.0, 0.25),
        question_template="Die rolled twice. P({t1} then {t2})?",
        options_template={"A":"{w1}","B":"{correct}","C":"{w2}","D":"{w3}"},
        correct_answer="B",
        explanation_template="P({t1})=1/6, P({t2})=1/6. Independence: 1/6×1/6=1/36={correct}.",
        param_generators={"t1": int_between(1,6), "t2": int_between(1,6)},
        computed_params={
            "correct": lambda p: "1/36", "w1": lambda p: "1/6",
            "w2": lambda p: "1/12", "w3": lambda p: "1/18",
        },
    ))

    # ── Averages ─────────────────────────────────────────────────────────
    t.append(QuestionTemplate(
        template_id="quant-avg-001", arena="quantitative", domain="Math",
        difficulty_tier="Bronze", shs_levels=["SHS 1"], irt_base=(1.0, -1.0, 0.25),
        question_template="Ages: {a1}, {a2}, {a3}, {a4}, {a5}. Mean?",
        options_template={"A":"{w1}","B":"{w2}","C":"{correct}","D":"{w3}"},
        correct_answer="C",
        explanation_template="Sum={a1}+{a2}+{a3}+{a4}+{a5}={sum}. Mean={sum}/5={correct}.",
        param_generators={
            "a1": int_between(10,18),"a2": int_between(10,18),"a3": int_between(10,18),
            "a4": int_between(10,18),"a5": int_between(10,18),
        },
        computed_params={
            "sum": lambda p: sum(p[f"a{i}"] for i in range(1,6)),
            "correct": lambda p: sum(p[f"a{i}"] for i in range(1,6))//5,
            "w1": lambda p: sum(p[f"a{i}"] for i in range(1,6))//5+1,
            "w2": lambda p: sum(p[f"a{i}"] for i in range(1,6))//5-1,
            "w3": lambda p: max(p[f"a{i}"] for i in range(1,6)),
        },
    ))
    t.append(QuestionTemplate(
        template_id="quant-avg-002", arena="quantitative", domain="Math",
        difficulty_tier="Gold", shs_levels=["SHS 2","SHS 3"], irt_base=(1.4, 1.0, 0.25),
        question_template="Scores: {m1}, {m2}, {m3}, {m4}, {m5}. Mean?",
        options_template={"A":"{w1}","B":"{w2}","C":"{correct}","D":"{w3}"},
        correct_answer="C",
        explanation_template="Sum={m1}+{m2}+...={sum}. Mean={sum}/5={correct}.",
        param_generators={
            "m1": int_between(50,95),"m2": int_between(50,95),"m3": int_between(50,95),
            "m4": int_between(50,95),"m5": int_between(50,95),
        },
        computed_params={
            "sum": lambda p: sum(p[f"m{i}"] for i in range(1,6)),
            "correct": lambda p: sum(p[f"m{i}"] for i in range(1,6))//5,
            "w1": lambda p: sum(p[f"m{i}"] for i in range(1,6))//5+3,
            "w2": lambda p: sum(p[f"m{i}"] for i in range(1,6))//5-3,
            "w3": lambda p: sum(p[f"m{i}"] for i in range(1,6))//5+5,
        },
    ))

    return t


# ══════════════════════════════════════════════════════════════════════════════
# SCIENTIFIC THINKING (all scenario-based — no independent pick_from)
# ══════════════════════════════════════════════════════════════════════════════

def _sci_templates() -> List[QuestionTemplate]:
    """All science templates use scenario-based _pick to ensure matched pairs."""

    # (scenario, opt_a, opt_b, opt_c, opt_d, explanation)
    _bio_bronze = [
        ("A plant in a dark cupboard turns yellow and grows tall and thin.",
         "The plant is not getting enough water.",
         "The temperature is too high in the cupboard.",
         "Without light, the plant cannot photosynthesise and stretches to find light (etiolation).",
         "The plant is infected with a fungus.",
         "Etiolation is a plant's response to low light — it stretches and loses chlorophyll."),
        ("When she exercises, her heart beats faster.",
         "Her heart is getting weaker.",
         "She is feeling anxious.",
         "Exercise increases oxygen demand, so the heart pumps faster to deliver more oxygen to muscles.",
         "She is running too fast.",
         "The heart increases cardiac output during exercise to supply working muscles with oxygenated blood."),
        ("Fertilised plant grows much taller than unfertilised one.",
         "The seeds in the second pot were older.",
         "The fertilised pot got more sunlight.",
         "Fertiliser provides essential nutrients (nitrogen, phosphorus, potassium) that promote plant growth.",
         "The fertiliser changed the soil colour.",
         "Fertiliser supplies macronutrients essential for plant growth that may be deficient in the soil."),
        ("A patient has a fever and high white blood cell count.",
         "The patient ate spoiled food.",
         "The patient needs more sleep.",
         "A high WBC count indicates the immune system is fighting an infection, which causes fever.",
         "The thermometer is broken.",
         "Leukocytosis (high WBC) is a standard immune response to bacterial or viral infection."),
    ]
    _bio_silver = [
        ("Villagers have high goitre rates. The local soil lacks a mineral.",
         "The patients are not eating enough.",
         "The village water is contaminated.",
         "The soil lacks iodine, essential for thyroid function.",
         "The village is at a higher altitude.",
         "Iodine is required for thyroid hormone. Iodine-deficient soil → iodine-deficient food → goitre."),
        ("A farmer rotates maize and beans. Her soil stays fertile longer than her neighbour who only plants maize.",
         "Beans use more nutrients from the soil.",
         "Maize alone adds nitrogen to the soil.",
         "Legumes (beans) fix nitrogen via root bacteria, restoring fertility naturally.",
         "The farmer uses more water.",
         "Leguminous plants host nitrogen-fixing Rhizobium bacteria in root nodules, enriching the soil."),
        ("Some birds have thick beaks for cracking seeds; others have thin beaks for sipping nectar.",
         "All birds belong to the same species.",
         "Birds developed different beaks due to lack of food.",
         "Different beak shapes are adaptations to different food sources (natural selection).",
         "All birds can eat any food with practice.",
         "Darwin's finches — beak shape evolves over generations to match available food sources."),
        ("Pond water with algae stays clear when snails are present. When snails are removed, water becomes cloudy with algae.",
         "Snails produce chemicals that kill algae.",
         "Algae need snails to reproduce.",
         "Snails eat the algae (herbivory), controlling the population naturally.",
         "Snails and algae are unrelated.",
         "The snails graze on algae. When removed, the algae population grows unchecked."),
    ]
    _bio_gold = [
        ("Sickle cell trait (HbAS) offers protection against severe malaria in Ghana. The HbS allele persists despite causing disease in HbSS individuals.",
         "The HbS allele provides no survival benefit.",
         "Malaria and sickle cell are completely unrelated.",
         "Heterozygote advantage — carrying one HbS allele confers malaria resistance, maintaining the allele in the population.",
         "Sickle cell disease has no genetic basis.",
         "Heterozygote advantage maintains the HbS allele in malaria-endemic regions. This is natural selection in action."),
        ("CRISPR-Cas9 is a revolutionary gene-editing tool. A scientist uses CRISPR to correct a mutation in the haemoglobin gene of a patient's cells.",
         "This will change all genes in the patient.",
         "CRISPR can only edit bacterial DNA.",
         "CRISPR uses a guide RNA to target a specific DNA sequence, where the Cas9 enzyme cuts the DNA for repair or replacement.",
         "Gene editing is impossible in human cells.",
         "CRISPR-Cas9 is a precise gene-editing tool. Guide RNA targets Cas9 to a specific DNA sequence, enabling targeted genetic modifications."),
        ("A Ghanain farmer plants genetically modified (GM) cowpea that produces its own pest-resistant protein. The pest population drops in the first year.",
         "The pests will evolve resistance over time through natural selection.",
         "GM crops always fail after one season.",
         "The farmer will need stronger pesticides.",
         "Natural selection favours resistant pest variants. Refuges (non-GM crops nearby) slow resistance evolution.",
         "Evolution — pests with resistance genes survive and reproduce. Planting refuges (non-Bt crops) dilutes resistance genes."),
        ("DNA analysis shows that two closely related bird species on different Canary Islands share a common ancestor but have different beak shapes.",
         "The birds deliberately changed their beaks.",
         "Different food sources on each island exerted different selective pressures over generations.",
         "Beak shape is determined by diet within a single lifetime.",
         "Beak shape varies randomly without reason.",
         "Natural selection: ancestral finches colonised islands with different food. Beak shapes evolved to match available food."),
        ("A fetus develops as female by default. The SRY gene on the Y chromosome triggers male development. A baby with XY chromosomes but a non-functional SRY gene develops as female.",
         "The baby must have XX chromosomes.",
         "Sex is purely determined by chromosomes.",
         "The SRY gene product (TDF protein) is necessary for male development. Without it, default female development occurs despite XY chromosomes.",
         "The baby will develop as male later in life.",
         "The SRY gene produces testis-determining factor. Without functional SRY, the bipotential gonads develop into ovaries — demonstrating genes, not just chromosomes, determine sex."),
    ]
    _phy_bronze = [
        ("A ball thrown upward comes back down.",
         "Thermal expansion", "Gravity pulls objects toward Earth's centre.",
         "Magnetism", "Air resistance",
         "Gravity is a fundamental force attracting all objects with mass toward Earth."),
        ("A moving lorry is harder to stop than a bicycle at the same speed.",
         "Friction", "Momentum depends on mass and speed. A lorry has more mass = more momentum.",
         "Inertia", "Centripetal force",
         "Momentum = mass × velocity. Greater mass = greater momentum = harder to stop."),
        ("Stepping out of a boat onto the dock makes the boat move backward.",
         "Surface tension", "Newton's Third Law — every action has an equal and opposite reaction.",
         "Buoyancy", "Viscosity",
         "You push backward on the boat; the boat pushes you forward to the dock."),
        ("Ice floats on water instead of sinking.",
         "Capillary action", "Ice is less dense than liquid water; water expands when it freezes.",
         "Convection", "Condensation",
         "Water reaches max density at 4°C. Ice at 0°C is ~9% less dense, so it floats."),
    ]
    _phy_silver = [
        ("A 6V battery powers one bulb brightly. Adding a second bulb in SERIES makes both dimmer.",
         "The battery is running out of power.",
         "The second bulb uses more voltage.",
         "In a series circuit, voltage is shared. Each gets ~3V instead of 6V, so both glow dimmer.",
         "The wires are not connected properly.",
         "Series circuit: total resistance doubles, current halves. Each bulb receives less power (P=V²/R)."),
        ("A metal spoon in hot tea becomes hot at the handle, even though only the tip is in the tea.",
         "The spoon is made of a special material.",
         "Heat travels through the air around the spoon.",
         "Heat is conducted along the metal from the hot end to the cool end (thermal conduction).",
         "The tea is not hot enough.",
         "Metals are good thermal conductors — free electrons transfer kinetic energy along the spoon."),
        ("A sound is louder close to the source than far away.",
         "Sound travels faster close to the source.",
         "Sound waves get weaker from air resistance.",
         "Sound intensity follows the inverse square law — energy spreads out as distance increases.",
         "Sound needs a medium to travel.",
         "Sound intensity I ∝ 1/r². Doubling distance reduces intensity to 1/4."),
    ]
    _phy_gold = [
        ("A fibre optic cable transmits light signals by total internal reflection. This technology powers high-speed internet across Ghana and the world.",
         "The light is reflected by mirrors inside the cable.",
         "Light travels through fibre optic cables faster than light in a vacuum.",
         "Light is confined to the core by total internal reflection, bouncing off the cladding at angles greater than the critical angle.",
         "Fibre optics use electricity, not light.",
         "Total internal reflection occurs when light travelling in a denser medium (glass core) hits the boundary at an angle > critical angle."),
        ("Carbon-14 dating measures the age of archaeological artefacts up to ~50,000 years old. The half-life of C-14 is 5,730 years.",
         "Carbon-14 dating gives exact dates with no error margin.",
         "C-14 dating works because all carbon in organisms is C-14 only.",
         "Living organisms absorb C-14 from the atmosphere. After death, C-14 decays. The remaining C-14 fraction indicates age.",
         "Carbon dating can be used on any material including rocks.",
         "Radioactive dating: C-14 half-life = 5,730 years. Ratio of C-14 to C-12 in a sample reveals time since death."),
        ("A hospital uses gamma radiation from Cobalt-60 to treat a cancer patient. The gamma rays are carefully targeted at the tumour from multiple angles.",
         "Gamma radiation is harmless to all cells.",
         "The patient becomes radioactive after treatment.",
         "Gamma rays penetrate tissue and deliver energy to kill rapidly dividing cancer cells. Multiple angles minimise damage to surrounding healthy tissue.",
         "Radiotherapy uses sound waves to treat cancer.",
         "Gamma radiation damages DNA in rapidly dividing cancer cells. Rotating the source around the patient concentrates dose at tumour."),
        ("A solar panel in Accra generates electricity from sunlight. The semiconductor material in the panel absorbs photons, releasing electrons.",
         "Solar panels generate electricity from heat, not light.",
         "The photovoltaic effect: photons transfer energy to electrons in silicon, creating electron-hole pairs that flow as electric current.",
         "Solar panels need direct sunlight at all times.",
         "Photovoltaic cells generate AC electricity directly.",
         "The photoelectric effect: photons with energy above the band gap excite electrons into the conduction band, creating a current."),
        ("An ultrasound scanner uses high-frequency sound waves to create images of an unborn baby without using ionising radiation.",
         "Ultrasound uses X-rays at a low dose.",
         "Sound waves reflect off tissues. The time delay and intensity of echoes are used to construct an image (echolocation).",
         "Ultrasound uses magnetic fields to see inside the body.",
         "Ultrasound only works for bone imaging.",
         "Medical ultrasound: transducer emits pulses >20 kHz. Echoes from tissue boundaries are processed to form real-time images. No ionising radiation."),
    ]
    _che_bronze = [
        ("A piece of paper is torn into small pieces.",
         "Chemical change", "Physical change — the paper's composition stays the same; only its shape changes.",
         "Physical change", "Biological change",
         "Tearing paper changes its shape but not its chemical bonds — this is a physical change."),
        ("An iron nail left outside becomes rusty.",
         "Physical change", "Chemical change — rusting is oxidation, forming a new substance (Fe₂O₃).",
         "Chemical change", "Phase change",
         "Rusting is an oxidation reaction where iron combines with oxygen, forming new substance iron oxide."),
        ("Sugar dissolves in water.",
         "Nuclear change", "Physical change — dissolving is a physical process; no new substance forms.",
         "Chemical change", "Melting",
         "Dissolving sugar is a physical change — the sugar molecules disperse but remain chemically the same."),
        ("Wood burns to produce ash and smoke.",
         "Physical change", "Chemical change — combustion produces new substances (ash, CO₂, H₂O).",
         "Evaporation", "Sublimation",
         "Burning involves combustion, a chemical reaction that produces new substances and cannot be reversed."),
    ]
    _che_gold = [
        ("Electrolysis of water produces hydrogen gas at the cathode and oxygen gas at the anode. The volume ratio of H₂ to O₂ is 2:1.",
         "Both electrodes produce hydrogen gas.",
         "Electrolysis only works with salt water.",
         "Water is split by electricity: 2H₂O → 2H₂ + O₂. The 2:1 volume ratio confirms the chemical formula of water.",
         "Hydrogen is produced at the anode.",
         "Electrolysis: H₂O reduced at cathode(-) → H₂; H₂O oxidised at anode(+) → O₂. 2:1 ratio confirms water = H₂O."),
        ("During fractional distillation of crude oil at Tema Oil Refinery, different hydrocarbon fractions condense at different temperatures.",
         "Crude oil is separated by density using a centrifuge.",
         "Fractional distillation separates hydrocarbons by boiling point. Shorter chain molecules have lower boiling points and condense higher in the column.",
         "Crude oil is separated by chemical reaction.",
         "All hydrocarbon fractions boil at the same temperature.",
         "Fractional distillation separates crude oil into fractions based on boiling points. Petrol (C₅-C₁₂) condenses high; bitumen (C₂₀+) at the bottom."),
        ("A catalyst in the Haber process (iron) allows ammonia production at lower temperature and pressure, making fertiliser production economical.",
         "Catalysts are consumed in the Haber process.",
         "The catalyst changes the equilibrium position of the reaction.",
         "Catalysts provide an alternative reaction pathway with lower activation energy, increasing reaction rate without being consumed.",
         "Ammonia production does not need a catalyst.",
         "Catalysts lower activation energy, speeding up reactions. In the Haber process: N₂ + 3H₂ ⇌ 2NH₃. Iron catalyst enables feasible conditions."),
        ("A local soap maker in Ghana heats palm oil with sodium hydroxide (NaOH) solution. The mixture thickens into soap.",
         "The heat melts the oil into soap.",
         "Saponification: triglycerides react with NaOH to produce soap (fatty acid salts) and glycerol.",
         "NaOH dissolves the oil without reaction.",
         "Soap is made by cooling oil rapidly.",
         "Saponification: fat/oil + NaOH → soap + glycerol. Soap molecules have hydrophobic tails and hydrophilic heads."),
        ("A pH meter reads 2.5 for lemon juice and 8.5 for antacid solution. The difference in hydrogen ion concentration is approximately:",
         "The lemon juice has 6 times more H⁺ than the antacid.",
         "The pH scale is logarithmic — each unit = 10× difference. pH difference = 6 units, so 10⁶ = 1 million times more H⁺ in lemon juice.",
         "The antacid is actually more acidic.",
         "pH 7 is the most acidic possible.",
         "pH = -log[H⁺]. A difference of 6 pH units = 10⁶ = 1,000,000× difference in hydrogen ion concentration."),
    ]

    def _make_sc(tid, tier, levels, irt, scenarios, has_question=False,
                  q_ext="", correct_key="C"):
        def _pick(rng, ck=correct_key):
            s = rng.choice(scenarios)
            # Tuple format: (scenario, wrong_A, correct, wrong_B/C, wrong_D, exp)
            # For correct_key="B":  opt_b=s[2]=correct,  correct=s[3]=wrong
            # For correct_key="C":  opt_b=s[3]=wrong,    correct=s[2]=correct
            if ck == "B":
                return {"scenario": s[0], "opt_a": s[1], "opt_b": s[2],
                        "correct": s[3], "opt_d": s[4], "exp": s[5]}
            else:
                return {"scenario": s[0], "opt_a": s[1], "opt_b": s[3],
                        "correct": s[2], "opt_d": s[4], "exp": s[5]}
        q = ("{scenario}" + q_ext) if not has_question else ("{scenario}\n\nWhich concept BEST explains this?")
        return QuestionTemplate(
            template_id=tid, arena="scientific", domain="Science",
            difficulty_tier=tier, shs_levels=levels, irt_base=irt,
            question_template=q,
            options_template={"A":"{opt_a}","B":"{opt_b}","C":"{correct}","D":"{opt_d}"},
            correct_answer=correct_key, explanation_template="{exp}",
            param_generators={"_s":_pick},
            computed_params={
                "scenario": lambda p: p["_s"]["scenario"],
                "opt_a": lambda p: p["_s"]["opt_a"],
                "opt_b": lambda p: p["_s"]["opt_b"],
                "opt_d": lambda p: p["_s"]["opt_d"],
                "correct": lambda p: p["_s"]["correct"],
                "exp": lambda p: p["_s"]["exp"],
            },
        )

    t: List[QuestionTemplate] = []

    # Biology
    scenarios_b1 = [(s[0],s[1],s[3],s[2],s[4],s[5]) for s in _bio_bronze]
    t.append(_make_sc("sci-bio-001","Bronze",["SHS 1"],(1.0,-1.0,0.25),scenarios_b1,
                       q_ext="\n\nWhat is the MOST likely explanation?"))

    scenarios_b2 = [(s[0],s[1],s[3],s[2],s[4],s[5]) for s in _bio_silver]
    t.append(_make_sc("sci-bio-002","Silver",["SHS 1","SHS 2"],(1.2,0.0,0.25),scenarios_b2,
                       q_ext="\n\nWhich BEST explains this?"))

    scenarios_b3 = [(s[0],s[1],s[3],s[2],s[4],s[5]) for s in _bio_gold]
    t.append(_make_sc("sci-bio-003","Gold",["SHS 2","SHS 3"],(1.4,1.0,0.25),scenarios_b3,
                       has_question=True))

    # Physics
    scenarios_p1 = [(s[0],s[1],s[2],s[3],s[4],s[5]) for s in _phy_bronze]
    t.append(_make_sc("sci-phy-001","Bronze",["SHS 1"],(1.0,-1.0,0.25),scenarios_p1,
                       q_ext="\n\nWhich principle explains this?", correct_key="B"))

    scenarios_p2 = [(s[0],s[1],s[3],s[2],s[4],s[5]) for s in _phy_silver]
    t.append(_make_sc("sci-phy-002","Silver",["SHS 1","SHS 2"],(1.2,0.0,0.25),scenarios_p2,
                       q_ext="\n\nWhich BEST explains this?"))

    scenarios_p3 = [(s[0],s[1],s[3],s[2],s[4],s[5]) for s in _phy_gold]
    t.append(_make_sc("sci-phy-003","Gold",["SHS 2","SHS 3"],(1.4,1.0,0.25),scenarios_p3,
                       q_ext="\n\nWhich statement BEST explains what happens?"))

    # Chemistry
    scenarios_c1 = [(s[0],s[1],s[2],s[3],s[4],s[5]) for s in _che_bronze]
    t.append(_make_sc("sci-che-001","Bronze",["SHS 1"],(1.0,-1.0,0.25),scenarios_c1,
                       q_ext="\n\nWhat type of change is this?", correct_key="B"))

    # che-002: static options fine
    t.append(QuestionTemplate(
        template_id="sci-che-002", arena="scientific", domain="Science",
        difficulty_tier="Silver", shs_levels=["SHS 1","SHS 2"], irt_base=(1.2,0.0,0.25),
        question_template="Baking soda + vinegar → bubbles + cold. What do bubbles indicate?",
        options_template={"A":"The substances are dissolving.","B":"A reaction is producing a gas.",
                          "C":"The mixture is boiling.","D":"The baking soda is melting."},
        correct_answer="B",
        explanation_template="Bubbles = gas production. Acid (vinegar) + carbonate (baking soda) → CO₂ gas.",
        param_generators={},
    ))

    scenarios_c3 = [(s[0],s[1],s[3],s[2],s[4],s[5]) for s in _che_gold]
    t.append(_make_sc("sci-che-003","Gold",["SHS 2","SHS 3"],(1.4,1.0,0.25),scenarios_c3,
                       q_ext="\n\nWhich BEST explains the observation?"))

    # Experimental design
    t.append(QuestionTemplate(
        template_id="sci-exp-001", arena="scientific", domain="Science",
        difficulty_tier="Bronze", shs_levels=["SHS 1"], irt_base=(1.0,-1.0,0.25),
        question_template="Student tests if music helps plants grow. One plant gets music, the other doesn't.\n\nIndependent variable?",
        options_template={"A":"Plant growth","B":"The music (presence/absence)",
                          "C":"The amount of water","D":"The amount of sunlight"},
        correct_answer="B",
        explanation_template="The independent variable is what the experimenter changes. Music is changed; everything else is constant.",
        param_generators={},
    ))
    t.append(_make_sc("sci-exp-002","Silver",["SHS 1","SHS 2"],(1.2,0.0,0.25),
        [("Pharmacist tests a new drug. Group A gets the drug. Group B gets a placebo.",
          "Group B (the placebo group)","Group A (the drug group)","Both groups","Neither group",
          "Group B receives a placebo with no active ingredient, serving as the control."),
         ("Biologist tests fertiliser on tomato plants. Group 1 gets fertiliser. Group 2 gets none.",
          "Group 2 (no fertiliser)","Group 1 (with fertiliser)","Both groups","The soil itself",
          "Group 2 receives no fertiliser, serving as the baseline to measure fertiliser's effect.")],
        q_ext="\n\nWhat is the control group?"))

    return t


# ══════════════════════════════════════════════════════════════════════════════
# COMMUNICATION / GENERAL REASONING (all scenario-based)
# ══════════════════════════════════════════════════════════════════════════════

def _comm_templates() -> List[QuestionTemplate]:
    t: List[QuestionTemplate] = []

    # ── Comprehension ────────────────────────────────────────────────────
    _comp_b = [("Adwoa woke up early, packed her bag, and walked to school. She smiled seeing her friends at the gate.",
                "What is Adwoa most likely feeling?","Sad","Excited","Angry","Tired",
                "Adwoa smiled when she saw her friends, suggesting she is happy."),
               ("Harmattan brings dry, dusty winds from the Sahara. Mornings are cold; midday is hot.",
                "What best describes harmattan?","Hot all day","Cold mornings, hot afternoons","Cold all day","Rainy",
                "The passage says harmattan air is cold in mornings but hot by midday.")]
    _comp_s = [("Education is more than passing exams. It's about thinking critically and contributing to society.",
                "Main point?","Exams are most important","Education involves thinking & contributing, not just exams",
                "Creative subjects should replace exams","Only smart people need education",
                "Education goes beyond exams to include critical thinking and societal contribution."),
               ("Mobile phones transformed African information access. Farmers check prices, students learn online.",
                "What has mobile growth done?","Made phones expensive","Transformed information access",
                "Reduced farming","Eliminated businesses",
                "Mobile growth 'has transformed how people access information' with concrete examples.")]
    _comp_g = [("Sustainable development says growth and environmental protection can coexist.",
                "What does sustainable development claim?","Growth & environment CANNOT coexist",
                "Growth & environment CAN coexist","Stop all growth","Environment only matters",
                "The passage says these are 'not opposing goals.'"),
               ("Critical thinking means evaluating evidence, identifying assumptions, and considering alternatives.",
                "NOT part of critical thinking?","Evaluating evidence","Accepting arguments at face value",
                "Identifying assumptions","Considering alternative views",
                "The passage lists evaluating evidence, identifying assumptions, and alternatives — NOT blind acceptance.")]
    def _mk_comp(tid,tier,levels,irt,scenes,ck="B"):
        def _pk(r):
            s=r.choice(scenes); return {"p":s[0],"q":s[1],"a":s[2],"b":s[3],"c":s[4],"d":s[5],"e":s[6]}
        return QuestionTemplate(template_id=tid,arena="communication",domain="Verbal",
            difficulty_tier=tier,shs_levels=levels,irt_base=irt,
            question_template='Read:\n"{p}"\n\n{q}',
            options_template={"A":"{a}","B":"{b}","C":"{c}","D":"{d}"},
            correct_answer=ck,explanation_template="{e}",
            param_generators={"_s":_pk},
            computed_params={"p":lambda p:p["_s"]["p"],"q":lambda p:p["_s"]["q"],
                             "a":lambda p:p["_s"]["a"],"b":lambda p:p["_s"]["b"],
                             "c":lambda p:p["_s"]["c"],"d":lambda p:p["_s"]["d"],
                             "e":lambda p:p["_s"]["e"]})
    t.append(_mk_comp("comm-comp-001","Bronze",["SHS 1"],(1.0,-1.0,0.25),_comp_b))
    t.append(_mk_comp("comm-comp-002","Silver",["SHS 1","SHS 2"],(1.2,0.0,0.25),_comp_s,ck="C"))
    t.append(_mk_comp("comm-comp-003","Gold",["SHS 2","SHS 3"],(1.3,1.0,0.25),_comp_g,ck="C"))

    # ── Decision ─────────────────────────────────────────────────────────
    _dec_b = [("You see a younger student being teased. They look upset.",
               "Ignore it","Kindly intervene or tell a teacher","Join the teasing","Film it",
               "The best action is to stop bullying by intervening or informing a teacher."),
              ("A friend asks to copy your homework.",
               "Let them copy","Offer to explain the topic","Report them to the teacher","Say no and walk away",
               "The kindest approach is to teach so they understand, rather than enabling copying."),
              ("You find a wallet with money and ID.",
               "Keep the money","Return it using the ID","Give it to a friend","Leave it",
               "The honest action is to return the wallet using the identification.")]
    _dec_s = [("Debate on whether social media helps or hinders education.",
               "Argue without preparing","Research both sides and prepare evidence","Read from a phone","Refuse",
               "A well-prepared argument requires research and evidence."),
              ("Group project deadline approaching; one member not contributing.",
               "Do their work silently","Talk to them and redistribute tasks","Remove their name","Complain to others",
               "Direct communication is best — the person may need support, not criticism."),
              ("One hour: study for test, help sibling with homework, or watch a show.",
               "Watch a show","Prioritise studying then help sibling","Help sibling then cram","Do nothing",
               "Balance priorities: do the time-sensitive task (studying) first, then help.")]
    _dec_g = [("Factory creates 500 jobs but requires cutting down a forest that is a water catchment for farms.",
               "Jobs > forests always","Balance economic benefits against environmental costs","Stop the factory","Relocate farms",
               "This trade-off requires considering both economic development and environmental sustainability."),
              ("School requires smartwatches tracking attendance, location, study time.",
               "It's clearly good","Balances safety vs privacy","Privacy is never worth sacrificing","Students have no say",
               "This policy creates tension between safety and privacy that deserves careful consideration."),
              ("Scholarship requires teaching in home community for 3 years after graduation.",
               "Unfair — restricts freedom","Mutually beneficial exchange","Students shouldn't give back","Only rich should pay",
               "The scholarship creates a reciprocal arrangement benefiting both student and community.")]
    def _mk_dec(tid,tier,levels,irt,scenes,qstr,ck="B"):
        def _pk(r):
            s=r.choice(scenes); return {"s":s[0],"a":s[1],"b":s[2],"c":s[3],"d":s[4],"e":s[5]}
        return QuestionTemplate(template_id=tid,arena="communication",domain="General",
            difficulty_tier=tier,shs_levels=levels,irt_base=irt,
            question_template=qstr,
            options_template={"A":"{a}","B":"{b}","C":"{c}","D":"{d}"},
            correct_answer=ck,explanation_template="{e}",
            param_generators={"_s":_pk},
            computed_params={"s":lambda p:p["_s"]["s"],"a":lambda p:p["_s"]["a"],
                             "b":lambda p:p["_s"]["b"],"c":lambda p:p["_s"]["c"],
                             "d":lambda p:p["_s"]["d"],"e":lambda p:p["_s"]["e"]})
    t.append(_mk_dec("comm-dec-001","Bronze",["SHS 1"],(1.0,-1.0,0.25),_dec_b,
                      "{s}\n\nWhat is the BEST course of action?"))
    t.append(_mk_dec("comm-dec-002","Silver",["SHS 1","SHS 2"],(1.1,0.0,0.25),_dec_s,
                      "{s}\n\nWhich approach is MOST reasonable?",ck="C"))
    t.append(_mk_dec("comm-dec-003","Gold",["SHS 2","SHS 3"],(1.3,1.0,0.25),_dec_g,
                      "{s}\n\nWhich BEST analyses the situation?",ck="C"))

    # ── Vocabulary ───────────────────────────────────────────────────────
    t.append(QuestionTemplate(
        template_id="comm-voc-001", arena="communication", domain="Verbal",
        difficulty_tier="Bronze", shs_levels=["SHS 1"], irt_base=(1.0,-1.0,0.25),
        question_template='In "{sentence}", "{word}" means:',
        options_template={"A":"{a}","B":"{b}","C":"{c}","D":"{d}"},
        correct_answer="B", explanation_template="{exp}",
        param_generators={"_s":pick_from([
            {"sentence":"The dazzling light made her shield her eyes.","word":"dazzling",
             "a":"Dim","b":"Blindingly bright","c":"Colourful","d":"Distant",
             "exp":'"Dazzling" means extremely bright, hard to look at.'},
            {"sentence":"His compelling argument changed everyone's mind.","word":"compelling",
             "a":"Weak","b":"Convincing","c":"Confusing","d":"Long",
             "exp":'"Compelling" means very convincing or persuasive.'},
            {"sentence":"The dilapidated building needed urgent repairs.","word":"dilapidated",
             "a":"Modern","b":"Run-down","c":"Spacious","d":"Secure",
             "exp":'"Dilapidated" means in a state of disrepair or ruin.'},
            {"sentence":"She gave a candid, honest response.","word":"candid",
             "a":"Vague","b":"Frank","c":"Harsh","d":"Polite",
             "exp":'"Candid" means truthful and straightforward.'},
            {"sentence":"The team collaborated to finish the project.","word":"collaborated",
             "a":"Competed","b":"Worked together","c":"Argued","d":"Waited",
             "exp":'"Collaborated" means worked jointly with others.'},
        ])},
        computed_params={"sentence":lambda p:p["_s"]["sentence"],"word":lambda p:p["_s"]["word"],
                         "a":lambda p:p["_s"]["a"],"b":lambda p:p["_s"]["b"],
                         "c":lambda p:p["_s"]["c"],"d":lambda p:p["_s"]["d"],
                         "exp":lambda p:p["_s"]["exp"]},
    ))
    t.append(QuestionTemplate(
        template_id="comm-voc-002", arena="communication", domain="Verbal",
        difficulty_tier="Silver", shs_levels=["SHS 1","SHS 2"], irt_base=(1.1,0.0,0.25),
        question_template='"The scientist spoke with such ________ that no one questioned her expertise."\n\nBEST word?',
        options_template={"A":"{a}","B":"{b}","C":"{c}","D":"{d}"},
        correct_answer="B", explanation_template="{exp}",
        param_generators={"_s":pick_from([
            {"a":"confusion","b":"authority","c":"hesitation","d":"anger",
             "exp":'"Authority" means expert knowledge commanding respect.'},
            {"a":"doubt","b":"conviction","c":"indifference","d":"fear",
             "exp":'"Conviction" means strong belief or certainty.'},
            {"a":"stuttering","b":"fluency","c":"whispering","d":"shouting",
             "exp":'"Fluency" means smooth, effortless expression.'},
            {"a":"rudeness","b":"eloquence","c":"silence","d":"simplicity",
             "exp":'"Eloquence" means fluent and persuasive speaking.'},
        ])},
        computed_params={"a":lambda p:p["_s"]["a"],"b":lambda p:p["_s"]["b"],
                         "c":lambda p:p["_s"]["c"],"d":lambda p:p["_s"]["d"],
                         "exp":lambda p:p["_s"]["exp"]},
    ))
    t.append(QuestionTemplate(
        template_id="comm-voc-003", arena="communication", domain="Verbal",
        difficulty_tier="Gold", shs_levels=["SHS 2","SHS 3"], irt_base=(1.2,1.0,0.25),
        question_template='"The speech was rhetoric, not substance."\n\n"Rhetoric" means:',
        options_template={"A":"Facts and figures","B":"Persuasive but empty language",
                          "C":"Scientific analysis","D":"Written documentation"},
        correct_answer="B",
        explanation_template='"Rhetoric" is persuasive language that often lacks meaningful content. The passage contrasts it with "substance."',
        param_generators={},
    ))

    # ── Argument Analysis ───────────────────────────────────────────────
    t.append(_mk_dec("comm-arg-001","Silver",["SHS 1","SHS 2"],(1.2,0.0,0.25),
        [("Students who eat breakfast perform better. So schools should provide free breakfast.",
          "Breakfast is cheap","Correlation ≠ causation — breakfast-eaters may have other advantages","Teachers eat breakfast too","All students like breakfast",
          "This weakens by pointing out correlation ≠ causation. Other factors may explain the link."),
         ("City A has more police and lower crime than City B. So more police reduce crime.",
          "City B is younger","Other factors (economy, schools) may explain lower crime","Police earn more in City A","City A is smaller",
          "The argument assumes police cause lower crime, but better economy/education could explain it."),
         ("New teaching method → test scores improved. So it's more effective.",
          "Old method was cheaper","Other changes (smaller classes, better materials) may have helped","Students preferred old method","New method was harder for teachers",
          "Improved scores could be due to other simultaneous changes.")],
        "{s}\n\nWhich would WEAKEN this argument?",ck="C"))
    t.append(_mk_dec("comm-arg-002","Gold",["SHS 2","SHS 3"],(1.4,1.0,0.25),
        [("Raising the school leaving age will reduce unemployment because unqualified teens struggle.",
          "Teens want to leave early","Staying in school assumes they'll gain employable qualifications","Other countries have different ages","Some jobs don't need qualifications",
          "Assumes staying longer = useful qualifications. If they don't learn employable skills, policy won't help."),
         ("Train community health workers rather than build hospitals. Workers can reach remote villages.",
          "Hospitals are more expensive","Workers need proper training/support to be effective","Villages prefer hospitals","Doctors are better",
          "Assumes community health workers can adequately handle needs without proper training and supplies.")],
        "{s}\n\nWhich assumption does this depend on?",ck="C"))

    # ── Fact vs Opinion ──────────────────────────────────────────────────
    _facts = [{"a":"Chocolate is the best food.","b":"Maths is too difficult.",
               "c":"Ghana became independent in 1957.","d":"Everyone should exercise.",
               "e":'"Ghana became independent in 1957" can be verified historically.'},
              {"a":"Football is the best sport.","b":"School uniforms are ugly.",
               "c":"Accra is the capital of Ghana.","d":"Reading is boring.",
               "e":'"Accra is the capital of Ghana" is verifiable geography.'},
              {"a":"Summer is the best season.","b":"Cats are better than dogs.",
               "c":"Water freezes at 0°C.","d":"Homework should be banned.",
               "e":"Water's freezing point is scientifically measurable."},
              {"a":"Pizza tastes better than banku.","b":"Monday is the worst day.",
               "c":"The Earth orbits the Sun.","d":"Everyone should learn to code.",
               "e":"The Earth's orbit is an established scientific fact."}]
    t.append(QuestionTemplate(
        template_id="comm-fact-001", arena="communication", domain="General",
        difficulty_tier="Bronze", shs_levels=["SHS 1"], irt_base=(1.0,-1.0,0.25),
        question_template="Which is a FACT (not an opinion)?",
        options_template={"A":"{a}","B":"{b}","C":"{c}","D":"{d}"},
        correct_answer="C", explanation_template="{e}",
        param_generators={"_s":pick_from(_facts)},
        computed_params={"a":lambda p:p["_s"]["a"],"b":lambda p:p["_s"]["b"],
                         "c":lambda p:p["_s"]["c"],"d":lambda p:p["_s"]["d"],
                         "e":lambda p:p["_s"]["e"]},
    ))

    # ── Main Idea ────────────────────────────────────────────────────────
    _main = [("Trees provide shade, clean air, prevent erosion, and provide habitats. More trees = better life.",
              "Trees are expensive","Only birds benefit","Trees improve quality of life in many ways","Replace all buildings",
              "The passage lists many benefits of trees and concludes they improve life."),
             ("Reading improves vocabulary, concentration, and exposes new ideas. 20 min/day makes a difference.",
              "Reading takes too much time","Only fiction is worth reading","Regular reading has many benefits","Only students should read",
              "The passage emphasises the benefits of regular reading."),
             ("Teamwork combines strengths to achieve difficult goals. Communication and trust help solve complex problems.",
              "Working alone is better","Teams should avoid disagreements","Teamwork with communication helps solve problems","Only large teams succeed",
              "The passage explains how teamwork and communication solve problems effectively.")]
    t.append(_mk_dec("comm-main-001","Bronze",["SHS 1"],(1.0,-1.0,0.25),_main,
                      "{s}\n\nWhat is the main idea?",ck="C"))

    return t


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
