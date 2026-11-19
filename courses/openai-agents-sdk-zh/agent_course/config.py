"""配置工具：加载 .env、校验密钥、固定输出目录。"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def model_name() -> str:
    """从环境读取模型名称，支持低成本实验时自主切换。"""
    return os.getenv("OPENAI_MODEL", "gpt-5-mini").strip() or "gpt-5-mini"


def require_openai_key() -> str:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("尚未设置 OPENAI_API_KEY。请复制 .env.example 为 .env 后填写。")
    return key


def require_ncbi_email() -> str:
    value = os.getenv("NCBI_EMAIL", "").strip()
    if "@" not in value or value.startswith("@") or value.endswith("@"):
        raise RuntimeError("请在 .env 中设置真实有效的 NCBI_EMAIL，不能使用示例/假邮箱。")
    return value


def output_dir() -> Path:
    path = PROJECT_ROOT / "outputs"
    path.mkdir(exist_ok=True)
    return path
