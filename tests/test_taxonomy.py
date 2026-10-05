"""Taxonomy loading: the real file's shape, and rejection of missing definitions or duplicate names."""
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from taxonomy import TAXONOMY, category_names, load_categories  # noqa: E402

# Count read straight from the YAML, independent of the loader, so adding a category doesn't break the suite.
EXPECTED = len(yaml.safe_load(TAXONOMY.read_text(encoding="utf-8"))["categories"])


def test_real_taxonomy_shape():
    cats = load_categories()
    assert len(cats) == EXPECTED
    assert len({c["name"] for c in cats}) == EXPECTED
    assert cats[-1]["name"] == "Other"
    assert all(c["definition"] for c in cats)


def test_names_in_file_order():
    assert category_names() == [c["name"] for c in load_categories()]


def test_missing_definition_rejected(tmp_path):
    p = tmp_path / "t.yaml"
    p.write_text("categories:\n  - name: X\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_categories(p)


def test_duplicate_names_rejected(tmp_path):
    p = tmp_path / "t.yaml"
    p.write_text("categories:\n  - {name: X, definition: a}\n  - {name: X, definition: b}\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_categories(p)
