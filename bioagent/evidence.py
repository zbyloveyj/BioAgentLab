"""Context-aware evidence bookkeeping; not an automatic semantic verifier."""
from __future__ import annotations
from dataclasses import dataclass, replace
from collections.abc import Iterable

DIRECTIONS = frozenset({"supports", "contradicts", "unknown"})


def nonempty(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    study_id: str
    claim_id: str
    text: str
    source: str
    direction: str = "unknown"
    context: str = "unspecified"
    synthetic: bool = False

    def __post_init__(self) -> None:
        for key in ("evidence_id", "study_id", "claim_id", "text", "source", "context"):
            nonempty(getattr(self, key), key)
        if self.direction not in DIRECTIONS:
            raise ValueError("Invalid evidence direction")
        if type(self.synthetic) is not bool:
            raise ValueError("synthetic must be boolean")


@dataclass(frozen=True)
class Candidate:
    identifier: str
    statement: str
    claim_ids: tuple[str, ...]
    version: int = 1
    parent: str | None = None
    verified_links: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        nonempty(self.identifier, "identifier")
        nonempty(self.statement, "statement")
        if type(self.version) is not int or self.version < 1:
            raise ValueError("Invalid version")
        if not isinstance(self.claim_ids, tuple) or not self.claim_ids:
            raise ValueError("claim_ids must be a non-empty tuple")
        if len(set(self.claim_ids)) != len(self.claim_ids):
            raise ValueError("Duplicate claim IDs")
        for item in self.claim_ids:
            nonempty(item, "claim_id")

    def revise(self, statement: str, claim_ids: tuple[str, ...]) -> Candidate:
        """A semantic revision invalidates all previous verification links."""
        return replace(self, statement=statement, claim_ids=claim_ids,
                       version=self.version + 1,
                       parent=f"{self.identifier}:v{self.version}", verified_links=())


class EvidenceLedger:
    def __init__(self, items: Iterable[Evidence] = ()) -> None:
        self.items: dict[str, Evidence] = {}
        for item in items:
            self.add(item)

    def add(self, item: Evidence) -> None:
        if not isinstance(item, Evidence):
            raise TypeError("Expected Evidence")
        if item.evidence_id in self.items:
            raise ValueError("Duplicate evidence ID")
        self.items[item.evidence_id] = item

    def check_citations(self, ids: Iterable[str]) -> bool:
        ids = tuple(ids)
        if any(not isinstance(i, str) or i not in self.items for i in ids):
            raise ValueError("Unknown evidence citation")
        return True

    def assess(self, claim_id: str, *, context: str | None = None,
               include_synthetic: bool = False) -> dict:
        nonempty(claim_id, "claim_id")
        all_items = [e for e in self.items.values() if e.claim_id == claim_id]
        accepted = [e for e in all_items
                    if (include_synthetic or not e.synthetic)
                    and (context is None or e.context == context)]
        support = {e.study_id for e in accepted if e.direction == "supports"}
        against = {e.study_id for e in accepted if e.direction == "contradicts"}
        if support and against:
            verdict = "conflicted"
        elif support:
            verdict = "supported_in_context"
        elif against:
            verdict = "contradicted_in_context"
        else:
            verdict = "insufficient"
        return {
            "claim_id": claim_id, "verdict": verdict,
            "support_studies": sorted(support),
            "contradicting_studies": sorted(against),
            "mixed_studies": sorted(support & against),
            "evidence_ids": sorted(e.evidence_id for e in accepted),
            "excluded_count": len(all_items) - len(accepted),
            "synthetic_included": any(e.synthetic for e in accepted),
            "method": "aggregation_of_supplied_annotations_not_semantic_verification",
        }

    def assess_candidate(self, candidate: Candidate, **kwargs) -> dict:
        checks = [self.assess(cid, **kwargs) for cid in candidate.claim_ids]
        return {
            "candidate": f"{candidate.identifier}:v{candidate.version}",
            "claims": checks,
            "unresolved": [x["claim_id"] for x in checks
                           if x["verdict"] != "supported_in_context"],
            "all_claims_supported_by_supplied_annotations": all(
                x["verdict"] == "supported_in_context" for x in checks),
            "causal_validation": False,
        }
