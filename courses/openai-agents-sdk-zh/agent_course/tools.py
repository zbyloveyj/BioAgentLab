"""用官方 @function_tool 把 Python 函数暴露给模型。

注意：openai-agents 的官方装饰器是 function_tool，不是 @tool。
"""
from __future__ import annotations

import json
from agents import function_tool
from .data import MICROBES
from .rag import retrieve


@function_tool
def lookup_microbe(name: str) -> str:
    """查询教学模拟数据库中的微生物基础介绍。

    Args:
        name: 精确英文菌种名称，如 Akkermansia muciniphila。
    """
    item = MICROBES.get(name.strip())
    if item is None:
        return json.dumps({"found": False, "name": name}, ensure_ascii=False)
    return json.dumps({"found": True, "name": name, **item, "source": "教学模拟数据"}, ensure_ascii=False)


@function_tool
def search_local_notes(question: str, top_k: int = 3) -> str:
    """查阅本地教学知识卡片，返回匹配的原文与来源，不编造论文 PMID。

    Args:
        question: 用户的科研方法问题。
        top_k: 返回的最多资料条数。
    """
    return json.dumps(retrieve(question, top_k), ensure_ascii=False)
