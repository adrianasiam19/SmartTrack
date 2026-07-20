# Atlas Recommendations — TODOs Before ML Integration

Status after KNUST cut-off Phases **A–C** (rule layer live):
- Cut-offs JSON loaded (`data/knust_cutoffs_2025.json`)
- WASSCE aggregate + Eligible / Stretch / Reach banding
- Soft family ranking still non-ML
- UI shows KNUST bands on Get Recommendations

**ML must wait** until the items below are solid. Cut-offs stay a hard gate; ML will only re-rank inside Eligible/Stretch.

---

## 1. Data & cut-offs hygiene

- [ ] Confirm KNUST aggregate formula against official admissions rules (core English + core Maths + which electives; programme-specific subject requirements).
- [ ] Add programme-level **required electives** (e.g. Medicine needs Biology/Chemistry) and fail closed when missing.
- [ ] Version cut-offs by cycle (`2025/2026`) and document how to refresh next year.
- [ ] Decide scope expansion: Business / Arts / Built Environment — separate cutoff files or one catalogue.
- [ ] Deduplicate / normalize campus variants (Obuasi vs Main) for display.

## 2. Grades pipeline

- [ ] Improve WASSCE upload extraction accuracy (manual grade edit UI if AI misses subjects).
- [ ] Persist computed `aggregate` + `subjects_used` on the user profile for reuse (phase recs + ML features).
- [ ] Surface “provisional aggregate” clearly when &lt; 6 usable grades.
- [ ] Allow user confirmation of grades before recommendations run.

## 3. Unify recommendation paths

Today there are two paths (phase checkpoint affinity vs upload engine). Before ML:

- [ ] Map psych affinity keys (`engineering`, `medicine_health`, …) → KNUST families / programmes consistently.
- [ ] Apply the **same cutoff gate** to phase checkpoint recommendations when grades exist.
- [ ] When grades are missing, keep interest-only ranking but always show the “subject to WASSCE cut-offs” caveat.
- [ ] Align API response shape so the frontend has one recommendation card model (family + KNUST programmes + band).

## 4. Challenge / psychometric features for ranking (still rule-based)

- [ ] Feed `UserSubjectPerformance` (challenge accuracies) into soft rank, not only rationale text.
- [ ] Feed checkpoint psych trait + affinity vectors into upload-path ranking.
- [ ] Store a stable **recommendation feature snapshot** per user/phase (aggregate, bands, psych tags, subject accuracies) for later ML training — no model call yet.

## 5. Product / UX

- [ ] Explain bands in plain language (Eligible = within cut-off; Stretch = close; Reach = aspirational).
- [ ] Let users filter by family (Health / Engineering / Science).
- [ ] Link “stretch” programmes to Learning Center topics that strengthen weak subjects.
- [ ] Hide or collapse Reach by default so it doesn’t look like false hope.

## 6. Quality & ops

- [ ] Unit tests for programme-specific elective rules once defined.
- [ ] Integration test: upload grades → generate → bands + aggregate in API payload.
- [ ] Seed / deploy checklist: ensure `knust_cutoffs_2025.json` ships with backend.
- [ ] Log recommendation runs (anonymized) for later ML dataset building.

## 7. Explicit ML hook (do last)

Only after 1–6:

- [ ] Define feature schema matching stored snapshots.
- [ ] Add `ml_rank_programmes(eligible_or_stretch, features) -> scores` behind a flag.
- [ ] Never let ML move a programme across eligibility bands.
- [ ] A/B compare rule-only vs ML re-rank on held-out users.

---

## Suggested order

1. Aggregate formula + elective requirements (1–2)  
2. Unify phase + upload recommendation paths (3)  
3. Wire challenge/psych soft features + feature snapshots (4)  
4. UX polish (5)  
5. Tests / logging (6)  
6. ML re-ranker (7)

Owner note: A–C are done; this checklist is the bridge to ML.
