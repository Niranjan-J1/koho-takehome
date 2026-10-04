# Results

## TL;DR
- **Question:** does giving the model the taxonomy's definitions and tie-breaks (B) beat category names alone (A)?
- **Answer:** yes, on this data. **B 99% vs A 92%** on 100 hand-labelled test rows.
- **Significance:** exact McNemar p = 0.016 (pre-registered test, alpha 0.05).
- **But:** the gap rests on 7 rows, and synthetic data makes 99% a ceiling, not a production estimate.
- **Where B wins:** non-merchant and catch-all rows (cash, refunds, "Other"). Neither approach missed a clearly-named merchant.
- **Confidence scores:** too coarse to use for triage yet (83 of 100 rows said exactly 100).

---

## The setup in one screen

| | |
|---|---|
| **Model** | gemini-3.5-flash-lite, zero-shot, temperature 0, JSON output |
| **Approach A** | Prompt lists the 12 category names only |
| **Approach B** | Same prompt, plus a one-line definition and tie-break rule per category |
| **Only difference** | The prompt's category block. Same model, same rows, same parsing. |
| **Data** | 300 synthetic Canadian bank descriptors; seeded, stratified split: dev 50 / test 100 / reserve 150 |
| **Ground truth** | My hand labels, written blind to the generator's intent |
| **Scoring** | Invalid model outputs count as wrong (there were 0) |

**Integrity guardrails**
- Analysis was **pre-registered** in `DECISIONS.md` before any test call.
- The test set was **run exactly once**. No prompt or taxonomy changes after that.
- Every prediction is in `results/*.csv`, so any number here can be audited.

---

## Headline numbers (test set, n = 100)

| Approach | Accuracy | 95% Wilson CI |
|---|---|---|
| A: names only | **92.0%** (92/100) | 85.0% to 95.9% |
| B: names + definitions + tie-breaks | **99.0%** (99/100) | 94.6% to 99.8% |

**Paired view (same 100 rows)**

| | B right | B wrong |
|---|---|---|
| **A right** | 92 | 0 |
| **A wrong** | **7** | 1 |

- **B minus A:** +7.0 points (95% paired bootstrap CI +2 to +12).
- **Exact McNemar, two-sided:** p = 0.016, on the 7 discordant rows.
- **Dev agreed in direction:** A 92%, B 100% on 50 rows, but only 4 discordant rows, p = 0.125 (not significant).

---

## How to read the statistics

1. **Why McNemar.** Both approaches classify the same rows, so the right test is paired. McNemar only looks at rows where they disagree.
2. **The result is significant but fragile.** All 7 disagreements favour B (7 to 0). If just one had flipped (6 to 1), p would be 0.125 and the gap would no longer be confirmed.
3. **The bootstrap interval is not extra evidence.** With every disagreement on B's side, no resample can show A ahead, so the interval can't go below zero by construction. I follow McNemar, the more conservative test.
4. **Conclusion:** B is better than A here, and the direction is solid. The **size** of the gap (+7 points) is uncertain.

---

## Where B's advantage came from

B didn't win on obvious merchants. It won on the non-merchant and catch-all categories, where a bare name like "Other" or "Income & Transfers" carries little meaning.

| id | description | A said | B said (correct) | Why B won |
|---|---|---|---|---|
| t228 | CASH WITHDRAWAL | Other | Income & Transfers | Definition names cash withdrawals |
| t213 | ATM W/D #3321 | Fees & Interest | Income & Transfers | Definition names cash withdrawals |
| t043 | RETURN WINNERS #212 | Shopping | Income & Transfers | Refund / return tie-break |
| t013 | CIRCLE K #2841 | Groceries | Shopping | Convenience-chain tie-break |
| t088 | SERVICEONTARIO LICENCE | Bills & Utilities | Other | Used "Other" instead of forcing a fit |
| t275 | UNIV OF TORONTO FEES | Fees & Interest | Other | Used "Other" instead of forcing a fit |
| t061 | VIA RAIL CANADA | Travel | Transport | Judgement call in my labels (the taxonomy doesn't name rail); B matched my label |

**A's weak spots, by class**

| Class | A | B |
|---|---|---|
| Other | 1/4 | 3/4 |
| Income & Transfers | 7/10 | 10/10 |

**Takeaway:** definitions matter most for categories whose names don't explain themselves.

---

## The one row both got wrong

| id | description | label | both predicted |
|---|---|---|---|
| t268 | SERVICE ONTARIO | Other | Bills & Utilities |

- Compare with **t088 `SERVICEONTARIO LICENCE`**, which B got right.
- The two strings differ in two ways: the space, and the word "LICENCE".
- With "LICENCE", the model could tell it wasn't a utility. Without it, "SERVICE ONTARIO" reads like a utility bill.
- **Root cause:** a taxonomy gap. Government services have no category.
- **Limit of the approach:** definitions only help when the string carries a signal to act on.

---

## Can B's confidence decide what to auto-accept?

The idea: auto-accept high-confidence predictions, and send the rest to a human.

| Coverage target | Rows kept | Lowest confidence kept | Accuracy |
|---|---|---|---|
| 100% | 100 | 85 | 99.0% |
| 90% | 96 | 95 | 99.0% |
| 80% | 83 | 100 | 100.0% |

- **Too coarse to rank.** Only 4 distinct confidence values; 83 of 100 rows said exactly 100. Coverage below 83% is unreachable.
- **The one error (t268) was at confidence 95.** Catching it means sending the 17 rows below 100 to a human.
- **One error is one data point**, not evidence of calibration.
- **Verdict:** not usable for triage as-is. A real system would need token log-probabilities or a self-consistency signal.

---

## What these numbers do NOT tell you

| Caveat | Why it matters |
|---|---|
| **Synthetic ceiling** | An LLM wrote the descriptors to fit my taxonomy. Real KOHO strings are messier; expect materially lower accuracy. |
| **Thin margin** | 7 discordant rows. The direction holds; the size needs a bigger labelled set. |
| **Small classes** | Per-class test counts run from 4 to 14 rows. Per-class numbers are descriptive only. |
| **One labeller** | All ground truth is mine. One dev label (FARMBOY) was wrong and corrected after the dev run; that fix is logged. |
| **Audit bias** | I only re-checked labels where the model disagreed with me, which can only raise measured accuracy. |
| **Hardest cases removed** | 11 rows were moved to reserve after their intended category was exposed; 10 of them were ambiguous. |
| **Near-duplicates** | t088 and t268 are variants of one merchant, slightly weakening independence. |
| **One model** | Results are for gemini-3.5-flash-lite. B's advantage could be smaller on a stronger model. |
| **Scope** | Canadian, English-language descriptors only. |

---

## What I'd do next
1. **Run the harness on a sample of real, messy strings**, to measure how far the synthetic ceiling sits from reality.
2. **Replace self-reported confidence** with a self-consistency or log-probability signal, then redo the coverage analysis.
3. **Add a government / public services category**, the one gap both approaches hit.
4. **Grow the labelled test set**, so the size of B's advantage can be estimated, not just its direction.

---

## Reproduce it

```
python src/compare.py --split test                 # paired A vs B, McNemar, bootstrap
python src/confidence.py --approach B --split test  # coverage table
pytest                                              # 57 tests, no API calls
```

These read the committed `results/*.csv` and need no API key. Re-running `src/eval.py` makes model calls and needs a Gemini key, because the response cache is not committed. Full decision history and every logged AI mistake: `DECISIONS.md`.
