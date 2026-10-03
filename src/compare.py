"""Paired A vs B comparison on one split: python src/compare.py [--split dev|test]. Reads results/A_<split>.csv and B_<split>.csv."""
import argparse
import csv
from pathlib import Path

from stats import bootstrap_diff, mcnemar_exact

RESULTS = Path(__file__).resolve().parent.parent / "results"


def load(path):
    with open(path, encoding="utf-8") as f:
        return [(r["id"], r["label"], r["correct"] == "True") for r in csv.DictReader(f)]


def compare(a_rows, b_rows):
    if [(i, l) for i, l, _ in a_rows] != [(i, l) for i, l, _ in b_rows]:
        raise ValueError("A and B results must cover the same ids and labels in the same order")
    a, b = [x for _, _, x in a_rows], [x for _, _, x in b_rows]
    only_a = sum(x and not y for x, y in zip(a, b))
    only_b = sum(y and not x for x, y in zip(a, b))
    diff, lo, hi = bootstrap_diff(a, b)
    return {"n": len(a), "acc_a": sum(a) / len(a), "acc_b": sum(b) / len(b),
            "both_right": sum(x and y for x, y in zip(a, b)), "only_a": only_a, "only_b": only_b,
            "both_wrong": sum(not x and not y for x, y in zip(a, b)),
            "diff": diff, "ci": (lo, hi), "p": mcnemar_exact(only_a, only_b)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--split", default="dev", choices=["dev", "test"])
    split = ap.parse_args(argv).split
    r = compare(load(RESULTS / f"A_{split}.csv"), load(RESULTS / f"B_{split}.csv"))
    print(f"split {split}, n={r['n']}: accuracy A {r['acc_a']:.1%}, B {r['acc_b']:.1%}")
    print(f"both right {r['both_right']} | only A {r['only_a']} | only B {r['only_b']} | both wrong {r['both_wrong']}")
    print(f"B - A = {r['diff']:+.1%}  (95% paired bootstrap CI {r['ci'][0]:+.1%} to {r['ci'][1]:+.1%})")
    print(f"exact McNemar, two-sided: p = {r['p']:.4f}  (uses only the {r['only_a'] + r['only_b']} discordant rows)")


if __name__ == "__main__":
    main()
