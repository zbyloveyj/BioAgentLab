"""NCBI PubMed 官方 E-utilities 客户端。

仅检索公开文献元数据/摘要。需要网络，并设置真实 NCBI_EMAIL。
不会绕过访问控制，也不把摘要当成经核实的结论。
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

import httpx
from .config import require_ncbi_email

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TOOL_NAME = "BioAgentLabCourse"


def parse_pubmed_xml(xml_text: str, *, retrieved_at: str = "") -> list[dict[str, str]]:
    """解析 NCBI EFetch XML，可用离线 fixture 测试。"""
    root = ET.fromstring(xml_text)
    entries: list[dict[str, str]] = []
    for item in root.findall(".//PubmedArticle"):
        med = item.find("./MedlineCitation")
        if med is None:
            continue
        pmid = (med.findtext("./PMID") or "").strip()
        title_el = med.find("./Article/ArticleTitle")
        title = "".join(title_el.itertext()).strip() if title_el is not None else ""
        abstr_parts = []
        for part in med.findall("./Article/Abstract/AbstractText"):
            text = "".join(part.itertext()).strip()
            if text:
                label = part.attrib.get("Label")
                abstr_parts.append(f"{label}: {text}" if label else text)
        pubdate_el = med.find("./Article/Journal/JournalIssue/PubDate")
        date = ""
        if pubdate_el is not None:
            date = " ".join(t.strip() for t in pubdate_el.itertext() if t and t.strip())
        if pmid:
            entries.append({
                "pmid": pmid,
                "title": title,
                "pubdate": date,
                "abstract": "\n".join(abstr_parts),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "retrieved_at": retrieved_at,
            })
    return entries


def search_pubmed(query: str, max_results: int = 5, *, client: httpx.Client | None = None) -> list[dict[str, str]]:
    """通过 ESearch 查 PMID，EFetch 获取元数据与摘要，限单次最多 10 篇。"""
    if not query.strip():
        raise ValueError("检索词不能空白")
    email = require_ncbi_email()
    max_results = max(1, min(int(max_results), 10))
    params_common = {"db": "pubmed", "tool": TOOL_NAME, "email": email}
    api_key = os.getenv("NCBI_API_KEY", "").strip()
    if api_key:
        params_common["api_key"] = api_key

    owns_client = client is None
    if client is None:
        client = httpx.Client(timeout=25.0, headers={"User-Agent": f"{TOOL_NAME}/0.1 ({email})"})
    try:
        res = client.get(f"{BASE}/esearch.fcgi", params={
            **params_common, "term": query, "retmax": max_results, "retmode": "json",
        })
        res.raise_for_status()
        ids = res.json().get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []
        if owns_client:
            time.sleep(0.4)  # 无 API Key 时，NCBI 默认建议不超过 3 请求/秒
        ret = client.get(f"{BASE}/efetch.fcgi", params={
            **params_common, "id": ",".join(ids), "retmode": "xml",
        })
        ret.raise_for_status()
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        return parse_pubmed_xml(ret.text, retrieved_at=now)
    finally:
        if owns_client:
            client.close()
