"""Small statistics helpers, standard library only. Used by eval.py (Wilson) and compare.py (McNemar, bootstrap)."""
import math
import random

Z95 = 1.959963984540054


def wilson(k, n, z=Z95):
    """Wilson score interval for k successes in n trials. Assumes independent items.

    Used instead of the normal (Wald) approximation, which gives a zero-width interval at 100%
    accuracy and can spill outside [0, 1] at n=50 or 100, exactly where our accuracies sit.
    """
    if n == 0:
        raise ValueError("n must be positive")
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, centre - half), min(1.0, centre + half)


def mcnemar_exact(b, c):
    """Two-sided exact McNemar p-value: binomial(b + c, 0.5) on the discordant pairs only.

    b = rows only A got right, c = rows only B got right. Assumes paired, independent items.
    Rows both got right (or both got wrong) say nothing about which approach is better, so only
    discordant rows enter. Exact rather than chi-square because the chi-square approximation is
    unreliable with this few discordant rows (4 on dev, 7 on test).
    """
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def bootstrap_diff(a_correct, b_correct, iters=10000, seed=2026):
    """Paired percentile bootstrap of accuracy(B) - accuracy(A). Returns (diff, lo, hi) for a 95% interval.

    Unreliable when the discordant rows all favour one side: no resample can then go below zero, so
    a lower bound above zero is an artefact, not evidence. Report it next to McNemar, never instead.
    """
    n = len(a_correct)
    if n == 0 or n != len(b_correct):
        raise ValueError("need two equal-length, non-empty paired vectors")
    d = [int(y) - int(x) for x, y in zip(a_correct, b_correct)]
    rng = random.Random(seed)
    samples = sorted(sum(d[rng.randrange(n)] for _ in range(n)) / n for _ in range(iters))
    return sum(d) / n, samples[int(0.025 * iters)], samples[int(0.975 * iters) - 1]
