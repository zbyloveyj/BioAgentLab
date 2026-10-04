"""Introductory role examples. Scores are heuristic, not truth probabilities."""
from collections import Counter
from dataclasses import replace
from statistics import mean
from .core import Hypothesis, LLMClient
from .retrieval import jaccard


class GenerationAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def generate(self, question: str, n=3):
        if not question.strip() or type(n) is not int or not 1 <= n <= 20:
            raise ValueError("Invalid generation request")
        result = []
        for i in range(1, n+1):
            text = self.llm.complete(
                "Generate a falsifiable candidate, not a verified fact.\n"
                f"Question: {question}\nCandidate #{i}:").strip()
            if not text:
                raise ValueError("Empty hypothesis")
            result.append(Hypothesis(f"H{i}", text, metadata={"verified": False}))
        return result


class ReflectionAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def critique(self, hypothesis):
        text = self.llm.complete(
            "Act as a skeptical scientific reviewer. Identify a specific limitation.\n"
            f"Hypothesis: {hypothesis.statement}").strip()
        if text:
            hypothesis.critiques.append(text)
        return hypothesis


class RankingAgent:
    def score(self, hypothesis):
        support = [e.confidence for e in hypothesis.evidence if e.direction == "supports"]
        against = [e.confidence for e in hypothesis.evidence if e.direction == "contradicts"]
        hypothesis.score = (mean(support) if support else 0.0) - (mean(against) if against else 0.0)
        return hypothesis.score

    def rank(self, hypotheses):
        for h in hypotheses:
            self.score(h)
        return sorted(hypotheses, key=lambda h: (-h.score, h.identifier))


class EvolutionAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def evolve(self, hypothesis):
        text = self.llm.complete(
            "Improve the hypothesis and preserve testability.\n"
            f"Original: {hypothesis.statement}\nCritiques: {hypothesis.critiques}").strip()
        if not text:
            raise ValueError("Empty revision")
        metadata = {**hypothesis.metadata, "parent_statement": hypothesis.statement,
                    "version": hypothesis.metadata.get("version", 1)+1,
                    "verified": False}
        return replace(hypothesis, statement=text, evidence=[], critiques=[], score=0.0, metadata=metadata)


class ProximityAgent:
    @staticmethod
    def similarity(left, right):
        return jaccard(left.statement, right.statement)

    def deduplicate(self, hypotheses, threshold=0.8):
        if not 0 < threshold <= 1:
            raise ValueError("Invalid threshold")
        kept = []
        for candidate in hypotheses:
            if all(self.similarity(candidate, previous) < threshold for previous in kept):
                kept.append(candidate)
        return kept


class MetaReviewAgent:
    def summarize(self, hypotheses):
        critiques = [c.strip() for h in hypotheses for c in h.critiques if c.strip()]
        return {"n_hypotheses": len(hypotheses), "n_critiques": len(critiques),
                "repeated_critiques": Counter(c.lower() for c in critiques).most_common(5),
                "method": "literal_theme_count_not_semantic_meta_review"}
