# KOHO take-home: transaction classification + evaluation harness

## What this project is
Classify messy bank transaction descriptions into merchant categories using
an LLM, and build an evaluation harness that shows honestly whether it works.
The evaluation is more important than the classifier. Time limit: 4 hours.

## Hard rules (evaluation integrity)
- NEVER create, edit or "fix" labels in data/dev_labels.csv or
  data/test_labels.csv. Labels are hand-written by me and are ground truth.
- NEVER use model-generated labels as ground truth.
- NEVER read or evaluate against the test set while iterating. Dev set only.
  The test set is run once, at the end, when I say so.
- Few-shot examples must not come from dev or test.
- Invalid model outputs count as errors. Do not silently drop them.

## How to work with me
- Plan first. For anything beyond a small edit, propose a plan and wait
  for my approval before writing code.
- Keep changes small (roughly under 50 lines) so I can read every line.
- Do not claim a library function, parameter or metric behaviour exists
  unless you are sure. Flag uncertainty instead of guessing.
- State assumptions explicitly. If a metric or test could mislead,
  say so.
- Explain stats choices briefly: why this test, what it assumes.

## Conventions
- Python. Taxonomy lives in taxonomy.yaml; prompts are built from it.
- Evaluation runs with one command: python src/eval.py --approach <name>
- Cache LLM responses; temperature 0.
- Run tests with: pytest

## Logging
Append notable decisions and any AI mistakes you catch to DECISIONS.md
when I ask.
