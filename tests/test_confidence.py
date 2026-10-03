import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from confidence import coverage_table  # noqa: E402


def row(conf, correct, valid=True):
    return {"confidence": "" if conf is None else str(conf), "correct": str(correct), "valid": str(valid)}


# 10 rows: confidences 95 x4 (tie), 90, 85, 80, 70, missing, invalid prediction.
ROWS = [row(95, True), row(95, True), row(95, True), row(95, False), row(90, True),
        row(85, True), row(80, False), row(70, True), row(None, False), row(99, False, valid=False)]


def by_level(table):
    return {t["level"]: t for t in table}


def test_full_coverage_is_plain_accuracy():
    t = by_level(coverage_table(ROWS)[0])
    assert t[1.0]["kept"] == 10 and t[1.0]["accuracy"] == pytest.approx(0.6)


def test_tie_group_at_boundary_kept_whole():
    t = by_level(coverage_table(ROWS, levels=(0.3,))[0])
    assert t[0.3]["kept"] == 4 and t[0.3]["min_conf"] == 95 and t[0.3]["accuracy"] == 0.75


def test_missing_and_invalid_rank_lowest():
    t = by_level(coverage_table(ROWS)[0])
    assert t[0.8]["kept"] == 8 and t[0.8]["min_conf"] == 70
    assert t[0.9]["min_conf"] == -1.0 and t[0.9]["kept"] == 10  # both lowest rows tie at the sentinel


def test_distinct_and_lowest_counts():
    _, distinct, lowest = coverage_table(ROWS)
    assert (distinct, lowest) == (5, 2)


def test_empty_rejected():
    with pytest.raises(ValueError):
        coverage_table([])
