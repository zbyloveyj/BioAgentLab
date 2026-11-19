from pathlib import Path
import json
from agent_course.data import MICROBES, LOCAL_NOTES
from agent_course.rag import retrieve
from agent_course.pubmed import parse_pubmed_xml
from agent_course.reports import export_evidence


def test_demo_data_is_labeled():
    assert "Akkermansia muciniphila" in MICROBES
    assert all(x["source"] == "教学说明（非论文）" for x in LOCAL_NOTES)


def test_retrieve():
    rows = retrieve("16S 宏基因组", top_k=2)
    assert rows and rows[0]["id"] == "DEMO-002"
    assert retrieve("  ") == []


def test_parse_pubmed_fixture():
    xml = (Path(__file__).parent / "fixtures" / "pubmed_sample.xml").read_text("utf-8")
    rows = parse_pubmed_xml(xml, retrieved_at="TEST-DATE")
    assert len(rows) == 1
    assert rows[0]["pmid"] == "000000001"
    assert "Synthetic" in rows[0]["abstract"]
    assert rows[0]["retrieved_at"] == "TEST-DATE"


def test_export_json_csv(tmp_path):
    result = [{"pmid": "test", "title": "=BAD", "abstract": "hello"}]
    path_json, path_csv = export_evidence(result, tmp_path)
    assert json.loads(path_json.read_text("utf-8"))[0]["title"] == "=BAD"
    assert "'=BAD" in path_csv.read_text("utf-8-sig")
    assert path_json.exists() and path_csv.exists()


def test_empty_pubmed_xml():
    assert parse_pubmed_xml("<PubmedArticleSet />") == []
