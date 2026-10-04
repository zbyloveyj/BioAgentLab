"""Small offline BM25 index with English tokens and Chinese bigrams."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
import math
import re


def terms(text: str) -> list[str]:
    if not isinstance(text, str):
        raise TypeError("Expected text")
    result = re.findall(r"[a-z0-9_]+", text.lower())
    for run in re.findall(r"[\u4e00-\u9fff]+", text):
        result.extend([run] if len(run) == 1 else
                      [run[i:i+2] for i in range(len(run)-1)])
    return result


def jaccard(left: str, right: str) -> float:
    a, b = set(terms(left)), set(terms(right))
    return len(a & b) / len(a | b) if a and b else 0.0


@dataclass(frozen=True)
class Document:
    identifier: str
    text: str
    source: str

    def __post_init__(self):
        if not all(isinstance(x, str) and x.strip()
                   for x in (self.identifier, self.text, self.source)):
            raise ValueError("Document fields must be non-empty strings")


@dataclass(frozen=True)
class SearchHit:
    document: Document
    score: float


class BM25Index:
    """Transparent teaching implementation; not a biomedical search benchmark."""
    def __init__(self, documents, k1=1.5, b=0.75):
        if not math.isfinite(k1) or k1 <= 0 or not math.isfinite(b) or not 0 <= b <= 1:
            raise ValueError("Invalid BM25 parameters")
        self.documents = tuple(documents)
        if len({d.identifier for d in self.documents}) != len(self.documents):
            raise ValueError("Duplicate document IDs")
        self.k1, self.b = k1, b
        self.counts = [Counter(terms(d.text)) for d in self.documents]
        self.lengths = [sum(c.values()) for c in self.counts]
        self.average = sum(self.lengths) / len(self.lengths) if self.lengths else 0.0
        self.df = Counter(t for c in self.counts for t in c)

    def search(self, query: str, top_k: int = 5) -> list[SearchHit]:
        if type(top_k) is not int or top_k < 1:
            raise ValueError("top_k must be positive")
        q = set(terms(query))
        if not q or not self.documents or not self.average:
            return []
        hits = []
        n = len(self.documents)
        for doc, counts, length in zip(self.documents, self.counts, self.lengths):
            score = 0.0
            for token in q:
                frequency = counts.get(token, 0)
                if not frequency:
                    continue
                idf = math.log(1 + (n - self.df[token] + 0.5) / (self.df[token] + 0.5))
                denom = frequency + self.k1 * (1 - self.b + self.b * length / self.average)
                score += idf * frequency * (self.k1 + 1) / denom
            if score > 0:
                hits.append(SearchHit(doc, score))
        return sorted(hits, key=lambda h: (-h.score, h.document.identifier))[:top_k]
