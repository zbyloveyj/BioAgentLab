"""MicroMetaCell: an explicit, synthetic, offline end-to-end teaching workflow."""
from __future__ import annotations
from collections import Counter
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform
from .biology import audit_sample_ids, clr, pseudobulk
from .evidence import Evidence, EvidenceLedger
from .ranking import tournament
from .research import ResearchAgents
from .retrieval import BM25Index, Document
from .runtime import Budget, BudgetExceeded, EventLog, Tool, ToolRegistry

CLAIMS = {
    "A_to_M": "A_to_M microbe metabolite association",
    "M_to_C": "M_to_C metabolite host cell response",
    "U_to_A": "U_to_A common exposure microbe",
    "U_to_C": "U_to_C common exposure host cell",
    "Y_to_A": "Y_to_A reverse direction phenotype microbe",
}


def synthetic_evidence() -> list[Evidence]:
    return [
        Evidence("E1", "S1", "A_to_M", "A_to_M synthetic association of A with M.", "synthetic://S1", "supports", "demo", True),
        Evidence("E2", "S1", "A_to_M", "A_to_M second fragment of the same synthetic study.", "synthetic://S1/fragment2", "supports", "demo", True),
        Evidence("E3", "S2", "M_to_C", "M_to_C synthetic host-response observation.", "synthetic://S2", "supports", "demo", True),
        Evidence("E4", "S3", "M_to_C", "M_to_C synthetic conflicting response.", "synthetic://S3", "contradicts", "demo", True),
        Evidence("E5", "S4", "U_to_A", "U_to_A synthetic common-exposure association.", "synthetic://S4", "supports", "demo", True),
        Evidence("E6", "S5", "Y_to_A", "Y_to_A synthetic result against the proposed direction.", "synthetic://S5", "contradicts", "demo", True),
    ]


class DemoModel:
    """Scripted test double, not a biological reasoning model."""
    def complete(self, prompt: str) -> str:
        obj = json.loads(prompt)
        if obj["task"] == "generate":
            answer = {"candidates": [
                {"id": "H1", "statement": "教学假设：A可能通过M联系宿主细胞C。", "claim_ids": ["A_to_M", "M_to_C"]},
                {"id": "H2", "statement": "教学假设：共同暴露U可能解释A与C的并行变化。", "claim_ids": ["U_to_A", "U_to_C"]},
                {"id": "H3", "statement": "教学假设：表型Y可能反向联系微生物A。", "claim_ids": ["Y_to_A"]},
            ][:obj["max_candidates"]]}
        elif obj["task"] == "reflect":
            answer = {"critiques": ["全部资料为合成教学输入，不能建立真实生物学结论。"]}
            if obj["assessment"]["unresolved"]:
                answer["critiques"].append("仍有关键关系缺失、冲突或不适用，必须保留替代解释。")
        elif obj["task"] == "evolve":
            answer = {"statement": "修订教学假设：先核验所列关系及其情境，不预先认定因果路径。",
                      "claim_ids": obj["claim_ids"]}
        else:
            raise ValueError("Unknown scripted task")
        return json.dumps(answer, ensure_ascii=False)


