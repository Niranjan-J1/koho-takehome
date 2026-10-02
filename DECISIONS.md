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

## 2026-10-02: Taxonomy weak spots fixed and YAML validated
**Decision:** Before any model run, I fixed three weak spots in `taxonomy.yaml` by reasoning, not from dev errors:
- Transport: gas-station and fuel-brand merchants are Transport, even if they also run convenience stores.
- Bills & Utilities: only natural gas utility providers belong here. Gas-station merchants and any bare "gas" at a fuel merchant are Transport.
- Entertainment: video game stores and publishers are Entertainment. A description naming a game subscription service is Subscriptions.

**Validation:** Parsed with PyYAML. 12 unique categories, each with `name` and `definition`, only the keys `name`, `definition` and `tie_break`, and Other is last.

**Known limitations:**
- The refund rule depends on the string saying refund, reversal or return. Other refunds will be categorised by merchant.
- Hybrid gas and convenience chains rely on the string making the fuel identity recognisable.

## 2026-10-02: Classifier model, gemini-3.8-flash
**Decision:** The classifier model is `gemini-3.8-flash`, chosen from the models my key can access (listed via `src/list_models.py`, 61 models returned).
**Reasoning:**
- It is a current non-preview Flash model.
- Flash balances capability with free-tier access.
- Pro left the free tier in April 2026.
- The explicit string is pinned rather than a `-latest` alias, because aliases can change which model they point to and would break reproducibility and the A vs B comparison.

## 2026-10-02: Same model for Approach A and Approach B
**Decision:** The same model is used for both Approach A and Approach B.
**Reasoning:** The only variable between them is the prompt detail level.

## 2026-10-02: Known limitation, optimistic accuracy
**Limitation:** I am using the newest, strongest free Flash model on synthetic data. This likely makes the task easier than real traffic, so reported accuracy will be optimistic.

## 2026-10-02: Synthetic data authored directly by Claude Code
**Decision:** The 300 rows in `data/transactions.csv` were written directly by Claude Code, not generated by Gemini and not by a script that calls an LLM. Rows were authored in category batches, then shuffled with a fixed seed (42) before ids `t001` to `t300` were assigned, so id order does not leak category.
**Reasoning:** The classifier is Gemini, so a different author avoids same-model contamination. The shuffle keeps the labelling order and later splits free of category structure.
**Sealed file:** `data/generation_meta.csv` (`intended_category`, `messiness_tags`, `is_ambiguous`) exists for coverage checks and later analysis. It is never ground truth. I do not open it while labelling.
**Design:**
- Intended counts: Dining 40, Shopping 36, Groceries 34, Transport 33, Income & Transfers 26, Subscriptions 24, Bills & Utilities 22, Health & Wellness 20, Fees & Interest 18, Travel 16, Entertainment 16, Other 15. Every class has at least 15 rows.
- 39 rows are marked ambiguous (Amazon, Walmart, Costco, Shoppers Drug Mart, bare Uber, bare PayPal, hybrid gas, bare GAS, gaming, bare INTEREST, and strings truncated beyond recognition). Ambiguous merchants are exempt from the 3-4 variant cap, up to about 6 each, so they survive the split.
- No dollar amounts. A check rejects currency patterns only, and leaves store numbers such as #1234 alone.
- No few-shot pool. The headline comparison (A vs B) does not use few-shot, so the leftover unlabelled rows are reserve.

## 2026-10-02: Known limitations of the synthetic data
- **Optimistic accuracy.** Claude Code wrote both the taxonomy and the data, so the strings may fit the categories more neatly than real transactions would. This adds to the optimism already noted for the strong free Flash model.
- **Realism.** The strings are plausible, not verbatim from real bank statements. Claude Code knows the general shape of processor strings, not each bank's exact format.
- **Intended categories are guesses.** For ambiguous rows, `intended_category` is the generator's most likely guess. My labels are the ground truth and may legitimately differ.
- **Small dev classes.** With about 50 dev rows over 12 classes, rare classes get only a few dev rows each, so per-class accuracy will be noisy.

## AI mistakes caught
- 2026-10-02: AI-drafted tie-breaks depended on information not present in a single transaction string.
