import json
import pytest
from bioagent.debate import DebateAgent
from bioagent.core import CallableLLMClient
from bioagent.evidence import Candidate, EvidenceLedger
from bioagent.runtime import Budget, BudgetExceeded


def candidates():
    return Candidate('A','first',('C1',)), Candidate('B','second',('C2',))


def scripted(prompt):
    obj=json.loads(prompt)
    if obj['task']=='debate_advocate':
        return json.dumps({'argument':'A testable explanation, not a fact', 'limitations':['No external verification'], 'evidence_ids':[]})
    return json.dumps({'winner':'draw','reason':'Both lack evidence','evidence_ids':[]})


def test_debate_draw_and_budget():
    a,b=candidates(); budget=Budget(4)
    result=DebateAgent(CallableLLMClient(scripted)).compare(a,b,EvidenceLedger(),budget=budget)
    assert result['outcome']==.5 and result['order_consistent']
    assert budget.used==4 and result['scientific_truth_probability'] is False


def test_position_bias_becomes_not_comparable():
    def biased(prompt):
        obj=json.loads(prompt)
        if obj['task']=='debate_advocate': return scripted(prompt)
        return json.dumps({'winner':obj['candidate_order'][0],'reason':'position bias','evidence_ids':[]})
    a,b=candidates()
    result=DebateAgent(CallableLLMClient(biased)).compare(a,b,EvidenceLedger(),budget=Budget(4))
    assert result['outcome'] is None and not result['order_consistent']


def test_debate_unknown_citation_rejected():
    model=CallableLLMClient(lambda p:json.dumps({'argument':'x','limitations':[],'evidence_ids':['FAKE']}))
    a,b=candidates()
    with pytest.raises(ValueError): DebateAgent(model).compare(a,b,EvidenceLedger(),budget=Budget(4))


def test_debate_budget():
    a,b=candidates()
    with pytest.raises(BudgetExceeded): DebateAgent(CallableLLMClient(scripted)).compare(a,b,EvidenceLedger(),budget=Budget(0))
