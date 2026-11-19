"""Lesson 11：可追溯的微生物科研证据导出。

结构：Python 直接从 NCBI 收集原文元数据 → 导出 JSON/CSV
      → 仅把选中的摘要传入 LLM 总结 → 保存单独的模型分析文本。
这样避免让模型编造 PMID，也不会把模型推断混进来源记录。
"""
from pathlib import Path
from agents import Agent, Runner
from agent_course.config import model_name, output_dir, require_ncbi_email, require_openai_key
from agent_course.pubmed import search_pubmed
from agent_course.reports import export_evidence

QUESTION = "gut microbiome AND depression"

def collect(query: str, max_results: int = 5) -> list[dict[str, str]]:
    """从 NCBI 返回可追溯的真实记录，不经过模型生成。"""
    require_ncbi_email()
    return search_pubmed(query, max_results)

def main() -> None:
    require_openai_key()
    print("第一步：从 PubMed 官方接口获取可核验记录")
    rows = collect(QUESTION)
    json_path, csv_path = export_evidence(rows, output_dir())
    print("已导出：", json_path, "和", csv_path)
    print("PMID 列表：", [r["pmid"] for r in rows])
    if not rows:
        print("没有检索到记录，停止生成总结；请调整检索式。")
        return
    # 在可复现任务中可以自行限制摘要长度，避免一次请求产生过多费用
    sections = []
    for row in rows:
        sections.append(
            f"PMID: {row['pmid']}\nTitle: {row['title']}\nDate: {row['pubdate']}\n"
            f"Abstract: {row['abstract'][:5000] or '[摘要缺失]'}"
        )
    prompt = (
        "请阅读以下 NCBI 真实检索结果，按 PMID 整理题目、研究问题、"
        "仅由摘要明确支持的描述、局限和待核查信息。"
        "任何摘要未提供的研究类型、样本量、结果都应标记为未知。"
        "禁止伪造新 PMID，也不要把关联解释成因果。\n\n"
        + "\n\n---\n\n".join(sections)
    )
    agent = Agent(
        name="文献证据归纳助手",
        model=model_name(),
        instructions="只使用输入中的来源材料，用中文谨慎总结，并明确说明仅基于摘要。",
    )
    result = Runner.run_sync(agent, prompt)
    out = output_dir() / "llm_literature_summary.md"
    out.write_text(
        "# AI 初步摘要分析（需要人工核查原文）\n\n"
        + str(result.final_output), encoding="utf-8",
    )
    print("模型初步整理：", out)
    print("\n完成：原始来源记录和 AI 解释独立存放。")

if __name__ == "__main__":
    main()
