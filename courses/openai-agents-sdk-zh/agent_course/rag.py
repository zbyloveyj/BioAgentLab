"""零依赖向量服务的简易检索；只展示 RAG 中的检索步骤。

不是语义向量检索，中文仅支持粗略字符/关键词匹配。
"""
from __future__ import annotations

import re
from .data import LOCAL_NOTES

def _terms(s: str) -> set[str]:
    lower = s.lower()
    en = set(re.findall(r"[a-z][a-z0-9_-]{1,}", lower))
    cn = re.findall(r"[\u4e00-\u9fff]+", lower)
    grams = set()
    for chunk in cn:
        grams.update(chunk[i:i+2] for i in range(max(0, len(chunk)-1)))
    return en | grams

def retrieve(query: str, top_k: int = 3) -> list[dict[str, str]]:
    """按本地文字词重叠打分，返回包含证据来源的文档条目。"""
    if not query.strip():
        return []
    terms = _terms(query)
    scored = []
    for note in LOCAL_NOTES:
        text = note["title"] + " " + note["text"]
        hits = len(terms & _terms(text))
        if hits:
            scored.append((hits, note["id"], note))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [dict(x[2]) for x in scored[:max(0, min(int(top_k), 10))]]
