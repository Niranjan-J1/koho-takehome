# Labelling guide

Applies to `dev_labels.csv` and `test_labels.csv`. Labels are hand-written by the author and are ground truth.

## Categories
Copy these verbatim into the `label` column (spelling as in `taxonomy.yaml`):

```
Groceries
Dining
Transport
Shopping
Subscriptions
Bills & Utilities
Health & Wellness
Entertainment
Travel
Fees & Interest
Income & Transfers
Other
```

## Convention (frozen 2026-10-02, before any model run; PayPal rule amended 2026-10-02, see DECISIONS.md)
- Unrecognizable/truncated strings (e.g. PETRO-): label Other.
- Bare ambiguous merchants, default rules: AMAZON → Shopping; bare PAYPAL → Other (unknowable); PAYPAL with a transfer/xfer keyword → Income & Transfers; bare GAS → Transport.
- Hybrid gas/convenience: fuel-first stations → Transport; convenience chains → Shopping unless the string says fuel.
- Pharmacy chains → Health & Wellness regardless.
- When genuinely torn, pick the best fit and write why under "Labelling notes" below, with the row id.

## Practical
- Label test before any dev model run, to prevent drift from seeing model errors.
- Never open `generation_meta.csv` while labelling.

## Labelling notes
One line per torn case: `id: reason`. The label files have no note column (dropped 2026-10-02).

_None recorded. No notes were written for any dev or test row._
