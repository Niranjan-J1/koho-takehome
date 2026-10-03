"""Small statistics helpers, standard library only."""
import math
import random

Z95 = 1.959963984540054


def wilson(k, n, z=Z95):
    """Wilson score interval for k successes in n trials. Assumes independent items."""
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
    """
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def bootstrap_diff(a_correct, b_correct, iters=10000, seed=2026):
    """Paired percentile bootstrap of accuracy(B) - accuracy(A). Returns (diff, lo, hi) for a 95% interval."""
    n = len(a_correct)
    if n == 0 or n != len(b_correct):
        raise ValueError("need two equal-length, non-empty paired vectors")
    d = [int(y) - int(x) for x, y in zip(a_correct, b_correct)]
    rng = random.Random(seed)
    samples = sorted(sum(d[rng.randrange(n)] for _ in range(n)) / n for _ in range(iters))
    return sum(d) / n, samples[int(0.025 * iters)], samples[int(0.975 * iters) - 1]
