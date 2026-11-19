"""使用 mock transport 的 PubMed 测试，不会访问网络。"""
import os
import httpx
import pytest
from agent_course.pubmed import BASE, search_pubmed


def test_pubmed_search_with_mock_transport(monkeypatch):
    monkeypatch.setenv("NCBI_EMAIL", "student@example.org")
    xml = '<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>123</PMID><Article><ArticleTitle>Fixture</ArticleTitle><Abstract><AbstractText>Test.</AbstractText></Abstract></Article></MedlineCitation></PubmedArticle></PubmedArticleSet>'

    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.path.endswith("/esearch.fcgi"):
            return httpx.Response(200, json={"esearchresult": {"idlist": ["123"]}})
        assert req.url.path.endswith("/efetch.fcgi")
        return httpx.Response(200, text=xml)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = search_pubmed("demo", max_results=1, client=client)
    assert result[0]["pmid"] == "123"
    assert result[0]["url"] == "https://pubmed.ncbi.nlm.nih.gov/123/"


def test_empty_query(monkeypatch):
    monkeypatch.setenv("NCBI_EMAIL", "student@example.org")
    with pytest.raises(ValueError):
        search_pubmed("   ")


def test_email_required(monkeypatch):
    monkeypatch.delenv("NCBI_EMAIL", raising=False)
    with pytest.raises(RuntimeError):
        search_pubmed("microbiome")
