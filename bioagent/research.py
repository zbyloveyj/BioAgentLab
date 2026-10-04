"""JSON-contract model roles. All biological verification remains external."""
from __future__ import annotations
import json
from .core import LLMClient
from .evidence import Candidate


class ContractError(ValueError):
    pass


def json_object(text: str) -> dict:
    try:
        obj = json.loads(text)
    except (ValueError, TypeError) as exc:
        raise ContractError("Model did not return valid JSON") from exc
    if not isinstance(obj, dict):
        raise ContractError("Expected a JSON object")
    return obj


class ResearchAgents:
    def __init__(self, model: LLMClient, known_claims: set[str]):
        self.model, self.known_claims = model, set(known_claims)

    def _claims(self, value):
        if not isinstance(value, list) or not value or not all(isinstance(v, str) for v in value):
            raise ContractError("Invalid claim list")
        if not set(value) <= self.known_claims or len(value) != len(set(value)):
            raise ContractError("Unknown or duplicate claims")
        return tuple(value)

    def generate(self, question: str, n=3) -> list[Candidate]:
        if not isinstance(question, str) or not question.strip() or type(n) is not int or not 1 <= n <= 10:
            raise ContractError("Invalid generation request")
        prompt = json.dumps({"task": "generate", "question": question, "max_candidates": n,
                             "known_claim_ids": sorted(self.known_claims),
                             "output_schema": {"candidates": [{"id": "str", "statement": "str", "claim_ids": ["str"]}]},
                             "instruction": "Return JSON only. Generate testable candidates; never invent evidence IDs."},
                            ensure_ascii=False)
        data = json_object(self.model.complete(prompt)).get("candidates")
        if not isinstance(data, list) or not 1 <= len(data) <= n:
            raise ContractError("Invalid candidate count")
        try:
            result = [Candidate(item["id"], item["statement"], self._claims(item["claim_ids"])) for item in data]
        except (KeyError, TypeError, ValueError) as exc:
            raise ContractError("Invalid candidate fields") from exc
        if len({x.identifier for x in result}) != len(result):
            raise ContractError("Duplicate candidate IDs")
        return result

    def reflect(self, candidate: Candidate, assessment: dict) -> list[str]:
        prompt = json.dumps({"task": "reflect", "statement": candidate.statement,
                             "assessment": assessment,
                             "instruction": "Return JSON with critiques: list of strings. Identify scope, causal and evidence limitations. No new sources."}, ensure_ascii=False)
        value = json_object(self.model.complete(prompt)).get("critiques")
        if not isinstance(value, list) or len(value) > 20 or not all(isinstance(x, str) and x.strip() for x in value):
            raise ContractError("Invalid critique list")
        return value

    def evolve(self, candidate: Candidate, critiques: list[str]) -> Candidate:
        prompt = json.dumps({"task": "evolve", "statement": candidate.statement,
                             "claim_ids": list(candidate.claim_ids), "critiques": critiques,
                             "known_claim_ids": sorted(self.known_claims),
                             "instruction": "Return JSON with statement and claim_ids. Narrow unsupported claims; no fabricated sources."}, ensure_ascii=False)
        obj = json_object(self.model.complete(prompt))
        try:
            return candidate.revise(obj["statement"], self._claims(obj["claim_ids"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise ContractError("Invalid revision") from exc
