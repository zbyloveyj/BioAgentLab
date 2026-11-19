"""结构化证据导出：避免 CSV 公式注入，保留来源。"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Mapping, Any

FIELDS = ["pmid", "title", "pubdate", "abstract", "url", "retrieved_at"]


def _safe_csv(value: Any) -> str:
    s = str(value if value is not None else "").replace("\x00", "")
    # Excel/LibreOffice 可能将这些字符开头的文本解析为公式。
    return "'" + s if s.startswith(("=", "+", "-", "@", "\t", "\r")) else s


def export_evidence(records: list[Mapping[str, Any]], folder: Path, stem: str = "pubmed_evidence") -> tuple[Path, Path]:
    """写入 UTF-8 JSON + Excel 兼容的 UTF-8 BOM CSV。"""
    folder.mkdir(parents=True, exist_ok=True)
    path_json = folder / (stem + ".json")
    path_csv = folder / (stem + ".csv")
    normalized = [{field: row.get(field, "") for field in FIELDS} for row in records]
    path_json.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
    with path_csv.open("w", newline="", encoding="utf-8-sig") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDS)
        writer.writeheader()
        for row in normalized:
            writer.writerow({key: _safe_csv(value) for key, value in row.items()})
    return path_json, path_csv
