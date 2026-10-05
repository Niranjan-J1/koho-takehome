"""Approach A and B prompts are identical except the category block, and A's block is a strict prefix of B's."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from prompts import build_prompt, category_block  # noqa: E402
from taxonomy import load_categories  # noqa: E402

DESC = "SQ *THE PINE CAFE"


def test_all_names_in_both_approaches():
    for detail in ("names", "full"):
        p = build_prompt(DESC, detail)
        assert all(c["name"] in p for c in load_categories())


def test_names_block_is_strict_prefix_of_full_block():
    a, b = category_block("names").splitlines(), category_block("full").splitlines()
    assert len(a) == len(b) == len(load_categories())
    assert all(lb.startswith(la) and len(lb) > len(la) for la, lb in zip(a, b))


def test_prompts_identical_outside_category_block():
    a, b = build_prompt(DESC, "names"), build_prompt(DESC, "full")
    assert a.replace(category_block("names"), "<BLOCK>") == b.replace(category_block("full"), "<BLOCK>")


def test_definitions_only_in_full():
    a, b = build_prompt(DESC, "names"), build_prompt(DESC, "full")
    for c in load_categories():
        assert c["definition"] in b and c["definition"] not in a


def test_description_between_markers_and_json_instruction():
    p = build_prompt(DESC, "names")
    assert f"<<<\n{DESC}\n>>>" in p
    assert '{"category":' in p


def test_unknown_detail_rejected():
    with pytest.raises(ValueError):
        build_prompt(DESC, "medium")
