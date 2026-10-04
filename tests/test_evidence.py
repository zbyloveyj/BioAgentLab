import pytest
from bioagent.evidence import Evidence, EvidenceLedger, Candidate


def ev(i='E1', study='S1', direction='supports', synthetic=False, context='human'):
    return Evidence(i,study,'C1','text','source',direction,context,synthetic)


def test_study_dedup():
    result=EvidenceLedger([ev(),ev('E2')]).assess('C1')
    assert result['support_studies']==['S1']
    assert len(result['evidence_ids'])==2


def test_synthetic_excluded_by_default():
    ledger=EvidenceLedger([ev(synthetic=True)])
    assert ledger.assess('C1')['verdict']=='insufficient'
    assert ledger.assess('C1',include_synthetic=True)['synthetic_included']


def test_conflict_is_preserved():
    ledger=EvidenceLedger([ev(),ev('E2','S2','contradicts')])
    assert ledger.assess('C1')['verdict']=='conflicted'


def test_same_study_mixed():
    ledger=EvidenceLedger([ev(),ev('E2','S1','contradicts')])
    assert ledger.assess('C1')['mixed_studies']==['S1']


def test_scope_filter():
    assert EvidenceLedger([ev()]).assess('C1',context='mouse')['verdict']=='insufficient'


def test_unknown_not_support():
    assert EvidenceLedger([ev(direction='unknown')]).assess('C1')['verdict']=='insufficient'


def test_only_negative():
    assert EvidenceLedger([ev(direction='contradicts')]).assess('C1')['verdict']=='contradicted_in_context'


def test_unknown_claim():
    assert EvidenceLedger([ev()]).assess('OTHER')['verdict']=='insufficient'


def test_duplicate_evidence_rejected():
    with pytest.raises(ValueError): EvidenceLedger([ev(),ev()])


def test_citations():
    ledger=EvidenceLedger([ev()])
    assert ledger.check_citations(['E1'])
    with pytest.raises(ValueError): ledger.check_citations(['FAKE'])


def test_revision_invalidates():
    parent=Candidate('H1','old',('C1',),verified_links=('E1',))
    child=parent.revise('new',('C2',))
    assert parent.verified_links==('E1',) and child.verified_links==()
    assert child.version==2 and child.parent=='H1:v1'


@pytest.mark.parametrize('args', [('','x',('C1',)),('H','',('C1',)),('H','x',()),('H','x',('C1','C1'))])
def test_invalid_candidate(args):
    with pytest.raises(ValueError): Candidate(*args)


@pytest.mark.parametrize('direction', ['yes','negative',''])
def test_invalid_direction(direction):
    with pytest.raises(ValueError): ev(direction=direction)
