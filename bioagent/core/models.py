from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


EvidenceLevel = Literal["observation", "association", "mechanism", "replication"]


@dataclass(frozen=True)
class EvidenceClaim:
    statement: str
    source: str
    level: EvidenceLevel = "observation"
    supports: bool = True


@dataclass
class Hypothesis:
    title: str
    rationale: str
    predictions: list[str]
    falsifiers: list[str]
    evidence: list[EvidenceClaim] = field(default_factory=list)
    score: float = 0.0
    audit: list[str] = field(default_factory=list)

    def evidence_balance(self) -> float:
        if not self.evidence:
            return 0.0
        signed = sum(1 if item.supports else -1 for item in self.evidence)
        return signed / len(self.evidence)

