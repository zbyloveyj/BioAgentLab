"""Small compatibility interfaces used by the introductory prompt workflow.

For provenance-aware work use bioagent.evidence.Evidence and EvidenceLedger.
"""
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Protocol
import math


class LLMClient(Protocol):
    def complete(self, prompt: str) -> str:
        ...


class CallableLLMClient:
    def __init__(self, fn: Callable[[str], str]) -> None:
        self._fn = fn

    def complete(self, prompt: str) -> str:
        value = self._fn(prompt)
        if not isinstance(value, str):
            raise TypeError("Model must return text")
        return value


@dataclass
class EvidenceItem:
    title: str
    source: str
    confidence: float = 0.5
    direction: str = "unknown"
    notes: str = ""

    def __post_init__(self):
        if not self.title.strip() or not self.source.strip():
            raise ValueError("Evidence title and source are required")
        if isinstance(self.confidence, bool) or not math.isfinite(self.confidence) or not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be finite and in [0,1]")
        if self.direction not in {"supports", "contradicts", "unknown"}:
            raise ValueError("Invalid direction")


@dataclass
class Hypothesis:
    identifier: str
    statement: str
    rationale: str = ""
    evidence: list[EvidenceItem] = field(default_factory=list)
    critiques: list[str] = field(default_factory=list)
    score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
