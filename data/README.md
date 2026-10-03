# Data

| File | Origin | Columns |
|------|--------|---------|
| `transactions.csv` | Authored directly by Claude Code (no LLM call), no labels. Rows shuffled with seed 42 before ids `t001`..`t300` were assigned | `id`, `description` |
| `generation_meta.csv` | Sealed. Generator intent for coverage checks and later analysis. Never ground truth. Do not open while labelling | `id`, `intended_category`, `messiness_tags`, `is_ambiguous` |
| `dev_transactions.csv` | Seeded split script output, unlabelled | `id`, `description` |
| `test_transactions.csv` | Seeded split script output, unlabelled | `id`, `description` |
| `reserve_transactions.csv` | Seeded split script output, unlabelled. Not labelled or evaluated. Includes 11 forced ids whose intended category was exposed | `id`, `description` |
| `dev_labels.csv` | Template from the split, labels hand-written by the author (see `LABELLING.md`) | `id`, `description`, `label`, `note` |
| `test_labels.csv` | Template from the split, labels hand-written by the author (see `LABELLING.md`) | `id`, `description`, `label`, `note` |

- Only the two `*_labels.csv` files are hand-written. They are ground truth and must never be edited by the AI.
- The generated data carries no labels, so labelling is blind.
- The split is seeded and done before labelling.
- The test set is run once, at the end.
