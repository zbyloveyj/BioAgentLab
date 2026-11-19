"""仅使用标准库，检查本地学习环境。"""
from __future__ import annotations
import importlib.util
import os
import platform
import sys
from .config import PROJECT_ROOT, model_name


def diagnostics() -> dict[str, object]:
    packages = {name: importlib.util.find_spec(name) is not None
                for name in ["agents", "httpx", "dotenv", "pydantic", "jupyterlab", "pytest"]}
    return {
        "python": sys.version.split()[0],
        "python_ok": sys.version_info >= (3, 10),
        "system": platform.platform(),
        "project": str(PROJECT_ROOT),
        "model": model_name(),
        "openai_key_configured": bool(os.getenv("OPENAI_API_KEY", "").strip()),
        "ncbi_email_configured": "@" in os.getenv("NCBI_EMAIL", ""),
        "packages": packages,
    }


def show_diagnostics() -> None:
    d = diagnostics()
    print("=== OpenAI Agents SDK 中文课程环境自检 ===")
    for key, value in d.items():
        print(f"{key}: {value}")
    print("提示：离线功能无需 API Key；在线课程需要密钥与网络。")

