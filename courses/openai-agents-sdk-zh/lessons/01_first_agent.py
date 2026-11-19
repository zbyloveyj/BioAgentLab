"""Lesson 01：第一个真正调用模型的 Agent。"""
from agents import Agent, Runner
from agent_course.config import require_openai_key, model_name

def main() -> None:
    require_openai_key()
    agent = Agent(
        name="微生物科研助理",
        model=model_name(),
        instructions=(
            "你是一位科研学习助理。用中文、按逻辑解释基础知识。"
            "遇到你不确定的事实要明确说明，不要伪造论文题目、PMID、引用或实验结论。"
        ),
    )
    result = Runner.run_sync(agent, "请通俗解释 shotgun 宏基因组测序与 16S 测序的不同。")
    print("\n=== 最终回答 ===")
    print(result.final_output)

if __name__ == "__main__":
    main()
