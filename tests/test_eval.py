import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import eval as ev  # noqa: E402
from stats import wilson  # noqa: E402

LABELS = [("x1", "AAA", "Dining"), ("x2", "BBB", "Travel"), ("x3", "CCC", "Other")]
REPLIES = {"AAA": '{"category": "Dining", "confidence": 90}',   # correct
           "BBB": '{"category": "transport", "confidence": 60}',  # valid, normalised, wrong
           "CCC": "not json"}                                      # invalid -> wrong


def fake_call(prompt, model, stats=None):
    fake_call.prompts.append(prompt)
    return next(v for k, v in REPLIES.items() if f"<<<\n{k}\n>>>" in prompt)


@pytest.fixture
def data(tmp_path):
    with open(tmp_path / "dev_labels.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([("id", "description", "label"), *LABELS])
    fake_call.prompts = []
    return tmp_path


def test_scores_invalid_as_wrong_and_writes_results(data):
    rows, _ = ev.run("A", "dev", "m", data, data / "out", fake_call)
    assert [r["correct"] for r in rows] == [True, False, False]
    assert [r["prediction"] for r in rows] == ["Dining", "Transport", "INVALID"]
    assert [r["normalised"] for r in rows] == [False, True, False]
    with open(data / "out" / "A_dev.csv", encoding="utf-8") as f:
        assert len(list(csv.DictReader(f))) == 3


def test_approach_selects_detail_level(data):
    ev.run("A", "dev", "m", data, data / "out", fake_call)
    ev.run("B", "dev", "m", data, data / "out", fake_call)
    assert "Tie-break" not in fake_call.prompts[0] and "Tie-break" in fake_call.prompts[3]


def test_off_taxonomy_label_rejected(tmp_path):
    with open(tmp_path / "dev_labels.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([("id", "description", "label"), ("x1", "AAA", "Food")])
    with pytest.raises(ValueError):
        ev.run("A", "dev", "m", tmp_path, tmp_path / "out", fake_call)


def test_test_split_requires_confirm(monkeypatch):
    monkeypatch.setattr(ev, "run", lambda *a, **k: pytest.fail("run() must not be called"))
    with pytest.raises(SystemExit):
        ev.main(["--approach", "A", "--split", "test"])


def test_wilson_reference_values():
    assert wilson(5, 10) == pytest.approx((0.2366, 0.7634), abs=1e-4)
    assert wilson(0, 10) == pytest.approx((0.0, 0.2775), abs=1e-4)
    assert wilson(10, 10) == pytest.approx((0.7225, 1.0), abs=1e-4)
