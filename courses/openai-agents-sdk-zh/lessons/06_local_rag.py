"""Lesson 06：先检索本地教学资料，再让模型组织回答（简化 RAG）。"""
from agents import Agent, Runner
from agent_course.config import require_openai_key, model_name
from agent_course.tools import search_local_notes

def main() -> None:
    require_openai_key()
    agent = Agent(
        name="本地文献方法学习助手",
        model=model_name(),
        tools=[search_local_notes],
        instructions=(
            "回答之前必须调用 search_local_notes。仅根据工具返回的教学资料回答。"
            "如未找到证据就说未找到，不允许伪造 PMID。"
            "应主动声明资料是教学说明而非真实论文。"
        ),
    )
    result = Runner.run_sync(agent, "宏基因组与16S测序相比有什么不同？")
    print(result.final_output)

if __name__ == "__main__":
    main()
