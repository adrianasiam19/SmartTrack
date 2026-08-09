"""Stage 5 — offline verification of challenge stabilization (Parts 1–16)."""
from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    from app.config import settings
    from app.phases import question_gen as qg
    from app.phases.academic_bank import allowed_levels_for_phase
    from app.phases.curriculum_topics import (
        curriculum_gate,
        phase_curriculum_label,
        topic_prompt_block,
    )
    from app.phases.prefetch import phase_prefetch_manager
    from app.phases.question_quality import fill_blank_is_self_contained

    failures: list[str] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        status = "PASS" if cond else "FAIL"
        print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))
        if not cond:
            failures.append(name)

    print("=== Config ===")
    check("LLM primary (BANK_FIRST=False)", settings.CHALLENGE_BANK_FIRST is False)
    check("LLM attempts >= 3", settings.CHALLENGE_LLM_ATTEMPTS >= 3, str(settings.CHALLENGE_LLM_ATTEMPTS))
    check("Format version aligned", settings.CHALLENGE_FORMAT_VERSION == 12)
    check("Prefetch buffer 2–3 levels", 2 <= settings.CHALLENGE_PREFETCH_BUFFER_LEVELS <= 3, str(settings.CHALLENGE_PREFETCH_BUFFER_LEVELS))

    print("\n=== Bloom mix ===")
    r = random.Random(42)
    counts = Counter(qg._pick_bloom_level(r) for _ in range(400))
    for level in qg.BLOOM_LEVELS:
        share = counts[level] / 400
        check(f"Bloom ~25% {level}", 0.18 <= share <= 0.32, f"{share:.2f}")

    print("\n=== Curriculum mapping ===")
    for phase, label in ((1, "SHS 1"), (2, "SHS 2")):
        check(f"Phase {phase} label", label in phase_curriculum_label(phase))
        check(f"Phase {phase} bank filter", allowed_levels_for_phase(phase) == {label})
    check("Phase 3 bank allows 1–3", allowed_levels_for_phase(3) == {"SHS 1", "SHS 2", "SHS 3"})
    check("Topic lock in prompt", "HARD TOPIC LOCK" in topic_prompt_block({"topic": "T", "focus": "F"}))

    ok, reason = curriculum_gate(
        {"question_text": "In Phase 1, what is osmosis?"},
        topic={"topic": "Diffusion and osmosis", "focus": "osmosis"},
        phase_number=1,
        subject="integrated_science",
    )
    check("Reject curriculum label leak", not ok and reason == "curriculum_label_leak", reason)

    ok, reason = curriculum_gate(
        {"question_text": "What happens during osmosis across a membrane?"},
        topic={"topic": "Diffusion and osmosis", "focus": "Identify osmosis diffusion"},
        phase_number=1,
        subject="integrated_science",
    )
    check("Accept on-topic item", ok, reason)

    ok, reason = curriculum_gate(
        {
            "question_text": "Use a Punnett square for genetics and inheritance heterozygous genotype"
        },
        topic={"topic": "Plant and animal cells", "focus": "cell wall chloroplast"},
        phase_number=1,
        subject="integrated_science",
    )
    check("Reject cross-phase drift", not ok and reason.startswith("topic_drift"), reason)

    print("\n=== Image demote (not hard reject) ===")
    demoted = qg._demote_to_text_question(
        {
            "question_text": "Study the diagram. Which label is the nucleus?",
            "question_type": "diagram_label",
            "options": {"choices": {"A": "x", "B": "y"}},
            "correct_answer": "A",
            "image": {"url": "http://example/x"},
        },
        reason="verify",
        subject="integrated_science",
    )
    check("Demote type → mcq", demoted.get("question_type") == "mcq")
    check("Demote removes image", not demoted.get("image"))

    print("\n=== Soft fill_blank gate ===")
    soft_ok = fill_blank_is_self_contained(
        {
            "question_text": "A bag costs GHS 80. Discount 10%. Sale price =",
            "question_type": "fill_blank",
            "options": {"template": "Sale price = GHS ___", "answers": ["72"]},
        }
    )
    check("Self-contained fill_blank passes", soft_ok)

    print("\n=== Prefetch rolling buffer ===")
    check("Buffer size config wired", phase_prefetch_manager._buffer_size() == settings.CHALLENGE_PREFETCH_BUFFER_LEVELS)
    check("Has start_many", hasattr(phase_prefetch_manager, "start_many"))
    check("Has buffer_status", hasattr(phase_prefetch_manager, "buffer_status"))
    check("Has claim_or_wait", hasattr(phase_prefetch_manager, "claim_or_wait"))

    print("\n=== FE/BE format version ===")
    fe = (ROOT.parent / "smarttrack-frontend" / "app" / "lib" / "phasesApi.ts").read_text(
        encoding="utf-8"
    )
    check("FE CHALLENGE_FORMAT_VERSION = 12", "CHALLENGE_FORMAT_VERSION = 12" in fe)
    check("FE warmPrefetchBuffer exported", "warmPrefetchBuffer" in fe)

    print("\n=== Summary ===")
    if failures:
        print(f"{len(failures)} failed: {', '.join(failures)}")
        return 1
    print("All Stage 5 offline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
