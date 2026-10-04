import json
import pytest
from bioagent.pubmed import parse_search, parse_records, PubMedError, PubMedClient
from bioagent.providers import response_text, ModelServiceError
from bioagent.research import ResearchAgents, ContractError
from bioagent.demo import DemoModel, CLAIMS
from bioagent.core import CallableLLMClient


def test_search_parser():
    raw=b'{"esearchresult":{"idlist":["12","34"],"count":"2"}}'
    assert parse_search(raw)['ids']==['12','34']


@pytest.mark.parametrize('raw', [b'not json',b'{}',b'{"error":"limited"}',b'{"esearchresult":{"idlist":["x"],"count":"1"}}'])
def test_search_parser_errors(raw):
    with pytest.raises(PubMedError): parse_search(raw)


def test_xml_nested_text():
    raw=b'<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>12</PMID><Article><ArticleTitle>A <i>gene</i> study</ArticleTitle><Abstract><AbstractText Label="RESULTS">A result</AbstractText></Abstract></Article></MedlineCitation></PubmedArticle></PubmedArticleSet>'
    record=parse_records(raw)[0]
    assert record['title']=='A gene study'
    assert record['abstract']=='RESULTS: A result'
    assert not record['full_text_retrieved']


@pytest.mark.parametrize('raw', [b'bad xml',b'<ERROR>x</ERROR>',b'<PubmedArticleSet><PubmedArticle/></PubmedArticleSet>'])
def test_bad_xml(raw):
    with pytest.raises(PubMedError): parse_records(raw)


def test_pubmed_requires_contact():
    with pytest.raises(ValueError): PubMedClient('')


def test_response_parser():
    payload={'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':'hello'}]}]}
    assert response_text(payload)=='hello'


@pytest.mark.parametrize('payload', [{},{'status':'incomplete'},{'status':'completed','output':[]}])
def test_response_rejects_incomplete(payload):
    with pytest.raises(ModelServiceError): response_text(payload)


def test_scripted_roles_contract():
    agents=ResearchAgents(DemoModel(),set(CLAIMS))
    hs=agents.generate('test')
    assert len(hs)==3
    child=agents.evolve(hs[0],['missing evidence'])
    assert child.version==2 and not child.verified_links


def test_unknown_model_claim_rejected():
    model=CallableLLMClient(lambda p:json.dumps({'candidates':[{'id':'H','statement':'x','claim_ids':['UNKNOWN']}]}))
    with pytest.raises(ContractError): ResearchAgents(model,{'KNOWN'}).generate('q')


def test_non_json_rejected():
    model=CallableLLMClient(lambda p:'a fluent but invalid answer')
    with pytest.raises(ContractError): ResearchAgents(model,{'KNOWN'}).generate('q')
