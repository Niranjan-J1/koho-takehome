"""Run one approach on a split: python src/eval.py --approach A|B [--split dev] [--split test --confirm-test]."""
import argparse
import csv
import os
import sys
from collections import Counter
from pathlib import Path

from llm import LLMError, classify
from parse import parse
from prompts import build_prompt
from stats import wilson
from taxonomy import category_names

ROOT = Path(__file__).resolve().parent.parent
APPROACHES = {"A": "names", "B": "full"}
FIELDS = ["id", "description", "label", "prediction", "valid", "normalised", "confidence", "correct"]


def run(approach, split, model, data_dir=ROOT / "data", out_dir=ROOT / "results", call=classify):
    names = category_names()
    with open(Path(data_dir) / f"{split}_labels.csv", encoding="utf-8") as f:
        labels = list(csv.DictReader(f))
    bad = {r["label"] for r in labels} - set(names)
    if bad:
        raise ValueError(f"labels not in taxonomy: {sorted(bad)}")
    rows, stats = [], {}
    for r in labels:
        raw = call(build_prompt(r["description"], APPROACHES[approach]), model, stats=stats)
        pred, conf, norm = parse(raw, names)
        rows.append({"id": r["id"], "description": r["description"], "label": r["label"],
                     "prediction": pred or "INVALID", "valid": pred is not None, "normalised": norm,
                     "confidence": "" if conf is None else conf, "correct": pred == r["label"]})
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    with open(Path(out_dir) / f"{approach}_{split}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return rows, stats


def report(rows, stats, names):
    n, k = len(rows), sum(r["correct"] for r in rows)
    lo, hi = wilson(k, n)
    print(f"accuracy {k}/{n} = {k / n:.1%}  (95% Wilson CI {lo:.1%} to {hi:.1%})")
    print(f"invalid outputs (scored wrong): {sum(not r['valid'] for r in rows)}  | normalised: {sum(r['normalised'] for r in rows)}")
    print(f"API calls: {stats.get('calls', 0)}  | cache hits: {stats.get('hits', 0)}")
    print("\nper class (descriptive only; small n):")
    for c in names:
        sub = [r for r in rows if r["label"] == c]
        if sub:
            print(f"  {c:22} {sum(r['correct'] for r in sub)}/{len(sub)}")
    errs = Counter((r["label"], r["prediction"]) for r in rows if not r["correct"])
    print("\nconfusions (label -> prediction):")
    for (lab, pred), cnt in errs.most_common(10):
        print(f"  {cnt}  {lab} -> {pred}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--approach", required=True, choices=sorted(APPROACHES))
    ap.add_argument("--split", default="dev", choices=["dev", "test"])
    ap.add_argument("--confirm-test", action="store_true", help="required to run the test set (run once, at the end)")
    a = ap.parse_args(argv)
    if a.split == "test" and not a.confirm_test:
        sys.exit("Refusing to run the test set without --confirm-test.")
    from dotenv import load_dotenv
    load_dotenv()
    model = os.environ.get("GEMINI_MODEL")
    if not model:
        sys.exit("GEMINI_MODEL is not set (expected in .env).")
    print(f"approach {a.approach} ({APPROACHES[a.approach]}) | split {a.split} | model {model}")
    try:
        rows, stats = run(a.approach, a.split, model)
    except LLMError as e:
        sys.exit(f"Aborted: {e}. Rerun to resume; completed calls are cached.")
    report(rows, stats, category_names())


if __name__ == "__main__":
    main()