def run_demo(out: Path, budget_limit=30, overwrite=False) -> dict:
    out = Path(out)
    if out.is_symlink():
        raise PermissionError("Output directory cannot be a symlink")
    if out.exists() and not overwrite:
        raise FileExistsError("Output exists; choose another directory or use --overwrite")
    out.mkdir(parents=True, exist_ok=True)
    for name in ("trace.jsonl", "report.json", "report.md", "manifest.json"):
        if (out/name).is_symlink():
            raise PermissionError("Output file cannot be a symlink")
    (out/"trace.jsonl").write_text("", encoding="utf-8")
    log = EventLog(out/"trace.jsonl")
    budget = Budget(budget_limit)
    report = {"mode": "synthetic_offline_teaching", "real_biological_validation": False,
              "question": "如何核对微生物—代谢物—宿主单细胞候选关系？",
              "completed_steps": [], "stop_reason": None,
              "limitations": ["合成数据与脚本模型，不代表真实发现。", "台账聚合已提供注释，不自动证明来源内容真实或因果成立。"]}
    log.write("start", mode=report["mode"], budget=budget.limit)
    try:
        budget.consume()
        samples = [{"sample_id": "D1"}, {"sample_id": "D2"}]
        report["audit"] = audit_sample_ids(samples)
        report["completed_steps"].append("audit")
        registry = ToolRegistry()
        registry.register(Tool("clr", clr, lambda args: None))
        registry.register(Tool("pseudobulk", pseudobulk, lambda args: None))
        report["clr"] = registry.call("clr", {"values": [2, 4, 8]}, budget=budget)
        cells = [
            {"cell_id": "c1", "donor_id": "D1", "cell_type": "C", "counts": [2, 1]},
            {"cell_id": "c2", "donor_id": "D1", "cell_type": "C", "counts": [3, 0]},
            {"cell_id": "c3", "donor_id": "D2", "cell_type": "C", "counts": [1, 4]},
        ]
        pb = registry.call("pseudobulk", {"cells": cells}, budget=budget)
        report["pseudobulk"] = [{"donor_id": d, "cell_type": c, "counts": counts}
                                for (d, c), counts in sorted(pb.items())]
        report["completed_steps"].append("numerical_tools")
        log.write("numerical_tools", n_donors=2, n_cells=3)
        agents = ResearchAgents(DemoModel(), set(CLAIMS))
        budget.consume()
        candidates = agents.generate(report["question"])
        items = synthetic_evidence()
        item_map = {e.evidence_id: e for e in items}
        index = BM25Index(Document(e.evidence_id, e.text, e.source) for e in items)
        ledger = EvidenceLedger()
        retrieved = set()
        for claim in sorted({cid for h in candidates for cid in h.claim_ids}):
            budget.consume()
            hits = index.search(claim, top_k=10)
            for hit in hits:
                if hit.document.identifier not in retrieved:
                    ledger.add(item_map[hit.document.identifier])
                    retrieved.add(hit.document.identifier)
            log.write("retrieve", claim_id=claim, document_ids=[h.document.identifier for h in hits])
        report["evidence"] = [asdict(e) for e in ledger.items.values()]
        report["real_evidence_assessment"] = [ledger.assess_candidate(h, context="demo") for h in candidates]
        assessments = {h.identifier: ledger.assess_candidate(h, context="demo", include_synthetic=True) for h in candidates}
        critiques = {}
        for h in candidates:
            budget.consume()
            critiques[h.identifier] = agents.reflect(h, assessments[h.identifier])
        report["teaching_assessment"] = list(assessments.values())
        report["critiques"] = critiques
        report["completed_steps"].append("retrieve_and_review")
        scores = {key: sum(1 if c["verdict"] == "supported_in_context" else
                           -1 if c["verdict"] in {"conflicted", "contradicted_in_context"} else 0
                           for c in a["claims"]) for key, a in assessments.items()}
        def judge(left, right):
            budget.consume()
            return 1.0 if scores[left] > scores[right] else 0.0 if scores[left] < scores[right] else 0.5
        report["preference_tournament"] = tournament([h.identifier for h in candidates], judge)
        report["preference_tournament"]["judge"] = "deterministic_synthetic_annotation_heuristic_not_LLM_debate"
        best = max(candidates, key=lambda h: report["preference_tournament"]["ratings"][h.identifier])
        budget.consume()
        child = agents.evolve(best, critiques[best.identifier])
        report["revision"] = asdict(child)
        report["revision_recheck"] = ledger.assess_candidate(child, context="demo")
        report["meta_review"] = dict(Counter(c for values in critiques.values() for c in values))
        report["candidates"] = [asdict(h) for h in candidates]
        report["completed_steps"].extend(["preference_tournament", "revision_and_reverification"])
        report["stop_reason"] = "completed_teaching_workflow_real_evidence_insufficient"
        log.write("review_complete", unresolved_real_claims=sorted(CLAIMS), revision_version=child.version)
    except BudgetExceeded:
        report["stop_reason"] = "budget_exhausted"
        log.write("stop", reason="budget_exhausted")
    report["budget"] = {"used": budget.used, "limit": budget.limit}
    report["conclusion"] = "本次仅演示计算与证据管理流程；没有真实生物学验证，不能认定任何机制成立。"
    log.write("report", stop_reason=report["stop_reason"])
    (out/"report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    lines = ["# MicroMetaCell 教学运行报告", "", "**合成数据；非真实研究结论。**", "", report["conclusion"], "",
             "## 运行状态", f"停止原因：`{report['stop_reason']}`", f"动作预算：{budget.used}/{budget.limit}", "",
             "## 已完成步骤", *[f"- {step}" for step in report["completed_steps"]], "",
             "## 证据边界", "台账只聚合输入中的方向与情境注释，不代替原文语义核验。模拟条目不计为真实支持。", "",
             "## 逐候选真实证据核对"]
    for result in report.get("real_evidence_assessment", []):
        lines += [f"### {result['candidate']}", "未解决关系：" + ", ".join(result["unresolved"])]
    lines += ["", "## 相对排名", "排名来自显式教学启发式，不是科学真实性概率；详见 report.json。", "",
              "## 下一步", "先获取合规、可定位且情境匹配的真实证据，再核验身份、暴露、供体结构和竞争解释。"]
    (out/"report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    manifest = {"mode": report["mode"], "python": platform.python_version(), "package_version": "0.2.0",
                "files": {name: hashlib.sha256((out/name).read_bytes()).hexdigest()
                          for name in ("report.json", "report.md", "trace.jsonl")}}
    (out/"manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return report
