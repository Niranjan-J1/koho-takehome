"""Accuracy vs coverage from self-reported confidence: python src/confidence.py [--approach B] [--split dev|test].

Reads results/<approach>_<split>.csv only; makes no API calls. Descriptive, not a calibration guarantee.
"""
import argparse
import csv
import math
from pathlib import Path

RESULTS = Path(__file__).resolve().parent.parent / "results"
LEVELS = (1.0, 0.9, 0.8, 0.7, 0.6, 0.5)


def score(row):
    """Ranking key. Missing confidence, and rows whose prediction is invalid, rank lowest."""
    if row["valid"] != "True" or row["confidence"] == "":
        return -1.0
    return float(row["confidence"])


def coverage_table(rows, levels=LEVELS):
    """For each level, keep the highest-confidence share of rows; a tie group at the boundary is kept whole."""
    if not rows:
        raise ValueError("no rows")
    ranked = sorted(rows, key=score, reverse=True)
    n, table = len(ranked), []
    for level in levels:
        cut = score(ranked[math.ceil(level * n) - 1])
        kept = [r for r in ranked if score(r) >= cut]
        right = sum(r["correct"] == "True" for r in kept)
        table.append({"level": level, "kept": len(kept), "coverage": len(kept) / n,
                      "min_conf": cut, "accuracy": right / len(kept), "errors": len(kept) - right})
    distinct = len({score(r) for r in rows if score(r) >= 0})
    lowest = sum(score(r) < 0 for r in rows)
    return table, distinct, lowest


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--approach", default="B", choices=["A", "B"])
    ap.add_argument("--split", default="dev", choices=["dev", "test"])
    a = ap.parse_args(argv)
    with open(RESULTS / f"{a.approach}_{a.split}.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    table, distinct, lowest = coverage_table(rows)
    print(f"approach {a.approach} | split {a.split} | n={len(rows)} | distinct confidence values: {distinct}"
          f" | missing/invalid ranked lowest: {lowest}")
    print("target  kept  actual  min conf  accuracy  errors kept")
    for t in table:
        mc = "invalid" if t["min_conf"] < 0 else f"{t['min_conf']:g}"
        print(f"{t['level']:>5.0%}  {t['kept']:>5}  {t['coverage']:>6.0%}  {mc:>8}  {t['accuracy']:>8.1%}  {t['errors']:>6}")


if __name__ == "__main__":
    main()
