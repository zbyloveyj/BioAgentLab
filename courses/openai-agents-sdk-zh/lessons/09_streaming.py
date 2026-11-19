"""Lesson 09：演示官方流式事件 API。"""
import asyncio
from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent
from agent_course.config import model_name, require_openai_key

async def go() -> None:
    agent = Agent(
        name="流式教学助手",
        model=model_name(),
        instructions="逐步解释但最终回答要通俗、准确、简洁。",
    )
    result = Runner.run_streamed(agent, input="简述什么是 AI Agent 里的工具调用。")
    print("开始接收输出：\n")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
    print("\n\n流式输出完成。")

if __name__ == "__main__":
    require_openai_key()
    asyncio.run(go())
