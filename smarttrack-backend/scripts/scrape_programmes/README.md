# Programme scrape → Course Directory

Offline pipeline that collects undergraduate programme info from Ghanaian universities and **merges rich detail into** `data/course_directory.json` for the Atlas Course Directory UI.

**Does not** change the Recommendations engine or cut-off eligibility.

## Run

From `smarttrack-backend` (venv active):

```bash
pip install beautifulsoup4 lxml tenacity
python -m scripts.scrape_programmes
```

Options:

```bash
python -m scripts.scrape_programmes --universities ug,upsa
python -m scripts.scrape_programmes --skip-merge
```

## Outputs

| File | Purpose |
|------|---------|
| `data/programmes/programmes_ug.json` | UG catalogue scrape |
| `data/programmes/programmes_knust.json` | KNUST names (from local cutoffs list — cut-offs not used in Course Directory) |
| `data/programmes/programmes_ucc.json` | UCC (partial/skipped if JS-only) |
| `data/programmes/programmes_upsa.json` | UPSA admissions list |
| `data/programmes/programmes_all.json` | Combined scrape rows |
| `data/course_directory.json` | Enriched with `offerings`, longer `detailed_overview`, `source_urls` |

## Status notes

- **UG**: Full HTML catalogue (`tid=18` undergraduate). Best overviews.
- **UPSA**: Programme names from admissions page; short generated overview.
- **KNUST**: Live portal is JS-heavy; names exported from `knust_cutoffs_2025.json` for coverage only.
- **UCC**: Livewire/JS catalogue — HTTP pass is partial; use Playwright later for full detail.

Respect `robots.txt`, keep request gaps (~1s), and never invent programmes when a site fails — write `status: skipped|error` stubs instead.

## Tests

```bash
python -m pytest tests/test_programme_scrape_schema.py -q
```
