"""Seeded, stratified dev/test/reserve split of data/transactions.csv. Run once, before labelling.

Stratified because 12 classes over 50 dev rows could otherwise leave a rare class empty. The strata
come from the sealed generator file and decide membership only; they are never used as labels.
"""
import argparse
import csv
import random
import sys
from collections import defaultdict
from pathlib import Path

SEED = 2026  # fixed before any split was seen and never re-rolled; re-rolling for a "nicer" split is tuning
DEV_N, TEST_N = 50, 100
# Intended categories for these ids were exposed in chat; keep them out of dev and test (see DECISIONS.md).
# t001-t003: sealed-file rows printed. Others: Costco and Walmart intent stated in chat.
FORCED_RESERVE = {"t001", "t002", "t003",
                  "t005", "t087", "t126", "t157",  # Costco
                  "t056", "t096", "t159", "t298"}  # Walmart
DATA = Path(__file__).resolve().parent.parent / "data"
SPLITS = ("dev", "test", "reserve")


def allocate(sizes, n):
    """Largest-remainder proportional allocation of n rows across classes."""
    total = sum(sizes.values())
    quotas = {c: s * n / total for c, s in sizes.items()}
    alloc = {c: int(q) for c, q in quotas.items()}
    for c in sorted(quotas, key=lambda c: (alloc[c] - quotas[c], c))[: n - sum(alloc.values())]:
        alloc[c] += 1
    return alloc


def split(rows, categories, seed=SEED, dev_n=DEV_N, test_n=TEST_N, forced=FORCED_RESERVE):
    """rows: [(id, description)]; categories: {id: stratum}. Returns ({split: rows}, dev_alloc, test_alloc)."""
    by_cat = defaultdict(list)
    for r in rows:
        if r[0] not in forced:
            by_cat[categories[r[0]]].append(r)
    sizes = {c: len(v) for c, v in sorted(by_cat.items())}
    dev_a, test_a = allocate(sizes, dev_n), allocate(sizes, test_n)
    rng = random.Random(seed)
    out = {k: [] for k in SPLITS}
    for c in sorted(by_cat):
        items = by_cat[c][:]
        rng.shuffle(items)
        out["dev"] += items[: dev_a[c]]
        out["test"] += items[dev_a[c] : dev_a[c] + test_a[c]]
        out["reserve"] += items[dev_a[c] + test_a[c] :]
    out["reserve"] += [r for r in rows if r[0] in forced]
    return {k: sorted(v) for k, v in out.items()}, dev_a, test_a


def run(data_dir=DATA, force=False):
    paths = {k: data_dir / f"{k}_transactions.csv" for k in SPLITS}
    # Once labelling starts, an accidental re-split would silently invalidate the hand labels.
    if not force and any(p.exists() for p in paths.values()):
        sys.exit("Split files already exist; refusing to overwrite (pass --force).")
    with open(data_dir / "transactions.csv", encoding="utf-8") as f:
        rows = [(r["id"], r["description"]) for r in csv.DictReader(f)]
    with open(data_dir / "generation_meta.csv", encoding="utf-8") as f:
        meta = {r["id"]: r for r in csv.DictReader(f)}
    out, dev_a, test_a = split(rows, {i: m["intended_category"] for i, m in meta.items()})
    for k, p in paths.items():
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["id", "description"])
            w.writerows(out[k])
    for c in dev_a:
        print(f"{c:22} dev {dev_a[c]:>2}  test {test_a[c]:>3}")
    for k in SPLITS:
        amb = sum(meta[i]["is_ambiguous"] == "yes" for i, _ in out[k])
        print(f"{k}: {len(out[k])} rows, {amb} ambiguous")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Seeded, stratified dev/test/reserve split. Run once, before labelling.")
    ap.add_argument("--force", action="store_true", help="overwrite existing split files")
    run(force=ap.parse_args().force)
