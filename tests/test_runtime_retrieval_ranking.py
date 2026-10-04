from pathlib import Path
import json
import pytest
from bioagent.runtime import Budget, BudgetExceeded, Tool, ToolRegistry, safe_path, topological_order, EventLog
from bioagent.retrieval import Document, BM25Index, jaccard
from bioagent.ranking import elo_pair, tournament


def test_budget_exact_boundary():
    b=Budget(1); b.consume()
    with pytest.raises(BudgetExceeded): b.consume()
    assert b.used==1


@pytest.mark.parametrize('limit', [-1,1.5,True])
def test_bad_budget(limit):
    with pytest.raises(ValueError): Budget(limit)


def test_registry_contract_and_approval():
    r=ToolRegistry(); r.register(Tool('add',lambda a,b:a+b,lambda d:None,True))
    b=Budget(3)
    with pytest.raises(PermissionError): r.call('add',{'a':1,'b':2},budget=b)
    assert b.used==0
    assert r.call('add',{'a':1,'b':2},budget=b,approved=True)==3
    with pytest.raises(TypeError): r.call('add',{'a':1,'b':2,'c':3},budget=b,approved=True)
    with pytest.raises(ValueError): r.call('unknown',{},budget=b)


def test_registry_duplicate():
    r=ToolRegistry(); t=Tool('x',lambda:1,lambda d:None); r.register(t)
    with pytest.raises(ValueError): r.register(t)


def test_paths(tmp_path):
    assert safe_path(tmp_path,'a.txt').parent==tmp_path
    with pytest.raises(PermissionError): safe_path(tmp_path,'../escape.txt')


def test_dag():
    assert topological_order({'a':set(),'b':{'a'},'c':{'a'}})==['a','b','c']
    with pytest.raises(ValueError): topological_order({'a':{'b'},'b':{'a'}})
    with pytest.raises(ValueError): topological_order({'a':{'missing'}})


def test_events(tmp_path):
    log=EventLog(tmp_path/'events.jsonl'); log.write('a',ok=True); log.write('b',ok=False)
    rows=[json.loads(x) for x in log.path.read_text().splitlines()]
    assert [r['sequence'] for r in rows]==[1,2]


def test_bm25_relevance():
    docs=[Document('a','microbial metabolite evidence','s'),Document('b','brain image','s')]
    assert BM25Index(docs).search('metabolite')[0].document.identifier=='a'
    assert BM25Index(docs).search('unseen')==[]


def test_chinese_retrieval():
    docs=[Document('a','微生物代谢研究','s'),Document('b','脑网络认知研究','s')]
    assert BM25Index(docs).search('微生物')[0].document.identifier=='a'
    assert jaccard('微生物代谢','脑网络认知')<.8
    assert jaccard('','')==0
    assert jaccard('same words','same words')==1


def test_empty_index_and_query():
    assert BM25Index([]).search('x')==[]
    assert BM25Index([Document('a','x','s')]).search('')==[]


def test_duplicate_docs():
    d=Document('a','x','s')
    with pytest.raises(ValueError): BM25Index([d,d])


@pytest.mark.parametrize('k,b', [(0,.5),(1,-1),(1,2),(float('nan'),.5)])
def test_bm25_bad_parameters(k,b):
    with pytest.raises(ValueError): BM25Index([],k,b)


def test_elo_known_and_conserved():
    assert elo_pair(1000,1000,1)==(1012,988)
    assert elo_pair(1000,1000,.5)==(1000,1000)
    a,b=elo_pair(800,1200,1)
    assert a+b==pytest.approx(2000) and a>812


@pytest.mark.parametrize('outcome', [-1,2,.3,True])
def test_elo_invalid(outcome):
    with pytest.raises(ValueError): elo_pair(1000,1000,outcome)


def test_tournament_missing_not_draw():
    out=tournament(['a','b'],lambda a,b:None)
    assert out['ratings']=={'a':1000,'b':1000}
    assert out['matches'][0]['status']=='not_comparable'
