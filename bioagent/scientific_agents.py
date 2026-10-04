"""Scientific reasoning agents used by the v0.1 framework."""

import re
from collections import Counter
from statistics import mean

from .core import Hypothesis, LLMClient


class GenerationAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def generate(self, question: str, n: int = 3) -> list[Hypothesis]:
        hypotheses: list[Hypothesis] = []
        for i in range(1, n + 1):
            prompt = (
                "Generate one falsifiable biological hypothesis. "
                "State a plausible mechanism and avoid merely restating the question.\n\n"
                f"Research question: {question}\nCandidate #{i}:"
            )
            statement = self.llm.complete(prompt).strip()
            hypotheses.append(
                Hypothesis(
                    identifier=f"H{i}",
                    statement=statement,
                    metadata={
                        "novelty": 0.5,
                        "feasibility": 0.5,
                        "falsifiability": 0.5,
                    },
                )
            )
        return hypotheses


class ReflectionAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def critique(self, hypothesis: Hypothesis) -> Hypothesis:
        prompt = (
            "Act as a skeptical scientific reviewer. Identify the single most important "
            "weakness, focusing on confounding, causal direction, missing evidence, "
            "alternative mechanisms or falsifiability.\n\n"
            f"Hypothesis: {hypothesis.statement}\nCritique:"
        )
        critique = self.llm.complete(prompt).strip()
        if critique:
            hypothesis.critiques.append(critique)
        return hypothesis


class RankingAgent:
    def score(self, hypothesis: Hypothesis) -> float:
        evidence_score = (
            mean(item.confidence for item in hypothesis.evidence)
            if hypothesis.evidence
            else 0.25
        )
        novelty = float(hypothesis.metadata.get("novelty", 0.5))
        feasibility = float(hypothesis.metadata.get("feasibility", 0.5))
        falsifiability = float(hypothesis.metadata.get("falsifiability", 0.5))
        critique_penalty = min(0.25, 0.05 * len(hypothesis.critiques))
        score = (
            0.35 * evidence_score
            + 0.20 * novelty
            + 0.20 * feasibility
            + 0.25 * falsifiability
            - critique_penalty
        )
        hypothesis.score = max(0.0, min(1.0, score))
        return hypothesis.score

    def rank(self, hypotheses: list[Hypothesis]) -> list[Hypothesis]:
        for hypothesis in hypotheses:
            self.score(hypothesis)
        return sorted(hypotheses, key=lambda item: item.score, reverse=True)


class EvolutionAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def evolve(self, hypothesis: Hypothesis) -> Hypothesis:
        critiques = "\n".join(f"- {item}" for item in hypothesis.critiques) or "- None"
        prompt = (
            "Improve the hypothesis while preserving falsifiability. "
            "Address the critiques and make the mechanism more testable.\n\n"
            f"Original hypothesis: {hypothesis.statement}\n"
            f"Critiques:\n{critiques}\nRevised hypothesis:"
        )
        revised = self.llm.complete(prompt).strip()
        if revised:
            hypothesis.metadata["parent_statement"] = hypothesis.statement
            hypothesis.statement = revised
        return hypothesis


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9_]+", text.lower()))


class ProximityAgent:
    @staticmethod
    def similarity(a: Hypothesis, b: Hypothesis) -> float:
        left, right = _tokens(a.statement), _tokens(b.statement)
        if not left and not right:
            return 1.0
        if not left or not right:
            return 0.0
        return len(left & right) / len(left | right)

    def deduplicate(
        self, hypotheses: list[Hypothesis], threshold: float = 0.80
    ) -> list[Hypothesis]:
        kept: list[Hypothesis] = []
        for candidate in hypotheses:
            if all(self.similarity(candidate, old) < threshold for old in kept):
                kept.append(candidate)
        return kept


class MetaReviewAgent:
    def summarize(self, hypotheses: list[Hypothesis]) -> dict[str, object]:
        critiques = [c.strip() for h in hypotheses for c in h.critiques if c.strip()]
        counts = Counter(c.lower() for c in critiques)
        return {
            "n_hypotheses": len(hypotheses),
            "n_critiques": len(critiques),
            "repeated_critiques": counts.most_common(5),
        }
