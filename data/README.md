# Data

| File | Origin | Columns |
|------|--------|---------|
| `transactions.csv` | Generated, no labels | `id`, `description` |
| `dev_transactions.csv` | Seeded split script output, unlabelled | `id`, `description` |
| `test_transactions.csv` | Seeded split script output, unlabelled | `id`, `description` |
| `dev_labels.csv` | Hand-written by the author | `id`, `category` |
| `test_labels.csv` | Hand-written by the author | `id`, `category` |

- Only the two `*_labels.csv` files are hand-written. They are ground truth and must never be edited by the AI.
- The generated data carries no labels, so labelling is blind.
- The split is seeded and done before labelling.
- The test set is run once, at the end.
