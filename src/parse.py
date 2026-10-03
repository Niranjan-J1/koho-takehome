"""Parse a raw model response. A category that is not one of the 12 names (after case/whitespace folding) is invalid."""
import json

from taxonomy import category_names


def _confidence(value):
    """Integer or float in [0, 100], else None. Booleans and numeric strings are rejected."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value) if 0 <= value <= 100 else None


def parse(raw, names=None):
    """Return (category | None, confidence | None, normalised). None category means invalid, scored wrong.

    `normalised` is True when the category only matched after folding case or stripping whitespace.
    Strict on purpose: no code-fence stripping, no fuzzy matching.
    """
    lookup = {n.lower(): n for n in (names or category_names())}
    try:
        obj = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None, None, False
    if not isinstance(obj, dict):
        return None, None, False
    conf = _confidence(obj.get("confidence"))
    cat = obj.get("category")
    if not isinstance(cat, str):
        return None, conf, False
    canon = lookup.get(cat.strip().lower())
    return canon, conf, canon is not None and canon != cat
