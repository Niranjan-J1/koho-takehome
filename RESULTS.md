# Results

## What I compared
Two zero-shot approaches, same model (gemini-3.5-flash-lite), same rows,
only the prompt differs:
- **Approach A** — category names only.
- **Approach B** — category names + one-line definitions + tie-break rules.

The question: does giving the model the taxonomy's definitions and tie-breaks
actually improve classification, or do the category names alone carry enough?

## Headline numbers (test set, n=100)
| Approach | Accuracy | 95% Wilson CI |
|---|---|---|
| A (names only) | 92.0% (92/100) | 85.0%–95.9% |
| B (full spec)  | 99.0% (99/100) | 94.6%–99.8% |

Paired comparison (same 100 rows):
- Both right: 92 | Only B right: 7 | Only A right: 0 | Both wrong: 1
- B − A = **+7.0%** (95% paired bootstrap CI +2% to +12%)
- Exact McNemar, two-sided: **p = 0.016**

## What I concluded
B is significantly better than A on this data (p < 0.05). But I hold three
caveats:

1. **The result is real but fragile.** It rests on 7 discordant rows, all
   favouring B. If one had gone the other way (6–1), McNemar would give
   p ≈ 0.125 and I could no longer confirm the gap. On dev (n=50) I had only
   4 discordant rows and the same test was non-significant (p=0.125), so the
   test set was the first point where the data was thick enough to confirm a
   direction that was visible in both.

2. **99% is an optimistic ceiling, not a production expectation.** I wrote
   the taxonomy, an LLM generated the data, and a capable model classified
   it. That alignment makes the task easier than real bank data. I'd expect
   materially lower accuracy on real KOHO transaction strings.

3. **The model made zero careless errors.** Every single error (A's 8 and
   B's 1) was a genuinely ambiguous or convention-dependent string, not a
   fumbled obvious merchant. That's a finding in itself.

## Where B's advantage came from
B fixed nothing on obvious merchants — it won entirely on the catch-all and
non-merchant categories, where a bare category name carries little meaning:

| id | description | A said | B said (correct) | Why B won |
|---|---|---|---|---|
| t013 | CIRCLE K #2841 | Groceries | Shopping | convenience-chain tie-break |
| t043 | RETURN WINNERS #212 | Shopping | Income & Transfers | refund/return rule |
| t061 | VIA RAIL CANADA | Travel | Transport | transit vs travel tie-break |
| t088 | SERVICEONTARIO LICENCE | Bills & Utilities | Other | definition of Other |
| t213 | ATM W/D #3321 | Fees & Interest | Income & Transfers | cash-withdrawal definition |
| t228 | CASH WITHDRAWAL | Other | Income & Transfers | cash-withdrawal definition |
| t275 | UNIV OF TORONTO FEES | Fees & Interest | Other | definition of Other |

A's per-class weak spots were exactly these: Other (1/4) and Income &
Transfers (7/10). B took both to near-perfect.

## The one case both got wrong
| id | description | label | both predicted |
|---|---|---|---|
| t268 | SERVICE ONTARIO | Other | Bills & Utilities |

Compare with t088 `SERVICEONTARIO LICENCE`, which B got right. The only
difference is the word "LICENCE." With it, the model could tell it wasn't a
utility; without it, bare "SERVICE ONTARIO" reads like a utility bill. This
is the limit of the tie-break approach: definitions help only when the string
carries a signal to act on.

## Confidence analysis (Approach B, test)
I checked whether B's self-reported confidence could decide which predictions
to auto-accept vs route to a human.

| Coverage target | Rows kept | Min confidence | Accuracy |
|---|---|---|---|
| 100% | 100 | 85 | 99.0% |
| 90%  | 96  | 95 | 99.0% |
| 80%  | 83  | 100 | 100.0% |

**Conclusion: the confidence signal is too coarse to be useful.** B used only
4 distinct confidence values, and 83 of 100 rows claimed exactly 100. You
can't get coverage below 83% because of the tie. It weakly isolated the one
error (confidence 85), but with this little granularity I would not trust it
for triage in production. A real system would need token log-probabilities or
a self-consistency signal instead.

## What these numbers do NOT tell me
- How the model does on real, messier merchant strings (synthetic ceiling).
- Whether B's margin holds at scale — 7 discordant rows is thin.
- Per-class reliability — rare classes have 4–10 test rows, so per-class
  numbers are descriptive only.
- A few test items are near-duplicates (t088/t268), slightly weakening the
  independence behind the confidence interval.
- Anything about non-English or non-Canadian descriptors.