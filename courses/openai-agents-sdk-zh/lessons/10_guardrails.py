"""Lesson 10：输入护栏，拦截要求编造科学证据的请求。

本课使用基于 Python 规则的输入护栏（免费、本地、可复核）。
生产级安全需要更全面的策略，不要只依赖关键词规则。
"""
from agents import (
    Agent, Runner, RunContextWrapper, GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered, input_guardrail,
)
from agent_course.config import model_name, require_openai_key

@input_guardrail
def evidence_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input: str
) -> GuardrailFunctionOutput:
    """示例规则：明确要求捏造 PMID 的输入触发阻断。"""
    text = input.lower()
    suspicious = any(phrase in text for phrase in [
        "编造pmid", "伪造pmid", "编造参考文献", "伪造参考文献", "fake pmid",
        "invent pmid", "fabricate citations",
    ])
    return GuardrailFunctionOutput(
        output_info={"reason": "拒绝生成虚构的参考文献标识" if suspicious else "允许"},
        tripwire_triggered=suspicious,
    )

def main() -> None:
    require_openai_key()
    agent = Agent(
        name="科研证据助手",
        model=model_name(),
        instructions="只提供可核查的研究思路，不捏造引用。",
        input_guardrails=[evidence_guardrail],
    )
    for question in ["请解释什么是 PMID。", "请编造PMID并说是真实文献。"]:
        try:
            result = Runner.run_sync(agent, question)
            print("允许：", result.final_output)
        except InputGuardrailTripwireTriggered:
            print("已拦截：", question)

if __name__ == "__main__":
    main()
