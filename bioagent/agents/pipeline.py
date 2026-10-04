from __future__ import annotations

from collections.abc import Iterable

from bioagent.core.models import Hypothesis


def generate(question: str) -> list[Hypothesis]:
    """Create contrasting, falsifiable hypothesis families without an LLM."""
    return [
        Hypothesis(
            title="Ecological opportunity model",
            rationale=f"For {question}, altered contact opportunity explains the signal.",
            predictions=["Adjustment for co-occurrence strongly attenuates the effect."],
            falsifiers=["The effect remains after abundance and contact adjustment."],
        ),
        Hypothesis(
            title="Excess genetic exchange model",
            rationale=f"For {question}, exchange exceeds ecological opportunity.",
            predictions=["Observed exchange is greater than a preregistered expected model."],
            falsifiers=["Negative controls show the same excess."],
        ),
        Hypothesis(
            title="Technical artifact model",
            rationale=f"For {question}, assembly or depth differences create an apparent signal.",
            predictions=["The signal tracks sequencing or assembly quality."],
            falsifiers=["Breakpoint validation replicates across balanced-depth subsets."],
        ),
    ]


def reflect(hypothesis: Hypothesis) -> Hypothesis:
    penalties = 0.0
    if not hypothesis.predictions:
        penalties += 1.0
        hypothesis.audit.append("missing predictions")
    if not hypothesis.falsifiers:
        penalties += 1.0
        hypothesis.audit.append("missing falsifiers")
    hypothesis.score = hypothesis.evidence_balance() - penalties
    hypothesis.audit.append("reflection complete")
    return hypothesis


def rank(items: Iterable[Hypothesis]) -> list[Hypothesis]:
    return sorted(items, key=lambda item: item.score, reverse=True)


def evolve(parent: Hypothesis, critique: str) -> Hypothesis:
    child = Hypothesis(
        title=f"{parent.title} - revised",
        rationale=f"{parent.rationale} Revision: {critique}",
        predictions=list(parent.predictions),
        falsifiers=list(parent.falsifiers),
        evidence=list(parent.evidence),
        audit=list(parent.audit) + ["evolved from critique"],
    )
    return reflect(child)


def meta_review(items: Iterable[Hypothesis]) -> dict[str, object]:
    ranked = rank(items)
    return {
        "winner": ranked[0].title if ranked else None,
        "requires_human_review": True,
        "risks": sorted({note for item in ranked for note in item.audit}),
    }

