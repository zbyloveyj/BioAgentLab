"""Lesson 08：主控 Agent 调用不同专业子 Agent，然后统一输出。"""
from agents import Agent, Runner
from agent_course.config import model_name, require_openai_key

def main() -> None:
    require_openai_key()
    methods = Agent(
        name="研究设计顾问",
        model=model_name(),
        instructions="讨论研究方法、混杂因素及验证手段，不捏造结论。",
    )
    writing = Agent(
        name="表达审校顾问",
        model=model_name(),
        instructions="将科研描述整理成通顺中文，不增加没有证据的事实。",
    )
    manager = Agent(
        name="科研总控",
        model=model_name(),
        instructions=(
            "先调用方法顾问，再调用表达审校顾问，最后汇总成两段："
            "第一段研究设计建议，第二段清晰的研究目标说明。"
        ),
        tools=[
            methods.as_tool(tool_name="methods_advisor", tool_description="研究设计与方法学建议"),
            writing.as_tool(tool_name="writing_advisor", tool_description="科研叙事与中文表达审校"),
        ],
    )
    result = Runner.run_sync(manager, "设计一项公开队列的肠道微生物跨疾病比较研究。")
    print(result.final_output)

if __name__ == "__main__":
    main()
