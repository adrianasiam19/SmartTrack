# ATLAS `ml_aspect` — Where the Career Model Fits

This note describes the trained model in `smarttrack-backend/ml_aspect/`, how it relates to live recommendations, and the **recommended architecture** so ML never drifts aggregates, cut-offs, XP, or challenge scores.

---

## 1. What is in `ml_aspect/`

| File | Role |
|------|------|
| `atlas_career_model.pkl` | Joblib bundle: RandomForest + label encoder + feature column order |
| `model_schema.json` | Feature list + 16 programme class labels |
| `predict.py` | Inference API: `predict_top_programmes(student_input, top_n=3)` |
| `train_model.py` / `generate_data.py` | Training on **synthetic** students (`synthetic_students.csv`) |
| `training_report.txt` | ~83% top-1, ~99.8% top-3 on held-out synthetic data |

### What the model predicts

A **broad career / programme family slug**, not a KNUST cut-off row:

- Science-ish: `medicine-surgery`, `nursing`, `pharmacy`, `computer-science`, `engineering-civil`, `electrical-engineering`, `agriculture`, …
- Arts / Business: `law`, `journalism`, `education`, `psychology`, `accounting`, `banking-finance`, `economics`, `marketing`, `public-administration`

### What it consumes (26 features)

1. **WASSCE subjects** — WAEC points `1–9` (A1=1 … F9=9), one float per subject  
2. **Traits** — `trait_analytical`, `trait_creative`, `trait_social`, `trait_practical`, `trait_leadership`, `trait_empathy` (0–100)  
3. **Arena accuracies** — `logic_accuracy`, `quant_accuracy`, `verbal_accuracy`, `scientific_accuracy` (0–100)  
4. **Engagement** — `xp`, `streak_days`

Missing features fall back to neutral defaults in `predict.py` (`FEATURE_DEFAULTS`).

### What it does **not** know

- KNUST aggregate  
- Cut-off points / Eligible–Stretch–Reach bands  
- Specific catalogue rows from `KNUST_Science_Engineering_Health_Cutoffs.docx`  
- University admissions rules  

It is a **profile → career affinity** classifier trained on synthetic labels, not an admissions engine.

---

## 2. What Atlas already treats as truth

After the recent recommendation work, the **authoritative** path is:

```
Uploaded WASSCE grades
  → compute aggregate (cutoffs.py)
  → gate against data/knust_cutoffs_2025.json
  → Eligible / Stretch / Reach programme lists
```

Owned by:

- `app/recommendations/cutoffs.py` — hard gate  
- `app/assessment/recommendation_engine.py` — upload → KNUST programmes only  
- `app/recommendations/service.py` — phase history uses the same gate when grades exist  

**These numbers must stay rule-based.** ML must not rewrite:

| Signal | Why ML must not touch it |
|--------|---------------------------|
| WASSCE grades / extracted records | Source of truth from upload |
| Aggregate | Admissions math |
| `eligibility_band` / cut-off | Document-backed gate |
| Challenge accuracy / IRT theta / XP / streak **as stored scores** | Learning progress integrity |

ML may **read** challenge accuracies, XP, and streak as **input features**. It must never write them back or use them to change band membership.

---

## 3. Necessity — do you need this model now?

| Need | Verdict |
|------|---------|
| Required for correct KNUST eligibility? | **No.** Cut-offs + aggregate already do that. |
| Useful as interest / career-fit signal? | **Yes**, especially for programmes **outside** the Science/Engineering/Health doc (Law, Business, Education, …). |
| Ready to replace primary recommendations? | **No.** Classes ≠ KNUST catalogue; training is synthetic; no elective/subject requirements. |

**Product necessity:** optional **second opinion** (“profile fit”), not the admissions answer.

**Engineering necessity:** wire only behind a feature flag, with a clear UI label, after a feature adapter maps live Atlas data → `model_schema.json`.

---

## 4. Architecture options (and the best one)

### Option A — ML replaces / blends primary list ❌

ML top-3 becomes (or mixes into) the main recommendation list.

**Reject.** Drift risk is high: students see `law` / `accounting` as if they were KNUST-eligible; confidence can drown cut-off truth.

