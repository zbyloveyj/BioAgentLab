"""Pairwise preference ratings. Ratings are not probabilities of scientific truth."""
import math


def elo_pair(a: float, b: float, outcome: float, k: float = 24.0) -> tuple[float, float]:
    if isinstance(outcome, bool) or outcome not in (0, 0.5, 1):
        raise ValueError("Outcome must be 0, 0.5 or 1")
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)
           for v in (a, b, k)) or k <= 0:
        raise ValueError("Invalid rating parameters")
    exponent = max(-300.0, min(300.0, (b-a)/400.0))
    expected = 1 / (1 + 10 ** exponent)
    delta = k * (outcome - expected)
    return a + delta, b - delta


def tournament(identifiers, judge, initial=1000.0, k=24.0):
    ids = tuple(identifiers)
    if not ids or any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
        raise ValueError("Expected unique non-empty candidate IDs")
    if not math.isfinite(initial):
        raise ValueError("Invalid initial rating")
    ratings = dict.fromkeys(ids, float(initial))
    matches = []
    for i, left in enumerate(ids):
        for right in ids[i+1:]:
            outcome = judge(left, right)
            if outcome is None:
                matches.append({"left": left, "right": right, "status": "not_comparable"})
                continue
            ratings[left], ratings[right] = elo_pair(ratings[left], ratings[right], outcome, k)
            matches.append({"left": left, "right": right, "outcome": outcome})
    return {"ratings": ratings, "matches": matches,
            "interpretation": "relative_preference_not_truth_probability"}
