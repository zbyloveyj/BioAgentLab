"""Agent 可调用的函数工具。

导入此模块需要先安装 openai-agents。不要向工具暴露任意本地文件读写。
"""
from __future__ import annotations
import json

from agents.decorators import tool

from .data import MICROBES
from .rag import retrieve


@tool
def lookup_microbe(name: str) -> str:
    """查询教学模拟数据库中的微生物基础介绍。

    Args:
        name: 精确英文菌种名称，如 Akkermansia muciniphila。
    """
    item = MICROBES.get(name.strip())
    if item is None:
        return json.dumps({"found": False, "name": name}, ensure_ascii=False)
    return json.dumps({"found": True, "name": name, **item, "source": "教学模拟数据"}, ensure_ascii=False)


@tool
def search_local_notes(question: str, top_k: int = 3) -> str:
    """查阅本地教学知识卡片，返回匹配的原文与来源，不编造论文 PMID。

    Args:
        question: 用户的科研方法问题。
        top_k: 返回的最多资料条数。
    """
    return json.dumps(retrieve(question, top_k), ensure_ascii=False)