### Option B — Soft re-ranker inside Eligible/Stretch only ⚠️

After `apply_cutoff_boundaries`, map ML classes → KNUST programme names and re-order only those rows.

**Possible later**, but weak today:

- Only a subset of ML classes map cleanly (`medicine-surgery` → MBChB / Human Biology, `nursing` → BSc Nursing, `computer-science` → BSc Computer Science, …).  
- Many ML classes have **no** row in the current cut-off JSON (Law, Accounting, Marketing, …).  
- Re-ranking still needs a stable mapping table and must never move a programme across bands.

Keep as a **phase-2 enhancement**, not the first integration.

### Option C — Parallel “alternate recommendations” track ✅ **Recommended**

Two outputs on the same generate call (or a sibling endpoint), clearly separated:

| Track | Source of truth | Purpose |
|-------|-----------------|--------|
| **Primary — KNUST eligibility** | Cut-off doc + aggregate | “What you can realistically aim for at KNUST (Science / Eng / Health)” |
| **Alternate — Career profile fit** | `ml_aspect` RandomForest | “What your grades + traits + arena performance look like in career terms” |

Primary is unchanged. ML never edits bands, aggregate, or stored scores. UI shows alternate as **interest / profile fit**, with copy like:

> Not an admissions guarantee. Based on your profile model, not KNUST cut-offs.

This matches your constraint (“don’t drift my scores”) and your openness to “alternate recommendations.”

---

## 5. Best place to include it in the codebase

### Recommended layout

```
smarttrack-backend/
  ml_aspect/                          # keep artefacts + predict.py here
  app/
    recommendations/
      cutoffs.py                      # UNCHANGED — hard gate
      service.py                      # phase path stays cut-off gated
      ml_career.py                    # NEW thin adapter (optional package)
    assessment/
      recommendation_engine.py        # after KNUST result, optionally attach ml block
      router.py                       # expose ml_career_fit in generate response
```

### Call graph (target)

```
POST /academic/upload          → grades only (no ML required)
GET  /recommendations/generate
        │
        ├─ RecommendationEngine.generate_recommendations()
        │     └─ apply_cutoff_boundaries(...)     → knust (PRIMARY)
        │
        └─ [if ML_RECOMMENDATIONS_ENABLED]
              build_ml_features(user, grades, psych, perfs, xp, streak)
              predict_top_programmes(features, top_n=5)
              map slugs → display labels
              → ml_career_fit (ALTERNATE, read-only)
```

### Concrete hook points

1. **Adapter** `app/recommendations/ml_career.py` (or `app/ml/career_predict.py`)  
   - Import `predict_top_programmes` from `ml_aspect.predict` (add `ml_aspect` to Python path / package).  
   - Map `AcademicRecord` subjects → `wassce_*` (use existing `grade_to_points` from `cutoffs.py`).  
   - Map psychometric tags / starter traits → `trait_*` (0–100; document the mapping).  
   - Map `UserSubjectPerformance` / skill estimates → arena accuracies.  
   - Pass `user.xp`, `user.streak`.  

2. **Generate endpoint** `GET /api/v1/challenges/recommendations/generate`  
   - Keep returning `knust` + KNUST programme cards as today.  
   - Add optional payload field, e.g.:

   ```json
   {
     "knust": { "...": "unchanged" },
     "ml_career_fit": {
       "enabled": true,
       "model_version": "atlas_career_model.pkl",
       "disclaimer": "Profile-based career fit; not KNUST cut-off eligibility.",
       "predictions": [
         { "programme": "medicine-surgery", "label": "Medicine & Surgery", "confidence": 0.41 }
       ]
     }
   }
   ```

3. **Frontend** `app/recommendations/page.tsx`  
   - Section 1: KNUST Eligible / Stretch / Reach (primary).  
   - Section 2: “Career profile suggestions (ML)” — visually secondary, collapse Reach-style treatment.  
   - Never merge the two lists into one ranked ladder without labels.

4. **Do not hook ML into**  
   - Challenge scoring / XP awards  
   - Adaptive difficulty / IRT  
   - Aggregate computation  
   - Psychometric checkpoint scoring  
   - Cut-off JSON  

