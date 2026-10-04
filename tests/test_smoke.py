from bioagent.core import EvidenceItem, Hypothesis
from bioagent.scientific_agents import ProximityAgent, RankingAgent


def test_ranking_prefers_stronger_evidence() -> None:
    strong = Hypothesis(
        identifier="H1",
        statement="Mechanism A",
        evidence=[EvidenceItem("study", "source", confidence=0.9)],
    )
    weak = Hypothesis(
        identifier="H2",
        statement="Mechanism B",
        evidence=[EvidenceItem("study", "source", confidence=0.2)],
    )
    ranked = RankingAgent().rank([weak, strong])
    assert ranked[0].identifier == "H1"


def test_proximity_detects_identical_hypotheses() -> None:
    left = Hypothesis("H1", "microbial metabolite alters immune signaling")
    right = Hypothesis("H2", "microbial metabolite alters immune signaling")
    assert ProximityAgent.similarity(left, right) == 1.0
