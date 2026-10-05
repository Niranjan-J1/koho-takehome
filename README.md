# KOHO take-home: transaction classification + evaluation harness

Classify messy Canadian bank transaction descriptions into 12 merchant
categories using an LLM, and measure honestly whether it works — and whether
giving the model the taxonomy's definitions and tie-breaks (Approach B) beats
category names alone (Approach A).

**Headline:** B 99% vs A 92% on 100 hand-labelled test rows (exact McNemar
p = 0.016, B − A = +7%). The result is statistically significant but rests on
7 discordant rows, so the size of the gap is uncertain. The high accuracy is
an optimistic synthetic ceiling, not a production estimate. See RESULTS.md for
the full read and every caveat.

## Setup
1. Python 3.11+ (developed on 3.14).
2. `pip install -r requirements.txt`
3. Create a `.env` file in the repo root with your key and the model:

   ```
   GEMINI_API_KEY=your_key_here
   GEMINI_MODEL=gemini-3.5-flash-lite
   ```

   Running the evaluation needs a `GEMINI_API_KEY`. A free Google AI Studio
   key is enough. All data is synthetic, so free-tier data-use terms are not a
   concern. Do not enable billing — it removes the free allowance.

## Run it
Dev set (for iterating; safe to run freely):

```
python src/eval.py --approach A
python src/eval.py --approach B
```

Test set (run once; guarded against accidents):

```
python src/eval.py --approach A --split test --confirm-test
python src/eval.py --approach B --split test --confirm-test
```

Compare the two approaches and analyse confidence:

```
python src/compare.py --split test
python src/confidence.py --approach B --split test
```

Run the test suite (no API calls):

```
pytest
```

Every LLM call is cached on disk under `cache/` (git-ignored). Within a
working copy, re-runs are served from that cache, so they make no new API calls
and reproduce the same numbers. The cache is not committed, so a fresh clone
starts empty and needs a key to run the evaluation.

## What's in the repo
- `taxonomy.yaml` — the 12 categories with definitions and tie-breaks. Prompts
  are built from this one file, so adding a category updates both approaches.
- `data/`
  - `transactions.csv` — 300 synthetic descriptions (`id`, `description`), no
    labels.
  - `dev_transactions.csv`, `test_transactions.csv`, `reserve_transactions.csv`
    — the seeded, stratified split (unlabelled).
  - `dev_labels.csv` (50), `test_labels.csv` (100) — my hand-written labels.
    This is the ground truth.
  - `generation_meta.csv` — sealed generator metadata (intended category,
    messiness tags). Never ground truth; never opened while labelling.
  - `LABELLING.md` — the 12 categories and the labelling convention.
- `src/`
  - `taxonomy.py` — loads and validates the taxonomy.
  - `prompts.py` — builds the A (names) and B (full) prompts from the taxonomy.
  - `llm.py` — cached Gemini client: JSON output, temperature 0, retries,
    aborts on persistent API failure (never scored as a model error).
  - `parse.py` — parses/validates output; invalid responses are scored wrong.
  - `eval.py` — runs one approach on a split; prints accuracy, Wilson CI,
    invalid count, per-class table, confusion pairs; writes a results CSV.
  - `compare.py` + `stats.py` — paired A-vs-B: exact McNemar + bootstrap CI.
  - `confidence.py` — accuracy-vs-coverage table for the confidence signal.
  - `split.py` — the seeded, stratified split.
  - `list_models.py` — lists models the key can access (setup helper).
- `results/` — per-row predictions for both approaches, for audit.
- `DECISIONS.md` — the full decision log, including every AI mistake caught.
- `RESULTS.md` — the results write-up.
- `BUILDLOG.md` — the build log.

## Key design choices (one line each; full reasoning in DECISIONS.md)
- The hand-labelled holdout is ground truth; labels were written blind, before
  any model run, with the generator's intent sealed away. One exception is
  logged: dev label t262 (FARMBOY) was corrected from Dining to Groceries after
  the dev run exposed it (see DECISIONS.md).
- The dev/test split is seeded and stratified; the test set is run exactly once.
- Temperature 0 + disk cache give reproducible re-runs. Reproducibility comes
  from the cache, not from determinism — a cleared cache can differ.
- Invalid model outputs are counted as errors, never silently dropped.
- One model for both approaches, so the only variable is the prompt detail.
