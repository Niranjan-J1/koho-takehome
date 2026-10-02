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

## 2026-10-02: Taxonomy provenance
**Decision:** The first taxonomy draft was written by Claude Code. I reviewed it, then got a second opinion from a separate Claude chat session, which found the problems listed in the entries below. I made the revision decisions.
**Note:** The first draft existed only in chat and was never committed, so git history starts at the revised version.

## 2026-10-02: Principle, tie-breaks must be decidable from the description string
**Decision:** Every tie-break must be decidable from a single transaction description string.
**Reasoning:** A rule that depends on information the string cannot contain (whether a payment recurs, what was bought) cannot be applied by the model or by me when labelling, so it adds noise instead of signal.

## 2026-10-02: Taxonomy revisions
**Decision:**
- Subscriptions: defined by merchant type (streaming, music, software, cloud services), not by recurrence.
- Health & Wellness: pharmacy chains go here regardless of what was bought.
- Groceries: ruled by chain type. Supermarkets and bulk food retailers stay; convenience-store chains go to Shopping.
- Bills & Utilities: says "natural gas" so it cannot be confused with fuel. "Rent" is removed.
- Income & Transfers: deliberately kept as "non-merchant money movement". Cash withdrawals are added, since ATM cash is common on a prepaid card.
- New category Entertainment (cinemas, concerts, events, games), making 12 categories. Streaming stays in Subscriptions.

**Known limitation:** Rent usually arrives as an e-transfer, so it will land in Income & Transfers.

## 2026-10-02: B's definitions and tie-breaks are frozen before the first model run
**Decision:** B's definitions and tie-breaks are frozen before the first model run. They must come from reasoning about the categories, not from errors seen on dev. Any later change must be logged with its reason, and I will weigh both approaches equally when tuning.

## 2026-10-02: One taxonomy file, two prompt detail levels
**Decision:** A single `taxonomy.yaml` feeds both approaches. The prompt builder has a detail setting: `names` (Approach A) or `full` (Approach B, which adds definitions and tie-breaks). Everything else in the prompt is identical.
**Reasoning:** A is a strict subset of B, so the label set is the same.

## AI mistakes caught
- 2026-10-02: AI-drafted tie-breaks depended on information not present in a single transaction string.
