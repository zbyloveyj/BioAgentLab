"""Read-only PubMed client with bounded requests and offline-testable parsing."""
from __future__ import annotations
from datetime import datetime, timezone
import json
import os
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import xml.etree.ElementTree as ET

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


class PubMedError(RuntimeError):
    pass


def parse_search(raw: bytes) -> dict:
    try:
        data = json.loads(raw)
        if data.get("error"):
            raise ValueError("API error")
        result = data["esearchresult"]
        if result.get("ERROR") or result.get("errorlist"):
            raise ValueError("Search error")
        ids = result["idlist"]
        if not isinstance(ids, list) or not all(isinstance(i, str) and i.isdigit() for i in ids):
            raise ValueError("Invalid identifiers")
        count = int(result["count"])
        if count < 0:
            raise ValueError("Negative count")
        return {"ids": ids, "count": count,
                "query_translation": result.get("querytranslation", "")}
    except (ValueError, TypeError, KeyError) as exc:
        raise PubMedError("Invalid ESearch response") from exc


def parse_records(raw: bytes) -> list[dict]:
    if len(raw) > 4_000_000:
        raise PubMedError("XML exceeds size limit")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise PubMedError("Invalid PubMed XML") from exc
    if root.tag != "PubmedArticleSet":
        raise PubMedError("Unexpected XML root")
    records = []
    for article in root.findall("PubmedArticle"):
        pmid = article.findtext("./MedlineCitation/PMID")
        title_node = article.find("./MedlineCitation/Article/ArticleTitle")
        if not pmid or not pmid.isdigit() or title_node is None:
            raise PubMedError("Missing PMID or title")
        title = "".join(title_node.itertext())
        sections = []
        for node in article.findall("./MedlineCitation/Article/Abstract/AbstractText"):
            text = "".join(node.itertext())
            sections.append((node.get("Label", "") + ": " if node.get("Label") else "") + text)
        doi = next((n.text for n in article.findall("./PubmedData/ArticleIdList/ArticleId")
                    if n.get("IdType") == "doi"), None)
        records.append({"pmid": pmid, "title": title, "abstract": "\n".join(sections),
                        "doi": doi, "source": "https://pubmed.ncbi.nlm.nih.gov/" + pmid + "/",
                        "full_text_retrieved": False})
    return records


class PubMedClient:
    """Single-process pacing; shared-IP deployments need a shared limiter.

    NCBI copyright/disclaimer: https://www.ncbi.nlm.nih.gov/About/disclaimer.html
    Retrieved abstracts may be copyrighted. Do not redistribute indiscriminately.
    """
    def __init__(self, email: str, api_key: str | None = None, timeout=20.0):
        if not isinstance(email, str) or "@" not in email or " " in email:
            raise ValueError("Provide a valid developer contact email")
        if not 0 < timeout <= 120:
            raise ValueError("Invalid timeout")
        self.email, self.api_key = email, api_key or os.getenv("NCBI_API_KEY", "")
        self.timeout = timeout
        self.last_request = 0.0
        self.interval = 0.4  # conservative even when a key is supplied

    def _get(self, endpoint: str, params: dict) -> bytes:
        if endpoint not in {"esearch.fcgi", "efetch.fcgi"}:
            raise ValueError("Endpoint not allowed")
        params = {**params, "tool": "BioAgentLab", "email": self.email}
        if self.api_key:
            params["api_key"] = self.api_key
        url = BASE + endpoint + "?" + urlencode(params)
        for attempt in range(3):
            time.sleep(max(0.0, self.interval - (time.monotonic() - self.last_request)))
            self.last_request = time.monotonic()
            try:
                req = Request(url, headers={"User-Agent": "BioAgentLab/0.2 teaching"})
                with urlopen(req, timeout=self.timeout) as response:
                    raw = response.read(4_000_001)
                if len(raw) > 4_000_000:
                    raise PubMedError("Response exceeds size limit")
                return raw
            except HTTPError as exc:
                if exc.code not in {429, 500, 502, 503, 504} or attempt == 2:
                    raise PubMedError(f"PubMed HTTP error {exc.code}") from None
                time.sleep(2 ** attempt)
            except (URLError, TimeoutError):
                if attempt == 2:
                    raise PubMedError("PubMed transport error") from None
                time.sleep(2 ** attempt)
        raise PubMedError("Request failed")

    def search(self, query: str, limit: int = 10) -> dict:
        if not isinstance(query, str) or not query.strip() or len(query) > 5000:
            raise ValueError("Invalid query")
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("limit must be 1..100")
        result = parse_search(self._get("esearch.fcgi", {
            "db": "pubmed", "term": query, "retmode": "json", "retmax": limit}))
        return {**result, "query": query,
                "retrieved_at": datetime.now(timezone.utc).isoformat(), "source": BASE}

    def fetch_records(self, ids: list[str]) -> list[dict]:
        if not ids or len(ids) > 100 or not all(isinstance(i, str) and i.isdigit() for i in ids):
            raise ValueError("Expected 1..100 numeric PubMed IDs")
        return parse_records(self._get("efetch.fcgi", {
            "db": "pubmed", "id": ",".join(ids), "retmode": "xml"}))
