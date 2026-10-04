from __future__ import annotations

import sys
from pathlib import Path

import pdfplumber
from pypdf import PdfReader


def verify(path: Path) -> None:
    reader = PdfReader(str(path))
    pages = len(reader.pages)
    if pages < 130:
        raise SystemExit(f"FAIL: expected >=130 pages, got {pages}")
    if not reader.metadata or "BioAgentLab" not in str(reader.metadata.title):
        raise SystemExit("FAIL: missing title metadata")
    with pdfplumber.open(path) as pdf:
        sample_numbers = sorted({0, 1, len(pdf.pages)//2, len(pdf.pages)-1})
        samples = [(n + 1, pdf.pages[n].extract_text() or "") for n in sample_numbers]
    for number, text in samples:
        if len(text.strip()) < 20:
            raise SystemExit(f"FAIL: page {number} has too little extractable text")
    print(f"PASS pages={pages} size={path.stat().st_size} bytes sampled={','.join(str(n) for n,_ in samples)}")


if __name__ == "__main__":
    verify(Path(sys.argv[1]))

