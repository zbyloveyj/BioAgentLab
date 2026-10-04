"""Validated teaching primitives, not a substitute for domain pipelines."""
from __future__ import annotations
from collections import defaultdict
import math


def _number(x) -> float:
    if isinstance(x, bool):
        raise ValueError("Boolean is not a measurement")
    try:
        value = float(x)
    except (ValueError, TypeError) as exc:
        raise ValueError("Expected a number") from exc
    if not math.isfinite(value):
        raise ValueError("Non-finite measurement")
    return value


def clr(values, pseudocount=None) -> list[float]:
    x = [_number(v) for v in values]
    if not x or any(v < 0 for v in x) or not any(v > 0 for v in x):
        raise ValueError("Expected nonnegative, nonzero sample")
    if pseudocount is not None:
        p = _number(pseudocount)
        if p <= 0:
            raise ValueError("Pseudocount must be positive")
        x = [v + p for v in x]
    if any(v <= 0 or not math.isfinite(v) for v in x):
        raise ValueError("Explicit valid zero handling required")
    logs = [math.log(v) for v in x]
    center = math.fsum(logs) / len(logs)
    return [v - center for v in logs]


def bh_adjust(values) -> list[float]:
    p = [_number(x) for x in values]
    if any(not 0 <= x <= 1 for x in p):
        raise ValueError("p-values must lie in [0,1]")
    order = sorted(range(len(p)), key=p.__getitem__)
    q = [0.0] * len(p)
    running = 1.0
    for rank in range(len(p), 0, -1):
        i = order[rank - 1]
        running = min(running, p[i] * len(p) / rank)
        q[i] = running
    return q


def audit_sample_ids(rows, field="sample_id") -> dict:
    ids = []
    for row in rows:
        value = row.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Missing {field}")
        ids.append(value)
    if not ids:
        raise ValueError("Empty sample table")
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate sample IDs")
    return {"n_samples": len(ids), "sample_ids": sorted(ids), "ok": True}


def align_by_id(left, right) -> dict:
    audit_sample_ids(left)
    audit_sample_ids(right)
    a = {r["sample_id"]: r for r in left}
    b = {r["sample_id"]: r for r in right}
    common = sorted(a.keys() & b.keys())
    return {"pairs": [(a[k], b[k]) for k in common],
            "left_only": sorted(a.keys() - b.keys()),
            "right_only": sorted(b.keys() - a.keys())}


def pseudobulk(cells) -> dict[tuple[str, str], list[int]]:
    totals = {}
    seen = set()
    width = None
    for cell in cells:
        for key in ("cell_id", "donor_id", "cell_type"):
            if not isinstance(cell.get(key), str) or not cell[key].strip():
                raise ValueError(f"Missing {key}")
        if cell["cell_id"] in seen:
            raise ValueError("Duplicate cell ID")
        seen.add(cell["cell_id"])
        counts = cell.get("counts")
        if not isinstance(counts, (list, tuple)) or not counts:
            raise ValueError("Missing counts")
        if width is None:
            width = len(counts)
        if len(counts) != width:
            raise ValueError("Inconsistent gene dimension")
        if any(type(v) is not int or v < 0 for v in counts):
            raise ValueError("Expected nonnegative integer raw counts")
        group = (cell["donor_id"], cell["cell_type"])
        old = totals.setdefault(group, [0] * width)
        totals[group] = [x + y for x, y in zip(old, counts)]
    if not seen:
        raise ValueError("Empty cell table")
    return totals