5. **Phase recommendations**  
   - Keep cut-off gated when grades exist.  
   - Optionally append the same `ml_career_fit` block as informational context — still not the phase “official” programme list.

### Config

```env
ML_RECOMMENDATIONS_ENABLED=false   # default off until adapter + UI ready
ML_MODEL_PATH=ml_aspect/atlas_career_model.pkl
ML_TOP_N=5
```

Dependencies (not yet in main `requirements.txt`): `scikit-learn`, `joblib`, `pandas`, `numpy`.

---

## 6. Hard rules (anti-drift contract)

1. **Cut-offs win.** If ML says `medicine-surgery` but aggregate is Reach for MBChB, the primary UI still shows Reach — ML stays in the alternate panel.  
2. **No write-back.** Prediction code is read-only on user progress tables.  
3. **No silent blend.** Do not average ML confidence into `family_fit_score` or headroom without an explicit product decision and UI disclosure.  
4. **Defaults are not facts.** Heavy use of `FEATURE_DEFAULTS` means weak confidence — surface `features_complete: false` when many subjects/traits are missing.  
5. **Synthetic model ≠ production truth.** Treat accuracy numbers as training hygiene until retrained on real Atlas users with the same schema.

---

## 7. Class ↔ KNUST mapping (for later Option B only)

Illustrative overlaps (not wired yet):

| ML class | Possible KNUST catalogue rows |
|----------|-------------------------------|
| `medicine-surgery` | MBChB Medicine, BSc Human Biology (Medicine) |
| `pharmacy` | Doctor of Pharmacy |
| `nursing` | BSc Nursing |
| `computer-science` | BSc Computer Science |
| `electrical-engineering` | BSc Electrical Engineering |
| `engineering-civil` | BSc Civil Engineering |

Non-overlaps (alternate track only until cut-off scope expands):  
`law`, `accounting`, `marketing`, `journalism`, `education`, `banking-finance`, `public-administration`, …

---

## 8. Suggested rollout order

1. **Document + flag** (this file) — no behaviour change.  
2. **Feature adapter + unit tests** — build vector from a fixture user; assert schema keys.  
3. **API field `ml_career_fit`** behind `ML_RECOMMENDATIONS_ENABLED=false`.  
4. **UI alternate section** with disclaimer.  
5. **Logging** anonymized feature snapshots for future real-data retrain.  
6. **Only then** consider Option B in-band re-rank for mapped Science/Health/Engineering classes.

---

## 9. Bottom line

| Question | Answer |
|----------|--------|
| Where does it fit best? | **Parallel alternate track** next to KNUST cut-off recommendations, not inside the cut-off scorer. |
| Where to include it? | Adapter under `app/recommendations/` (or `app/ml/`), called from `recommendations/generate` after cut-offs; UI second section. |
| Is it necessary for correct admissions advice? | **No.** |
| Is it useful? | **Yes** — broader career fit + programmes outside the current KNUST Science/Eng/Health document. |
| Will it drift scores? | **Not if** you never feed it into aggregate, bands, XP, or challenge scoring — read features out, write predictions only into a separate response field. |

**Canonical product sentence:**  
*KNUST cut-offs decide eligibility; the career model suggests profile fit as an optional second opinion.*

---

## 10. Implementation status (wired)

### A) Legacy career RF (`atlas_career_model.pkl`)
Still in `ml_aspect/` for reference; **not** the live alternate path.

### B) KNUST Decision Tree alternate (`ml_aspect/knust_dt/`) — **live**

| Piece | Path |
|-------|------|
| Features | `ml_aspect/knust_dt/features.py` |
| Teacher (no LLM) | `soft_label.py` + cut-offs Eligible/Stretch |
| Data | `python -m ml_aspect.knust_dt.generate_data` |
| Train | `python -m ml_aspect.knust_dt.train` |
| Serve | `predict_knust_dt_alternate` — intersect Eligible∪Stretch only |
| API | `ml_alternate` on generate; `primary_source` stays `knust_cutoffs` |
| Flag | `ML_ALTERNATE_ENABLED` |

**Promotion rule:** keep DT as alternate until it consistently agrees with a trusted teacher (rule soft-rank / future human labels). Only then flip primary ranking to DT *inside* cut-off bands — never replace the cut-off gate itself.
