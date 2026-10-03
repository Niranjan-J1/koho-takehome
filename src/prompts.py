"""Build classification prompts. Approach A = `names`, Approach B = `full`; only the category block differs."""
from taxonomy import load_categories

DETAILS = ("names", "full")

TEMPLATE = """You classify Canadian bank transaction descriptions into exactly one category.

Categories:
{categories}

Transaction description (between the markers):
<<<
{description}
>>>

Respond with JSON only, in this form:
{{"category": "<one category name, exactly as listed>", "confidence": <integer 0-100, how likely your category is correct>}}"""


def category_block(detail, categories=None):
    """One line per category. `names` lines are a strict prefix of the matching `full` lines."""
    if detail not in DETAILS:
        raise ValueError(f"detail must be one of {DETAILS}, got {detail!r}")
    lines = []
    for c in categories or load_categories():
        line = f"- {c['name']}"
        if detail == "full":
            line += f": {c['definition']}"
            if c["tie_break"]:
                line += f" Tie-break: {c['tie_break']}"
        lines.append(line)
    return "\n".join(lines)


def build_prompt(description, detail, categories=None):
    return TEMPLATE.format(categories=category_block(detail, categories), description=description)
