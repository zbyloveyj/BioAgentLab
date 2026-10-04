from __future__ import annotations

from bioagent.agents.pipeline import generate, meta_review, rank, reflect
from bioagent.core.models import Hypothesis


class ScientificSupervisor:
    """Minimal auditable supervisor used by the offline teaching example."""

    def run(self, question: str) -> tuple[list[Hypothesis], dict[str, object]]:
        candidates = [reflect(item) for item in generate(question)]
        ranked = rank(candidates)
        return ranked, meta_review(ranked)

