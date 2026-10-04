"""Core schemas and provider-agnostic model interface."""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Protocol


class LLMClient(Protocol):
    """Minimal interface required by reasoning agents."""

    def complete(self, prompt: str) -> str:
        """Return a text completion."""
        ...


class CallableLLMClient:
    """Adapt any string-to-string callable into an LLM client."""

    def __init__(self, fn: Callable[[str], str]) -> None:
        self._fn = fn

    def complete(self, prompt: str) -> str:
        return self._fn(prompt)


@dataclass
class EvidenceItem:
    """A traceable piece of evidence supporting or challenging a claim."""

    title: str
    source: str
    confidence: float = 0.5
    direction: str = "unknown"
    notes: str = ""

    def __post_init__(self) -> None:
        self.confidence = max(0.0, min(1.0, float(self.confidence)))


@dataclass
class Hypothesis:
    """A scientific hypothesis with evidence, critiques and scores."""

    identifier: str
    statement: str
    rationale: str = ""
    evidence: list[EvidenceItem] = field(default_factory=list)
    critiques: list[str] = field(default_factory=list)
    score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
