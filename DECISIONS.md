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

## 2026-10-02: Seeded stratified split
**Decision:** `src/split.py` splits the 300 rows into dev 50, test 100 and reserve 150, stratified by `intended_category` from the sealed file, with seed 2026. The seed was chosen before seeing any split and will not be re-rolled. The script refuses to overwrite existing split files without `--force`.
**Reasoning:** With 12 classes and 50 dev rows, a plain random split could leave a rare class with no dev rows. Stratifying uses the sealed file only to decide membership, before any labelling, and never as a label.
**Assumption:** Intended categories are guesses for ambiguous rows, so per-class counts in my labels may drift slightly from the allocation.
**Result:** Dev gets 3 to 7 rows per class and test gets 5 to 14. Ambiguous rows: dev 3, test 12, reserve 24.
**Caveats:**
- Per-class accuracy on about 5 test rows moves in 20-point steps, so per-class numbers are descriptive only. Overall accuracy and the paired A vs B comparison on the 100 test rows are the headline results.
- Dev has only 3 ambiguous rows, so iterating on dev gives little signal on hard cases. I accept this rather than re-rolling the seed.

## 2026-10-02: 11 ids forced into reserve after exposure
**Decision:** Eleven ids are forced into reserve so that no dev or test row has an intended category I saw before labelling: `t001`, `t002`, `t003` (sealed-file rows printed in chat), Costco `t005`, `t087`, `t126`, `t157`, and Walmart `t056`, `t096`, `t159`, `t298` (intended category stated in chat). They are excluded before stratifying. If the reserve is ever used, these stay excluded.
**Cost:** 10 of the 11 are ambiguous, so dev and test lose some of their most instructive rows.

## 2026-10-02: Labelling convention, frozen before any model run
**Decision:** I label with this convention, frozen now, before any model run:
- Unrecognizable/truncated strings (e.g. PETRO-): label Other.
- Bare ambiguous merchants, default rules: AMAZON → Shopping; bare PAYPAL → Income & Transfers; bare GAS → Transport.
- Hybrid gas/convenience: fuel-first stations → Transport; convenience chains → Shopping unless the string says fuel.
- Pharmacy chains → Health & Wellness regardless.
- When genuinely torn, pick the best fit and write why in the note.

**Order:** Dev is labelled before test, and test is labelled before any dev model run, so model errors seen on dev cannot shift how I label test.
**Format:** `dev_labels.csv` and `test_labels.csv` have the columns `id`, `description`, `label`, `note`, pre-filled with ids and descriptions from the split and with empty labels. The category list and this convention live in `data/LABELLING.md`, not in a `#` header, because Python's `csv` module has no comment support and pandas' `comment="#"` would truncate descriptions at store numbers such as `#1042`.

**Measured effects (recorded, not fixed):**
- Approach B's prompt does not contain this convention. Rows where the convention decides the label (bare PayPal, truncated strings, convenience chains vs fuel) may be systematically wrong for both approaches. That error is part of what is measured.
- The frozen taxonomy's Transport tie-break says fuel brands are Transport even if they also run convenience stores, while this convention sends convenience chains to Shopping unless the string says fuel. A chain that is both can land differently under each. My label decides, with the reason in the note.

## 2026-10-02: Labelling done; note column dropped
**Status:** I finished labelling dev (50) and test (100), in that order, before any model run.
**Decision:** The `note` column is dropped from both label files, which are now `id`, `description`, `label`. Torn-case reasoning lives in `data/LABELLING.md` under "Labelling notes", next to the convention. Only where the reasoning is written changes; the convention itself is unchanged.
**Reasoning:** No note was written for any row, so the column carried no information, and one shared place for reasoning is easier to audit than a per-row column.
**Convention amendment (PayPal):** The frozen rule "bare PAYPAL → Income & Transfers" is replaced by "bare PAYPAL → Other (unknowable); PAYPAL with a transfer/xfer keyword → Income & Transfers". Bare PayPal could be a purchase, a transfer or a refund, so the string alone cannot decide it. I labelled `t016` (`PAYPAL`) as Other, and `t089` (`PAYPAL INST XFER`) stays Income & Transfers. The original entry above is left unedited for the audit trail.
**Caveat:** This change was made during test labelling, prompted by a test string, before any model run. No model output was involved. Only these two test rows are affected; dev has no PayPal rows.
**AI edit to label files, at my request:** Claude Code removed the empty `note` column from both files. It checked that every id, description and label is identical before and after, and that every label is one of the 12 taxonomy names. No label was read out or changed.

