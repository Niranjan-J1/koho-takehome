import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from split import run, split  # noqa: E402

SIZES = {"A": 30, "B": 12, "C": 6}  # synthetic fixture, not the real data


def fixture():
    rows, cats = [], {}
    for c, n in SIZES.items():
        for _ in range(n):
            tid = f"t{len(rows) + 1:03d}"
            rows.append((tid, f"desc {tid}"))
            cats[tid] = c
    return rows, cats


def ids(out, k):
    return {i for i, _ in out[k]}


def test_disjoint_complete_and_sized():
    rows, cats = fixture()
    out, _, _ = split(rows, cats, dev_n=8, test_n=16, forced={"t001"})
    dev, test, res = ids(out, "dev"), ids(out, "test"), ids(out, "reserve")
    assert not (dev & test or dev & res or test & res)
    assert dev | test | res == {i for i, _ in rows}
    assert (len(dev), len(test)) == (8, 16)
    assert "t001" in res


def test_same_seed_same_split_and_seed_matters():
    rows, cats = fixture()
    assert split(rows, cats, seed=1, dev_n=8, test_n=16)[0] == split(rows, cats, seed=1, dev_n=8, test_n=16)[0]
    assert split(rows, cats, seed=1, dev_n=8, test_n=16)[0] != split(rows, cats, seed=2, dev_n=8, test_n=16)[0]


def test_every_class_in_dev():
    rows, cats = fixture()
    out, _, _ = split(rows, cats, dev_n=8, test_n=16)
    assert {cats[i] for i in ids(out, "dev")} == set(SIZES)


def test_refuses_to_overwrite(tmp_path):
    rows, cats = fixture()
    with open(tmp_path / "transactions.csv", "w", newline="") as f:
        csv.writer(f).writerows([("id", "description"), *rows])
    with open(tmp_path / "generation_meta.csv", "w", newline="") as f:
        csv.writer(f).writerows([("id", "intended_category", "messiness_tags", "is_ambiguous"),
                                 *[(i, cats[i], "clean", "no") for i, _ in rows]])
    run(tmp_path)
    with pytest.raises(SystemExit):
        run(tmp_path)
    run(tmp_path, force=True)
