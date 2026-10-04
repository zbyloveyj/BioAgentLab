"""Minimal supervisor coordinating the scientific-agent loop."""

from .core import Hypothesis, LLMClient
from .scientific_agents import (
    GenerationAgent,
    MetaReviewAgent,
    ProximityAgent,
    RankingAgent,
    ReflectionAgent,
)


class ScientificSupervisor:
    def __init__(self, llm: LLMClient) -> None:
        self.generator = GenerationAgent(llm)
        self.reflector = ReflectionAgent(llm)
        self.proximity = ProximityAgent()
        self.ranker = RankingAgent()
        self.meta_reviewer = MetaReviewAgent()

    def run(self, question: str, n: int = 3) -> dict[str, object]:
        hypotheses = self.generator.generate(question, n=n)
        hypotheses = [self.reflector.critique(item) for item in hypotheses]
        hypotheses = self.proximity.deduplicate(hypotheses)
        ranked: list[Hypothesis] = self.ranker.rank(hypotheses)
        return {
            "question": question,
            "hypotheses": ranked,
            "meta_review": self.meta_reviewer.summarize(ranked),
        }