## 2026-10-03: Harness choices
**Decision:**
- Output is JSON mode with no enum constraint on the category. Any category that is not one of the 12 names, any malformed JSON and any missing field is invalid and scored as an error.
- `thinking_config` is left at the model default for both approaches. Tuning it would add a second variable next to the prompt detail level.
- The better approach for the confidence analysis is picked on dev and frozen here before the test run.
- `results/*.csv` are committed so every prediction can be audited.

**Reasoning:** An enum constraint would push invalid outputs to near zero and hide that failure mode. Picking the better approach on test would be selection on test.
**Reproducibility:** Reruns are reproducible because every response is cached on disk, not because of temperature 0 or a seed. Temperature 0 and a seed reduce variation between fresh calls but do not guarantee identical outputs, so a cleared cache can give different results.

## 2026-10-03: Switched classifier model to gemini-3.5-flash-lite

Decision: Changed GEMINI_MODEL from gemini-3.8-flash to gemini-3.5-flash-lite
for all classification runs.

Reason: Repeated 429 rate-limit errors on gemini-3.8-flash exhausted the free-
tier quota before I could complete the dev runs. Flash-Lite has higher free-
tier limits, which lets me finish the A/B comparison in one session.

Integrity: No completed result set existed when I switched — the dev run
aborted on the 429 before eval.py wrote any results file, so no results mix
two models. All reported results (dev and test, A and B) use flash-lite
consistently. One approach, one model, all rows. The cache key includes the
model name, so the handful of orphaned flash calls from the aborted run stay
separate and are not used in any result.

Trade-off: Flash-Lite is a smaller model, so absolute accuracy may be lower
than Flash would give. That doesn't affect the A-vs-B comparison, which is
what I'm measuring, because both approaches use the same model. If I regain
Flash quota, a Flash-vs-Flash-Lite comparison would be a useful add-on and is
noted as possible future work.

## 2026-10-03: Dev results and findings (exploratory)
**Model:** gemini-3.5-flash-lite. n=50 dev rows. Dev results are exploratory; the headline is the test run.

**As first scored (before the t262 label correction):**
- Approach A (names only): 90.0% (45/50), 95% Wilson CI 78.6–95.7%.
- Approach B (full definitions + tie-breaks): 98.0% (49/50), CI 89.5–99.6%.
- Paired: both right 45, only A 0, only B 4, both wrong 1.
- B - A = +8.0%, 95% paired bootstrap CI +2.0% to +16.0%.
- Exact McNemar two-sided p = 0.125 on 4 discordant rows.

**After correcting t262 (rescored from cache, 0 new API calls):**
- A: 92.0% (46/50), 95% Wilson CI 81.2–96.8%.
- B: 100.0% (50/50), CI 92.9–100.0%.
- Paired: both right 46, only A 0, only B 4, both wrong 0.
- B - A = +8.0%, 95% paired bootstrap CI +2.0% to +16.0%. Exact McNemar two-sided p = 0.125.
- The correction moved both approaches up by one row and did not change the discordant pairs.

**Interpretation:**
- The bootstrap CI excludes zero but exact McNemar is non-significant. With only 4 discordant rows this is expected: 4-0 gives p=0.125 at best, so the data is too thin to confirm the gap. Headline claim follows the more conservative test: B directionally better on dev, NOT statistically confirmed.
- The bootstrap lower bound above zero is not independent evidence. All 4 discordant rows favour B, so no resample can produce a negative difference; the lower bound sits above zero only because a resample with no discordant rows is rare. With this few discordant rows the percentile bootstrap is unreliable, which is another reason to follow McNemar.
- B's advantage came entirely from tie-breaks/definitions resolving ambiguous or convention-dependent cases, not from better handling of obvious merchants. Specifics:
  - t072 7-ELEVEN: A->Groceries, B->Shopping (convenience-chain tie-break).
  - t074 ATM WITHDRAWAL: A->Other, B->Income & Transfers (definition names cash withdrawals).
  - t273 REVERSAL TIM HORTONS: A->Dining, B->Income & Transfers (refund/reversal tie-break).
  - t012 CANADA POST: A->Bills & Utilities, B->Other (B avoided forcing a wrong fit).
