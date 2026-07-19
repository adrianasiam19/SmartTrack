import json
from pathlib import Path
from collections import Counter

data = Path("data")
files = [
    "questions_v2.json",
    "questions_expanded.json",
    "questions.json",
    "communication_shs1.json",
    "scientific_thinking_shs3.json",
    "atlas_question_bank.json",
    "psychometric_cards.json",
    "curriculum_lessons.json",
    "modules.json",
    "communication_raw.json",
]

for fn in files:
    p = data / fn
    if not p.exists():
        print(f"=== {fn}: MISSING ===")
        continue
    with open(p, encoding="utf-8") as f:
        raw = json.load(f)
    print(f"\n=== {fn} ===")
    print(f"type={type(raw).__name__}", end="")
    if isinstance(raw, list):
        print(f" len={len(raw)}")
        if raw:
            print("keys:", sorted(raw[0].keys()) if isinstance(raw[0], dict) else type(raw[0]))
            sample = raw[0]
            if isinstance(sample, dict):
                s = {
                    k: (v[:80] + "...") if isinstance(v, str) and len(v) > 80 else v
                    for k, v in sample.items()
                }
                print("sample:", json.dumps(s, ensure_ascii=False)[:700])
            shs_c = Counter()
            tier_c = Counter()
            arena_c = Counter()
            domain_c = Counter()
            subject_c = Counter()
            for q in raw:
                if not isinstance(q, dict):
                    continue
                levels = q.get("shs_levels") or q.get("shs_level") or q.get("level")
                if isinstance(levels, list):
                    for L in levels:
                        shs_c[str(L)] += 1
                elif levels is not None:
                    shs_c[str(levels)] += 1
                if q.get("difficulty_tier"):
                    tier_c[q["difficulty_tier"]] += 1
                if q.get("arena"):
                    arena_c[q["arena"]] += 1
                if q.get("domain"):
                    domain_c[q["domain"]] += 1
                if q.get("subject"):
                    subject_c[q["subject"]] += 1
                if q.get("category"):
                    subject_c["cat:" + q["category"]] += 1
            if shs_c:
                print("shs_levels counts:", dict(shs_c))
            if tier_c:
                print("difficulty_tier:", dict(tier_c))
            if arena_c:
                print("arena:", dict(arena_c))
            if domain_c:
                print("domain top:", dict(domain_c.most_common(10)))
            if subject_c:
                print("subject/cat top:", dict(list(subject_c.most_common(15))))
    elif isinstance(raw, dict):
        print(f" keys={list(raw.keys())[:20]}")
        for k, v in raw.items():
            if isinstance(v, list):
                print(f"  {k}: list len={len(v)}")
                if v and isinstance(v[0], dict):
                    print(f"    item keys: {sorted(v[0].keys())}")
                    s = {
                        kk: (vv[:80] + "...") if isinstance(vv, str) and len(vv) > 80 else vv
                        for kk, vv in v[0].items()
                    }
                    print("    sample:", json.dumps(s, ensure_ascii=False)[:600])
                    # category counts for atlas
                    if "category" in v[0]:
                        print("    categories:", dict(Counter(x.get("category") for x in v).most_common(20)))
            elif isinstance(v, dict):
                print(f"  {k}: dict keys={list(v.keys())[:10]}")
