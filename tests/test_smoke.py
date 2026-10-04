from bioagent.core import EvidenceItem, Hypothesis
from bioagent.scientific_agents import ProximityAgent, RankingAgent, EvolutionAgent
from bioagent.core import CallableLLMClient


def test_ranking_prefers_stronger_explicit_support():
    a = Hypothesis('H1', 'A', evidence=[EvidenceItem('study', 'source', .9, 'supports')])
    b = Hypothesis('H2', 'B', evidence=[EvidenceItem('study', 'source', .2, 'supports')])
    assert RankingAgent().rank([b, a])[0].identifier == 'H1'


def test_identical_hypotheses():
    a = Hypothesis('H1', 'microbial metabolite alters immune signaling')
    b = Hypothesis('H2', a.statement)
    assert ProximityAgent.similarity(a, b) == 1


def test_chinese_not_all_identical():
    a = Hypothesis('H1', '微生物代谢影响免疫')
    b = Hypothesis('H2', '神经网络改变认知')
    assert ProximityAgent.similarity(a, b) < .8


def test_revision_clears_old_support():
    old = Hypothesis('H1', 'old', evidence=[EvidenceItem('s', 'u', .9, 'supports')], score=.9)
    new = EvolutionAgent(CallableLLMClient(lambda p: 'new')).evolve(old)
    assert new is not old and old.statement == 'old'
    assert not new.evidence and new.score == 0


def test_no_evidence_no_support_score():
    assert RankingAgent().score(Hypothesis('H', 'claim')) == 0
