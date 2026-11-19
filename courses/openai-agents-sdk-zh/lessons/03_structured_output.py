"""Lesson 03：用 Pydantic 保证结果字段有结构（不保证模型事实正确）。"""
from pydantic import BaseModel, Field
from agents import Agent, Runner
from agent_course.config import model_name, require_openai_key

class ResearchSummary(BaseModel):
    topic: str = Field(description="研究主题")
    methods: list[str] = Field(description="建议考虑的研究方法，非真实实验结论")
    uncertainties: list[str] = Field(description="不确定性及待核查点")
    next_step: str = Field(description="下一步建议")

def main() -> None:
    require_openai_key()
    agent = Agent(
        name="结构化科研规划助手",
        model=model_name(),
        instructions="只讨论研究设计，避免伪造真实论文与实验结果。",
        output_type=ResearchSummary,
    )
    result = Runner.run_sync(
        agent,
        "帮我规划一个关于肠道微生物组与抑郁症关联的公开文献研究问题。",
    )
    structured: ResearchSummary = result.final_output
    print(structured.model_dump_json(indent=2))

if __name__ == "__main__":
    main()
