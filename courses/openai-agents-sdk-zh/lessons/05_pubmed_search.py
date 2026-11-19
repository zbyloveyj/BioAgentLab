"""Lesson 05：连接真正的 PubMed，先检索再让模型总结摘要。"""
from agents import Agent, Runner, function_tool
from agent_course.config import model_name, require_ncbi_email, require_openai_key
from agent_course.pubmed import search_pubmed
import json

@function_tool
def pubmed_articles(query: str, max_results: int = 3) -> str:
    """通过 NCBI PubMed 检索真实文献的 PMID、标题、日期和摘要。

    Args:
        query: PubMed 官方检索语法，例如 gut microbiome AND depression。
        max_results: 本次查询返回的最多论文数量，1 到 10 篇。
    """
    records = search_pubmed(query, max_results)
    print(f"PubMed 返回 {len(records)} 篇真实记录")
    return json.dumps(records, ensure_ascii=False)

def main() -> None:
    require_openai_key()
    require_ncbi_email()
    agent = Agent(
        name="PubMed 文献检索员",
        model=model_name(),
        tools=[pubmed_articles],
        instructions=(
            "遇到文献检索必须调用 pubmed_articles。"
            "只使用工具返回的 PMID、题名、摘要，不能编造文章。"
            "输出 1. 检索关键词 2. PMID+题名 3. 摘要能够支持的发现 "
            "4. 摘要不足以得出的结论。不要把关联当因果。"
        ),
    )
    result = Runner.run_sync(
        agent, "检索 gut microbiome AND depression，至多找3篇文献，用中文概述研究主题。"
    )
    print(result.final_output)

if __name__ == "__main__":
    main()
