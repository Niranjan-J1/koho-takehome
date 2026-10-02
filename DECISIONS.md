# Decisions

## 2026-10-02: Gemini free tier, one model family
**Decision:** The classifier is Gemini via the Google AI Studio free tier. One model family only. The exact model string is confirmed by the author from the AI Studio model list.
**Reasoning:** The free tier keeps cost at zero, and a single family keeps the comparison clean.

## 2026-10-02: Headline comparison, Approach A vs Approach B
**Decision:** Approach A is a prompt with category names only. Approach B is the same prompt plus definitions and tie-break rules.
**Reasoning:** Same model, same data, only the prompt differs, so any difference in results is attributable to the prompt.

## 2026-10-02: Secondary analysis, confidence vs errors
**Decision:** On the better approach, check whether the model's self-reported confidence predicts its errors (accuracy vs coverage). No repeated sampling for now.
**Reasoning:** Scoped to the 4-hour limit and the free-tier quota. Repeated sampling multiplies calls.
**Caveat:** Self-reported confidence is often poorly calibrated, and ~50 dev items is thin for an accuracy-vs-coverage curve.

## 2026-10-02: Generated data, hand-written labels, blind labelling
**Decision:** `data/transactions.csv` is generated (`id`, `description`) with no category column. Only `data/dev_labels.csv` and `data/test_labels.csv` are hand-written by the author. Dev is ~50 items for iteration, and test is ~100 items, run once at the end.
**Reasoning:** Generated data carries no labels, so labelling is blind: the author labels without seeing any generator intent or model output. Model-generated labels are never used as ground truth.

## 2026-10-02: Seeded split done before labelling
**Decision:** `dev_transactions.csv` and `test_transactions.csv` are produced from `transactions.csv` by a seeded split script, unlabelled, before any labelling happens.
**Reasoning:** A fixed seed makes the split reproducible. Splitting first means labelling and prompt iteration cannot influence which items land in test.

## 2026-10-02: Cache every LLM call on disk
**Decision:** Every LLM response is cached on disk in `cache/` (git-ignored), with temperature 0.
**Reasoning:** The free-tier quota is limited, and caching makes reruns free and reproducible.

## AI mistakes caught
_None logged yet. Entries are added when the author asks._
