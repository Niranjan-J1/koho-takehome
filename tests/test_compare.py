import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from compare import compare  # noqa: E402
from stats import bootstrap_diff, mcnemar_exact  # noqa: E402


@pytest.mark.parametrize("b,c,p", [
    (0, 0, 1.0),
    (1, 9, 2 * (1 + 10) / 1024),   # 0.0215
    (9, 1, 2 * (1 + 10) / 1024),   # symmetric
    (0, 6, 2 / 64),                # 0.03125
    (5, 5, 1.0),                   # capped at 1
])
def test_mcnemar_hand_computed(b, c, p):
    assert mcnemar_exact(b, c) == pytest.approx(p)


def test_bootstrap_identical_vectors_zero():
    assert bootstrap_diff([1, 0, 1, 1], [1, 0, 1, 1], iters=200) == (0.0, 0.0, 0.0)


def test_bootstrap_seeded_and_bracketing():
    a, b = [1, 0, 1, 0, 1, 1, 0, 1], [1, 1, 1, 0, 1, 1, 1, 1]
    r = bootstrap_diff(a, b, iters=2000)
    assert r == bootstrap_diff(a, b, iters=2000)
    assert r[0] == 0.25 and r[1] <= r[0] <= r[2]


def test_compare_counts():
    a = [("x1", "Dining", True), ("x2", "Travel", False), ("x3", "Other", True), ("x4", "Other", False)]
    b = [("x1", "Dining", True), ("x2", "Travel", True), ("x3", "Other", False), ("x4", "Other", False)]
    r = compare(a, b)
    assert (r["both_right"], r["only_a"], r["only_b"], r["both_wrong"]) == (1, 1, 1, 1)
    assert r["p"] == 1.0 and r["diff"] == 0.0


def test_compare_rejects_mismatched_rows():
    with pytest.raises(ValueError):
        compare([("x1", "Dining", True)], [("x2", "Dining", True)])