- t262 FARMBOY: both approaches predicted Groceries (confidence 100 for A, 95 for B) against my Dining label; this exposed a labelling error in my own ground truth, now corrected. Farm Boy is a Canadian grocery chain, so Dining was wrong against my taxonomy's Groceries definition. Lesson recorded: when both approaches confidently disagree with a label in the same way, the label itself is worth re-checking.

**Label audit and its bias:** To avoid fixing only model-favourable rows, the other four dev errors (t012, t072, t074, t273) were re-checked. Claude Code re-checked the other four labels against the taxonomy and reported all four consistent; I reviewed its reasoning and agree. None changed; these are genuine model errors, not label errors. This audit only looked at rows where a model disagreed with me. Rows where a model agreed with a wrong label were not re-checked, so correcting disagreements can only raise measured accuracy. I checked test for any Farm Boy row before the test run: there is none.

## 2026-10-03: Test-run pre-registration (written before any test call)
- Headline comparison: test-set accuracy, Approach A vs Approach B, on the
  same 100 test rows.
- Significance test: exact McNemar, two-sided, alpha = 0.05, on the
  discordant rows. Paired bootstrap 95% CI on (B - A) reported alongside,
  with the caveat already logged that at this sample size the bootstrap is
  not independent evidence.
- Primary conclusion follows the more conservative of the two (McNemar).
- Confidence analysis: runs on Approach B only, chosen on dev (B 100% vs A
  92% after the t262 correction). Accuracy-vs-coverage via confidence.py.
- Test is run exactly once: A and B each via --split test --confirm-test,
  then compare.py --split test. No prompt or taxonomy changes after this
  entry; both are frozen. If a result looks surprising I will report it, not
  re-run to get a different number.
- Expectation recorded in advance: I expect test accuracy below the dev
  numbers (dev may be optimistic; B's 100% will likely not hold), and the
  A-vs-B gap may or may not reach significance at n=100.

## 2026-10-03: Confidence analysis method (fixed before any test call)
**Purpose:** This measures whether B's self-reported confidence can be used to decide which predictions to auto-accept vs route to a human. It is descriptive at n=100, not a calibration guarantee.
**Method (`src/confidence.py`, run as `python src/confidence.py --approach B --split test`):**
- Rank test rows by B's reported confidence, highest first.
- Report accuracy at coverage levels 100/90/80/70/60/50% (the share of highest-confidence rows kept).
- Rows with tied confidence are kept together; report the number of distinct confidence values. When a tie group straddles a coverage level, the whole group is kept and the actual coverage achieved is reported next to the target.
- Invalid or missing confidence is treated as lowest. Rows whose prediction is invalid are also ranked lowest, since an invalid prediction cannot be auto-accepted.

**Observed on dev, before test:** B reported only 3 distinct confidence values (90, 95, 100), with 42 of 50 rows at 100. The ranking is therefore coarse: no coverage below 84% is reachable on dev, and the 80/70/60/50% levels all collapse to the same 42 rows. B made no dev errors, so dev only shows that the code runs, not whether confidence predicts errors. If test shows the same coarseness, the result will be reported as "confidence too coarse to rank", not tuned away.

## AI mistakes caught
- 2026-10-02: AI-drafted tie-breaks depended on information not present in a single transaction string.
- 2026-10-02: When showing a commit diff, Claude Code printed the first rows of the sealed `generation_meta.csv`, exposing intended categories for `t001` to `t003`. Fixed by forcing them into reserve.
- 2026-10-02: In a progress report, Claude Code stated its intended category for Costco (Groceries) and Walmart (Shopping), exposing 8 rows. Fixed by forcing them into reserve.
- 2026-10-02: Per-category ambiguous counts in a progress report could be matched against the ambiguous merchant list to infer intended categories (for example, 3 ambiguous Health & Wellness rows and 3 Shoppers rows). This is an inferential exposure only. The taxonomy's pharmacy rule already settles Shoppers, so no rows were reserved for it.
- 2026-10-02: Claude Code authored every intended category, so it must not suggest labels for dev or test rows.
- 2026-10-03: My own holdout contained a labelling error (t262 FARMBOY labelled Dining, should be Groceries), surfaced by model/label disagreement rather than by me.
