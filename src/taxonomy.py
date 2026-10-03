"""Load the category taxonomy from taxonomy.yaml. Both prompt approaches are built from this."""
from pathlib import Path

import yaml

TAXONOMY = Path(__file__).resolve().parent.parent / "taxonomy.yaml"


def load_categories(path=TAXONOMY):
    """Return [{name, definition, tie_break}] in file order; tie_break is None when absent."""
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)["categories"]
    cats = []
    for c in raw:
        if not c.get("name") or not c.get("definition"):
            raise ValueError(f"category missing name or definition: {c}")
        cats.append({"name": c["name"], "definition": c["definition"], "tie_break": c.get("tie_break")})
    names = [c["name"] for c in cats]
    if len(set(names)) != len(names):
        raise ValueError(f"duplicate category names in {path}")
    return cats


def category_names(path=TAXONOMY):
    return [c["name"] for c in load_categories(path)]
