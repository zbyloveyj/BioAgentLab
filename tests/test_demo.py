import hashlib
import json
import pytest
from bioagent.demo import run_demo


def test_demo_end_to_end(tmp_path):
    out=tmp_path/'run'
    result=run_demo(out)
    assert result['mode']=='synthetic_offline_teaching'
    assert result['stop_reason'].startswith('completed_teaching')
    assert result['real_biological_validation'] is False
    assert all(a['unresolved'] for a in result['real_evidence_assessment'])
    assert result['revision']['verified_links']==()
    assert result['revision']['version']==2
    manifest=json.loads((out/'manifest.json').read_text())
    for name,digest in manifest['files'].items():
        assert hashlib.sha256((out/name).read_bytes()).hexdigest()==digest
    with pytest.raises(FileExistsError): run_demo(out)


@pytest.mark.parametrize('budget', [0,1,5,10])
def test_budget_stops_with_partial_report(tmp_path,budget):
    result=run_demo(tmp_path/str(budget),budget)
    assert result['stop_reason']=='budget_exhausted'
    assert result['budget']['used']<=budget
    assert result['real_biological_validation'] is False


def test_explicit_overwrite(tmp_path):
    out=tmp_path/'run'; run_demo(out); run_demo(out,overwrite=True)
    rows=[json.loads(x) for x in (out/'trace.jsonl').read_text().splitlines()]
    assert rows[0]['sequence']==1
