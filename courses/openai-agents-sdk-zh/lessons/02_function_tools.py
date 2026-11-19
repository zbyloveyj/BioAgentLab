"""Lesson 02：让 Agent 调用有明确范围的 Python 工具。"""
from agents import Agent, Runner
from agent_course.config import require_openai_key, model_name
from agent_course.tools import lookup_microbe

def main() -> None:
    require_openai_key()
    agent = Agent(
        name="微生物数据库助手",
        model=model_name(),
        instructions=(
            "当用户询问特定菌种资料时，先调用 lookup_microbe 查询教学数据。"
            "不得把教学资料描述为真实文献或临床证据。如果没有记录，请明确说未找到。"
        ),
        tools=[lookup_microbe],
    )
    answer = Runner.run_sync(agent, "请查询 Akkermansia muciniphila 的资料，注明信息来源。")
    print(answer.final_output)
    print("\n观察要点：Agent 可以根据问题提出 Python 工具调用请求。")

if __name__ == "__main__":
    main()
