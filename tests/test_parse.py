import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from parse import parse  # noqa: E402


def test_exact_match():
    assert parse('{"category": "Dining", "confidence": 90}') == ("Dining", 90.0, False)


def test_case_and_whitespace_normalised_and_flagged():
    assert parse('{"category": "  bills & utilities ", "confidence": 70}') == ("Bills & Utilities", 70.0, True)


@pytest.mark.parametrize("raw", [
    '{"category": "Food", "confidence": 90}',          # not one of the 12 names
    '{"category": "Dining Out", "confidence": 90}',    # no fuzzy matching
    '{"confidence": 90}',                              # missing category
    '{"category": 3, "confidence": 90}',               # wrong type
    '["Dining"]',                                      # not an object
    'Dining',                                          # not JSON
    '```json\n{"category": "Dining"}\n```',            # code fence is not stripped
    '',                                                # empty response
])
def test_invalid_category(raw):
    assert parse(raw)[0] is None


@pytest.mark.parametrize("conf", ["101", "-1", '"80"', "true", "null"])
def test_bad_confidence_is_none_but_category_kept(conf):
    assert parse(f'{{"category": "Travel", "confidence": {conf}}}') == ("Travel", None, False)


def test_missing_confidence():
    assert parse('{"category": "Other"}') == ("Other", None, False)


def test_none_input_is_invalid():
    assert parse(None) == (None, None, False)
