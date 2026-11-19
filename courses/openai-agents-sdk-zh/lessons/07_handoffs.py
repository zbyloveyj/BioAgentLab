"""Lesson 07：使用 handoffs 把不同领域问题转给专业 Agent。"""
from agents import Agent, Runner
from agent_course.config import require_openai_key, model_name

def main() -> None:
    require_openai_key()
    bio = Agent(
        name="生物学导师",
        model=model_name(),
        handoff_description="回答肠道菌群与宏基因组的基础研究问题。",
        instructions="使用中文解释微生物学。对不确定事实保留不确定性。",
    )
    python = Agent(
        name="Python导师",
        model=model_name(),
        handoff_description="解决 Python 数据处理和程序基础问题。",
        instructions="使用中文从基础解释 Python 代码；提供安全简短的代码示例。",
    )
    router = Agent(
        name="课程路由器",
        model=model_name(),
        instructions="判断问题属于生物学还是 Python，并转交正确的专家 Agent。",
        handoffs=[bio, python],
    )
    result = Runner.run_sync(router, "在 Python 中怎么读取 CSV 文件中的微生物丰度数据？")
    print("最终由：", result.last_agent.name)
    print(result.final_output)

if __name__ == "__main__":
    main()
