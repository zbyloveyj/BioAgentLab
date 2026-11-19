"""Lesson 04：通过 SQLiteSession 延续多轮对话。

演示结束后会在 outputs/ 目录产生会话数据库，不纳入 Git。
"""
from agents import Agent, Runner, SQLiteSession
from agent_course.config import require_openai_key, model_name, output_dir

def main() -> None:
    require_openai_key()
    session = SQLiteSession("microbiome-course-demo", str(output_dir() / "study_memory.sqlite3"))
    agent = Agent(
        name="学习陪练",
        model=model_name(),
        instructions="用简洁、通俗的中文解释概念，记住本轮会话的讨论主题。",
    )
    first = Runner.run_sync(agent, "本次我们学习宏基因组测序。请用两句话介绍。", session=session)
    print("第一轮：", first.final_output)
    second = Runner.run_sync(agent, "请针对刚才的主题给我一道简单思考题。", session=session)
    print("\n第二轮：", second.final_output)

if __name__ == "__main__":
    main()
